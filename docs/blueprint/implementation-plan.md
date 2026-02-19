# RAG + MMM Marketing Intelligence Platform — Implementation Plan

## Context

**Problem**: The platform has a complete data layer (19 CSVs, 7 contracts, 3 MMM-ready weeklies) but the RAG chat is just "Claude reads flat files" — no embeddings, no vector search, no retrieval strategies. The MMM Dashboard is entirely static with hardcoded data. The platform also needs **multimodal search** — users should be able to search campaign images/digital assets alongside text data.

**What exists today**:
- Data generators: fully working (19 CSVs, 7 contracts, 3 MMM weeklies, ~67K rows)
- API: 8 endpoints working (raw dashboard, RAG chat via file reading, data profiles)
- Frontend: 3 pages scaffolded (RagChat, MmmDashboard, DataManagement)
- Agent SDK: basic single-agent chat in `rag_agent.py` (reads files, no embeddings)
- Tests: 85% coverage on API layer
- All dependencies installed (LlamaIndex, statsmodels, scikit-learn, Agent SDK)

**Key decisions**:
1. **Vector DB**: Qdrant (embedded mode for dev — local disk, no Docker needed; Docker for prod)
2. **Embeddings**: OpenAI text-embedding-3-small (1536 dims) for text; image descriptions embedded as text
3. **Retrieval**: Hybrid (vector + BM25 fusion via reciprocal reranking)
4. **Multimodal**: Generate ~50 mock campaign images via PIL, embed their descriptions, search text+images together
5. **Agent orchestration**: Claude Agent SDK with `ClaudeSDKClient` for sessions, MCP tools for RAG search
6. **MMM**: Ridge regression (regularized — only ~17 post-launch data points)
7. **Accuracy target**: 95% retrieval hit rate on curated evaluation set

---

## Architecture

```
User --> React Frontend (port 3001)
         | HTTP
       FastAPI (port 8000)
         |
       Agent SDK Orchestrator (ClaudeSDKClient)
         |-- RAG Agent (subagent, model=sonnet)
         |     tools: mcp__rag__search_data, mcp__rag__search_assets,
         |            mcp__rag__filter_by_channel
         |     --> LlamaIndex hybrid retriever --> Qdrant
         |
         |-- MMM Agent (subagent, model=sonnet)
         |     tools: Read, Bash (runs mmm_scripts/*.py)
         |     --> reads data/mmm/, runs regression/optimization
         |
         +-- [Orchestrator routes by intent]
               "find/show/compare" --> RAG Agent
               "show me creatives/images" --> RAG Agent (asset search)
               "optimize/model/ROI" --> MMM Agent
               combined --> RAG --> MMM chain

       Qdrant (embedded mode -- local disk at ./data/qdrant_db)
         |-- "text_documents" collection (1536-dim, text-embedding-3-small)
         |     CSVs, contracts, config data
         |-- "campaign_assets" collection (1536-dim, description embeddings)
         |     Image metadata + descriptions --> text embeddings
         +-- BM25 index (keyword search, persisted to data/index/bm25)

       data/assets/                      (generated mock campaign images)
         |-- meta/                       ~8 images (social posts, stories)
         |-- google/                     ~6 images (display, search ads)
         |-- tv/                         ~6 images (TV stills, bumpers)
         |-- ooh/                        ~6 images (billboard mockups)
         |-- youtube/, tiktok/, ...      ~24 more across channels
         +-- asset_manifest.csv          (image_path, description, campaign_id,
                                          channel, model, creative_type)
```

---

## Phase 1: RAG Pipeline + Asset Generation

**Goal**: Ingest all data + generate mock images --> embed --> store in Qdrant --> hybrid retrieval working.

### 1.1 Dependencies

**`requirements.txt` additions**:
```
qdrant-client>=1.9.0
llama-index-vector-stores-qdrant>=0.3.0
Pillow>=10.0.0
```

No Docker, no config files, no connection strings. Qdrant runs embedded.

### 1.2 Mock campaign asset generator

**`data/generators/assets.py`** (~180 lines)

Generates ~50 branded campaign images using PIL + metadata manifest.

