# PRD: MS-1 to MS-3 Closeout (Strict Parity)

## 1. Introduction/Overview

This PRD defines the implementation work required to close strict checklist parity gaps for:
- MS-1 issue #80 (`docs/issues/issue-080-ms1-synthetic-data-mock-assets.md`)
- MS-2 issue #81 (`docs/issues/issue-081-ms2-rag-pipeline-ingest-embed-retrieve.md`)
- MS-3 issue #82 (`docs/issues/issue-082-ms3-agent-orchestration-multi-agent-routing.md`)

This is a closeout PRD, not a new feature PRD. Completion is defined by matching issue wording and passing verification tests, not by "mostly works" behavior.

Source baseline for this PRD:
- `docs/issues/issue-088-ms1-ms3-closeout-strict-parity.md`

## 2. Goals

- Close #80 task parity for ignore rules (`data/assets/*.png`, `data/qdrant_db/`).
- Add missing MS-2 query engine builder interfaces.
- Add explicit `SentenceSplitter(chunk_size=1024, chunk_overlap=50)` usage in text indexing path.
- Add missing MS-3 `filter_by_channel` MCP tool and register it everywhere required.
- Add explicit decomposition handling in routing logic (not prompt-only).
- Preserve `/api/rag/chat` response contract (`{reply, sources, session_id, agent_used}`).
- Keep existing passing tests green and add targeted tests for new behavior.

## 3. User Stories

### US-001: Align MS-1 Ignore Rules
**Description:** As a maintainer, I want `.gitignore` entries to match issue #80 wording so milestone closure is unambiguous.

**Acceptance Criteria:**
- [ ] `.gitignore` includes `data/assets/*.png`
- [ ] `.gitignore` includes `data/qdrant_db/`
- [ ] `.venv/bin/python data/generators/generate_all.py --validate-only` exits with code 0
- [ ] No unrelated ignore rules are removed

### US-002: Add MS-2 Query Engine Builders
**Description:** As a RAG developer, I want explicit query engine builder functions so code matches issue #81 interface expectations.

**Acceptance Criteria:**
- [ ] `build_text_query_engine(...)` exists in `src/rag/retrieval/query_engine.py`
- [ ] `build_asset_query_engine(...)` exists in `src/rag/retrieval/query_engine.py`
- [ ] `search_text(...)` and `search_assets(...)` use the new builder path
- [ ] Existing retrieval smoke tests remain passing

### US-003: Apply Explicit SentenceSplitter Config
**Description:** As a reviewer, I want splitter configuration explicitly represented in indexing so implementation matches issue #81 wording.

**Acceptance Criteria:**
- [ ] Text indexing path explicitly uses `SentenceSplitter(chunk_size=1024, chunk_overlap=50)`
- [ ] No regression in text index build behavior
- [ ] Tests verify splitter configuration usage or equivalent observable behavior

### US-004: Add `filter_by_channel` MCP Tool
**Description:** As an orchestrator developer, I want a third MCP tool so #82 KR1 and task 3.2 are fully satisfied.

**Acceptance Criteria:**
- [ ] `filter_by_channel` implemented in `src/platform/api/agents/tools.py`
- [ ] Tool calls retrieval-layer filtering function
- [ ] Tool is registered in MCP server tool list
- [ ] Tool is exported from `src/platform/api/agents/__init__.py`

### US-005: Register All 3 Tools in Router
**Description:** As an API integrator, I want rag-analyst to expose all required MCP tools for strict #82 parity.

**Acceptance Criteria:**
- [ ] `mcp__rag-tools__search_data` present in rag-analyst tools
- [ ] `mcp__rag-tools__search_assets` present in rag-analyst tools
- [ ] `mcp__rag-tools__filter_by_channel` present in rag-analyst tools
- [ ] Same 3 MCP tools present in router `allowed_tools`

### US-006: Add Explicit Decomposition Routing Path
**Description:** As a product owner, I want complex query decomposition handled by routing logic, not only prompt guidance.

**Acceptance Criteria:**
- [ ] Router detects comparative/multi-timeframe/cross-category query patterns
- [ ] Router applies decomposition instruction path before agent query on complex prompts
- [ ] Complex query tests verify decomposition path trigger
- [ ] Simple query tests verify no unnecessary decomposition

### US-007: Preserve RAG Chat API Contract and Fallback
**Description:** As a client developer, I want closeout work to avoid breaking current API clients.

