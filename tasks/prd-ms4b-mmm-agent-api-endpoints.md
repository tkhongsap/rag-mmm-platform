# PRD: MS-4b — MMM Agent and API Endpoints

**Issue:** [#84](https://github.com/tkhongsap/rag-mmm-platform/issues/84)
**Branch:** `fix/issue-84-ms4b-mmm-agent-api-endpoints`
**Date:** 2026-02-20

## Introduction

MS-4b adds MMM capability to the agent layer and exposes backend endpoints for MMM summary and chat. It extends the existing orchestrator to include MMM intent routing while reusing the script outputs hardened in MS-4a.

## Goals

- Add MMM subagent that can execute MMM scripts and return analytic answers.
- Route optimization and ROI questions to `mmm-analyst` when intent matches.
- Expose `/api/mmm/summary` and `/api/mmm/chat` with stable response shapes.
- Keep MMM integration fully additive to existing RAG flows.

## User Stories

### US-001: Add MMM agent implementation
**Description:** As a data analyst, I want a dedicated MMM agent so I can ask budget and ROI questions and receive answers from live script outputs.

**Acceptance Criteria:**
- [ ] `src/platform/api/agents/mmm_agent.py` defines `ask_mmm_question(question)`.
- [ ] Agent uses tools to read scripts/data and run `src/platform/api/mmm_scripts/*.py`.
- [ ] MMM responses include numeric references from actual script output JSON.
- [ ] Agent errors are captured and returned in user-visible text instead of raw traces.

### US-002: Add MMM routing in orchestrator
**Description:** As a system, I want routing that classifies ROI and budget optimization questions and delegates to MMM agent.

**Acceptance Criteria:**
- [ ] `src/platform/api/agents/rag_router.py` registers `mmm-analyst` and routes keywords like optimize, ROI, budget.
- [ ] RAG-friendly queries continue to use rag flow.
- [ ] `agent_used` in responses correctly identifies `mmm-analyst` for MMM intents.

### US-003: Expose MMM summary endpoint
**Description:** As a dashboard user, I want the API to provide live MMM summary fields so the UI can render real KPIs.

**Acceptance Criteria:**
- [ ] `GET /api/mmm/summary` returns JSON with required fields from `build_mmm_summary()`.
- [ ] Endpoint returns proper status and error shape when MMM data is unavailable.

### US-004: Expose MMM chat endpoint
**Description:** As a business user, I want to ask MMM questions from API clients and receive plain text results from analysis scripts.

**Acceptance Criteria:**
- [ ] `POST /api/mmm/chat` accepts `question`.
- [ ] Endpoint returns answer payload compatible with frontend chat rendering.
- [ ] MMM query "What is the ROI of TV spend?" produces non-empty reply.

## Functional Requirements

- FR-1: Create `src/platform/api/agents/mmm_agent.py` with `ask_mmm_question` and tool configuration.
- FR-2: Extend `src/platform/api/agents/prompts.py` with `MMM_AGENT_PROMPT`.
- FR-3: Extend `src/platform/api/agents/rag_router.py` routing map to include MMM intents.
- FR-4: Add MMM API routes in `src/platform/api/main.py` for summary and chat.
- FR-5: Keep MMM responses aligned with MS-4a JSON schema and MS-5 frontend expectations.

## Non-Goals

- UI dashboard implementation for MMM visuals (handled in MS-5).
- Deep MMM model rewrites or new simulation features.
- Deployment-level concerns and infrastructure migration (MS-7).

## Technical Considerations

- Prefer command execution through constrained Bash tool usage and controlled paths.
- Protect command and file reads to `data/mmm/` and MMM script paths.
- Keep `agent_used` stable for analytics and debugging.

## Files to Modify

| File | Change |
|------|--------|
| `src/platform/api/agents/mmm_agent.py` | New |
| `src/platform/api/agents/prompts.py` | Add MMM prompt |
| `src/platform/api/agents/rag_router.py` | Update routing and registration |
| `src/platform/api/main.py` | Add `/api/mmm/summary`, `/api/mmm/chat` |

## Success Metrics

- `/api/mmm/summary` returns JSON with >= 5 fields, including channel and spend totals.
- `/api/mmm/chat` with "What is TV ROI?" returns substantive non-empty answer.
- RAG query "Optimize budget" via `/api/rag/chat` is routed to `mmm-analyst`.
- MMM requests do not degrade RAG endpoint behavior.

## Verification

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

## Open Questions

- For MMM execution safety, should script execution remain in-process or move to a background job queue in later phases?
