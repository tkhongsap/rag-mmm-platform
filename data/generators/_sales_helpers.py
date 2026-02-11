"""
Helper functions for sales pipeline generator.

Handles media spend loading, lead stage assignment, and small utilities.
"""

import datetime
import os

import numpy as np
import pandas as pd

from data.generators.config import (
    RANDOM_SEED, RAW_DIR, DATE_RANGE, START_DATE, END_DATE,
    DATE_FORMAT, VEHICLE_MODELS, FINANCE_TYPES, FINANCE_DISTRIBUTION,
)

# ---------------------------------------------------------------------------
# Lead pipeline constants
# ---------------------------------------------------------------------------
LEAD_STAGE_FLOW = [
    ("NEW", 1.00), ("CONTACTED", 0.85), ("QUALIFIED", 0.60),
    ("TD_BOOKED", 0.45), ("TD_COMPLETED", 0.35),
    ("NEGOTIATION", 0.20), ("WON", 0.12), ("LOST", None),
]

TD_OUTCOMES = {"completed": 0.68, "no_show": 0.22, "cancelled": 0.10}

# ---------------------------------------------------------------------------
# Media spend loading
# ---------------------------------------------------------------------------

def load_daily_digital_spend() -> pd.DataFrame:
    """Load and aggregate daily digital media spend from CSVs."""
    frames = []
    file_map = {
        "meta": "meta_ads.csv", "google": "google_ads.csv",
        "dv360": "dv360.csv", "tiktok": "tiktok_ads.csv",
        "youtube": "youtube_ads.csv", "linkedin": "linkedin_ads.csv",
    }
    for ch, fname in file_map.items():
        path = os.path.join(RAW_DIR, fname)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, usecols=["date", "spend"])
        daily = df.groupby("date")["spend"].sum().reset_index()
        daily["channel"] = ch
        frames.append(daily)
    if not frames:
        return pd.DataFrame(columns=["date", "spend", "channel"])
    return pd.concat(frames, ignore_index=True)


def load_daily_traditional_spend() -> pd.DataFrame:
    """Load and aggregate daily traditional media spend (weekly→daily split)."""
    frames = []
    # TV — weekly data, spread evenly across 7 days
    tv_path = os.path.join(RAW_DIR, "tv_performance.csv")
    if os.path.exists(tv_path):
        tv = pd.read_csv(tv_path, usecols=["date_week_start", "spend"])
        weekly = tv.groupby("date_week_start")["spend"].sum().reset_index()
        rows = []
        for _, r in weekly.iterrows():
            start = pd.to_datetime(r["date_week_start"]).date()
            daily_spend = r["spend"] / 7.0
            for d in range(7):
                day = start + datetime.timedelta(days=d)
                if START_DATE <= day <= END_DATE:
                    rows.append({"date": day.strftime(DATE_FORMAT), "spend": daily_spend, "channel": "tv"})
        if rows:
            frames.append(pd.DataFrame(rows))

    # OOH, Radio — start/end date ranges, spread evenly
    for ch, fname in [("ooh", "ooh_performance.csv"), ("radio", "radio_performance.csv")]:
        path = os.path.join(RAW_DIR, fname)
        if not os.path.exists(path):
            continue
        df = pd.read_csv(path, usecols=["start_date", "end_date", "spend"])
        rows = []
        for _, r in df.iterrows():
            s = pd.to_datetime(r["start_date"]).date()
            e = pd.to_datetime(r["end_date"]).date()
            ndays = max((e - s).days + 1, 1)
            daily_spend = r["spend"] / ndays
            for d in range(ndays):
                day = s + datetime.timedelta(days=d)
                if START_DATE <= day <= END_DATE:
                    rows.append({"date": day.strftime(DATE_FORMAT), "spend": daily_spend, "channel": ch})
        if rows:
            frames.append(pd.DataFrame(rows))

    # Print — daily
    print_path = os.path.join(RAW_DIR, "print_performance.csv")
    if os.path.exists(print_path):
        pr = pd.read_csv(print_path, usecols=["date", "spend"])
        daily = pr.groupby("date")["spend"].sum().reset_index()
        daily["channel"] = "print"
        frames.append(daily)

    if not frames:
        return pd.DataFrame(columns=["date", "spend", "channel"])
    return pd.concat(frames, ignore_index=True)


def build_daily_spend_index() -> pd.Series:
    """Build a daily total media spend series (all channels combined)."""
    digital = load_daily_digital_spend()
    trad = load_daily_traditional_spend()
    combined = pd.concat([digital, trad], ignore_index=True)
    daily = combined.groupby("date")["spend"].sum()
    idx = pd.Series([d.strftime(DATE_FORMAT) for d in DATE_RANGE], name="date")
    daily = daily.reindex(idx, fill_value=0.0)
    return daily


def campaign_names_from_media() -> list:
    """Extract campaign names from digital media CSVs for UTM mapping."""
    names = []
    for fname in ["meta_ads.csv", "google_ads.csv", "tiktok_ads.csv"]:
        path = os.path.join(RAW_DIR, fname)
        if os.path.exists(path):
            df = pd.read_csv(path, usecols=["campaign_name"])
            names.extend(df["campaign_name"].unique().tolist())
    return names if names else ["BRAND_AWARENESS_DEFAULT"]


# ---------------------------------------------------------------------------
# Lead / sales utilities
# ---------------------------------------------------------------------------

def assign_lead_stage(rng, created_date: datetime.date):
    """Walk lead through pipeline stages probabilistically."""
    stage = "NEW"
    stage_date = created_date
    for next_stage, rate in LEAD_STAGE_FLOW[1:]:
        if rate is None:
            break
        if rng.random() < rate:
            stage = next_stage
            stage_date = stage_date + datetime.timedelta(days=int(rng.integers(1, 14)))
            if stage_date > END_DATE:
                stage_date = END_DATE
        else:
            if rng.random() < 0.5 and stage not in ("NEW",):
                stage = "LOST"
            break
    return stage, stage_date


def build_lead_row(rng, idx, date_str, source, model, dealer_id, stage, stage_date, market):
    """Build a single lead row dict."""
    finance = rng.choice(FINANCE_TYPES, p=list(FINANCE_DISTRIBUTION.values()))
    return {
        "lead_id": f"LD{idx + 1:06d}",
        "created_date": date_str,
        "source": source,
        "model": model,
        "dealer_id": dealer_id,
        "stage": stage,
        "stage_updated_date": stage_date.strftime(DATE_FORMAT) if isinstance(stage_date, datetime.date) else stage_date,
        "market": market,
        "finance_type": finance if stage in ("NEGOTIATION", "WON") else None,
        "is_qualified": stage in ("QUALIFIED", "TD_BOOKED", "TD_COMPLETED", "NEGOTIATION", "WON"),
    }


def display_to_model_key(display_name: str):
    """Map display name to model key."""
    for k, v in VEHICLE_MODELS.items():
        if v["display_name"] == display_name:
            return k
    return None


def days_in_month(m: int) -> int:
    if m == 12:
        return 31
    return (datetime.date(2025, m + 1, 1) - datetime.date(2025, m, 1)).days
