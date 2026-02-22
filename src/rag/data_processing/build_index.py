"""CLI for building and inspecting RAG retrieval indexes."""

from __future__ import annotations

import argparse
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from dotenv import load_dotenv
from llama_index.core import Document
from qdrant_client import QdrantClient

load_dotenv()

from src.rag.data_processing.ingest import (
    load_all_text_documents,
    load_asset_documents,
    load_config_document,
    load_contract_documents,
    load_csv_documents,
)
from src.rag.embeddings.indexer import RAGIndexer

_TEXT_COLLECTION = "text_documents"
_ASSET_COLLECTION = "campaign_assets"
_DEFAULT_QDRANT_PATH = "data/qdrant_db"
_DEFAULT_BM25_PATH = "data/index/bm25"
_EMBEDDING_COST_PER_1M_TOKENS_USD = 0.13


@dataclass(frozen=True)
class BuildTargets:
    """Selected index targets for this run."""

    include_text: bool
    include_assets: bool


@dataclass(frozen=True)
class LoadedDocuments:
    """Loaded documents split by retrieval target."""

    text_docs: list[Document]
    asset_docs: list[Document]


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


def build_arg_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for index build and validation flows."""
    parser = argparse.ArgumentParser(
        description=(
            "Build RAG indexes (Qdrant + BM25), estimate embedding cost, "
            "or check index status."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Load/chunk documents and print doc count, chunk count, token estimate, "
            "and cost estimate without building indexes."
        ),
    )
    parser.add_argument(
        "--max-cost-usd",
        type=float,
        metavar="FLOAT",
        help="Abort if estimated embedding cost exceeds this USD cap.",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Build text_documents + BM25 only.",
    )
    parser.add_argument(
        "--assets",
        action="store_true",
        help="Build campaign_assets only.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print Qdrant collection stats and BM25 status without rebuilding indexes.",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help=(
            "Use one file per category instead of full corpus: meta_ads.csv, "
            "tv_performance.csv, vehicle_sales.csv, MediaAgency_Terms_of_Business.md, "
            "config.py, and asset_manifest.csv."
        ),
    )
    return parser


def _resolve_targets(args: argparse.Namespace) -> BuildTargets:
    """Choose which index targets should be built for this run."""
    has_explicit_target = args.text or args.assets
    return BuildTargets(
        include_text=args.text or not has_explicit_target,
        include_assets=args.assets or not has_explicit_target,
    )


def _load_sample_text_documents(project_root: Path) -> list[Document]:
    """Load one predefined file per text category."""
    docs: list[Document] = []
    docs.extend(load_csv_documents(project_root / "data" / "raw" / "meta_ads.csv"))
    docs.extend(load_csv_documents(project_root / "data" / "raw" / "tv_performance.csv"))
    docs.extend(load_csv_documents(project_root / "data" / "raw" / "vehicle_sales.csv"))
    docs.extend(
        load_contract_documents(
            project_root
            / "data"
            / "raw"
            / "contracts"
            / "MediaAgency_Terms_of_Business.md"
        )
    )
    docs.append(load_config_document())
    return docs


def _load_documents(targets: BuildTargets, sample: bool) -> LoadedDocuments:
    """Load documents for the selected targets and source mode."""
    text_docs: list[Document] = []
    asset_docs: list[Document] = []
    project_root = _get_project_root()

    if targets.include_text:
        text_docs = (
            _load_sample_text_documents(project_root)
            if sample
            else load_all_text_documents()
        )

    if targets.include_assets:
        # Assets are sourced from a single manifest file in both full and sample modes.
        asset_docs = load_asset_documents()

    return LoadedDocuments(text_docs=text_docs, asset_docs=asset_docs)


def _estimate_tokens(text: str) -> int:
    """Estimate token count using a local heuristic to avoid API calls."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def _estimate_documents(docs: list[Document]) -> dict[str, int | float]:
    """Estimate document/chunk volume and embedding cost."""
    estimated_tokens = sum(_estimate_tokens(doc.text) for doc in docs)
    estimated_cost_usd = round(
        (estimated_tokens / 1_000_000) * _EMBEDDING_COST_PER_1M_TOKENS_USD,
        8,
    )

    source_files = {
        str(doc.metadata.get("source_file"))
        for doc in docs
        if doc.metadata and doc.metadata.get("source_file")
    }
    doc_count = len(source_files) if source_files else len(docs)

    return {
        "doc_count": doc_count,
        "chunk_count": len(docs),
        "estimated_tokens": estimated_tokens,
        "estimated_cost_usd": estimated_cost_usd,
    }


