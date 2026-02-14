# Raw Data Dashboard Issue Review — 2026-02-14

Status is based on open issues in `tkhongsap/rag-mmm-platform`.

## Open Issues at Review Time
- `#3` US-009: Row-count selector and cross-file check badge
- `#5` US-001: Design system foundation
- `#6` US-002: Header, layout shell, and loading/error states
- `#7` US-003: Summary cards redesign
- `#8` US-004: File inventory table redesign
- `#9` US-005: PRD conformance table redesign
- `#10` US-006: File preview panel redesign
- `#11` US-007: Check filter dropdown with count badges
- `#12` US-008: Expandable column profiles in file inventory

## Implementation Mapping

- `#5` UI foundation tokens and font import are implemented in `ui/raw-data-dashboard/index.html` and `ui/raw-data-dashboard/src/styles.css`.
- `#6` Header, refresh button states, skeleton loading, error banner, and empty states are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#7` Summary cards and metric formatting are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#8` Data Files table redesign and row behaviors are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#9` PRD conformance table redesign and status pills are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#10` File preview panel redesign is implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#11` Check filter controls are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#12` Expand/collapse row-level column profiles are implemented in `ui/raw-data-dashboard/src/App.jsx` and `ui/raw-data-dashboard/src/styles.css`.
- `#3` Row-count selector behavior is implemented in `ui/raw-data-dashboard/src/App.jsx`; cross-file badge behavior is implemented with reusable detection logic in `ui/raw-data-dashboard/src/App.jsx`.

## Additional AC closure in this PR
- Added explicit cross-file badge detection via `isCrossFileCheck` in `ui/raw-data-dashboard/src/App.jsx`.
- Added explicit `Loading preview...` label in the preview loading state.

## Note
All open issues above are now implemented in code with these enhancements.
