"""
Validators and MMM data aggregator for synthetic data generation.

Runs 10 validation checks across all generated files, then produces
3 MMM-ready aggregated datasets in data/mmm/.

Usage:
    .venv/bin/python -m data.generators.validators
"""

import os
import sys
import datetime
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from data.generators.config import (
    RAW_DIR, CONTRACTS_DIR, MMM_DIR,
    START_DATE, END_DATE, DATE_FORMAT,
    UK_TOTAL_ANNUAL_BUDGET, CHANNEL_BUDGETS_GBP,
    MARKETS, ALL_CHANNELS, DIGITAL_CHANNELS, TRADITIONAL_CHANNELS,
    SEASONAL_MULTIPLIERS, UK_DEALERS, UK_DEALER_DF,
    STAGE_CONVERSION_RATES, ADSTOCK_DECAY_RATES,
    apply_adstock,
)


# ---------------------------------------------------------------------------
# Expected file manifest
# ---------------------------------------------------------------------------
EXPECTED_CSVS = {
    # Digital media (Task #3)
    "meta_ads.csv":           (4_000, 12_000),
    "google_ads.csv":         (3_000, 10_000),
    "dv360.csv":              (2_000, 7_000),
    "tiktok_ads.csv":         (1_500, 5_000),
    "youtube_ads.csv":        (2_000, 7_000),
    "linkedin_ads.csv":       (800, 3_000),
    # Traditional media (Task #4)
    "tv_performance.csv":     (100, 600),
    "ooh_performance.csv":    (50, 300),
    "print_performance.csv":  (40, 200),
    "radio_performance.csv":  (20, 120),
    # External data (Task #5)
    "competitor_spend.csv":   (100, 600),
    "economic_indicators.csv": (12, 60),
    "events.csv":             (8, 30),
    "sla_tracking.csv":       (20, 100),
    # Sales pipeline (Task #6)
    "vehicle_sales.csv":      (2_000, 8_000),
    "website_analytics.csv":  (2_500, 8_000),
    "configurator_sessions.csv": (5_000, 20_000),
    "leads.csv":              (4_000, 16_000),
    "test_drives.csv":        (3_000, 13_000),
}

EXPECTED_CONTRACTS = [
    "ITV_Airtime_Agreement.md",
    "Sky_Airtime_Agreement.md",
    "Sky_BVOD_Addendum.md",
    "JCDecaux_OOH_Contract.md",
    "ClearChannel_DOOH_Agreement.md",
    "Channel4_Media_Partnership.md",
    "MediaAgency_Terms_of_Business.md",
]

# Spend columns per file (file_name -> spend_column)
SPEND_COLUMNS = {
    "meta_ads.csv": "spend",
    "google_ads.csv": "spend",
    "dv360.csv": "spend",
    "tiktok_ads.csv": "spend",
    "youtube_ads.csv": "spend",
    "linkedin_ads.csv": "spend",
    "tv_performance.csv": "spend",
    "ooh_performance.csv": "spend",
    "print_performance.csv": "spend",
    "radio_performance.csv": "spend",
}

# Channel mapping from file to config channel key
FILE_TO_CHANNEL = {
    "meta_ads.csv": "meta",
    "google_ads.csv": "google",
    "dv360.csv": "dv360",
    "tiktok_ads.csv": "tiktok",
    "youtube_ads.csv": "youtube",
    "linkedin_ads.csv": "linkedin",
    "tv_performance.csv": "tv",
    "ooh_performance.csv": "ooh",
    "print_performance.csv": "print",
    "radio_performance.csv": "radio",
}

# Date columns per file
DATE_COLUMNS = {
    "meta_ads.csv": "date",
    "google_ads.csv": "date",
    "dv360.csv": "date",
    "tiktok_ads.csv": "date",
    "youtube_ads.csv": "date",
    "linkedin_ads.csv": "date",
    "tv_performance.csv": "date_week_start",
    "ooh_performance.csv": "start_date",
    "print_performance.csv": "date",
    "radio_performance.csv": "start_date",
    "competitor_spend.csv": "year_month",
    "economic_indicators.csv": "year_month",
    "events.csv": "start_date",
    "sla_tracking.csv": "year_month",
    "vehicle_sales.csv": "date",
    "website_analytics.csv": "date",
    "configurator_sessions.csv": "date",
    "leads.csv": "created_date",
    "test_drives.csv": "booking_date",
}


# ===========================================================================
# Validation helpers
# ===========================================================================

