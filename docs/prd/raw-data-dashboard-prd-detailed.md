# PRD: Raw Data Inventory Dashboard (Detailed)

> **Location note:** This PRD lives in `docs/prd/` (the repo convention for product docs) rather than `tasks/prd-*.md` (the Ralph SKILL.md default). This is intentional — all PRDs in this project are co-located with their associated assets (e.g., `dashboard_checks.yml`).

## 1. Introduction / Overview

Build a local developer dashboard that provides visibility into the synthesized raw data in `data/raw/`. The dashboard consists of a **FastAPI backend** (Python) that scans, profiles, and evaluates data files against PRD-defined rules, and a **React frontend** (Vite + JSX) that presents the results in a single-page UI.

The problem this solves: after running the synthetic data generators (`data/generators/generate_all.py`), the team needs a fast, reliable way to confirm that the output files are present, structurally correct, and conform to PRD expectations — without manually opening individual files or running ad-hoc scripts.

The dashboard reads **only** from `data/raw/` (no writes) and evaluates checks defined in `docs/prd/dashboard_checks.yml`. It runs entirely on localhost and requires no authentication.

## 2. Goals

- **G-1**: Provide a one-page summary of all files in `data/raw/` — count, size, row/column stats, and last-modified timestamps — loadable in under 5 seconds on a typical dev machine.
- **G-2**: Evaluate every rule currently defined in `dashboard_checks.yml` (all per-file and cross-file checks) and display results with pass/warn/fail status.
- **G-3**: Enable file preview (first N rows for CSVs, first 1024 chars for text/markdown) without leaving the dashboard.
- **G-4**: Allow re-scanning via a Refresh button so developers can regenerate data and immediately verify, without restarting the app.
- **G-5**: Surface enough detail on each failed check (file, rule ID, observed value, expected value, detail message) that a developer can diagnose the issue without reading the check engine source code.

## 3. User Stories

### US-001: Backend Summary Endpoint

**Description:** As a frontend client, I want a single API call that returns global summary statistics, per-file profiles, and all check results, so that the dashboard can render its initial view from one request.

**Acceptance Criteria:**
- [ ] `GET /api/raw/dashboard/summary` returns JSON with three top-level keys: `summary`, `files`, `checks`
- [ ] `summary` object contains: `total_files`, `csv_files`, `total_rows`, `total_size_bytes`, `passing_checks`, `warn_checks`, `failing_checks`, `scanned_at`
- [ ] `files` is an array of file profile objects, each with at minimum: `file_name`, `file_size_bytes`, `last_modified`, `is_csv`
- [ ] CSV file profiles additionally include: `rows`, `columns`, `column_names`, `column_profiles`, `overall_missing_ratio`
- [ ] `checks` is an array of check result objects, each with: `id`, `title`, `file`, `status` (pass/warn/fail), `observed`, `expected`, `details`
- [ ] Returns an empty `files` array and empty `checks` array when `data/raw/` is missing or empty (does not error)
- [ ] Responds within 5 seconds for a fully populated `data/raw/` (~19 CSVs + 7 contracts)
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)

### US-002: Backend Filtered Endpoints

**Description:** As a frontend client, I want separate endpoints that return only file profiles or only check results (alongside the global summary), so that the UI can make lighter-weight calls when it only needs partial data.

**Acceptance Criteria:**
- [ ] `GET /api/raw/dashboard/files` returns JSON with `summary` and `files` keys only (no `checks`)
- [ ] `GET /api/raw/dashboard/prd-checks` returns JSON with `summary` and `checks` keys only (no `files`)
- [ ] Both endpoints use the same profiling/scanning logic as `/summary` — results are consistent
- [ ] Both return 200 with empty arrays when `data/raw/` is empty
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)

### US-003: Backend File Preview Endpoint

**Description:** As a frontend client, I want to fetch a preview of any raw file's content (first N rows for CSV, first 1024 chars for text), so that users can inspect data without leaving the dashboard.

