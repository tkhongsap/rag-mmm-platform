"""Utilities for profiling raw CSV files and evaluating PRD checks."""

from __future__ import annotations

from datetime import datetime
import warnings
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd
import numpy as np
import yaml


PROJECT_ROOT = Path(__file__).resolve()
for parent in PROJECT_ROOT.parents:
    if (parent / "requirements.txt").is_file() and (parent / "src").is_dir() and (parent / "data").is_dir():
        PROJECT_ROOT = parent
        break

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RULES_PATH = PROJECT_ROOT / "docs" / "prd" / "dashboard_checks.yml"


DATE_CANDIDATE_COLUMNS = {
    "date",
    "created_date",
    "booking_date",
    "test_drive_date",
    "date_week_start",
    "start_date",
    "year_month",
}


class ProfileError(RuntimeError):
    """Raised when a file cannot be read for profiling."""


def resolve_raw_path(reference: str) -> Path:
    """Resolve a path under data/raw with traversal protection."""
    candidate = Path(reference)
    resolved = (RAW_DATA_DIR / candidate).resolve()
    try:
        resolved.relative_to(RAW_DATA_DIR.resolve())
    except ValueError as exc:  # pragma: no cover - impossible by construction, guard only
        raise ProfileError(f"invalid raw-data reference: {reference}") from exc

    return resolved


def _to_python_value(value: Any) -> Any:
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def _looks_like_date_series(values: pd.Series) -> bool:
    lowered = values.name.lower() if values.name else ""
    if lowered in DATE_CANDIDATE_COLUMNS:
        return True

    sample = values.dropna().head(30).astype(str).tolist()
    if not sample:
        return False

    matched = 0
    for value in sample:
        txt = str(value).strip()
        if len(txt) == 7 or len(txt) == 10:
            matched += 1
    return matched >= max(1, int(len(sample) * 0.5))


def _parse_dates(values: pd.Series) -> Optional[pd.Series]:
    if values.empty:
        return None

    values_as_str = values.astype(str)

    sample = values_as_str.dropna().astype(str).head(20)
    date_pattern = sample.str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    month_pattern = sample.str.fullmatch(r"\d{4}-\d{2}")

    if date_pattern.mean() >= 0.8:
        date_series = pd.to_datetime(values, errors="coerce", format="%Y-%m-%d")
    elif month_pattern.mean() >= 0.8:
        date_series = pd.to_datetime(values, errors="coerce", format="%Y-%m")
    else:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Could not infer format.*",
                category=UserWarning,
            )
            date_series = pd.to_datetime(values, errors="coerce")

    if date_series.notna().mean() < 0.5:
        return None
    return date_series


def _column_profile(column: pd.Series) -> Dict[str, Any]:
    col_name = column.name
    null_count = int(column.isna().sum())
    total = int(len(column))
    null_ratio = null_count / total if total else 0.0
    distinct_count = int(column.nunique(dropna=True))

    profile: Dict[str, Any] = {
        "name": col_name,
        "dtype": str(column.dtype),
        "null_count": null_count,
        "null_ratio": round(null_ratio, 6),
        "distinct_count": distinct_count,
    }

    # Sample values for quick inspection in the UI.
    sample_values = (
        column.dropna()
        .astype(str)
        .str.slice(0, 120)
        .drop_duplicates()
        .head(3)
        .tolist()
    )
    profile["sample_values"] = sample_values

    if pd.api.types.is_numeric_dtype(column):
        numeric = pd.to_numeric(column, errors="coerce").dropna()
        if not numeric.empty:
            profile["numeric_min"] = _to_python_value(numeric.min())
            profile["numeric_max"] = _to_python_value(numeric.max())

    if _looks_like_date_series(column):
        parsed = _parse_dates(column)
        if parsed is not None:
            parsed = parsed.dropna()
            if not parsed.empty:
                profile["date_min"] = _to_python_value(parsed.min())
                profile["date_max"] = _to_python_value(parsed.max())

    return profile


