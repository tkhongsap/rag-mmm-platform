"""Hybrid retrieval query engine for MS-2 dry-run validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from llama_index.core import VectorStoreIndex
from llama_index.core.indices.vector_store.retrievers import VectorIndexRetriever
from llama_index.core.llms.mock import MockLLM
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.retrievers.fusion_retriever import FUSION_MODES
from llama_index.core.schema import MetadataMode, NodeWithScore
from llama_index.core.vector_stores.types import ExactMatchFilter, MetadataFilters
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

_TEXT_COLLECTION = "text_documents"
_DEFAULT_QDRANT_PATH = "data/qdrant_db"
_DEFAULT_BM25_PATH = "data/index/bm25"
_DEFAULT_EMBEDDING_MODEL = "text-embedding-3-large"


def _get_project_root() -> Path:
    """Walk up from this file to find the directory containing requirements.txt."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "requirements.txt").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no requirements.txt found)")


def _resolve_project_path(raw_path: str) -> Path:
    """Resolve a path against project root when a relative path is provided."""
    resolved_path = Path(raw_path)
    if resolved_path.is_absolute():
        return resolved_path
    return _get_project_root() / resolved_path


def _build_category_filters(category: str | None) -> MetadataFilters | None:
    """Build category metadata filters for retrievers when requested."""
    if not category:
        return None

    normalized = category.strip()
    if not normalized:
        return None

    return MetadataFilters(
        filters=[ExactMatchFilter(key="category", value=normalized)]
    )


def _node_text(node_with_score: NodeWithScore) -> str:
    """Extract node text from retrieval results in a version-safe way."""
    node = node_with_score.node
    try:
        return node.get_content(metadata_mode=MetadataMode.NONE)
    except TypeError:
        return node.get_content()


def _serialize_node(node_with_score: NodeWithScore) -> dict[str, Any]:
    """Convert a LlamaIndex NodeWithScore into a JSON-serializable payload."""
    metadata = dict(node_with_score.node.metadata or {})
    score = float(node_with_score.score) if node_with_score.score is not None else 0.0
    return {
        "score": score,
        "text": _node_text(node_with_score),
        "metadata": metadata,
    }


def _matches_category(node_with_score: NodeWithScore, category: str | None) -> bool:
    """Check whether a retrieved node belongs to the requested category."""
    if not category:
        return True

    expected = category.strip().lower()
    actual = str((node_with_score.node.metadata or {}).get("category", "")).lower()
    return actual == expected


def _bm25_top_k(bm25_retriever: BM25Retriever, requested_top_k: int) -> int:
    """Clamp BM25 top-k so it never exceeds indexed corpus size."""
    raw_num_docs = bm25_retriever.bm25.scores.get("num_docs")
    try:
        num_docs = int(raw_num_docs) if raw_num_docs is not None else requested_top_k
    except (TypeError, ValueError):
        num_docs = requested_top_k
    if num_docs <= 0:
        return 1
    return min(requested_top_k, num_docs)


def search_text(
    query: str,
    top_k: int = 5,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Run hybrid text retrieval (dense + BM25) with reciprocal reranking."""
    query_text = query.strip()
    if not query_text:
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    qdrant_path = _resolve_project_path(os.getenv("QDRANT_PATH", _DEFAULT_QDRANT_PATH))
    bm25_path = _resolve_project_path(_DEFAULT_BM25_PATH)

    if not bm25_path.exists() or not any(bm25_path.iterdir()):
        raise FileNotFoundError(
            f"BM25 index not found at {bm25_path}. Run build_index.py to create it."
        )

    embedding_model_name = (
        os.getenv("EMBEDDING_MODEL")
        or os.getenv("EMBED_MODEL", _DEFAULT_EMBEDDING_MODEL)
    )
    embedding = OpenAIEmbedding(model=embedding_model_name)
    filters = _build_category_filters(category)

    qdrant_client = QdrantClient(path=str(qdrant_path))
    try:
        if not qdrant_client.collection_exists(_TEXT_COLLECTION):
            raise FileNotFoundError(
                "Qdrant collection 'text_documents' not found. Run build_index.py --text first."
            )

        vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=_TEXT_COLLECTION,
        )
        vector_index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            embed_model=embedding,
        )
        vector_retriever = VectorIndexRetriever(
            index=vector_index,
            similarity_top_k=top_k,
            filters=filters,
            embed_model=embedding,
        )

        bm25_retriever = BM25Retriever.from_persist_dir(str(bm25_path))
        bm25_retriever.similarity_top_k = _bm25_top_k(bm25_retriever, top_k)

        fusion_retriever = QueryFusionRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            llm=MockLLM(),
            mode=FUSION_MODES.RECIPROCAL_RANK,
            similarity_top_k=top_k,
            num_queries=1,
            use_async=False,
        )

        nodes = fusion_retriever.retrieve(query_text)
        filtered_nodes = [node for node in nodes if _matches_category(node, category)]
        return [_serialize_node(node) for node in filtered_nodes[:top_k]]
    finally:
        qdrant_client.close()
