# PRD: MS-2 Dry-Run Validation — Parse, Chunk, Embed, Index, Retrieve (Sample Data)

**Issue:** [#81 Precursor — MS-2 Dry-Run Test](../docs/issues/issue-081-ms2-dry-run-test.md)
**Branch:** `ms2-dry-run-validation`
**Status:** Draft
**Created:** 2026-02-20

---

## Introduction

Before indexing all 27+ production documents, validate the entire RAG pipeline (parse → chunk → embed → index → retrieve) with a small, representative sample. The dry-run uses 6 files (1 per data category) to verify embedding costs, document parsing, chunking strategies, Qdrant collection creation, BM25 indexing, and hybrid retrieval end-to-end. Collections are ephemeral (auto-cleanup); only the final report persists for cost baseline and success validation.

**Target User:** Developers running locally during feature development, before submitting PR.

---

## Goals

- Validate the entire ingest → embed → index → retrieve pipeline with minimal cost and risk
- Estimate embedding costs (text-embedding-3-large) with accuracy ±10% of actual API usage
- Confirm parsing handles multi-format data (CSVs, markdown, Python config, manifest)
- Verify chunking strategies preserve data integrity (20-row CSV windows, sentence splitting for text)
- Test hybrid retrieval (vector + BM25 + reciprocal reranking) with smoke queries
- Provide reproducible baseline (same input → same chunk count, vectors, cost)
- Support easy re-run without side effects (ephemeral collections auto-cleanup)

---

## User Stories

### US-001: Add --dry-run CLI flag with cost estimation

**Description:** As a developer, I want to run a dry-run that estimates embedding cost and chunk counts without hitting the API, so I can validate the pipeline design before production.

**Acceptance Criteria:**
- [ ] `build_index.py` accepts `--dry-run` flag
- [ ] Dry-run loads 6 sample files (meta_ads.csv, tv_spend.csv, vehicle_sales.csv, meta_contract.md, config.py, asset_manifest first 5 rows)
- [ ] Dry-run parses and chunks all 6 files without errors
- [ ] Dry-run reports: document count (6), chunk count (40–60), estimated tokens, estimated cost
- [ ] Estimated cost printed before any API calls
- [ ] Cost estimate is accurate within ±10% of actual API cost (validated in later story)
- [ ] Help text documents `--dry-run` flag
- [ ] Typecheck passes

### US-002: Add --max-cost-usd guard to prevent budget overruns

**Description:** As an operator, I want to set a maximum cost cap so the build aborts if estimated cost exceeds my budget.

**Acceptance Criteria:**
- [ ] `build_index.py` accepts `--max-cost-usd <float>` flag
- [ ] If cost estimate exceeds cap, CLI prints error and aborts before embedding
- [ ] Error message includes: estimated cost, cap value, difference
- [ ] Example: `--dry-run --max-cost-usd 0.10` with $0.0002 estimate succeeds; with $0.50 estimate aborts
- [ ] Default behavior (no flag) has no cost cap
- [ ] Help text documents flag and default behavior
- [ ] Typecheck passes

### US-003: Implement parsing and chunking for sample files

**Description:** As a developer, I want the dry-run to parse and chunk CSV, markdown, and config files correctly so I can verify chunking strategies don't break data integrity.

**Acceptance Criteria:**
- [ ] CSV files chunk at 20-row windows (e.g., 520 rows → ~26 chunks)
- [ ] Markdown contracts chunk by sentence/paragraph (SentenceSplitter behavior)
- [ ] Python config loaded as searchable text (not executed)
- [ ] Asset manifest rows parsed as documents (1 row = 1 doc)
- [ ] Chunk metadata includes: source file, chunk_id, text snippet, row range (for CSVs)
- [ ] Dry-run --check prints chunk breakdown by file
- [ ] No errors during parsing (validate with 6 test files)
- [ ] Typecheck passes

### US-004: Create ephemeral Qdrant collections with vectors

**Description:** As a developer, I want sample documents embedded and stored in temporary Qdrant collections so I can test retrieval without polluting production.

**Acceptance Criteria:**
- [ ] Dry-run creates collection: `dry_run_text_documents` (text CSVs + contracts + config)
- [ ] Dry-run creates collection: `dry_run_campaign_assets` (asset manifest descriptions)
- [ ] Collections stored in data/qdrant_db/ (local, embedded Qdrant)
- [ ] Each collection contains correct vector count:
  - dry_run_text_documents: ~52 vectors (all text chunks)
  - dry_run_campaign_assets: 5 vectors (manifest rows)
- [ ] Each vector includes metadata: source file, chunk_id, text
- [ ] Embedding model: OpenAI text-embedding-3-large (configurable via EMBEDDING_MODEL env var)
- [ ] Re-running dry-run on same files does NOT duplicate vectors (collection recreate or idempotent update)
- [ ] Typecheck passes

### US-005: Build BM25 index for sample documents

**Description:** As a retrieval engineer, I want BM25 indexes persisted for sample data so hybrid (vector + lexical) retrieval can be tested.

**Acceptance Criteria:**
- [ ] BM25 index built from sample text docs (same documents as Qdrant collection)
- [ ] BM25 artifacts persisted to `data/index/bm25/dry_run/`
- [ ] Directory contains inverted index files (e.g., `inverted_index.pkl`, `metadata.json`, `tokenizer.json`)
- [ ] BM25 can be loaded on second run without rebuilding
- [ ] BM25 index size > 0 bytes (validate with `ls -la`)
- [ ] Typecheck passes

### US-006: Implement hybrid retrieval with smoke tests

**Description:** As a query consumer, I want to test hybrid text search (vector + BM25 + reranking) with real queries so I know retrieval works end-to-end.

**Acceptance Criteria:**
- [ ] `search_text(query, collection='dry_run_text_documents', top_k=5)` function exists
- [ ] Uses QueryFusionRetriever (Qdrant vector + BM25 lexical retrieval)
- [ ] Applies reciprocal reranking to combined results
- [ ] Query "Meta CPM" returns top-5 nodes:
  - At least 1 node from meta_ads.csv (with row range in metadata)
  - At least 1 node from config.py (with line/section in metadata)
  - Each node includes: score, text snippet, source file
- [ ] Query "TV spend" returns tv_spend.csv nodes in top-5
- [ ] Query "vehicle sales channel" returns vehicle_sales.csv nodes in top-5
- [ ] `search_assets(query, collection='dry_run_campaign_assets', top_k=5)` function exists and works
- [ ] Query "S07 launch creative" returns asset description nodes with image_path metadata
- [ ] No exceptions raised during queries
- [ ] Typecheck passes

### US-007: Implement --check-dry-run report mode

**Description:** As an operator, I want a summary report of dry-run collections, costs, and sample queries so I can validate the build succeeded and understand capacity.

**Acceptance Criteria:**
- [ ] `build_index.py --check-dry-run` prints summary without mutation
- [ ] Report includes:
  - Collection stats: dry_run_text_documents (vector count, approx size)
  - Collection stats: dry_run_campaign_assets (vector count, approx size)
  - BM25 index stats: path, file count, total size
  - Cost summary: model, tokens used, actual cost (from API), budget remaining
- [ ] Report includes 1 sample query result for each collection (e.g., "Meta CPM" for text, "S07" for assets)
- [ ] Report is human-readable and suitable for docs/capacity planning
- [ ] Report runs in <2 seconds (no heavy recomputation)
- [ ] Typecheck passes

### US-008: Implement ephemeral collection cleanup with --cleanup flag

**Description:** As a developer, I want dry-run collections to auto-cleanup after tests pass so the local environment stays clean.

**Acceptance Criteria:**
- [ ] After smoke tests pass, dry_run_* collections deleted from Qdrant
- [ ] BM25 index at data/index/bm25/dry_run/ NOT deleted (for manual inspection if needed)
- [ ] `--cleanup` flag added to explicitly trigger manual cleanup if needed
- [ ] Cleanup status printed: "Dry-run collections cleaned up" or "Cleanup skipped (use --cleanup to force)"
- [ ] Error in cleanup does not fail overall build (logged as warning)
- [ ] Re-running dry-run immediately after cleanup succeeds without conflicts
- [ ] Typecheck passes

### US-009: Add dry-run smoke test suite

**Description:** As a QA engineer, I want automated tests that validate the entire dry-run pipeline so regressions are caught early.

**Acceptance Criteria:**
- [ ] New file: `tests/rag/test_dry_run_pipeline.py`
- [ ] Test: `test_dry_run_dry_estimate()` — parse 6 files, verify chunk count 40–60
- [ ] Test: `test_dry_run_cost_estimation()` — estimate cost, verify ±10% accuracy
- [ ] Test: `test_dry_run_qdrant_collections()` — collections created with correct vector counts
- [ ] Test: `test_dry_run_bm25_index()` — BM25 persisted and loadable
- [ ] Test: `test_dry_run_text_retrieval()` — "Meta CPM" query returns expected sources
- [ ] Test: `test_dry_run_asset_retrieval()` — "S07 launch creative" query returns image_path
- [ ] Test: `test_dry_run_cleanup()` — collections deleted after test
- [ ] All tests pass: `pytest tests/rag/test_dry_run_pipeline.py -v`
- [ ] Tests run in <30 seconds total (avoid long OpenAI API calls in tests; use mocks if needed)

### US-010: Document dry-run workflow in README and .env.example

**Description:** As a new developer, I want clear instructions on how to run the dry-run so I can validate the RAG pipeline locally before production build.

**Acceptance Criteria:**
- [ ] `.env.example` documents:
  - EMBEDDING_MODEL (default: text-embedding-3-large)
  - QDRANT_PATH (default: data/qdrant_db)
  - Any other new env vars introduced
- [ ] `docs/` or `README.md` includes dry-run quickstart:
  - "Run: `python -m src.rag.data_processing.build_index --dry-run --text --assets --max-cost-usd 0.10`"
  - Expected output (chunk count, cost, collection stats)
  - Smoke test examples
- [ ] Instructions include cleanup: "After testing, collections auto-cleanup; BM25 index persists at data/index/bm25/dry_run/"
- [ ] Instructions link to full MS-2 production build docs
- [ ] Typecheck passes

---

## Functional Requirements

- **FR-1:** CLI supports `--dry-run` flag to estimate without embedding
- **FR-2:** CLI supports `--text` flag to index text docs (CSVs, contracts, config)
- **FR-3:** CLI supports `--assets` flag to index asset manifest descriptions
- **FR-4:** CLI supports `--max-cost-usd <float>` to enforce cost cap
- **FR-5:** CLI supports `--check-dry-run` to print collection/cost summary without mutation
- **FR-6:** CLI supports `--cleanup` to manually delete dry_run_* collections
- **FR-7:** Dry-run loads exactly 6 sample files (1 per data category) by default
- **FR-8:** Parsing correctly chunks CSVs at 20-row windows; text at sentence/paragraph boundaries
- **FR-9:** Qdrant collections named `dry_run_text_documents` and `dry_run_campaign_assets`
- **FR-10:** BM25 index persisted to `data/index/bm25/dry_run/`
- **FR-11:** Embedding model configurable via EMBEDDING_MODEL env var (default: text-embedding-3-large)
- **FR-12:** Hybrid retrieval uses QueryFusionRetriever + reciprocal reranking
- **FR-13:** Smoke queries validated: "Meta CPM", "TV spend", "vehicle sales", "S07 launch creative"
- **FR-14:** Dry-run collections auto-cleanup after tests pass; BM25 index persists
- **FR-15:** Cost estimate accurate within ±10% of actual API cost

---

## Non-Goals

- Full production indexing of all 27+ documents (that's MS-2 main build)
- Real-time query latency optimization (smoke tests only)
- Asset image embedding or similarity search (text-to-image-path only)
- Sub-question routing or multi-hop retrieval (simple single-query search only)
- Persistent dry-run results for historical tracking (ephemeral, single-use)
- Dry-run mode for incremental indexing (text/asset choices are independent, not incremental)
- Custom chunking strategies (20-row CSV, SentenceSplitter for text only)

---

## Design Considerations

### CLI Layout

```bash
# Basic dry-run (estimate only)
python -m src.rag.data_processing.build_index --dry-run --text --assets

# With cost cap
python -m src.rag.data_processing.build_index --dry-run --text --assets --max-cost-usd 0.10

# Check collections after build
python -m src.rag.data_processing.build_index --check-dry-run

# Manual cleanup (if auto-cleanup failed or user wants to inspect longer)
python -m src.rag.data_processing.build_index --cleanup
```

### Report Output Example

```
Dry-run report:
===============
Dry-run completed successfully!

Collections:
  dry_run_text_documents
    - Vectors: 52
    - Size: ~500 KB
    - Status: ready
    - Sample query "Meta CPM": 3 results (meta_ads, config, tv_spend)

  dry_run_campaign_assets
    - Vectors: 5
    - Size: ~50 KB
    - Status: ready
    - Sample query "S07 launch creative": 2 results (image_path included)

BM25 Index:
  Path: data/index/bm25/dry_run/
  Files: 3 (inverted_index.pkl, metadata.json, tokenizer.json)
  Size: ~100 KB
  Status: ready

Cost Summary:
  Model: text-embedding-3-large
  Tokens: 10,240
  Cost: $0.0002
  Budget: $0.10
  Used: 0.2%

Next: Run full MS-2 production build (all 27+ documents).
Cleanup: dry_run_* collections will be deleted on next session.
```

---

## Technical Considerations

- **Embedding Model:** text-embedding-3-large (higher quality than text-embedding-3-small; ~20K tokens = $0.0004, well under $0.10 budget)
- **Qdrant:** Local embedded mode (data/qdrant_db/) — no external server needed
- **BM25:** Persisted to allow inspection; not auto-deleted (separate from Qdrant cleanup)
- **Sample Selection:**
  - meta_ads.csv: typical digital media CSV (largest, ~520 rows)
  - tv_spend.csv: traditional media (smaller, ~52 rows)
  - vehicle_sales.csv: different schema (KPIs not spend)
  - meta_contract.md: tests markdown parsing
  - config.py: tests Python config-as-text
  - asset_manifest: 5 rows for asset indexing test
- **Cost Tracking:** Implement token counter before API call; log actual usage after API response
- **Reusable Components:**
  - Reuse `src/rag/data_processing/ingest.py` for loading documents
  - Reuse `src/rag/embeddings/indexer.py` for Qdrant/BM25 creation (once implemented)
  - Build smoke tests in `tests/rag/test_dry_run_pipeline.py`

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| **Pipeline runs end-to-end** | ✓ | All 6 files parse, chunk, embed, index without errors |
| **Chunk count accuracy** | 40–60 chunks | Actual vs. estimate within 5% |
| **Cost estimate accuracy** | ±10% | Estimated vs. actual API cost |
| **All smoke queries return results** | ✓ | 3 text queries + 1 asset query each return ≥1 result |
| **Retrieval sources match expectations** | ✓ | "Meta CPM" returns meta_ads.csv + config.py in top results |
| **BM25 index persists** | ✓ | data/index/bm25/dry_run/ non-empty after build |
| **Collections auto-cleanup** | ✓ | dry_run_* collections deleted after tests |
| **Reproducibility** | ✓ | Same input produces same chunk count / vector count |

---

## Open Questions

1. Should dry-run support custom sample file selection, or always use the fixed 6 files?
2. Should BM25 index also auto-cleanup, or persist for inspection?
3. Should smoke tests use mocked OpenAI API (faster, but less realistic) or real API calls (slower, but validates end-to-end)?
4. Should cost estimates include latency/rate-limit warnings?
5. Should dry-run report be saved to file (e.g., `data/dry_run_report.json`) for CI/CD integration?

---

## Dependencies

- **MS-1** (#80) — asset manifest must exist
- **ingest.py** — already exists; dry-run reuses it
- **OpenAI API** — OPENAI_API_KEY required in .env
- **LlamaIndex** — QueryFusionRetriever, OpenAIEmbedding

---

## Rollout Plan

### Phase 1: Dry-Run (This PRD)
✓ Validate parse/chunk/embed/index/retrieve with 6 sample files
✓ Cost estimation (<$0.01)
✓ Ephemeral collections auto-cleanup
✓ Smoke tests pass locally

### Phase 2: Production Build (MS-2 Main, #81)
→ Same pipeline, all 27+ documents
→ Persistent collections: text_documents, campaign_assets
→ BM25 at data/index/bm25/ (no subfolder)
→ Full RAG Chat integration

---

## Files Created/Modified

| File | Change | Est. Lines |
|------|--------|-----------|
| `src/rag/data_processing/build_index.py` | New CLI with --dry-run, --max-cost-usd, --check-dry-run, --cleanup | ~100 |
| `src/rag/embeddings/indexer.py` | Add dry-run mode, cost tracking, collection naming (will be created in earlier story) | +40 |
| `src/rag/retrieval/query_engine.py` | Add dry-run collection support (will be created in earlier story) | +15 |
| `tests/rag/test_dry_run_pipeline.py` | New smoke test suite | ~120 |
| `.env.example` | Document EMBEDDING_MODEL, QDRANT_PATH | +2 |
| `docs/README.md` or `docs/DRY_RUN.md` | Quickstart guide and instructions | ~30 |

---

## Summary

The dry-run is a **low-cost, high-confidence pre-flight check** for MS-2. Developers run it locally during feature development; it validates the entire pipeline with 6 representative files, estimates real costs, and cleans up after itself. Success unlocks the production MS-2 build with confidence.

