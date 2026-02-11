"""
Master configuration module for synthetic data generation.

All shared constants, parameters, helper functions, dealer data,
campaign templates, and seasonal multipliers for the DEEPAL/AVATR
UK launch synthetic dataset.

Every other generator module imports from this file.
"""

import os
import datetime
from typing import List, Dict, Optional

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
RNG = np.random.default_rng(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CONTRACTS_DIR = os.path.join(RAW_DIR, "contracts")
MMM_DIR = os.path.join(DATA_DIR, "mmm")
GENERATORS_DIR = os.path.join(DATA_DIR, "generators")

# Ensure output directories exist
for _d in [RAW_DIR, CONTRACTS_DIR, MMM_DIR]:
    os.makedirs(_d, exist_ok=True)

# ---------------------------------------------------------------------------
# Date Range
# ---------------------------------------------------------------------------
START_DATE = datetime.date(2025, 1, 1)
END_DATE = datetime.date(2025, 12, 31)
UK_LAUNCH_DATE = datetime.date(2025, 9, 1)   # DEEPAL S07 launch
S05_PREVIEW_DATE = datetime.date(2025, 12, 1)  # DEEPAL S05 preview/pre-order
AVATR_12_LAUNCH = datetime.date(2025, 9, 1)
AVATR_11_LAUNCH = datetime.date(2025, 10, 1)

DATE_RANGE = pd.date_range(START_DATE, END_DATE, freq="D")
NUM_DAYS = len(DATE_RANGE)

# ISO 8601 date format
DATE_FORMAT = "%Y-%m-%d"

# ---------------------------------------------------------------------------
# Markets & Budget Split
# ---------------------------------------------------------------------------
MARKETS = {
    "GB": {"name": "United Kingdom", "budget_share": 0.72, "currency": "GBP"},
    "DE": {"name": "Germany", "budget_share": 0.20, "currency": "EUR"},
    "FR": {"name": "France", "budget_share": 0.08, "currency": "EUR"},
}

PRIMARY_MARKET = "GB"

# Total annual budget for UK (GBP)
UK_TOTAL_ANNUAL_BUDGET = 20_000_000  # £20M

# ---------------------------------------------------------------------------
# Vehicle Models
# ---------------------------------------------------------------------------
VEHICLE_MODELS = {
    "DEEPAL_S07": {
        "display_name": "DEEPAL S07",
        "type": "SUV",
        "available_from": datetime.date(2025, 9, 1),
        "is_main_launch": True,
        "trims": {
            "Pure": {"price_gbp": 27_990, "price_eur": 32_490},
            "Design": {"price_gbp": 31_990, "price_eur": 37_190},
            "Intelligence": {"price_gbp": 35_990, "price_eur": 41_790},
        },
    },
    "DEEPAL_S05": {
        "display_name": "DEEPAL S05",
        "type": "SUV-Coupe",
        "available_from": datetime.date(2025, 12, 1),
        "is_main_launch": False,
        "trims": {
            "Pure": {"price_gbp": 24_990, "price_eur": 28_990},
            "Design": {"price_gbp": 28_990, "price_eur": 33_690},
        },
    },
    "AVATR_12": {
        "display_name": "AVATR 12",
        "type": "Premium SUV",
        "available_from": datetime.date(2025, 9, 1),
        "is_main_launch": False,
        "trims": {
            "Long Range": {"price_gbp": 54_990, "price_eur": 63_990},
            "Performance": {"price_gbp": 64_990, "price_eur": 75_490},
        },
    },
    "AVATR_11": {
        "display_name": "AVATR 11",
        "type": "Premium Sedan",
        "available_from": datetime.date(2025, 10, 1),
        "is_main_launch": False,
        "trims": {
            "Executive": {"price_gbp": 59_990, "price_eur": 69_790},
            "Executive Plus": {"price_gbp": 69_990, "price_eur": 81_390},
        },
    },
}

# ---------------------------------------------------------------------------
# Channel Budgets (UK Annual, GBP)
# ---------------------------------------------------------------------------
CHANNEL_BUDGETS_GBP = {
    "tv":       6_000_000,
    "ooh":      3_000_000,
    "youtube":  2_400_000,
    "meta":     2_200_000,
    "google":   1_800_000,
    "dv360":    1_400_000,
    "tiktok":   1_000_000,
    "linkedin":   600_000,
    "print":      600_000,
    "radio":      400_000,
    "events":     600_000,
}

assert sum(CHANNEL_BUDGETS_GBP.values()) == UK_TOTAL_ANNUAL_BUDGET, (
    f"Channel budgets sum to {sum(CHANNEL_BUDGETS_GBP.values()):,}, expected {UK_TOTAL_ANNUAL_BUDGET:,}"
)

# Group channels by type for convenience
DIGITAL_CHANNELS = ["youtube", "meta", "google", "dv360", "tiktok", "linkedin"]
TRADITIONAL_CHANNELS = ["tv", "ooh", "print", "radio"]
EVENT_CHANNELS = ["events"]
ALL_CHANNELS = DIGITAL_CHANNELS + TRADITIONAL_CHANNELS + EVENT_CHANNELS

# ---------------------------------------------------------------------------
# Seasonal Multipliers (monthly index, 1.0 = average)
# ---------------------------------------------------------------------------
SEASONAL_MULTIPLIERS = {
    1:  0.30,   # Jan — post-holiday quiet
    2:  0.30,   # Feb — quiet
    3:  0.40,   # Mar — spring plate change
    4:  0.35,   # Apr — early spring
    5:  0.40,   # May — pre-summer
    6:  0.50,   # Jun — summer ramp-up
    7:  0.70,   # Jul — summer activity
    8:  0.90,   # Aug — pre-launch build
    9:  2.50,   # Sep — LAUNCH MONTH
    10: 1.80,   # Oct — post-launch momentum
    11: 1.20,   # Nov — sustained push
    12: 0.80,   # Dec — S05 preview + year-end
}

# Normalised so that weighted mean across months ≈ 1.0
_seasonal_sum = sum(SEASONAL_MULTIPLIERS.values())
_seasonal_mean = _seasonal_sum / 12.0

# Pre-compute days-in-month weights for budget distribution
_DAYS_IN_MONTH_2025 = {m: (datetime.date(2025, m + 1, 1) - datetime.date(2025, m, 1)).days
                       if m < 12 else 31 for m in range(1, 13)}

# ---------------------------------------------------------------------------
# UK Dealer Network (50 dealers)
# ---------------------------------------------------------------------------
_DEALER_GROUPS = [
    "Lookers", "Stoneacre", "Parks Motor Group", "Arnold Clark",
    "Pendragon", "Vertu Motors", "JCT600", "Sytner Group",
    "Inchcape", "Marshall Motor Group", "Jardine Motors",
    "Caffyns", "Listers Group", "Swansway Motor Group",
    "Snows Motor Group", "Hendy Group", "Bristol Street Motors",
    "Macklin Motors", "TrustFord", "Peter Vardy",
    "Devonshire Motors", "Robins & Day", "CarShop",
    "Motorpoint", "Evans Halshaw", "Charles Hurst",
    "Hartwell", "Lloyd Motor Group", "Mercedes-Benz Retail",
    "Stephen James Group",
]

_UK_REGIONS = {
    "London": ["Central London", "Croydon", "Stratford", "Enfield", "Bromley"],
    "South East": ["Brighton", "Reading", "Guildford", "Milton Keynes", "Oxford"],
    "South West": ["Bristol", "Exeter", "Plymouth", "Bath", "Swindon"],
    "Midlands": ["Birmingham", "Coventry", "Nottingham", "Leicester", "Derby"],
    "North West": ["Manchester", "Liverpool", "Chester", "Preston", "Bolton"],
    "North East": ["Newcastle", "Leeds", "Sheffield", "York", "Hull"],
    "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee", "Inverness"],
    "Wales": ["Cardiff", "Swansea", "Newport"],
    "East Anglia": ["Cambridge", "Norwich", "Ipswich"],
    "Northern Ireland": ["Belfast", "Derry"],
}

