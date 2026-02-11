"""
Digital media data generator.

Produces 6 CSV files for Meta, Google, DV360, TikTok, YouTube, and LinkedIn
advertising data. All constants are imported from the master config module.
"""

import datetime
import os
from typing import Dict, List

import numpy as np
import pandas as pd

from data.generators.config import (
    AUDIENCE_SEGMENTS,
    CAMPAIGN_TEMPLATES,
    CHANNEL_BUDGETS_GBP,
    CREATIVE_IDS,
    DATE_FORMAT,
    DATE_RANGE,
    DIGITAL_BENCHMARKS,
    PRIMARY_MARKET,
    RANDOM_SEED,
    RAW_DIR,
    VEHICLE_MODELS,
    WEEKEND_SPEND_FACTORS,
    distribute_budget_monthly,
    generate_campaign_name,
    get_active_models,
    is_pre_launch,
)

# ---------------------------------------------------------------------------
# Per-channel deterministic RNG (seed derived from master)
# ---------------------------------------------------------------------------
_SEED_OFFSETS = {
    "meta": 100, "google": 200, "dv360": 300,
    "tiktok": 400, "youtube": 500, "linkedin": 600,
}

# Rows per day: (pre_launch, post_launch) — tuned to hit target totals
# Pre-launch = Jan-Aug (243 days), Post-launch = Sep-Dec (122 days)
_ROWS_PER_DAY = {
    "meta": (10, 45),       # ~8,000
    "google": (10, 30),     # ~6,000
    "dv360": (7, 20),       # ~4,000
    "tiktok": (5, 15),      # ~3,000
    "youtube": (6, 20),     # ~4,000
    "linkedin": (3, 7),     # ~1,500
}


def _rng_for(channel: str) -> np.random.Generator:
    return np.random.default_rng(RANDOM_SEED + _SEED_OFFSETS[channel])


def _model_short(key: str) -> str:
    """DEEPAL_S07 -> S07, AVATR_12 -> AVATR12."""
    return key.replace("DEEPAL_", "").replace("AVATR_", "AVATR")


# ---------------------------------------------------------------------------
# Daily spend with ±15% noise, scaled to exact annual total
# ---------------------------------------------------------------------------
def _daily_channel_spend(channel: str, rng: np.random.Generator) -> np.ndarray:
    annual = CHANNEL_BUDGETS_GBP[channel]
    monthly = distribute_budget_monthly(annual)
    wknd_factor = WEEKEND_SPEND_FACTORS.get(channel, 1.0)
    raw = np.empty(len(DATE_RANGE))
    for i, dt in enumerate(DATE_RANGE):
        m = dt.month
        days_in_m = (pd.Timestamp(dt.year, m, 1) + pd.offsets.MonthEnd(0)).day
        base = monthly[m] / days_in_m
        base *= (1.0 + rng.uniform(-0.15, 0.15))
        # Scale down weekend spend (Sat=5, Sun=6)
        if dt.dayofweek >= 5:
            base *= wknd_factor
        raw[i] = max(0.0, base)
    return raw / raw.sum() * annual


# ---------------------------------------------------------------------------
# Campaign-row builder for a single day
# ---------------------------------------------------------------------------
def _day_campaigns(
    channel: str,
    n_rows: int,
    objectives: List[str],
    models: List[str],
    rng: np.random.Generator,
    date_str: str,
) -> List[Dict]:
    """Return *n_rows* campaign dicts, cycling through objectives and models."""
    camps = []
    for i in range(n_rows):
        obj = objectives[i % len(objectives)]
        mk = models[i % len(models)]
        aud = str(rng.choice(AUDIENCE_SEGMENTS))
        cre = str(rng.choice(CREATIVE_IDS))
        name = generate_campaign_name(
            channel, PRIMARY_MARKET, _model_short(mk), obj, date_str,
            audience=aud, creative=cre,
        )
        cid = f"{channel.upper()[:2]}{rng.integers(10000, 99999)}"
        camps.append({
            "campaign_name": name,
            "campaign_id": cid,
            "objective": obj,
            "model": VEHICLE_MODELS[mk]["display_name"],
            "model_key": mk,
        })
    return camps


# ===========================================================================
# Per-channel generators
# ===========================================================================

