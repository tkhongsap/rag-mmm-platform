"""Tests for src/platform/api/data_profiles.py — value converters, column/file
profiling, check handlers, and orchestration helpers."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from src.platform.api.data_profiles import (
    ProfileError,
    _build_file_profile,
    _check_date_range,
    _check_exists,
    _check_foreign_key_reference,
    _check_min_non_null_ratio,
    _check_numeric_range,
    _check_required_columns,
    _check_required_values,
    _check_row_count,
    _coerce_check_value,
    _column_profile,
    _evaluate_check,
    _looks_like_date_series,
    _parse_dates,
    _parse_rule_date,
    _safe_json_value,
    _to_python_value,
    build_overview,
    evaluate_rules,
    load_preview,
    resolve_raw_path,
    RAW_DATA_DIR,
)


# ── A. Value converters ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "inp, expected",
    [
        (np.bool_(True), True),
        (np.int64(42), 42),
        (np.float64(3.14), 3.14),
        (np.nan, None),
        (pd.Timestamp("2025-01-01"), "2025-01-01T00:00:00"),
        ("hello", "hello"),
    ],
    ids=["np_bool", "np_int64", "np_float64", "np_nan", "pd_timestamp", "plain_str"],
)
def test_to_python_value(inp, expected):
    assert _to_python_value(inp) == expected


def test_safe_json_value_dict():
    result = _safe_json_value({"a": np.int64(1)})
    assert result == {"a": 1}
    assert isinstance(result["a"], int)


def test_safe_json_value_list():
    result = _safe_json_value([np.float64(2.5), np.bool_(False)])
    assert result == [2.5, False]


def test_safe_json_value_numpy_scalar():
    assert _safe_json_value(np.int64(99)) == 99


def test_safe_json_value_nan():
    assert _safe_json_value(np.nan) is None


def test_safe_json_value_timestamp():
    assert _safe_json_value(pd.Timestamp("2025-06-15")) == "2025-06-15T00:00:00"


@pytest.mark.parametrize(
    "inp, expected",
    [
        (None, "none"),
        ("hello", "hello"),
        (42, "42"),
        ([1, 2, 3], "1, 2, 3"),
        ({"key": "val"}, "{'key': 'val'}"),
    ],
    ids=["none", "str", "int", "list", "dict"],
)
def test_coerce_check_value(inp, expected):
    assert _coerce_check_value(inp) == expected


@pytest.mark.parametrize(
    "inp, is_nat",
    [
        (pd.Timestamp("2025-03-01"), False),
        (datetime(2025, 3, 1), False),
        (None, True),
        ("2025-01-01", False),
        ("2025-01", False),
    ],
    ids=["timestamp", "datetime", "none", "date_str", "month_str"],
)
def test_parse_rule_date(inp, is_nat):
    result = _parse_rule_date(inp)
    if is_nat:
        assert result is pd.NaT
    else:
        assert isinstance(result, pd.Timestamp)


# ── B. Date detection + parsing ──────────────────────────────────────────


def test_looks_like_date_series_by_name():
    s = pd.Series([1, 2, 3], name="date")
    assert _looks_like_date_series(s) is True


def test_looks_like_date_series_by_pattern():
    s = pd.Series(["2025-01-01"] * 10, name="col")
    assert _looks_like_date_series(s) is True


def test_looks_like_date_series_negative():
    s = pd.Series(["abc", "def", "ghi"], name="random_col")
    assert _looks_like_date_series(s) is False


def test_parse_dates_iso():
    s = pd.Series(["2025-01-01", "2025-01-02", "2025-01-03"])
    result = _parse_dates(s)
    assert result is not None
    assert len(result) == 3


def test_parse_dates_month():
    s = pd.Series(["2025-01", "2025-02", "2025-03"])
    result = _parse_dates(s)
    assert result is not None
    assert len(result) == 3


def test_parse_dates_empty():
    s = pd.Series([], dtype=str)
    result = _parse_dates(s)
    assert result is None


# ── C. Column profiling ─────────────────────────────────────────────────


def test_column_profile_numeric():
    col = pd.Series([10, 20, 30], name="spend")
    profile = _column_profile(col)
    assert profile["name"] == "spend"
    assert "numeric_min" in profile
    assert "numeric_max" in profile
    assert profile["numeric_min"] == 10
    assert profile["numeric_max"] == 30


def test_column_profile_date():
    col = pd.Series(["2025-01-01", "2025-06-15", "2025-12-31"], name="date")
    profile = _column_profile(col)
    assert profile["name"] == "date"
    assert "date_min" in profile
    assert "date_max" in profile


def test_column_profile_text():
    col = pd.Series(["alpha", "beta", "gamma"], name="label")
    profile = _column_profile(col)
    assert profile["name"] == "label"
    assert "sample_values" in profile
    assert "numeric_min" not in profile
    assert "date_min" not in profile


# ── D. File profiling ───────────────────────────────────────────────────


def test_build_file_profile_csv(tmp_path):
    csv = tmp_path / "test.csv"
    csv.write_text("date,spend\n2025-01-01,100\n2025-01-02,200\n")
    with patch("src.platform.api.data_profiles.RAW_DATA_DIR", tmp_path):
        profile = _build_file_profile(csv)
    assert profile["is_csv"] is True
    assert profile["rows"] == 2
    assert profile["columns"] == 2
    assert "date" in profile["column_names"]


def test_build_file_profile_contract(tmp_path):
    md = tmp_path / "vendor.md"
    md.write_text("# Contract\nSome terms.\n")
    with patch("src.platform.api.data_profiles.RAW_DATA_DIR", tmp_path):
        profile = _build_file_profile(md)
    assert profile["is_csv"] is False
    assert "rows" not in profile


def test_resolve_raw_path():
    result = resolve_raw_path("test.csv")
    assert result == (RAW_DATA_DIR / "test.csv").resolve()


# ── E. Check handlers ───────────────────────────────────────────────────


# -- _check_exists --

def test_check_exists_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv"}
    result = _check_exists(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_exists_fail(sample_frames):
    rule = {"file": "missing.csv"}
    result = _check_exists(rule, None, sample_frames)
    assert result["status"] == "fail"


# -- _check_row_count --

def test_check_row_count_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv", "min": 1, "max": 100}
    result = _check_row_count(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_row_count_fail(sample_profile, sample_frames):
    rule = {"file": "test.csv", "min": 100, "max": 200}
    result = _check_row_count(rule, sample_profile, sample_frames)
    assert result["status"] == "fail"


def test_check_row_count_missing(sample_frames):
    rule = {"file": "test.csv", "min": 1, "max": 100}
    result = _check_row_count(rule, None, sample_frames)
    assert result["status"] == "fail"


# -- _check_required_columns --

def test_check_required_columns_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv", "columns": ["date", "spend"]}
    result = _check_required_columns(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_required_columns_fail(sample_profile, sample_frames):
    rule = {"file": "test.csv", "columns": ["date", "nonexistent"]}
    result = _check_required_columns(rule, sample_profile, sample_frames)
    assert result["status"] == "fail"
    assert "nonexistent" in result["observed"]


def test_check_required_columns_not_csv(sample_frames):
    profile = {"is_csv": False}
    rule = {"file": "vendor.md", "columns": ["date"]}
    result = _check_required_columns(rule, profile, sample_frames)
    assert result["status"] == "fail"
    assert "not a CSV" in result["details"]


# -- _check_required_values --

def test_check_required_values_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv", "column": "campaign_name", "values": ["camp_a", "camp_b"]}
    result = _check_required_values(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_required_values_fail(sample_profile, sample_frames):
    rule = {"file": "test.csv", "column": "campaign_name", "values": ["camp_a", "camp_z"]}
    result = _check_required_values(rule, sample_profile, sample_frames)
    assert result["status"] == "fail"


def test_check_required_values_empty_df(sample_profile):
    empty_df = pd.DataFrame({"campaign_name": pd.Series([], dtype=str)})
    frames = {"test.csv": empty_df}
    rule = {"file": "test.csv", "column": "campaign_name", "values": ["camp_a"]}
    result = _check_required_values(rule, sample_profile, frames)
    assert result["status"] == "warn"


# -- _check_date_range --

def test_check_date_range_pass(sample_profile, sample_frames):
    rule = {
        "file": "test.csv",
        "column": "date",
        "min": "2025-01-01",
        "max": "2025-12-31",
    }
    result = _check_date_range(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_date_range_fail(sample_profile, sample_frames):
    rule = {
        "file": "test.csv",
        "column": "date",
        "min": "2025-03-01",
        "max": "2025-12-31",
    }
    result = _check_date_range(rule, sample_profile, sample_frames)
    assert result["status"] == "fail"


def test_check_date_range_nat_boundary(sample_profile, sample_frames):
    rule = {
        "file": "test.csv",
        "column": "date",
        "min": None,
        "max": "2025-12-31",
    }
    result = _check_date_range(rule, sample_profile, sample_frames)
    assert result["status"] == "warn"
    assert "invalid expected date boundary" in result["details"]


# -- _check_numeric_range --

def test_check_numeric_range_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv", "column": "spend", "min": 0, "max": 10000}
    result = _check_numeric_range(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_numeric_range_fail_below(sample_profile, sample_frames):
    rule = {"file": "test.csv", "column": "spend", "min": 5000, "max": 10000}
    result = _check_numeric_range(rule, sample_profile, sample_frames)
    assert result["status"] == "fail"


def test_check_numeric_range_missing_file(sample_frames):
    rule = {"file": "missing.csv", "column": "spend", "min": 0, "max": 10000}
    result = _check_numeric_range(rule, None, sample_frames)
    assert result["status"] == "fail"


# -- _check_min_non_null_ratio --

def test_check_min_non_null_ratio_pass(sample_profile, sample_frames):
    rule = {"file": "test.csv", "column": "spend", "min_ratio": 0.9}
    result = _check_min_non_null_ratio(rule, sample_profile, sample_frames)
    assert result["status"] == "pass"


def test_check_min_non_null_ratio_fail(sample_profile):
    df = pd.DataFrame({"val": [1.0, None, None, None, None]})
    frames = {"test.csv": df}
    rule = {"file": "test.csv", "column": "val", "min_ratio": 0.9}
    result = _check_min_non_null_ratio(rule, sample_profile, frames)
    assert result["status"] == "fail"


# -- _check_foreign_key_reference --

def test_check_foreign_key_pass():
    source_df = pd.DataFrame({"id": [1, 2, 3]})
    target_df = pd.DataFrame({"ref_id": [1, 2]})
    frames = {"source.csv": source_df, "target.csv": target_df}
    rule = {
        "source_file": "source.csv",
        "target_file": "target.csv",
        "source_column": "id",
        "target_column": "ref_id",
        "min_match_ratio": 1.0,
    }
    result = _check_foreign_key_reference(rule, None, frames)
    assert result["status"] == "pass"


def test_check_foreign_key_fail_orphans():
    source_df = pd.DataFrame({"id": [1, 2]})
    target_df = pd.DataFrame({"ref_id": [1, 2, 99]})
    frames = {"source.csv": source_df, "target.csv": target_df}
    rule = {
        "source_file": "source.csv",
        "target_file": "target.csv",
        "source_column": "id",
        "target_column": "ref_id",
        "min_match_ratio": 1.0,
    }
    result = _check_foreign_key_reference(rule, None, frames)
    assert result["status"] == "fail"


def test_check_foreign_key_missing_source():
    target_df = pd.DataFrame({"ref_id": [1]})
    frames = {"target.csv": target_df}
    rule = {
        "source_file": "source.csv",
        "target_file": "target.csv",
        "source_column": "id",
        "target_column": "ref_id",
    }
    result = _check_foreign_key_reference(rule, None, frames)
    assert result["status"] == "fail"
    assert "source file missing" in result["details"]


# ── F. Orchestration ────────────────────────────────────────────────────


def test_evaluate_check_known_type(sample_profiles, sample_frames):
    rule = {"file": "test.csv", "type": "exists", "id": "c1", "title": "File exists"}
    result = _evaluate_check(rule, sample_profiles, sample_frames)
    assert result["status"] == "pass"
    assert result["id"] == "c1"


def test_evaluate_check_unknown_type(sample_profiles, sample_frames):
    rule = {"file": "test.csv", "type": "bogus_check", "id": "c2", "title": "Bad"}
    result = _evaluate_check(rule, sample_profiles, sample_frames)
    assert result["status"] == "warn"
    assert "unsupported" in result["details"]


def test_evaluate_rules(sample_profiles, sample_frames):
    fake_rules = {
        "files": [
            {
                "file": "test.csv",
                "checks": [
                    {"type": "exists", "id": "r1", "title": "exists check"},
                    {"type": "row_count_between", "id": "r2", "title": "row check", "min": 1, "max": 100},
                ],
            },
        ],
        "cross_file_checks": [
            {"file": "test.csv", "type": "exists", "id": "r3", "title": "cross exists"},
        ],
    }
    with patch("src.platform.api.data_profiles._load_rules", return_value=fake_rules):
        results = evaluate_rules(sample_profiles, sample_frames)
    assert len(results) == 3
    assert all(r["status"] == "pass" for r in results)


def test_build_overview():
    fake_profiles = {
        "test.csv": {
            "file_name": "test.csv",
            "is_csv": True,
            "rows": 5,
            "file_size_bytes": 100,
        },
    }
    fake_frames = {"test.csv": pd.DataFrame({"a": [1]})}
    fake_checks = [{"status": "pass", "id": "c1", "file": "test.csv", "title": "ok",
                     "expected": True, "observed": True, "details": ""}]

    with patch("src.platform.api.data_profiles.scan_raw_directory", return_value=(fake_profiles, fake_frames)), \
         patch("src.platform.api.data_profiles.evaluate_rules", return_value=fake_checks):
        overview = build_overview()

    assert "summary" in overview
    assert "files" in overview
    assert "checks" in overview
    assert overview["summary"]["csv_files"] == 1
    assert overview["summary"]["passing_checks"] == 1


def test_load_preview_csv(tmp_path):
    csv = tmp_path / "demo.csv"
    csv.write_text("a,b\n1,2\n3,4\n")
    with patch("src.platform.api.data_profiles.RAW_DATA_DIR", tmp_path):
        result = load_preview("demo.csv", rows=10)
    assert result["rows"] == 2
    assert result["columns"] == ["a", "b"]
    assert len(result["preview_rows"]) == 2


def test_load_preview_markdown(tmp_path):
    md = tmp_path / "note.md"
    md.write_text("# Title\nLine 2\nLine 3\n")
    with patch("src.platform.api.data_profiles.RAW_DATA_DIR", tmp_path):
        result = load_preview("note.md")
    assert result["rows"] == 3
    assert result["columns"] == ["text"]


def test_load_preview_nonexistent(tmp_path):
    with patch("src.platform.api.data_profiles.RAW_DATA_DIR", tmp_path):
        with pytest.raises(ProfileError):
            load_preview("no_such_file.csv")
