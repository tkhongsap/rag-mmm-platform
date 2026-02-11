# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An enterprise platform combining RAG (Retrieval-Augmented Generation) with Marketing Mix Modeling (MMM). Built with LlamaIndex and OpenAI for the RAG pipeline, and statsmodels/scikit-learn for MMM. English-first, general enterprise use case.

**Two main modules:**
1. **RAG (`src/rag/`)**: 4-stage pipeline — data processing → embeddings → index loading → retrieval with 7 strategies
2. **MMM (`src/mmm/`)**: Marketing mix modeling — data ingestion → modeling → optimization/attribution

Connected through a shared Streamlit UI (`src/ui/`) and platform layer (`src/platform/`).

## Architecture

```
src/
├── rag/                          # RAG pipeline
│   ├── data_processing/          # Stage 1: CSV/document → structured docs
│   ├── embeddings/               # Stage 2: Embedding generation (batch)
│   ├── retrieval/                # Stage 3+4: Index loading + retrieval
│   │   └── retrievers/           # 7 strategy adapters
│   └── common/                   # Shared RAG utilities
├── mmm/                          # Marketing Mix Modeling
│   ├── data_ingestion/           # Media spend, sales data loading
│   ├── modeling/                 # Bayesian/regression MMM models
│   ├── optimization/             # Budget allocation, ROI analysis
│   └── common/                   # Shared MMM utilities
├── platform/                     # Shared platform layer
│   ├── api/                      # REST API (if needed)
│   └── config/                   # Centralized configuration
└── ui/                           # Streamlit multi-page app
    ├── pages/                    # RAG chat, MMM dashboard, data management
    └── components/               # Reusable UI components
```

### RAG Retrieval Strategies
1. **Vector** (`retrieval/retrievers/vector.py`): Semantic similarity search
2. **Summary** (`retrieval/retrievers/summary.py`): Document summary-first retrieval
3. **Recursive** (`retrieval/retrievers/recursive.py`): Hierarchical multi-level retrieval
4. **Metadata** (`retrieval/retrievers/metadata.py`): Fast filtering by attributes
5. **Chunk Decoupling** (`retrieval/retrievers/chunk_decoupling.py`): Separates embedding from content storage
6. **Hybrid** (`retrieval/retrievers/hybrid.py`): Combines vector + keyword (BM25) search
7. **Planner** (`retrieval/retrievers/planner.py`): Multi-step query planning agent

### MMM Components
- **Data Ingestion**: Load media spend (TV, digital, print), sales/KPI data, external factors
- **Modeling**: Adstock transformation, saturation curves, Bayesian regression or OLS
- **Optimization**: Budget allocation across channels, ROI analysis, scenario simulation

## Common Commands

### Installation
```bash
make install                    # Install all dependencies
cp .env.example .env            # Configure environment
```

### RAG Pipeline
```bash
# Data processing
python -m src.rag.data_processing.run

# Generate embeddings
python -m src.rag.embeddings.batch_embedding

# Interactive retrieval CLI
python -m src.rag.retrieval.cli --interactive

# Single query
python -m src.rag.retrieval.cli --query "your question here"
```

### MMM Pipeline
```bash
# Data ingestion
python -m src.mmm.data_ingestion.run

# Run model
python -m src.mmm.modeling.run

# Optimization analysis
python -m src.mmm.optimization.run
```

### Streamlit App
```bash
make run-app                    # Launch multi-page app on port 8501
```

### Testing
```bash
make test                       # Run all tests
make test-rag                   # RAG tests only
make test-mmm                   # MMM tests only
make test-cov                   # Tests with coverage report
python -m pytest tests/ -v      # Verbose output
```

## Environment Setup

Required environment variables in `.env`:
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# RAG Configuration (with defaults)
CHUNK_SIZE=1024
CHUNK_OVERLAP=50
EMBED_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
BATCH_SIZE=10
MAX_WORKERS=4
REQUEST_DELAY=0.1
MAX_RETRIES=3
CLASSIFIER_MODE=llm

# MMM Configuration
MMM_DATE_COLUMN=date
MMM_TARGET_COLUMN=sales
MMM_ADSTOCK_MAX_LAG=8
MMM_CONFIDENCE_LEVEL=0.95
```

## Development Guidelines

### Code Organization
- Single `src/` with subpackages — avoid code duplication across modules
- Prefer editing existing files over creating new ones
- Follow modular architecture: processing → embedding/modeling → output
- Keep files under 200-300 lines; refactor if exceeding
- Check for existing similar functionality before adding new code

### Pattern Consistency
- Iterate on existing patterns before introducing new approaches
- Don't drastically change proven patterns without exhausting alternatives
- Focus on relevant code areas only; don't touch unrelated code
- Use simple solutions and avoid unnecessary complexity

### File Structure
- `src/rag/`: RAG pipeline modules
- `src/mmm/`: Marketing mix model modules
- `src/platform/`: Shared config, API layer
- `src/ui/`: Streamlit pages and components
- `tests/`: pytest suites mirroring `src/` structure
- `references/`: Carried-over methodology docs and guides
- `docs/`: New project documentation
- `data/`: Gitignored data directories

### Performance Optimization
- Use batch processing for large datasets (default: 10 files per batch)
- Enable fast metadata filtering for attribute-heavy queries
- Monitor API rate limits and implement delays
- Adjust `MAX_WORKERS` based on CPU cores
- Choose appropriate retrieval strategy:
  - **Vector**: Fast, simple queries
  - **Hybrid**: Best overall for mixed content
  - **Metadata**: Structured queries with filtering
  - **Planner**: Complex multi-step questions

### Testing Strategy
- Write thorough tests for all major functionality
- Use pytest for unit and integration tests
- Name test files `test_*.py`, keep fixtures colocated
- Test with realistic data samples
- Validate embedding quality and retrieval accuracy
- Validate MMM model outputs against known baselines

### Server Management
- Always kill existing related servers before starting new ones
- Start up a new server after making changes for testing

### Configuration Management
- Never overwrite `.env` files without confirming first
- Use YAML for dataset-specific configurations
- Keep configurations in version control (except secrets)
- Avoid stubbing/fake data in dev or prod environments

## Troubleshooting

### Common Issues

**API Key Errors**: Verify `OPENAI_API_KEY` is set in `.env`

**Memory Issues**: Reduce `BATCH_SIZE`, process smaller datasets, monitor system memory

**Import Errors**: Run from project root, verify dependencies installed (`make install`)

**Missing Embeddings**: Generate embeddings before retrieval (`python -m src.rag.embeddings.batch_embedding`)

**Empty Retrieval Results**: Check embedding quality, try different strategies, verify input data

**Slow Performance**: Use vector strategy for simple queries, enable fast metadata filtering, reduce `top_k`

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
