"""Index builders for RAG text retrieval."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)

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