_REGION_LIST = list(_UK_REGIONS.keys())
_CITIES_FLAT = [(region, city) for region, cities in _UK_REGIONS.items() for city in cities]


def _generate_dealers() -> List[Dict]:
    """Generate 50 realistic UK dealer entries."""
    rng = np.random.default_rng(RANDOM_SEED + 1)
    dealers = []

    # Pre-select ~15 launch dealers
    launch_indices = set(rng.choice(50, size=15, replace=False))

    for i in range(50):
        dealer_id = f"DLR{i + 1:03d}"

        # Assign dealer group (cycle through, some groups get multiple locations)
        group = _DEALER_GROUPS[i % len(_DEALER_GROUPS)]

        # Assign region/city
        region, city = _CITIES_FLAT[i % len(_CITIES_FLAT)]

        is_launch = i in launch_indices

        # Opening date: launch dealers open with launch, others open later
        if is_launch:
            open_offset = rng.integers(0, 14)  # 0-13 days around launch
            opening_date = UK_LAUNCH_DATE + datetime.timedelta(days=int(open_offset))
        else:
            open_offset = rng.integers(14, 90)  # 2 weeks to 3 months after launch
            opening_date = UK_LAUNCH_DATE + datetime.timedelta(days=int(open_offset))

        dealers.append({
            "dealer_id": dealer_id,
            "dealer_group": group,
            "dealer_name": f"{group} {city}",
            "region": region,
            "city": city,
            "is_launch_dealer": is_launch,
            "opening_date": opening_date.strftime(DATE_FORMAT),
            "capacity_units_month": int(rng.integers(10, 40)),
        })

    return dealers


