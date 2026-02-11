"""
Traditional media data generator.

Produces 4 CSV files:
  - tv_performance.csv       (~300 rows, weekly × broadcaster)
  - ooh_performance.csv      (~150 rows, per-campaign period)
  - print_performance.csv    (~100 rows, per-insertion)
  - radio_performance.csv    (~60 rows, per-flight)

All constants imported from data.generators.config.
"""

import os
import datetime

import numpy as np
import pandas as pd

from data.generators.config import (
    RANDOM_SEED,
    RNG,
    RAW_DIR,
    START_DATE,
    END_DATE,
    UK_LAUNCH_DATE,
    DATE_FORMAT,
    CHANNEL_BUDGETS_GBP,
    SEASONAL_MULTIPLIERS,
    TRADITIONAL_BENCHMARKS,
    TV_REGIONS,
    TV_PROGRAMMES,
    VEHICLE_MODELS,
    _UK_REGIONS,
    _DAYS_IN_MONTH_2025,
    distribute_budget_monthly,
    get_seasonal_multiplier,
    add_noise,
    date_to_str,
    get_active_models,
)


# ── Reproducible RNG instances (one per dataset) ─────────────────────────
_rng_tv = np.random.default_rng(RANDOM_SEED + 40)
_rng_ooh = np.random.default_rng(RANDOM_SEED + 41)
_rng_print = np.random.default_rng(RANDOM_SEED + 42)
_rng_radio = np.random.default_rng(RANDOM_SEED + 43)


# ═══════════════════════════════════════════════════════════════════════════
# 1. TV Performance  (~300 rows — weekly × broadcaster)
# ═══════════════════════════════════════════════════════════════════════════

_BROADCASTERS = {
    "ITV":       {"share": 0.35, "type": "linear"},
    "Channel 4": {"share": 0.20, "type": "linear"},
    "Sky":       {"share": 0.15, "type": "linear"},
    "ITVX":      {"share": 0.12, "type": "bvod"},
    "Channel4 Streaming": {"share": 0.10, "type": "bvod"},
    "Sky Go":    {"share": 0.08, "type": "bvod"},
}

_DAYPARTS = {
    "Peak":       {"share": 0.40, "grp_mult": 1.3},
    "Daytime":    {"share": 0.15, "grp_mult": 0.7},
    "Late Night": {"share": 0.10, "grp_mult": 0.6},
    "Breakfast":  {"share": 0.15, "grp_mult": 0.9},
    "Pre-Peak":   {"share": 0.20, "grp_mult": 1.1},
}

_SPOT_LENGTHS = [30, 60]
_SPOT_LENGTH_WEIGHTS = [0.70, 0.30]

_TV_PROGRAMME_NAMES = [
    "Coronation Street", "Emmerdale", "The Chase", "Good Morning Britain",
    "Saturday Night Takeaway", "F1 Live", "Grand Designs", "Gogglebox",
    "The Great British Bake Off", "News at Ten", "Sky Sports Premier League",
    "Channel 4 News",
]


def _is_tv_flight_on(week_start: datetime.date) -> bool:
    """
    Determine if TV is on-air for a given week.

    Pattern:
      - Jul-Aug: pre-launch teasers (1 week on / 2 weeks off)
      - Sep-Dec: main flight (2 weeks on / 1 week off)
      - Jan-Jun: dark (no TV)
    """
    month = week_start.month
    if month < 7:
        return False
    if month in (7, 8):
        # Teaser phase — 1 week on, 2 weeks off
        weeks_since_jul1 = (week_start - datetime.date(2025, 7, 1)).days // 7
        return weeks_since_jul1 % 3 == 0
    # Sep-Dec — 2 weeks on, 1 week off
    weeks_since_sep1 = (week_start - datetime.date(2025, 9, 1)).days // 7
    return weeks_since_sep1 % 3 != 2  # on, on, off


