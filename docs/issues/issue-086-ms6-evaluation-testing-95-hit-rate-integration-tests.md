# Issue #86 — MS-6: Evaluation & Testing — 95% Hit Rate + Integration Tests

**State:** Open
**Created:** 2026-02-19T09:56:52Z
**Updated:** 2026-02-19T09:56:52Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/86

---

## Objective

Validate retrieval quality with a curated evaluation set, achieve 95% hit rate, and add integration tests across all pipelines. Maintain >= 80% test coverage.

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Evaluation dataset covers all data categories | 50 questions: ~15 digital media, ~10 sales, ~10 contracts, ~10 traditional, ~5 cross-category |
| 2 | Retrieval hit rate meets target | >= 95% (47/50 questions retrieve correct source in top-5) |
| 3 | MRR is acceptable | Mean Reciprocal Rank >= 0.80 |
| 4 | RAG pipeline integration tests pass | Document loading, embedding, retrieval all tested |
| 5 | MMM script integration tests pass | Each script produces valid JSON, regression R² > 0.5, optimizer constraints hold |
| 6 | Agent endpoint integration tests pass | RAG chat, MMM summary, MMM chat all return expected response shapes |
| 7 | Overall test coverage maintained | `pytest --cov` reports >= 80% on `src/` (baseline: 85% on API layer) |

## Tasks

- [ ] **6.1** Create `tests/evaluation/eval_questions.yml` (~50 curated Q&A pairs) — balanced across categories: ~15 digital media, ~10 sales pipeline, ~10 contracts, ~10 traditional media, ~5 cross-category. Include asset search queries.
- [ ] **6.2** Create `tests/evaluation/run_retrieval_eval.py` (~120 lines) — For each question: run hybrid retrieval (top_k=5), check expected sources in results, compute hit_rate and MRR. Report per-category breakdown and failing queries.
- [ ] **6.3** If below 95% hit rate, apply tuning levers in order:
  1. Increase `top_k` from 5 → 10
  2. Increase `chunk_overlap` from 50 → 100
  3. Enable query expansion (`num_queries=3` in QueryFusionRetriever)
  4. Add metadata pre-filtering (channel-specific queries)
  5. Add document summary layer (two-stage retrieval)
- [ ] **6.4** Create `tests/integration/test_rag_pipeline.py` (~100 lines) — document loading, embedding, retrieval tests
- [ ] **6.5** Create `tests/integration/test_mmm_scripts.py` (~80 lines) — each script produces valid JSON, regression R² > 0.5, optimizer constraints hold
- [ ] **6.6** Create `tests/integration/test_agent_endpoints.py` (~60 lines) — RAG chat returns reply + sources, MMM summary returns expected fields, MMM chat returns reply
- [ ] **6.7** Run full test suite: `pytest tests/ -v --cov=src --cov-report=term-missing` — target >= 80% coverage

## Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `tests/evaluation/eval_questions.yml` | New | ~200 |
| `tests/evaluation/run_retrieval_eval.py` | New | ~120 |
| `tests/integration/test_rag_pipeline.py` | New | ~100 |
| `tests/integration/test_mmm_scripts.py` | New | ~80 |
| `tests/integration/test_agent_endpoints.py` | New | ~60 |

## Verification

```bash
python tests/evaluation/run_retrieval_eval.py
# Expected: Hit Rate: >= 0.95, MRR: >= 0.80

python -m pytest tests/integration/ -v
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

## Dependencies

- **MS-5** (#85) — all pipelines and endpoints must be functional before evaluation.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
