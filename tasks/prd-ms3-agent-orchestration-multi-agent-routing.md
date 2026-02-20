# PRD: MS-3 — Agent Orchestration and Multi-Agent Routing (RAG-first)

**Issue:** [#82](https://github.com/tkhongsap/rag-mmm-platform/issues/82)
**Branch:** `fix/issue-82-ms3-agent-orchestration-multi-agent-routing`
**Date:** 2026-02-20

## Introduction

MS-3 implements the orchestration layer that routes user queries to specialized agents and bridges API requests to retrieval tools. It adds stable session continuity and explicit API response shape while keeping an MMM migration path in MS-4b.

## Goals

- Introduce tool-based MCP wrappers around RAG retrieval functions.
- Add routing logic that decides whether a query should be handled by RAG workflows.
- Keep response payload stable for UI consumption.
- Preserve a fallback path when retrieval infrastructure is unavailable.

## User Stories

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

## Functional Requirements

- FR-1: Add `src/platform/api/agents/__init__.py`.
- FR-2: Add MCP tool definitions in `src/platform/api/agents/tools.py`.
- FR-3: Add prompts in `src/platform/api/agents/prompts.py` with explicit routing guidance.
- FR-4: Implement `src/platform/api/agents/rag_router.py` for `ask_with_routing` and session handling.
- FR-5: Update `src/platform/api/main.py` chat endpoint contract to include `session_id` and `agent_used`.

## Non-Goals

- MMM agent prompts or routing decisions (handled in MS-4b).
- Frontend rendering of sources, badges, and sessions (handled in MS-5).
- Asset HTTP serving endpoints (also MS-5).

## Technical Considerations

- Use `ClaudeSDKClient` as the orchestration surface for consistency with planned future agents.
- Keep tool imports lightweight to avoid startup overhead when only fallback path is used.
- Ensure tool return shapes are serializable and safe for JSON clients.
- Route classification should be conservative: prioritize clarity over over-aggressive routing.

## Files to Modify

| File | Change |
|------|--------|
| `src/platform/api/agents/__init__.py` | New |
| `src/platform/api/agents/tools.py` | New |
| `src/platform/api/agents/prompts.py` | New |
| `src/platform/api/agents/rag_router.py` | New |
| `src/platform/api/main.py` | Update chat endpoint response/inputs |

## Success Metrics

- `POST /api/rag/chat` with "What is our Meta CPM benchmark?" returns `agent_used: rag-analyst`.
- `POST /api/rag/chat` with "Show me launch creatives" returns `agent_used: rag-analyst` and image-capable sources.
- Same session ID across follow-up requests returns conversational continuity.
- Graceful behavior remains when Qdrant is down: no unhandled crash and still returns a response shape.

## Verification

```bash
uvicorn src.platform.api.main:app --reload --port 8000

curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our Meta CPM benchmark?"}' | python -m json.tool

SESSION=$(curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is Meta CPM?"}' | python -c "import sys,json; print(json.load(sys.stdin)['session_id'])")
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d "{\"message\":\"Compare that to Google\",\"session_id\":\"$SESSION\"}" | python -m json.tool
```

## Open Questions

- Should `session_id` be issued as opaque UUID v4 or a signed token with expiry claims?
