"""ROI analysis per channel using Ridge regression coefficients."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

_here = Path(__file__).resolve().parent
PROJECT_ROOT = _here
for _ in range(10):
    if (PROJECT_ROOT / "requirements.txt").exists():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_PATH = PROJECT_ROOT / "data" / "mmm" / "model_ready.csv"

CHANNELS = [
    "tv", "ooh", "print", "radio", "youtube",
    "meta", "google", "dv360", "tiktok", "linkedin", "events",
]

ADSTOCK_COLS = [f"adstock_{ch}" for ch in CHANNELS]
CONTROL_COLS = ["consumer_confidence_index", "bank_rate_pct", "competitor_spend_weekly"]
TARGET = "units_sold"


def run_roi_analysis():
    """Compute per-channel ROI from regression coefficients."""
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])
    df_post = df[df[TARGET] > 0].copy()

    feature_names = ADSTOCK_COLS + CONTROL_COLS
    X = df_post[feature_names].values
    y = df_post[TARGET].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)

    # Average revenue per unit from post-launch data
    total_revenue = float(df_post["revenue"].sum())
    total_units = float(df_post[TARGET].sum())
    revenue_per_unit = total_revenue / total_units if total_units > 0 else 0

    channels_result = []
    overall_spend = 0.0
    overall_revenue = total_revenue

    for i, ch in enumerate(CHANNELS):
        adstock_col = f"adstock_{ch}"
        spend_col = f"spend_{ch}"

        coef_scaled = model.coef_[i]
        # Convert scaled coefficient back to original units
        coef_original = coef_scaled / scaler.scale_[i]

        total_adstock = float(df_post[adstock_col].sum())
        total_spend = float(df_post[spend_col].sum())

        incremental_units = coef_original * total_adstock
        incremental_revenue = incremental_units * revenue_per_unit
        roi = incremental_revenue / total_spend if total_spend > 0 else 0

        # Marginal ROI: effect of one more unit of adstock spend
        marginal_roi = coef_original * revenue_per_unit

        channels_result.append({
            "name": ch,
            "total_spend": round(total_spend, 2),
            "incremental_units": round(float(incremental_units), 2),
            "incremental_revenue": round(float(incremental_revenue), 2),
            "roi": round(float(roi), 4),
            "marginal_roi": round(float(marginal_roi), 4),
        })
        overall_spend += total_spend

    return {
        "channels": channels_result,
        "total_spend": round(overall_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "total_units": round(total_units, 2),
        "revenue_per_unit": round(revenue_per_unit, 2),
    }


if __name__ == "__main__":
    results = run_roi_analysis()
    json.dump(results, sys.stdout, indent=2)
    print()
