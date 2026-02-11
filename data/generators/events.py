"""
Generate events calendar dataset.

Produces:
    data/raw/events.csv  (~15-17 rows, one per event)
"""

import os
import datetime
import numpy as np
import pandas as pd

from data.generators.config import (
    RAW_DIR,
    RANDOM_SEED,
    UK_EVENTS,
    SEASONAL_MULTIPLIERS,
    add_noise,
)


# ---------------------------------------------------------------------------
# Event metadata enrichment
# ---------------------------------------------------------------------------

_EVENT_LOCATIONS = {
    "motor_show": ["ExCeL London", "Goodwood Estate", "Farnborough", "NEC Birmingham"],
    "launch": ["Battersea Evolution, London", "Printworks, London", "The Shard, London"],
    "ev_show": ["Farnborough International", "ExCeL London"],
    "fleet": ["Silverstone Circuit", "NEC Birmingham"],
    "industry": ["Millbrook Proving Ground"],
    "tech": ["ExCeL London", "Olympia London"],
    "roadshow": None,  # location is in the event name
    "promo": ["National (online + dealer network)"],
}

_ROADSHOW_LOCATIONS = {
    "London": "Battersea Power Station, London",
    "Manchester": "MediaCityUK, Manchester",
    "Edinburgh": "Royal Highland Centre, Edinburgh",
    "Birmingham": "NEC Birmingham",
}

_EVENT_DESCRIPTIONS = {
    "London Motor Show": (
        "Major UK automotive showcase. DEEPAL/AVATR stand featuring S07 prototype "
        "display, configurator kiosks, and brand ambassadors. First UK public appearance."
    ),
    "Goodwood Festival of Speed": (
        "Prestige motorsport and automotive event. DEEPAL S07 hillclimb run, "
        "static display in Future Lab, VIP hospitality, media drives on track."
    ),
    "DEEPAL S07 UK Launch Event": (
        "Official UK market launch. Press conference, first customer handovers, "
        "dealer principal briefing, influencer experiences, live-streamed reveal."
    ),
    "Fully Charged Live": (
        "Leading EV consumer event. Product demos, expert talks on EV tech, "
        "test drive bookings, lead capture, partnership with Fully Charged media."
    ),
    "British Motor Show": (
        "National motor show open to public. Full stand build-out, S07 test drives, "
        "family-friendly activities, configurator stations, finance consultations."
    ),
    "Fleet Show": (
        "B2B fleet and leasing event. Corporate pricing presentations, fleet manager "
        "test drives, TCO analysis demos, Salary Sacrifice scheme showcase."
    ),
    "SMMT Test Day": (
        "Industry press event for automotive journalists. Pre-production S07 drives, "
        "engineering briefings, one-on-one interviews, embargo-lift coordination."
    ),
    "CES London (Tech)": (
        "Technology showcase positioning AVATR 12 as a tech-forward EV. AI assistant "
        "demo, autonomous features display, connected car ecosystem presentation."
    ),
    "AVATR 12 Reveal": (
        "Premium reveal event for AVATR 12 SUV. Exclusive venue, invitation-only "
        "press and VIP guests, design philosophy presentation, first drives."
    ),
    "AVATR 11 Reveal": (
        "AVATR 11 sedan UK debut. Executive audience, Huawei HarmonyOS demo, "
        "luxury positioning, comparison with BMW i5/Mercedes EQE."
    ),
    "DEEPAL S05 Preview": (
        "Pre-order event for DEEPAL S05 SUV-Coupe. Online livestream, early-bird "
        "reservation pricing, configurator launch, dealer allocation preview."
    ),
    "Dealer Launch Roadshow — London": (
        "South East dealer activation. Customer test drives, local media coverage, "
        "dealer staff certification, opening weekend celebration."
    ),
    "Dealer Launch Roadshow — Manchester": (
        "North West dealer activation. Community engagement, local influencer "
        "partnerships, test drive routes through Peak District."
    ),
    "Dealer Launch Roadshow — Edinburgh": (
        "Scotland dealer activation. Highlands test drive route, Scottish media "
        "engagement, partnership with local EV charging network."
    ),
    "Dealer Launch Roadshow — Birmingham": (
        "Midlands dealer activation. NEC proximity event, fleet customer demonstrations, "
        "M6 corridor visibility campaign tie-in."
    ),
    "Black Friday Sales Event": (
        "Limited-time digital promotional campaign with dealer support. Enhanced "
        "finance offers, deposit contribution, free home charger bundle."
    ),
    "Year-End Clearance": (
        "End of year sales push across all models. Fleet registrations, "
        "demonstrator clearance, Q1 2026 order incentives, S05 early reservations."
    ),
}

