# Issue #88 — PRD: MS-1 to MS-3 Closeout (Strict Parity)

**State:** Open
**Created:** 2026-02-22T00:00:00Z
**Updated:** 2026-02-22T00:00:00Z
**Labels:** prd, closeout
**Assignees:** —
**Source:** Internal closeout PRD for issues #80, #81, #82

---

## Objective

Close the remaining checklist gaps for:
- `docs/issues/issue-080-ms1-synthetic-data-mock-assets.md`
- `docs/issues/issue-081-ms2-rag-pipeline-ingest-embed-retrieve.md`
- `docs/issues/issue-082-ms3-agent-orchestration-multi-agent-routing.md`

This PRD enforces strict parity with issue wording, not only functional equivalence.

## Scope

In scope:
- MS-1 task parity for ignore rules and generation verification.
- MS-2 task parity for required query engine builders and splitter usage.
- MS-3 task parity for 3-tool MCP contract and explicit decomposition routing logic.
- Tests and verification commands required to close all three issues.

Out of scope:
- MS-4+ milestones.
- UI/UX redesign.
- Cloud migration and deployment changes.
- New MMM routing behavior beyond MS-3 placeholder expectations.

## Current Snapshot (as of 2026-02-22)

Verified working:
- Synthetic data/asset pipeline runs and validates.
- `data/assets/asset_manifest.csv` exists with 50 asset rows.
- Qdrant collections and BM25 artifacts exist and are populated.
- `/api/rag/chat` returns `{reply, sources, session_id, agent_used}`.
- Existing targeted tests are passing.

Remaining strict-parity deltas:
- `filter_by_channel` MCP tool is missing from implementation and registration.
- Decomposition is prompt-driven only; no explicit routing-layer decomposition handling.
- `build_text_query_engine()` and `build_asset_query_engine()` are missing.
- `SentenceSplitter(chunk_size=1024, chunk_overlap=50)` is not explicitly used in index build path.
- `.gitignore` policy does not match issue #80 task `1.4` wording.

## Gap Matrix

| Issue | Required by Issue | Current State | Gap to Close |
|------|--------------------|---------------|--------------|
| #80 | Ignore `data/assets/*.png` and `data/qdrant_db/` | `data/assets/*` ignored; qdrant policy intentionally tracked | Align ignore rules to issue wording |
| #81 | `build_text_query_engine()` and `build_asset_query_engine()` | Only `search_text()` and `search_assets()` exist | Add builder functions and wire usage |
| #81 | `SentenceSplitter(1024, 50)` in indexing | Ingest chunks CSVs manually; index build uses `transformations=[]` | Explicitly add splitter in index build path |
| #82 | 3 MCP tools: `search_data`, `search_assets`, `filter_by_channel` | Only 2 tools implemented/registered | Add third tool and register it |
| #82 | Decomposition in prompt + routing logic | Prompt has instructions; router has no decomposition branch | Add explicit decomposition branch in router |

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | #80 task parity complete | `.gitignore` contains issue-required patterns and validations still pass |
| 2 | #81 task parity complete | Query engine exposes both builder functions and uses configured splitter |
| 3 | #82 tooling parity complete | `filter_by_channel` importable/callable and in rag-analyst tools arrays |
| 4 | #82 decomposition parity complete | Complex query path triggers decomposition handling in router |
| 5 | No regressions | Existing and new tests pass; API schema remains stable |

## Required Implementation Changes

### A) MS-1 Strict Parity (#80)

Files:
- `.gitignore`

Changes:
1. Add/adjust ignore patterns to satisfy task `1.4` exactly:
- `data/assets/*.png`
- `data/qdrant_db/`
2. Keep project safety for placeholders via explicit negation rules where necessary.
3. Re-run validation command to confirm pipeline integrity unchanged.

Acceptance checks:
- `ls data/assets/meta data/assets/google data/assets/tv` still shows generated PNGs locally.
- `.gitignore` contains both required entries.
- `.venv/bin/python data/generators/generate_all.py --validate-only` passes.

### B) MS-2 Strict Parity (#81)

Files:
- `src/rag/embeddings/indexer.py`
- `src/rag/retrieval/query_engine.py`
- `tests/rag/test_query_engine.py`
- `tests/rag/test_build_index_cli.py` (if interface behavior changes)

Changes:
1. In `indexer.py`, apply explicit splitter config for text indexing:
- `SentenceSplitter(chunk_size=1024, chunk_overlap=50)`
2. In `query_engine.py`, add:
- `build_text_query_engine(...)`
- `build_asset_query_engine(...)`
3. Keep `search_text()` and `search_assets()` externally compatible; route through new builders.
4. Preserve reciprocal fusion behavior for text query flow.
5. Preserve existing error messages for missing BM25/Qdrant to avoid API/UX regressions.

Acceptance checks:
- Builders are importable and used by search functions.
- Existing smoke tests for Meta CPM and asset retrieval still pass.
- CLI `--text`, `--assets`, `--check` behavior remains valid.

### C) MS-3 Strict Parity (#82)

