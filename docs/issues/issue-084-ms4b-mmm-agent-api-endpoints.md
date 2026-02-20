# Issue #84 — MS-4b: MMM Agent + API Endpoints

**State:** Open
**Created:** 2026-02-19T09:55:52Z
**Updated:** 2026-02-19T09:55:52Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/84

---

## Objective

Wrap the MMM scripts with a Claude Agent SDK agent, expose API endpoints, and extend the orchestrator to route MMM intents.

## Current State

- MMM scripts exist and produce JSON output (validated in MS-4a)
- Orchestrator exists from MS-3 but only handles RAG queries
- No MMM agent or MMM API endpoints yet

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | MMM agent can answer ROI questions | `POST /api/mmm/chat` with "What is TV ROI?" returns a substantive answer |
| 2 | MMM summary endpoint returns live data | `GET /api/mmm/summary` returns JSON with >= 5 fields |
| 3 | Agent runs scripts via Bash tool | Agent response references actual regression/ROI numbers |
| 4 | Orchestrator routes MMM queries correctly | "Optimize budget" → MMM agent; response references regression/ROI numbers |

## Tasks

- [ ] **4b.1** Create `src/platform/api/agents/mmm_agent.py` (~120 lines) — `ask_mmm_question(question)` using `ClaudeAgentOptions` with `MMM_AGENT_PROMPT`, tools: `Read`, `Bash`, `Glob`, `Grep`. Agent reads `data/mmm/`, runs `mmm_scripts/*.py`, interprets JSON output.
- [ ] **4b.2** Update `src/platform/api/agents/rag_router.py` — Register `mmm-analyst` subagent. Add routing rules: "optimize/model/ROI/budget" queries go to MMM agent.
- [ ] **4b.3** Update `src/platform/api/main.py`:
  - Add `GET /api/mmm/summary` — calls `mmm_summary.build_mmm_summary()`
  - Add `POST /api/mmm/chat` — calls `mmm_agent.ask_mmm_question(question)`

## Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `src/platform/api/agents/mmm_agent.py` | New | ~120 |
| `src/platform/api/agents/rag_router.py` | Modify | +40 |
| `src/platform/api/main.py` | Modify | +20 |

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
# Should return agent_used = "mmm-analyst"
```

## Dependencies

- **MS-3** (#82) — base orchestrator and RAG routing must be operational.
- **MS-4a** (#83) — scripts must produce valid JSON output.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
