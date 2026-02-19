# Team Milestones & Key Results

> Companion to [`implementation-plan.md`](./implementation-plan.md).
> Use this document for sprint planning, stand-ups, and cross-team coordination.

---

## Dependency Graph

```
MS-1 ──→ MS-2 ──→ MS-3 ────────────────┐
  └────────────→ MS-4a ──→ MS-4b ──────┤──→ MS-5 ──→ MS-6 ──→ MS-7
                      (depends on MS-3) ┘
```

- **MS-1** is the data foundation — everything else depends on it.
- **MS-2** (RAG) and **MS-4a** (MMM scripts) can run in parallel once MS-1 is done.
- **MS-3** is now explicitly RAG-first only (chat + assets + sessions).
- **MS-4b** is where MMM intent delegation is added to the orchestrator.
- **MS-5** (frontend) requires both agent layers (MS-3 + MS-4b) to be API-ready.
- **MS-7** is a future-scope placeholder — no implementation work yet.

### Before vs After (Compact)

**Before (implicit in old KRs, inconsistent):**
```
MS-1 → MS-2 → MS-3 (RAG + MMM routing implied) → MS-5 → MS-6 → MS-7
MS-4a → MS-4b ------------------------------------^
```

**After (corrected and decision-consistent):**
```
MS-1 → MS-2 → MS-3 (RAG-first)
MS-1 → MS-4a → MS-4b (MMM agent + MMM routing in orchestrator)
MS-3 + MS-4b → MS-5 → MS-6 → MS-7
```

---

## MS-1: Synthetic Data & Mock Assets

**Objective**: Extend the existing data generators with campaign image assets so every downstream pipeline has complete input data.

### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Mock campaign image generator produces branded PNGs | >= 50 images across 10 channels in `data/assets/{channel}/` |
| 2 | Asset manifest is complete and valid | `data/assets/asset_manifest.csv` exists with columns: `image_path`, `description`, `channel`, `vehicle_model`, `creative_type`, `audience_segment`, `campaign_id`, `dimensions`, `file_size` |
| 3 | `generate_all.py` runs end-to-end including new Step 8 | Exit code 0, all 10 validation checks pass, images present |
| 4 | Pillow added to dependencies | `Pillow>=10.0.0` in `requirements.txt`, installs cleanly |

### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `data/generators/assets.py` | Exists — review/harden | 326 |
| `data/generators/generate_all.py` | Exists — Step 8 present | — |
| `requirements.txt` | Modify | +1 |

### Dependencies

- None — this is the root milestone.

### Verification

```bash
pip install -r requirements.txt
python data/generators/generate_all.py
ls data/assets/meta/ data/assets/google/ data/assets/tv/   # images exist
wc -l data/assets/asset_manifest.csv                       # >= 51 (header + 50 rows)
python data/generators/generate_all.py --validate-only     # all checks pass
```

---

## MS-2: RAG Pipeline — Ingest, Embed, Retrieve

**Objective**: Build the core retrieval engine: load all documents (CSVs, contracts, config, asset descriptions) into LlamaIndex, embed into Qdrant, and expose hybrid search (vector + BM25).

### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Text document loader produces correct document count | >= 19 CSVs + 7 contracts + 1 config = 27+ source documents loaded |
| 2 | Asset document loader produces one doc per image | Document count matches row count in `asset_manifest.csv` |
| 3 | Qdrant collections are populated | `text_documents` and `campaign_assets` collections exist with >0 vectors each |
| 4 | BM25 index persists to disk | `data/index/bm25/` directory exists and is non-empty |
| 5 | Hybrid text search returns relevant results | Query "What is Meta CPM?" returns nodes citing `meta_ads.csv` or `config.py` |
| 6 | Asset search returns relevant results | Query "DEEPAL S07 launch creative" returns nodes with valid `image_path` metadata |
| 7 | Build CLI supports incremental modes | `--text`, `--assets`, `--check` flags all work |

### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/rag/data_processing/ingest.py` | Exists — review/harden | 279 |
| `src/rag/data_processing/build_index.py` | New | ~50 |
| `src/rag/embeddings/indexer.py` | New | ~160 |
| `src/rag/retrieval/query_engine.py` | New | ~120 |
| `requirements.txt` | Modify | +2 |
| `.env.example` | Modify | +1 |

### Dependencies

- **MS-1** — asset manifest and images must exist for asset document loading.

### Verification

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

---

## MS-3: Agent Orchestration — Multi-Agent Routing

**Objective**: Build the Claude Agent SDK orchestration layer with MCP tools that bridge to LlamaIndex retrieval, RAG-first routing, asset APIs, and session continuity. MMM routing is enabled in MS-4b.

### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Three MCP tools wrap LlamaIndex retrieval and are assigned to rag-analyst | `search_data`, `search_assets`, `filter_by_channel` importable, callable, and listed in rag-analyst's `tools` array |
| 2 | Orchestrator routes RAG queries correctly | "What is Meta CPM?" → RAG agent; "Show me launch creatives" → RAG agent (asset search) |
| 3 | Session continuity works across requests | Second request with `session_id` references context from first |
| 4 | RAG chat API returns structured response | `POST /api/rag/chat` → `{reply, sources, session_id, agent_used}` |
| 5 | Graceful fallback when Qdrant index missing | Agent falls back to file reading, no crash |

### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/agents/__init__.py` | New | ~5 |
| `src/platform/api/agents/tools.py` | New | ~120 |
| `src/platform/api/agents/prompts.py` | New | ~250 |
| `src/platform/api/agents/rag_router.py` | New | ~160 |
| `src/platform/api/main.py` | Modify | +40 |

### Dependencies

- **MS-2** — Qdrant indices and `query_engine.py` must be operational (though fallback works without them).

### Verification

```bash
uvicorn src.platform.api.main:app --reload --port 8000

# RAG query
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our Meta CPM benchmark?"}' | python -m json.tool

# Session continuity
SESSION=$(curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is Meta CPM?"}' | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"Compare that to Google\",\"session_id\":\"$SESSION\"}" | python -m json.tool

```

---

## MS-4: MMM Pipeline — Statistical Models + Agent

Split into two sub-milestones to enable parallel work:

### MS-4a: MMM Analysis Scripts

**Objective**: Build standalone statistical modeling scripts that read `data/mmm/model_ready.csv` and output JSON results to stdout.

#### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Ridge regression produces valid output | `regression.py` outputs JSON with `r_squared > 0.5`, `coefficients` dict, `coefficient_magnitudes` (normalized importance ranking) |
| 2 | ROI analysis computes per-channel ROI | `roi_analysis.py` outputs JSON with all 11 channels, `roi` and `marginal_roi` per channel |
| 3 | Budget optimizer respects constraints | `budget_optimizer.py` output: each channel within ±30% of current, total budget unchanged |
| 4 | Adstock curves render decay and saturation | `adstock_curves.py` outputs per-channel `raw`, `adstocked`, `saturated` arrays |
| 5 | Dashboard summary returns KPIs | `mmm_summary.py` returns `total_spend`, `total_units`, `channel_breakdown`, `weekly_spend` |

#### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/mmm_scripts/__init__.py` | New | empty |
| `src/platform/api/mmm_scripts/regression.py` | New | ~100 |
| `src/platform/api/mmm_scripts/roi_analysis.py` | New | ~100 |
| `src/platform/api/mmm_scripts/budget_optimizer.py` | New | ~100 |
| `src/platform/api/mmm_scripts/adstock_curves.py` | New | ~80 |
| `src/platform/api/mmm_summary.py` | New | ~100 |

#### Dependencies

- **MS-1** — `data/mmm/model_ready.csv` must exist (already generated by existing data pipeline).

#### Verification

```bash
python src/platform/api/mmm_scripts/regression.py | python -m json.tool
python src/platform/api/mmm_scripts/roi_analysis.py | python -m json.tool
python src/platform/api/mmm_scripts/budget_optimizer.py | python -m json.tool
python src/platform/api/mmm_scripts/adstock_curves.py | python -m json.tool
python -c "
from src.platform.api.mmm_summary import build_mmm_summary
s = build_mmm_summary()
assert 'total_spend' in s and 'channel_breakdown' in s
print('Summary OK')
"
```

### MS-4b: MMM Agent + API Endpoints

**Objective**: Wrap the MMM scripts with a Claude Agent SDK agent, expose API endpoints, and extend the orchestrator to route MMM intents.

#### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | MMM agent can answer ROI questions | `POST /api/mmm/chat` with "What is TV ROI?" returns a substantive answer |
| 2 | MMM summary endpoint returns live data | `GET /api/mmm/summary` returns JSON with >= 5 fields |
| 3 | Agent runs scripts via Bash tool | Agent response references actual regression/ROI numbers |
| 4 | Orchestrator routes MMM queries correctly | "Optimize budget" → MMM agent; response references regression/ROI numbers |

#### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/agents/mmm_agent.py` | New | ~120 |
| `src/platform/api/agents/rag_router.py` | Modify | +40 |
| `src/platform/api/main.py` | Modify | +20 |

#### Dependencies

- **MS-3** — base orchestrator and RAG routing must be operational.
- **MS-4a** — scripts must produce valid JSON output.

#### Verification