Files:
- `src/platform/api/agents/tools.py`
- `src/platform/api/agents/rag_router.py`
- `src/platform/api/agents/prompts.py`
- `src/platform/api/agents/__init__.py`
- `src/rag/retrieval/query_engine.py` (if needed to back tool implementation)
- `tests/integration/test_rag_chat_api.py`
- `tests/integration/test_rag_router_tools.py` (new)

Changes:
1. Add MCP tool `filter_by_channel` in `tools.py`.
2. Ensure tool calls retrieval-layer function in `query_engine.py`:
- Preferred: add `filter_by_channel(query, channel, top_k=5)` helper.
3. Register the new tool in:
- MCP server `tools=[...]`
- rag-analyst `tools` array in router
- router `allowed_tools` list
- package exports in `agents/__init__.py`
4. Add explicit decomposition handling in router logic:
- Detect comparative, multi-timeframe, and cross-category intents.
- For complex queries, prepend decomposition directive before forwarding to agent.
- Keep transparent phrasing requirement (`"Let me break this into parts..."`) enforced in prompt and routing hint.
5. Keep fallback to `rag_agent.py` unchanged for index/tool failures.

Acceptance checks:
- `filter_by_channel` is importable and callable.
- rag-analyst tool arrays include all 3 MCP tools.
- Complex query path hits decomposition branch in router tests.
- `/api/rag/chat` response contract remains unchanged.

## Public APIs / Interfaces

New interfaces:
1. MCP tool:
- `filter_by_channel(args: {"query": str, "channel": str, "top_k": int}) -> dict`
2. Query engine builders:
- `build_text_query_engine(...)`
- `build_asset_query_engine(...)`
3. Optional retrieval helper for tool traceability:
- `filter_by_channel(query: str, channel: str, top_k: int = 5) -> list[dict[str, Any]]`

Unchanged interfaces:
- `POST /api/rag/chat` request and response schema:
- request: `{message: str, session_id?: str, history?: list}`
- response: `{reply: str, sources: list[str], session_id: str, agent_used: str}`

## Test Plan

### Unit tests

`tests/rag/test_query_engine.py`
1. Builders exist and construct expected retrievers.
2. `search_text()` uses builder + reciprocal rerank.
3. `search_assets()` builder path preserves metadata (`image_path`).
4. `filter_by_channel()` filters channel case-insensitively.

`tests/rag/test_indexer_assets.py` or new indexer tests
1. Text index path applies `SentenceSplitter` with `chunk_size=1024` and `chunk_overlap=50`.

### Integration tests

`tests/integration/test_rag_chat_api.py`
1. Response contract remains stable.
2. Session ID passthrough remains stable.
3. Fallback behavior remains stable.

`tests/integration/test_rag_router_tools.py` (new)
1. rag-analyst includes:
- `mcp__rag-tools__search_data`
- `mcp__rag-tools__search_assets`
- `mcp__rag-tools__filter_by_channel`
2. Complex query triggers decomposition branch.
3. Simple query bypasses decomposition branch.

## Verification Commands

```bash
# MS-1 validation
.venv/bin/python data/generators/generate_all.py --validate-only
find data/assets -maxdepth 2 -type f -name '*.png' | wc -l
wc -l data/assets/asset_manifest.csv

# MS-2 index and retrieval checks
.venv/bin/python -m src.rag.data_processing.build_index --check
.venv/bin/python -m pytest tests/rag/test_build_index_cli.py tests/rag/test_query_engine.py -q

# MS-3 API and routing checks
.venv/bin/python -m pytest tests/integration/test_rag_chat_api.py tests/integration/test_rag_router_tools.py -q

# Optional end-to-end API smoke
uvicorn src.platform.api.main:app --reload --port 8000
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is our Meta CPM benchmark?"}'
curl -s -X POST http://localhost:8000/api/rag/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Compare Meta CPM vs Google CPC in Q3 and Q4"}'
```

## Execution Order

1. Update `.gitignore` for #80 parity.
2. Implement #81 builders and splitter usage.
3. Add #82 third MCP tool and router wiring.
4. Add #82 decomposition routing branch.
5. Add/update tests.
6. Run verification commands and capture outputs.
7. Update issue checkboxes in #80/#81/#82 with evidence links.

## Rollout and Risk Controls

1. Keep API contracts unchanged.
2. Keep fallback path active while upgrading tools/routing.
3. Make changes in small commits per milestone slice:
- commit A: #80 parity
- commit B: #81 parity
- commit C: #82 tool parity
- commit D: #82 decomposition parity + tests
4. If retrieval behavior drifts, gate through tests before merge.

## Acceptance Criteria

All criteria must be true:
1. Every unchecked task in #80/#81/#82 has implementation evidence.
2. New interfaces (`filter_by_channel`, builder functions) are present and covered by tests.
3. Decomposition handling is present in both prompt and router logic.
4. Existing targeted tests remain green.
5. New tests for added behavior are green.
6. `/api/rag/chat` schema is unchanged.

## Assumptions and Defaults

1. Strict issue parity takes precedence over historical local policy differences.
2. `.venv/bin/python` is the canonical interpreter path for commands.
3. Qdrant local mode remains the default runtime for milestone checks.
4. No external infra changes are required to close these milestones.

## Dependencies

- #80 has no upstream dependency.
- #81 depends on #80 assets and manifest availability.
- #82 depends on #81 retrieval/query functions being operational.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
