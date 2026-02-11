# Repository Guidelines

## Project Structure & Module Organization
- `src/rag/` hosts the RAG pipeline modules: data processing, embedding generation, index loading, and retrieval with 7 strategies.
- `src/mmm/` hosts the Marketing Mix Model modules: data ingestion, modeling (Bayesian/regression), and optimization/attribution.
- `src/platform/` provides shared services: centralized config, API layer.
- `src/ui/` contains the Streamlit multi-page app with pages for RAG chat, MMM dashboard, and data management.
- `tests/` holds pytest suites split by `rag/`, `mmm/`, and `integration/`; keep fixtures colocated with their suite.
- `references/` contains methodology docs and guides carried from prior work; `docs/` is for new project documentation.
- `data/` directories are gitignored; generated embeddings and model outputs stay out of version control.

## Build, Test, and Development Commands
- `make install` installs all dependencies from `requirements.txt`.
- `make test` runs the full test suite; `make test-rag` and `make test-mmm` scope to specific modules.
- `make run-app` launches the Streamlit multi-page application.
- `python -m src.rag.retrieval.cli --interactive` runs the RAG retrieval CLI.
- `python -m pytest tests/ -v` for verbose test output; add `-k rag` or `-k mmm` to scope.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, `snake_case` for functions, and constants in `UPPER_SNAKE_CASE`.
- Provide concise docstrings and type hints on public surfaces; prefer module-level config values to inline literals.
- Reuse shared configuration from `src/platform/config/` and `.env` instead of reinventing entry points.

## Testing Guidelines
- Tests use pytest; name files `test_*.py` and keep scenario fixtures lightweight, colocated, and deterministic.
- Run targeted tests after changes: `python -m pytest tests/rag/ -v` or `python -m pytest tests/mmm/ -v`.
- Note any external API dependencies in test docstrings.

## Commit & Pull Request Guidelines
- Write commits in imperative present tense; use prefixes like `feat:`, `fix:`, or `docs:` to clarify intent.
- Keep commits focused, explain behavioral impacts, and update `.env.example` or docs when configuration changes.
- Pull requests link related issues, list validation commands, and include screenshots for UI updates.

## Security & Configuration Tips
- Copy `.env.example` to `.env`, populate `OPENAI_API_KEY`, and never commit secrets.
- Remove large generated artifacts before submitting a PR.
- Prefer tuning batch behavior via environment variables rather than editing code defaults.
