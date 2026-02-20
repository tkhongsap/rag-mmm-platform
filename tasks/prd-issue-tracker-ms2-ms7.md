# PRD Tracker: MS-2 to MS-7

## Purpose
Track PRD execution status for issue-based planning milestones derived from GitHub issues 81-87.

## Legend
- **Status**: `not_started | in_progress | done | blocked`
- **Owner**: person or agent handling the item
- **Branch**: implementation branch referenced by each PRD
- **Primary PRD**: corresponding `tasks/prd-*.md`
- **Issue**: GitHub issue URL for source-of-truth

## Milestone Tracker

### MS-2 — RAG Pipeline: Ingest, Embed, Retrieve
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-81-ms2-rag-pipeline-ingest-embed-retrieve`
- **Primary PRD:** `tasks/prd-ms2-rag-pipeline-ingest-embed-retrieve.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/81`
- **Acceptance Focus:** indexed corpus, `text_documents` + `campaign_assets` collections, hybrid retrieval CLI
- **Done Criteria:** text and asset retrieval scripts produce >0 results; `--check` validates index health

### MS-3 — Agent Orchestration: Multi-Agent Routing
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-82-ms3-agent-orchestration-multi-agent-routing`
- **Primary PRD:** `tasks/prd-ms3-agent-orchestration-multi-agent-routing.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/82`
- **Acceptance Focus:** MCP tools, session continuity, routing to rag-analyst
- **Done Criteria:** `/api/rag/chat` returns `reply`, `sources`, `session_id`, `agent_used`

### MS-4a — MMM Analysis Scripts: Validate & Harden
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-83-ms4a-mmm-analysis-scripts-validate-harden`
- **Primary PRD:** `tasks/prd-ms4a-mmm-analysis-scripts-validate-harden.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/83`
- **Acceptance Focus:** regression/ROI/optimizer/adstock summary JSON contracts
- **Done Criteria:** script outputs include required fields and constraints validated

### MS-4b — MMM Agent + API Endpoints
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-84-ms4b-mmm-agent-api-endpoints`
- **Primary PRD:** `tasks/prd-ms4b-mmm-agent-api-endpoints.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/84`
- **Acceptance Focus:** MMM agent and routing, `/api/mmm/summary`, `/api/mmm/chat`
- **Done Criteria:** MMM intents route to `mmm-analyst` with valid summaries and chat answers

### MS-5 — Frontend Integration: Live Data + Asset Endpoints
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-85-ms5-frontend-integration-live-data-asset-endpoints`
- **Primary PRD:** `tasks/prd-ms5-frontend-integration-live-data-asset-endpoints.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/85`
- **Acceptance Focus:** sessioned RAG chat, source badges/images, MMM live dashboard
- **Done Criteria:** pages render live values and show backend-error states gracefully

### MS-6 — Evaluation & Testing (95% Hit Rate)
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-86-ms6-evaluation-testing-95-hit-rate-integration-tests`
- **Primary PRD:** `tasks/prd-ms6-evaluation-testing-95-hit-rate-integration-tests.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/86`
- **Acceptance Focus:** 50-question eval, `run_retrieval_eval.py`, integration tests for RAG/MMM/agent APIs
- **Done Criteria:** hit_rate >= 0.95, MRR >= 0.80, integration tests passing

### MS-7 — Cloud Migration
- **Status:** not_started
- **Owner:** TBD
- **Branch:** `fix/issue-87-ms7-cloud-migration`
- **Primary PRD:** `tasks/prd-ms7-cloud-migration.md`
- **Issue:** `https://github.com/tkhongsap/rag-mmm-platform/issues/87`
- **Acceptance Focus:** managed services migration, containerization, CI/CD baseline
- **Done Criteria:** services runnable via compose; deploy pipeline and cloud storage/vector strategy in place

## Execution Order (Suggested)
1. MS-2
2. MS-3
3. MS-4a + MS-4b (parallel with MS-3 where possible)
4. MS-5
5. MS-6
6. MS-7

## Risk Register
- Dependency chain means MS-5 is blocked until MS-3/MS-4b APIs are production-usable.
- MS-7 remains high-level and should start only after MS-1..MS-6 delivery confidence.