UK_DEALERS = _generate_dealers()
UK_DEALER_DF = pd.DataFrame(UK_DEALERS)
NUM_DEALERS = len(UK_DEALERS)
NUM_LAUNCH_DEALERS = sum(1 for d in UK_DEALERS if d["is_launch_dealer"])

# ---------------------------------------------------------------------------
# Campaign Name Templates
# ---------------------------------------------------------------------------
CAMPAIGN_TEMPLATES = {
    "meta": {
        "awareness": "META_{market}_{model}_AWR_{audience}_{date}",
        "consideration": "META_{market}_{model}_CON_{audience}_{date}",
        "conversion": "META_{market}_{model}_CVR_{audience}_{date}",
        "retargeting": "META_{market}_{model}_RTG_{audience}_{date}",
    },
    "google": {
        "search_brand": "GOOG_{market}_{model}_SRC_BRAND_{date}",
        "search_generic": "GOOG_{market}_{model}_SRC_GEN_{date}",
        "pmax": "GOOG_{market}_{model}_PMAX_{date}",
        "display": "GOOG_{market}_{model}_GDN_{audience}_{date}",
    },
    "dv360": {
        "prospecting": "DV360_{market}_{model}_PROSP_{audience}_{date}",
        "retargeting": "DV360_{market}_{model}_RTG_{audience}_{date}",
        "contextual": "DV360_{market}_{model}_CTX_{placement}_{date}",
    },
    "tiktok": {
        "awareness": "TT_{market}_{model}_AWR_{creative}_{date}",
        "traffic": "TT_{market}_{model}_TRF_{creative}_{date}",
        "conversion": "TT_{market}_{model}_CVR_{creative}_{date}",
    },
    "youtube": {
        "trueview": "YT_{market}_{model}_TRV_{creative}_{date}",
        "bumper": "YT_{market}_{model}_BMP_{creative}_{date}",
        "masthead": "YT_{market}_{model}_MST_{date}",
        "shorts": "YT_{market}_{model}_SHT_{creative}_{date}",
    },
    "linkedin": {
        "awareness": "LI_{market}_{model}_AWR_{audience}_{date}",
        "lead_gen": "LI_{market}_{model}_LGN_{audience}_{date}",
        "thought_leadership": "LI_{market}_{model}_THL_{date}",
    },
    "tv": {
        "spot_30": "TV_{market}_{model}_30S_{region}_{date}",
        "spot_60": "TV_{market}_{model}_60S_{region}_{date}",
        "sponsorship": "TV_{market}_{model}_SPONS_{programme}_{date}",
    },
}

