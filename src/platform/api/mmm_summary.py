"""Build a high-level MMM data summary from data/mmm/ files."""

from pathlib import Path

import pandas as pd

_here = Path(__file__).resolve().parent
PROJECT_ROOT = _here
for _ in range(10):
    if (PROJECT_ROOT / "requirements.txt").exists():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent

MMM_DIR = PROJECT_ROOT / "data" / "mmm"
DATA_PATH = MMM_DIR / "model_ready.csv"

CHANNELS = [
    "tv", "ooh", "print", "radio", "youtube",
    "meta", "google", "dv360", "tiktok", "linkedin", "events",
]


def build_mmm_summary() -> dict:
    """Return a summary dict of the MMM dataset."""
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])

    total_spend = float(df["spend_total"].sum())
    total_units = int(df["units_sold"].sum())
    total_revenue = float(df["revenue"].sum())
    total_leads = int(df["leads"].sum())
    total_test_drives = int(df["test_drives"].sum())

    channel_breakdown = {}
    for ch in CHANNELS:
        col = f"spend_{ch}"
        channel_breakdown[ch] = round(float(df[col].sum()), 2)

    weekly_spend = []
    for _, row in df.iterrows():
        weekly_spend.append({
            "week_start": row["week_start"].strftime("%Y-%m-%d"),
            "total_spend": round(float(row["spend_total"]), 2),
        })

    weeks_of_data = len(df)
    post_launch_weeks = int((df["units_sold"] > 0).sum())

    return {
        "total_spend": round(total_spend, 2),
        "total_units": total_units,
        "total_revenue": round(total_revenue, 2),
        "total_leads": total_leads,
        "total_test_drives": total_test_drives,
        "channel_breakdown": channel_breakdown,
        "weekly_spend": weekly_spend,
        "weeks_of_data": weeks_of_data,
        "post_launch_weeks": post_launch_weeks,
    }


if __name__ == "__main__":
    import json
    import sys

    summary = build_mmm_summary()
    json.dump(summary, sys.stdout, indent=2)
    print()