def _generate_meta(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("meta", rng)
    bm = DIGITAL_BENCHMARKS["meta"]
    all_obj = list(CAMPAIGN_TEMPLATES["meta"].keys())
    pre_obj = ["awareness"]
    platforms = ["Facebook", "Instagram"]
    pre_n, post_n = _ROWS_PER_DAY["meta"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("meta", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            platform = platforms[rng.integers(0, 2)]
            cpm = rng.uniform(*bm["cpm"])
            impressions = int(spend / cpm * 1000)
            if impressions <= 0:
                continue
            ctr = rng.uniform(*bm["ctr"])
            clicks = max(1, int(impressions * ctr))
            reach = int(impressions * rng.uniform(0.55, 0.85))
            freq = round(impressions / max(1, reach), 2)
            is_awr = "awareness" in camp["objective"]
            vviews = int(impressions * rng.uniform(0.15, 0.40)) if is_awr else 0
            vvr = round(vviews / impressions, 4) if vviews else 0.0
            is_conv = "conversion" in camp["objective"] or "retargeting" in camp["objective"]
            leads = int(clicks * rng.uniform(*bm["conversion_rate"])) if is_conv else 0
            cpl = round(spend / leads, 2) if leads > 0 else 0.0
            link_clicks = int(clicks * rng.uniform(0.70, 0.95))
            lpv = int(link_clicks * rng.uniform(0.60, 0.85))
            rows.append({
                "date": d_str, "campaign_name": camp["campaign_name"],
                "campaign_id": camp["campaign_id"], "platform": platform,
                "objective": camp["objective"], "market": PRIMARY_MARKET,
                "model": camp["model"], "impressions": impressions,
                "clicks": clicks, "ctr": round(clicks / impressions, 6),
                "cpm": round(cpm, 2), "cpc": round(spend / clicks, 2),
                "spend": round(spend, 2), "reach": reach, "frequency": freq,
                "video_views": vviews, "video_view_rate": vvr,
                "leads": leads, "link_clicks": link_clicks,
                "landing_page_views": lpv, "cost_per_lead": cpl,
            })
    return pd.DataFrame(rows)


def _generate_google(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("google", rng)
    bm = DIGITAL_BENCHMARKS["google"]
    all_obj = list(CAMPAIGN_TEMPLATES["google"].keys())
    pre_obj = ["search_brand"]
    kw_groups = ["brand_exact", "brand_broad", "ev_suv", "electric_car",
                 "competitor", "price", "review", "dealer", "test_drive"]
    pre_n, post_n = _ROWS_PER_DAY["google"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("google", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            is_brand = "brand" in camp["objective"]
            ctr_range = (0.05, 0.15) if is_brand else bm["ctr"]
            ctr = rng.uniform(*ctr_range)
            cpc = rng.uniform(*bm["cpc"])
            clicks = max(1, int(spend / cpc))
            impressions = max(clicks, int(clicks / ctr))
            conv_rate = rng.uniform(*bm["conversion_rate"])
            conversions = max(0, int(clicks * conv_rate))
            cpa = round(spend / conversions, 2) if conversions > 0 else 0.0
            qs = int(rng.uniform(5, 10)) if is_brand else int(rng.uniform(3, 8))
            obj = camp["objective"]
            ctype = ("Search" if "search" in obj
                     else "Performance Max" if "pmax" in obj else "Display")
            rows.append({
                "date": d_str, "campaign_name": camp["campaign_name"],
                "campaign_id": camp["campaign_id"], "campaign_type": ctype,
                "market": PRIMARY_MARKET, "model": camp["model"],
                "keyword_group": str(rng.choice(kw_groups)),
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions, 6),
                "avg_cpc": round(spend / clicks, 2),
                "spend": round(spend, 2), "conversions": conversions,
                "conversion_rate": round(conv_rate, 4),
                "cost_per_conversion": cpa, "quality_score": qs,
                "impression_share": round(rng.uniform(0.40, 0.85), 2),
                "search_impression_share": round(rng.uniform(0.30, 0.75), 2),
            })
    return pd.DataFrame(rows)


def _generate_dv360(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("dv360", rng)
    bm = DIGITAL_BENCHMARKS["dv360"]
    all_obj = list(CAMPAIGN_TEMPLATES["dv360"].keys())
    pre_obj = ["prospecting"]
    sizes = ["300x250", "728x90", "160x600", "320x50", "970x250"]
    exchanges = ["Google AdX", "Xandr", "Index Exchange", "PubMatic", "OpenX"]
    pre_n, post_n = _ROWS_PER_DAY["dv360"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("dv360", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            cpm = rng.uniform(*bm["cpm"])
            impressions = int(spend / cpm * 1000)
            if impressions <= 0:
                continue
            ctr = rng.uniform(*bm["ctr"])
            clicks = max(1, int(impressions * ctr))
            viewability = rng.uniform(0.70, 0.92)
            viewable_imp = int(impressions * viewability)
            has_video = rng.random() > 0.5
            vid_comp = int(impressions * rng.uniform(0.10, 0.30)) if has_video else 0
            vcr = round(vid_comp / impressions, 4) if vid_comp else 0.0
            rows.append({
                "date": d_str,
                "insertion_order": f"IO{rng.integers(1000, 9999)}",
                "line_item_name": camp["campaign_name"],
                "line_item_id": camp["campaign_id"],
                "market": PRIMARY_MARKET, "model": camp["model"],
                "creative_size": str(rng.choice(sizes)),
                "exchange": str(rng.choice(exchanges)),
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions, 6),
                "cpm": round(cpm, 2), "spend": round(spend, 2),
                "viewable_impressions": viewable_imp,
                "viewability_rate": round(viewability, 4),
                "video_completions": vid_comp,
                "video_completion_rate": vcr,
            })
    return pd.DataFrame(rows)


def _generate_tiktok(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("tiktok", rng)
    bm = DIGITAL_BENCHMARKS["tiktok"]
    all_obj = list(CAMPAIGN_TEMPLATES["tiktok"].keys())
    pre_obj = ["awareness"]
    pre_n, post_n = _ROWS_PER_DAY["tiktok"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("tiktok", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            cpm = rng.uniform(*bm["cpm"])
            impressions = int(spend / cpm * 1000)
            if impressions <= 0:
                continue
            ctr = rng.uniform(*bm["ctr"])
            clicks = max(1, int(impressions * ctr))
            vid_views = int(impressions * rng.uniform(0.40, 0.75))
            rows.append({
                "date": d_str, "campaign_name": camp["campaign_name"],
                "campaign_id": camp["campaign_id"],
                "objective": camp["objective"],
                "market": PRIMARY_MARKET, "model": camp["model"],
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions, 6),
                "cpm": round(cpm, 2), "spend": round(spend, 2),
                "video_views": vid_views,
                "video_view_rate": round(vid_views / impressions, 4),
                "avg_watch_time_seconds": round(rng.uniform(3.0, 15.0), 1),
                "shares": int(vid_views * rng.uniform(0.001, 0.008)),
                "comments": int(vid_views * rng.uniform(0.0005, 0.003)),
                "likes": int(vid_views * rng.uniform(0.005, 0.025)),
                "profile_visits": int(clicks * rng.uniform(0.05, 0.20)),
                "website_clicks": int(clicks * rng.uniform(0.30, 0.70)),
            })
    return pd.DataFrame(rows)


def _generate_youtube(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("youtube", rng)
    bm = DIGITAL_BENCHMARKS["youtube"]
    all_obj = list(CAMPAIGN_TEMPLATES["youtube"].keys())
    pre_obj = ["trueview", "bumper"]
    fmt_labels = {"trueview": "TrueView In-Stream", "bumper": "Bumper 6s",
                  "masthead": "Masthead", "shorts": "YouTube Shorts"}
    pre_n, post_n = _ROWS_PER_DAY["youtube"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("youtube", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            cpm = rng.uniform(*bm["cpm"])
            impressions = int(spend / cpm * 1000)
            if impressions <= 0:
                continue
            view_rate = rng.uniform(*bm["view_rate"])
            views = int(impressions * view_rate)
            ctr = rng.uniform(*bm["ctr"])
            clicks = max(1, int(impressions * ctr))
            cpv = spend / max(1, views)
            p25 = int(views * rng.uniform(0.85, 0.95))
            p50 = int(p25 * rng.uniform(0.70, 0.85))
            p75 = int(p50 * rng.uniform(0.65, 0.80))
            p100 = int(p75 * rng.uniform(0.55, 0.75))
            earned_views = int(views * rng.uniform(0.01, 0.06))
            earned_subs = int(earned_views * rng.uniform(0.001, 0.01))
            rows.append({
                "date": d_str, "campaign_name": camp["campaign_name"],
                "campaign_id": camp["campaign_id"],
                "format": fmt_labels.get(camp["objective"], camp["objective"]),
                "market": PRIMARY_MARKET, "model": camp["model"],
                "impressions": impressions, "views": views,
                "view_rate": round(view_rate, 4), "clicks": clicks,
                "ctr": round(clicks / impressions, 6),
                "cpv": round(cpv, 4), "cpm": round(cpm, 2),
                "spend": round(spend, 2),
                "video_played_25": p25, "video_played_50": p50,
                "video_played_75": p75, "video_played_100": p100,
                "earned_views": earned_views,
                "earned_subscribers": earned_subs,
            })
    return pd.DataFrame(rows)


def _generate_linkedin(rng: np.random.Generator) -> pd.DataFrame:
    spend_arr = _daily_channel_spend("linkedin", rng)
    bm = DIGITAL_BENCHMARKS["linkedin"]
    all_obj = list(CAMPAIGN_TEMPLATES["linkedin"].keys())
    pre_obj = ["awareness"]
    pre_n, post_n = _ROWS_PER_DAY["linkedin"]
    rows: list = []

    for idx, dt in enumerate(DATE_RANGE):
        d_str = dt.strftime(DATE_FORMAT)
        pre = is_pre_launch(dt)
        objectives = pre_obj if pre else all_obj
        models = get_active_models(dt) or ["DEEPAL_S07"]
        n = pre_n if pre else post_n
        camps = _day_campaigns("linkedin", n, objectives, models, rng, d_str)
        splits = rng.dirichlet(np.ones(n))
        for camp, share in zip(camps, splits):
            spend = spend_arr[idx] * share
            cpm = rng.uniform(*bm["cpm"])
            impressions = int(spend / cpm * 1000)
            if impressions <= 0:
                continue
            ctr = rng.uniform(*bm["ctr"])
            clicks = max(1, int(impressions * ctr))
            is_lead = "lead" in camp["objective"]
            leads = int(clicks * rng.uniform(*bm["conversion_rate"])) if is_lead else 0
            cpl = round(spend / leads, 2) if leads > 0 else 0.0
            social_actions = int(impressions * rng.uniform(0.001, 0.005))
            rows.append({
                "date": d_str, "campaign_name": camp["campaign_name"],
                "campaign_id": camp["campaign_id"],
                "objective": camp["objective"],
                "market": PRIMARY_MARKET, "model": camp["model"],
                "impressions": impressions, "clicks": clicks,
                "ctr": round(clicks / impressions, 6),
                "cpm": round(cpm, 2),
                "cpc": round(spend / clicks, 2),
                "spend": round(spend, 2), "leads": leads,
                "cost_per_lead": cpl, "social_actions": social_actions,
                "follower_gains": int(social_actions * rng.uniform(0.02, 0.10)),
                "company_page_clicks": int(clicks * rng.uniform(0.05, 0.15)),
            })
    return pd.DataFrame(rows)


# ===========================================================================
# Public entry point
# ===========================================================================

_GENERATORS = {
    "meta_ads": ("meta", _generate_meta),
    "google_ads": ("google", _generate_google),
    "dv360": ("dv360", _generate_dv360),
    "tiktok_ads": ("tiktok", _generate_tiktok),
    "youtube_ads": ("youtube", _generate_youtube),
    "linkedin_ads": ("linkedin", _generate_linkedin),
}


def generate() -> Dict[str, pd.DataFrame]:
    """Generate all 6 digital media CSV files and return DataFrames."""
    results = {}
    for filename, (channel, gen_func) in _GENERATORS.items():
        rng = _rng_for(channel)
        df = gen_func(rng)
        path = os.path.join(RAW_DIR, f"{filename}.csv")
        df.to_csv(path, index=False)
        expected = CHANNEL_BUDGETS_GBP[channel]
        actual = df["spend"].sum()
        pct = abs(actual - expected) / expected * 100
        print(f"  {filename + '.csv':<20s}  rows={len(df):>6,}  "
              f"spend=£{actual:>12,.2f}  budget=£{expected:>12,.0f}  "
              f"diff={pct:.2f}%")
        results[filename] = df
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("DIGITAL MEDIA DATA GENERATOR")
    print("=" * 70)
    dfs = generate()
    print("-" * 70)
    total_spend = sum(df["spend"].sum() for df in dfs.values())
    total_rows = sum(len(df) for df in dfs.values())
    print(f"  TOTAL: {total_rows:,} rows, £{total_spend:,.2f} spend")
    print("Done.")
