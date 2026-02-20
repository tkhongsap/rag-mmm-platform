# Issue #81 (Precursor) — MS-2 Dry-Run: Parse, Chunk, Embed, Index (Text-Only, Single Files)

**State:** Draft
**Created:** 2026-02-20
**Updated:** 2026-02-20
**Parent Issue:** [#81 — MS-2: RAG Pipeline — Ingest, Embed, Retrieve](issue-081-ms2-rag-pipeline-ingest-embed-retrieve.md)
**Type:** Pre-flight test / Cost estimation

---

## Objective

Before running the full MS-2 pipeline (embedding all 27+ source documents + asset manifest), validate the entire parse → chunk → embed → index → retrieve workflow with **minimal data and cost**. Pick one representative file from each data category, estimate total embedding cost, and verify the pipeline end-to-end.

---

## Rationale

- **Risk mitigation**: Full production indexing could hit API rate limits, unexpected tokenization errors, or high costs. Testing with 1 file per folder catches bugs early.
- **Cost estimation**: Dry-run estimates tokens and cost (text-embedding-3-large model) before full production run.
- **Architecture validation**: Confirms ingest.py parsing, chunking, Qdrant collection creation, and hybrid retrieval work as designed.
- **Documentation**: Provides baseline numbers (chunk count, tokens, cost per file) for production capacity planning.

---

## Scope: One File Per Data Category

Pick a **single representative file** from each source folder:

| Data Category | Test File | Reason | Estimated Rows/Size |
|---------------|-----------|--------|---------------------|
| **Digital Media CSV** | `data/raw/meta_ads.csv` | Most common CSV type; typical ad spend structure | ~520 rows |
| **Traditional Media CSV** | `data/raw/tv_spend.csv` | Smaller but similar schema | ~52 rows |
| **Sales Pipeline CSV** | `data/raw/vehicle_sales.csv` | Different schema (KPIs vs. spend); validates multi-schema support | ~52 rows |
| **Contracts** | `data/raw/contracts/meta_contract.md` | Representative markdown; tests text chunking strategy | ~3-5 KB |
| **Config** | `data/generators/config.py` | Structured config as searchable text | ~2 KB |
| **Asset Manifest** | `data/assets/asset_manifest.csv` | Single row (or first 5 rows) for asset indexing test | 1–5 rows |

**Total estimated source documents**: ~6 files / ~650 rows + 10 KB text
**Expected chunks** (CSV 20-row windows, text SentenceSplitter): ~40–60 chunks
**Estimated tokens**: ~8K–12K (text-embedding-3-large @ ~$0.02 / 1M tokens) ≈ **$0.0002** (negligible)

---

## High-Level Workflow

```
1. Manual parse step (dry-run):
   - Load meta_ads.csv → inspect 20-row chunking
   - Load tv_spend.csv → inspect chunking
   - Load vehicle_sales.csv → inspect chunking
   - Load meta_contract.md → inspect sentence splitting
   - Load config.py → inspect text parsing
   - Load asset_manifest.csv (5 rows) → inspect asset doc structure

2. Estimate step:
   - Count total chunks
   - Estimate tokens per model (text-embedding-3-large)
   - Report estimated cost

3. Embed step (live API):
   - Create Qdrant collection: dry_run_text_documents
   - Embed sample chunks with OpenAI
   - Store vectors in Qdrant (local, data/qdrant_db/)

4. BM25 index step:
   - Build BM25 index from same sample docs
   - Persist to data/index/bm25/dry_run/

5. Retrieval test:
   - Smoke query: "Meta CPM"
   - Smoke query: "TV spend Q1"
   - Smoke query: "vehicle sales channel"
   - Verify results returned with correct source metadata

6. Report:
   - Print document count, chunk count, token estimate, actual cost
   - Collection stats (vector_count, data size)
   - Sample retrieval results
```

---

## Implementation Approach

### Phase 1: Dry-Run Entry Point (New CLI Flag)

Add `--dry-run` flag to `build_index.py`:

```bash
python -m src.rag.data_processing.build_index \
  --dry-run \
  --text \
  --max-cost-usd 0.10
```

**Behavior**:
- Loads sample files (defined in config or hardcoded in test mode)
- Parses and chunks; does NOT embed
- Prints estimate:
  ```
  Dry-run estimate:
  - Documents: 6
  - Chunks: 52
  - Estimated tokens: 10,240 (text-embedding-3-large)
  - Estimated cost: $0.0002
  - Qdrant collection: dry_run_text_documents
  - BM25 index: data/index/bm25/dry_run/

  Continue with full build? [y/n]
  ```

### Phase 2: Cost-Guarded Embedding

Add `--max-cost-usd` to build_index.py:

```bash
python -m src.rag.data_processing.build_index \
  --dry-run \
  --text \
  --max-cost-usd 0.10
```

**Behavior**:
- Proceeds with embedding only if `actual_cost_estimate <= max_cost_usd`
- If estimate exceeds cap, prints message and aborts
- Stores collection under test namespace (dry_run_text_documents)

### Phase 3: Smoke Tests

Create `tests/rag/test_dry_run_retrieval.py`:

```python
def test_dry_run_text_search():
    """Verify dry-run indexing and retrieval work end-to-end."""
    results = search_text("Meta CPM", collection="dry_run_text_documents")
    assert len(results) > 0
    assert any("meta" in r.text.lower() for r in results)

def test_dry_run_channel_search():
    """Verify multi-CSV schema search."""
    results = search_text("TV spend")
    assert len(results) > 0

def test_dry_run_config_search():
    """Verify config.py retrieval."""
    results = search_text("CPM benchmark")
    assert len(results) > 0
```

### Phase 4: Report Generation

CLI flag `--check-dry-run`:

```bash
python -m src.rag.data_processing.build_index --check-dry-run
```

**Output**:
```
Dry-run index summary:
=====================
Text collection: dry_run_text_documents
  - Vectors: 52
  - Status: ready

BM25 index: data/index/bm25/dry_run/
  - Files: inverted_index.pkl, metadata.json
  - Status: ready

Sample query results:
  Q: "Meta CPM"
  → (score=0.89, source=meta_ads.csv, rows=1-20)
  → (score=0.76, source=config.py, line=45)

Cost summary:
  - Model: text-embedding-3-large
  - Tokens used: 10,240
  - Cost: $0.0002
  - Used capacity: 0.0002 / 0.10 max (0.2%)
```

---

## Acceptance Criteria

### 1. CLI Support

- [ ] `build_index.py` accepts `--dry-run` flag
- [ ] `build_index.py` accepts `--max-cost-usd <float>` flag
- [ ] `build_index.py` accepts `--check-dry-run` flag
- [ ] Help text documents all three flags

### 2. Dry-Run Estimation

- [ ] Dry-run mode loads 6 sample files without errors
- [ ] Dry-run reports document count (6), chunk count (40–60), token estimate
- [ ] Dry-run prints estimated cost (should be ~$0.0002–$0.001)
- [ ] Cost estimate is accurate within 10% of actual API call cost
- [ ] If estimate exceeds `--max-cost-usd`, CLI aborts with clear message

### 3. Parsing & Chunking

- [ ] CSV parser correctly chunks meta_ads.csv at 20-row windows
- [ ] CSV parser correctly chunks tv_spend.csv (52 rows = ~3 chunks)
- [ ] CSV parser correctly chunks vehicle_sales.csv (52 rows = ~3 chunks)
- [ ] Markdown parser correctly splits meta_contract.md into sentences/paragraphs
- [ ] Config parser loads config.py as searchable text (not Python code)
- [ ] Asset parser creates doc per manifest row (5 test rows = 5 docs)

### 4. Embedding & Qdrant

- [ ] Qdrant collection `dry_run_text_documents` created successfully
- [ ] Collection contains exactly 52 vectors (one per chunk)
- [ ] Each vector has metadata: source file, chunk_id, text snippet
- [ ] Vectors persist after script exit (data/qdrant_db/)
- [ ] Re-running dry-run on same corpus does NOT duplicate vectors

### 5. BM25 Index

- [ ] BM25 index persisted to data/index/bm25/dry_run/ (or subfolder)
- [ ] Directory contains inverted index artifacts
- [ ] BM25 can be loaded without rebuild on second run

### 6. Retrieval Smoke Tests

- [ ] Query "Meta CPM" returns top-5 nodes with meta_ads.csv or config.py in source
- [ ] Query "TV spend Q1" returns tv_spend.csv nodes
- [ ] Query "vehicle sales channel" returns vehicle_sales.csv nodes
- [ ] Each result node includes: score, text snippet, source file, chunk_id
- [ ] No errors or exceptions during retrieval

### 7. Report / Check Mode

- [ ] `--check-dry-run` prints collection stats without mutation
- [ ] Report includes vector counts, file paths, estimated cost
- [ ] Sample query results included in report
- [ ] Report is human-readable and suitable for capacity planning

### 8. Code Quality

- [ ] New/modified code passes `py_compile` type checking
- [ ] No hardcoded paths (use env vars or project root)
- [ ] Docstrings on new functions
- [ ] Smoke tests pass: `pytest tests/rag/test_dry_run_retrieval.py -v`

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| **Pipeline runs end-to-end without errors** | ✓ | All 6 files parse, chunk, embed, index successfully |
| **Chunk count matches expectation** | 40–60 chunks | Actual vs. estimate within 5% |
| **Estimated cost < $0.01** | ✓ | Reported by dry-run before embedding |
| **Retrieval returns correct sources** | ✓ | All 3 smoke queries return expected files in top-5 |
| **BM25 + vector hybrid retrieval works** | ✓ | Same queries tested with both retrievers |
| **Cost tracking accurate** | ±10% | Estimated vs. actual API cost |
| **Code is reproducible** | ✓ | Same input always produces same chunk count / vectors |

---

## Files Affected / Created

| File | Change | Lines |
|------|--------|-------|
| `src/rag/data_processing/build_index.py` | New CLI with --dry-run, --max-cost-usd, --check-dry-run | ~80 |
| `src/rag/embeddings/indexer.py` | Add dry-run mode, cost tracking, collection naming | +30 |
| `src/rag/retrieval/query_engine.py` | Add dry-run collection support | +10 |
| `tests/rag/test_dry_run_retrieval.py` | New smoke tests | ~40 |
| `.env.example` | Document EMBEDDING_MODEL, QDRANT_PATH (if not yet) | +2 |

---

## Dependencies

- **MS-1** (#80) — asset manifest must exist (only needed if testing asset indexing; text-only dry-run does not require it)
- **ingest.py** — already exists and loads test files
- **OpenAI API** — OPENAI_API_KEY must be set in .env

---

## Timeline & Rollout

### Step 1: Dry-Run Complete ✓
- CLI flags implemented
- 6 sample files parse and chunk successfully
- Cost estimated before embedding
- Smoke tests pass

### Step 2: Production Build (Issue #81 Follow-up)
- Same pipeline, all 27+ source documents
- No --dry-run flag needed
- Full Qdrant collections: text_documents, campaign_assets
- BM25 index at data/index/bm25/ (no subfolder)
- Full retrieval suite (RAG Chat integration, etc.)

---

## Notes

- **Dry-run collections are ephemeral**: Use `dry_run_*` namespace to avoid conflicts with production collections. Can be deleted before full MS-2 run.
- **Cost tracking matters**: Even though dry-run is cheap, accurate estimates build confidence for full production run.
- **Sample selection is representative**: meta_ads.csv is typical digital media; tv_spend.csv is simpler; vehicle_sales.csv has different KPIs; contracts + config test text parsing. Together, they cover all parsing strategies.
- **Re-run safety**: CLI should not duplicate chunks if dry-run is re-executed on same files (enforce collection drop or update-only semantics).

---

📋 **Next step after dry-run**: [Issue #81 — MS-2 Full Production Build](issue-081-ms2-rag-pipeline-ingest-embed-retrieve.md)

