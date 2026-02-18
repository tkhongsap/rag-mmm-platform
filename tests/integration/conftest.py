"""Shared fixtures for integration tests."""

from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from src.platform.api.main import app


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def sample_csv_df():
    return pd.DataFrame({
        "date": ["2025-01-06", "2025-01-13", "2025-01-20", "2025-01-27", "2025-02-03"],
        "campaign_name": ["camp_a", "camp_b", "camp_c", "camp_a", "camp_b"],
        "spend": [1000.0, 2000.0, 1500.0, 1800.0, 2200.0],
        "impressions": [50000, 60000, 55000, 58000, 62000],
        "clicks": [500, 600, 550, 580, 620],
    })


@pytest.fixture()
def sample_profile():
    return {
        "file_name": "test.csv",
        "path": "/fake/data/raw/test.csv",
        "file_size_bytes": 1234,
        "last_modified": "2025-06-01T00:00:00",
        "is_csv": True,
        "rows": 5,
        "columns": 5,
        "column_names": ["date", "campaign_name", "spend", "impressions", "clicks"],
        "column_profiles": [],
        "overall_missing_ratio": 0.0,
        "date_columns": {
            "date": {"min": "2025-01-06", "max": "2025-02-03"},
        },
    }


@pytest.fixture()
def sample_profiles(sample_profile):
    return {"test.csv": sample_profile}


@pytest.fixture()
def sample_frames(sample_csv_df):
    return {"test.csv": sample_csv_df}


@pytest.fixture()
def mock_overview():
    return {
        "summary": {
            "total_files": 2,
            "csv_files": 1,
            "total_rows": 5,
            "total_size_bytes": 2000,
            "passing_checks": 1,
            "warn_checks": 0,
            "failing_checks": 0,
            "scanned_at": "2025-06-01T00:00:00",
        },
        "files": [
            {
                "file_name": "test.csv",
                "is_csv": True,
                "rows": 5,
                "columns": 5,
                "file_size_bytes": 1234,
                "last_modified": "2025-06-01T00:00:00",
            },
            {
                "file_name": "contracts/vendor.md",
                "is_csv": False,
                "rows": None,
                "columns": None,
                "file_size_bytes": 800,
                "last_modified": "2025-06-01T00:00:00",
            },
        ],
        "checks": [
            {
                "id": "chk1",
                "title": "test exists",
                "file": "test.csv",
                "status": "pass",
                "expected": True,
                "observed": True,
                "details": "test.csv exists",
            },
        ],
    }