**Acceptance Criteria:**
- [ ] `GET /api/raw/dashboard/file/{file_name:path}?rows=N` returns preview data for CSV files
- [ ] CSV response includes: `file_name`, `rows` (total row count), `columns` (column name list), `preview_rows` (array of row objects, max N rows)
- [ ] Non-CSV files (e.g., `contracts/ITV_Airtime_Agreement.md`) return first 1024 characters as a single text entry
- [ ] `rows` parameter is validated: must be between 1 and 200 inclusive; returns HTTP 400 otherwise
- [ ] Returns HTTP 404 with descriptive message when the file does not exist
- [ ] Path traversal outside `data/raw/` is rejected (e.g., `../../etc/passwd` returns 404 or 400)
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)

### US-004: Check Evaluation Engine

**Description:** As a backend developer, I want a check evaluation engine that reads rules from `dashboard_checks.yml` and evaluates them against profiled data, so that the API can report pass/warn/fail status for every defined rule.

**Acceptance Criteria:**
- [ ] All 8 check types are implemented: `exists`, `row_count_between`, `required_columns`, `date_range`, `required_values`, `numeric_range`, `min_non_null_ratio`, `foreign_key_reference`
- [ ] `exists`: returns pass if the file is present in `data/raw/`, fail otherwise
- [ ] `row_count_between`: returns pass if CSV row count is within `[min, max]` range, fail otherwise
- [ ] `required_columns`: returns pass if all listed columns exist in the CSV, fail with list of missing columns
- [ ] `date_range`: parses the specified date column (supports `YYYY-MM-DD` and `YYYY-MM` formats) and returns pass if observed min/max fall within the expected range
- [ ] `required_values`: returns pass if all specified values appear in the column; supports optional `min_ratio` threshold
- [ ] `numeric_range`: returns pass if all values in the column fall within `[min, max]`
- [ ] `min_non_null_ratio`: returns pass if the non-null ratio of the column meets or exceeds `min_ratio`
- [ ] `foreign_key_reference`: returns pass if every value in `target_column` of `target_file` exists in `source_column` of `source_file`; supports `ignore_nulls` and `min_match_ratio`
- [ ] Cross-file checks from the `cross_file_checks` section of the YAML are evaluated alongside per-file checks
- [ ] Each check result includes: `id`, `title`, `file`, `status`, `observed`, `expected`, `details`
- [ ] Unsupported check types return `warn` status with descriptive detail message
- [ ] Engine does not crash if a referenced file is missing — returns `fail` with "file missing" detail
- [ ] `python -m pytest tests/ -v` passes for the check evaluation module

### US-005: Frontend Summary Cards

**Description:** As a developer viewing the dashboard, I want to see key inventory metrics at a glance (total files, CSV count, total rows, total size, check pass rate, last scan time), so that I can immediately assess data readiness.

**Acceptance Criteria:**
- [ ] Dashboard header shows title "Raw Data Inventory" and subtitle "Synthetic data readiness against PRD checks"
- [ ] A "Refresh" button in the header triggers a full re-scan and re-render
- [ ] Summary cards display: Total Files, CSV Files, Total Rows (with locale formatting), Total Size (human-readable: KB/MB/GB), Checks Passing (e.g., "58/62 (94%)"), Checks Warn/Fail counts, Last Scan timestamp
- [ ] All cards update when Refresh is clicked
- [ ] Cards show zeroes (not errors) when `data/raw/` is empty
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)
- [ ] **Verify in browser using dev-browser skill**

### US-006: Frontend File Inventory Table

**Description:** As a developer viewing the dashboard, I want a table listing every file in `data/raw/` with its key statistics (rows, columns, size, modified date, null ratio, type), so that I can quickly scan the inventory.

**Acceptance Criteria:**
- [ ] Table columns: File, Rows, Columns, Size, Modified, Null Ratio, Type
- [ ] CSV files show numeric values for Rows and Columns; non-CSV files show "n/a"
- [ ] Null Ratio is displayed as a percentage (e.g., "0.12%")
- [ ] Type column shows "CSV" or "Other"
- [ ] Clicking a table row selects that file (visually highlighted) and triggers the file preview panel
- [ ] The first file is auto-selected on initial load
- [ ] Table renders an empty state message when no files exist
- [ ] Files are sorted alphabetically by file name
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)
- [ ] **Verify in browser using dev-browser skill**

### US-007: Frontend PRD Conformance Table

