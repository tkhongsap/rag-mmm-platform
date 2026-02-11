"""
Sales pipeline data generator.

Produces 5 CSVs with causal relationships to media spend:
  ad spend → website traffic → configurator → leads → test drives → sales

Reads actual media CSVs to model spend→traffic correlations.
"""

import datetime
import os
import re

import numpy as np
import pandas as pd

from data.generators.config import (
    RANDOM_SEED, RAW_DIR, DATE_RANGE, END_DATE, UK_LAUNCH_DATE,
    MARKETS, UK_DEALERS, VEHICLE_MODELS,
    SEASONAL_MULTIPLIERS, FINANCE_TYPES, FINANCE_DISTRIBUTION,
    DATE_FORMAT, get_active_models, is_pre_launch, get_trim_mix,
)
from data.generators._sales_helpers import (
    build_daily_spend_index, campaign_names_from_media,
    assign_lead_stage, build_lead_row, display_to_model_key, days_in_month,
    TD_OUTCOMES,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ANNUAL_SALES = {"GB": 2800, "DE": 1200, "FR": 600}
MODEL_SHARE = {"DEEPAL_S07": 0.70, "AVATR_12": 0.20, "AVATR_11": 0.08, "DEEPAL_S05": 0.02}

TRAFFIC_CHANNELS = ["organic_search", "paid_search", "social_paid", "social_organic",
                     "direct", "email", "referral", "display"]
DEVICES = ["desktop", "mobile", "tablet"]
DEVICE_WEIGHTS = [0.35, 0.55, 0.10]

CH_WEIGHTS = {"organic_search": 0.25, "paid_search": 0.20, "social_paid": 0.15,
              "social_organic": 0.08, "direct": 0.15, "email": 0.05,
              "referral": 0.05, "display": 0.07}


def _campaign_date_ok(name, session_dt):
    match = re.search(r'(\d{8})$', name)
    if not match:
        return True
    try:
        camp_dt = datetime.datetime.strptime(match.group(1), "%Y%m%d").date()
        return camp_dt <= session_dt
    except ValueError:
        return True


def _filter_campaigns_by_date(campaigns, session_date_str):
    session_dt = datetime.datetime.strptime(session_date_str, "%Y-%m-%d").date()
    filtered = [c for c in campaigns if _campaign_date_ok(c, session_dt)]
    return filtered if filtered else ["organic"]


def _gen_website_analytics(daily_spend: pd.Series) -> pd.DataFrame:
    """Generate website_analytics.csv (~5,000 rows): daily × channel × device."""
    rng = np.random.default_rng(RANDOM_SEED + 61)
    spend_norm = daily_spend.values.astype(float) / (daily_spend.values.mean() + 1e-6)
    rows = []
    for i, date_str in enumerate(daily_spend.index):
        dt = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        seasonal = SEASONAL_MULTIPLIERS[dt.month]
        base = rng.integers(10_000, 30_000) if is_pre_launch(dt) else rng.integers(80_000, 150_000)
        lag_d = spend_norm[max(0, i - 14):max(0, i - 6)]
        lag_t = spend_norm[max(0, i - 3):max(0, i)]
        effect = 0.5 + 0.3 * (float(np.mean(lag_d)) if len(lag_d) else 0.5) \
                     + 0.2 * (float(np.mean(lag_t)) if len(lag_t) else 0.5)
        daily_sessions = max(500, int(base * seasonal * effect))
        n_ch = rng.choice([5, 6], p=[0.4, 0.6])
        n_dv = rng.choice([2, 3], p=[0.45, 0.55])
        sel_ch = rng.choice(TRAFFIC_CHANNELS, size=n_ch, replace=False)
        sel_dv = rng.choice(DEVICES, size=n_dv, replace=False)
        combos = [(c, d) for c in sel_ch for d in sel_dv]
        wts = np.array([CH_WEIGHTS.get(c, 0.1) * DEVICE_WEIGHTS[DEVICES.index(d)] for c, d in combos])
        wts /= wts.sum()
        for (ch, dv), sess in zip(combos, rng.multinomial(daily_sessions, wts)):
            if sess < 10:
                continue
            rows.append({"date": date_str, "channel": ch, "device": dv,
                         "sessions": int(sess), "users": int(sess * rng.uniform(0.75, 0.95)),
                         "new_users": int(sess * rng.uniform(0.40, 0.70)),
                         "bounce_rate": round(rng.uniform(0.30, 0.70), 4),
                         "avg_session_duration_sec": round(
                             rng.uniform(40, 120) if ch == "social_paid" else
                             rng.uniform(30, 90) if ch == "social_organic" else
                             rng.uniform(60, 300), 1),
                         "pages_per_session": round(rng.uniform(1.5, 5.0), 2),
                         "configurator_starts": int(sess * rng.uniform(0.02, 0.05))})
    return pd.DataFrame(rows)


def _gen_configurator_sessions(website_df: pd.DataFrame, campaign_names: list) -> pd.DataFrame:
    """Generate configurator_sessions.csv (~12,000 rows): per-session."""
    rng = np.random.default_rng(RANDOM_SEED + 62)
    daily_starts = website_df.groupby("date")["configurator_starts"].sum()
    utm_src = ["google", "meta", "tiktok", "linkedin", "direct", "organic"]
    utm_med = ["cpc", "social", "display", "organic", "referral", "email"]
    scale = 12000 / max(daily_starts.sum(), 1)
    rows = []
    for date_str, starts in daily_starts.items():
        dt = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        active = get_active_models(dt) or ["DEEPAL_S07"]
        mw = np.array([MODEL_SHARE.get(m, 0.01) for m in active]); mw /= mw.sum()
        for _ in range(max(1, int(starts * scale))):
            model = rng.choice(active, p=mw)
            completed = rng.random() < rng.uniform(0.30, 0.40)
            rows.append({
                "session_id": f"CFG{len(rows)+1:06d}", "date": date_str,
                "model": VEHICLE_MODELS[model]["display_name"],
                "trim": rng.choice(list(VEHICLE_MODELS[model]["trims"].keys())),
                "device": rng.choice(DEVICES, p=DEVICE_WEIGHTS),
                "utm_source": rng.choice(utm_src), "utm_medium": rng.choice(utm_med),
                "utm_campaign": rng.choice(_filter_campaigns_by_date(campaign_names, date_str)) if rng.random() < 0.6 else "organic",
                "duration_sec": min(int(rng.lognormal(5.0, 0.8)), 3600),
                "steps_completed": int(rng.integers(5, 8) if completed else rng.integers(1, 8)),
                "completed": completed, "lead_submitted": completed and rng.random() < rng.uniform(0.08, 0.12),
                "market": rng.choice(list(MARKETS.keys()), p=[0.72, 0.20, 0.08])})
    return pd.DataFrame(rows)


def _gen_leads(config_df: pd.DataFrame) -> pd.DataFrame:
    """Generate leads.csv (~10,000 rows): per-lead with pipeline stages."""
    rng = np.random.default_rng(RANDOM_SEED + 63)
    dealer_ids = [d["dealer_id"] for d in UK_DEALERS]
    open_dates = {d["dealer_id"]: datetime.datetime.strptime(d["opening_date"], DATE_FORMAT).date()
                  for d in UK_DEALERS}
    other_src = ["website_organic", "dealer_walkin", "phone_enquiry", "live_chat",
                 "social_media", "referral", "event", "email_campaign"]
    source_weights = np.array([0.20, 0.15, 0.12, 0.08, 0.15, 0.12, 0.10, 0.08])
    source_weights /= source_weights.sum()
    rows = []

    def _pick_dealer(dt):
        avail = [d for d in dealer_ids if open_dates[d] <= dt]
        return rng.choice(avail if avail else dealer_ids[:5])

    # From configurator submissions
    for _, r in config_df[config_df["lead_submitted"]].iterrows():
        dt = datetime.datetime.strptime(r["date"], DATE_FORMAT).date()
        stage, sdate = assign_lead_stage(rng, dt)
        rows.append(build_lead_row(rng, len(rows), r["date"], "configurator",
                                   r["model"], _pick_dealer(dt), stage, sdate, r.get("market", "GB")))
    # Fill to target
    date_strs = [d.strftime(DATE_FORMAT) for d in DATE_RANGE]
    dwts = np.array([SEASONAL_MULTIPLIERS[d.month] for d in DATE_RANGE], dtype=float); dwts /= dwts.sum()
    for _ in range(max(0, 10000 - len(rows))):
        ds = rng.choice(date_strs, p=dwts)
        dt = datetime.datetime.strptime(ds, DATE_FORMAT).date()
        active = get_active_models(dt) or ["DEEPAL_S07"]
        mw = np.array([MODEL_SHARE.get(m, 0.01) for m in active]); mw /= mw.sum()
        model = rng.choice(active, p=mw)
        stage, sdate = assign_lead_stage(rng, dt)
        market = rng.choice(list(MARKETS.keys()), p=[0.72, 0.20, 0.08])
        rows.append(build_lead_row(rng, len(rows), ds, rng.choice(other_src, p=source_weights),
                                   VEHICLE_MODELS[model]["display_name"],
                                   _pick_dealer(dt), stage, sdate, market))
    return pd.DataFrame(rows)


def _gen_test_drives(leads_df: pd.DataFrame) -> pd.DataFrame:
    """Generate test_drives.csv (~8,000 rows): per-booking."""
    rng = np.random.default_rng(RANDOM_SEED + 64)
    td_stages = {"TD_BOOKED", "TD_COMPLETED", "NEGOTIATION", "WON"}
    rows = []

    def _td_row(lead, booking_str, rng_inst, conv_rate=None):
        dt = datetime.datetime.strptime(str(booking_str), DATE_FORMAT).date()
        td_dt = min(dt + datetime.timedelta(days=int(rng_inst.integers(1, 14))), END_DATE)
        outcome = rng_inst.choice(list(TD_OUTCOMES.keys()), p=list(TD_OUTCOMES.values()))
        cr = conv_rate or rng_inst.uniform(0.15, 0.25)
        return {"booking_id": f"TD{len(rows)+1:06d}", "lead_id": lead["lead_id"],
                "dealer_id": lead["dealer_id"], "booking_date": booking_str,
                "test_drive_date": td_dt.strftime(DATE_FORMAT), "model": lead["model"],
                "outcome": outcome,
                "duration_min": int(rng_inst.integers(15, 60)) if outcome == "completed" else 0,
                "converted_to_sale": outcome == "completed" and rng_inst.random() < cr,
                "market": lead["market"]}

    for _, ld in leads_df[leads_df["stage"].isin(td_stages)].iterrows():
        bk = ld["stage_updated_date"] if pd.notna(ld.get("stage_updated_date")) else ld["created_date"]
        rows.append(_td_row(ld, bk, rng))

    n_extra = max(0, 8000 - len(rows))
    if n_extra > 0:
        eligible = leads_df[~leads_df["stage"].isin({"NEW"} | td_stages)]
        if len(eligible) > 0:
            for _, ld in eligible.sample(n=n_extra, random_state=RANDOM_SEED + 65, replace=True).iterrows():
                rows.append(_td_row(ld, ld["created_date"], rng, conv_rate=0.18))
    return pd.DataFrame(rows)


def _gen_vehicle_sales(td_df: pd.DataFrame, leads_df: pd.DataFrame) -> pd.DataFrame:
    """Generate vehicle_sales.csv (~4,600 rows): no sales before Sep 2025."""
    rng = np.random.default_rng(RANDOM_SEED + 65)
    dealer_ids = [d["dealer_id"] for d in UK_DEALERS]
    open_dates = {d["dealer_id"]: datetime.datetime.strptime(d["opening_date"], DATE_FORMAT).date()
                  for d in UK_DEALERS}
    month_wts = {9: 0.35, 10: 0.30, 11: 0.20, 12: 0.15}

    # Blend structural month weights with actual media spend (70/30)
    daily_spend = build_daily_spend_index()
    spend_by_month = {}
    for date_str, spend_val in daily_spend.items():
        dt = datetime.datetime.strptime(date_str, DATE_FORMAT).date()
        if dt.month in month_wts:
            spend_by_month[dt.month] = spend_by_month.get(dt.month, 0.0) + spend_val
    total_spend = sum(spend_by_month.get(m, 0.0) for m in month_wts)
    if total_spend > 0:
        for m in month_wts:
            spend_prop = spend_by_month.get(m, 0.0) / total_spend
            month_wts[m] = 0.70 * month_wts[m] + 0.30 * spend_prop
        wt_sum = sum(month_wts.values())
        month_wts = {m: w / wt_sum for m, w in month_wts.items()}

    rows = []

    for _, td in td_df[td_df["converted_to_sale"]].iterrows():
        td_dt = datetime.datetime.strptime(td["test_drive_date"], DATE_FORMAT).date()
        sale_dt = td_dt + datetime.timedelta(days=int(rng.integers(3, 90)))
        # Skip weekends with 40% probability → ~40% fewer weekend sales
        if sale_dt.weekday() >= 5 and rng.random() < 0.40:
            sale_dt -= datetime.timedelta(days=(sale_dt.weekday() - 4))  # move to Friday
        if sale_dt > END_DATE or sale_dt < UK_LAUNCH_DATE:
            continue
        mk = display_to_model_key(td["model"])
        if mk is None:
            continue
        tmix = get_trim_mix(mk); trim = rng.choice(list(tmix.keys()), p=list(tmix.values()))
        rows.append({"sale_id": "", "date": sale_dt.strftime(DATE_FORMAT), "model": td["model"],
                     "trim": trim, "dealer_id": td["dealer_id"], "market": td["market"],
                     "price_gbp": VEHICLE_MODELS[mk]["trims"][trim]["price_gbp"],
                     "finance_type": rng.choice(FINANCE_TYPES, p=list(FINANCE_DISTRIBUTION.values())),
                     "lead_id": td["lead_id"], "source": "test_drive"})

    for market, target in ANNUAL_SALES.items():
        n_have = sum(1 for r in rows if r["market"] == market)
        for _ in range(max(0, target - n_have)):
            month = rng.choice(list(month_wts.keys()), p=list(month_wts.values()))
            sale_dt = datetime.date(2025, month, int(rng.integers(1, days_in_month(month) + 1)))
            # Skip weekends with 40% probability → ~40% fewer weekend sales
            if sale_dt.weekday() >= 5 and rng.random() < 0.40:
                sale_dt -= datetime.timedelta(days=(sale_dt.weekday() - 4))  # move to Friday
            active = get_active_models(sale_dt)
            if not active:
                continue
            mw = np.array([MODEL_SHARE.get(m, 0.01) for m in active]); mw /= mw.sum()
            mk = rng.choice(active, p=mw)
            tmix = get_trim_mix(mk); trim = rng.choice(list(tmix.keys()), p=list(tmix.values()))
            avail = [d for d in dealer_ids if open_dates[d] <= sale_dt]
            rows.append({"sale_id": "", "date": sale_dt.strftime(DATE_FORMAT),
                         "model": VEHICLE_MODELS[mk]["display_name"], "trim": trim,
                         "dealer_id": rng.choice(avail if avail else dealer_ids[:5]),
                         "market": market,
                         "price_gbp": VEHICLE_MODELS[mk]["trims"][trim]["price_gbp"],
                         "finance_type": rng.choice(FINANCE_TYPES, p=list(FINANCE_DISTRIBUTION.values())),
                         "lead_id": None,
                         "source": rng.choice(["dealer_walkin", "website", "referral", "event"])})

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    df["sale_id"] = [f"SL{i+1:06d}" for i in range(len(df))]
    return df


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate(web, cfg, leads, td, sales):
    print("\n--- Validation ---")
    for name, df, tgt in [("website_analytics", web, 5000), ("configurator_sessions", cfg, 12000),
                           ("leads", leads, 10000), ("test_drives", td, 8000), ("vehicle_sales", sales, 4600)]:
        print(f"{name}: {len(df)} rows (target ~{tgt})")
    lead_ids = set(leads["lead_id"])
    print(f"\nFK orphan test_drive lead_ids: {len(set(td['lead_id']) - lead_ids)}")
    valid_dlrs = {d['dealer_id'] for d in UK_DEALERS}
    for n, df in [("leads", leads), ("test_drives", td), ("sales", sales)]:
        print(f"FK invalid {n} dealer_ids: {len(set(df['dealer_id']) - valid_dlrs)}")
    if len(sales):
        print(f"\nEarliest sale: {pd.to_datetime(sales['date']).min().date()} (>= {UK_LAUNCH_DATE})")
        mc = sales["market"].value_counts()
        for m, t in ANNUAL_SALES.items():
            print(f"  {m}: {mc.get(m, 0)} (target ~{t})")
    ts = web["sessions"].sum(); cs = web["configurator_starts"].sum()
    print(f"\nFunnel: sessions={ts:,} → cfg_starts={cs:,} ({cs/max(ts,1)*100:.1f}%)")
    cc = cfg["completed"].sum()
    print(f"  cfg completion: {cc}/{len(cfg)} ({cc/max(len(cfg),1)*100:.1f}%)")
    tdc = (td["outcome"] == "completed").sum()
    print(f"  TD completion: {tdc}/{len(td)} ({tdc/max(len(td),1)*100:.1f}%)")
    conv = td["converted_to_sale"].sum()
    print(f"  TD→sale: {conv}/{tdc} ({conv/max(tdc,1)*100:.1f}%)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def generate():
    """Generate all 5 sales pipeline CSVs."""
    print("Loading media spend data...")
    daily_spend = build_daily_spend_index()
    campaigns = campaign_names_from_media()
    print(f"  {len(daily_spend)} days, total £{daily_spend.sum():,.0f}, {len(campaigns)} campaigns")

    for step, name, fn, args in [
        (1, "website_analytics", _gen_website_analytics, (daily_spend,)),
        (2, "configurator_sessions", _gen_configurator_sessions, None),
        (3, "leads", _gen_leads, None),
        (4, "test_drives", _gen_test_drives, None),
        (5, "vehicle_sales", _gen_vehicle_sales, None),
    ]:
        print(f"\n{step}/5 Generating {name}.csv...")
        if step == 1:
            web = fn(daily_spend)
            web.to_csv(os.path.join(RAW_DIR, f"{name}.csv"), index=False)
            print(f"  → {len(web)} rows")
        elif step == 2:
            cfg = fn(web, campaigns)
            cfg.to_csv(os.path.join(RAW_DIR, f"{name}.csv"), index=False)
            print(f"  → {len(cfg)} rows")
        elif step == 3:
            leads = fn(cfg)
            leads.to_csv(os.path.join(RAW_DIR, f"{name}.csv"), index=False)
            print(f"  → {len(leads)} rows")
        elif step == 4:
            td = fn(leads)
            td.to_csv(os.path.join(RAW_DIR, f"{name}.csv"), index=False)
            print(f"  → {len(td)} rows")
        elif step == 5:
            sales = fn(td, leads)
            sales.to_csv(os.path.join(RAW_DIR, f"{name}.csv"), index=False)
            print(f"  → {len(sales)} rows")

    _validate(web, cfg, leads, td, sales)
    print("\nSales pipeline generation complete.")


if __name__ == "__main__":
    generate()
