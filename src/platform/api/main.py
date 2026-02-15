"""FastAPI server for raw-data inventory and PRD conformance checks."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .data_profiles import build_overview, load_preview, ProfileError

app = FastAPI(title="RAG + MMM Data Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>RAG + MMM Platform API</title>
    <style>
      :root {{
        color-scheme: dark;
        font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      }}
      body {{
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: radial-gradient(circle at 15% 10%, #1f2d4a 0%, #0d1a2d 45%, #070f1b 100%);
        color: #e9eef7;
      }}
      .card {{
        width: min(560px, 92vw);
        border: 1px solid #2d4a78;
        border-radius: 18px;
        padding: 28px;
        background: linear-gradient(140deg, #111f32, #162844 55%, #0d1a2f);
        box-shadow: 0 16px 35px rgba(3, 8, 18, 0.45);
      }}
      .status {{
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(16, 185, 129, 0.12);
        color: #8fffc8;
        font-weight: 700;
        letter-spacing: 0.02em;
      }}
      .dot {{
        width: 10px;
        height: 10px;
        border-radius: 999px;
        background: #2de39f;
        box-shadow: 0 0 10px #2de39f;
      }}
      h1 {{
        margin: 14px 0 8px;
        font-size: 1.5rem;
      }}
      p {{ margin: 8px 0; color: #c2d1ec; }}
      .meta {{
        margin-top: 18px;
        padding: 12px 14px;
        border: 1px solid #2a3f63;
        border-radius: 10px;
        background: rgba(8, 20, 39, 0.7);
      }}
      .links {{
        margin-top: 18px;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
      }}
      a {{
        text-decoration: none;
        color: #8bc5ff;
        font-weight: 600;
      }}
      a:hover {{ text-decoration: underline; }}
      .footer {{
        margin-top: 14px;
        font-size: 0.85rem;
        color: #9ab1d2;
      }}
    </style>
  </head>
  <body>
    <main class=\"card\">
      <div class=\"status\">
        <span class=\"dot\" aria-hidden=\"true\"></span>
        SERVICE ONLINE
      </div>
      <h1>RAG + MMM Platform API</h1>
      <p>Raw-data dashboard API is running and reachable.</p>
      <div class=\"meta\">
        <p><strong>Endpoint:</strong> /</p>
        <p><strong>Checked at:</strong> {now}</p>
        <p><strong>JSON health check:</strong> <a href=\"/health\">/health</a></p>
        <p><strong>API docs:</strong> <a href=\"/docs\">/docs</a></p>
      </div>
      <div class=\"links\">
        <a href=\"/api/raw/dashboard/summary\">Dashboard summary JSON</a>
        <a href=\"/api/raw/dashboard/files\">Dashboard files JSON</a>
        <a href=\"/api/raw/dashboard/prd-checks\">PRD checks JSON</a>
      </div>
      <p class=\"footer\">If this page renders, the service is on.</p>
    </main>
  </body>
</html>"""


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