# Audience segments used in campaign names
AUDIENCE_SEGMENTS = [
    "EV_INTENDERS", "PREMIUM_AUTO", "TECH_ENTHUSIASTS",
    "ECO_CONSCIOUS", "LUXURY_LIFESTYLE", "YOUNG_PROFESSIONALS",
    "FAMILY_BUYERS", "FLEET_MANAGERS", "CONQUEST_TESLA",
    "CONQUEST_BMW", "CONQUEST_AUDI", "LOOKALIKE_CONVERTERS",
    "SITE_VISITORS", "CONFIGURATOR_USERS", "ENGAGED_VIEWERS",
]

# Creative IDs used in campaign names
CREATIVE_IDS = [
    "HERO_LAUNCH", "PRODUCT_FEATURES", "LIFESTYLE", "TESTIMONIAL",
    "PRICE_REVEAL", "CONFIGURATOR_CTA", "DEALER_LOCATOR",
    "RESERVATION_CTA", "COMPARISON", "AWARD_WINNER",
]

# TV regions
TV_REGIONS = [
    "NATIONAL", "LONDON", "MIDLANDS", "NORTH_WEST",
    "SCOTLAND", "SOUTH_EAST", "YORKSHIRE",
]

# TV programmes for sponsorship
TV_PROGRAMMES = [
    "F1_HIGHLIGHTS", "TOP_GEAR", "GRAND_DESIGNS",
    "CHANNEL4_NEWS", "SKY_SPORTS", "ITV_DRAMA",
]

# ---------------------------------------------------------------------------
# Digital Metrics — Benchmark Ranges
# ---------------------------------------------------------------------------
DIGITAL_BENCHMARKS = {
    "meta": {
        "cpm": (3.5, 16.0),         # GBP
        "ctr": (0.008, 0.025),
        "cpc": (0.40, 1.80),
        "conversion_rate": (0.01, 0.04),
    },
    "google": {
        "cpm": (3.0, 10.0),
        "ctr": (0.02, 0.06),
        "cpc": (0.50, 3.50),
        "conversion_rate": (0.02, 0.06),
    },
    "dv360": {
        "cpm": (2.0, 8.0),
        "ctr": (0.003, 0.012),
        "cpc": (0.30, 1.50),
        "conversion_rate": (0.005, 0.02),
    },
    "tiktok": {
        "cpm": (4.0, 10.0),
        "ctr": (0.005, 0.018),
        "cpc": (0.30, 1.20),
        "conversion_rate": (0.008, 0.025),
    },
    "youtube": {
        "cpv": (0.02, 0.08),         # cost per view
        "view_rate": (0.25, 0.55),
        "cpm": (6.0, 15.0),
        "ctr": (0.004, 0.012),
    },
    "linkedin": {
        "cpm": (20.0, 45.0),
        "ctr": (0.003, 0.010),
        "cpc": (3.00, 8.00),
        "conversion_rate": (0.01, 0.035),
    },
}

# Weekend spend adjustment factors (fraction of weekday spend)
WEEKEND_SPEND_FACTORS = {
    "meta": 0.72, "google": 0.78, "dv360": 0.70,
    "tiktok": 0.82, "youtube": 0.85, "linkedin": 0.55,
}

# ---------------------------------------------------------------------------
# Traditional Media Benchmarks
# ---------------------------------------------------------------------------
TRADITIONAL_BENCHMARKS = {
    "tv": {
        "cpp_30s": (20_000, 45_000),    # cost per spot 30s (GBP)
        "cpp_60s": (35_000, 80_000),
        "reach_per_spot_pct": (0.8, 6.0),
        "frequency_target": (3.0, 6.0),
    },
    "ooh": {
        "cost_per_panel_week": (200, 2_000),
        "impressions_per_panel_day": (5_000, 50_000),
        "formats": ["6_SHEET", "48_SHEET", "96_SHEET", "DIGITAL_SCREEN", "BUS_SHELTER"],
    },
    "print": {
        "cost_per_page": (5_000, 30_000),
        "publications": [
            "Autocar", "What Car?", "Top Gear Magazine", "Auto Express",
            "CAR Magazine", "EVO", "The Sunday Times Driving",
            "Financial Times", "The Telegraph Motoring",
        ],
    },
    "radio": {
        "cost_per_spot_30s": (100, 800),
        "stations": [
            "Classic FM", "LBC", "talkSPORT", "Heart",
            "Capital FM", "Smooth Radio", "BBC Radio 5",
        ],
    },
}