- Uses campaign naming templates from `data/generators/config.py` (CREATIVE_IDS, AUDIENCE_SEGMENTS, channel list)
- Each image: 800x600 PNG, brand gradient background, channel icon, vehicle name, creative type label
- Outputs to `data/assets/{channel}/` organized by channel
- Generates `data/assets/asset_manifest.csv` with columns:
  `image_path, description, channel, vehicle_model, creative_type, audience_segment, campaign_id, dimensions, file_size`

**Descriptions** are detailed text captions (e.g. "Hero launch creative for DEEPAL S07 -- lifestyle shot targeting EV intenders, used in Meta social campaigns, September 2025 UK launch"). These get embedded as text vectors for search.

**`data/generators/generate_all.py`** (modify) — add Step 8: generate assets.

### 1.3 Document ingestion

**`src/rag/data_processing/ingest.py`** (~200 lines)

Loads all data into LlamaIndex `Document` objects with rich metadata.

**Text documents** (CSVs + contracts + config):
- `load_csv_documents(csv_path)` — groups rows into chunks of ~20, metadata: source_file, file_type, category, columns, row_range, total_rows
- `load_contract_documents(md_path)` — full markdown text, metadata: source_file, file_type=contract, vendor
- `load_config_document()` — `data/generators/config.py` as document (benchmarks, budgets)
- `load_all_text_documents()` — returns all text `Document` objects

**Asset documents** (images):
- `load_asset_documents()` — reads `data/assets/asset_manifest.csv`, creates one `Document` per image with:
  - `text` = description (for embedding)
  - `metadata` = image_path, channel, vehicle_model, creative_type, campaign_id, audience_segment
  - `excluded_embed_metadata_keys` = ["image_path", "dimensions", "file_size"]

**Reuse**: `data/generators/config.py` for channel names, creative IDs, audience segments — used by `_categorize()`.

### 1.4 Embedding + indexing (Qdrant)

**`src/rag/embeddings/indexer.py`** (~160 lines)

Two Qdrant collections + one BM25 index.

```python
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever

QDRANT_PATH = PROJECT_ROOT / "data" / "qdrant_db"
INDEX_DIR = PROJECT_ROOT / "data" / "index"

def build_index(text_documents, asset_documents):
    Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", embed_batch_size=100)
    Settings.text_splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=50)

    client = QdrantClient(path=str(QDRANT_PATH))

    # Collection 1: text documents (CSVs, contracts, config)
    text_store = QdrantVectorStore(client=client, collection_name="text_documents")
    text_ctx = StorageContext.from_defaults(vector_store=text_store)
    text_index = VectorStoreIndex.from_documents(
        text_documents, storage_context=text_ctx, show_progress=True
    )

    # Collection 2: campaign assets (image descriptions as text embeddings)
    asset_store = QdrantVectorStore(client=client, collection_name="campaign_assets")
    asset_ctx = StorageContext.from_defaults(vector_store=asset_store)
    asset_index = VectorStoreIndex.from_documents(
        asset_documents, storage_context=asset_ctx, show_progress=True
    )

    # BM25 index from text nodes (persisted to disk)
    text_nodes = list(text_index.docstore.docs.values())
    bm25 = BM25Retriever.from_defaults(nodes=text_nodes, similarity_top_k=5)
    bm25.persist(str(INDEX_DIR / "bm25"))

def load_indices():
    client = QdrantClient(path=str(QDRANT_PATH))
    text_store = QdrantVectorStore(client=client, collection_name="text_documents")
    asset_store = QdrantVectorStore(client=client, collection_name="campaign_assets")
    text_index = VectorStoreIndex.from_vector_store(text_store)
    asset_index = VectorStoreIndex.from_vector_store(asset_store)
    bm25 = BM25Retriever.from_persist_dir(str(INDEX_DIR / "bm25"))
    return text_index, asset_index, bm25
```

### 1.5 Hybrid retrieval

**`src/rag/retrieval/query_engine.py`** (~120 lines)

Two retrieval modes:

