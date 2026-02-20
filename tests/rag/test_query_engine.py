"""Tests for hybrid retrieval in src.rag.retrieval.query_engine."""

from __future__ import annotations

from pathlib import Path

from llama_index.core import Document
from llama_index.core.embeddings import MockEmbedding
from llama_index.core.schema import NodeWithScore, TextNode

from src.rag.embeddings import indexer as indexer_module
from src.rag.embeddings.indexer import RAGIndexer
from src.rag.retrieval import query_engine


def test_search_text_uses_reciprocal_fusion_and_formats_results(tmp_path: Path, monkeypatch):
    bm25_dir = tmp_path / "bm25"
    bm25_dir.mkdir(parents=True, exist_ok=True)
    (bm25_dir / "retriever.json").write_text("{}", encoding="utf-8")

    qdrant_dir = tmp_path / "qdrant"
    qdrant_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("QDRANT_PATH", str(qdrant_dir))
    monkeypatch.setattr(query_engine, "_DEFAULT_BM25_PATH", str(bm25_dir))

    calls: dict[str, object] = {}

    class _FakeEmbedding:
        def __init__(self, model: str) -> None:
            calls["embedding_model"] = model

    class _FakeQdrantClient:
        def __init__(self, path: str) -> None:
            calls["qdrant_path"] = path

        def collection_exists(self, collection_name: str) -> bool:
            calls["collection_name"] = collection_name
            return True

        def close(self) -> None:
            calls["client_closed"] = True

    class _FakeVectorStore:
        def __init__(self, client, collection_name: str) -> None:
            calls["vector_store_collection"] = collection_name

    class _FakeVectorStoreIndex:
        @staticmethod
        def from_vector_store(vector_store, embed_model):
            calls["from_vector_store"] = True
            return {"vector_store": vector_store, "embed_model": embed_model}

    class _FakeVectorRetriever:
        def __init__(self, index, similarity_top_k: int, filters, embed_model) -> None:
            calls["vector_top_k"] = similarity_top_k
            calls["vector_filters"] = filters
            calls["vector_embed_model"] = embed_model

    class _FakeBM25Inner:
        def __init__(self) -> None:
            self.scores = {"num_docs": 2}

    class _FakeBM25Retriever:
        def __init__(self) -> None:
            self.bm25 = _FakeBM25Inner()
            self.similarity_top_k: int | None = None

        @staticmethod
        def from_persist_dir(path: str) -> "_FakeBM25Retriever":
            calls["bm25_path"] = path
            return _FakeBM25Retriever()

    class _FakeFusionRetriever:
        def __init__(
            self,
            retrievers,
            llm,
            mode,
            similarity_top_k: int,
            num_queries: int,
            use_async: bool,
        ) -> None:
            calls["fusion_llm"] = llm
            calls["fusion_mode"] = mode
            calls["fusion_top_k"] = similarity_top_k
            calls["fusion_num_queries"] = num_queries
            calls["fusion_use_async"] = use_async
            calls["fusion_retriever_count"] = len(retrievers)

        def retrieve(self, query: str) -> list[NodeWithScore]:
            calls["query"] = query
            return [
                NodeWithScore(
                    node=TextNode(
                        text="Meta CPM benchmark is available in the launch dataset.",
                        metadata={
                            "source_file": "data/raw/meta_ads.csv",
                            "category": "digital_media",
                        },
                    ),
                    score=0.91,
                )
            ]

    monkeypatch.setattr(query_engine, "OpenAIEmbedding", _FakeEmbedding)
    monkeypatch.setattr(query_engine, "QdrantClient", _FakeQdrantClient)
    monkeypatch.setattr(query_engine, "QdrantVectorStore", _FakeVectorStore)
    monkeypatch.setattr(query_engine, "VectorStoreIndex", _FakeVectorStoreIndex)
    monkeypatch.setattr(query_engine, "VectorIndexRetriever", _FakeVectorRetriever)
    monkeypatch.setattr(query_engine, "BM25Retriever", _FakeBM25Retriever)
    monkeypatch.setattr(query_engine, "QueryFusionRetriever", _FakeFusionRetriever)

    results = query_engine.search_text(
        query="What is Meta CPM?",
        top_k=5,
        category="digital_media",
    )

    assert len(results) == 1
    assert results[0]["score"] == 0.91
    assert results[0]["metadata"]["source_file"] == "data/raw/meta_ads.csv"
    assert "Meta CPM benchmark" in results[0]["text"]

    assert calls["collection_name"] == "text_documents"
    assert calls["fusion_mode"] == query_engine.FUSION_MODES.RECIPROCAL_RANK
    assert calls["fusion_num_queries"] == 1
    assert calls["fusion_use_async"] is False
    assert calls["fusion_llm"] is not None
    assert calls["fusion_retriever_count"] == 2
    assert calls["query"] == "What is Meta CPM?"
    assert calls["client_closed"] is True


def test_search_text_smoke_meta_cpm_returns_expected_sources(tmp_path: Path, monkeypatch):
    qdrant_dir = tmp_path / "qdrant"
    bm25_dir = tmp_path / "bm25"

    monkeypatch.setenv("QDRANT_PATH", str(qdrant_dir))
    monkeypatch.setattr(query_engine, "_DEFAULT_BM25_PATH", str(bm25_dir))
    monkeypatch.setattr(indexer_module, "OpenAIEmbedding", lambda model: MockEmbedding(embed_dim=8))
    monkeypatch.setattr(query_engine, "OpenAIEmbedding", lambda model: MockEmbedding(embed_dim=8))

    docs = [
        Document(
            text=(
                "Meta CPM benchmark guidance: target CPM is tracked weekly for launch "
                "campaign optimization."
            ),
            metadata={"source_file": "data/raw/meta_ads.csv", "category": "digital_media"},
        ),
        Document(
            text=(
                "Configuration notes include Meta CPM fallback thresholds used when "
                "automated pacing alerts trigger."
            ),
            metadata={"source_file": "data/generators/config.py", "category": "config"},
        ),
        Document(
            text="TV performance dataset contains GRP and reach metrics by week.",
            metadata={"source_file": "data/raw/tv_performance.csv", "category": "traditional_media"},
        ),
    ]

    indexer = RAGIndexer(qdrant_path=str(qdrant_dir), bm25_path=str(bm25_dir))
    indexer.build_text_index(docs)
    indexer.build_bm25_index(docs)
    indexer.qdrant_client.close()

    results = query_engine.search_text("What is Meta CPM?", top_k=5)
    source_files = [result["metadata"].get("source_file", "") for result in results]

    assert len(results) > 0
    assert any("meta_ads.csv" in source or "config.py" in source for source in source_files)
    assert len(results) <= 5
    assert all("score" in result and "text" in result and "metadata" in result for result in results)
