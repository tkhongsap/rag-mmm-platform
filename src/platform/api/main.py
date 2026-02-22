"""FastAPI server for raw-data inventory and PRD conformance checks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .data_profiles import build_overview, load_preview, ProfileError

app = FastAPI(title="RAG + MMM Data Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _normalize_theme(theme: str | None = None) -> Literal["dark", "light"]:
    if theme in {"dark", "light"}:
        return theme
    return "dark"


@app.get("/", response_class=HTMLResponse)
def root(theme: str | None = None) -> str:
    selected_theme = _normalize_theme(theme)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    page = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RAG + MMM Platform API</title>
    <style>
      :root {
        --font-stack: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
        --status-green: #22c55e;
        --status-green-soft: rgba(34, 197, 94, 0.16);
        --status-chip-text: #dfffe6;
        --status-chip-bg: rgba(16, 185, 129, 0.18);
        --page-bg-dark: radial-gradient(115% 90% at 15% 8%, #192f4e 0%, #0b1a2d 36%, #060d1a 100%);
        --card-bg-dark: linear-gradient(140deg, #111f31, #162848 58%, #0f1d34);
        --card-border-dark: #2d4c7c;
        --muted-dark: #b4c4de;
        --panel-dark: rgba(10, 24, 41, 0.7);
        --line-dark: #2b4363;
        --link-dark: #8bc5ff;
        --text-dark: #e9eef7;
        --footer-dark: #9fb6d8;
        --shadow-dark: 0 16px 35px rgba(3, 8, 18, 0.45);
      }
      [data-theme='dark'] {
        color-scheme: dark;
        --page-bg: var(--page-bg-dark);
        --card-bg: var(--card-bg-dark);
        --card-border: var(--card-border-dark);
        --muted: var(--muted-dark);
        --panel: var(--panel-dark);
        --line: var(--line-dark);
        --status-green: #22c55e;
        --status-green-soft: rgba(34, 197, 94, 0.16);
        --status-chip-text: #dfffe6;
        --status-chip-bg: rgba(16, 185, 129, 0.16);
        --status-chip-shadow: rgba(16, 185, 129, 0.35);
        --status-dot: #2de39f;
        --text-main: #e9eef7;
        --text-muted: var(--muted);
        --link: var(--link-dark);
        --footer: #9ab1d2;
        --shadow: var(--shadow-dark);
      }
      [data-theme='light'] {
        color-scheme: light;
        --page-bg: radial-gradient(110% 90% at 15% 8%, #f5f9ff 0%, #e6edf8 36%, #dce6f4 100%);
        --card-bg: linear-gradient(140deg, #ffffff, #eaf2ff 55%, #f5f8ff);
        --card-border: #bfd0ea;
        --muted: #516480;
        --panel: rgba(245, 250, 255, 0.76);
        --line: #c9d8eb;
        --status-green: #16a34a;
        --status-green-soft: rgba(22, 163, 74, 0.16);
        --status-chip-text: #f0fff3;
        --status-chip-bg: rgba(16, 185, 129, 0.14);
        --status-chip-shadow: rgba(22, 163, 74, 0.28);
        --status-dot: #18be62;
        --text-main: #132b4b;
        --text-muted: #516480;
        --link: #2060c5;
        --footer: #6f7f97;
        --shadow: 0 16px 30px rgba(25, 41, 66, 0.14);
      }
      :root {
        font-family: var(--font-stack);
      }
      :root[data-theme='dark'],
      :root[data-theme='light'] {
        color: var(--text-main);
      }
      [data-theme='dark'] .card,
      [data-theme='light'] .card {
        color: var(--text-main);
      }
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        padding: 16px;
        background: var(--page-bg);
        color: var(--text-main);
        line-height: 1.35;
      }
      .card {
        width: min(680px, 92vw);
        border: 1px solid var(--card-border);
        border-radius: 18px;
        padding: 28px;
        background: var(--card-bg);
        box-shadow: var(--shadow);
      }
      .status {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px;
        border-radius: 999px;
        background: var(--status-chip-bg);
        color: var(--status-chip-text);
        font-weight: 700;
        letter-spacing: 0.02em;
        box-shadow: 0 0 0 1px color-mix(in srgb, var(--status-chip-bg) 74%, transparent),
          0 8px 18px var(--status-chip-shadow);
      }
      .dot {
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: var(--status-dot);
        box-shadow: 0 0 10px var(--status-dot);
      }
      h1 {
        margin: 14px 0 8px;
        font-size: 1.5rem;
      }
      p {
        margin: 8px 0;
        color: var(--muted);
      }
      .meta {
        margin-top: 18px;
        padding: 12px 14px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel);
      }
      .links {
        margin-top: 18px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }
      a {
        text-decoration: none;
        color: var(--link);
        font-weight: 600;
      }
      a:hover {
        text-decoration: underline;
      }
      .footer {
        margin-top: 14px;
        font-size: 0.85rem;
        color: var(--footer);
      }
      .controls {
        margin-top: 12px;
        display: flex;
        justify-content: flex-end;
      }
      button {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: transparent;
        color: var(--text-main);
        padding: 8px 12px;
        font-size: 0.78rem;
        font-weight: 700;
        cursor: pointer;
        letter-spacing: 0.02em;
      }
      button:hover {
        background: color-mix(in srgb, var(--text-main) 10%, transparent);
      }
    </style>
    <script>
      const themeFromServer = '__THEME__';
      const storageKey = 'rag-mmm-api-theme';
      const buttonLabel = {
        dark: '☀️ Light mode',
        light: '🌙 Dark mode',
      };

      const normalizeTheme = (value) => (value === 'light' || value === 'dark' ? value : null);

      const initTheme = () => {
        const queryTheme = new URLSearchParams(window.location.search).get('theme');
        const urlSafeTheme = normalizeTheme(queryTheme);
        const storedTheme = normalizeTheme(localStorage.getItem(storageKey));
        const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
        return urlSafeTheme || storedTheme || (systemPrefersLight ? 'light' : 'dark');
      };

      const applyTheme = (nextTheme) => {
        document.documentElement.setAttribute('data-theme', nextTheme);
        const button = document.getElementById('theme-toggle');
        if (button) {
          button.textContent = buttonLabel[nextTheme];
          button.setAttribute('aria-label', `Switch to ${nextTheme === 'dark' ? 'light' : 'dark'} theme`);
        }

        try {
          localStorage.setItem(storageKey, nextTheme);
        } catch {
          // Ignore storage access exceptions in locked-down contexts.
        }

        const params = new URLSearchParams(window.location.search);
        params.set('theme', nextTheme);
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        window.history.replaceState({}, '', newUrl);
      };

      const toggleTheme = () => {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const nextTheme = current === 'dark' ? 'light' : 'dark';
        applyTheme(nextTheme);
      };

      const serverTheme = normalizeTheme(themeFromServer) || 'dark';
      const applyInitialTheme = () => {
        applyTheme(initTheme() || serverTheme);
      };

      applyInitialTheme();
      window.addEventListener('DOMContentLoaded', applyInitialTheme);
    </script>
  </head>
  <body>
    <main class="card">
      <div class="status">
        <span class="dot" aria-hidden="true"></span>
        SERVICE ONLINE
      </div>
      <div class="controls">
        <button type="button" id="theme-toggle" onclick="toggleTheme()" aria-label="Switch theme"></button>
      </div>
      <h1>RAG + MMM Platform API</h1>
      <p>Raw-data dashboard API is running and reachable.</p>
      <div class="meta">
        <p><strong>Endpoint:</strong> /</p>
        <p><strong>Checked at:</strong> __NOW__</p>
        <p><strong>JSON health check:</strong> <a href="/health">/health</a></p>
        <p><strong>API docs:</strong> <a href="/docs">/docs</a></p>
      </div>
      <div class="links">
        <a href="/api/raw/dashboard/summary">Dashboard summary JSON</a>
        <a href="/api/raw/dashboard/files">Dashboard files JSON</a>
        <a href="/api/raw/dashboard/prd-checks">PRD checks JSON</a>
      </div>
      <p class="footer">If this page renders, the service is on.</p>
    </main>
  </body>
</html>"""

    return page.replace("__THEME__", selected_theme).replace("__NOW__", now)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/raw/dashboard/summary")