def _build_file_profile(path: Path) -> Dict[str, Any]:
    """Build profile for a raw data file."""
    is_contract = path.suffix.lower() != ".csv"
    profile: Dict[str, Any] = {
        "file_name": str(path.relative_to(RAW_DATA_DIR)),
        "path": str(path),
        "file_size_bytes": path.stat().st_size,
        "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
        "is_csv": not is_contract,
    }

    if is_contract:
        return profile

    try:
        df = pd.read_csv(path)
    except Exception as exc:
        raise ProfileError(f"failed to read {path.name}: {exc}") from exc

    profile.update({
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
    })

    column_profiles = [_column_profile(df[col]) for col in df.columns]
    profile["column_profiles"] = column_profiles
    profile["overall_missing_ratio"] = (
        round(df.isna().sum().sum() / max(1, df.size), 6)
    )

    date_columns = {
        col["name"]: {"min": col.get("date_min"), "max": col.get("date_max")} for col in column_profiles
        if "date_min" in col and "date_max" in col
    }
    profile["date_columns"] = date_columns

    if date_columns:
        valid_dates = [
            pd.to_datetime(v["min"]) for v in date_columns.values() if v.get("min") is not None
        ]
        valid_max = [
            pd.to_datetime(v["max"]) for v in date_columns.values() if v.get("max") is not None
        ]
        if valid_dates and valid_max:
            profile["global_date_min"] = _to_python_value(min(valid_dates))
            profile["global_date_max"] = _to_python_value(max(valid_max))

    return profile


def scan_raw_directory() -> Tuple[Dict[str, Dict[str, Any]], Dict[str, pd.DataFrame]]:
    """Return file profiles and loaded CSV dataframes for raw inputs."""
    profiles: Dict[str, Dict[str, Any]] = {}
    dataframes: Dict[str, pd.DataFrame] = {}

    if not RAW_DATA_DIR.exists():
        return profiles, dataframes

    for path in sorted(RAW_DATA_DIR.glob("**/*")):
        if not path.is_file():
            continue
        if path.name == ".gitkeep":
            continue

        relative_name = str(path.relative_to(RAW_DATA_DIR))
        try:
            profile = _build_file_profile(path)
        except ProfileError:
            profile = {
                "file_name": relative_name,
                "path": str(path),
                "file_size_bytes": path.stat().st_size,
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                "is_csv": path.suffix.lower() == ".csv",
                "rows": None,
                "columns": None,
                "column_names": [],
                "column_profiles": [],
                "overall_missing_ratio": 1.0,
                "error": "unable to parse",
            }

        profiles[relative_name] = profile
        if path.suffix.lower() == ".csv":
            try:
                dataframes[relative_name] = pd.read_csv(path)
            except Exception:
                pass

    return profiles, dataframes


def _load_rules() -> Dict[str, Any]:
    if not RULES_PATH.exists():
        raise RuntimeError(f"missing PRD rules file: {RULES_PATH}")

    with RULES_PATH.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f)

    if not isinstance(payload, dict):
        raise RuntimeError("dashboard rules file is invalid")

    return payload


def _safe_json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _safe_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_safe_json_value(v) for v in value]
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, (np.integer, np.int64)):
        return int(value)
    if isinstance(value, (np.floating, np.float64)):
        return float(value)
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def _coerce_check_value(raw: Any) -> str:
    if raw is None:
        return "none"
    if isinstance(raw, (str, int, float, bool)):
        return str(raw)
    if isinstance(raw, (list, tuple)):
        return ", ".join([str(v) for v in raw])
    return str(raw)


def _parse_rule_date(value: Any) -> pd.Timestamp:
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, (datetime,)):
        return pd.Timestamp(value)
    if value is None:
        return pd.NaT
    txt = str(value)
    if len(txt) == 10:
        parsed = pd.to_datetime(txt, errors="coerce", format="%Y-%m-%d")
    elif len(txt) == 7:
        parsed = pd.to_datetime(txt, errors="coerce", format="%Y-%m")
    else:
        parsed = pd.to_datetime(txt, errors="coerce")
    return parsed