```python
def build_text_query_engine():
    """Hybrid text retrieval: vector + BM25 fusion."""
    text_index, _, bm25 = load_indices()
    vector_retriever = text_index.as_retriever(similarity_top_k=5)
    hybrid = QueryFusionRetriever(
        [vector_retriever, bm25],
        similarity_top_k=5, num_queries=1,
        mode="reciprocal_rerank", use_async=True,
    )
    return RetrieverQueryEngine(retriever=hybrid, ...)

def build_asset_query_engine():
    """Asset search: vector similarity on image descriptions."""
    _, asset_index, _ = load_indices()
    return asset_index.as_retriever(similarity_top_k=10)

def search_text(query, top_k=5, category=None):
    """Raw node retrieval for MCP tool (text)."""
    ...

def search_assets(query, top_k=5, channel=None):
    """Raw node retrieval for MCP tool (images)."""
    # Returns: [{description, image_path, channel, campaign_id, score}]
    ...
```

### 1.6 CLI entry point

**`src/rag/data_processing/build_index.py`** (~50 lines)

```bash
python -m src.rag.data_processing.build_index          # full rebuild (text + assets)
python -m src.rag.data_processing.build_index --text    # text only
python -m src.rag.data_processing.build_index --assets  # assets only
python -m src.rag.data_processing.build_index --check   # verify indices exist
```

### Phase 1 verification

```bash
python data/generators/generate_all.py                  # generates data + assets
python -m src.rag.data_processing.build_index           # ingest + embed into Qdrant
python -c "
from src.rag.retrieval.query_engine import search_text, search_assets
print(search_text('What is Meta CPM?'))                 # text retrieval
print(search_assets('DEEPAL S07 launch creative'))      # asset retrieval
"
```

---

## Phase 2: Agent SDK Orchestration

**Goal**: RAG-first orchestration via Agent SDK. RAG subagent queries Qdrant via MCP tool, exposes asset endpoints, and supports session continuity via `ClaudeSDKClient`. MMM subagent routing is added in Phase 3.

### 2.1 MCP tools (LlamaIndex + Qdrant bridge)

**`src/platform/api/agents/tools.py`** (~120 lines)

Three MCP tools wrapping LlamaIndex:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("search_data",
      "Hybrid semantic+keyword search across marketing data, contracts, and reports",
      {"query": str, "top_k": int, "category": str})
async def search_data(args):
    # Calls query_engine.search_text()
    # Returns: source files, matching text, metadata
    ...

@tool("search_assets",
      "Search campaign digital assets (images, creatives, banners) by description",
      {"query": str, "top_k": int, "channel": str})
async def search_assets(args):
    # Calls query_engine.search_assets()
    # Returns: [{description, image_path, channel, campaign_id, score}]
    ...

@tool("filter_by_channel",
      "Get all data for a specific channel and date range",
      {"channel": str, "start_date": str, "end_date": str})
async def filter_by_channel(args):
    # Metadata-filtered retrieval from Qdrant
    ...