def _load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV from data/raw/."""
    path = os.path.join(RAW_DIR, filename)
    return pd.read_csv(path)


def _parse_dates(series: pd.Series) -> pd.Series:
    """Parse dates from various formats (YYYY-MM-DD or YYYY-MM)."""
    sample = str(series.iloc[0])
    if len(sample) == 7:  # YYYY-MM format
        return pd.to_datetime(series, format="%Y-%m")
    return pd.to_datetime(series)


# ===========================================================================
# 10 VALIDATION CHECKS
# ===========================================================================

def check_file_existence() -> Tuple[bool, List[str]]:
    """Check 1: All 19 CSVs and 7 contracts exist."""
    issues = []
    for csv_name in EXPECTED_CSVS:
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            issues.append(f"  MISSING CSV: {csv_name}")
    for contract in EXPECTED_CONTRACTS:
        path = os.path.join(CONTRACTS_DIR, contract)
        if not os.path.isfile(path):
            issues.append(f"  MISSING CONTRACT: {contract}")
    return len(issues) == 0, issues


def check_row_counts() -> Tuple[bool, List[str]]:
    """Check 2: Row counts within expected ranges (+-20%)."""
    issues = []
    for csv_name, (min_rows, max_rows) in EXPECTED_CSVS.items():
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)
        actual = len(df)
        if actual < min_rows or actual > max_rows:
            issues.append(
                f"  {csv_name}: {actual:,} rows (expected {min_rows:,}-{max_rows:,})"
            )
    return len(issues) == 0, issues


def check_budget_totals() -> Tuple[bool, List[str]]:
    """Check 3: Budget totals ~ GBP20M (+/-5%)."""
    issues = []
    total_spend = 0.0
    channel_spends = {}

    for csv_name, spend_col in SPEND_COLUMNS.items():
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)

        # Try common spend column names
        actual_col = None
        for candidate in [spend_col, "spend_gbp", "negotiated_cost"]:
            if candidate in df.columns:
                actual_col = candidate
                break
        if actual_col is None:
            # Look for any column with 'spend' in name
            spend_cols = [c for c in df.columns if "spend" in c.lower()]
            if spend_cols:
                actual_col = spend_cols[0]

        if actual_col is None:
            issues.append(f"  {csv_name}: no spend column found")
            continue

        file_spend = df[actual_col].sum()
        channel = FILE_TO_CHANNEL.get(csv_name, csv_name)
        channel_spends[channel] = file_spend
        total_spend += file_spend

    # Also add events spend if available
    events_path = os.path.join(RAW_DIR, "events.csv")
    if os.path.isfile(events_path):
        events_df = _load_csv("events.csv")
        if "spend" in events_df.columns:
            events_spend = events_df["spend"].sum()
            channel_spends["events"] = events_spend
            total_spend += events_spend

    expected = UK_TOTAL_ANNUAL_BUDGET
    tolerance = 0.05
    deviation = abs(total_spend - expected) / expected if expected > 0 else 0

    if deviation > tolerance:
        issues.append(
            f"  Total spend: GBP{total_spend:,.0f} vs expected GBP{expected:,.0f} "
            f"(deviation: {deviation:.1%}, tolerance: {tolerance:.0%})"
        )

    # Per-channel check (wider tolerance)
    for channel, actual_spend in channel_spends.items():
        expected_ch = CHANNEL_BUDGETS_GBP.get(channel, 0)
        if expected_ch > 0:
            ch_dev = abs(actual_spend - expected_ch) / expected_ch
            if ch_dev > 0.15:  # 15% channel tolerance
                issues.append(
                    f"  Channel {channel}: GBP{actual_spend:,.0f} vs expected GBP{expected_ch:,.0f} "
                    f"(deviation: {ch_dev:.1%})"
                )

    return len(issues) == 0, issues


def check_sales_totals() -> Tuple[bool, List[str]]:
    """Check 4: Sales totals by market."""
    issues = []
    path = os.path.join(RAW_DIR, "vehicle_sales.csv")
    if not os.path.isfile(path):
        issues.append("  vehicle_sales.csv not found")
        return False, issues

    df = _load_csv("vehicle_sales.csv")

    # Find market column
    market_col = None
    for candidate in ["market", "market_code", "country"]:
        if candidate in df.columns:
            market_col = candidate
            break

    if market_col is None:
        issues.append("  No market column found in vehicle_sales.csv")
        return False, issues

    market_counts = df[market_col].value_counts()
    expected_totals = {"GB": 2800, "DE": 1200, "FR": 600}

    for market, expected in expected_totals.items():
        actual = market_counts.get(market, 0)
        tolerance = 0.10
        if expected > 0:
            dev = abs(actual - expected) / expected
            if dev > tolerance:
                issues.append(
                    f"  Market {market}: {actual:,} units vs expected ~{expected:,} "
                    f"(deviation: {dev:.1%})"
                )

    return len(issues) == 0, issues


def check_date_ranges() -> Tuple[bool, List[str]]:
    """Check 5: Date ranges cover 2025."""
    issues = []
    for csv_name, date_col in DATE_COLUMNS.items():
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)
        if date_col not in df.columns:
            # Try common alternatives
            alternatives = ["date", "start_date", "date_week_start", "year_month"]
            found = False
            for alt in alternatives:
                if alt in df.columns:
                    date_col = alt
                    found = True
                    break
            if not found:
                issues.append(f"  {csv_name}: date column '{date_col}' not found")
                continue

        try:
            dates = _parse_dates(df[date_col])
            min_year = dates.dt.year.min()
            max_year = dates.dt.year.max()
            if min_year != 2025 or max_year != 2025:
                issues.append(
                    f"  {csv_name}: year range {min_year}-{max_year} (expected 2025)"
                )
        except Exception as e:
            issues.append(f"  {csv_name}: date parse error: {e}")

    return len(issues) == 0, issues


def check_foreign_keys() -> Tuple[bool, List[str]]:
    """Check 6: No orphaned foreign keys."""
    issues = []

    valid_dealer_ids = set(d["dealer_id"] for d in UK_DEALERS)

    # Check dealer_ids in sales/test_drives/leads
    for csv_name in ["vehicle_sales.csv", "test_drives.csv", "leads.csv"]:
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)
        if "dealer_id" in df.columns:
            file_dealer_ids = set(df["dealer_id"].dropna().unique())
            orphaned = file_dealer_ids - valid_dealer_ids
            if orphaned:
                issues.append(
                    f"  {csv_name}: {len(orphaned)} orphaned dealer_ids: "
                    f"{list(orphaned)[:5]}..."
                )

    # Check lead_id in test_drives exists in leads
    leads_path = os.path.join(RAW_DIR, "leads.csv")
    td_path = os.path.join(RAW_DIR, "test_drives.csv")
    if os.path.isfile(leads_path) and os.path.isfile(td_path):
        leads_df = _load_csv("leads.csv")
        td_df = _load_csv("test_drives.csv")
        if "lead_id" in leads_df.columns and "lead_id" in td_df.columns:
            valid_lead_ids = set(leads_df["lead_id"].unique())
            td_lead_ids = set(td_df["lead_id"].dropna().unique())
            orphaned_leads = td_lead_ids - valid_lead_ids
            if orphaned_leads:
                issues.append(
                    f"  test_drives.csv: {len(orphaned_leads)} orphaned lead_ids "
                    f"(sample: {list(orphaned_leads)[:5]})"
                )

    return len(issues) == 0, issues


def check_conversion_funnel() -> Tuple[bool, List[str]]:
    """Check 7: Conversion funnel logic (each stage <= previous stage)."""
    issues = []

    # Check leads pipeline if stage column exists
    path = os.path.join(RAW_DIR, "leads.csv")
    if os.path.isfile(path):
        df = _load_csv("leads.csv")
        if "stage" in df.columns:
            stage_counts = df["stage"].value_counts()
            stages_ordered = [
                s for s in STAGE_CONVERSION_RATES.keys()
                if s in stage_counts.index
            ]
            prev_count = None
            for stage in stages_ordered:
                count = stage_counts.get(stage, 0)
                if prev_count is not None and count > prev_count * 1.1:
                    issues.append(
                        f"  Funnel violation: {stage} ({count:,}) > previous stage ({prev_count:,})"
                    )
                prev_count = count

    # Check configurator completion rate
    config_path = os.path.join(RAW_DIR, "configurator_sessions.csv")
    if os.path.isfile(config_path):
        df = _load_csv("configurator_sessions.csv")
        if "completed" in df.columns:
            total = len(df)
            completed = df["completed"].sum()
            rate = completed / total if total > 0 else 0
            if rate < 0.15 or rate > 0.60:
                issues.append(
                    f"  Configurator completion rate: {rate:.1%} (expected 30-40%)"
                )

    # Check test drive completion
    td_path = os.path.join(RAW_DIR, "test_drives.csv")
    if os.path.isfile(td_path):
        df = _load_csv("test_drives.csv")
        # Try both "status" and "outcome" column names
        status_col = "outcome" if "outcome" in df.columns else "status"
        if status_col in df.columns:
            total = len(df)
            completed = (df[status_col] == "completed").sum()
            rate = completed / total if total > 0 else 0
            if rate < 0.40 or rate > 0.90:
                issues.append(
                    f"  Test drive completion rate: {rate:.1%} (expected ~68%)"
                )

    return len(issues) == 0, issues


def check_seasonal_patterns() -> Tuple[bool, List[str]]:
    """Check 8: Seasonal patterns are present (Sep peak)."""
    issues = []

    # Check that media spend peaks in Sep-Oct
    for csv_name in ["meta_ads.csv", "tv_performance.csv"]:
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)

        date_col = DATE_COLUMNS.get(csv_name, "date")
        if date_col not in df.columns:
            continue

        spend_col = SPEND_COLUMNS.get(csv_name, "spend")
        if spend_col not in df.columns:
            # Try alternatives
            for alt in ["spend_gbp", "spend"]:
                if alt in df.columns:
                    spend_col = alt
                    break
            else:
                continue

        dates = _parse_dates(df[date_col])
        df = df.copy()
        df["_month"] = dates.dt.month

        monthly_spend = df.groupby("_month")[spend_col].sum()
        if len(monthly_spend) < 6:
            continue

        # Sep (month 9) should be among top 3 months
        top_months = monthly_spend.nlargest(3).index.tolist()
        if 9 not in top_months and 10 not in top_months:
            issues.append(
                f"  {csv_name}: Sep/Oct not in top 3 spend months "
                f"(top: {top_months})"
            )

    # Check sales seasonality
    sales_path = os.path.join(RAW_DIR, "vehicle_sales.csv")
    if os.path.isfile(sales_path):
        df = _load_csv("vehicle_sales.csv")
        if "date" in df.columns:
            dates = pd.to_datetime(df["date"])
            df = df.copy()
            df["_month"] = dates.dt.month
            monthly_sales = df.groupby("_month").size()
            if len(monthly_sales) > 0:
                top_months = monthly_sales.nlargest(3).index.tolist()
                if 9 not in top_months and 10 not in top_months:
                    issues.append(
                        f"  vehicle_sales.csv: Sep/Oct not in top 3 sales months "
                        f"(top: {top_months})"
                    )

    return len(issues) == 0, issues


def check_no_negative_values() -> Tuple[bool, List[str]]:
    """Check 9: No negative values in spend/impression/click columns."""
    issues = []
    non_negative_cols = [
        "spend", "spend_gbp", "negotiated_cost", "impressions",
        "clicks", "views", "leads", "reach", "reach_000",
        "video_views", "conversions", "grps", "spots_aired",
    ]

    for csv_name in EXPECTED_CSVS:
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)
        for col in non_negative_cols:
            if col in df.columns:
                neg_count = (df[col] < 0).sum()
                if neg_count > 0:
                    issues.append(
                        f"  {csv_name}.{col}: {neg_count} negative values"
                    )

    return len(issues) == 0, issues


def check_ctr_consistency() -> Tuple[bool, List[str]]:
    """Check 10: CTR = clicks / impressions (within tolerance)."""
    issues = []
    digital_files = [
        "meta_ads.csv", "google_ads.csv", "dv360.csv",
        "tiktok_ads.csv", "youtube_ads.csv", "linkedin_ads.csv",
    ]

    for csv_name in digital_files:
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = _load_csv(csv_name)
        if "clicks" not in df.columns or "impressions" not in df.columns:
            continue
        if "ctr" not in df.columns:
            continue

        # Only check rows with non-zero impressions
        mask = df["impressions"] > 0
        if mask.sum() == 0:
            continue

        calculated_ctr = df.loc[mask, "clicks"] / df.loc[mask, "impressions"]
        reported_ctr = df.loc[mask, "ctr"]

        # Check if CTR is reported as percentage or decimal
        if reported_ctr.mean() > 1:
            # Likely percentage, convert
            reported_ctr = reported_ctr / 100.0

        # Allow 1% absolute difference
        diff = (calculated_ctr - reported_ctr).abs()
        bad_rows = (diff > 0.01).sum()
        total = mask.sum()
        bad_pct = bad_rows / total if total > 0 else 0

        if bad_pct > 0.05:  # More than 5% of rows have CTR mismatch
            issues.append(
                f"  {csv_name}: {bad_rows:,}/{total:,} rows ({bad_pct:.1%}) "
                f"have CTR mismatch > 1%"
            )

    return len(issues) == 0, issues


# ===========================================================================
# VALIDATE ALL
# ===========================================================================

def validate_all() -> Dict[str, Tuple[bool, List[str]]]:
    """Run all 10 validation checks and return results."""
    checks = {
        "1. File existence":        check_file_existence,
        "2. Row counts":            check_row_counts,
        "3. Budget totals (~GBP20M)": check_budget_totals,
        "4. Sales totals by market": check_sales_totals,
        "5. Date ranges (2025)":    check_date_ranges,
        "6. Foreign keys":          check_foreign_keys,
        "7. Conversion funnel":     check_conversion_funnel,
        "8. Seasonal patterns":     check_seasonal_patterns,
        "9. No negative values":    check_no_negative_values,
        "10. CTR consistency":      check_ctr_consistency,
    }

    results = {}
    for name, func in checks.items():
        try:
            passed, issues = func()
            results[name] = (passed, issues)
        except Exception as e:
            results[name] = (False, [f"  ERROR: {e}"])

    return results


# ===========================================================================
# MMM AGGREGATION
# ===========================================================================

def _get_weekly_dates() -> pd.DatetimeIndex:
    """Generate 52 weekly start dates for 2025 (ISO weeks)."""
    weeks = pd.date_range(
        start="2025-01-06",  # First Monday of 2025
        periods=52,
        freq="W-MON",
    )
    return weeks


def _aggregate_digital_spend_weekly(weeks: pd.DatetimeIndex) -> pd.DataFrame:
    """Aggregate digital channel spend to weekly level."""
    result = pd.DataFrame({"week_start": weeks})

    for csv_name, channel in FILE_TO_CHANNEL.items():
        if channel not in DIGITAL_CHANNELS:
            continue
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            result[f"spend_{channel}"] = 0.0
            continue

        df = _load_csv(csv_name)
        date_col = DATE_COLUMNS.get(csv_name, "date")
        if date_col not in df.columns:
            result[f"spend_{channel}"] = 0.0
            continue

        spend_col = SPEND_COLUMNS.get(csv_name, "spend")
        if spend_col not in df.columns:
            for alt in ["spend_gbp", "spend"]:
                if alt in df.columns:
                    spend_col = alt
                    break
            else:
                result[f"spend_{channel}"] = 0.0
                continue

        df["_date"] = pd.to_datetime(df[date_col])
        daily = df.groupby("_date")[spend_col].sum().reset_index()
        daily.columns = ["date", "spend"]
        daily = daily.set_index("date").sort_index()

        weekly_spend = []
        for ws in weeks:
            we = ws + pd.Timedelta(days=6)
            mask = (daily.index >= ws) & (daily.index <= we)
            weekly_spend.append(daily.loc[mask, "spend"].sum())

        result[f"spend_{channel}"] = weekly_spend

    return result


def _aggregate_traditional_spend_weekly(weeks: pd.DatetimeIndex) -> pd.DataFrame:
    """Aggregate traditional channel spend to weekly level."""
    result = pd.DataFrame({"week_start": weeks})

    # TV: already weekly
    tv_path = os.path.join(RAW_DIR, "tv_performance.csv")
    if os.path.isfile(tv_path):
        df = _load_csv("tv_performance.csv")
        date_col = "date_week_start"
        if date_col not in df.columns:
            for alt in ["date", "date_week_start"]:
                if alt in df.columns:
                    date_col = alt
                    break
        if date_col in df.columns and "spend" in df.columns:
            df["_date"] = pd.to_datetime(df[date_col])
            weekly = df.groupby("_date")["spend"].sum().reset_index()
            weekly.columns = ["date", "spend"]
            weekly = weekly.set_index("date")
            tv_spend = []
            for ws in weeks:
                # Match to nearest week
                mask = (weekly.index >= ws - pd.Timedelta(days=3)) & \
                       (weekly.index <= ws + pd.Timedelta(days=3))
                tv_spend.append(weekly.loc[mask, "spend"].sum())
            result["spend_tv"] = tv_spend
        else:
            result["spend_tv"] = 0.0
    else:
        result["spend_tv"] = 0.0

    # OOH: campaign periods -> distribute across weeks
    ooh_path = os.path.join(RAW_DIR, "ooh_performance.csv")
    if os.path.isfile(ooh_path):
        df = _load_csv("ooh_performance.csv")
        ooh_weekly = np.zeros(52)
        if "start_date" in df.columns and "end_date" in df.columns and "spend" in df.columns:
            for _, row in df.iterrows():
                sd = pd.to_datetime(row["start_date"])
                ed = pd.to_datetime(row["end_date"])
                days = max((ed - sd).days, 1)
                daily_spend = row["spend"] / days
                for i, ws in enumerate(weeks):
                    we = ws + pd.Timedelta(days=6)
                    overlap_start = max(sd, ws)
                    overlap_end = min(ed, we)
                    overlap_days = max((overlap_end - overlap_start).days + 1, 0)
                    ooh_weekly[i] += daily_spend * overlap_days
        result["spend_ooh"] = ooh_weekly
    else:
        result["spend_ooh"] = 0.0

    # Print: per-insertion -> assign to week
    print_path = os.path.join(RAW_DIR, "print_performance.csv")
    if os.path.isfile(print_path):
        df = _load_csv("print_performance.csv")
        spend_col = "spend" if "spend" in df.columns else "negotiated_cost"
        if spend_col in df.columns and "date" in df.columns:
            df["_date"] = pd.to_datetime(df["date"])
            print_weekly = np.zeros(52)
            for _, row in df.iterrows():
                d = row["_date"]
                for i, ws in enumerate(weeks):
                    we = ws + pd.Timedelta(days=6)
                    if ws <= d <= we:
                        print_weekly[i] += row[spend_col]
                        break
            result["spend_print"] = print_weekly
        else:
            result["spend_print"] = 0.0
    else:
        result["spend_print"] = 0.0

    # Radio: per-flight -> distribute across weeks
    radio_path = os.path.join(RAW_DIR, "radio_performance.csv")
    if os.path.isfile(radio_path):
        df = _load_csv("radio_performance.csv")
        radio_weekly = np.zeros(52)
        if "start_date" in df.columns and "end_date" in df.columns and "spend" in df.columns:
            for _, row in df.iterrows():
                sd = pd.to_datetime(row["start_date"])
                ed = pd.to_datetime(row["end_date"])
                days = max((ed - sd).days, 1)
                daily_spend = row["spend"] / days
                for i, ws in enumerate(weeks):
                    we = ws + pd.Timedelta(days=6)
                    overlap_start = max(sd, ws)
                    overlap_end = min(ed, we)
                    overlap_days = max((overlap_end - overlap_start).days + 1, 0)
                    radio_weekly[i] += daily_spend * overlap_days
        result["spend_radio"] = radio_weekly
    else:
        result["spend_radio"] = 0.0

    return result


def _aggregate_events_spend_weekly(weeks: pd.DatetimeIndex) -> pd.Series:
    """Aggregate events spend to weekly."""
    events_weekly = np.zeros(52)
    path = os.path.join(RAW_DIR, "events.csv")
    if os.path.isfile(path):
        df = _load_csv("events.csv")
        if "start_date" in df.columns and "spend" in df.columns:
            for _, row in df.iterrows():
                sd = pd.to_datetime(row["start_date"])
                end_col = "end_date" if "end_date" in df.columns else None
                if end_col and pd.notna(row.get(end_col)):
                    ed = pd.to_datetime(row[end_col])
                else:
                    ed = sd + pd.Timedelta(days=1)
                days = max((ed - sd).days, 1)
                daily_spend = row["spend"] / days
                for i, ws in enumerate(weeks):
                    we = ws + pd.Timedelta(days=6)
                    overlap_start = max(sd, ws)
                    overlap_end = min(ed, we)
                    overlap_days = max((overlap_end - overlap_start).days + 1, 0)
                    events_weekly[i] += daily_spend * overlap_days
    return pd.Series(events_weekly, name="spend_events")


def aggregate_mmm_data() -> Dict[str, str]:
    """
    Aggregate all generated data into 3 MMM-ready files in data/mmm/.

    Returns dict of {filename: filepath} for created files.
    """
    os.makedirs(MMM_DIR, exist_ok=True)
    weeks = _get_weekly_dates()
    created_files = {}

    # ----- 1. weekly_channel_spend.csv -----
    digital = _aggregate_digital_spend_weekly(weeks)
    traditional = _aggregate_traditional_spend_weekly(weeks)
    events_spend = _aggregate_events_spend_weekly(weeks)

    spend_df = digital.copy()
    for col in traditional.columns:
        if col != "week_start":
            spend_df[col] = traditional[col].values
    spend_df["spend_events"] = events_spend.values

    # Add total
    spend_cols = [c for c in spend_df.columns if c.startswith("spend_")]
    spend_df["spend_total"] = spend_df[spend_cols].sum(axis=1)

    path = os.path.join(MMM_DIR, "weekly_channel_spend.csv")
    spend_df.to_csv(path, index=False)
    created_files["weekly_channel_spend.csv"] = path

    # ----- 2. weekly_sales.csv -----
    sales_df = pd.DataFrame({"week_start": weeks})

    # Sales units
    vs_path = os.path.join(RAW_DIR, "vehicle_sales.csv")
    if os.path.isfile(vs_path):
        vs = _load_csv("vehicle_sales.csv")
        if "date" in vs.columns:
            vs["_date"] = pd.to_datetime(vs["date"])
            market_col = None
            for cand in ["market", "market_code", "country"]:
                if cand in vs.columns:
                    market_col = cand
                    break

            # Total units per week
            units_weekly = []
            for ws in weeks:
                we = ws + pd.Timedelta(days=6)
                mask = (vs["_date"] >= ws) & (vs["_date"] <= we)
                units_weekly.append(mask.sum())
            sales_df["units_sold"] = units_weekly

            # Revenue if price column exists
            price_col = None
            for cand in ["price_gbp", "price", "revenue", "transaction_price"]:
                if cand in vs.columns:
                    price_col = cand
                    break
            if price_col:
                rev_weekly = []
                for ws in weeks:
                    we = ws + pd.Timedelta(days=6)
                    mask = (vs["_date"] >= ws) & (vs["_date"] <= we)
                    rev_weekly.append(vs.loc[mask, price_col].sum())
                sales_df["revenue"] = rev_weekly

            # Per-market units
            if market_col:
                for mkt in ["GB", "DE", "FR"]:
                    mkt_units = []
                    for ws in weeks:
                        we = ws + pd.Timedelta(days=6)
                        mask = (vs["_date"] >= ws) & (vs["_date"] <= we) & (vs[market_col] == mkt)
                        mkt_units.append(mask.sum())
                    sales_df[f"units_{mkt.lower()}"] = mkt_units

    # Test drives
    td_path = os.path.join(RAW_DIR, "test_drives.csv")
    if os.path.isfile(td_path):
        td = _load_csv("test_drives.csv")
        td_date_col = "booking_date" if "booking_date" in td.columns else "date"
        if td_date_col in td.columns:
            td["_date"] = pd.to_datetime(td[td_date_col])
            td_weekly = []
            for ws in weeks:
                we = ws + pd.Timedelta(days=6)
                mask = (td["_date"] >= ws) & (td["_date"] <= we)
                td_weekly.append(mask.sum())
            sales_df["test_drives"] = td_weekly

    # Leads
    leads_path = os.path.join(RAW_DIR, "leads.csv")
    if os.path.isfile(leads_path):
        leads = _load_csv("leads.csv")
        leads_date_col = "created_date" if "created_date" in leads.columns else "date"
        if leads_date_col in leads.columns:
            leads["_date"] = pd.to_datetime(leads[leads_date_col])
            leads_weekly = []
            for ws in weeks:
                we = ws + pd.Timedelta(days=6)
                mask = (leads["_date"] >= ws) & (leads["_date"] <= we)
                leads_weekly.append(mask.sum())
            sales_df["leads"] = leads_weekly

    # Web sessions
    web_path = os.path.join(RAW_DIR, "website_analytics.csv")
    if os.path.isfile(web_path):
        web = _load_csv("website_analytics.csv")
        if "date" in web.columns:
            web["_date"] = pd.to_datetime(web["date"])
            session_col = None
            for cand in ["sessions", "visits", "pageviews", "users"]:
                if cand in web.columns:
                    session_col = cand
                    break
            if session_col:
                web_weekly = []
                for ws in weeks:
                    we = ws + pd.Timedelta(days=6)
                    mask = (web["_date"] >= ws) & (web["_date"] <= we)
                    web_weekly.append(web.loc[mask, session_col].sum())
                sales_df["web_sessions"] = web_weekly

    path = os.path.join(MMM_DIR, "weekly_sales.csv")
    sales_df.to_csv(path, index=False)
    created_files["weekly_sales.csv"] = path

    # ----- 3. model_ready.csv -----
    # Join spend + sales + adstock + external factors
    model_df = spend_df.copy()

    # Merge sales columns
    for col in sales_df.columns:
        if col != "week_start":
            model_df[col] = sales_df[col].values

    # Apply adstock transforms
    adstock_rates = {
        "spend_tv": 0.85,
        "spend_ooh": 0.70,
        "spend_print": 0.60,
        "spend_radio": 0.50,
    }
    # Digital channels all get 0.40
    for ch in DIGITAL_CHANNELS:
        adstock_rates[f"spend_{ch}"] = 0.40

    for col, decay in adstock_rates.items():
        if col in model_df.columns:
            model_df[f"adstock_{col.replace('spend_', '')}"] = apply_adstock(
                model_df[col], decay
            ).values

    # Add events adstock
    if "spend_events" in model_df.columns:
        model_df["adstock_events"] = apply_adstock(
            model_df["spend_events"], 0.80
        ).values

    # Add external factors (weekly)
    econ_path = os.path.join(RAW_DIR, "economic_indicators.csv")
    if os.path.isfile(econ_path):
        econ = _load_csv("economic_indicators.csv")
        if "year_month" in econ.columns:
            econ["_month"] = pd.to_datetime(econ["year_month"]).dt.month

            # Only use GB rows if country column exists
            if "country" in econ.columns:
                econ = econ[econ["country"].isin(["GB", "UK"])].copy()

            # Map monthly data to weeks
            model_df["_month"] = pd.to_datetime(model_df["week_start"]).dt.month

            for econ_col in ["consumer_confidence_index", "bank_rate_pct",
                             "bev_market_share_pct", "cpi_index"]:
                if econ_col in econ.columns:
                    month_map = dict(zip(econ["_month"], econ[econ_col]))
                    model_df[econ_col] = model_df["_month"].map(month_map)

            model_df.drop(columns=["_month"], inplace=True)

    # Add competitor spend (monthly -> weekly)
    comp_path = os.path.join(RAW_DIR, "competitor_spend.csv")
    if os.path.isfile(comp_path):
        comp = _load_csv("competitor_spend.csv")
        if "year_month" in comp.columns and "estimated_spend_gbp" in comp.columns:
            comp["_month"] = pd.to_datetime(comp["year_month"]).dt.month
            monthly_comp = comp.groupby("_month")["estimated_spend_gbp"].sum()
            model_df["_month"] = pd.to_datetime(model_df["week_start"]).dt.month
            # Weekly = monthly / ~4.33
            model_df["competitor_spend_weekly"] = (
                model_df["_month"].map(monthly_comp) / 4.33
            )
            model_df.drop(columns=["_month"], inplace=True)

    # Add seasonal index
    model_df["seasonal_index"] = pd.to_datetime(
        model_df["week_start"]
    ).dt.month.map(SEASONAL_MULTIPLIERS)

    path = os.path.join(MMM_DIR, "model_ready.csv")
    model_df.to_csv(path, index=False)
    created_files["model_ready.csv"] = path

    return created_files


# ===========================================================================
# SUMMARY REPORT
# ===========================================================================

def print_report(validation_results: Dict, mmm_files: Dict[str, str]) -> str:
    """Print comprehensive summary report. Returns report as string."""
    lines = []
    lines.append("=" * 70)
    lines.append("SYNTHETIC DATA VALIDATION & MMM AGGREGATION REPORT")
    lines.append("=" * 70)

    # --- Validation Results ---
    lines.append("\n--- VALIDATION RESULTS ---\n")
    total_checks = len(validation_results)
    passed_checks = sum(1 for v in validation_results.values() if v[0])
    failed_checks = total_checks - passed_checks

    for name, (passed, issues) in validation_results.items():
        status = "PASS" if passed else "FAIL"
        icon = "[+]" if passed else "[X]"
        lines.append(f"  {icon} {name}: {status}")
        if not passed:
            for issue in issues:
                lines.append(f"      {issue}")

    lines.append(f"\n  Summary: {passed_checks}/{total_checks} checks passed, "
                 f"{failed_checks} failed")

    # --- File inventory ---
    lines.append("\n--- FILE INVENTORY ---\n")
    for csv_name in sorted(EXPECTED_CSVS.keys()):
        path = os.path.join(RAW_DIR, csv_name)
        if os.path.isfile(path):
            df = pd.read_csv(path)
            size_kb = os.path.getsize(path) / 1024
            lines.append(f"  {csv_name:35s} {len(df):>8,} rows  {size_kb:>8.1f} KB")
        else:
            lines.append(f"  {csv_name:35s} MISSING")

    lines.append("")
    for contract in EXPECTED_CONTRACTS:
        path = os.path.join(CONTRACTS_DIR, contract)
        if os.path.isfile(path):
            size_kb = os.path.getsize(path) / 1024
            lines.append(f"  contracts/{contract:35s} {size_kb:>8.1f} KB")
        else:
            lines.append(f"  contracts/{contract:35s} MISSING")

    # --- Spend Summary ---
    lines.append("\n--- SPEND SUMMARY (GBP) ---\n")
    total_spend = 0.0
    for csv_name, spend_col in SPEND_COLUMNS.items():
        path = os.path.join(RAW_DIR, csv_name)
        if not os.path.isfile(path):
            continue
        df = pd.read_csv(path)
        actual_col = None
        for cand in [spend_col, "spend_gbp", "spend", "negotiated_cost"]:
            if cand in df.columns:
                actual_col = cand
                break
        if actual_col:
            channel_spend = df[actual_col].sum()
            channel = FILE_TO_CHANNEL.get(csv_name, csv_name)
            expected = CHANNEL_BUDGETS_GBP.get(channel, 0)
            dev = abs(channel_spend - expected) / expected * 100 if expected > 0 else 0
            lines.append(
                f"  {channel:12s}: GBP{channel_spend:>12,.0f}  "
                f"(expected GBP{expected:>12,}, dev {dev:>5.1f}%)"
            )
            total_spend += channel_spend

    lines.append(f"  {'TOTAL':12s}: GBP{total_spend:>12,.0f}  "
                 f"(expected GBP{UK_TOTAL_ANNUAL_BUDGET:>12,})")

    # --- Sales Summary ---
    lines.append("\n--- SALES SUMMARY ---\n")
    vs_path = os.path.join(RAW_DIR, "vehicle_sales.csv")
    if os.path.isfile(vs_path):
        df = pd.read_csv(vs_path)
        lines.append(f"  Total units: {len(df):,}")
        market_col = None
        for cand in ["market", "market_code", "country"]:
            if cand in df.columns:
                market_col = cand
                break
        if market_col:
            for mkt in ["GB", "DE", "FR"]:
                count = (df[market_col] == mkt).sum()
                lines.append(f"    {mkt}: {count:,} units")

        model_col = None
        for cand in ["model", "vehicle_model", "model_key"]:
            if cand in df.columns:
                model_col = cand
                break
        if model_col:
            lines.append("  By model:")
            for model, count in df[model_col].value_counts().items():
                lines.append(f"    {model}: {count:,} units")

    # --- MMM Aggregation ---
    lines.append("\n--- MMM AGGREGATED FILES ---\n")
    for filename, filepath in mmm_files.items():
        if os.path.isfile(filepath):
            df = pd.read_csv(filepath)
            size_kb = os.path.getsize(filepath) / 1024
            lines.append(f"  {filename}: {len(df)} rows, {len(df.columns)} columns, "
                         f"{size_kb:.1f} KB")
            lines.append(f"    Columns: {', '.join(df.columns[:10])}")
            if len(df.columns) > 10:
                lines.append(f"             ... and {len(df.columns) - 10} more")

    lines.append("\n" + "=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    report = "\n".join(lines)
    print(report)
    return report


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    print("Running validation checks...")
    validation_results = validate_all()

    print("Aggregating MMM data...")
    mmm_files = aggregate_mmm_data()

    report = print_report(validation_results, mmm_files)