# ---------------------------------------------------------------------------
# Sales Pipeline Parameters
# ---------------------------------------------------------------------------
LEAD_SOURCES = [
    "website_organic", "website_paid", "dealer_walkin", "phone_enquiry",
    "live_chat", "social_media", "referral", "event", "email_campaign",
    "configurator", "test_drive_booking",
]

PIPELINE_STAGES = [
    "new_lead", "qualified", "test_drive_booked", "test_drive_completed",
    "finance_application", "order_placed", "delivered",
]

STAGE_CONVERSION_RATES = {
    "new_lead": 1.00,
    "qualified": 0.45,
    "test_drive_booked": 0.30,
    "test_drive_completed": 0.25,
    "finance_application": 0.15,
    "order_placed": 0.10,
    "delivered": 0.08,
}

FINANCE_TYPES = ["PCP", "HP", "lease", "cash"]
FINANCE_DISTRIBUTION = {"PCP": 0.55, "HP": 0.15, "lease": 0.20, "cash": 0.10}

# ---------------------------------------------------------------------------
# External / Economic Data Parameters
# ---------------------------------------------------------------------------
UK_BANK_RATE_2025 = 4.5  # 4.5% base rate (percentage points)
UK_CPI_MONTHLY_RANGE = (0.001, 0.005)  # monthly CPI change
UK_CONSUMER_CONFIDENCE_RANGE = (-15, -5)  # GfK-style index

COMPETITOR_BRANDS = [
    "Tesla", "BMW", "Audi", "Mercedes-Benz", "Hyundai",
    "Kia", "Volvo", "Polestar", "BYD", "MG",
]

COMPETITOR_MONTHLY_SPEND_RANGE = {
    "Tesla": (800_000, 2_000_000),
    "BMW": (2_000_000, 4_000_000),
    "Audi": (1_500_000, 3_500_000),
    "Mercedes-Benz": (2_000_000, 4_000_000),
    "Hyundai": (800_000, 1_800_000),
    "Kia": (700_000, 1_500_000),
    "Volvo": (500_000, 1_200_000),
    "Polestar": (300_000, 800_000),
    "BYD": (400_000, 1_000_000),
    "MG": (600_000, 1_400_000),
}

# ---------------------------------------------------------------------------
# Events Calendar Parameters
# ---------------------------------------------------------------------------
UK_EVENTS = [
    {"name": "London Motor Show", "date": "2025-04-17", "duration_days": 4, "type": "motor_show"},
    {"name": "Goodwood Festival of Speed", "date": "2025-07-10", "duration_days": 4, "type": "motor_show"},
    {"name": "DEEPAL S07 UK Launch Event", "date": "2025-09-01", "duration_days": 3, "type": "launch"},
    {"name": "Fully Charged Live", "date": "2025-06-06", "duration_days": 3, "type": "ev_show"},
    {"name": "British Motor Show", "date": "2025-08-14", "duration_days": 4, "type": "motor_show"},
    {"name": "Fleet Show", "date": "2025-05-07", "duration_days": 2, "type": "fleet"},
    {"name": "SMMT Test Day", "date": "2025-03-04", "duration_days": 2, "type": "industry"},
    {"name": "CES London (Tech)", "date": "2025-10-15", "duration_days": 3, "type": "tech"},
    {"name": "AVATR 12 Reveal", "date": "2025-09-15", "duration_days": 1, "type": "launch"},
    {"name": "AVATR 11 Reveal", "date": "2025-10-20", "duration_days": 1, "type": "launch"},
    {"name": "DEEPAL S05 Preview", "date": "2025-12-01", "duration_days": 2, "type": "launch"},
    {"name": "Dealer Launch Roadshow — London", "date": "2025-09-05", "duration_days": 2, "type": "roadshow"},
    {"name": "Dealer Launch Roadshow — Manchester", "date": "2025-09-12", "duration_days": 2, "type": "roadshow"},
    {"name": "Dealer Launch Roadshow — Edinburgh", "date": "2025-09-19", "duration_days": 2, "type": "roadshow"},
    {"name": "Dealer Launch Roadshow — Birmingham", "date": "2025-09-26", "duration_days": 2, "type": "roadshow"},
    {"name": "Black Friday Sales Event", "date": "2025-11-28", "duration_days": 4, "type": "promo"},
    {"name": "Year-End Clearance", "date": "2025-12-15", "duration_days": 17, "type": "promo"},
]

