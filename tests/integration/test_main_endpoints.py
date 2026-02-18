"""Tests for untested endpoints in src/platform/api/main.py."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.platform.api.data_profiles import ProfileError


OVERVIEW_MOCK_TARGET = "src.platform.api.main.build_overview"
PREVIEW_MOCK_TARGET = "src.platform.api.main.load_preview"


# ── Health & root ────────────────────────────────────────────────────────


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_root_default_theme(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "SERVICE ONLINE" in resp.text


def test_root_light_theme(client):
    resp = client.get("/?theme=light")
    assert resp.status_code == 200
    body = resp.text
    assert "'light'" in body or "light" in body


# ── Dashboard endpoints ─────────────────────────────────────────────────


@patch(OVERVIEW_MOCK_TARGET)
def test_dashboard_summary(mock_build, client, mock_overview):
    mock_build.return_value = mock_overview
    resp = client.get("/api/raw/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "files" in data
    assert "checks" in data


@patch(OVERVIEW_MOCK_TARGET)
def test_dashboard_files(mock_build, client, mock_overview):
    mock_build.return_value = mock_overview
    resp = client.get("/api/raw/dashboard/files")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "files" in data
    assert "checks" not in data


@patch(OVERVIEW_MOCK_TARGET)
def test_dashboard_checks(mock_build, client, mock_overview):
    mock_build.return_value = mock_overview
    resp = client.get("/api/raw/dashboard/prd-checks")
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "checks" in data
    assert "files" not in data


# ── File preview ────────────────────────────────────────────────────────


@patch(PREVIEW_MOCK_TARGET)
def test_file_preview_success(mock_load, client):
    mock_load.return_value = {
        "file_name": "test.csv",
        "rows": 5,
        "columns": ["a", "b"],
        "preview_rows": [{"a": 1, "b": 2}],
    }
    resp = client.get("/api/raw/dashboard/file/test.csv")
    assert resp.status_code == 200
    assert resp.json()["file_name"] == "test.csv"


def test_file_preview_rows_too_low(client):
    resp = client.get("/api/raw/dashboard/file/test.csv?rows=0")
    assert resp.status_code == 400


def test_file_preview_rows_too_high(client):
    resp = client.get("/api/raw/dashboard/file/test.csv?rows=201")
    assert resp.status_code == 400


@patch(PREVIEW_MOCK_TARGET, side_effect=ProfileError("file does not exist: missing.csv"))
def test_file_preview_not_found(mock_load, client):
    resp = client.get("/api/raw/dashboard/file/missing.csv")
    assert resp.status_code == 404
    assert "missing.csv" in resp.json()["detail"]


# ── Dataset list ────────────────────────────────────────────────────────


@patch(OVERVIEW_MOCK_TARGET)
def test_data_datasets(mock_build, client, mock_overview):
    mock_build.return_value = mock_overview
    resp = client.get("/api/data/datasets")
    assert resp.status_code == 200
    datasets = resp.json()
    assert isinstance(datasets, list)
    csv_names = [d["name"] for d in datasets]
    assert "test.csv" in csv_names
    assert all("contracts" not in n for n in csv_names)


# ── __init__.py coverage ────────────────────────────────────────────────


def test_api_init_unknown_attr():
    import src.platform.api as api_pkg
    with pytest.raises(AttributeError):
        _ = api_pkg.nonexistent_attribute
