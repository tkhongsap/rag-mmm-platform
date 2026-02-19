"""Adstock and saturation curve parameters per channel."""

import json
import sys
from pathlib import Path

import pandas as pd

_here = Path(__file__).resolve().parent
PROJECT_ROOT = _here
for _ in range(10):
    if (PROJECT_ROOT / "requirements.txt").exists():
        break
    PROJECT_ROOT = PROJECT_ROOT.parent

DATA_PATH = PROJECT_ROOT / "data" / "mmm" / "model_ready.csv"

# Import decay rates and saturation params from config
sys.path.insert(0, str(PROJECT_ROOT / "data" / "generators"))
from config import ADSTOCK_DECAY_RATES, SATURATION_PARAMS

CHANNELS = [
    "tv", "ooh", "print", "radio", "youtube",
    "meta", "google", "dv360", "tiktok", "linkedin", "events",
]


def run_adstock_curves():
    """Compute adstock transformation stats per channel."""
    df = pd.read_csv(DATA_PATH, parse_dates=["week_start"])

    channels_result = []
    for ch in CHANNELS:
        spend_col = f"spend_{ch}"
        adstock_col = f"adstock_{ch}"

        total_raw_spend = float(df[spend_col].sum())
        total_adstocked = float(df[adstock_col].sum())
        peak_adstock = float(df[adstock_col].max())

        decay_rate = ADSTOCK_DECAY_RATES.get(ch, 0.5)
        sat = SATURATION_PARAMS.get(ch, {"alpha": 0.5, "gamma": 0.5})

        channels_result.append({
            "name": ch,
            "decay_rate": decay_rate,
            "saturation_alpha": sat["alpha"],
            "saturation_gamma": sat["gamma"],
            "peak_adstock": round(peak_adstock, 2),
            "total_raw_spend": round(total_raw_spend, 2),
            "total_adstocked": round(total_adstocked, 2),
        })

    return {"channels": channels_result}


if __name__ == "__main__":
    results = run_adstock_curves()
    json.dump(results, sys.stdout, indent=2)
    print()
