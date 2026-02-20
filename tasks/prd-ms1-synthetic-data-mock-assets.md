# PRD: MS-1 — Synthetic Data & Mock Assets (Foundation)

**Issue:** [#80](https://github.com/tkhongsap/rag-mmm-platform/issues/80)
**Branch:** `fix/issue-80-ms1-foundation`
**Date:** 2026-02-20

---

## Introduction

MS-1 is the **root milestone** for the RAG + MMM platform — every downstream milestone depends on it. The synthetic data generators (`data/generators/`) produce marketing data for a UK automotive launch (DEEPAL/AVATR brands, 2025), including CSVs, vendor contracts, campaign images, and MMM-ready datasets.

The generators are ~95% complete. All data files exist on disk, but four gaps remain: a broken module import that silently skips MMM aggregation, a spend verification bug that reports a false 761.7% deviation warning, missing Python dependencies in `requirements.txt`, and missing `.gitignore` entries for generated binary files. This PRD defines the work needed to close these gaps so `generate_all.py` runs cleanly end-to-end and MS-2/MS-4a can begin.

## Goals

- Fix the `aggregate_mmm` import so Step 9 (MMM aggregation) runs instead of silently skipping
- Fix the spend verification filter so it reports accurate budget deviation (< 5%)
- Ensure all required Python packages are declared in `requirements.txt`
- Prevent generated binaries (PNGs, vector DB, index files) from being committed to git
- Achieve a fully clean `generate_all.py` run: all 8 generation steps + aggregation + 10 validation checks pass + spend verification OK

## User Stories

### US-001: Fix aggregate_mmm module import

**Description:** As a developer, I want the MMM aggregation step to run successfully so that `generate_all.py` completes all steps without skipping any.

**Acceptance Criteria:**
- [ ] `data/generators/aggregate_mmm.py` exists and re-exports `aggregate_mmm_data` from `data/generators/validators.py:748`
- [ ] Running `python3 data/generators/generate_all.py` shows Step 9 (MMM aggregation) as "OK" instead of "SKIPPED"
- [ ] No changes needed to `generate_all.py` itself — the new module matches its existing import pattern (line 187)
- [ ] MMM output files in `data/mmm/` are correctly generated (model_ready.csv, weekly_channel_spend.csv, weekly_sales.csv — 52 rows each)

### US-002: Fix spend verification column filter

**Description:** As a developer, I want the spend verification to accurately report budget deviation so that I can trust the validation output.

**Acceptance Criteria:**
- [ ] Spend verification in `generate_all.py` (lines 270–283) correctly sums channel spend from raw CSVs
- [ ] Filter matches the actual column name `"spend"` (not `"spend"` + `"gbp"`)
- [ ] `competitor_spend.csv` is excluded from the sum (it contains external competitor data, not our budget)
- [ ] `data/mmm/` directory is excluded from the scan (it double-counts spend already in `data/raw/`)
- [ ] After fix, reported deviation is < 5% with status "OK"
- [ ] Running `python3 data/generators/generate_all.py` shows spend verification without WARNING

### US-003: Add missing Python dependencies

**Description:** As a developer, I want all required packages declared in `requirements.txt` so that a fresh `pip install -r requirements.txt` succeeds and the full pipeline runs.

**Acceptance Criteria:**
- [ ] `Pillow>=10.0.0` added to `requirements.txt` (required by `data/generators/assets.py:18` for PNG generation)
- [ ] `qdrant-client>=1.9.0` added to `requirements.txt` (vector store client, prepares for MS-2)
- [ ] `llama-index-vector-stores-qdrant>=0.3.0` added to `requirements.txt` (LlamaIndex Qdrant integration, prepares for MS-2)
- [ ] `pip install -r requirements.txt` completes without errors

### US-004: Add .gitignore entries for generated files

**Description:** As a developer, I want generated binary files excluded from git tracking so that PNGs and database files don't bloat the repository.

**Acceptance Criteria:**
- [ ] `data/assets/*` added to `.gitignore` (excludes ~50 generated PNGs)
- [ ] `data/qdrant_db/` added to `.gitignore` (vector database directory for MS-2)
- [ ] `data/index/` added to `.gitignore` (BM25 index directory for MS-2)
- [ ] Existing `!data/**/.gitkeep` pattern (line 92) still works — `.gitkeep` files remain tracked
- [ ] `git status` does not show `data/assets/` PNGs as untracked files

## Functional Requirements

- **FR-1:** Create `data/generators/aggregate_mmm.py` that imports and re-exports `aggregate_mmm_data()` from `data/generators/validators.py`
- **FR-2:** Update the spend verification loop in `generate_all.py` (lines 270–283) to scan only `data/raw/`, exclude `competitor_spend.csv`, and match columns where `column.lower() == "spend"`
- **FR-3:** Add `Pillow>=10.0.0`, `qdrant-client>=1.9.0`, and `llama-index-vector-stores-qdrant>=0.3.0` to `requirements.txt`
- **FR-4:** Add `data/assets/*`, `data/qdrant_db/`, and `data/index/` to the "Data directories" section of `.gitignore`
- **FR-5:** The full pipeline `python3 data/generators/generate_all.py` must exit with code 0, all 10 validation checks passing, spend deviation < 5%

## Non-Goals

- No changes to the data generators themselves (`digital_media.py`, `traditional_media.py`, `sales_pipeline.py`, `contracts.py`, `events.py`, `external_data.py`, `assets.py`)
- No changes to the validation logic in `validators.py` (only the spend verification in `generate_all.py`)
- No implementation of MS-2 RAG pipeline code (only adding dependencies to `requirements.txt` to prepare)
- No modifications to the UI or API layers
- No new tests (verification is via the existing `generate_all.py --validate-only` checks)

## Technical Considerations

- **Import pattern:** `generate_all.py` uses `_import_generator(name)` which does `importlib.import_module(f"data.generators.{name}")`. The new `aggregate_mmm.py` must be importable via this pattern.
- **Spend column naming:** Raw CSVs (meta_ads, google_ads, tv_performance, etc.) all use `"spend"` as the column name. Only `competitor_spend.csv` uses `"estimated_spend_gbp"`. The MMM datasets in `data/mmm/` use `"spend_meta"`, `"spend_tv"`, etc.
- **Budget reference:** `config.py` defines `UK_TOTAL_ANNUAL_BUDGET = £20,000,000` split across `CHANNEL_BUDGETS_GBP` (11 channels). The spend verification compares summed CSV spend against this value.
- **Existing data:** All output files already exist on disk (19 CSVs, 7 contracts, 50 PNGs, 3 MMM datasets). The fixes ensure the pipeline runs cleanly, not that it generates data for the first time.

## Files to Modify

| File | Change | New/Edit |
|------|--------|----------|
| `data/generators/aggregate_mmm.py` | Thin re-export module (~4 lines) | New |
| `data/generators/generate_all.py` | Fix spend verification filter (lines 270–283) | Edit |
| `requirements.txt` | Add 3 packages | Edit |
| `.gitignore` | Add 3 entries in "Data directories" section | Edit |

## Success Metrics

- `python3 data/generators/generate_all.py` exits with code 0
- All 8 generation steps report OK
- MMM aggregation step reports OK (not SKIPPED)
- All 10 validation checks pass
- Spend verification reports deviation < 5% (OK)
- `python3 data/generators/generate_all.py --validate-only` passes cleanly
- `data/assets/asset_manifest.csv` has >= 51 lines (header + 50 rows)
- `git status` shows no untracked PNGs in `data/assets/`

## Verification

```bash
# 1. Install updated dependencies
pip install -r requirements.txt

# 2. Full end-to-end generation
python3 data/generators/generate_all.py
# Expected: Steps 1-8 OK, MMM aggregation OK, 10/10 validations pass, spend < 5%

# 3. Validate-only mode
python3 data/generators/generate_all.py --validate-only

# 4. Confirm assets
ls data/assets/meta/ data/assets/google/ data/assets/tv/
wc -l data/assets/asset_manifest.csv   # >= 51

# 5. Confirm .gitignore
git status   # data/assets/ PNGs should NOT appear as untracked
```

## Open Questions

- None — scope is well-defined and all issues have been investigated.
