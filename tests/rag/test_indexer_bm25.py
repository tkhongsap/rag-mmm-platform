"""Tests for BM25 indexing in src.rag.embeddings.indexer."""

from __future__ import annotations

from pathlib import Path

import pytest
from llama_index.core import Document

from src.rag.embeddings.indexer import RAGIndexer


def _sample_docs() -> list[Document]:
    return [
        Document(
            text="Meta CPM benchmark guidance for campaign planning.",
            metadata={"source_file": "meta_ads.csv", "category": "digital_media"},
        ),
        Document(
            text="TV reach and frequency targets for the 2025 launch.",
            metadata={"source_file": "tv_performance.csv", "category": "traditional"},
        ),
    ]


def test_build_bm25_index_persists_artifacts(tmp_path: Path):
    bm25_dir = tmp_path / "bm25"
    indexer = RAGIndexer(
        qdrant_path=str(tmp_path / "qdrant"),
        bm25_path=str(bm25_dir),
    )

    bm25 = indexer.build_bm25_index(_sample_docs())

    assert bm25 is not None
    assert bm25_dir.exists()
    assert any(bm25_dir.iterdir())
    assert (bm25_dir / "retriever.json").exists()


def test_build_bm25_index_loads_from_disk_on_second_call(tmp_path: Path, monkeypatch):
    bm25_dir = tmp_path / "bm25"
    indexer = RAGIndexer(
        qdrant_path=str(tmp_path / "qdrant"),
        bm25_path=str(bm25_dir),
    )
    docs = _sample_docs()

    first = indexer.build_bm25_index(docs)
    assert first is not None

    def _fail_from_defaults(*args, **kwargs):
        raise AssertionError("BM25 should load from disk instead of rebuilding")

    monkeypatch.setattr(
        "src.rag.embeddings.indexer.BM25Retriever.from_defaults",
        _fail_from_defaults,
    )

    reloaded = indexer.build_bm25_index([])
    results = reloaded.retrieve("What is Meta CPM?")

    assert len(results) > 0
    assert results[0].node.metadata["source_file"] == "meta_ads.csv"


def test_build_bm25_index_requires_docs_for_first_build(tmp_path: Path):
    indexer = RAGIndexer(
        qdrant_path=str(tmp_path / "qdrant"),
        bm25_path=str(tmp_path / "bm25"),
    )

    with pytest.raises(ValueError, match="docs must contain at least one Document"):
        indexer.build_bm25_index([])