**Description:** As a developer viewing the dashboard, I want a table showing every PRD check with its status (pass/warn/fail), associated file, observed value, expected value, and detail message, so that I can identify what fails and why.

**Acceptance Criteria:**
- [ ] Table columns: Status, Check, File, Observed, Expected, Details
- [ ] Status column shows a colored pill/badge: green for pass, yellow/amber for warn, red for fail
- [ ] Observed and Expected columns display JSON values in a readable format (using `<pre>` or monospace)
- [ ] At least 95% of checks from `dashboard_checks.yml` are visible and readable in the table
- [ ] Failed checks clearly show the file name, rule title, what was observed vs. what was expected, and a human-readable detail message
- [ ] Table renders an empty state when no checks exist
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)
- [ ] **Verify in browser using dev-browser skill**

### US-008: Frontend File Preview Panel

**Description:** As a developer viewing the dashboard, I want to click a file in the inventory table and see a preview of its contents (first 20 rows for CSVs, first 1024 chars for text files), so that I can inspect data without opening files manually.

**Acceptance Criteria:**
- [ ] Panel displays below the tables with heading "File Preview"
- [ ] Shows the source file name (e.g., "Source: meta_ads.csv")
- [ ] For CSV files, displays the first 20 rows as formatted JSON
- [ ] For non-CSV files (contracts), displays the text content
- [ ] Shows "Loading preview..." while the preview API call is in flight
- [ ] Shows an error message if the preview request fails
- [ ] Shows "Select a file from the table to view a preview." when no file is selected
- [ ] Preview updates when a different file is selected
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)
- [ ] **Verify in browser using dev-browser skill**

### US-009: Frontend Enhanced Interactions

**Description:** As a developer viewing the dashboard, I want to filter checks by status, choose how many preview rows to load, expand file rows to see column-level profiles, and visually distinguish cross-file checks, so that I can efficiently triage data issues without navigating away.

**Acceptance Criteria:**
- [ ] PRD conformance table has a filter dropdown with options: All, Pass, Warn, Fail
- [ ] Selecting a filter immediately hides non-matching rows; "All" shows everything
- [ ] Filter shows a count badge (e.g., "Fail (3)") so the user sees how many match before filtering
- [ ] Preview panel includes a row-count dropdown with options: 10, 20, 50, 100 (default: 20)
- [ ] Changing the row count triggers a new API call with the updated `rows` parameter
- [ ] Each file row in the inventory table has an expand/collapse toggle (chevron icon)
- [ ] Expanding a CSV file row reveals a sub-table of column-level profiles: column name, dtype, null count, null ratio, distinct count, min/max (numeric or date), sample values
- [ ] Non-CSV file rows do not show the expand toggle
- [ ] Cross-file checks in the PRD table display a "cross-file" indicator badge next to the check title
- [ ] Quality checks pass (`python -m py_compile` for backend files; `npm run build` for frontend)
- [ ] **Verify in browser using dev-browser skill**

## 4. Functional Requirements

### API

- **FR-1:** `GET /api/raw/dashboard/summary` returns a JSON object with keys `summary`, `files`, and `checks`.
- **FR-2:** `GET /api/raw/dashboard/files` returns a JSON object with keys `summary` and `files` only.
- **FR-3:** `GET /api/raw/dashboard/prd-checks` returns a JSON object with keys `summary` and `checks` only.
- **FR-4:** `GET /api/raw/dashboard/file/{file_name:path}?rows=N` returns a JSON preview of the specified file. The `rows` parameter must be between 1 and 200; otherwise the endpoint returns HTTP 400.
- **FR-5:** All API endpoints use the `data/raw/` directory as the sole data source. No other directories are scanned.
- **FR-6:** All API endpoints accept CORS requests from any origin (for local development convenience).
- **FR-7:** A `GET /health` endpoint returns `{"status": "ok"}` for liveness checking.

### Check Engine

