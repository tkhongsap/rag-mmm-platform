"""Tests for src.rag.data_processing.build_index CLI behavior."""

from __future__ import annotations

from pathlib import Path

from llama_index.core import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from src.rag.data_processing import build_index


def test_help_documents_all_flags():
    parser = build_index.build_arg_parser()
    help_text = parser.format_help()

    assert "--dry-run" in help_text
    assert "--max-cost-usd" in help_text
    assert "--text" in help_text
    assert "--assets" in help_text
    assert "--check" in help_text
    assert "--sample" in help_text


def test_dry_run_prints_estimate_without_build(monkeypatch, capsys):
    calls = {"indexer_init": 0}

    class _FakeIndexer:
        def __init__(self) -> None:
            calls["indexer_init"] += 1

    monkeypatch.setattr(build_index, "RAGIndexer", _FakeIndexer)
    monkeypatch.setattr(
        build_index,
        "load_all_text_documents",
        lambda: [
            Document(text="meta cpm", metadata={"source_file": "data/raw/meta_ads.csv"}),
        ],
    )
    monkeypatch.setattr(
        build_index,
        "load_asset_documents",
        lambda: [
            Document(
                text="creative asset",
                metadata={"source_file": "data/assets/asset_manifest.csv"},
            ),
        ],
    )

    exit_code = build_index.main(["--dry-run"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Estimate:" in output
    assert "doc_count=" in output
    assert "chunk_count=" in output
    assert "estimated_tokens=" in output
    assert "estimated_cost_usd=" in output
    assert "Dry run complete. No indexes were built." in output
    assert calls["indexer_init"] == 0


def test_max_cost_guard_aborts_before_build(monkeypatch, capsys):
    build_calls: list[str] = []

    class _FakeIndexer:
        def __init__(self) -> None:
            build_calls.append("init")

        def build_text_index(self, docs: list[Document]) -> None:
            build_calls.append(f"text:{len(docs)}")

        def build_bm25_index(self, docs: list[Document]) -> None:
            build_calls.append(f"bm25:{len(docs)}")

    monkeypatch.setattr(build_index, "RAGIndexer", _FakeIndexer)
    monkeypatch.setattr(
        build_index,
        "load_all_text_documents",
        lambda: [
            Document(
                text="x" * 5000,
                metadata={"source_file": "data/raw/meta_ads.csv"},
            ),
        ],
    )

    exit_code = build_index.main(["--text", "--max-cost-usd", "0.0"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "exceeds --max-cost-usd" in output
    assert build_calls == []


def test_text_flag_builds_text_and_bm25_only(monkeypatch):
    calls: list[str] = []
    docs = [Document(text="Meta CPM benchmark", metadata={"source_file": "meta_ads.csv"})]

    class _FakeIndexer:
        def build_text_index(self, passed_docs: list[Document]) -> None:
            assert passed_docs == docs
            calls.append("text")

        def build_bm25_index(self, passed_docs: list[Document]) -> None:
            assert passed_docs == docs
            calls.append("bm25")

        def build_asset_index(self, passed_docs: list[Document]) -> None:
            _ = passed_docs
            calls.append("assets")

    monkeypatch.setattr(build_index, "RAGIndexer", _FakeIndexer)
    monkeypatch.setattr(build_index, "load_all_text_documents", lambda: docs)
    monkeypatch.setattr(
        build_index,
        "load_asset_documents",
        lambda: (_ for _ in ()).throw(AssertionError("assets loader should not run")),
    )

    exit_code = build_index.main(["--text"])

    assert exit_code == 0
    assert calls == ["text", "bm25"]


def test_assets_flag_builds_assets_only(monkeypatch):
    calls: list[str] = []
    docs = [
        Document(
            text="DEEPAL S07 launch creative",
            metadata={"source_file": "data/assets/asset_manifest.csv"},
        )
    ]

    class _FakeIndexer:
        def build_text_index(self, passed_docs: list[Document]) -> None:
            _ = passed_docs
            calls.append("text")

        def build_bm25_index(self, passed_docs: list[Document]) -> None:
            _ = passed_docs
            calls.append("bm25")

        def build_asset_index(self, passed_docs: list[Document]) -> None:
            assert passed_docs == docs
            calls.append("assets")

    monkeypatch.setattr(build_index, "RAGIndexer", _FakeIndexer)
    monkeypatch.setattr(
        build_index,
        "load_all_text_documents",
        lambda: (_ for _ in ()).throw(AssertionError("text loader should not run")),
    )
    monkeypatch.setattr(build_index, "load_asset_documents", lambda: docs)

    exit_code = build_index.main(["--assets"])

    assert exit_code == 0
    assert calls == ["assets"]


def test_sample_mode_uses_predefined_files(monkeypatch):
    observed_csv_files: list[str] = []
    observed_contract_files: list[str] = []
    observed = {"config_calls": 0, "asset_calls": 0}

    def _fake_csv_loader(csv_path: Path) -> list[Document]:
        observed_csv_files.append(csv_path.name)
        return [Document(text=csv_path.name, metadata={"source_file": str(csv_path)})]

    def _fake_contract_loader(md_path: Path) -> list[Document]:
        observed_contract_files.append(md_path.name)
        return [Document(text=md_path.name, metadata={"source_file": str(md_path)})]

    def _fake_config_loader() -> Document:
        observed["config_calls"] += 1
        return Document(
            text="config",
            metadata={"source_file": "data/generators/config.py"},
        )

    def _fake_asset_loader() -> list[Document]:
        observed["asset_calls"] += 1
        return [
            Document(
                text="asset",
                metadata={"source_file": "data/assets/asset_manifest.csv"},
            )
        ]

    monkeypatch.setattr(build_index, "load_csv_documents", _fake_csv_loader)
    monkeypatch.setattr(build_index, "load_contract_documents", _fake_contract_loader)
    monkeypatch.setattr(build_index, "load_config_document", _fake_config_loader)
    monkeypatch.setattr(build_index, "load_asset_documents", _fake_asset_loader)

    exit_code = build_index.main(["--dry-run", "--sample"])

    assert exit_code == 0
    assert observed_csv_files == ["meta_ads.csv", "tv_performance.csv", "vehicle_sales.csv"]
    assert observed_contract_files == ["MediaAgency_Terms_of_Business.md"]
    assert observed["config_calls"] == 1
    assert observed["asset_calls"] == 1


def test_check_prints_collection_stats_and_bm25_status(tmp_path, monkeypatch, capsys):
    qdrant_path = tmp_path / "qdrant"
    bm25_path = tmp_path / "bm25"
    qdrant_path.mkdir(parents=True, exist_ok=True)
    bm25_path.mkdir(parents=True, exist_ok=True)
    (bm25_path / "retriever.json").write_text("{}", encoding="utf-8")

    qdrant_client = QdrantClient(path=str(qdrant_path))
    qdrant_client.create_collection(
        collection_name="text_documents",
        vectors_config=VectorParams(size=4, distance=Distance.COSINE),
    )
    qdrant_client.close()

    monkeypatch.setenv("QDRANT_PATH", str(qdrant_path))
    monkeypatch.setattr(build_index, "_DEFAULT_BM25_PATH", str(bm25_path))

    exit_code = build_index.main(["--check"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "text_documents: vector_count=0, status=green" in output
    assert "campaign_assets: vector_count=0, status=missing" in output
    assert "BM25: path=" in output
    assert "status=ready" in output
