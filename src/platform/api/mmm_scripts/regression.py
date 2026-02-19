"""Ridge regression for MMM: units_sold ~ adstock channels + controls."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

# Resolve project root (walk up until we find requirements.txt)
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


def run_regression():
    """Run Ridge regression on post-launch weeks and return results dict."""
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])

    # Filter to post-launch weeks (units_sold > 0)
    df_post = df[df[TARGET] > 0].copy()
    n = len(df_post)

    feature_names = ADSTOCK_COLS + CONTROL_COLS
    X = df_post[feature_names].values
    y = df_post[TARGET].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = Ridge(alpha=1.0)
    model.fit(X_scaled, y)

    y_pred = model.predict(X_scaled)
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - ss_res / ss_tot
    p = X_scaled.shape[1]
    adjusted_r_squared = 1 - (1 - r_squared) * (n - 1) / (n - p - 1)

    coefficients = {}
    for i, name in enumerate(feature_names):
        coefficients[name] = round(float(model.coef_[i]), 6)

    return {
        "r_squared": round(float(r_squared), 4),
        "adjusted_r_squared": round(float(adjusted_r_squared), 4),
        "intercept": round(float(model.intercept_), 4),
        "coefficients": coefficients,
        "n_observations": n,
        "feature_names": feature_names,
        "scaler_mean": {name: round(float(m), 4) for name, m in zip(feature_names, scaler.mean_)},
        "scaler_scale": {name: round(float(s), 4) for name, s in zip(feature_names, scaler.scale_)},
    }


if __name__ == "__main__":
    results = run_regression()
    json.dump(results, sys.stdout, indent=2)
    print()
