"""FastAPI server for raw-data inventory and PRD conformance checks."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
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


@app.get("/")
def root() -> dict:
    return {
        "status": "online",
        "service": "rag-mmm-platform-api",
        "message": "Service is running",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


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
