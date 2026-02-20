# PRD: MS-5 — Frontend Integration: Live Data and Asset Endpoints

**Issue:** [#85](https://github.com/tkhongsap/rag-mmm-platform/issues/85)
**Branch:** `fix/issue-85-ms5-frontend-integration-live-data-asset-endpoints`
**Date:** 2026-02-20

## Introduction

MS-5 wires the existing frontend to live backend endpoints and adds asset serving paths. This makes the product interactive: users can chat with real agents, inspect citations, view inline asset results, and view live MMM dashboard metrics.

## Goals

- Replace placeholder UI data with live RAG and MMM API calls.
- Add session continuity and source visibility to RAG chat.
- Render asset thumbnails from API image endpoints securely.
- Provide a live MMM dashboard with ask MMM capabilities.
- Add robust error handling when backend services are unavailable.

## User Stories

### US-001: Persist RAG sessions in client
**Description:** As a user, I want follow-up RAG questions to maintain context across messages.

**Acceptance Criteria:**
- [ ] `ui/platform/src/api.js` sends and receives `session_id` for chat requests.
- [ ] `RagChat` stores `sessionId` in `sessionStorage`.
- [ ] Subsequent requests include prior session id.

### US-002: Show sources, agent badge, and inline images in chat
**Description:** As a user, I want to see what the system used to answer and who answered it.

**Acceptance Criteria:**
- [ ] Chat responses include a source list with file references.
- [ ] Response shows agent badge (`rag-analyst` or `mmm-analyst`).
- [ ] When response nodes include `image_path`, a thumbnail gallery renders in the chat UI.
- [ ] Thumbnails use safe URL encoding and image API paths.

### US-003: Connect MMM dashboard to live summary
**Description:** As a marketing analyst, I want real KPI numbers and channel charts from live summary data.

**Acceptance Criteria:**
- [ ] `MmmDashboard` fetches `GET /api/mmm/summary` on mount.
- [ ] KPI cards render dynamic values from API response.
- [ ] Channel breakdown is rendered as a bar visualization from `channel_breakdown` data.

### US-004: Add MMM ask chat in dashboard
**Description:** As a user, I want to run MMM questions directly from the dashboard.

**Acceptance Criteria:**
- [ ] Dashboard includes an input for MMM questions.
- [ ] `sendMmmQuestion` endpoint call is implemented and wired.
- [ ] MMM responses render in the dashboard chat area.

### US-005: Add backend asset endpoints
**Description:** As a frontend, I need secure endpoints to search and load assets by path.

**Acceptance Criteria:**
- [ ] `GET /api/assets/search?q=...&channel=...` returns search hits.
- [ ] `GET /api/assets/image/{path}` serves image bytes from `data/assets/`.
- [ ] Path traversal is rejected (relative segments like `..` or absolute path usage).

### US-006: Graceful backend-unavailable states
**Description:** As a user, I want clear UI feedback when backend is not running.

**Acceptance Criteria:**
- [ ] Chat and dashboard pages show useful error banners instead of blank failures.
- [ ] Retry behavior is stable without losing chat history state.

## Functional Requirements

- FR-1: Update `ui/platform/src/api.js` with `sendChatMessage`, `sendMmmQuestion`, and `searchAssets`.
- FR-2: Update `ui/platform/src/pages/RagChat.jsx` with session management and enriched response rendering.
- FR-3: Rewrite `ui/platform/src/pages/MmmDashboard.jsx` to consume live summary and MMM chat endpoint.
- FR-4: Add `GET /api/assets/search` and `GET /api/assets/image/{path}` to `src/platform/api/main.py`.
- FR-5: Implement safe path checks in image serving path.
- FR-6: Add user-visible backend error states.

## Non-Goals

- Visual redesign beyond the required component wiring and data binding.
- Changes to retrieval algorithm quality (MS-6).
- Deployment/container concerns (MS-7).

## Technical Considerations

- Keep UI API calls resilient to partial outages and malformed responses.
- Ensure `sessionStorage` usage avoids exposing sensitive tokens.
- For image path, URL encode and sanitize `path` segments before constructing request URL.
- Use existing CSS conventions where possible, extend for image gallery styles.

## Files to Modify

| File | Change |
|------|--------|
| `ui/platform/src/api.js` | Add sessioned chat, MMM chat, and asset search calls |
| `ui/platform/src/pages/RagChat.jsx` | Add citations, badges, images, session persistence |
| `ui/platform/src/pages/MmmDashboard.jsx` | Replace placeholder data with live API |
| `src/platform/api/main.py` | Add asset search and image serving endpoints |

## Success Metrics

- RAG chat displays sources and agent badge for each assistant response.
- At least one follow-up question reuses prior session and returns context-consistent results.
- MMM dashboard KPI cards and channel bars reflect backend payload values.
- Asset search returns list of hits and images render inline in chat.
- Backend outage surfaces clear error state on both pages instead of blank screens.

## Verification

```bash
# Backend
uvicorn src.platform.api.main:app --reload --port 8000

# Frontend
cd ui/platform && npm run dev

# API checks
curl -s "http://localhost:8000/api/assets/search?q=DEEPAL+launch" | python -m json.tool
curl -s "http://localhost:8000/api/mmm/summary" | python -m json.tool
```

## Open Questions

- Do image thumbnails need lightbox or lazy-loading behavior in this milestone, or in a follow-up UI pass?