**Acceptance Criteria:**
- [ ] `POST /api/rag/chat` still returns `{reply, sources, session_id, agent_used}`
- [ ] Session continuity behavior remains intact
- [ ] Fallback to file-reader remains intact under tool/router failure
- [ ] Existing integration tests remain passing

## 4. Functional Requirements

- FR-1: The system must include `.gitignore` entries required by #80 task 1.4.
- FR-2: The query engine must expose `build_text_query_engine(...)`.
- FR-3: The query engine must expose `build_asset_query_engine(...)`.
- FR-4: `search_text(...)` must use vector + BM25 reciprocal fusion via builder path.
- FR-5: Text indexing must explicitly apply `SentenceSplitter(1024, 50)`.
- FR-6: Agent tools module must expose `search_data`, `search_assets`, and `filter_by_channel`.
- FR-7: MCP server registration must include all 3 tools.
- FR-8: Rag router `rag-analyst` and `allowed_tools` must include all 3 MCP tool names.
- FR-9: Router must implement explicit decomposition handling for complex queries.
- FR-10: `/api/rag/chat` request/response schema must remain backward compatible.
- FR-11: Fallback behavior must remain operational if routing/tooling fails.
- FR-12: Test suite must cover newly added interfaces and routing behavior.

## 5. Non-Goals (Out of Scope)

- No MS-4/MS-5 feature delivery.
- No new UI endpoints (asset HTTP endpoints remain in MS-5 scope).
- No cloud migration, deployment workflow changes, or infra re-architecture.
- No retrieval model changes unrelated to strict parity closure.

## 6. Design Considerations

- Prefer additive and minimal changes to existing modules.
- Preserve current file/module boundaries unless strictly needed for acceptance.
- Avoid broad refactors unrelated to #80/#81/#82 closeout.

## 7. Technical Considerations

- Use `.venv/bin/python` for all documented verification commands.
- Preserve local Qdrant mode assumptions currently used by tests.
- Keep existing error semantics where tests/assertions depend on message patterns.
- Ensure channel matching behavior remains case-insensitive.

## 8. Success Metrics

- 100% of unchecked checklist items in #80/#81/#82 can be marked complete with evidence.
- All existing targeted tests continue to pass.
- New targeted tests for tool parity and decomposition pass.
- `/api/rag/chat` response schema shows zero regressions.
- Verification commands execute successfully on a clean run.

## 9. Open Questions

- Should strict #80 parity override the repository comment that qdrant/bm25 may be tracked for cloud runs, or should issue #80 wording be updated to reflect current policy?
- For decomposition routing, should trigger logic be deterministic keyword/rule-based only, or allow lightweight classifier logic in-router?
- Should `filter_by_channel` live only in agent tools as an adapter, or also be exported as a first-class retrieval API in `query_engine.py`?

## Important Public API / Interface Changes

- Add `filter_by_channel` MCP tool interface in `src/platform/api/agents/tools.py`.
- Add `build_text_query_engine(...)` and `build_asset_query_engine(...)` in `src/rag/retrieval/query_engine.py`.
- Optionally add retrieval helper `filter_by_channel(query, channel, top_k=5)` in `src/rag/retrieval/query_engine.py` for traceable tool wiring.
- No breaking change to `/api/rag/chat` payload contract.

## Test Cases and Scenarios

### Unit
- Query-engine builders exist and are used by search functions.
- Splitter config is applied in text index path.
- `filter_by_channel` returns only nodes matching channel filter.

### Integration
- Rag router includes all 3 MCP tools.
- Complex query triggers decomposition branch.
- Simple query bypasses decomposition branch.
- Session continuity behavior remains unchanged.
- Fallback behavior remains unchanged.

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
```

## Assumptions and Defaults

- Strict issue parity is the primary acceptance policy.
- Output file path is fixed to `tasks/prd-ms1-ms3-closeout-strict-parity.md`.
- Existing behavior that already passes tests should remain unchanged unless parity explicitly requires change.
- No new external services are required for milestone closure.

## Implementation Sequence

1. Copy objective and gap context from `docs/issues/issue-088-ms1-ms3-closeout-strict-parity.md`.
2. Convert each gap to a small user story with explicit acceptance criteria.
3. Map stories to numbered functional requirements.
4. Add non-goals, technical constraints, and interface changes.
5. Add test scenarios and command-based verification.
6. Use this PRD as the execution contract for code changes.
