# PRD: MS-3 — Agent Orchestration and Multi-Agent Routing (RAG-first)

**Issue:** [#82](https://github.com/tkhongsap/rag-mmm-platform/issues/82)
**Branch:** `fix/issue-82-ms3-agent-orchestration-multi-agent-routing`
**Date:** 2026-02-22

---

## 1. Introduction / Overview

MS-3 builds the Claude Agent SDK orchestration layer that bridges API requests to LlamaIndex retrieval via MCP tools. The layer provides RAG-first routing, query decomposition for complex questions, and session continuity across requests.

This milestone is **RAG-only** — MMM agent routing is deferred to MS-4b. The scope covers three MCP tools wrapping existing `query_engine.py` functions, a routing orchestrator, prompt-driven decomposition for comparative/multi-timeframe queries, and structured API responses.

## 2. Goals

- Three MCP tools wrap LlamaIndex retrieval (`search_data`, `search_assets`, `filter_by_channel`) and are assigned to `rag-analyst`.
- Orchestrator routes RAG queries correctly (text search vs. asset search).
- Session continuity works across follow-up requests.
- RAG chat API returns structured response: `{reply, sources, session_id, agent_used}`.
- Graceful fallback when Qdrant index is unavailable.
- Complex queries are decomposed into sub-queries, executed individually, and synthesized into a combined answer.

## 3. User Stories

### US-001: Register MCP retrieval tools

**Description:** As a developer, I want MCP tools to expose search functions to the agent so routing is reusable and deterministic.

**Acceptance Criteria:**
- [ ] `src/platform/api/agents/tools.py` defines `search_data`, `search_assets`, and `filter_by_channel` tools.
- [ ] Each tool imports and calls the corresponding function in `src.rag.retrieval.query_engine`.
- [ ] `rag-analyst` has all three tools configured and imported in its tool list.
- [ ] Invalid tool calls return clear validation messages and do not crash the request loop.

### US-002: Add routing prompt and orchestrator

**Description:** As a user-facing system, I want queries to route to the right agent behavior so responses are consistent and useful.

**Acceptance Criteria:**
- [ ] `src/platform/api/agents/prompts.py` defines `ORCHESTRATOR_PROMPT` and `RAG_AGENT_PROMPT`.
- [ ] `ORCHESTRATOR_PROMPT` maps find/search/compare intents to RAG handlers and documents MMM handoff placeholder.
- [ ] `ask_with_routing(question, session_id)` exists and returns `{reply, sources, session_id, agent_used}`.
- [ ] Routing handles both asset and text retrieval intents.

### US-003: Maintain session continuity

**Description:** As a user, I want follow-up questions to preserve context so interactions are conversational rather than stateless.

**Acceptance Criteria:**
- [ ] `POST /api/rag/chat` accepts `session_id` and returns the same or new session ID.
- [ ] A second request with prior `session_id` reuses context and returns coherent follow-up behavior.
- [ ] Missing `session_id` creates a new valid session.

### US-004: Keep fallback behavior when retrieval backend is unavailable

**Description:** As an operator, I want the system to remain usable if Qdrant is unavailable by using direct file reading.

**Acceptance Criteria:**
- [ ] When index dependencies fail, `/api/rag/chat` does not return 500.
- [ ] API response still returns a valid answer format with `agent_used` populated.
- [ ] Fallback path is observable in logs and does not leak stack traces to the client.

### US-005: Preserve existing rag_agent module

**Description:** As a maintainer, I want backward compatibility with current fallback logic.

**Acceptance Criteria:**
- [ ] `src/platform/api/rag_agent.py` is retained unchanged in purpose.
- [ ] New routing layer imports this module only for fallback/reference paths.

### US-006: Query decomposition for complex questions

**Description:** As a user asking comparative or multi-dimensional questions, I want the agent to automatically break my query into targeted sub-queries, execute each, and synthesize a combined answer so I get comprehensive results from a single question.

**Acceptance Criteria:**
- [ ] `prompts.py` includes decomposition instructions and worked examples in `RAG_AGENT_PROMPT` (~80 additional lines across `prompts.py` + `rag_router.py`).
- [ ] Agent detects complex query patterns: multi-entity, multi-timeframe, and cross-category.
- [ ] Agent decomposes into sub-queries and executes each via the appropriate MCP tool with targeted filters (category, channel).
- [ ] Agent synthesizes sub-query results into a combined, coherent answer.
- [ ] Agent states when it is decomposing for transparency ("Let me break this into parts...").
- [ ] Three example patterns are included in the prompt:
  - **Comparative:** "Compare Meta CPM vs Google CPC" → 2 searches (one per platform) → merged comparison.
  - **Multi-timeframe:** "How did TV spend change Q1 to Q3?" → date-filtered searches per period → trend summary.
  - **Cross-category:** "Which channel has best ROI across digital and traditional?" → search digital_media + traditional_media → ranked answer.

## 4. Functional Requirements

- **FR-1:** Add `src/platform/api/agents/__init__.py`.
- **FR-2:** Add MCP tool definitions in `src/platform/api/agents/tools.py` — three tools wrapping `query_engine.py` functions.
- **FR-3:** Add prompts in `src/platform/api/agents/prompts.py` with explicit routing guidance (`ORCHESTRATOR_PROMPT`, `RAG_AGENT_PROMPT`, `MMM_AGENT_PROMPT` placeholder).
- **FR-4:** Implement `src/platform/api/agents/rag_router.py` for `ask_with_routing` and session handling via `ClaudeSDKClient`.
- **FR-5:** Update `src/platform/api/main.py` chat endpoint contract to include `session_id` and `agent_used`.
- **FR-6:** Implement prompt-driven query decomposition (~80 lines across `prompts.py` + `rag_router.py`). Decomposition is handled entirely within the agent prompt — no separate planner module or infrastructure.

## 5. Non-Goals

- MMM agent prompts or routing decisions (MS-4b).
- Frontend rendering of sources, badges, and sessions (MS-5).
- Asset HTTP serving endpoints (`GET /api/assets/search`, `GET /api/assets/image/{path}`) (MS-5).
- Separate planner infrastructure for decomposition — prompt-driven only.

## 6. Technical Considerations

- Use `ClaudeSDKClient` as the orchestration surface for consistency with planned future agents.
- Tools call existing `query_engine.py` functions: `search_text()`, `search_assets()`, `check_indexes()` (from MS-2).
- Keep tool imports lightweight to avoid startup overhead when only fallback path is used.
- Ensure tool return shapes are JSON-serializable and safe for API clients.
- Route classification should be conservative: prioritize clarity over over-aggressive routing.
- Decomposition is prompt-driven — include explicit instructions and examples in `RAG_AGENT_PROMPT`, no separate planner module.

## 7. Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/agents/__init__.py` | New | ~5 |
| `src/platform/api/agents/tools.py` | New | ~120 |
| `src/platform/api/agents/prompts.py` | New | ~330 |
| `src/platform/api/agents/rag_router.py` | New | ~200 |
| `src/platform/api/main.py` | Modify | +40 |

## 8. Success Metrics

- Simple RAG query ("What is our Meta CPM benchmark?") returns `agent_used: rag-analyst`.
- Asset query ("Show me launch creatives") returns `agent_used: rag-analyst` with image-capable sources.
- Complex query ("Compare Meta CPM vs Google CPC in Q3 and Q4") decomposes into sub-queries and synthesizes a combined answer.
- Same `session_id` across follow-up requests returns conversational continuity.
- Graceful fallback when Qdrant is down: no unhandled crash, still returns valid response shape.

## 9. Verification

```bash
uvicorn src.platform.api.main:app --reload --port 8000

# 1. Simple RAG query
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our Meta CPM benchmark?"}' | python -m json.tool

# 2. Complex query (decomposition)
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Compare Meta CPM vs Google CPC in Q3 and Q4"}' | python -m json.tool

# 3. Session continuity (two-step)
SESSION=$(curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is Meta CPM?"}' | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"Compare that to Google\",\"session_id\":\"$SESSION\"}" | python -m json.tool
```

## 10. Open Questions

- Should `session_id` be issued as opaque UUID v4 or a signed token with expiry claims?

## 11. Dependencies

- **MS-2** (#81) — **Completed.** Qdrant indices and `query_engine.py` are operational (fallback works without them).