# ---------------------------------------------------------------------------
# Adstock & Saturation Defaults
# ---------------------------------------------------------------------------
ADSTOCK_DECAY_RATES = {
    "tv":       0.85,
    "ooh":      0.70,
    "youtube":  0.60,
    "meta":     0.50,
    "google":   0.40,
    "dv360":    0.55,
    "tiktok":   0.45,
    "linkedin": 0.50,
    "print":    0.75,
    "radio":    0.65,
    "events":   0.80,
}

SATURATION_PARAMS = {
    "tv":       {"alpha": 0.6, "gamma": 0.4},
    "ooh":      {"alpha": 0.5, "gamma": 0.5},
    "youtube":  {"alpha": 0.7, "gamma": 0.3},
    "meta":     {"alpha": 0.65, "gamma": 0.35},
    "google":   {"alpha": 0.75, "gamma": 0.25},
    "dv360":    {"alpha": 0.6, "gamma": 0.4},
    "tiktok":   {"alpha": 0.7, "gamma": 0.3},
    "linkedin": {"alpha": 0.55, "gamma": 0.45},
    "print":    {"alpha": 0.45, "gamma": 0.55},
    "radio":    {"alpha": 0.5, "gamma": 0.5},
    "events":   {"alpha": 0.4, "gamma": 0.6},
}


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def get_seasonal_multiplier(date) -> float:
    """Return the seasonal multiplier for a given date."""
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
    if isinstance(date, datetime.datetime):
        date = date.date()
    return SEASONAL_MULTIPLIERS[date.month]


def get_daily_budget(channel: str, date) -> float:
    """
    Return the daily budget (GBP) for a channel on a specific date,
    accounting for seasonal weighting.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
    if isinstance(date, datetime.datetime):
        date = date.date()

    annual = CHANNEL_BUDGETS_GBP.get(channel.lower(), 0)
    month = date.month

    # Weighted share for this month: (multiplier * days_in_month) / total_weighted_days
    multiplier = SEASONAL_MULTIPLIERS[month]
    days_in_month = _DAYS_IN_MONTH_2025[month]

    total_weighted_days = sum(
        SEASONAL_MULTIPLIERS[m] * _DAYS_IN_MONTH_2025[m]
        for m in range(1, 13)
    )

    monthly_budget = annual * (multiplier * days_in_month) / total_weighted_days
    daily = monthly_budget / days_in_month
    return round(daily, 2)


def get_weekly_budget(channel: str, week_start) -> float:
    """
    Return the total weekly budget (GBP) for a channel starting on week_start.
    Sums daily budgets for 7 days from week_start.
    """
    if isinstance(week_start, str):
        week_start = datetime.datetime.strptime(week_start, DATE_FORMAT).date()
    if isinstance(week_start, datetime.datetime):
        week_start = week_start.date()

    total = 0.0
    for i in range(7):
        day = week_start + datetime.timedelta(days=i)
        if START_DATE <= day <= END_DATE:
            total += get_daily_budget(channel, day)
    return round(total, 2)


def apply_adstock(spend_series: pd.Series, decay_rate: float) -> pd.Series:
    """
    Apply geometric adstock transformation to a spend series.

    adstock[t] = spend[t] + decay_rate * adstock[t-1]
    """
    adstocked = np.zeros(len(spend_series))
    values = spend_series.values
    adstocked[0] = values[0]
    for t in range(1, len(values)):
        adstocked[t] = values[t] + decay_rate * adstocked[t - 1]
    return pd.Series(adstocked, index=spend_series.index, name=spend_series.name)


def apply_saturation(x: float, alpha: float = 0.6, gamma: float = 0.4) -> float:
    """
    Apply Hill-function saturation curve.

    saturation(x) = x^alpha / (x^alpha + gamma^alpha)
    """
    if x <= 0:
        return 0.0
    x_a = x ** alpha
    g_a = gamma ** alpha
    return x_a / (x_a + g_a)


def generate_campaign_name(
    channel: str,
    market: str = "GB",
    model: str = "S07",
    campaign_type: Optional[str] = None,
    date: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Generate a campaign name from templates.

    Args:
        channel: Channel key (meta, google, dv360, etc.)
        market: Market code (GB, DE, FR)
        model: Model short code (S07, S05, AVATR12, AVATR11)
        campaign_type: Campaign type key from CAMPAIGN_TEMPLATES
        date: Date string for the campaign name
        **kwargs: Additional template fields (audience, creative, region, etc.)
    """
    channel_lower = channel.lower()

    if channel_lower not in CAMPAIGN_TEMPLATES:
        # Fallback generic format
        parts = [channel.upper(), market, model]
        if campaign_type:
            parts.append(campaign_type.upper())
        if date:
            parts.append(date.replace("-", ""))
        return "_".join(parts)

    templates = CAMPAIGN_TEMPLATES[channel_lower]

    if campaign_type and campaign_type in templates:
        template = templates[campaign_type]
    else:
        # Use first available template
        template = list(templates.values())[0]

    # Build substitution dict
    subs = {
        "market": market,
        "model": model,
        "date": (date or "").replace("-", ""),
        "audience": kwargs.get("audience", RNG.choice(AUDIENCE_SEGMENTS)),
        "creative": kwargs.get("creative", RNG.choice(CREATIVE_IDS)),
        "region": kwargs.get("region", RNG.choice(TV_REGIONS)),
        "placement": kwargs.get("placement", "ROS"),
        "programme": kwargs.get("programme", RNG.choice(TV_PROGRAMMES)),
    }

    try:
        return template.format(**subs)
    except KeyError:
        return f"{channel.upper()}_{market}_{model}_{date or ''}"