```bash
uvicorn src.platform.api.main:app --reload --port 8000
curl -s http://localhost:8000/api/mmm/summary | python -m json.tool
curl -s -X POST http://localhost:8000/api/mmm/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the ROI of TV spend?"}' | python -m json.tool
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Optimize budget by channel"}' | python -m json.tool
```

---

## MS-5: Frontend Integration

**Objective**: Wire the React UI to live backend data — real RAG responses with sources, session continuity, inline image results, and live MMM dashboard.

### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | RAG Chat shows source citations | Assistant bubbles display list of cited source files |
| 2 | RAG Chat supports session continuity | `sessionId` stored in `sessionStorage`, passed on subsequent messages |
| 3 | RAG Chat renders inline image results | Asset search queries display thumbnail grid with metadata |
| 4 | RAG Chat shows agent badge | Response indicates which agent (rag-analyst / mmm-analyst) answered |
| 5 | MMM Dashboard shows live KPIs | KPI cards populated from `GET /api/mmm/summary` (not hardcoded) |
| 6 | MMM Dashboard shows channel breakdown | CSS bar chart renders `channel_breakdown` data from API |
| 7 | MMM Dashboard has "Ask MMM" chat | Chat section at bottom sends to `POST /api/mmm/chat` |
| 8 | Error states handled gracefully | Helpful message shown when backend is not running |
| 9 | Asset search API endpoint works | `GET /api/assets/search?q=...` returns results with image URLs |
| 10 | Asset image serving is safe and functional | `GET /api/assets/image/{path}` returns image bytes; path traversal outside `data/assets/` is rejected |

### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `ui/platform/src/api.js` | Modify | +30 |
| `ui/platform/src/pages/RagChat.jsx` | Modify | +80 |
| `ui/platform/src/pages/MmmDashboard.jsx` | Rewrite | ~250 |

### Dependencies

- **MS-3** — RAG chat API and asset endpoints must be live.
- **MS-4b** — MMM summary and chat endpoints must be live.

### Verification

```bash
# Start backend and frontend
uvicorn src.platform.api.main:app --reload --port 8000 &
cd ui/platform && npm run dev &

# Manual browser testing:
# 1. RAG Chat → ask "show me DEEPAL S07 launch creatives" → images render
# 2. RAG Chat → ask "What is Meta CPM?" → source citations appear
# 3. RAG Chat → ask follow-up → session continuity works
# 4. MMM Dashboard → KPI cards show real numbers
# 5. MMM Dashboard → "Ask MMM" → type "What is TV ROI?" → response renders
# 6. Stop backend → pages show error state

# Asset endpoints
curl -s "http://localhost:8000/api/assets/search?q=DEEPAL+launch" | python -m json.tool
curl -i "http://localhost:8000/api/assets/image/../.env"  # expect 400/404
```

---

## MS-6: Evaluation & Testing

**Objective**: Validate retrieval quality with a curated evaluation set, achieve 95% hit rate, and add integration tests across all pipelines.

### Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Evaluation dataset covers all data categories | 50 questions: ~15 digital media, ~10 sales, ~10 contracts, ~10 traditional, ~5 cross-category |
| 2 | Retrieval hit rate meets target | >= 95% (47/50 questions retrieve correct source in top-5) |
| 3 | MRR is acceptable | Mean Reciprocal Rank >= 0.80 |
| 4 | RAG pipeline integration tests pass | Document loading, embedding, retrieval all tested |
| 5 | MMM script integration tests pass | Each script produces valid JSON, regression R² > 0.5, optimizer constraints hold |
| 6 | Agent endpoint integration tests pass | RAG chat, MMM summary, MMM chat all return expected response shapes |
| 7 | Overall test coverage maintained | `pytest --cov` reports >= 80% on `src/` (baseline: 85% on API layer) |

### Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `tests/evaluation/eval_questions.yml` | New | ~200 |
| `tests/evaluation/run_retrieval_eval.py` | New | ~120 |
| `tests/integration/test_rag_pipeline.py` | New | ~100 |
| `tests/integration/test_mmm_scripts.py` | New | ~80 |
| `tests/integration/test_agent_endpoints.py` | New | ~60 |

### Dependencies

- **MS-5** — all pipelines and endpoints must be functional before evaluation.

### Tuning Levers (if below 95%)

1. Increase `top_k` from 5 → 10
2. Increase `chunk_overlap` from 50 → 100
3. Enable query expansion (`num_queries=3` in QueryFusionRetriever)
4. Add metadata pre-filtering (channel-specific queries)
5. Add document summary layer (two-stage retrieval)

### Verification

