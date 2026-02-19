"""Document loading for the RAG pipeline.

Loads CSV data files, markdown contracts, and config into LlamaIndex Document
objects with rich metadata for retrieval and filtering.
"""

from __future__ import annotations

import csv
import io
import logging
from pathlib import Path
from typing import List

from llama_index.core import Document

logger = logging.getLogger(__name__)

# Number of CSV rows to group into each Document chunk
_CSV_CHUNK_SIZE = 20

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_project_root() -> Path:
    """Walk up from this file to find the directory containing requirements.txt."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "requirements.txt").exists():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find project root (no requirements.txt found)")


def _categorize(filename: str) -> str:
    """Return a category string based on the filename."""
    name = filename.lower()

    digital = {"meta_ads", "google_ads", "dv360", "tiktok_ads", "youtube_ads", "linkedin_ads"}
    traditional = {"tv_performance", "ooh_performance", "print_performance", "radio_performance"}
    sales = {
        "vehicle_sales", "website_analytics", "configurator_sessions",
        "leads", "test_drives", "sla_tracking",
    }
    external = {"competitor_spend", "economic_indicators", "events"}

    stem = Path(name).stem

    if stem in digital:
        return "digital_media"
    if stem in traditional:
        return "traditional_media"
    if stem in sales:
        return "sales_pipeline"
    if stem in external:
        return "external"
    if name.endswith(".md"):
        return "contracts"
    return "config"


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_csv_documents(csv_path: Path) -> List[Document]:
    """Load a CSV file and group rows into chunked Documents.

    Each Document contains up to ``_CSV_CHUNK_SIZE`` rows formatted as CSV text.
    Metadata includes source file, category, column names, row range, and total
    row count.  Embedding-irrelevant metadata keys are excluded from the
    embedding representation.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        logger.warning("CSV file not found: %s", csv_path)
        return []

    root = _get_project_root()
    rel_path = str(csv_path.relative_to(root))
    category = _categorize(csv_path.name)

    text = csv_path.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)

    if len(rows) < 2:
        logger.warning("CSV file has no data rows: %s", csv_path)
        return []

    header = rows[0]
    data_rows = rows[1:]
    total_rows = len(data_rows)

    documents: List[Document] = []
    for chunk_start in range(0, total_rows, _CSV_CHUNK_SIZE):
        chunk_end = min(chunk_start + _CSV_CHUNK_SIZE, total_rows)
        chunk = data_rows[chunk_start:chunk_end]

        # Rebuild CSV text with header
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(header)
        writer.writerows(chunk)
        chunk_text = buf.getvalue()

        row_start = chunk_start + 1
        row_end = chunk_end

        doc = Document(
            text=chunk_text,
            metadata={
                "source_file": rel_path,
                "file_type": "csv",
                "category": category,
                "columns": header,
                "row_range": f"{row_start}-{row_end}",
                "total_rows": total_rows,
            },
            excluded_embed_metadata_keys=["source_file", "row_range", "total_rows"],
        )
        documents.append(doc)

    logger.info("Loaded %d chunks from %s (%d rows)", len(documents), rel_path, total_rows)
    return documents


# ---------------------------------------------------------------------------
# Contract / markdown loading
# ---------------------------------------------------------------------------

def load_contract_documents(md_path: Path) -> List[Document]:
    """Load a markdown contract file as a single Document.

    The vendor name is extracted from the filename by stripping the extension
    and replacing underscores with spaces.
    """
    md_path = Path(md_path)
    if not md_path.exists():
        logger.warning("Contract file not found: %s", md_path)
        return []

    root = _get_project_root()
    rel_path = str(md_path.relative_to(root))
    vendor = md_path.stem.replace("_", " ")

    text = md_path.read_text(encoding="utf-8")

    doc = Document(
        text=text,
        metadata={
            "source_file": rel_path,
            "file_type": "contract",
            "category": "contracts",
            "vendor": vendor,
        },
    )
    logger.info("Loaded contract: %s (vendor=%s)", rel_path, vendor)
    return [doc]


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config_document() -> Document:
    """Load data/generators/config.py as a Document with key values extracted.

    Extracts budget totals, channel list, seasonal multipliers, vehicle models,
    and date range into the document text and metadata.
    """
    root = _get_project_root()
    config_path = root / "data" / "generators" / "config.py"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    text = config_path.read_text(encoding="utf-8")
    rel_path = str(config_path.relative_to(root))

    doc = Document(
        text=text,
        metadata={
            "source_file": rel_path,
            "file_type": "config",
            "category": "config",
        },
    )
    logger.info("Loaded config document: %s", rel_path)
    return doc


# ---------------------------------------------------------------------------
# Asset manifest loading
# ---------------------------------------------------------------------------

def load_asset_documents() -> List[Document]:
    """Load data/assets/asset_manifest.csv, creating one Document per row.

    Each document's text is the description field (for embedding).  Metadata
    carries the image path, channel, vehicle model, creative type, campaign ID,
    and audience segment.

    Returns an empty list if the manifest file does not exist yet.
    """
    root = _get_project_root()
    manifest_path = root / "data" / "assets" / "asset_manifest.csv"

    if not manifest_path.exists():
        logger.info("Asset manifest not found at %s — skipping", manifest_path)
        return []

    rel_path = str(manifest_path.relative_to(root))
    text = manifest_path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text))

    documents: List[Document] = []
    for row in reader:
        description = row.get("description", "")
        if not description:
            continue

        doc = Document(
            text=description,
            metadata={
                "source_file": rel_path,
                "file_type": "asset",
                "category": "assets",
                "image_path": row.get("image_path", ""),
                "channel": row.get("channel", ""),
                "vehicle_model": row.get("vehicle_model", ""),
                "creative_type": row.get("creative_type", ""),
                "campaign_id": row.get("campaign_id", ""),
                "audience_segment": row.get("audience_segment", ""),
            },
            excluded_embed_metadata_keys=["image_path", "dimensions", "file_size"],
        )
        documents.append(doc)

    logger.info("Loaded %d asset documents from %s", len(documents), rel_path)
    return documents


# ---------------------------------------------------------------------------
# Aggregate loader
# ---------------------------------------------------------------------------

def load_all_text_documents() -> List[Document]:
    """Load all CSV data, contracts, and config into a combined Document list.

    Scans:
    - ``data/raw/*.csv``
    - ``data/raw/contracts/*.md``
    - ``data/generators/config.py``
    """
    root = _get_project_root()
    documents: List[Document] = []

    # CSVs
    raw_dir = root / "data" / "raw"
    if raw_dir.exists():
        for csv_file in sorted(raw_dir.glob("*.csv")):
            documents.extend(load_csv_documents(csv_file))

    # Contracts
    contracts_dir = raw_dir / "contracts"
    if contracts_dir.exists():
        for md_file in sorted(contracts_dir.glob("*.md")):
            documents.extend(load_contract_documents(md_file))

    # Config
    try:
        documents.append(load_config_document())
    except FileNotFoundError:
        logger.warning("Config file not found — skipping")

    logger.info("Total documents loaded: %d", len(documents))
    return documents