def _check_exists(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    passed = file_profile is not None
    return {
        "status": "pass" if passed else "fail",
        "observed": bool(passed),
        "expected": True,
        "details": f"{rule.get('file')} exists" if passed else f"missing file {rule.get('file')}",
    }


def _check_row_count(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    if file_profile is None or file_profile.get("rows") is None:
        return {"status": "fail", "observed": None, "expected": f"{rule.get('min', 0)}-{rule.get('max', 0)}", "details": "file missing or unreadable"}
    rows = int(file_profile["rows"])
    min_rows = int(rule.get("min", 0))
    max_rows = int(rule.get("max", 10**12))
    passed = min_rows <= rows <= max_rows
    return {
        "status": "pass" if passed else "fail",
        "observed": rows,
        "expected": f"{min_rows} to {max_rows}",
        "details": f"rows={rows}",
    }


def _check_required_columns(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    if file_profile is None:
        return {"status": "fail", "observed": None, "expected": rule.get("columns", []), "details": "file missing"}
    if not file_profile.get("is_csv", False):
        return {"status": "fail", "observed": None, "expected": rule.get("columns", []), "details": "not a CSV file"}
    columns = set(file_profile.get("column_names", []))
    required = [str(c) for c in rule.get("columns", [])]
    missing = [c for c in required if c not in columns]
    return {
        "status": "pass" if not missing else "fail",
        "observed": "all present" if not missing else f"missing: {', '.join(missing)}",
        "expected": required,
        "details": "required columns present" if not missing else f"missing {len(missing)} required columns",
    }


def _check_required_values(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    file_name = rule.get("file")
    column = rule.get("column")
    values = rule.get("values", [])
    min_ratio = float(rule.get("min_ratio", 0.0))

    if file_profile is None or not file_profile.get("is_csv", False):
        return {"status": "fail", "observed": None, "expected": values, "details": "file missing or not CSV"}

    df = dataframes.get(file_name or "")
    if df is None or column not in df.columns:
        return {"status": "fail", "observed": None, "expected": values, "details": f"column {column} missing"}

    total = len(df)
    if total == 0:
        return {"status": "warn", "observed": 0, "expected": values, "details": "empty table"}

    series = df[column].astype(str)
    missing_map = {}
    for value in values:
        ratio = float((series == str(value)).mean())
        missing_map[value] = ratio

    missing = [value for value, ratio in missing_map.items() if ratio == 0.0]
    low = [value for value, ratio in missing_map.items() if ratio < min_ratio]

    observed = {
        "values": missing_map,
        "covered_ratio_min": min(missing_map.values(), default=1.0),
    }

    if min_ratio > 0:
        failed = low
    else:
        failed = missing

    return {
        "status": "pass" if not failed else "fail",
        "observed": observed,
        "expected": values,
        "details": "values present" if not failed else f"coverage gaps: {', '.join(map(str, failed))}",
    }


def _check_date_range(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    file_name = rule.get("file")
    column = rule.get("column")
    expected_min = _parse_rule_date(rule.get("min"))
    expected_max = _parse_rule_date(rule.get("max"))

    if expected_min is pd.NaT or expected_max is pd.NaT:
        return {
            "status": "warn",
            "observed": None,
            "expected": {"min": rule.get("min"), "max": rule.get("max")},
            "details": "invalid expected date boundary",
        }

    if file_profile is None:
        return {
            "status": "fail",
            "observed": None,
            "expected": {"min": _coerce_check_value(expected_min), "max": _coerce_check_value(expected_max)},
            "details": "file missing",
        }

    if not file_profile.get("is_csv", False):
        return {"status": "fail", "observed": None, "expected": None, "details": "not a CSV file"}

    date_info = (file_profile.get("date_columns", {}) or {}).get(column)
    if not date_info:
        return {"status": "fail", "observed": None, "expected": None, "details": f"no detectable date column {column}"}

    observed_min = _parse_rule_date(date_info.get("min"))
    observed_max = _parse_rule_date(date_info.get("max"))
    if observed_min is pd.NaT or observed_max is pd.NaT:
        return {"status": "warn", "observed": None, "expected": None, "details": f"unable to parse observed date values in {column}"}

    passed = observed_min >= expected_min and observed_max <= expected_max
    return {
        "status": "pass" if passed else "fail",
        "observed": {"min": _coerce_check_value(observed_min), "max": _coerce_check_value(observed_max)},
        "expected": {"min": _coerce_check_value(expected_min), "max": _coerce_check_value(expected_max)},
        "details": f"[{observed_min.date()}, {observed_max.date()}] in expected range",
    }


def _check_numeric_range(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    file_name = rule.get("file")
    column = rule.get("column")
    expected_min = rule.get("min")
    expected_max = rule.get("max")

    if file_profile is None or not file_profile.get("is_csv", False):
        return {"status": "fail", "observed": None, "expected": {"min": expected_min, "max": expected_max}, "details": "file missing or non-CSV"}

    df = dataframes.get(file_name or "")
    if df is None or column not in df.columns:
        return {"status": "fail", "observed": None, "expected": None, "details": f"column {column} missing"}

    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return {"status": "fail", "observed": None, "expected": {"min": expected_min, "max": expected_max}, "details": f"no numeric values in {column}"}

    observed_min = float(series.min())
    observed_max = float(series.max())
    passed = True
    if expected_min is not None and observed_min < float(expected_min):
        passed = False
    if expected_max is not None and observed_max > float(expected_max):
        passed = False

    return {
        "status": "pass" if passed else "fail",
        "observed": {"min": observed_min, "max": observed_max},
        "expected": {"min": expected_min, "max": expected_max},
        "details": f"{column} min/max observed",
    }


def _check_min_non_null_ratio(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    file_name = rule.get("file")
    column = rule.get("column")
    min_ratio = float(rule.get("min_ratio", 0.0))

    if file_profile is None or not file_profile.get("is_csv", False):
        return {"status": "fail", "observed": None, "expected": min_ratio, "details": "file missing or non-CSV"}

    df = dataframes.get(file_name or "")
    if df is None or column not in df.columns:
        return {"status": "fail", "observed": None, "expected": min_ratio, "details": f"column {column} missing"}

    total = len(df)
    if total == 0:
        return {"status": "warn", "observed": 0.0, "expected": min_ratio, "details": "empty table"}

    non_null_ratio = 1.0 - (df[column].isna().sum() / float(total))
    return {
        "status": "pass" if non_null_ratio >= min_ratio else "fail",
        "observed": round(non_null_ratio, 6),
        "expected": min_ratio,
        "details": f"{column} non-null ratio",
    }


def _check_foreign_key_reference(
    rule: Dict[str, Any],
    file_profile: Optional[Dict[str, Any]],
    dataframes: Dict[str, pd.DataFrame],
) -> Dict[str, Any]:
    source_file = rule.get("source_file")
    target_file = rule.get("target_file")
    source_column = rule.get("source_column")
    target_column = rule.get("target_column")
    min_match_ratio = float(rule.get("min_match_ratio", 1.0))
    ignore_nulls = bool(rule.get("ignore_nulls", True))

    source_df = dataframes.get(source_file)
    target_df = dataframes.get(target_file)
    if source_df is None:
        return {"status": "fail", "observed": None, "expected": min_match_ratio, "details": f"source file missing: {source_file}"}
    if target_df is None:
        return {"status": "fail", "observed": None, "expected": min_match_ratio, "details": f"target file missing: {target_file}"}

    if source_column not in source_df.columns:
        return {"status": "fail", "observed": None, "expected": min_match_ratio, "details": f"missing source column: {source_column}"}
    if target_column not in target_df.columns:
        return {"status": "fail", "observed": None, "expected": min_match_ratio, "details": f"missing target column: {target_column}"}

    source_values = set(source_df[source_column].dropna().astype(str).tolist())
    target_values = target_df[target_column].astype(str)
    if ignore_nulls:
        target_values = target_values[target_df[target_column].notna()]

    if target_values.empty:
        return {
            "status": "warn",
            "observed": 1.0,
            "expected": min_match_ratio,
            "details": "no target keys to validate",
        }

    matches = target_values.astype(str).isin(source_values)
    match_ratio = float(matches.mean()) if len(matches) else 1.0
    return {
        "status": "pass" if match_ratio >= min_match_ratio else "fail",
        "observed": round(match_ratio, 6),
        "expected": min_match_ratio,
        "details": f"matched {int(matches.sum())}/{len(matches)} target references",
    }


CHECK_HANDLERS = {
    "exists": _check_exists,
    "row_count_between": _check_row_count,
    "required_columns": _check_required_columns,
    "required_values": _check_required_values,
    "date_range": _check_date_range,
    "numeric_range": _check_numeric_range,
    "min_non_null_ratio": _check_min_non_null_ratio,
    "foreign_key_reference": _check_foreign_key_reference,
}


def _evaluate_check(rule: Dict[str, Any], profiles: Dict[str, Dict[str, Any]], dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    file_name = rule.get("file")
    check_type = rule.get("type")
    file_profile = profiles.get(file_name)

    handler = CHECK_HANDLERS.get(check_type)
    if not handler:
        return {
            "id": rule.get("id", ""),
            "title": rule.get("title", "Unknown check"),
            "file": file_name,
            "status": "warn",
            "expected": None,
            "observed": None,
            "details": f"unsupported check type: {check_type}",
        }

    result = handler(rule, file_profile, dataframes)
    return {
        "id": rule.get("id", ""),
        "title": rule.get("title", ""),
        "file": file_name,
        "status": result["status"],
        "expected": _safe_json_value(result.get("expected")),
        "observed": _safe_json_value(result.get("observed")),
        "details": result.get("details", ""),
    }


def evaluate_rules(profiles: Dict[str, Dict[str, Any]], dataframes: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    rules_payload = _load_rules()
    file_rules = rules_payload.get("files", []) or []
    cross_checks = rules_payload.get("cross_file_checks", []) or []

    results: List[Dict[str, Any]] = []

    for file_rule in file_rules:
        file_name = file_rule.get("file")
        for check in file_rule.get("checks", []):
            check = dict(check)
            check["file"] = file_name
            results.append(_evaluate_check(check, profiles, dataframes))

    for check in cross_checks:
        results.append(_evaluate_check(check, profiles, dataframes))

    return results


def build_overview() -> Dict[str, Any]:
    profiles, dataframes = scan_raw_directory()
    checks = evaluate_rules(profiles, dataframes)

    csv_profiles = [
        p for p in profiles.values() if p.get("is_csv", False)
    ]

    summary = {
        "total_files": len(profiles),
        "csv_files": len(csv_profiles),
        "total_rows": int(sum((p.get("rows", 0) or 0) for p in csv_profiles)),
        "total_size_bytes": int(sum((p.get("file_size_bytes", 0) or 0) for p in profiles.values())),
        "passing_checks": len([c for c in checks if c["status"] == "pass"]),
        "warn_checks": len([c for c in checks if c["status"] == "warn"]),
        "failing_checks": len([c for c in checks if c["status"] == "fail"]),
        "scanned_at": datetime.utcnow().isoformat(),
    }

    return {
        "summary": summary,
        "files": sorted(
            _safe_json_value(list(profiles.values())),
            key=lambda item: (item.get("file_name") or ""),
        ),
        "checks": sorted(
            _safe_json_value(checks),
            key=lambda item: f"{item.get('file') or ''}{item.get('id', '')}",
        ),
    }


def load_preview(file_name: str, rows: int = 20) -> Dict[str, Any]:
    path = resolve_raw_path(file_name)
    if not path.exists():
        raise ProfileError(f"file does not exist: {file_name}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        preview = df.head(rows).to_dict(orient="records")
        return {
            "file_name": str(path.relative_to(RAW_DATA_DIR)),
            "rows": int(len(df)),
            "columns": list(df.columns),
            "preview_rows": _safe_json_value(preview),
        }

    with path.open("r", encoding="utf-8") as f:
        text = f.read()
    return {
        "file_name": str(path.relative_to(RAW_DATA_DIR)),
        "rows": len(text.splitlines()),
        "columns": ["text"],
        "preview_rows": [_safe_json_value(text[:1024])],
    }
