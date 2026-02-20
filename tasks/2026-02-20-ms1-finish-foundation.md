# MS-1: Finish Synthetic Data & Mock Assets (Foundation)

**Date:** 2026-02-20
**Issue:** [#80](https://github.com/tkhongsap/rag-mmm-platform/issues/80)
**Status:** In Progress (~95% complete)
**Blocks:** MS-2 (#81), MS-4a (#83), and all downstream milestones

---

## Current State

Everything is generated and on disk:
- 19 CSVs in `data/raw/`
- 7 markdown contracts in `data/raw/contracts/`
- 3 MMM-ready datasets in `data/mmm/` (model_ready, weekly_channel_spend, weekly_sales)
- 50 PNG campaign images across 10 channels in `data/assets/`
- Asset manifest (`data/assets/asset_manifest.csv`) with 50 rows

**4 remaining gaps must be closed before MS-1 is done.**

---

## Task 1: Fix `aggregate_mmm` Import

**File:** `data/generators/generate_all.py` (line 187)

**Problem:** `_import_generator("aggregate_mmm")` tries to import a nonexistent `data/generators/aggregate_mmm.py`. The actual function `aggregate_mmm_data()` lives in `data/generators/validators.py:748`. This causes Step 9 (MMM aggregation) to silently skip with "SKIPPED — module not yet implemented".

**Fix:** Create `data/generators/aggregate_mmm.py` as a thin re-export:

```python
"""Re-export MMM aggregation from validators module."""
from data.generators.validators import aggregate_mmm_data

__all__ = ["aggregate_mmm_data"]
```

**Why this approach:** `generate_all.py` already expects this module (line 187-188). No changes needed to `generate_all.py` itself. Matches the import pattern used by all other generators.

---

## Task 2: Fix Spend Verification Column Filter

**File:** `data/generators/generate_all.py` (line 277)

**Problem:** The spend verification filter requires BOTH "spend" AND "gbp" in column names:

```python
spend_cols = [c for c in df.columns if "spend" in c.lower() and "gbp" in c.lower()]
```

Actual channel CSVs (meta_ads.csv, tv_performance.csv, etc.) use just `"spend"` as the column name. Only `competitor_spend.csv` has `"estimated_spend_gbp"`, which inflates the total to £172M and triggers a false **761.7% deviation warning**.

**Fix:** Update the verification loop (lines 270-283) to:
1. Only scan `data/raw/` (skip `data/mmm/` which double-counts)
2. Exclude `competitor_spend.csv` (external data, not our budget)
3. Match columns named exactly `"spend"` instead of requiring "gbp"

```python
for root, _, files in os.walk(RAW_DIR):
    for f in files:
        if f.endswith(".csv") and f != "competitor_spend.csv":
            ...
            spend_cols = [c for c in df.columns if c.lower() == "spend"]
```

**Expected result:** Deviation should be < 5% (OK) after fix.

---

## Task 3: Add Missing Dependencies to `requirements.txt`

**File:** `requirements.txt`

**Add these packages:**

| Package | Why |
|---------|-----|
| `Pillow>=10.0.0` | Required by `data/generators/assets.py:18` for PNG generation |
| `qdrant-client>=1.9.0` | Vector store client, preps for MS-2 |
| `llama-index-vector-stores-qdrant>=0.3.0` | LlamaIndex Qdrant integration, preps for MS-2 |

---

## Task 4: Add `.gitignore` Entries

**File:** `.gitignore` (in the "Data directories" section, after line 91)

**Add:**

```
data/assets/*
data/qdrant_db/
data/index/
```

- `data/assets/*` — 50 generated PNGs (~950 KB) should not be committed
- `data/qdrant_db/` — vector database directory (MS-2)
- `data/index/` — BM25 index directory (MS-2)

Existing `!data/**/.gitkeep` pattern on line 92 ensures `.gitkeep` files are still tracked.

---

## Verification Checklist

```bash
# 1. Install updated dependencies
pip install -r requirements.txt

# 2. Full end-to-end generation (all 8 steps + aggregation + validation)
python3 data/generators/generate_all.py
# Expected:
#   - Steps 1-8: all OK
#   - MMM aggregation: OK (no longer skips)
#   - All 10 validation checks pass
#   - Spend deviation < 5% (OK)

# 3. Validate-only mode
python3 data/generators/generate_all.py --validate-only

# 4. Confirm assets exist
ls data/assets/meta/ data/assets/google/ data/assets/tv/
wc -l data/assets/asset_manifest.csv   # should be 51 (header + 50 rows)

# 5. Confirm .gitignore works
git status   # data/assets/ PNGs should NOT appear as untracked
```

---

## Files Changed Summary

| File | Change | Est. Effort |
|------|--------|-------------|
| `data/generators/aggregate_mmm.py` | **New** — thin re-export (~4 lines) | 2 min |
| `data/generators/generate_all.py` | **Edit** — fix spend filter (lines 270-283) | 5 min |
| `requirements.txt` | **Edit** — add 3 packages | 2 min |
| `.gitignore` | **Edit** — add 3 entries | 1 min |

---

## What's Next After MS-1

Once MS-1 is closed, two parallel tracks are unblocked:
- **MS-2** (#81) — RAG Pipeline: Ingest, Embed, Retrieve (depends on MS-1)
- **MS-4a** (#83) — MMM Scripts: Validate & Harden (depends on MS-1, parallel track)