def _generate_tv() -> pd.DataFrame:
    """Generate tv_performance.csv."""
    rng = _rng_tv
    annual_budget = CHANNEL_BUDGETS_GBP["tv"]  # £6M
    monthly_budgets = distribute_budget_monthly(annual_budget)
    benchmarks = TRADITIONAL_BENCHMARKS["tv"]

    # Build week starts (Mondays) that fall in 2025
    week_starts = pd.date_range(
        start=START_DATE - datetime.timedelta(days=START_DATE.weekday()),
        end=END_DATE,
        freq="W-MON",
    )
    week_starts = [w.date() for w in week_starts if START_DATE <= w.date() <= END_DATE]

    rows = []
    for ws in week_starts:
        if not _is_tv_flight_on(ws):
            continue

        month = ws.month
        seasonal = SEASONAL_MULTIPLIERS[month]

        # Weekly budget allocation (from monthly)
        month_budget = monthly_budgets[month]
        weeks_in_month = _DAYS_IN_MONTH_2025[month] / 7.0
        week_budget = month_budget / weeks_in_month

        # Distribute across broadcaster × daypart
        for bc_name, bc_info in _BROADCASTERS.items():
            bc_budget = week_budget * bc_info["share"]

            # Pick 3-4 dayparts per broadcaster per week to hit ~300 rows
            n_dayparts = rng.choice([3, 4], p=[0.5, 0.5])
            daypart_keys = list(_DAYPARTS.keys())
            chosen_dayparts = rng.choice(daypart_keys, size=n_dayparts, replace=False)

            for dp in chosen_dayparts:
                dp_info = _DAYPARTS[dp]
                dp_budget = bc_budget * dp_info["share"] / sum(
                    _DAYPARTS[d]["share"] for d in chosen_dayparts
                )
                if dp_budget < 500:
                    continue

                # Spot length
                spot_len = rng.choice(_SPOT_LENGTHS, p=_SPOT_LENGTH_WEIGHTS)
                if spot_len == 30:
                    cpp_low, cpp_high = benchmarks["cpp_30s"]
                else:
                    cpp_low, cpp_high = benchmarks["cpp_60s"]

                cpp = rng.uniform(cpp_low, cpp_high)
                # Adjust CPP by daypart multiplier
                cpp *= dp_info["grp_mult"]
                cpp = add_noise(cpp, 0.08, rng)

                spots_aired = max(1, int(round(dp_budget / cpp)))
                spend = round(spots_aired * cpp, 2)

                # GRPs: 50-150 base, scaled by seasonal
                base_grps = rng.uniform(50, 150) * dp_info["grp_mult"]
                grps = round(base_grps * (seasonal / 1.0) * (spots_aired / 5.0), 1)
                grps = max(5.0, grps)

                # Reach
                reach_pct_low, reach_pct_high = benchmarks["reach_per_spot_pct"]
                reach_pct = rng.uniform(reach_pct_low, reach_pct_high) * spots_aired
                reach_pct = min(reach_pct, 85.0)
                reach_pct = round(add_noise(reach_pct, 0.05, rng), 1)
                # UK adult population ~53M
                reach_000 = round(53_000 * reach_pct / 100.0, 0)

                # Frequency
                freq_low, freq_high = benchmarks["frequency_target"]
                avg_freq = round(rng.uniform(freq_low, freq_high), 1)

                # Market: GB for all national TV
                market = "GB"

                # Programme name
                programme = rng.choice(_TV_PROGRAMME_NAMES)

                rows.append({
                    "date_week_start": date_to_str(ws),
                    "broadcaster": bc_name,
                    "daypart": dp,
                    "market": market,
                    "spot_length_seconds": int(spot_len),
                    "spots_aired": spots_aired,
                    "grps": grps,
                    "reach_000": int(reach_000),
                    "reach_pct": reach_pct,
                    "avg_frequency": avg_freq,
                    "cpp": round(cpp, 2),
                    "spend": spend,
                    "programme_name": programme,
                })

    df = pd.DataFrame(rows)
    df.sort_values("date_week_start", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Scale spend to hit annual budget target
    actual_total = df["spend"].sum()
    if actual_total > 0:
        scale = annual_budget / actual_total
        df["spend"] = (df["spend"] * scale).round(2)
        df["cpp"] = (df["cpp"] * scale).round(2)

    return df


# ═══════════════════════════════════════════════════════════════════════════
# 2. OOH Performance  (~150 rows — per-campaign period, 2-week cycles)
# ═══════════════════════════════════════════════════════════════════════════

_OOH_VENDORS = ["JCDecaux", "Clear Channel", "Global", "Ocean Outdoor", "Primesight"]

_OOH_CAMPAIGN_THEMES = [
    "S07 Launch Awareness", "S07 Range & Price", "AVATR 12 Premium",
    "EV Lifestyle", "Test Drive Call-to-Action", "Dealer Network Launch",
    "S05 Preview Teaser", "Year-End Promo", "Brand Building",
    "Conquest - Tesla Alternative",
]

_OOH_CITIES = [
    "London", "Manchester", "Birmingham", "Leeds", "Glasgow",
    "Edinburgh", "Bristol", "Liverpool", "Newcastle", "Cardiff",
    "Nottingham", "Sheffield", "Brighton", "Reading", "Oxford",
]

_OOH_REGIONS = [
    "London", "South East", "South West", "Midlands",
    "North West", "North East", "Scotland", "Wales",
]


def _generate_ooh() -> pd.DataFrame:
    """Generate ooh_performance.csv."""
    rng = _rng_ooh
    annual_budget = CHANNEL_BUDGETS_GBP["ooh"]  # £3M
    monthly_budgets = distribute_budget_monthly(annual_budget)
    benchmarks = TRADITIONAL_BENCHMARKS["ooh"]
    formats = benchmarks["formats"]

    # Digital vs classic split
    digital_share = 0.55
    classic_share = 0.45
    digital_formats = ["DIGITAL_SCREEN"]
    classic_formats = [f for f in formats if f != "DIGITAL_SCREEN"]

    rows = []
    campaign_counter = 0

    # Generate 1-week campaign periods across the year for ~150 rows
    period_start = START_DATE
    while period_start <= END_DATE:
        period_end = min(period_start + datetime.timedelta(days=6), END_DATE)
        month = period_start.month
        seasonal = SEASONAL_MULTIPLIERS[month]

        # Monthly budget pro-rated to 1-week period
        month_budget = monthly_budgets[month]
        days_in_period = (period_end - period_start).days + 1
        period_budget = month_budget * days_in_period / _DAYS_IN_MONTH_2025[month]

        # Skip very low-spend periods
        if period_budget < 500:
            period_start = period_end + datetime.timedelta(days=1)
            continue

        # Major bursts in Sep-Oct get extra campaigns per week — target ~150 rows
        n_campaigns = 1
        if month in (9, 10):
            n_campaigns = rng.choice([4, 5, 6], p=[0.3, 0.4, 0.3])
        elif month in (7, 8, 11, 12):
            n_campaigns = rng.choice([3, 4], p=[0.5, 0.5])
        elif month in (3, 4, 5, 6):
            n_campaigns = rng.choice([1, 2, 3], p=[0.3, 0.4, 0.3])

        campaign_budget = period_budget / n_campaigns

        for _ in range(n_campaigns):
            campaign_counter += 1
            campaign_id = f"OOH-{campaign_counter:04d}"

            # Format selection
            is_digital = rng.random() < digital_share
            if is_digital:
                fmt = rng.choice(digital_formats)
                fmt_budget = campaign_budget * digital_share
            else:
                fmt = rng.choice(classic_formats)
                fmt_budget = campaign_budget * classic_share

            # Sites booked
            cost_low, cost_high = benchmarks["cost_per_panel_week"]
            cost_per_panel = rng.uniform(cost_low, cost_high)
            if fmt == "DIGITAL_SCREEN":
                cost_per_panel *= 1.8  # premium for digital
            weeks_in_period = max(1, days_in_period / 7)
            sites_booked = max(1, int(round(fmt_budget / (cost_per_panel * weeks_in_period))))

            spend = round(sites_booked * cost_per_panel * weeks_in_period, 2)

            # Impressions
            imp_low, imp_high = benchmarks["impressions_per_panel_day"]
            imp_per_panel_day = rng.uniform(imp_low, imp_high)
            if fmt == "DIGITAL_SCREEN":
                imp_per_panel_day *= 1.5
            impressions = int(round(imp_per_panel_day * sites_booked * days_in_period))

            # Reach: ~30-70% of impressions are unique
            unique_ratio = rng.uniform(0.30, 0.70)
            reach_000 = int(round(impressions * unique_ratio / 1000))

            # Frequency
            frequency = round(impressions / max(1, reach_000 * 1000), 1)
            frequency = max(1.0, min(frequency, 15.0))

            # Location
            city = rng.choice(_OOH_CITIES)
            region = rng.choice(_OOH_REGIONS)

            # Campaign name
            theme = rng.choice(_OOH_CAMPAIGN_THEMES)
            campaign_name = f"{theme} - {city} {fmt}"

            vendor = rng.choice(_OOH_VENDORS)
            market = "GB"

            rows.append({
                "campaign_name": campaign_name,
                "campaign_id": campaign_id,
                "start_date": date_to_str(period_start),
                "end_date": date_to_str(period_end),
                "market": market,
                "format": fmt,
                "vendor": vendor,
                "sites_booked": sites_booked,
                "impressions": impressions,
                "reach_000": reach_000,
                "frequency": frequency,
                "spend": spend,
                "region": region,
                "city": city,
            })

        period_start = period_end + datetime.timedelta(days=1)

    df = pd.DataFrame(rows)

    # Scale spend to hit annual budget target
    actual_total = df["spend"].sum()
    if actual_total > 0:
        scale = annual_budget / actual_total
        df["spend"] = (df["spend"] * scale).round(2)

    return df


# ═══════════════════════════════════════════════════════════════════════════
# 3. Print Performance  (~100 rows — per-insertion)
# ═══════════════════════════════════════════════════════════════════════════

_PRINT_EDITIONS = ["Standard", "Special Issue", "Supplement", "Buyers Guide"]

_PRINT_FORMATS = [
    "Full Page", "Double Page Spread", "Half Page", "Quarter Page",
    "Gatefold", "Cover Position",
]

_PRINT_FORMAT_COST_MULT = {
    "Full Page": 1.0,
    "Double Page Spread": 1.8,
    "Half Page": 0.55,
    "Quarter Page": 0.30,
    "Gatefold": 2.2,
    "Cover Position": 2.5,
}

_PUBLICATION_CIRCULATION = {
    "Autocar": 28_000,
    "What Car?": 45_000,
    "Top Gear Magazine": 60_000,
    "Auto Express": 32_000,
    "CAR Magazine": 22_000,
    "EVO": 18_000,
    "The Sunday Times Driving": 120_000,
    "Financial Times": 170_000,
    "The Telegraph Motoring": 95_000,
}

_READERSHIP_MULTIPLIER = {
    "Autocar": 4.5,
    "What Car?": 5.0,
    "Top Gear Magazine": 6.0,
    "Auto Express": 4.2,
    "CAR Magazine": 3.8,
    "EVO": 4.0,
    "The Sunday Times Driving": 3.0,
    "Financial Times": 2.5,
    "The Telegraph Motoring": 2.8,
}


def _generate_print() -> pd.DataFrame:
    """Generate print_performance.csv."""
    rng = _rng_print
    annual_budget = CHANNEL_BUDGETS_GBP["print"]  # £600K
    monthly_budgets = distribute_budget_monthly(annual_budget)
    benchmarks = TRADITIONAL_BENCHMARKS["print"]
    publications = benchmarks["publications"]
    cost_range = benchmarks["cost_per_page"]

    rows = []
    creative_counter = 0

    for month in range(1, 13):
        seasonal = SEASONAL_MULTIPLIERS[month]
        month_budget = monthly_budgets[month]

        if month_budget < 500:
            continue

        # Number of insertions this month — target ~100 total rows
        if month >= 9:
            n_insertions = rng.integers(10, 18)
        elif month >= 7:
            n_insertions = rng.integers(6, 12)
        elif month in (3, 6):
            n_insertions = rng.integers(3, 6)
        elif month in (4, 5):
            n_insertions = rng.integers(2, 4)
        else:
            n_insertions = rng.integers(1, 3)

        insertion_budget = month_budget / n_insertions

        for _ in range(n_insertions):
            creative_counter += 1
            creative_id = f"PRT-CR-{creative_counter:04d}"

            pub = rng.choice(publications)
            edition = rng.choice(_PRINT_EDITIONS)
            fmt = rng.choice(_PRINT_FORMATS)
            fmt_mult = _PRINT_FORMAT_COST_MULT[fmt]

            # Rate card cost
            rate_card_base = rng.uniform(cost_range[0], cost_range[1])
            rate_card_cost = round(rate_card_base * fmt_mult, 2)

            # Negotiated cost: 50-70% of rate card
            discount = rng.uniform(0.50, 0.70)
            negotiated_cost = round(rate_card_cost * discount, 2)

            # Spend = negotiated cost
            spend = negotiated_cost

            # Circulation and readership
            circ = _PUBLICATION_CIRCULATION.get(pub, 30_000)
            circ = int(add_noise(circ, 0.05, rng))
            readership_mult = _READERSHIP_MULTIPLIER.get(pub, 4.0)
            readership_000 = int(round(circ * readership_mult / 1000))

            # Random day in month
            day = rng.integers(1, min(28, _DAYS_IN_MONTH_2025[month]) + 1)
            insertion_date = datetime.date(2025, month, day)

            # Page number
            page_number = int(rng.integers(3, 80))

            # Active models determine which model to feature
            active = get_active_models(insertion_date)
            if active:
                model_key = rng.choice(active)
                model = VEHICLE_MODELS[model_key]["display_name"]
            else:
                model = "DEEPAL S07"  # pre-launch still references main model

            rows.append({
                "date": date_to_str(insertion_date),
                "publication": pub,
                "edition": edition,
                "format": fmt,
                "market": "GB",
                "model": model,
                "rate_card_cost": rate_card_cost,
                "negotiated_cost": negotiated_cost,
                "spend": spend,
                "circulation": circ,
                "readership_000": readership_000,
                "page_number": page_number,
                "creative_id": creative_id,
            })

    df = pd.DataFrame(rows)
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Scale spend to hit annual budget target
    actual_total = df["spend"].sum()
    if actual_total > 0:
        scale = annual_budget / actual_total
        df["spend"] = (df["spend"] * scale).round(2)
        df["negotiated_cost"] = (df["negotiated_cost"] * scale).round(2)
        df["rate_card_cost"] = (df["rate_card_cost"] * scale).round(2)

    return df


# ═══════════════════════════════════════════════════════════════════════════
# 4. Radio Performance  (~60 rows — per-flight)
# ═══════════════════════════════════════════════════════════════════════════

_RADIO_DAYPARTS = {
    "Breakfast Drive": {"share": 0.60, "hours": "06:00-10:00"},
    "Daytime":         {"share": 0.15, "hours": "10:00-16:00"},
    "Drive Time":      {"share": 0.20, "hours": "16:00-19:00"},
    "Evening":         {"share": 0.05, "hours": "19:00-00:00"},
}

_STATION_GROUPS = {
    "Global": ["Capital FM", "Heart", "Classic FM", "Smooth Radio", "LBC"],
    "Bauer": ["talkSPORT"],
    "BBC": ["BBC Radio 5"],
}

_RADIO_REGIONS = list(_UK_REGIONS.keys())

_RADIO_CAMPAIGN_THEMES = [
    "S07 Launch", "Dealer Opening", "Test Drive Invite",
    "Price Announcement", "Year-End Offer", "S05 Preview",
    "Brand Awareness", "Conquest EV",
]


def _get_station_group(station: str) -> str:
    """Look up which group a station belongs to."""
    for group, stations in _STATION_GROUPS.items():
        if station in stations:
            return group
    return "Independent"


def _generate_radio() -> pd.DataFrame:
    """Generate radio_performance.csv."""
    rng = _rng_radio
    annual_budget = CHANNEL_BUDGETS_GBP["radio"]  # £400K
    monthly_budgets = distribute_budget_monthly(annual_budget)
    benchmarks = TRADITIONAL_BENCHMARKS["radio"]
    stations = benchmarks["stations"]
    cost_range = benchmarks["cost_per_spot_30s"]

    rows = []

    for month in range(1, 13):
        seasonal = SEASONAL_MULTIPLIERS[month]
        month_budget = monthly_budgets[month]

        if month_budget < 300:
            continue

        # Number of flights: regional focus around dealer openings — target ~60 rows
        if month in (9, 10):
            n_flights = rng.integers(8, 14)
        elif month in (7, 8, 11, 12):
            n_flights = rng.integers(5, 9)
        elif month in (3, 6):
            n_flights = rng.integers(2, 4)
        else:
            n_flights = rng.integers(1, 3)

        flight_budget = month_budget / n_flights

        for _ in range(n_flights):
            station = rng.choice(stations)
            station_group = _get_station_group(station)

            # Daypart
            dp_names = list(_RADIO_DAYPARTS.keys())
            dp_weights = [_RADIO_DAYPARTS[d]["share"] for d in dp_names]
            dp_weights = np.array(dp_weights) / sum(dp_weights)
            daypart = rng.choice(dp_names, p=dp_weights)
            dp_info = _RADIO_DAYPARTS[daypart]

            # Flight duration: 1-3 weeks
            flight_weeks = int(rng.choice([1, 2, 3], p=[0.3, 0.5, 0.2]))
            flight_days = flight_weeks * 7

            # Start date: random day in month
            max_start_day = max(1, _DAYS_IN_MONTH_2025[month] - flight_days)
            start_day = int(rng.integers(1, max_start_day + 1))
            start_date = datetime.date(2025, month, start_day)
            end_date = start_date + datetime.timedelta(days=flight_days - 1)
            if end_date > END_DATE:
                end_date = END_DATE

            # Spots per day (more for breakfast drive)
            if daypart == "Breakfast Drive":
                spots_per_day = int(rng.integers(8, 20))
            elif daypart == "Drive Time":
                spots_per_day = int(rng.integers(6, 15))
            else:
                spots_per_day = int(rng.integers(3, 10))

            total_spots = spots_per_day * flight_days

            # Cost per spot
            cost_per_spot = rng.uniform(cost_range[0], cost_range[1])
            # Adjust by daypart premium
            if daypart == "Breakfast Drive":
                cost_per_spot *= 1.4
            elif daypart == "Drive Time":
                cost_per_spot *= 1.2
            cost_per_spot = add_noise(cost_per_spot, 0.08, rng)

            spend = round(total_spots * cost_per_spot, 2)

            # Reach (000s) — regional station reach
            base_reach = rng.uniform(50, 400)  # thousands
            reach_000 = int(round(add_noise(base_reach * (total_spots / 50), 0.10, rng)))
            reach_000 = max(10, reach_000)

            # Frequency
            frequency = round(total_spots / max(1, reach_000 / 10), 1)
            frequency = max(1.0, min(frequency, 20.0))

            # CPM
            cpm = round(spend / max(1, reach_000) * 1000 / 1000, 2) if reach_000 > 0 else 0
            cpm = round(spend / (reach_000 * 1000) * 1000, 2) if reach_000 > 0 else 0

            region = rng.choice(_RADIO_REGIONS)
            theme = rng.choice(_RADIO_CAMPAIGN_THEMES)
            campaign_name = f"{theme} - {station} {region}"
            market = "GB"

            rows.append({
                "campaign_name": campaign_name,
                "start_date": date_to_str(start_date),
                "end_date": date_to_str(end_date),
                "station": station,
                "station_group": station_group,
                "market": market,
                "daypart": daypart,
                "spots_per_day": spots_per_day,
                "total_spots": total_spots,
                "reach_000": reach_000,
                "frequency": frequency,
                "cpm": cpm,
                "spend": spend,
                "region": region,
            })

    df = pd.DataFrame(rows)
    df.sort_values("start_date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Scale spend to hit annual budget target
    actual_total = df["spend"].sum()
    if actual_total > 0:
        scale = annual_budget / actual_total
        df["spend"] = (df["spend"] * scale).round(2)
        df["cpm"] = (df["cpm"] * scale).round(2)

    return df


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def generate() -> dict[str, pd.DataFrame]:
    """
    Generate all 4 traditional media CSV files and return DataFrames.

    Returns:
        dict mapping filename to DataFrame
    """
    datasets = {
        "tv_performance.csv": _generate_tv(),
        "ooh_performance.csv": _generate_ooh(),
        "print_performance.csv": _generate_print(),
        "radio_performance.csv": _generate_radio(),
    }

    for filename, df in datasets.items():
        path = os.path.join(RAW_DIR, filename)
        df.to_csv(path, index=False)
        print(f"  Wrote {path} ({len(df)} rows)")

    return datasets


# ═══════════════════════════════════════════════════════════════════════════
# Standalone execution
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("TRADITIONAL MEDIA DATA GENERATOR")
    print("=" * 60)

    results = generate()

    print("\n--- Verification ---")
    for filename, df in results.items():
        channel = filename.replace("_performance.csv", "")
        expected = CHANNEL_BUDGETS_GBP.get(channel, 0)
        actual = df["spend"].sum()
        pct_diff = abs(actual - expected) / expected * 100 if expected else 0
        print(f"  {filename:30s}  rows={len(df):>4d}  "
              f"spend=£{actual:>12,.2f}  target=£{expected:>12,}  "
              f"diff={pct_diff:.1f}%")

    print("\nDone.")