# Attendance and impression baselines by event type
_EVENT_BASELINES = {
    "motor_show": {"attendance": 80_000, "impressions": 15_000_000, "spend": 80_000,
                   "leads": 800, "test_drives": 200},
    "launch": {"attendance": 500, "impressions": 5_000_000, "spend": 120_000,
               "leads": 300, "test_drives": 50},
    "ev_show": {"attendance": 35_000, "impressions": 8_000_000, "spend": 55_000,
                "leads": 600, "test_drives": 150},
    "fleet": {"attendance": 8_000, "impressions": 2_000_000, "spend": 30_000,
              "leads": 250, "test_drives": 80},
    "industry": {"attendance": 500, "impressions": 3_000_000, "spend": 15_000,
                 "leads": 50, "test_drives": 30},
    "tech": {"attendance": 20_000, "impressions": 6_000_000, "spend": 45_000,
             "leads": 350, "test_drives": 0},
    "roadshow": {"attendance": 2_000, "impressions": 1_500_000, "spend": 25_000,
                 "leads": 200, "test_drives": 120},
    "promo": {"attendance": 0, "impressions": 10_000_000, "spend": 40_000,
              "leads": 1_500, "test_drives": 0},
}


def _get_location(event: dict) -> str:
    """Determine event location."""
    etype = event["type"]
    name = event["name"]

    if etype == "roadshow":
        for city, venue in _ROADSHOW_LOCATIONS.items():
            if city in name:
                return venue
        return "UK Dealer Network"

    locations = _EVENT_LOCATIONS.get(etype, ["London, UK"])
    if locations is None:
        return "London, UK"

    # Pick location based on event name hash for determinism
    idx = hash(name) % len(locations)
    return locations[idx]


def generate() -> dict:
    """
    Generate events calendar dataset.

    Returns:
        dict mapping filename to (DataFrame, output_path) tuple.
    """
    rng = np.random.default_rng(RANDOM_SEED + 600)
    rows = []

    total_spend = 0.0

    for event in UK_EVENTS:
        name = event["name"]
        start = datetime.datetime.strptime(event["date"], "%Y-%m-%d").date()
        end = start + datetime.timedelta(days=event["duration_days"] - 1)
        etype = event["type"]
        location = _get_location(event)

        baselines = _EVENT_BASELINES.get(etype, _EVENT_BASELINES["launch"])

        attendance = int(add_noise(baselines["attendance"], 0.15, rng)) if baselines["attendance"] > 0 else 0
        impressions = int(add_noise(baselines["impressions"], 0.20, rng))
        spend = round(add_noise(baselines["spend"], 0.10, rng), 2)
        leads = int(add_noise(baselines["leads"], 0.15, rng))
        test_drives = int(add_noise(baselines["test_drives"], 0.20, rng)) if baselines["test_drives"] > 0 else 0

        # Goodwood is the biggest event — scale up
        if "Goodwood" in name:
            attendance = int(attendance * 2.5)
            impressions = int(impressions * 2)
            spend = round(spend * 1.8, 2)
            leads = int(leads * 1.5)

        # Launch event is premium, high spend
        if "S07 UK Launch" in name:
            spend = round(spend * 1.5, 2)
            impressions = int(impressions * 2)

        total_spend += spend

        description = _EVENT_DESCRIPTIONS.get(name, f"{name} — brand activation event.")

        rows.append({
            "event_name": name,
            "event_type": etype,
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d"),
            "location": location,
            "market": "GB",
            "estimated_attendance": attendance,
            "media_impressions": impressions,
            "spend": spend,
            "leads_generated": leads,
            "test_drives_completed": test_drives,
            "description": description,
        })

    df = pd.DataFrame(rows)

    # Scale spend so total is approximately £600K
    target_total = 600_000
    if total_spend > 0:
        scale = target_total / total_spend
        df["spend"] = (df["spend"] * scale).round(2)

    path = os.path.join(RAW_DIR, "events.csv")
    df.to_csv(path, index=False)
    print(f"  [events] events.csv: {len(df)} rows -> {path}")
    print(f"  [events] Total events spend: £{df['spend'].sum():,.2f}")

    return {"events.csv": (df, path)}


if __name__ == "__main__":
    print("Generating events calendar...")
    results = generate()
    print(f"\nDone. Generated {len(results)} file(s).")
    for name, (df, path) in results.items():
        print(f"  {name}: {len(df)} rows, total spend: £{df['spend'].sum():,.2f}")