rag_mcp = create_sdk_mcp_server(
    name="rag", tools=[search_data, search_assets, filter_by_channel]
)
```

### 2.2 Agent prompts

**`src/platform/api/agents/prompts.py`** (~250 lines)

Domain-specific prompts with exact file names and column names from `data/generators/config.py`:

- **ORCHESTRATOR_PROMPT** — intent classification, delegation rules, synthesis format, mandatory source citations
- **RAG_AGENT_PROMPT** — knows all 19 CSVs + 7 contracts + ~50 campaign assets, uses `mcp__rag__search_data`, `mcp__rag__search_assets`, and `mcp__rag__filter_by_channel`, cites source files, returns image paths for asset queries
- **MMM_AGENT_PROMPT** — knows `data/mmm/model_ready.csv` structure (52 weeks, adstock columns, controls), runs `mmm_scripts/*.py` via Bash, interprets JSON output

### 2.3 Orchestrator

**`src/platform/api/agents/rag_router.py`** (~160 lines)

```python
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AgentDefinition

# Subagent definition (RAG-first in Phase 2; MMM agent added in Phase 3)
AGENTS = {
    "rag-analyst": AgentDefinition(
        description="Search and retrieve marketing data, contracts, and campaign assets",
        prompt=RAG_AGENT_PROMPT,
        tools=[
            "mcp__rag__search_data",
            "mcp__rag__search_assets",
            "mcp__rag__filter_by_channel",
            "Read",
            "Glob",
        ],
        model="sonnet",
    ),
}

async def ask_with_routing(question: str, session_id: str | None = None) -> dict:
    options = ClaudeAgentOptions(
        system_prompt=ORCHESTRATOR_PROMPT,
        max_turns=15,
        cwd=str(PROJECT_ROOT),
        allowed_tools=["Task", "mcp__rag__search_data", "mcp__rag__search_assets",
                        "mcp__rag__filter_by_channel", "Read"],
        permission_mode="bypassPermissions",
        agents=AGENTS,
        mcp_servers={"rag": rag_mcp},
        resume=session_id,
    )
    # Use ClaudeSDKClient for session persistence
    async with ClaudeSDKClient(options=options) as client:
        await client.query(question, session_id=session_id or "default")
        result_text, sources = [], []
        async for message in client.receive_response():
            # extract text blocks + source citations
            ...
    return {"reply": ..., "sources": ..., "session_id": ...}
```

**Fallback**: If Qdrant index doesn't exist, subagents still have `Read/Glob` and fall back to direct file reading. The `search_data` tool returns a helpful error.

### 2.4 API endpoint updates

**`src/platform/api/main.py`** (modify existing)

- Update `ChatRequest` model: add `session_id: str | None = None`
- Update `POST /api/rag/chat` to call `agents.rag_router.ask_with_routing`
- Return `{"reply": str, "sources": list, "session_id": str, "agent_used": str}`
- Add `GET /api/assets/search?q=...&channel=...` -> `search_assets()` results with image URLs
- Add `GET /api/assets/image/{path}` -> serve image file from `data/assets/` with path normalization; reject traversal patterns (`..`, absolute paths)

### Phase 2 verification

```bash
uvicorn src.platform.api.main:app --reload --port 8000

# RAG query
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our Meta CPM benchmark?"}' | python -m json.tool

# Session continuity
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Compare that to Google","session_id":"<from-above>"}' | python -m json.tool

# Asset search + image serving hardening
curl -s "http://localhost:8000/api/assets/search?q=DEEPAL+launch" | python -m json.tool
curl -i "http://localhost:8000/api/assets/image/../.env"  # expect 400/404
```

---

## Phase 3: MMM Pipeline

**Goal**: Statistical modeling scripts + MMM agent + dashboard summary endpoint, then extend orchestrator routing to delegate MMM intents.

### 3.1 Analysis scripts

**`src/platform/api/mmm_scripts/`** (4 scripts, each ~100 lines)

Standalone Python scripts reading `data/mmm/model_ready.csv`, printing JSON to stdout. The MMM agent runs them via Bash.

| Script | What it does | Key output |
|--------|-------------|------------|
| `regression.py` | Ridge regression (units_sold ~ adstock channels + controls), post-launch weeks only (36-52) | `{r_squared, coefficients, standardized_coefficients, n_observations, ridge_alpha}` |
| `roi_analysis.py` | ROI per channel = (coef x total_spend) / total_revenue | `{channels: [{name, spend, roi, marginal_roi}]}` |
| `budget_optimizer.py` | Shift budget from low-->high marginal ROI (+/-30% constraint per channel) | `{current, optimal, projected_lift_pct}` |
| `adstock_curves.py` | Adstock decay + Hill saturation curves per channel | `{channels: [{name, raw, adstocked, saturated}]}` |

**Why Ridge**: Only ~17 post-launch data points with 11 channels + 3 controls. Ridge handles multicollinearity.

**Reuse**: Adstock decay rates and saturation params from `data/generators/config.py` (ADSTOCK_DECAY_RATES, SATURATION_PARAMS).

### 3.2 Dashboard summary

**`src/platform/api/mmm_summary.py`** (~100 lines)

Pure Python, no agent. Reads `data/mmm/` and returns:
- `total_spend`, `total_units`, `total_revenue`, `total_leads`, `total_test_drives`
- `channel_breakdown` dict (channel --> total spend)
- `weekly_spend` list for timeline chart
- `weeks_of_data`, `post_launch_weeks`

### 3.3 MMM agent

**`src/platform/api/agents/mmm_agent.py`** (~120 lines)

Also update `src/platform/api/agents/rag_router.py` to register `mmm-analyst` and route MMM intents (`optimize`, `model`, `ROI`) to that subagent.

```python
async def ask_mmm_question(question: str) -> dict:
    options = ClaudeAgentOptions(
        system_prompt=MMM_AGENT_PROMPT,
        max_turns=12,
        allowed_tools=["Read", "Bash", "Glob", "Grep"],
        permission_mode="bypassPermissions",
        cwd=str(PROJECT_ROOT),
    )
    # Agent reads data/mmm/, runs mmm_scripts/*.py, interprets JSON output
```

### 3.4 API endpoints

**`src/platform/api/main.py`** (add to existing)

```python
GET  /api/mmm/summary   -> mmm_summary.build_mmm_summary()
POST /api/mmm/chat       -> agents.mmm_agent.ask_mmm_question(question)
# /api/rag/chat now supports MMM intent delegation via updated rag_router
```

### Phase 3 verification

```bash
# Direct script test
python src/platform/api/mmm_scripts/regression.py | python -m json.tool

# API test
curl -s http://localhost:8000/api/mmm/summary | python -m json.tool
curl -s -X POST http://localhost:8000/api/mmm/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"What is the ROI of TV spend?"}' | python -m json.tool
```

---

## Phase 4: Frontend Integration

**Goal**: Wire up the React UI to the new API endpoints.

### 4.1 API client

**`ui/platform/src/api.js`** (modify)

- `sendChatMessage(message, history, sessionId)` — pass session_id, return `{reply, sources, session_id, agent_used}`
- `sendMmmQuestion(question)` — new function --> `POST /api/mmm/chat`
- `getMmmSummary()` — already exists

### 4.2 RAG Chat page

**`ui/platform/src/pages/RagChat.jsx`** (modify)

- Store `sessionId` in component state (persisted in `sessionStorage`)
- Show source files below assistant bubbles (muted list of cited files)
- Show agent badge (rag-analyst / mmm-analyst) next to assistant response
- **Image results**: when response includes `image_path` fields, render thumbnails inline
- Pass session_id in subsequent messages for conversation continuity

### 4.3 MMM Dashboard page

**`ui/platform/src/pages/MmmDashboard.jsx`** (significant rewrite)

- Fetch `/api/mmm/summary` on mount --> populate KPI cards with real data
- Replace `PlaceholderChart` with CSS bar charts from `channel_breakdown` data
- Add "Ask MMM" chat section at bottom (reuse bubble pattern from RagChat)
- Update header badge from "Model not yet trained" to show actual stats
- Error state: show helpful message if backend not running

### 4.4 Asset gallery API + serving

Asset endpoints are implemented in Phase 2 and consumed here by the frontend image grid.

### Phase 4 verification

```bash
cd ui/platform && npm run dev   # http://localhost:3001
# Navigate to RAG Chat -> ask "show me DEEPAL S07 launch creatives" -> see images
# Navigate to RAG Chat -> ask "What is Meta CPM?" -> see text citations
# Navigate to MMM Dashboard -> verify KPI cards show real numbers
# Navigate to MMM Dashboard -> use "Ask MMM" chat -> verify response
```

---

## Phase 5: Evaluation & Polish

**Goal**: Achieve 95% retrieval accuracy, comprehensive tests, production readiness.

### 5.1 Evaluation dataset

**`tests/evaluation/eval_questions.yml`** (~50 questions)

Curated question-answer pairs covering all data categories:

```yaml
- question: "What is the CPM benchmark for Meta ads?"
  expected_sources: ["meta_ads.csv", "config.py"]
  category: digital_media
  expected_keywords: ["CPM", "Meta", "benchmark"]

- question: "What are the payment terms in the ITV contract?"
  expected_sources: ["itv_airtime_agreement.md"]
  category: contracts

- question: "How many vehicles were sold in October 2025?"
  expected_sources: ["vehicle_sales.csv"]
  category: sales_pipeline
```

Balanced across categories: ~15 digital media, ~10 sales pipeline, ~10 contracts, ~10 traditional media, ~5 cross-category.

### 5.2 Retrieval evaluation script

**`tests/evaluation/run_retrieval_eval.py`** (~120 lines)

```python
# For each question:
#   1. Run hybrid retrieval (top_k=5)
#   2. Check if expected_sources appear in retrieved nodes
#   3. Compute hit_rate and MRR
# Report: overall accuracy, per-category breakdown, failing queries
```

**Target**: 95% hit rate (47/50 questions retrieve the correct source file in top-5).

### 5.3 Tuning levers (if below 95%)

1. Increase `top_k` from 5 --> 10 (easy win)
2. Increase `chunk_overlap` from 50 --> 100 (better boundary coverage)
3. Add query expansion (`num_queries=3` in QueryFusionRetriever)
4. Add metadata pre-filtering (if question mentions "Meta" --> filter to category=digital_media)
5. Add document summaries as a retrieval layer (two-stage: summary --> chunks)

### 5.4 Integration tests

**`tests/integration/test_rag_pipeline.py`** (~100 lines)
- Test document loading (correct doc count, metadata)
- Test embedding (index exists in Qdrant)
- Test retrieval (known query --> expected source)

**`tests/integration/test_mmm_scripts.py`** (~80 lines)
- Test each script produces valid JSON
- Test regression R-squared is reasonable (>0.5)
- Test budget optimizer constraints hold

**`tests/integration/test_agent_endpoints.py`** (~60 lines)
- Test RAG chat endpoint returns reply + sources
- Test MMM summary returns expected fields
- Test MMM chat endpoint returns reply

### Phase 5 verification

```bash
# Run evaluation
python tests/evaluation/run_retrieval_eval.py
# Output: Hit Rate: 0.96, MRR: 0.89, Failing: [list]

# Run all tests
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Full end-to-end
python -m src.rag.data_processing.build_index
uvicorn src.platform.api.main:app --reload --port 8000
cd ui/platform && npm run dev
```

---

## File Summary

### Planned files (23; new or major refactor)

```
# RAG Pipeline (Phase 1)
data/generators/assets.py                      ~180 lines  Mock campaign image generator
src/rag/data_processing/ingest.py              ~200 lines  Text + asset document loading
src/rag/data_processing/build_index.py          ~50 lines  CLI to build index
src/rag/embeddings/indexer.py                  ~160 lines  Qdrant + BM25 indexing
src/rag/retrieval/query_engine.py              ~120 lines  Hybrid text + asset retriever

# Agent Orchestration (Phase 2)
src/platform/api/agents/__init__.py              ~5 lines  Module init
src/platform/api/agents/tools.py               ~120 lines  MCP tools (search_data, search_assets, filter_by_channel)
src/platform/api/agents/prompts.py             ~250 lines  All agent system prompts
src/platform/api/agents/rag_router.py          ~160 lines  Multi-agent orchestrator

# MMM Pipeline (Phase 3)
src/platform/api/agents/mmm_agent.py           ~120 lines  MMM analysis agent
src/platform/api/mmm_summary.py                ~100 lines  Dashboard KPIs (no agent)
src/platform/api/mmm_scripts/__init__.py         empty
src/platform/api/mmm_scripts/regression.py     ~100 lines  Ridge regression
src/platform/api/mmm_scripts/roi_analysis.py   ~100 lines  Channel ROI
src/platform/api/mmm_scripts/budget_optimizer.py ~100 lines Budget optimization
src/platform/api/mmm_scripts/adstock_curves.py   ~80 lines Adstock/saturation curves

# Evaluation (Phase 5)
tests/evaluation/eval_questions.yml             ~200 lines  50 curated Q&A pairs (text + asset queries)
tests/evaluation/run_retrieval_eval.py          ~120 lines  Hit rate + MRR eval
tests/integration/test_rag_pipeline.py          ~100 lines  RAG pipeline tests
tests/integration/test_mmm_scripts.py            ~80 lines  MMM script tests
tests/integration/test_agent_endpoints.py        ~60 lines  Agent endpoint tests

# Generated (by build steps, not checked in)
data/assets/                                     ~50 PNGs  Mock campaign images
data/assets/asset_manifest.csv                   manifest  Image metadata + descriptions
data/qdrant_db/                                  binary    Qdrant embedded storage
data/index/bm25/                                 binary    BM25 index files
```

### Modified files (7)

```
requirements.txt                                 ADD: qdrant-client, llama-index-vector-stores-qdrant, Pillow
.env.example                                    ADD: QDRANT_PATH (optional override)
data/generators/generate_all.py                 ADD: Step 8 -- generate assets
src/platform/api/main.py                        ADD: 5 endpoints (rag chat update, mmm summary, mmm chat, asset search, asset serve)
ui/platform/src/api.js                          ADD: session_id, sendMmmQuestion(), searchAssets()
ui/platform/src/pages/RagChat.jsx               ADD: session, sources, agent badge, inline image results
ui/platform/src/pages/MmmDashboard.jsx          REWRITE: live data + Ask MMM chat
```

---

## Implementation Order

| Step | Phase | What | Verify |
|------|-------|------|--------|
| 1 | P1 | `requirements.txt` + install deps | `pip install -r requirements.txt` |
| 2 | P1 | `assets.py` -- mock image generator | `python data/generators/generate_all.py` --> images in `data/assets/` |
| 3 | P1 | `ingest.py` -- text + asset document loading | Unit test: correct doc count + metadata |
| 4 | P1 | `indexer.py` -- embed + store in Qdrant | `python -m src.rag.data_processing.build_index` |
| 5 | P1 | `query_engine.py` -- hybrid + asset retrieval | Python test query for text + images |
| 6 | P2 | `agents/tools.py` -- 3 MCP tools | Import check |
| 7 | P2 | `agents/prompts.py` | Import check |
| 8 | P2 | `agents/rag_router.py` -- orchestrator | curl POST /api/rag/chat |
| 9 | P2 | Update `main.py` -- RAG + asset endpoints | curl test with session_id + asset search |
| 10 | P3 | MMM scripts (all 4) | `python src/platform/api/mmm_scripts/regression.py` |
| 11 | P3 | `mmm_summary.py` + `mmm_agent.py` | curl GET/POST |
| 12 | P3 | Update `main.py` -- MMM endpoints | curl test |
| 13 | P4 | Frontend: `api.js` + `RagChat.jsx` (with image rendering) | Browser test |
| 14 | P4 | Frontend: `MmmDashboard.jsx` | Browser test |
| 15 | P5 | `eval_questions.yml` + eval script (text + asset queries) | 95% hit rate |
| 16 | P5 | Integration tests | `pytest tests/ -v` |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| `OPENAI_API_KEY` not set --> embed fails | `build_index` prints clear error; agent falls back to file reading |
| Qdrant embedded mode limitations at scale | Can switch to Docker mode (`QdrantClient(host="localhost")`) with 1 line change |
| `create_sdk_mcp_server` API mismatch | Verified against `docs/agent-sdk/03_python-reference.md` -- API confirmed |
| Only ~17 post-launch rows for MMM | Ridge regression with regularization; reduce features if needed |
| Asset image endpoint path traversal | Normalize requested paths under `data/assets/` and reject `..` / absolute paths with 400 |
| Agent response time 15-30s | `model="sonnet"` for subagents; loading indicator in UI |
| Below 95% retrieval accuracy | 5 tuning levers: top_k, overlap, query expansion, metadata filter, two-stage retrieval |
| `ClaudeSDKClient` session management | Fallback to `query()` with `resume=session_id` if client mode has issues |
| Image descriptions not distinctive enough | Tune description templates in `assets.py`; add more metadata to embedding text |
| PIL quality for mock images | Sufficient for demo; can replace with real stock photos later |

---

## NOT in scope

- Real campaign photos — using generated mock assets
- Cloud vector DBs (Pinecone, Weaviate) — using local Qdrant embedded
- True CLIP image embeddings — using text-description embeddings (can upgrade later)
- Reranking models (Cohere, BGE) — hybrid fusion sufficient for 95% target
- Streaming SSE responses — can be added later
- File upload/processing — Data Management page stays read-only for now
- Deleting `rag_agent.py` — keep as reference
