# Issue #81 — MS-2: RAG Pipeline — Ingest, Embed, Retrieve

**State:** Open
**Created:** 2026-02-19T09:54:37Z
**Updated:** 2026-02-19T09:54:37Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/81

---

## Objective

Build the core retrieval engine: load all documents (CSVs, contracts, config, asset descriptions) into LlamaIndex, embed into Qdrant, and expose hybrid search (vector + BM25).

## Current State

- `src/rag/data_processing/ingest.py` exists (279 lines) — full LlamaIndex document loading, review/harden
- Stubs in `embeddings/` and `retrieval/` — need implementation
- No Qdrant collections or BM25 index on disk yet

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Text document loader produces correct document count | >= 19 CSVs + 7 contracts + 1 config = 27+ source documents loaded |
| 2 | Asset document loader produces one doc per image | Document count matches row count in `asset_manifest.csv` |
| 3 | Qdrant collections are populated | `text_documents` and `campaign_assets` collections exist with >0 vectors each |
| 4 | BM25 index persists to disk | `data/index/bm25/` directory exists and is non-empty |
| 5 | Hybrid text search returns relevant results | Query "What is Meta CPM?" returns nodes citing `meta_ads.csv` or `config.py` |
| 6 | Asset search returns relevant results | Query "DEEPAL S07 launch creative" returns nodes with valid `image_path` metadata |
| 7 | Build CLI supports incremental modes | `--text`, `--assets`, `--check` flags all work |

## Tasks

- [ ] **2.1** Create `src/rag/embeddings/indexer.py` (~160 lines) — Two Qdrant collections (`text_documents`, `campaign_assets`) using embedded mode at `data/qdrant_db/`, plus BM25 index persisted to `data/index/bm25/`. Use `OpenAIEmbedding(model="text-embedding-3-small")` and `SentenceSplitter(chunk_size=1024, chunk_overlap=50)`.
- [ ] **2.2** Create `src/rag/retrieval/query_engine.py` (~120 lines) — `build_text_query_engine()` with `QueryFusionRetriever` (vector + BM25, reciprocal rerank), `build_asset_query_engine()` for image description search, `search_text(query, top_k, category)` and `search_assets(query, top_k, channel)` for raw node retrieval.
- [ ] **2.3** Create `src/rag/data_processing/build_index.py` (~50 lines) — CLI entry point supporting `--text`, `--assets`, `--check` flags. Calls `ingest.py` loaders then `indexer.py` build functions.
- [ ] **2.4** Update `.env.example` with optional `QDRANT_PATH` override

## Deliverables

| File | Status | Est. Lines |
|------|--------|-----------|
| `src/rag/data_processing/ingest.py` | Exists — review/harden | 279 |
| `src/rag/data_processing/build_index.py` | New | ~50 |
| `src/rag/embeddings/indexer.py` | New | ~160 |
| `src/rag/retrieval/query_engine.py` | New | ~120 |
| `requirements.txt` | Modify | +2 |
| `.env.example` | Modify | +1 |

## Verification

```bash
python -m src.rag.data_processing.build_index
python -m src.rag.data_processing.build_index --check      # prints collection stats
python -c "
from src.rag.retrieval.query_engine import search_text, search_assets
results = search_text('What is Meta CPM?')
assert len(results) > 0, 'No text results'
print('Text search OK:', len(results), 'results')
results = search_assets('DEEPAL S07 launch creative')
assert len(results) > 0, 'No asset results'
print('Asset search OK:', len(results), 'results')
"
```

## Dependencies

- **MS-1** (#80) — asset manifest and images must exist for asset document loading.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
