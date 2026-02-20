# Issue #82 — MS-3: Agent Orchestration — Multi-Agent Routing (RAG-first)

**State:** Open
**Created:** 2026-02-19T09:55:06Z
**Updated:** 2026-02-19T09:55:06Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/82

---

## Objective

Build the Claude Agent SDK orchestration layer with MCP tools that bridge to LlamaIndex retrieval, RAG-first routing, and session continuity. This milestone is **RAG-only** — MMM routing is added in MS-4b.

## Current State

- `src/platform/api/rag_agent.py` — basic single agent that reads files directly, no embeddings
- No `agents/` directory exists yet
- API has 8 endpoints but no agent routing

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Three MCP tools wrap LlamaIndex retrieval and are assigned to rag-analyst | `search_data`, `search_assets`, `filter_by_channel` importable, callable, and listed in rag-analyst's `tools` array |
| 2 | Orchestrator routes RAG queries correctly | "What is Meta CPM?" → RAG agent; "Show me launch creatives" → RAG agent (asset search) |
| 3 | Session continuity works across requests | Second request with `session_id` references context from first |
| 4 | RAG chat API returns structured response | `POST /api/rag/chat` → `{reply, sources, session_id, agent_used}` |
| 5 | Graceful fallback when Qdrant index missing | Agent falls back to file reading, no crash |

> **Note**: Asset HTTP endpoints (`GET /api/assets/search`, `GET /api/assets/image/{path}`) are in MS-5, not here. MS-3 focuses on the agent/MCP layer only.

## Tasks

- [ ] **3.1** Create `src/platform/api/agents/__init__.py`
- [ ] **3.2** Create `src/platform/api/agents/tools.py` (~120 lines) — Three MCP tools wrapping LlamaIndex: `search_data`, `search_assets`, `filter_by_channel`. Each tool calls the corresponding function in `query_engine.py`. All three must be in the rag-analyst `tools` array.
- [ ] **3.3** Create `src/platform/api/agents/prompts.py` (~250 lines) — `ORCHESTRATOR_PROMPT` (intent classification + delegation rules), `RAG_AGENT_PROMPT` (knows all 19 CSVs, 7 contracts, ~50 assets, uses MCP tools, cites sources), `MMM_AGENT_PROMPT` (placeholder for MS-4b).
- [ ] **3.4** Create `src/platform/api/agents/rag_router.py` (~160 lines) — `ask_with_routing(question, session_id)` using `ClaudeSDKClient`. Defines `rag-analyst` subagent with all 3 MCP tools. Routes "find/show/compare" queries to RAG agent. Returns `{reply, sources, session_id, agent_used}`.
- [ ] **3.5** Update `src/platform/api/main.py` — Modify `POST /api/rag/chat` to accept `session_id`, call `rag_router.ask_with_routing`, return `{reply, sources, session_id, agent_used}`
- [ ] **3.6** Keep `rag_agent.py` as fallback reference (do not delete)

## Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/agents/__init__.py` | New | ~5 |
| `src/platform/api/agents/tools.py` | New | ~120 |
| `src/platform/api/agents/prompts.py` | New | ~250 |
| `src/platform/api/agents/rag_router.py` | New | ~160 |
| `src/platform/api/main.py` | Modify | +40 |

## Verification

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

## Dependencies

- **MS-2** (#81) — Qdrant indices and `query_engine.py` must be operational (though fallback works without them).

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
