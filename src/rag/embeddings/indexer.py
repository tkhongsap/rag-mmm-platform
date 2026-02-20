"""Index builders for RAG text retrieval."""

from __future__ import annotations

import logging
import math
import os
from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.rag.data_processing.ingest import load_all_text_documents, load_asset_documents

logger = logging.getLogger(__name__)

_TEXT_COLLECTION = "text_documents"
_ASSET_COLLECTION = "campaign_assets"
_DEFAULT_QDRANT_PATH = "data/qdrant_db"
_DEFAULT_BM25_PATH = "data/index/bm25"
_DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
_EMBEDDING_COST_PER_1M_TOKENS_USD = 0.13


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


class RAGIndexer:
    """Builds and persists retrieval indexes for RAG."""

    def __init__(
        self,
        qdrant_path: str | None = None,
        bm25_path: str | None = None,
        embedding_model: str | None = None,
    ) -> None:
        self.embedding_model_name = (
            embedding_model
            or os.getenv("EMBEDDING_MODEL")
            or os.getenv("EMBED_MODEL", _DEFAULT_EMBEDDING_MODEL)
        )
        raw_qdrant_path = qdrant_path or os.getenv("QDRANT_PATH", _DEFAULT_QDRANT_PATH)
        self.qdrant_path = _resolve_project_path(raw_qdrant_path)
        self.qdrant_path.mkdir(parents=True, exist_ok=True)

        raw_bm25_path = bm25_path or _DEFAULT_BM25_PATH
        self.bm25_path = _resolve_project_path(raw_bm25_path)
        self.bm25_path.mkdir(parents=True, exist_ok=True)

        self.qdrant_client = QdrantClient(path=str(self.qdrant_path))
        self.embedding = OpenAIEmbedding(model=self.embedding_model_name)

    def _reset_collection(self, collection_name: str) -> None:
        """Drop an existing collection so each build is clean and de-duplicated."""
        if self.qdrant_client.collection_exists(collection_name):
            self.qdrant_client.delete_collection(collection_name)

    def _has_bm25_artifacts(self) -> bool:
        """Return True when the persisted BM25 directory already has index artifacts."""
        return self.bm25_path.exists() and any(self.bm25_path.iterdir())

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate tokens without API calls using a 4-chars-per-token heuristic."""
        if not text:
            return 0
        return max(1, math.ceil(len(text) / 4))

    def build_text_index(self, docs: list[Document]) -> VectorStoreIndex:
        """Build the dense text index in Qdrant for pre-chunked document inputs."""
        if not docs:
            raise ValueError("docs must contain at least one Document")

        self._reset_collection(_TEXT_COLLECTION)

        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=_TEXT_COLLECTION,
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Keep ingest.py as the only chunking layer; do not apply extra split transforms.
        index = VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            embed_model=self.embedding,
            transformations=[],
        )
        logger.info(
            "Built text index collection '%s' with %d documents",
            _TEXT_COLLECTION,
            len(docs),
        )
        return index

    def index_text(self) -> VectorStoreIndex:
        """Load all text documents via ingest and build the text index."""
        docs = load_all_text_documents()
        return self.build_text_index(docs)

    def build_asset_index(self, docs: list[Document]) -> VectorStoreIndex:
        """Build the dense asset index in Qdrant for creative search."""
        if not docs:
            raise ValueError("docs must contain at least one Document")

        for doc in docs:
            if doc.metadata is None:
                doc.metadata = {}
            doc.metadata.setdefault("image_path", "")

        self._reset_collection(_ASSET_COLLECTION)

        vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=_ASSET_COLLECTION,
        )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        index = VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            embed_model=self.embedding,
            transformations=[],
        )
        logger.info(
            "Built asset index collection '%s' with %d documents",
            _ASSET_COLLECTION,
            len(docs),
        )
        return index

    def index_assets(self) -> VectorStoreIndex:
        """Load asset documents via ingest and build the asset index."""
        docs = load_asset_documents()
        return self.build_asset_index(docs)

    def estimate(self, docs: list[Document]) -> dict[str, int | float]:
        """Estimate embedding tokens and cost for a document list without API calls."""
        estimated_tokens = sum(self._estimate_tokens(doc.text) for doc in docs)
        estimated_cost = (estimated_tokens / 1_000_000) * _EMBEDDING_COST_PER_1M_TOKENS_USD
        return {
            "chunk_count": len(docs),
            "estimated_tokens": estimated_tokens,
            "estimated_cost_usd": round(estimated_cost, 8),
        }

    def build_bm25_index(self, docs: list[Document]) -> BM25Retriever:
        """Build or load the persisted BM25 retriever for lexical text search."""
        if self._has_bm25_artifacts():
            logger.info("Loading BM25 retriever from '%s'", self.bm25_path)
            return BM25Retriever.from_persist_dir(str(self.bm25_path))

        if not docs:
            raise ValueError("docs must contain at least one Document")

        bm25_retriever = BM25Retriever.from_defaults(nodes=docs)
        bm25_retriever.persist(str(self.bm25_path))
        logger.info(
            "Built BM25 index with %d documents and persisted to '%s'",
            len(docs),
            self.bm25_path,
        )
        return bm25_retriever
