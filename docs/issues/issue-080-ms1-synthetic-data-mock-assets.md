# Issue #80 — MS-1: Synthetic Data & Mock Assets (Foundation)

**State:** OPEN
**Created:** 2026-02-19
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/80

---

## Objective

Ensure all generated data is complete and the asset pipeline produces actual PNG files. This is the **root milestone** — everything else depends on it.

## Current State

- `data/generators/assets.py` exists (326 lines) — review/harden
- `data/generators/generate_all.py` exists with Step 8 present — review/harden
- **However**: PNG files are not on disk, and `aggregate_mmm` import is broken (logic lives in `validators.py`)

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | Mock campaign image generator produces branded PNGs | >= 50 images across 10 channels in `data/assets/{channel}/` |
| 2 | Asset manifest is complete and valid | `data/assets/asset_manifest.csv` exists with columns: `image_path`, `description`, `channel`, `vehicle_model`, `creative_type`, `audience_segment`, `campaign_id`, `dimensions`, `file_size` |
| 3 | `generate_all.py` runs end-to-end including Step 8 | Exit code 0, all 10 validation checks pass, images present |
| 4 | Pillow added to dependencies | `Pillow>=10.0.0` in `requirements.txt`, installs cleanly |

## Tasks

- [ ] **1.1** Fix the `aggregate_mmm` import issue in `generate_all.py` — either create `data/generators/aggregate_mmm.py` that re-exports from `validators.aggregate_mmm_data()`, or fix the import path directly
- [ ] **1.2** Add `Pillow>=10.0.0` to `requirements.txt` if not present; add `qdrant-client>=1.9.0` and `llama-index-vector-stores-qdrant>=0.3.0` for MS-2
- [ ] **1.3** Run `python data/generators/generate_all.py` end-to-end and verify: all 19 CSVs, 7 contracts, ~50 PNGs in `data/assets/{channel}/`, `asset_manifest.csv` with 50+ rows, all 10 validation checks pass
- [ ] **1.4** Add `data/assets/*.png` and `data/qdrant_db/` to `.gitignore`

## Deliverables

| File | Status | Lines |
|------|--------|-------|
| `data/generators/assets.py` | Exists — review/harden | 326 |
| `data/generators/generate_all.py` | Exists — Step 8 present | — |
| `requirements.txt` | Modify | +3 |

## Verification

```bash
pip install -r requirements.txt
python data/generators/generate_all.py
ls data/assets/meta/ data/assets/google/ data/assets/tv/   # images exist
wc -l data/assets/asset_manifest.csv                       # >= 51 (header + 50 rows)
python data/generators/generate_all.py --validate-only     # all checks pass
```

## Dependencies

None — this is the root milestone.

## Blocks

- MS-2 (#81), MS-4a (#83) (everything downstream)

---

📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
