# Issue #85 — MS-5: Frontend Integration — Live Data + Asset Endpoints

**State:** Open
**Created:** 2026-02-19T09:56:24Z
**Updated:** 2026-02-19T09:56:24Z
**Labels:** —
**Assignees:** —
**Source:** https://github.com/tkhongsap/rag-mmm-platform/issues/85

---

## Objective

Wire the React UI to live backend data — real RAG responses with sources, session continuity, inline image results, live MMM dashboard, and asset serving endpoints with security hardening.

## Current State

- `ui/platform/src/pages/RagChat.jsx` — functional with basic agent, no sources/images/sessions
- `ui/platform/src/pages/MmmDashboard.jsx` — hardcoded placeholder data
- `ui/platform/src/api.js` — basic API client, no session management
- Asset HTTP endpoints not yet implemented (moved here from MS-3)

## Key Results

| # | Key Result | Measure |
|---|-----------|---------|
| 1 | RAG Chat shows source citations | Assistant bubbles display list of cited source files |
| 2 | RAG Chat supports session continuity | `sessionId` stored in `sessionStorage`, passed on subsequent messages |
| 3 | RAG Chat renders inline image results | Asset search queries display thumbnail grid with metadata |
| 4 | RAG Chat shows agent badge | Response indicates which agent (rag-analyst / mmm-analyst) answered |
| 5 | MMM Dashboard shows live KPIs | KPI cards populated from `GET /api/mmm/summary` (not hardcoded) |
| 6 | MMM Dashboard shows channel breakdown | CSS bar chart renders `channel_breakdown` data from API |
| 7 | MMM Dashboard has "Ask MMM" chat | Chat section at bottom sends to `POST /api/mmm/chat` |
| 8 | Error states handled gracefully | Helpful message shown when backend is not running |
| 9 | Asset search API endpoint works | `GET /api/assets/search?q=...` returns results with image URLs |
| 10 | Asset image serving is safe and functional | `GET /api/assets/image/{path}` returns image bytes; path traversal outside `data/assets/` is rejected |

## Tasks

- [ ] **5.1** Update `ui/platform/src/api.js`:
  - Modify `sendChatMessage` to pass/receive `session_id`
  - Add `sendMmmQuestion(question)` — POST `/api/mmm/chat`
  - Add `searchAssets(query, channel)` — GET `/api/assets/search`
- [ ] **5.2** Update `ui/platform/src/pages/RagChat.jsx`:
  - Store `sessionId` in component state (persist in `sessionStorage`)
  - Show source file citations below assistant bubbles
  - Show agent badge (rag-analyst / mmm-analyst) next to responses
  - Render inline image thumbnails when response includes `image_path` fields
  - Pass `session_id` in subsequent messages for continuity
- [ ] **5.3** Rewrite `ui/platform/src/pages/MmmDashboard.jsx` (~250 lines):
  - Fetch `/api/mmm/summary` on mount — populate KPI cards with real data
  - Replace placeholder charts with CSS bar charts from `channel_breakdown`
  - Add "Ask MMM" chat section at bottom (reuse bubble pattern from RagChat)
  - Update header badge from "Model not yet trained" to show actual stats
  - Add error state when backend is unavailable
- [ ] **5.4** Add `GET /api/assets/search?q=...&channel=...` endpoint to `main.py` — calls `search_assets()`
- [ ] **5.5** Add `GET /api/assets/image/{path}` endpoint to `main.py` — serves images from `data/assets/` with path traversal protection (normalize paths, reject `..` and absolute paths with 400)
- [ ] **5.6** Add graceful error states on all pages when backend is not running

## Deliverables

| File | Type | Est. Lines |
|------|------|-----------|
| `ui/platform/src/api.js` | Modify | +30 |
| `ui/platform/src/pages/RagChat.jsx` | Modify | +80 |
| `ui/platform/src/pages/MmmDashboard.jsx` | Rewrite | ~250 |
| `src/platform/api/main.py` | Modify | +30 (asset endpoints) |

## Verification

```bash
# Start backend and frontend
uvicorn src.platform.api.main:app --reload --port 8000 &
cd ui/platform && npm run dev &

# Manual browser testing:
# 1. RAG Chat → ask "show me DEEPAL S07 launch creatives" → images render
# 2. RAG Chat → ask "What is Meta CPM?" → source citations appear
# 3. RAG Chat → ask follow-up → session continuity works
# 4. MMM Dashboard → KPI cards show real numbers
# 5. MMM Dashboard → "Ask MMM" → type "What is TV ROI?" → response renders
# 6. Stop backend → pages show error state

# Asset endpoints
curl -s "http://localhost:8000/api/assets/search?q=DEEPAL+launch" | python -m json.tool
curl -i "http://localhost:8000/api/assets/image/../.env"  # expect 400/404
```

## Dependencies

- **MS-3** (#82) — RAG chat API must be live.
- **MS-4b** (#84) — MMM summary and chat endpoints must be live.

---
📋 Reference: [`docs/blueprint/milestones.md`](docs/blueprint/milestones.md) · [`docs/blueprint/team-execution-plan.md`](docs/blueprint/team-execution-plan.md)
