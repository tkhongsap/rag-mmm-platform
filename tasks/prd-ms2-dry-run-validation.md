# PRD: MS-2 Dry-Run — Validate RAG Pipeline on Sample Data

## Introduction

Before committing to the full MS-2 production build (27+ files), prove the entire RAG pipeline works end-to-end: parse → chunk → embed → index → retrieve. Build the three missing modules (`indexer.py`, `query_engine.py`, `build_index.py`), then test them with one representative file per data category. The result is a working pipeline validated on sample data, with cost guards (`--dry-run`, `--max-cost-usd`) to prevent surprises. This precursor unlocks [Issue #81](../docs/issues/issue-081-ms2-rag-pipeline-ingest-embed-retrieve.md) for the full production build using the same code.

## Goals

- Build the three missing MS-2 modules (indexer, query engine, CLI)
- Validate the pipeline on 1 file per data category (~6 files, ~$0.05 estimated cost)
- Embed with `text-embedding-3-large` into local Qdrant at `data/qdrant_db/`
- Confirm hybrid retrieval (vector + BM25 + reciprocal reranking) returns relevant results
- Provide `--dry-run` cost estimation and `--max-cost-usd` budget guard for safe operation
- Establish a cost baseline to inform the full #81 production run

## User Stories

### US-001: Configuration and environment setup

**Description:** As a developer, I want embedding model and Qdrant path configurable via `.env` so the pipeline is portable across environments.

**Acceptance Criteria:**
- [ ] `.env.example` documents `QDRANT_PATH` with default `data/qdrant_db`
- [ ] `.env.example` documents `EMBEDDING_MODEL` with default `text-embedding-3-large`
- [ ] `requirements.txt` already contains `llama-index-retrievers-bm25`, `qdrant-client`, `llama-index-vector-stores-qdrant` — verify present, no changes needed
- [ ] `data/qdrant_db/` and `data/index/bm25/` added to `.gitignore` if not already
- [ ] Typecheck passes

### US-002: RAGIndexer — Qdrant collections and BM25 index

**Description:** As a platform engineer, I want an indexer that embeds documents into Qdrant and builds a BM25 index so both dense and lexical retrieval are available.

**Acceptance Criteria:**
- [ ] `src/rag/embeddings/indexer.py` exists with `RAGIndexer` class
- [ ] `RAGIndexer.__init__` reads `QDRANT_PATH` and `EMBEDDING_MODEL` from env with defaults
- [ ] `build_text_index(docs: list[Document])` creates `text_documents` collection in Qdrant using `OpenAIEmbedding(model=EMBEDDING_MODEL)`
- [ ] Documents passed directly to `VectorStoreIndex` without additional splitting — `ingest.py` handles pre-chunking (20-row CSV windows, single-doc contracts/config)
- [ ] `build_bm25_index(docs: list[Document])` persists BM25 index to `data/index/bm25/`
- [ ] `build_asset_index(docs: list[Document])` creates `campaign_assets` collection in Qdrant
- [ ] Clean rebuild: drops and recreates collections on each run — no duplicate vectors
- [ ] `estimate(docs: list[Document])` returns dict with `chunk_count`, `estimated_tokens`, `estimated_cost_usd` without calling the OpenAI API
- [ ] Typecheck passes

### US-003: build_index.py CLI with dry-run and cost guard

**Description:** As a developer, I want a CLI that can estimate costs, limit spend, and build indexes incrementally so I can test safely before production.

**Acceptance Criteria:**
- [ ] `src/rag/data_processing/build_index.py` runnable as `python -m src.rag.data_processing.build_index`
- [ ] `--dry-run`: loads and chunks documents, prints estimate (doc count, chunk count, tokens, cost), exits without calling OpenAI
- [ ] `--max-cost-usd <float>`: aborts with clear message if estimated cost exceeds cap
- [ ] `--text`: builds `text_documents` collection + BM25 index only
- [ ] `--assets`: builds `campaign_assets` collection only
- [ ] `--check`: prints collection stats (name, vector count, status) and BM25 index status without mutation
- [ ] `--sample`: loads 1 file per data category instead of all files (see Sample Files table below)
- [ ] No flags defaults to full build (text + assets, all files)
- [ ] Help text (`--help`) documents all flags
- [ ] Typecheck passes

**Sample files** (used with `--sample`):

| Category | File | Rows | Expected Chunks |
|----------|------|------|-----------------|
| Digital media | `data/raw/meta_ads.csv` | 7,920 | ~396 |
| Traditional media | `data/raw/tv_performance.csv` | 305 | ~16 |
| Sales pipeline | `data/raw/vehicle_sales.csv` | 4,600 | ~230 |
| Contract | `data/raw/contracts/MediaAgency_Terms_of_Business.md` | — | 1 |
| Config | `data/generators/config.py` | — | 1 |
| Assets | `data/assets/asset_manifest.csv` | 50 | 50 |

### US-004: Hybrid retrieval — search_text and search_assets

**Description:** As a query consumer, I want hybrid text search combining dense vectors and BM25 lexical matching so retrieval is strong for both semantic and keyword-heavy questions.

**Acceptance Criteria:**
- [ ] `src/rag/retrieval/query_engine.py` exists
- [ ] `search_text(query: str, top_k: int = 5, category: str | None = None)` function
- [ ] `search_text` uses `QueryFusionRetriever` over Qdrant vector retriever + BM25 retriever
- [ ] `search_text` applies reciprocal reranking and returns ranked list of nodes
- [ ] Each returned node has `score`, `text`, and `metadata` (including `source_file`, `category`)
- [ ] `search_assets(query: str, top_k: int = 5, channel: str | None = None)` function
- [ ] `search_assets` queries `campaign_assets` collection and returns nodes with `image_path` metadata
- [ ] `check_indexes()` prints collection stats without mutating indexes
- [ ] Typecheck passes

### US-005: End-to-end dry-run validation

**Description:** As a developer, I want to run the full pipeline on sample files and verify results with smoke queries so I have confidence before the production build.

**Acceptance Criteria:**
- [ ] `python -m src.rag.data_processing.build_index --sample --dry-run` prints estimate without errors
- [ ] Estimated cost for sample files is under $0.10
- [ ] `python -m src.rag.data_processing.build_index --sample --text --max-cost-usd 10` completes successfully
- [ ] `text_documents` collection exists with >0 vectors
- [ ] `data/index/bm25/` directory exists and is non-empty
- [ ] `python -m src.rag.data_processing.build_index --sample --assets --max-cost-usd 10` completes successfully
- [ ] `campaign_assets` collection exists with >0 vectors
- [ ] `python -m src.rag.data_processing.build_index --check` prints stats for both collections
- [ ] Smoke query `"What is Meta CPM?"` returns nodes citing `meta_ads.csv` or `config.py` in top-5
- [ ] Smoke query `"DEEPAL S07 launch creative"` returns nodes with valid `image_path` metadata
- [ ] Re-running the build on same data does not create duplicate vectors
- [ ] Typecheck passes

## Functional Requirements

- FR-1: `indexer.py` creates two Qdrant collections (`text_documents`, `campaign_assets`) in local embedded mode at `QDRANT_PATH`
- FR-2: `indexer.py` builds BM25 index from text documents and persists to `data/index/bm25/`
- FR-3: `indexer.py` provides cost estimation (chunk count, tokens, cost) without calling OpenAI API
- FR-4: `build_index.py` CLI supports `--dry-run`, `--max-cost-usd`, `--text`, `--assets`, `--check`, `--sample` flags
- FR-5: `--sample` loads exactly 6 predefined files (1 per data category) via individual ingest.py loaders
- FR-6: `query_engine.py` implements hybrid retrieval using `QueryFusionRetriever` with reciprocal reranking
- FR-7: Embedding model is `text-embedding-3-large`, configurable via `EMBEDDING_MODEL` env var
- FR-8: Clean rebuild mode drops and recreates collections — no duplicate vectors on re-run
- FR-9: Build aborts before any API calls if `--max-cost-usd` cap is exceeded

## Non-Goals

- Full production indexing of all 27+ files (that is Issue #81)
- Incremental/delta indexing (clean rebuild only for this precursor)
- Query latency optimization or caching
- Sub-question routing or multi-hop retrieval
- Embedding PNG images directly (text-to-image-path via asset manifest metadata only)
- UI integration or RAG Chat page wiring

## Technical Considerations

- **ingest.py is ready**: `load_csv_documents()`, `load_contract_documents()`, `load_config_document()`, `load_asset_documents()` already exist and produce chunked `Document` objects. No modification needed — `--sample` just calls these with specific paths instead of `load_all_text_documents()`.
- **No SentenceSplitter on CSVs**: `ingest.py` pre-chunks CSVs at 20-row windows. Passing them through `SentenceSplitter` would break tabular structure. Documents go directly into `VectorStoreIndex`.
- **BM25 package**: Use `llama-index-retrievers-bm25` (the LlamaIndex integration), not `rank-bm25` (raw library).
- **Cost model**: `text-embedding-3-large` at $0.13/1M tokens. Sample files (~694 chunks, ~347K tokens) ≈ $0.045. Full corpus will be proportionally more but still well under $10.
- **Qdrant embedded mode**: No external server needed. Qdrant stores data at `data/qdrant_db/` on disk.

## Success Metrics

- Pipeline runs end-to-end on 6 sample files without errors
- `--dry-run` cost estimate is within ±20% of actual API cost
- Both Qdrant collections exist with correct vector counts after build
- BM25 index persists and loads without rebuild
- Smoke queries return relevant results with correct source metadata
- Total API cost for sample run is under $0.10

## Open Questions

1. Should `--sample` file list be configurable or always use the 6 predefined files?
2. Should the cost report be saved to a file (e.g., `data/dry_run_report.json`) for reference?
3. For automated tests: mock the OpenAI API (fast, free) or call it live (slow, more realistic)?
