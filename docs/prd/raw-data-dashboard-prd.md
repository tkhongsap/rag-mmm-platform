# Raw Data Inventory Dashboard PRD

## What We Want to Do

Build a simple local frontend dashboard for synthesized raw data in `data/raw` so we can assess data readiness before building or iterating on MMM/RAG features. The dashboard must:

- show what files are present,
- summarize size/shape/quality dimensions,
- run PRD-based checks from a rule file,
- and surface quick file previews in one place.

## Objective

Provide a fast and reliable visibility layer for synthesized dataset quality so the team can:

- confirm that generated data is present and structurally compatible with PRD expectations,
- identify where data fails checks and why,
- decide quickly whether the dataset is ready for app/modeling work.

## Expected Outcome

- A one-page React dashboard running locally on `http://localhost:3000` that reads data from the local FastAPI backend.
- A consistent summary of raw data inventory:
  - total files, total CSV files, total rows, and total byte size,
  - row/column counts and null ratios per file,
  - last modified timestamps for traceability.
- A PRD conformance list showing pass/warn/fail for each rule defined in `docs/prd/dashboard_checks.yml`.
- A file preview workflow where users can click a file and inspect its first `N` rows without opening files manually.
- Reduced decision time for model/onboarding and faster triage of synthetic data issues.

## Scope

- Backend: expose API endpoints that scan `data/raw`, evaluate checks, and return summary/check/preview payloads.
- Frontend: single-page UI with:
  - summary cards,
  - file inventory table,
  - PRD check table,
  - selected-file preview panel.
- PRD rules source of truth: `docs/prd/dashboard_checks.yml`.

## Functional Requirements

1. API behavior
   - `GET /api/raw/dashboard/summary` returns:
     - global summary,
     - file list,
     - check results.
   - `GET /api/raw/dashboard/files` returns summary + file list only.
   - `GET /api/raw/dashboard/prd-checks` returns summary + check results only.
   - `GET /api/raw/dashboard/file/{file_name:path}?rows=<1..200>` returns preview rows.

2. Check evaluation
   - Supported check types:
     - `exists`
     - `row_count_between`
     - `required_columns`
     - `date_range`
     - `required_values`
     - `numeric_range`
     - `min_non_null_ratio`
     - `foreign_key_reference`
   - Check metadata is read from YAML and displayed with status (`pass`, `warn`, `fail`).

3. UI behavior
   - Load dashboard summary on mount.
   - Allow refresh without restarting app.
   - Click table row to fetch and display preview for that file.
   - Preserve simple visual hierarchy: summary → file table/PRD status → preview panel.

4. Operational constraints
   - No data edits in UI.
   - No authentication requirement in this phase (local developer utility).
   - Local-only data source (`data/raw`) is expected.

## Success Criteria

- Dashboard renders on first load with a populated inventory.
- At least 95% of checks are visible and readable in the PRD table.
- Preview loads for selected CSV and contract/text file when requested.
- Any failed rule clearly displays file, rule, observed vs expected, and detail message.
- Re-runs against changed files are possible by clicking Refresh.

## Acceptance Scenarios

1. Empty `data/raw`
   - Summary loads with file count zero.
   - UI does not crash and shows an appropriate empty state.

2. Populated `data/raw` with known-good files
   - Inventory lists all files with row/column stats for CSVs.
   - Multiple checks render as pass.

3. Known rule failure (example)
   - `events_market_coverage` check fails if market coverage does not include required values.
   - PRD table shows `fail` with explicit coverage gap in details.

4. Preview
   - Selecting a file loads `rows` sample payload and displays in the preview area.

## Timeline (Implementation)

1. Backend + rule integration
   - Implement profiler/check evaluator.
   - Add API contracts above.
2. Frontend single page
   - Implement summary, files, checks, and preview components.
3. Integration and smoke test
   - Run local checks against generated synthetic data and document run commands.