def is_pre_launch(date) -> bool:
    """Return True if date is before the UK launch date (2025-09-01)."""
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
    if isinstance(date, datetime.datetime):
        date = date.date()
    return date < UK_LAUNCH_DATE


def get_active_models(date) -> List[str]:
    """
    Return list of vehicle model keys that are available/active on a given date.
    """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, DATE_FORMAT).date()
    if isinstance(date, datetime.datetime):
        date = date.date()

    active = []
    for model_key, info in VEHICLE_MODELS.items():
        if date >= info["available_from"]:
            active.append(model_key)
    return active


def get_market_budget(market: str) -> float:
    """Return total annual budget for a market (GBP-equivalent)."""
    share = MARKETS.get(market, {}).get("budget_share", 0)
    # Total group budget = UK / UK share
    total_group = UK_TOTAL_ANNUAL_BUDGET / MARKETS[PRIMARY_MARKET]["budget_share"]
    return round(total_group * share, 2)


def date_to_str(d) -> str:
    """Convert a date/datetime to ISO 8601 string."""
    if isinstance(d, datetime.datetime):
        d = d.date()
    return d.strftime(DATE_FORMAT)


def str_to_date(s: str) -> datetime.date:
    """Parse an ISO 8601 date string to datetime.date."""
    return datetime.datetime.strptime(s, DATE_FORMAT).date()


def add_noise(value: float, noise_pct: float = 0.10, rng_inst=None) -> float:
    """Add Gaussian noise to a value. noise_pct is std dev as fraction of value."""
    if rng_inst is None:
        rng_inst = RNG
    noise = rng_inst.normal(0, abs(value) * noise_pct)
    return max(0, value + noise)


def distribute_budget_monthly(annual_budget: float) -> Dict[int, float]:
    """
    Distribute an annual budget across months using seasonal multipliers.
    Returns dict {month_number: monthly_budget}.
    """
    total_weighted_days = sum(
        SEASONAL_MULTIPLIERS[m] * _DAYS_IN_MONTH_2025[m]
        for m in range(1, 13)
    )

    monthly = {}
    for m in range(1, 13):
        weight = SEASONAL_MULTIPLIERS[m] * _DAYS_IN_MONTH_2025[m]
        monthly[m] = round(annual_budget * weight / total_weighted_days, 2)
    return monthly