def raw_dashboard_summary() -> dict:
    return build_overview()


@app.get("/api/raw/dashboard/files")
def raw_dashboard_files() -> dict:
    payload = build_overview()
    return {
        "summary": payload["summary"],
        "files": payload["files"],
    }


@app.get("/api/raw/dashboard/prd-checks")
def raw_dashboard_checks() -> dict:
    payload = build_overview()
    return {
        "summary": payload["summary"],
        "checks": payload["checks"],
    }


@app.get("/api/raw/dashboard/file/{file_name:path}")
def raw_file_preview(file_name: str, rows: int = 20) -> dict:
    if rows < 1 or rows > 200:
        raise HTTPException(status_code=400, detail="rows must be between 1 and 200")
    try:
        payload = load_preview(file_name, rows=rows)
    except ProfileError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return payload


# ---------------------------------------------------------------------------
# Dataset list (consumed by Data Management page)
# ---------------------------------------------------------------------------

_CATEGORY_MAP: dict[str, str] = {
    # Digital media
    "meta_ads.csv": "Digital Media",
    "google_ads.csv": "Digital Media",
    "dv360.csv": "Digital Media",
    "tiktok_ads.csv": "Digital Media",
    "youtube_ads.csv": "Digital Media",
    "linkedin_ads.csv": "Digital Media",
    # Traditional media
    "tv_performance.csv": "Traditional Media",
    "ooh_performance.csv": "Traditional Media",
    "print_performance.csv": "Traditional Media",
    "radio_performance.csv": "Traditional Media",
    # Sales pipeline
    "vehicle_sales.csv": "Sales Pipeline",
    "website_analytics.csv": "Sales Pipeline",
    "configurator_sessions.csv": "Sales Pipeline",
    "leads.csv": "Sales Pipeline",
    "test_drives.csv": "Sales Pipeline",
    # External / context
    "competitor_spend.csv": "External",
    "economic_indicators.csv": "External",
    "events.csv": "External",
    "sla_tracking.csv": "External",
}


@app.get("/api/data/datasets")
def data_datasets() -> list:
    """Return a dataset catalogue entry for each raw CSV file."""
    payload = build_overview()
    datasets = []
    for f in payload["files"]:
        if not f.get("is_csv"):
            continue
        name = f["file_name"]
        datasets.append({
            "name": name,
            "category": _CATEGORY_MAP.get(name, "Other"),
            "rows": f.get("rows") or 0,
            "updated": (f.get("last_modified") or "")[:10],
            "status": "ready",
        })
    return datasets


# ---------------------------------------------------------------------------
# RAG Chat (Agent SDK)
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    history: list = []
    session_id: str | None = None


@app.post("/api/rag/chat")
async def rag_chat(req: ChatRequest) -> dict:
    """Answer a marketing question via agent routing with session continuity."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    from .agents.rag_router import ask_with_routing

    result = await ask_with_routing(req.message, req.session_id)
    return result