- **FR-8:** The check engine reads rules exclusively from `docs/prd/dashboard_checks.yml`. No rules are hardcoded in application code.
- **FR-9:** The engine supports 8 check types: `exists`, `row_count_between`, `required_columns`, `date_range`, `required_values`, `numeric_range`, `min_non_null_ratio`, `foreign_key_reference`.
- **FR-10:** Each check result includes: `id` (from YAML), `title` (from YAML), `file` (which file was checked), `status` (pass/warn/fail), `observed` (actual value found), `expected` (value from the rule), `details` (human-readable explanation).
- **FR-11:** Cross-file checks (defined under `cross_file_checks` in the YAML) are evaluated using the same handler dispatch as per-file checks.
- **FR-12:** If a check references a file that does not exist in `data/raw/`, the check returns `fail` with detail "file missing" (the engine does not throw an exception).
- **FR-13:** If a check type is not recognized, the check returns `warn` with detail "unsupported check type: {type}".

### Frontend

- **FR-14:** The frontend loads dashboard summary data (`/api/raw/dashboard/summary`) on initial page mount.
- **FR-15:** A "Refresh" button in the page header triggers a full re-fetch of summary data without a page reload.
- **FR-16:** Summary cards display: Total Files, CSV Files, Total Rows (locale-formatted), Total Size (human-readable bytes), Checks Passing (count and percentage), Checks Warn/Fail, Last Scan timestamp.
- **FR-17:** The file inventory table lists all files sorted alphabetically by `file_name`, with columns: File, Rows, Columns, Size, Modified, Null Ratio, Type.
- **FR-18:** Clicking a row in the file inventory table selects that file and triggers a preview fetch via `GET /api/raw/dashboard/file/{file_name}?rows=20`.
- **FR-19:** The PRD conformance table displays all check results with columns: Status (pill badge), Check (title), File, Observed, Expected, Details.
- **FR-20:** Status pills use visual color coding: green = pass, amber/yellow = warn, red = fail.
- **FR-21:** The file preview panel shows formatted JSON for CSV previews and raw text for non-CSV files.
- **FR-22:** The dashboard shows appropriate empty states when `data/raw/` contains no files (zero counts, empty tables, no crashes).
- **FR-23:** The dashboard displays a user-visible error message when API calls fail (e.g., backend not running).
- **FR-24:** The PRD conformance table includes a filter dropdown (All / Pass / Warn / Fail) that shows only matching checks. Each option displays a count badge.
- **FR-25:** The file preview panel includes a row-count dropdown (10 / 20 / 50 / 100). Changing the selection triggers a new preview API call with the updated `rows` parameter.
- **FR-26:** Each CSV file row in the inventory table supports expand/collapse to reveal column-level profiles (name, dtype, null count, null ratio, distinct count, numeric min/max, date min/max, sample values). Non-CSV rows are not expandable.
- **FR-27:** Cross-file checks in the PRD conformance table display a visual "cross-file" badge next to the check title to distinguish them from single-file checks.
- **FR-28:** The dashboard uses skeleton loading placeholders (not just a spinner) while initial data is loading.
- **FR-29:** The dashboard uses the `frontend-design` skill for all UI implementation to achieve a polished, production-grade visual design.

## 5. Non-Goals (Out of Scope)

- **No data editing.** The dashboard is read-only. Users cannot modify, delete, or regenerate files from the UI.
- **No authentication or authorization.** This is a local developer utility; no login, tokens, or role-based access.
- **No persistent storage.** The dashboard does not cache results to disk or a database. Every scan reads live from `data/raw/`.
- **No deployment pipeline.** The dashboard runs on `localhost` only — no Docker, CI/CD, or cloud deployment in this phase.
- **No custom check authoring from the UI.** Check rules are defined only in `dashboard_checks.yml`; there is no in-app editor.
- **No real-time file watching.** The dashboard does not auto-refresh when files change. Users must click Refresh.
- **No MMM or RAG pipeline integration.** The dashboard scans `data/raw/` only; it does not trigger or depend on the RAG/MMM modules in `src/`.
- **No pagination or full-text search on tables.** Tables render all rows without pagination. The PRD conformance table supports status filtering (All/Pass/Warn/Fail) but not free-text search. For the expected data volume (~25 files, ~65 checks), this is sufficient.

## 6. Design Considerations

### Design Philosophy

