# PRD: MS-4a — MMM Analysis Scripts: Validate and Harden

**Issue:** [#83](https://github.com/tkhongsap/rag-mmm-platform/issues/83)
**Branch:** `fix/issue-83-ms4a-mmm-analysis-scripts-validate-harden`
**Date:** 2026-02-20

## Introduction

MS-4a hardens MMM analysis scripts that power the modeling layer by validating outputs, tightening edge-case handling, and guaranteeing stable JSON contract behavior before they are called by agents and APIs.

## Goals

- Validate regression, ROI, optimizer, and adstock outputs against expected schema and numeric quality checks.
- Ensure MMM summary helper returns all required dashboard fields.
- Add package hygiene for MMM scripts package import.
- Identify and fix output consistency issues before MS-4b and MS-5 depend on these scripts.

## User Stories

### US-001: Validate regression outputs and importance rankings
**Description:** As a model operator, I want regression output to include stable fields and quality metrics so downstream agents can rely on it.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_scripts/regression.py` prints JSON with `r_squared` and dictionary `coefficients`.
- [ ] `r_squared` is > 0.5 on standard synthetic dataset.
- [ ] `coefficient_magnitudes` exists and is a normalized ranking of channel importance.

### US-002: Validate ROI output includes all channels
**Description:** As a strategist, I want ROI output to be channel-complete so every channel budget decision is informed.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_scripts/roi_analysis.py` returns JSON with 11 channel entries.
- [ ] Each channel contains both `roi` and `marginal_roi`.
- [ ] Numerical output is finite and non-negative where defined.

### US-003: Validate optimizer constraints
**Description:** As an operations owner, I need optimizer results within defined spend constraints so recommendations stay feasible.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_scripts/budget_optimizer.py` keeps each channel within ±30% of current spend.
- [ ] Total recommended budget equals current total spend within tolerance.
- [ ] Output retains source channel labels and constraints metadata.

### US-004: Validate adstock curve outputs
**Description:** As an analyst, I want decay and saturation arrays for each channel to support model explainability.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_scripts/adstock_curves.py` outputs per-channel arrays with keys `raw`, `adstocked`, and `saturated`.
- [ ] Arrays are monotonic where expected and same length per channel.

### US-005: Validate MMM summary contract
**Description:** As a UI layer, I need consistent summary fields so dashboard rendering is deterministic.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_summary.py` `build_mmm_summary()` returns `total_spend`, `total_units`, `total_revenue`, `channel_breakdown`, `weekly_spend`, and `weeks_of_data`.
- [ ] `channel_breakdown` includes all supported MMM channels.
- [ ] Summary helper gracefully handles missing files with informative errors.

### US-006: Package init for MMM scripts
**Description:** As a developer, I want `src.platform.api.mmm_scripts` to be import-safe as a module.

**Acceptance Criteria:**
- [ ] `src/platform/api/mmm_scripts/__init__.py` exists.
- [ ] Existing imports using module form succeed.

## Functional Requirements

- FR-1: Validate standalone script outputs via `python script.py | python -m json.tool` checks.
- FR-2: Fix any schema mismatches and output formatting issues discovered during validation.
- FR-3: Add validation guards for edge cases and missing files.
- FR-4: Ensure `coefficient_magnitudes` is computed from normalized coefficient abs values and included in JSON.
- FR-5: Add `src/platform/api/mmm_scripts/__init__.py` if absent.

## Non-Goals

- Implementing the MMM agent and API endpoints (MS-4b).
- Refactoring the underlying MMM model math unless a runtime bug is discovered in validation.
- Adding new optimization algorithms beyond current scope.

## Technical Considerations

- Scripts are single-file and imported in future agent workflows; keep output deterministic and compact JSON.
- Use clear assertions and exception paths to avoid silent `None` payloads.
- Preserve script entrypoints for manual execution.

## Files to Modify

| File | Change |
|------|--------|
| `src/platform/api/mmm_scripts/regression.py` | Validate/fix output fields |
| `src/platform/api/mmm_scripts/roi_analysis.py` | Validate/fix output fields |
| `src/platform/api/mmm_scripts/budget_optimizer.py` | Validate constraints |
| `src/platform/api/mmm_scripts/adstock_curves.py` | Validate curve output fields |
| `src/platform/api/mmm_summary.py` | Validate return contract |
| `src/platform/api/mmm_scripts/__init__.py` | New |

## Success Metrics

- `python src/platform/api/mmm_scripts/regression.py | python -m json.tool` returns valid JSON with required fields.
- `python src/platform/api/mmm_scripts/roi_analysis.py | python -m json.tool` includes 11 channels.
- `python src/platform/api/mmm_scripts/budget_optimizer.py | python -m json.tool` constraints hold in output.
- `python src/platform/api/mmm_scripts/adstock_curves.py | python -m json.tool` includes per-channel arrays.
- `python -c` call to `build_mmm_summary()` passes contract checks.

## Verification

```bash
python src/platform/api/mmm_scripts/regression.py | python -m json.tool
python src/platform/api/mmm_scripts/roi_analysis.py | python -m json.tool
python src/platform/api/mmm_scripts/budget_optimizer.py | python -m json.tool
python src/platform/api/mmm_scripts/adstock_curves.py | python -m json.tool
python -c "from src.platform.api.mmm_summary import build_mmm_summary; s=build_mmm_summary(); assert 'total_spend' in s and 'channel_breakdown' in s; print('Summary OK')"
```

## Open Questions

- Should regression quality checks include confidence intervals for coefficients in this phase or later when scripts are upgraded?
