# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enterprise platform combining RAG (Retrieval-Augmented Generation) with Marketing Mix Modeling (MMM). Built with LlamaIndex and OpenAI for the RAG pipeline, statsmodels/scikit-learn for MMM. Frontend is a React + Vite app (`ui/platform/`) with sidebar navigation and three pages: RAG Chat, MMM Dashboard, Data Management.

**Current state**: The `src/` modules are **architectural scaffolding** (docstring stubs in `__init__.py` only — no implementation yet). The **synthetic data generators** in `data/generators/` are fully implemented and production-ready. Reference docs and LlamaIndex guides are complete.

## Commands

```bash
# Install
make install                    # pip install -r requirements.txt
cp .env.example .env            # Then set OPENAI_API_KEY
# Note: use the project venv first (`source .venv/bin/activate`) because
# system-level `pip install` may fail under PEP 668 externally managed Python.

# Test
make test                       # python -m pytest tests/ -v
make test-rag                   # pytest tests/rag/ -v
make test-mmm                   # pytest tests/mmm/ -v
make test-cov                   # pytest with --cov=src --cov-report=term-missing
python -m pytest tests/rag/test_foo.py -v   # Single test file
python -m pytest tests/ -k "test_name" -v   # Single test by name

# Run
make run-app                    # cd ui/platform && npm run dev  (http://localhost:3001)
make run-rag-cli                # python -m src.rag.retrieval.cli --interactive

# Other
make lint                       # py_compile checks on src/rag and src/mmm
make clean                      # Remove __pycache__, .pytest_cache, coverage artifacts
make help                       # List all make targets

# Synthetic data generation
python data/generators/generate_all.py              # Generate all data (~63K rows)
python data/generators/generate_all.py --validate-only  # Validate existing data only
```

## Architecture

```
src/
├── rag/                          # RAG pipeline (all stubs, not yet implemented)
│   ├── data_processing/          # Stage 1: Document → structured LlamaIndex docs
│   ├── embeddings/               # Stage 2: Batch embedding generation
│   ├── retrieval/                # Stage 3+4: Index loading + retrieval
│   │   └── retrievers/           # 7 strategy adapters (vector, summary, recursive,
│   │                             #   metadata, chunk_decoupling, hybrid, planner)
│   └── common/                   # Shared RAG utilities
├── mmm/                          # Marketing Mix Modeling (all stubs)
│   ├── data_ingestion/           # Media spend, sales data loading
│   ├── modeling/                 # Adstock, saturation curves, Bayesian/OLS regression
│   ├── optimization/             # Budget allocation, ROI analysis
│   └── common/
├── platform/
│   ├── api/                      # REST API (stub)
│   └── config/                   # Centralized configuration (stub)

ui/
├── platform/                     # React + Vite platform app (port 3001)
│   └── src/
│       ├── App.jsx               # Sidebar layout + React Router
│       ├── api.js                # API client (VITE_API_BASE → http://localhost:8000)
│       └── pages/                # RagChat, MmmDashboard, DataManagement
└── raw-data-dashboard/           # Vite React data inventory viewer (port 3000)

data/generators/                  # FULLY IMPLEMENTED synthetic data pipeline
├── config.py                     # Master config (seed, budgets, channels, benchmarks)
├── digital_media.py              # 6 CSVs: meta, google, dv360, tiktok, youtube, linkedin
├── traditional_media.py          # 4 CSVs: tv, ooh, print, radio
├── sales_pipeline.py             # 5 CSVs: vehicle_sales, website, configurator, leads, test_drives
├── contracts.py                  # 7 markdown vendor contracts
├── events.py                     # Events calendar
├── external_data.py              # Competitor spend, economic indicators
├── aggregate_mmm.py              # Compatibility shim re-exporting aggregate_mmm_data
├── validators.py                 # 10 validation checks + MMM weekly aggregation
└── generate_all.py               # 7-step orchestrator entry point

data/raw/                         # Generated output: ~19 CSVs + 7 contracts
data/mmm/                         # MMM-ready: weekly_channel_spend, weekly_sales, model_ready
references/rag-llamaindex/        # LlamaIndex framework reference docs (9 guides)
references/rag-methodology/       # RAG methodology docs (10 files)
docs/llamaindex-framework/        # LlamaIndex tutorial series (15 files)
docs/prd/                         # Product requirements (Word docs)
prompts/                          # Agent team prompt for synthetic data generation
```

Generated data artifacts are ignored in `.gitignore`; preserve the `!data/**/.gitkeep` exception when adding new ignored `data/` subdirectories so empty folder sentinels stay tracked.

## Data Generator Details

The generators produce synthetic marketing data for a UK automotive launch (DEEPAL/AVATR brands, 2025). Key design:

- **config.py** is the single source of truth: seed (42), date range, £20M annual budget, 50 UK dealers, channel benchmarks (CPM/CTR/CPC), seasonal multipliers, campaign naming templates
- **Causal chain**: media spend → website sessions → configurator → leads → test drives → sales (sales_pipeline.py reads generated media CSVs)
- **Validation**: 10 checks (file existence, row counts, date ranges, spend ±5% of budget, KPI ranges, no negatives, no NaN in critical columns)
- **MMM aggregation**: validators.py also produces 3 weekly datasets for modeling (52 weeks × 11 channels)
- **Orchestrator import contract**: `generate_all.py` imports MMM aggregation from `data.generators.aggregate_mmm`; keep a module at that path exposing `aggregate_mmm_data` even if implementation lives in `validators.py`.
- **Summary spend verification rule**: `generate_all.py` spend verification should scan only `data/raw/`, ignore `competitor_spend.csv`, and sum only columns named exactly `spend` to avoid double counting and non-channel spend fields.
- Helper functions: `apply_adstock()` (geometric decay), `apply_saturation()` (Hill function), seasonal multipliers

## Environment Variables

Required in `.env` (see `.env.example` for all defaults):
- `OPENAI_API_KEY` — required for RAG pipeline
- RAG: `CHUNK_SIZE=1024`, `CHUNK_OVERLAP=50`, `EMBEDDING_MODEL=text-embedding-3-large`, `QDRANT_PATH=data/qdrant_db`, `LLM_MODEL=claude-opus-4-6`
- Legacy alias: `EMBED_MODEL` remains supported for older modules and should match `EMBEDDING_MODEL`
- MMM: `MMM_DATE_COLUMN=date`, `MMM_TARGET_COLUMN=sales`, `MMM_ADSTOCK_MAX_LAG=8`

## Development Rules

- Iterate on existing patterns before introducing new ones; don't change proven patterns without exhausting alternatives
- Prefer editing existing files over creating new ones
- Keep files under 200-300 lines; refactor at that threshold
- Focus on relevant code areas only; don't touch unrelated code
- Never overwrite `.env` without confirming first
- No stubbing/fake data in dev or prod (tests only)
- Kill existing servers before starting new ones; start a new server after changes
- All modules run from project root (`python -m src.rag.data_processing.run`, not relative imports)
- For text indexing, ingest.py already provides pre-chunked `Document` objects; keep `VectorStoreIndex.from_documents(..., transformations=[])` to avoid implicit re-splitting.
- For asset indexing, use the separate `campaign_assets` Qdrant collection and guarantee each `Document` metadata includes `image_path` (default empty string) so downstream retrieval/UI rendering can rely on that key.
- Persist BM25 lexical index artifacts under `data/index/bm25/`; when available, load via `BM25Retriever.from_persist_dir(...)` instead of rebuilding.
