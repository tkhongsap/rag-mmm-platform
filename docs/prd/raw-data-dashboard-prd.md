# Raw Data Inventory Dashboard PRD

## 1. Purpose

Create a simple frontend page that shows what synthetic raw data is available for local development and where it fails or passes the PRD-based quality checks defined for the platform. The dashboard should help product and data teams quickly verify whether `data/raw` is ready to drive app development.

## 2. Problem

- Raw files are currently not visually summarized.
- Data checks are not centrally surfaced in one place.
- Team members lack a fast signal for missing columns, wrong row volumes, and failed PRD expectations before running pipelines.

## 3. Goals

- Show an inventory of all files under `data/raw` with row count, column count, file size, and update time.
- Run a machine-readable PRD check set from `docs/prd/dashboard_checks.yml` and show pass/warn/fail status per rule.
- Allow users to inspect a quick row-level preview of any file.
- Keep the page single-screen and lightweight for local use.

## 4. Success Criteria

- One page must render in under 2 seconds on local data sizes (current synthetic corpus).
- At least `N-1` check categories visible at all times:
  - file inventory
  - check status list
  - selected-file preview
- Checks should refresh from source files without rebuilding the frontend.
- No critical warnings in console during normal operation.

## 5. Data Scope and Dimensions

- Input files: all current files under `data/raw`, including contract markdown files.
- For each CSV:
  - rows, columns, size, null ratio, last modified timestamp
  - distinct values sample for quick inspection
  - date span for inferred date fields
- PRD checks:
  - `row_count_between`
  - `required_columns`
  - `date_range`
  - `min_non_null_ratio`
  - `required_values`
  - `numeric_range`
  - `foreign_key_reference`

## 6. Functional Requirements

1. Backend service:
   - Expose `/api/raw/dashboard/summary`, `/api/raw/dashboard/files`, `/api/raw/dashboard/prd-checks`, and `/api/raw/dashboard/file/{file_name}` endpoints.
   - Use `docs/prd/dashboard_checks.yml` as the source of truth for check definitions.
   - Return JSON payloads suitable for direct rendering in the UI.
2. Frontend page:
   - Display cards for overall summary (counts and checks pass/fail).
   - List all files in a selectable table.
   - Show PRD check results in a status table.
   - Show a preview panel of the selected file (first `n` rows).
3. Deployment model:
   - Run as a lightweight local React app.
   - Consume backend through `VITE_API_BASE` env variable.

## 7. Out of Scope

- Editing or correcting raw data records from the UI.
- Running heavy ETL/transformation pipelines in-browser.
- Authn/z or role-based access controls.

## 8. Milestones

1. Backend profiling + check API.
2. React single-page dashboard with summary and file table.
3. PRD conformance table and preview interaction.
4. Smoke-test against local dataset and document run commands.