```bash
python tests/evaluation/run_retrieval_eval.py
# Expected: Hit Rate: >= 0.95, MRR: >= 0.80

python -m pytest tests/integration/ -v
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## MS-7: Cloud Migration (Future)

**Objective**: Move from local-disk infrastructure to cloud-ready deployment. This is a **placeholder milestone** — scope will be refined when MS-1 through MS-6 are complete.

### Key Results (Provisional)

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Qdrant runs as managed service | Qdrant Cloud instance provisioned, collections migrated |
| 2 | Assets served from object storage | Campaign images in S3/GCS, asset URLs point to cloud |
| 3 | Application is containerized | `Dockerfile` + `docker-compose.yml` build and run successfully |
| 4 | CI/CD pipeline exists | GitHub Actions workflow: lint → test → build → deploy |
| 5 | Environment config externalized | All secrets via env vars / secret manager, no local `.env` required |

### Deliverables (Provisional)

| File | Type |
|------|------|
| `Dockerfile` | New |
| `docker-compose.yml` | New |
| `.github/workflows/ci.yml` | New |
| Infrastructure configuration | TBD |

### Dependencies

- **MS-6** — all tests passing and evaluation targets met before migration.

### Verification

```bash
docker-compose up --build
# Application accessible at configured port
# All integration tests pass against containerized services
```

---

## File → Milestone Mapping

Every file from the implementation plan's File Summary is accounted for below.

### New Files (20) + Existing Files (3)

| File | Milestone | Status |
|------|-----------|--------|
| `data/generators/assets.py` | MS-1 | Exists (326 lines) |
| `src/rag/data_processing/ingest.py` | MS-2 | Exists (279 lines) |
| `src/rag/data_processing/build_index.py` | MS-2 | New |
| `src/rag/embeddings/indexer.py` | MS-2 | New |
| `src/rag/retrieval/query_engine.py` | MS-2 | New |
| `src/platform/api/agents/__init__.py` | MS-3 | New |
| `src/platform/api/agents/tools.py` | MS-3 | New |
| `src/platform/api/agents/prompts.py` | MS-3 | New |
| `src/platform/api/agents/rag_router.py` | MS-3, MS-4b | New |
| `src/platform/api/mmm_scripts/__init__.py` | MS-4a | New |
| `src/platform/api/mmm_scripts/regression.py` | MS-4a | New |
| `src/platform/api/mmm_scripts/roi_analysis.py` | MS-4a | New |
| `src/platform/api/mmm_scripts/budget_optimizer.py` | MS-4a | New |
| `src/platform/api/mmm_scripts/adstock_curves.py` | MS-4a | New |
| `src/platform/api/mmm_summary.py` | MS-4a | New |
| `src/platform/api/agents/mmm_agent.py` | MS-4b | New |
| `tests/evaluation/eval_questions.yml` | MS-6 | New |
| `tests/evaluation/run_retrieval_eval.py` | MS-6 | New |
| `tests/integration/test_rag_pipeline.py` | MS-6 | New |
| `tests/integration/test_mmm_scripts.py` | MS-6 | New |
| `tests/integration/test_agent_endpoints.py` | MS-6 | New |
| `data/assets/` (generated PNGs) | MS-1 (generated) | Exists |
| `data/assets/asset_manifest.csv` | MS-1 (generated) | Exists |

### Modified Files (7)

| File | Milestone | Change |
|------|-----------|--------|
| `requirements.txt` | MS-1, MS-2 | Add Pillow, qdrant-client, llama-index-vector-stores-qdrant |
| `.env.example` | MS-2 | Add QDRANT_PATH |
| `data/generators/generate_all.py` | MS-1 | Step 8 already present — review/harden |
| `src/platform/api/main.py` | MS-3, MS-4b | Add 5 endpoints |
| `ui/platform/src/api.js` | MS-5 | Add session_id, sendMmmQuestion(), searchAssets() |
| `ui/platform/src/pages/RagChat.jsx` | MS-5 | Add sessions, sources, agent badge, image results |
| `ui/platform/src/pages/MmmDashboard.jsx` | MS-5 | Rewrite with live data + Ask MMM chat |

### Generated Artifacts (not checked in)

| Path | Milestone | Notes |
|------|-----------|-------|
| `data/qdrant_db/` | MS-2 | Qdrant embedded storage |
| `data/index/bm25/` | MS-2 | BM25 index files |

---

## Parallel Work Opportunities

| Parallel Track A | Parallel Track B | When |
|-----------------|-----------------|------|
| MS-2 (RAG pipeline) | MS-4a (MMM scripts) | After MS-1 completes |
| MS-3 (Agent orchestration) | MS-4a (MMM scripts, if not done) | After MS-2 completes |
| MS-6 eval dataset authoring | MS-5 frontend work | Can draft questions early |