This dashboard should feel like a **premium developer tool** — polished, information-dense, and visually satisfying. Think Linear, Vercel Dashboard, or Raycast: clean typography, generous whitespace, subtle animations, and a cohesive color system. It should not look like a generic Bootstrap admin panel.

**Use the `frontend-design` skill** when implementing all UI stories to ensure distinctive, production-grade visual quality.

### Layout

The dashboard is a single-page layout with four visual sections, top to bottom:

1. **Header bar** — Title, subtitle, and Refresh button (top-right). Subtle bottom border or shadow to separate from content.
2. **Summary cards** — A responsive horizontal row of metric cards with icon accents, micro-animations on data load, and clear visual hierarchy (large number, small label).
3. **Tabbed content area** — File inventory table and PRD conformance table presented as two tabs (or a two-panel grid on wide viewports). Active tab has a clear visual indicator.
4. **Preview panel** — Full-width collapsible panel at the bottom showing selected file contents. Includes a row-count selector dropdown.

### Visual Design Specifications

- **Color system**: Dark-mode-first with a light neutral background option. Use a restrained palette:
  - Pass: emerald green (#10b981) with subtle green-tinted background
  - Warn: amber (#f59e0b) with subtle amber-tinted background
  - Fail: rose red (#f43f5e) with subtle red-tinted background
  - Neutral surfaces: slate grays (#0f172a background, #1e293b cards in dark mode)
  - Accent: a single brand accent color for interactive elements (e.g., indigo #6366f1)
- **Typography**: System font stack for UI text; monospace (JetBrains Mono or Fira Code via CDN, with `monospace` fallback) for data values, code, and preview content
- **Spacing**: 8px base grid. Cards use 16-24px internal padding. Tables use comfortable row heights (40-48px)
- **Borders & shadows**: Subtle 1px borders on cards. Soft box-shadow for elevation. No harsh outlines.
- **Animations**: Fade-in on initial data load. Smooth transitions on tab switches and row selection. Skeleton loading placeholders (not spinner-only) while data is loading.
- **Status pills**: Rounded badges with colored background + matching text. Not just colored text — the badge itself communicates status at a glance.
- **Data density**: Tables should feel information-rich but not cramped. Use alternating row backgrounds or subtle horizontal rules for scanability.
- **Responsive**: Cards reflow to 2-column or stacked on narrow viewports. Tables get horizontal scroll wrappers. Minimum usable width: 768px.

### Existing Components to Evolve

The following components exist in `ui/raw-data-dashboard/src/App.jsx` and should be **redesigned** (not just restyled) to meet the visual standard above:

- `SummaryCard` — upgrade to include icon, subtle background gradient, and number animation on load
- `StatusPill` — upgrade to full badge with background color, rounded corners, and consistent sizing
- `formatBytes()` / `formatDate()` — keep logic, improve output formatting (e.g., relative time for "Last Scan")

### New UI Capabilities (from resolved Open Questions)

- **Check filter dropdown** on the PRD conformance table: filter by All / Pass / Warn / Fail
- **Row-count selector** in the preview panel: dropdown with options 10 / 20 / 50 / 100
- **Expandable file detail** in the inventory table: clicking an expand icon on a row reveals column-level profiles (null ratio, min/max, distinct count, sample values per column)
- **Cross-file check badge**: cross-file checks in the PRD table show a small "cross-file" indicator badge next to the check title to distinguish them from single-file checks

## 7. Technical Considerations

### Backend

| Component | File Path | Notes |
|-----------|-----------|-------|
| FastAPI app | `src/platform/api/main.py` | Defines 4 route handlers + health check |
| Data profiler | `src/platform/api/data_profiles.py` | 677 lines; scans `data/raw/`, builds per-file profiles, evaluates YAML rules |
| Check rules | `docs/prd/dashboard_checks.yml` | Defines all per-file and cross-file validation rules (single source of truth) |
| Data directory | `data/raw/` | ~19 CSVs + 7 markdown contracts |
| Generators | `data/generators/generate_all.py` | Produces the data that the dashboard inspects |

- The profiler (`data_profiles.py`) loads all CSVs into pandas DataFrames for check evaluation. For the current data volume (~63K rows total), this fits comfortably in memory.
- Date parsing supports both `YYYY-MM-DD` and `YYYY-MM` formats via `_parse_dates()` and `_parse_rule_date()`.
- Path traversal protection is implemented via `resolve_raw_path()` which validates that resolved paths remain under `data/raw/`.
- The check handler registry (`CHECK_HANDLERS` dict) maps check type strings to handler functions. Adding a new check type requires adding one function and one dict entry.

### Frontend

| Component | File Path | Notes |
|-----------|-----------|-------|
| React app entry | `ui/raw-data-dashboard/src/main.jsx` | Vite entry point |
| Main component | `ui/raw-data-dashboard/src/App.jsx` | ~224 lines; all UI logic in one component |
| API client | `ui/raw-data-dashboard/src/api.js` | Thin fetch wrapper; base URL from `VITE_API_BASE` env var |
| Styles | `ui/raw-data-dashboard/src/styles.css` | Custom CSS (no framework) |

- The frontend is a single `App` component using React hooks (`useState`, `useEffect`, `useMemo`).
- API base URL defaults to `http://localhost:8000` and can be overridden via `VITE_API_BASE`.
- Preview fetches are cancelable (uses a `cancelled` flag pattern to avoid stale state updates).

### Running Locally

```bash
# Terminal 1: Start backend
cd <project-root>
uvicorn src.platform.api.main:app --reload --port 8000

# Terminal 2: Start frontend
cd ui/raw-data-dashboard
npm install && npm run dev
# Dashboard available at http://localhost:3000 (or Vite's default port)
```

### Dependencies

- **Backend:** FastAPI, uvicorn, pandas, numpy, PyYAML (all in `requirements.txt`)
- **Frontend:** React 18+, Vite (defined in `ui/raw-data-dashboard/package.json`)

## 8. Success Metrics

- **SM-1:** Dashboard renders on first load with a populated inventory within 5 seconds (backend scan + frontend render).
- **SM-2:** At least 95% of all checks currently defined in `dashboard_checks.yml` are visible and readable in the PRD conformance table (accounts for possible future unsupported check types showing as warn).
- **SM-3:** Preview loads successfully for both CSV files and contract/markdown files when a row is clicked.
- **SM-4:** Every failed check displays all five diagnostic fields: file, rule title, observed value, expected value, and detail message.
- **SM-5:** Clicking Refresh re-scans `data/raw/` and updates all summary cards, tables, and the preview panel with fresh data.
- **SM-6:** Dashboard does not crash or show unhandled errors when `data/raw/` is empty — it displays zero counts and empty tables.
- **SM-7:** A developer unfamiliar with the codebase can run the dashboard and understand data readiness status within 2 minutes.

## 9. Resolved Questions

These were originally open questions. They are now resolved and incorporated into the PRD as user stories (US-009) and functional requirements (FR-24 through FR-29).

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| OQ-1 | Filter PRD checks by status? | **Yes** — add a filter dropdown (All/Pass/Warn/Fail) with count badges. | Essential for triage when the check count grows. Implemented in FR-24, US-009. |
| OQ-2 | Configurable preview row count? | **Yes** — add a dropdown (10/20/50/100, default 20). | Low implementation cost; lets users see more data when needed. Implemented in FR-25, US-009. |
| OQ-3 | Show column-level profiles? | **Yes** — expandable detail rows in the file inventory table. | The backend already computes `column_profiles`; surfacing them makes the dashboard significantly more useful. Implemented in FR-26, US-009. |
| OQ-4 | Cache scan results? | **No** — always scan live from `data/raw/`. | This is a local dev tool; simplicity and freshness matter more than avoiding a 2-5 second scan. Users have an explicit Refresh button. |
| OQ-5 | Distinguish cross-file checks? | **Yes** — show a "cross-file" badge on those checks. | Helps developers understand which checks span multiple files without reading the YAML. Implemented in FR-27, US-009. |

## 10. Open Questions

- **OQ-6:** Should the dashboard support a dark/light mode toggle, or ship dark-mode-only? (Current design spec is dark-mode-first.)
- **OQ-7:** Should we add Tailwind CSS (or another utility framework) to the frontend, or continue with custom CSS? Adding Tailwind would accelerate the visual upgrade but adds a build dependency.