def _format_collection_status(name: str, vector_count: int, status: str) -> str:
    """Render collection status line consistently."""
    return f"{name}: vector_count={vector_count}, status={status}"


def _read_collection_status(client: QdrantClient, collection_name: str) -> tuple[int, str]:
    """Read collection vector count and status if present."""
    if not client.collection_exists(collection_name):
        return (0, "missing")

    collection = client.get_collection(collection_name)
    vector_count = int(collection.points_count or 0)
    status = str(getattr(collection.status, "value", collection.status))
    return (vector_count, status)


def check_indexes() -> int:
    """Print collection and BM25 artifact status without rebuilding indexes."""
    raw_qdrant_path = os.getenv("QDRANT_PATH", _DEFAULT_QDRANT_PATH)
    qdrant_path = _resolve_project_path(raw_qdrant_path)
    bm25_path = _resolve_project_path(_DEFAULT_BM25_PATH)

    print("Index status:")
    if qdrant_path.exists():
        client = QdrantClient(path=str(qdrant_path))
        try:
            text_count, text_status = _read_collection_status(client, _TEXT_COLLECTION)
            asset_count, asset_status = _read_collection_status(client, _ASSET_COLLECTION)
        finally:
            client.close()
    else:
        text_count, text_status = (0, "missing")
        asset_count, asset_status = (0, "missing")

    print(f"- {_format_collection_status(_TEXT_COLLECTION, text_count, text_status)}")
    print(f"- {_format_collection_status(_ASSET_COLLECTION, asset_count, asset_status)}")

    bm25_files = list(bm25_path.iterdir()) if bm25_path.exists() else []
    bm25_status = "ready" if bm25_files else "missing"
    print(
        "- BM25: "
        f"path={bm25_path}, status={bm25_status}, file_count={len(bm25_files)}"
    )
    return 0


def _print_estimate(docs: LoadedDocuments, totals: dict[str, int | float]) -> None:
    """Print estimate summary for dry-run and pre-build checks."""
    print("Estimate:")
    print(f"- text_chunks={len(docs.text_docs)}")
    print(f"- asset_chunks={len(docs.asset_docs)}")
    print(f"- doc_count={totals['doc_count']}")
    print(f"- chunk_count={totals['chunk_count']}")
    print(f"- estimated_tokens={totals['estimated_tokens']}")
    print(f"- estimated_cost_usd={totals['estimated_cost_usd']:.8f}")


def _validate_cost_cap(max_cost_usd: float | None, estimated_cost_usd: float) -> tuple[bool, str]:
    """Validate optional cost ceiling before build."""
    if max_cost_usd is None:
        return (True, "")
    if max_cost_usd < 0:
        return (False, "Error: --max-cost-usd must be >= 0.")
    if estimated_cost_usd > max_cost_usd:
        return (
            False,
            (
                f"Aborting: estimated cost ${estimated_cost_usd:.8f} exceeds "
                f"--max-cost-usd ${max_cost_usd:.8f}."
            ),
        )
    return (True, "")


def run(args: argparse.Namespace) -> int:
    """Execute CLI behavior from parsed arguments."""
    if args.check:
        return check_indexes()

    targets = _resolve_targets(args)
    docs = _load_documents(targets, sample=args.sample)
    all_docs = docs.text_docs + docs.asset_docs
    totals = _estimate_documents(all_docs)
    _print_estimate(docs, totals)

    is_valid, reason = _validate_cost_cap(
        max_cost_usd=args.max_cost_usd,
        estimated_cost_usd=float(totals["estimated_cost_usd"]),
    )
    if not is_valid:
        print(reason)
        return 1

    if args.dry_run:
        print("Dry run complete. No indexes were built.")
        return 0

    indexer = RAGIndexer()

    if targets.include_text:
        if not docs.text_docs:
            print("No text documents loaded. Skipping text_documents and BM25 builds.")
        else:
            indexer.build_text_index(docs.text_docs)
            indexer.build_bm25_index(docs.text_docs)
            print(f"Built text_documents + BM25 from {len(docs.text_docs)} chunks.")

    if targets.include_assets:
        if not docs.asset_docs:
            print("No asset documents loaded. Skipping campaign_assets build.")
        else:
            indexer.build_asset_index(docs.asset_docs)
            print(f"Built campaign_assets from {len(docs.asset_docs)} chunks.")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for `python -m src.rag.data_processing.build_index`."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
