"""Tests for campaign asset indexing and embedding cost estimation."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from llama_index.core import Document

from src.rag.embeddings.indexer import RAGIndexer


def test_build_asset_index_sets_image_path_metadata(tmp_path: Path, monkeypatch):
    indexer = RAGIndexer(qdrant_path=str(tmp_path / "qdrant"))
    docs = [
        Document(
            text="DEEPAL S07 launch creative with panoramic roof close-up.",
            metadata={"source_file": "data/assets/asset_manifest.csv", "image_path": "s07.png"},
        ),
        Document(
            text="AVATR 11 social teaser focused on interior experience.",
            metadata={"source_file": "data/assets/asset_manifest.csv"},
        ),
    ]

    calls: dict[str, object] = {}

    def _fake_reset(collection_name: str) -> None:
        calls["collection_name"] = collection_name

    def _fake_from_documents(
        documents: list[Document],
        storage_context,
        embed_model,
        transformations,
    ) -> str:
        calls["from_documents_called"] = True
        assert storage_context is not None
        assert embed_model is not None
        assert transformations == []
        assert all("image_path" in doc.metadata for doc in documents)
        return "asset-index"

    monkeypatch.setattr(indexer, "_reset_collection", _fake_reset)
    monkeypatch.setattr(
        "src.rag.embeddings.indexer.VectorStoreIndex.from_documents",
        _fake_from_documents,
    )

    result = indexer.build_asset_index(docs)

    assert result == "asset-index"
    assert calls["collection_name"] == "campaign_assets"
    assert calls["from_documents_called"] is True
    assert docs[0].metadata["image_path"] == "s07.png"
    assert docs[1].metadata["image_path"] == ""


def test_build_asset_index_requires_docs(tmp_path: Path):
    indexer = RAGIndexer(qdrant_path=str(tmp_path / "qdrant"))

    with pytest.raises(ValueError, match="docs must contain at least one Document"):
        indexer.build_asset_index([])


def test_estimate_returns_chunk_tokens_and_cost(tmp_path: Path):
    indexer = RAGIndexer(qdrant_path=str(tmp_path / "qdrant"))
    docs = [
        Document(text="Meta CPM guidance for launch planning."),
        Document(text="TV burst calendar by week for Q2."),
    ]

    expected_tokens = sum(math.ceil(len(doc.text) / 4) for doc in docs)
    expected_cost = round((expected_tokens / 1_000_000) * 0.13, 8)

    estimate = indexer.estimate(docs)

    assert estimate == {
        "chunk_count": 2,
        "estimated_tokens": expected_tokens,
        "estimated_cost_usd": expected_cost,
    }

