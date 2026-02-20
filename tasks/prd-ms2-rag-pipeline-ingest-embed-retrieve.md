# PRD: MS-2 — RAG Pipeline: Ingest, Embed, Retrieve

**Issue:** [#81](https://github.com/tkhongsap/rag-mmm-platform/issues/81)
**Branch:** `fix/issue-81-ms2-rag-pipeline-ingest-embed-retrieve`
**Date:** 2026-02-20

## Introduction

MS-2 delivers the first production-capable RAG retrieval foundation for text and assets. The RAG pipeline should load all supported source documents, create persistent indexes, and expose hybrid retrieval for text and campaign assets. This enables the platform to move from file-based stubs to semantic retrieval against indexed data.

## Goals

- Load all source documents and build consistent chunked embeddings for retrieval.
- Create and persist both Qdrant collections and BM25 index artifacts.
- Provide query APIs for text search and asset search that return ranked, source-rich results.
- Add a CLI that can build text indexes, asset indexes, or print index health.
- Prepare environment wiring for path overrides and local persistence.

## User Stories

### US-001: Build text and asset Qdrant indexes
**Description:** As a platform engineer, I want documents and campaign assets indexed into Qdrant so that retrieval is fast and repeatable.

**Acceptance Criteria:**
- [ ] `src/rag/embeddings/indexer.py` creates `text_documents` and `campaign_assets` collections under `data/qdrant_db/`.
- [ ] Both collections contain vectors generated with `OpenAIEmbedding(model="text-embedding-3-small")`.
- [ ] Document chunks use `SentenceSplitter(chunk_size=1024, chunk_overlap=50)`.
- [ ] `data/index/bm25/` is created and persists non-empty BM25 artifacts after indexing.
- [ ] Running indexing on the same corpus twice replaces or updates vectors deterministically without duplicate failures.

### US-002: Support hybrid text retrieval with reranking
**Description:** As a query consumer, I want text search to combine dense and lexical signals so relevance is strong for both semantic and keyword-heavy questions.

**Acceptance Criteria:**
- [ ] `build_text_query_engine()` exists and uses `QueryFusionRetriever` over Qdrant and BM25.
- [ ] Reciprocal re-rank is enabled and returns a stable top-k list with source metadata.
- [ ] A text query for "What is Meta CPM?" returns nodes from `meta_ads.csv` or `config.py` metadata.
- [ ] `search_text(query, top_k, category)` accepts `category` and returns list-like nodes with `score`, `text`, and metadata fields.

### US-003: Support asset retrieval
**Description:** As a campaign analyst, I want asset descriptions searchable by intent so I can locate visuals and creatives by campaign terms.

**Acceptance Criteria:**
- [ ] `build_asset_query_engine()` exists and targets the `campaign_assets` collection.
- [ ] `search_assets(query, top_k, channel)` returns nodes with `image_path` metadata and path-safe payload fields.
- [ ] A query for "DEEPAL S07 launch creative" returns matching creative entries and image paths.
- [ ] `search_assets()` supports optional channel filter without crashing on unknown channels.

### US-004: Add indexed build and health CLI
**Description:** As an operator, I want a CLI that can run text indexing, asset indexing, and index diagnostics separately.

**Acceptance Criteria:**
- [ ] `src/rag/data_processing/build_index.py` supports `--text`, `--assets`, and `--check` flags.
- [ ] `--check` prints collection statistics and does not mutate indexes.
- [ ] Running the module without flags defaults to full indexing or explicitly documents default behavior in help text.
- [ ] All generated index locations are configurable through environment and resolve to default local paths.

### US-005: Make Qdrant location configurable
**Description:** As a devops operator, I want to override index storage paths to support alternate runtime environments.

**Acceptance Criteria:**
- [ ] `.env.example` documents optional `QDRANT_PATH`.
- [ ] Running with `QDRANT_PATH=/tmp/test_qdrant` creates indexes in that path.
- [ ] `requirements.txt` contains dependencies needed for Qdrant-backed indexing.

## Functional Requirements

- FR-1: Implement `src/rag/embeddings/indexer.py` with robust loaders for both document corpus and asset manifest.
- FR-2: Create vector collections named exactly `text_documents` and `campaign_assets` under `data/qdrant_db/`.
- FR-3: Persist BM25 index data under `data/index/bm25/` and load it for hybrid retrieval.
- FR-4: Implement `src/rag/retrieval/query_engine.py` exposing `build_text_query_engine`, `build_asset_query_engine`, `search_text`, and `search_assets`.
- FR-5: Implement `src/rag/data_processing/build_index.py` with command flags for text indexing, asset indexing, and diagnostics.
- FR-6: Add `QDRANT_PATH` configuration with safe fallback in `.env.example`.

## Non-Goals

- Building any agent orchestration or routing layer.
- Adding new source file formats beyond CSVs, contracts, config, and asset manifest-backed metadata.
- Exposing public search REST API endpoints (covered by MS-3/5).
- Frontend search UX.

## Technical Considerations

- `src/rag/data_processing/ingest.py` already contains loader paths and should be hardened, not replaced.
- Use shared config for path resolution to avoid hardcoding `data/` paths.
- Handle empty corpus and partial failures defensively; indexing should fail with clear errors when required files are absent.
- Keep metadata keys consistent across both vector and BM25 stores so ranking can include same source references.

## Files to Modify

| File | Change |
|------|--------|
| `src/rag/embeddings/indexer.py` | New |
| `src/rag/retrieval/query_engine.py` | New |
| `src/rag/data_processing/build_index.py` | New |
| `src/rag/data_processing/ingest.py` | Review and harden for retrieval inputs |
| `.env.example` | Add `QDRANT_PATH` |
| `requirements.txt` | Add/verify embedding and Qdrant deps |

## Success Metrics

- `data/qdrant_db/text_documents` and `data/qdrant_db/campaign_assets` exist and contain >0 vectors.
- `data/index/bm25/` directory exists and is non-empty after build.
- `search_text("What is Meta CPM?")` returns at least one result and cites expected source files.
- `search_assets("DEEPAL S07 launch creative")` returns at least one result with valid `image_path`.
- CLI `--check` outputs vector and BM25 health without raising.

## Verification

```bash
python -m src.rag.data_processing.build_index
python -m src.rag.data_processing.build_index --check
python -c "from src.rag.retrieval.query_engine import search_text, search_assets; results = search_text('What is Meta CPM?'); assert len(results) > 0, 'No text results'; print('Text search OK:', len(results), 'results'); results = search_assets('DEEPAL S07 launch creative'); assert len(results) > 0, 'No asset results'; print('Asset search OK:', len(results), 'results')"
```

## Open Questions

- Keep 2 local collection names exactly as requested, or allow an environment-driven collection naming convention for multi-tenant use?
