# PRD: MS-6 — Evaluation and Testing (95% Hit Rate)

**Issue:** [#86](https://github.com/tkhongsap/rag-mmm-platform/issues/86)
**Branch:** `fix/issue-86-ms6-evaluation-testing-95-hit-rate-integration-tests`
**Date:** 2026-02-20

## Introduction

MS-6 introduces quantitative quality gates for retrieval and integration stability. It defines a curated evaluation set, automated retrieval scoring, and integration coverage for RAG, MMM scripts, and agent endpoints so the platform can be validated before production integration and migration.

## Goals

- Achieve >=95% retrieval hit rate (top-5) and MRR >=0.80 across a balanced eval set.
- Ensure core integration paths are covered with tests in `tests/`.
- Keep quality and regression coverage >=80% with explicit verification commands.
- Provide a repeatable tuning loop when metrics miss targets.

## User Stories

### US-001: Create evaluation dataset
**Description:** As a quality lead, I want a balanced set of real questions to evaluate retrieval quality across data classes.

**Acceptance Criteria:**
- [ ] `tests/evaluation/eval_questions.yml` contains ~50 questions.
- [ ] Distribution includes ~15 digital media, ~10 sales, ~10 contracts, ~10 traditional media, ~5 cross-category.
- [ ] Asset search scenarios are present.
- [ ] Each question has expected source or answer criteria.

### US-002: Build retrieval evaluation runner
**Description:** As a platform engineer, I want a script that computes hit-rate and MRR so we can measure changes objectively.

**Acceptance Criteria:**
- [ ] `tests/evaluation/run_retrieval_eval.py` runs all questions and calls hybrid retrieval with `top_k=5`.
- [ ] Script outputs overall hit_rate and MRR plus per-category metrics and failing query list.
- [ ] Output includes totals that can be parsed in CI logs.

### US-003: Add retrieval tuning loop guidance
**Description:** As an operator, I want deterministic knobs to improve retrieval when metrics are below target.

**Acceptance Criteria:**
- [ ] Tuning order documented in script comments or docs: top_k, chunk overlap, query expansion, metadata filtering, document summary.
- [ ] Script can be run repeatedly and reports updated metrics.

### US-004: Add integration tests for RAG pipeline
**Description:** As a maintainer, I want automated checks for load/embed/retrieve flow so regressions are caught early.

**Acceptance Criteria:**
- [ ] `tests/integration/test_rag_pipeline.py` validates document loading, indexing APIs, and retrieval calls.
- [ ] Tests are deterministic and run in CI.

### US-005: Add integration tests for MMM scripts
**Description:** As a data analyst, I want script execution safety and output schema checks in integration tests.

**Acceptance Criteria:**
- [ ] `tests/integration/test_mmm_scripts.py` verifies JSON schema and key numeric constraints.
- [ ] Regression `r_squared` expectation and optimizer constraints are asserted.

### US-006: Add integration tests for API endpoints
**Description:** As a product QA owner, I want endpoint-level guarantees for chat and summary routes.

**Acceptance Criteria:**
- [ ] `tests/integration/test_agent_endpoints.py` verifies RAG chat payload includes reply, sources, session id, agent_used.
- [ ] MMM summary and MMM chat return expected fields and non-empty outputs.
- [ ] Tests remain stable when run with `pytest -v` and expected data fixtures are controlled.

## Functional Requirements

- FR-1: Add curated evaluation dataset at `tests/evaluation/eval_questions.yml`.
- FR-2: Add `tests/evaluation/run_retrieval_eval.py` with hit_rate and MRR computation.
- FR-3: Add fallback tuning checklist and report formatting to evaluator.
- FR-4: Add integration tests for RAG pipeline, MMM scripts, and API endpoints.
- FR-5: Update test workflow if needed to include eval or new integration targets.

## Non-Goals

- Replacing retrieval pipeline implementation (MS-2/82).
- Introducing synthetic evaluation data generation beyond static files.
- Full production-grade model monitoring dashboard.

## Technical Considerations

- Keep eval expectations resilient to ranking variance while still strict enough to enforce retrieval quality.
- Tests should not mutate repo-tracked state and should tolerate local path differences for generated data.
- Ensure pytest markers or fixtures isolate slow integration tests.

## Files to Modify

| File | Change |
|------|--------|
| `tests/evaluation/eval_questions.yml` | New |
| `tests/evaluation/run_retrieval_eval.py` | New |
| `tests/integration/test_rag_pipeline.py` | New |
| `tests/integration/test_mmm_scripts.py` | New |
| `tests/integration/test_agent_endpoints.py` | New |

## Success Metrics

- Retrieval evaluation outputs `Hit Rate >= 0.95` and `MRR >= 0.80`.
- Evaluation coverage includes all defined categories with no missing-source answers.
- Integration suite `pytest tests/integration/ -v` passes.
- Full coverage command `pytest tests/ -v --cov=src --cov-report=term-missing` reports >=80%.

## Verification

```bash
python tests/evaluation/run_retrieval_eval.py
python -m pytest tests/integration/ -v
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Open Questions

- Should hit-rate and MRR be measured only on semantic retrieval, or include keyword-only fallback results as valid matches?
