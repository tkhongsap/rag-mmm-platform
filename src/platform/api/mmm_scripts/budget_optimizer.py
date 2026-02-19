"""Budget optimizer: shift spend from low to high marginal-ROI channels."""

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

MAX_SHIFT_PCT = 0.30  # +/-30% constraint per channel


def run_budget_optimizer():
    """Optimize budget allocation based on marginal ROI."""
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])
    df_post = df[df[TARGET] > 0].copy()

    feature_names = ADSTOCK_COLS + CONTROL_COLS
    X = df_post[feature_names].values
    y = df_post[TARGET].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)

    total_revenue = float(df_post["revenue"].sum())
    total_units = float(df_post[TARGET].sum())
    revenue_per_unit = total_revenue / total_units if total_units > 0 else 0

    # Current allocation and marginal ROI per channel
    current_allocation = {}
    marginal_rois = {}
    for i, ch in enumerate(CHANNELS):
        spend_col = f"spend_{ch}"
        total_spend = float(df_post[spend_col].sum())
        current_allocation[ch] = total_spend

        coef_original = model.coef_[i] / scaler.scale_[i]
        marginal_rois[ch] = coef_original * revenue_per_unit

    total_budget = sum(current_allocation.values())

    # Iterative gradient-based reallocation
    optimal = dict(current_allocation)
    n_iterations = 50
    step_size = total_budget * 0.01  # 1% of total budget per step

    for _ in range(n_iterations):
        # Find highest and lowest marginal ROI channels that still have room
        sorted_channels = sorted(marginal_rois.keys(), key=lambda c: marginal_rois[c])
        moved = False
        for low_ch in sorted_channels:
            for high_ch in reversed(sorted_channels):
                if low_ch == high_ch:
                    continue
                if marginal_rois[high_ch] <= marginal_rois[low_ch]:
                    continue

                low_floor = current_allocation[low_ch] * (1 - MAX_SHIFT_PCT)
                high_ceil = current_allocation[high_ch] * (1 + MAX_SHIFT_PCT)

                can_take = optimal[low_ch] - low_floor
                can_give = high_ceil - optimal[high_ch]
                transfer = min(step_size, can_take, can_give)

                if transfer > 1:
                    optimal[low_ch] -= transfer
                    optimal[high_ch] += transfer
                    moved = True
                    break
            if moved:
                break
        if not moved:
            break

    # Estimate projected lift
    current_units = 0
    optimal_units = 0
    for i, ch in enumerate(CHANNELS):
        coef_original = model.coef_[i] / scaler.scale_[i]
        current_units += coef_original * current_allocation[ch]
        optimal_units += coef_original * optimal[ch]

    lift_pct = ((optimal_units - current_units) / current_units * 100
                if current_units != 0 else 0)

    return {
        "current_allocation": {ch: round(v, 2) for ch, v in current_allocation.items()},
        "optimal_allocation": {ch: round(v, 2) for ch, v in optimal.items()},
        "projected_lift_pct": round(float(lift_pct), 2),
        "total_budget": round(total_budget, 2),
        "marginal_rois": {ch: round(float(v), 4) for ch, v in marginal_rois.items()},
    }


if __name__ == "__main__":
    results = run_budget_optimizer()
    json.dump(results, sys.stdout, indent=2)
    print()
