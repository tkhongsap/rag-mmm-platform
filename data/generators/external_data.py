"""
Generate external context datasets: competitor spend, economic indicators,
and SLA tracking.

Produces:
    data/raw/competitor_spend.csv   (~360 rows)
    data/raw/economic_indicators.csv (~36 rows)
    data/raw/sla_tracking.csv       (~50 rows)
"""

import datetime
import numpy as np
import pandas as pd

from data.generators.config import (
    RAW_DIR,
    RANDOM_SEED,
    START_DATE,
    END_DATE,
    COMPETITOR_BRANDS,
    COMPETITOR_MONTHLY_SPEND_RANGE,
    UK_BANK_RATE_2025,
    UK_CPI_MONTHLY_RANGE,
    UK_CONSUMER_CONFIDENCE_RANGE,
    MARKETS,
    SEASONAL_MULTIPLIERS,
    add_noise,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_COMPETITOR_CHANNELS = ["tv", "digital", "ooh"]
_CHANNEL_SHARE = {"tv": 0.45, "digital": 0.40, "ooh": 0.15}

_SOV_SOURCES = [
    "Nielsen Ad Intel", "Kantar Media", "BARB/RAJAR",
    "Pathmatics", "Comscore", "Internal Estimate",
]


def _generate_competitor_spend(rng: np.random.Generator) -> pd.DataFrame:
    """
    Monthly competitor spend by channel for 10 competitors over 12 months.
    ~360 rows (10 competitors × 12 months × 3 channels).
    """
    rows = []
    months = pd.date_range(START_DATE, END_DATE, freq="MS")

    for month_start in months:
        ym = month_start.strftime("%Y-%m")
        month_num = month_start.month
        seasonal = SEASONAL_MULTIPLIERS[month_num]

        for competitor in COMPETITOR_BRANDS:
            lo, hi = COMPETITOR_MONTHLY_SPEND_RANGE[competitor]
            monthly_total = rng.uniform(lo, hi) * (0.7 + 0.3 * seasonal)

            for channel in _COMPETITOR_CHANNELS:
                share = _CHANNEL_SHARE[channel]
                spend = round(add_noise(monthly_total * share, 0.08, rng), 2)

                # Share of voice: higher-spending brands get higher SOV
                base_sov = (spend / 3_000_000) * 100
                sov = round(min(max(add_noise(base_sov, 0.15, rng), 0.5), 35.0), 1)

                source = rng.choice(_SOV_SOURCES)

                rows.append({
                    "year_month": ym,
                    "competitor": competitor,
                    "channel": channel,
                    "estimated_spend_gbp": spend,
                    "share_of_voice_pct": sov,
                    "source": source,
                })

    return pd.DataFrame(rows)


def _generate_economic_indicators(rng: np.random.Generator) -> pd.DataFrame:
    """
    Monthly UK economic data for 3 markets over 12 months.
    ~36 rows (12 months × 3 markets).
    """
    rows = []
    months = pd.date_range(START_DATE, END_DATE, freq="MS")

    # UK-specific base trajectories (2025 realistic)
    uk_base = {
        "smmt_total_registrations": 165_000,    # monthly avg
        "smmt_bev_registrations": 33_000,       # ~20% BEV share growing
        "bev_market_share_pct": 20.0,
        "consumer_confidence_index": -10.0,
        "bank_rate_pct": UK_BANK_RATE_2025,
        "avg_petrol_price_ppl": 142.0,          # pence per litre
        "avg_electricity_price_pkwh": 28.5,     # pence per kWh
        "unemployment_rate_pct": 4.2,
        "cpi_index": 131.5,                     # 2015=100 base
        "new_car_avg_transaction_price_gbp": 38_500,
    }

    # Germany base
    de_base = {
        "smmt_total_registrations": 240_000,
        "smmt_bev_registrations": 55_000,
        "bev_market_share_pct": 23.0,
        "consumer_confidence_index": -8.0,
        "bank_rate_pct": 3.75,                  # ECB rate
        "avg_petrol_price_ppl": 165.0,
        "avg_electricity_price_pkwh": 35.0,
        "unemployment_rate_pct": 5.8,
        "cpi_index": 119.2,
        "new_car_avg_transaction_price_gbp": 42_000,
    }

    # France base
    fr_base = {
        "smmt_total_registrations": 150_000,
        "smmt_bev_registrations": 30_000,
        "bev_market_share_pct": 20.0,
        "consumer_confidence_index": -12.0,
        "bank_rate_pct": 3.75,
        "avg_petrol_price_ppl": 175.0,
        "avg_electricity_price_pkwh": 22.0,
        "unemployment_rate_pct": 7.3,
        "cpi_index": 118.5,
        "new_car_avg_transaction_price_gbp": 36_000,
    }

    market_bases = {"GB": uk_base, "DE": de_base, "FR": fr_base}

    # Monthly registration seasonal pattern (UK SMMT-like: Mar + Sep peaks)
    reg_seasonal = {
        1: 0.55, 2: 0.60, 3: 1.90, 4: 0.85, 5: 0.80, 6: 1.00,
        7: 0.85, 8: 0.60, 9: 1.80, 10: 0.80, 11: 0.65, 12: 0.60,
    }

    for market_code in MARKETS:
        base = market_bases[market_code]
        cpi_cumulative = base["cpi_index"]
        bev_share = base["bev_market_share_pct"]

        for i, month_start in enumerate(months):
            ym = month_start.strftime("%Y-%m")
            m = month_start.month

            # Registrations with seasonal pattern
            reg_mult = reg_seasonal[m]
            total_reg = int(add_noise(base["smmt_total_registrations"] * reg_mult, 0.05, rng))

            # BEV share grows ~0.3pp per month in 2025
            bev_share_m = bev_share + i * 0.3
            bev_reg = int(total_reg * bev_share_m / 100)
            bev_share_actual = round(bev_reg / max(total_reg, 1) * 100, 1)

            # Consumer confidence: slight improvement through the year (can be negative)
            cc_base = base["consumer_confidence_index"] + i * 0.3
            cc = round(cc_base + rng.normal(0, abs(cc_base) * 0.10), 1)

            # Bank rate: slight cuts expected in 2025
            # 2 BoE-style 25bp rate cuts: July (i=6) and October (i=9)
            rate_cuts = 0.0
            if i >= 6:
                rate_cuts = 0.25
            if i >= 9:
                rate_cuts = 0.50
            bank_rate = round(max(3.5, base["bank_rate_pct"] - rate_cuts), 3)

            # Petrol price with seasonal variation
            petrol = round(add_noise(base["avg_petrol_price_ppl"] + rng.uniform(-3, 3), 0.02, rng), 1)

            # Electricity price: relatively stable
            elec = round(add_noise(base["avg_electricity_price_pkwh"], 0.03, rng), 1)

            # Unemployment: gentle decline
            unemp = round(max(3.0, add_noise(base["unemployment_rate_pct"] - i * 0.02, 0.02, rng)), 1)

            # CPI: monthly increments
            cpi_change = rng.uniform(*UK_CPI_MONTHLY_RANGE)
            cpi_cumulative = round(cpi_cumulative * (1 + cpi_change), 1)

            # Transaction price: slight increase through year
            tx_price = int(add_noise(base["new_car_avg_transaction_price_gbp"] + i * 120, 0.02, rng))

            rows.append({
                "year_month": ym,
                "country": market_code,
                "smmt_total_registrations": total_reg,
                "smmt_bev_registrations": bev_reg,
                "bev_market_share_pct": bev_share_actual,
                "consumer_confidence_index": cc,
                "bank_rate_pct": bank_rate,
                "avg_petrol_price_ppl": petrol,
                "avg_electricity_price_pkwh": elec,
                "unemployment_rate_pct": unemp,
                "cpi_index": cpi_cumulative,
                "new_car_avg_transaction_price_gbp": tx_price,
            })

    return pd.DataFrame(rows)


# SLA vendor/contract definitions
_SLA_CONTRACTS = [
    {
        "vendor": "ITV",
        "contract_type": "TV Airtime",
        "metrics": [
            ("delivery_vs_booked_grps_pct", 95.0),
            ("makegood_turnaround_days", 5.0),
        ],
    },
    {
        "vendor": "Sky Media",
        "contract_type": "TV + BVOD Airtime",
        "metrics": [
            ("delivery_vs_booked_grps_pct", 95.0),
            ("adsmart_targeting_accuracy_pct", 90.0),
        ],
    },
    {
        "vendor": "JCDecaux",
        "contract_type": "OOH",
        "metrics": [
            ("site_uptime_pct", 98.0),
            ("posting_compliance_pct", 95.0),
        ],
    },
    {
        "vendor": "Clear Channel",
        "contract_type": "DOOH",
        "metrics": [
            ("screen_uptime_pct", 97.0),
            ("impression_delivery_pct", 90.0),
        ],
    },
    {
        "vendor": "MediaAgency",
        "contract_type": "Agency Services",
        "metrics": [
            ("campaign_launch_on_time_pct", 95.0),
            ("monthly_report_timeliness_days", 3.0),
        ],
    },
]


def _generate_sla_tracking(rng: np.random.Generator) -> pd.DataFrame:
    """
    Monthly SLA compliance across vendors and metrics.
    ~50 rows (5 vendors × ~2 metrics × varying months).
    Not all vendors active from month 1 — TV/Agency from Jan, OOH from Jul.
    """
    rows = []
    months = pd.date_range(START_DATE, END_DATE, freq="MS")

    # When each vendor contract becomes active
    vendor_start_month = {
        "ITV": 8,           # Aug (pre-launch media booking)
        "Sky Media": 9,     # Sep (launch month)
        "JCDecaux": 7,      # Jul (OOH sites go up before launch)
        "Clear Channel": 8, # Aug
        "MediaAgency": 7,   # Jul (agency ramps up for launch prep)
    }

    for contract in _SLA_CONTRACTS:
        vendor = contract["vendor"]
        contract_type = contract["contract_type"]
        start_m = vendor_start_month[vendor]

        for month_start in months:
            m = month_start.month
            if m < start_m:
                continue

            ym = month_start.strftime("%Y-%m")

            for metric_name, contracted_value in contract["metrics"]:
                # Most months: compliant. Occasional misses (~10% chance → ~90% compliance)
                if rng.random() < 0.10:
                    # Miss: actual is 80-99% of contracted
                    if "days" in metric_name:
                        # For days-based metrics, higher is worse
                        actual = round(contracted_value + rng.uniform(1, 4), 1)
                    else:
                        actual = round(contracted_value * rng.uniform(0.82, 0.98), 1)
                    in_compliance = False
                    notes = rng.choice([
                        "Under review — vendor notified",
                        "Credit note pending",
                        "Weather/technical disruption",
                        "Scheduling conflict — makegood agreed",
                        "Partial delivery — reconciliation in progress",
                    ])
                else:
                    # Compliant
                    if "days" in metric_name:
                        actual = round(max(1.0, contracted_value - rng.uniform(0, 2)), 1)
                    else:
                        actual = round(min(100.0, contracted_value + rng.uniform(0, 3)), 1)
                    in_compliance = True
                    notes = ""

                if "days" in metric_name:
                    variance = round(((actual - contracted_value) / contracted_value) * 100, 1)
                else:
                    variance = round(((actual - contracted_value) / contracted_value) * 100, 1)

                rows.append({
                    "year_month": ym,
                    "vendor": vendor,
                    "contract_type": contract_type,
                    "metric_name": metric_name,
                    "contracted_value": contracted_value,
                    "actual_value": actual,
                    "variance_pct": variance,
                    "in_compliance": in_compliance,
                    "notes": notes,
                })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate() -> dict:
    """
    Generate all external context datasets.

    Returns:
        dict mapping filename to (DataFrame, output_path) tuples.
    """
    rng = np.random.default_rng(RANDOM_SEED + 500)
    import os

    results = {}

    # 1. Competitor spend
    df_comp = _generate_competitor_spend(rng)
    path_comp = os.path.join(RAW_DIR, "competitor_spend.csv")
    df_comp.to_csv(path_comp, index=False)
    results["competitor_spend.csv"] = (df_comp, path_comp)
    print(f"  [external_data] competitor_spend.csv: {len(df_comp)} rows -> {path_comp}")

    # 2. Economic indicators
    df_econ = _generate_economic_indicators(rng)
    path_econ = os.path.join(RAW_DIR, "economic_indicators.csv")
    df_econ.to_csv(path_econ, index=False)
    results["economic_indicators.csv"] = (df_econ, path_econ)
    print(f"  [external_data] economic_indicators.csv: {len(df_econ)} rows -> {path_econ}")

    # 3. SLA tracking
    df_sla = _generate_sla_tracking(rng)
    path_sla = os.path.join(RAW_DIR, "sla_tracking.csv")
    df_sla.to_csv(path_sla, index=False)
    results["sla_tracking.csv"] = (df_sla, path_sla)
    print(f"  [external_data] sla_tracking.csv: {len(df_sla)} rows -> {path_sla}")

    return results


if __name__ == "__main__":
    print("Generating external context datasets...")
    results = generate()
    print(f"\nDone. Generated {len(results)} files.")
    for name, (df, path) in results.items():
        print(f"  {name}: {len(df)} rows")