def get_trim_mix(model_key: str) -> Dict[str, float]:
    """Return expected trim mix proportions for a vehicle model."""
    trims = list(VEHICLE_MODELS[model_key]["trims"].keys())
    n = len(trims)
    if n == 3:
        # Entry-heavy distribution
        return {trims[0]: 0.50, trims[1]: 0.35, trims[2]: 0.15}
    elif n == 2:
        return {trims[0]: 0.60, trims[1]: 0.40}
    else:
        equal = 1.0 / n
        return {t: equal for t in trims}


# ---------------------------------------------------------------------------
# Validation Helpers
# ---------------------------------------------------------------------------

def validate_date_range(df: pd.DataFrame, date_col: str = "date") -> bool:
    """Check that all dates in a DataFrame fall within the configured range."""
    dates = pd.to_datetime(df[date_col]).dt.date
    return dates.min() >= START_DATE and dates.max() <= END_DATE


def validate_spend_total(df: pd.DataFrame, spend_col: str = "spend_gbp",
                         channel: Optional[str] = None,
                         tolerance: float = 0.05) -> bool:
    """
    Check that total spend in a DataFrame is within tolerance of expected budget.
    """
    actual = df[spend_col].sum()
    if channel:
        expected = CHANNEL_BUDGETS_GBP.get(channel.lower(), 0)
    else:
        expected = UK_TOTAL_ANNUAL_BUDGET

    if expected == 0:
        return actual == 0

    deviation = abs(actual - expected) / expected
    return deviation <= tolerance


# ---------------------------------------------------------------------------
# Module self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("SYNTHETIC DATA GENERATOR — MASTER CONFIG")
    print("=" * 60)
    print(f"\nDate range: {START_DATE} to {END_DATE} ({NUM_DAYS} days)")
    print(f"UK Launch:  {UK_LAUNCH_DATE}")
    print(f"S05 Preview: {S05_PREVIEW_DATE}")

    print(f"\n--- Markets ---")
    for code, info in MARKETS.items():
        budget = get_market_budget(code)
        print(f"  {code} ({info['name']}): {info['budget_share']:.0%} share = £{budget:,.0f}")

    print(f"\n--- Vehicle Models ---")
    for key, info in VEHICLE_MODELS.items():
        trims_str = ", ".join(
            f"{t} (£{p['price_gbp']:,})" for t, p in info["trims"].items()
        )
        print(f"  {info['display_name']}: from {info['available_from']} — {trims_str}")

    print(f"\n--- Channel Budgets (UK, GBP) ---")
    for ch, budget in sorted(CHANNEL_BUDGETS_GBP.items(), key=lambda x: -x[1]):
        print(f"  {ch:12s}: £{budget:>12,}")
    print(f"  {'TOTAL':12s}: £{sum(CHANNEL_BUDGETS_GBP.values()):>12,}")

    print(f"\n--- Seasonal Multipliers ---")
    for m, mult in SEASONAL_MULTIPLIERS.items():
        bar = "█" * int(mult * 20)
        print(f"  {datetime.date(2025, m, 1).strftime('%b'):3s}: {mult:.2f} {bar}")

    print(f"\n--- UK Dealers ---")
    print(f"  Total: {NUM_DEALERS}, Launch dealers: {NUM_LAUNCH_DEALERS}")
    print(f"  Sample: {UK_DEALERS[0]['dealer_name']} ({UK_DEALERS[0]['dealer_id']})")

    print(f"\n--- Helper Function Tests ---")
    test_date = datetime.date(2025, 9, 15)
    print(f"  Daily budget (TV, {test_date}): £{get_daily_budget('tv', test_date):,.2f}")
    print(f"  Weekly budget (Meta, {test_date}): £{get_weekly_budget('meta', test_date):,.2f}")
    print(f"  Is pre-launch ({test_date}): {is_pre_launch(test_date)}")
    print(f"  Active models ({test_date}): {get_active_models(test_date)}")
    print(f"  Campaign name: {generate_campaign_name('meta', 'GB', 'S07', 'awareness', '2025-09-15')}")

    # Verify budget distribution sums correctly
    tv_monthly = distribute_budget_monthly(CHANNEL_BUDGETS_GBP["tv"])
    print(f"\n  TV monthly distribution sum: £{sum(tv_monthly.values()):,.2f} (expected £{CHANNEL_BUDGETS_GBP['tv']:,})")

    print("\nConfig module loaded successfully.")
