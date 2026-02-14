# RAG + MMM Platform

An enterprise platform combining **Retrieval-Augmented Generation (RAG)** with **Marketing Mix Modeling (MMM)** for data-driven marketing intelligence.

## Architecture

```
src/
├── rag/                 # RAG pipeline (4-stage)
│   ├── data_processing/ # Stage 1: CSV/document → structured docs
│   ├── embeddings/      # Stage 2: Embedding generation (batch)
│   ├── retrieval/       # Stage 3+4: Index loading + retrieval
│   │   └── retrievers/  # 7 strategy adapters
│   └── common/          # Shared RAG utilities
├── mmm/                 # Marketing Mix Modeling
│   ├── data_ingestion/  # Media spend, sales data loading
│   ├── modeling/        # Bayesian/regression MMM models
│   ├── optimization/    # Budget allocation, ROI analysis
│   └── common/          # Shared MMM utilities
├── platform/            # Shared platform layer
│   ├── api/             # REST API
│   └── config/          # Centralized configuration
└── ui/                  # Streamlit multi-page app
    ├── pages/           # RAG chat, MMM dashboard, data management
    └── components/      # Reusable UI components
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM / Embeddings | OpenAI GPT-4o-mini, text-embedding-3-small |
| RAG Framework | LlamaIndex 0.11+ |
| MMM | statsmodels, scikit-learn, scipy |
| Frontend | Streamlit, Plotly |
| Data | pandas, NumPy |
| Testing | pytest, pytest-cov |

## Quick Start

```bash
# Clone
git clone https://github.com/tkhongsap/rag-mmm-platform.git
cd rag-mmm-platform

# Install dependencies
make install

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run tests
make test

# Launch the app
make run-app
```

## Raw Data Inventory Dashboard (React)

Start the FastAPI backend:

```bash
python -m uvicorn src.platform.api.main:app --reload --host 0.0.0.0 --port 8000
```

Start the React dashboard:

```bash
cd ui/raw-data-dashboard
npm install
npm run dev
```

Open `http://localhost:3000` while the API is running on `http://localhost:8000`.

The dashboard surfaces:

- inventory and row/column volume from `data/raw`
- PRD check results from `docs/prd/dashboard_checks.yml`
- file previews for quick sampling

PRD for this dashboard is in `docs/prd/raw-data-dashboard-prd.md`.

## Data Storage Policy

The repository intentionally keeps data artifacts out of Git history:

- `data/raw/*`
- `data/processed/*`
- `data/embeddings/*`
- `data/mmm/*`

Only `.gitkeep` files are tracked to preserve directory structure.

This means files you place in `data/raw/` will not show up in `git status`,
cannot be committed, and therefore cannot be pushed to GitHub.

Use external storage for shared raw datasets (for example: S3, GCS, or an
internal shared drive), then sync data into `data/raw/` locally as needed.

See `docs/data-management.md` for validation commands and workflow details.

## RAG Retrieval Strategies

The platform supports 7 retrieval strategies, automatically selected by an LLM-based router:

1. **Vector** — Semantic similarity search
2. **Summary** — Document summary-first retrieval
3. **Recursive** — Hierarchical multi-level retrieval
4. **Metadata** — Fast filtering by document attributes
5. **Chunk Decoupling** — Separates embedding from content storage
6. **Hybrid** — Combines vector + keyword (BM25) search
7. **Planner** — Multi-step query planning agent

## MMM Capabilities

- Media spend decomposition and attribution
- Adstock and saturation curve modeling
- Budget allocation optimization
- ROI analysis and scenario planning

## Project Structure

```
rag-mmm-platform/
├── src/           # Application source code
├── tests/         # pytest test suites
├── references/    # Methodology docs and guides (carried from prior work)
├── docs/          # Project documentation
├── data/          # Data directories (gitignored)
├── .claude/       # Claude Code skills
├── .cursor/       # Cursor IDE rules
└── .github/       # GitHub config
```

## Development

```bash
make help          # Show all available commands
make test          # Run all tests
make test-rag      # Run RAG tests only
make test-mmm      # Run MMM tests only
make test-cov      # Run tests with coverage
make lint          # Linting checks
make clean         # Remove generated artifacts
```

## License

MIT
