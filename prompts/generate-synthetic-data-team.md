# Agent Team Prompt: Synthetic Data Generation for RAG-MMM Platform

> **Purpose**: This prompt spawns a 6-agent team to generate 20 synthetic datasets (~63K CSV rows + 7 contract documents) for the RAG-MMM platform. The data represents a fictional Chinese EV brand (DEEPAL/AVATR) launching in UK, Germany, and France during 2025.
>
> **Do not execute this prompt directly.** Use it as the input when you're ready to spawn the agent team via Claude Code's `TeamCreate` + `Task` tools.

---

## Pre-flight Checklist

Before launching the team, complete these setup steps:

### 1. Configure tmux split-pane monitoring

Use tmux so you can watch all 6 agents working simultaneously in separate panes.

```bash
# Start a new tmux session
tmux new -s synth-data

# The recommended layout: 3 rows x 2 columns (6 panes)
# tmux will manage pane splitting automatically when using teammateMode: "tmux"
```

### 2. Set Claude Code teammate mode

Ensure your Claude Code settings enable tmux-based teammates. In your project or user settings (`.claude/settings.json`), set:

```json
{
  "teammateMode": "tmux"
}
```

This tells Claude Code to spawn each teammate in a separate tmux pane, giving you real-time visibility into all agents.

### 3. Verify directory structure

```bash
# These directories must exist (the config-engineer agent will create them,
# but you can pre-create to avoid race conditions):
mkdir -p data/generators data/raw/contracts data/mmm
```

### 4. Verify Python environment

```bash
# Ensure pandas and numpy are available (used by all generators)
python -c "import pandas, numpy; print('OK')"
```

---

## Data Inventory

All 20 datasets at a glance. Use this as a checklist during and after generation.

| # | File | Format | Rows | Owner | Phase |
|---|------|--------|------|-------|-------|
| 1 | `data/raw/meta_ads.csv` | CSV | ~8,000 | digital-media-gen | 2 |
| 2 | `data/raw/google_ads.csv` | CSV | ~6,000 | digital-media-gen | 2 |
| 3 | `data/raw/dv360.csv` | CSV | ~4,000 | digital-media-gen | 2 |
| 4 | `data/raw/tiktok_ads.csv` | CSV | ~3,000 | digital-media-gen | 2 |
| 5 | `data/raw/youtube_ads.csv` | CSV | ~4,000 | digital-media-gen | 2 |
| 6 | `data/raw/linkedin_ads.csv` | CSV | ~1,500 | digital-media-gen | 2 |
| 7 | `data/raw/tv_performance.csv` | CSV | ~300 | traditional-media-gen | 2 |
| 8 | `data/raw/ooh_performance.csv` | CSV | ~150 | traditional-media-gen | 2 |
| 9 | `data/raw/print_performance.csv` | CSV | ~100 | traditional-media-gen | 2 |
| 10 | `data/raw/radio_performance.csv` | CSV | ~60 | traditional-media-gen | 2 |
| 11 | `data/raw/competitor_spend.csv` | CSV | ~360 | external-context-gen | 2 |
| 12 | `data/raw/economic_indicators.csv` | CSV | ~36 | external-context-gen | 2 |
| 13 | `data/raw/events.csv` | CSV | ~15 | external-context-gen | 2 |
| 14 | `data/raw/sla_tracking.csv` | CSV | ~50 | external-context-gen | 2 |
| 15 | `data/raw/vehicle_sales.csv` | CSV | ~4,600 | sales-pipeline-gen | 3 |
| 16 | `data/raw/website_analytics.csv` | CSV | ~5,000 | sales-pipeline-gen | 3 |
| 17 | `data/raw/configurator_sessions.csv` | CSV | ~12,000 | sales-pipeline-gen | 3 |
| 18 | `data/raw/leads.csv` | CSV | ~10,000 | sales-pipeline-gen | 3 |
| 19 | `data/raw/test_drives.csv` | CSV | ~8,000 | sales-pipeline-gen | 3 |
| 20a | `data/mmm/weekly_channel_spend.csv` | CSV | 52 | validator | 4 |
| 20b | `data/mmm/weekly_sales.csv` | CSV | 52 | validator | 4 |
| 20c | `data/mmm/model_ready.csv` | CSV | 52 | validator | 4 |
| C1 | `data/raw/contracts/ITV_Airtime_Agreement.md` | MD | ~200 | external-context-gen | 2 |
| C2 | `data/raw/contracts/Sky_Airtime_Agreement.md` | MD | ~200 | external-context-gen | 2 |
| C3 | `data/raw/contracts/Sky_BVOD_Addendum.md` | MD | ~150 | external-context-gen | 2 |
| C4 | `data/raw/contracts/JCDecaux_OOH_Contract.md` | MD | ~200 | external-context-gen | 2 |
| C5 | `data/raw/contracts/ClearChannel_DOOH_Agreement.md` | MD | ~180 | external-context-gen | 2 |
| C6 | `data/raw/contracts/Channel4_Media_Partnership.md` | MD | ~180 | external-context-gen | 2 |
| C7 | `data/raw/contracts/MediaAgency_Terms_of_Business.md` | MD | ~250 | external-context-gen | 2 |

**Totals**: ~63,000 CSV rows + 7 contract documents + 3 MMM-ready aggregation files

---

## Critical Data Relationships

The causal chain that all generators must respect:

```
Media Spend (all channels)
  ──[7-14 day lag (digital), 1-3 day lag (TV)]──►
    Website Sessions
      ──[2-5% of sessions]──►
        Configurator Starts
          ──[30-40% completion rate]──►
            Configurator Completes
              ──[25% of completers]──►
                Leads Submitted
                  ──[45% of qualified leads]──►
                    Test Drives Booked
                      ──[68% show rate]──►
                        Test Drives Completed
                          ──[15-25% within 90 days]──►
                            Vehicle Sales
```

**Key constraints across datasets:**
- `dealer_id` values in `vehicle_sales.csv` and `test_drives.csv` must exist in the config dealer list
- `lead_id` values in `test_drives.csv` must exist in `leads.csv`
- UTM campaign names in `configurator_sessions.csv` must map to campaigns in media CSVs
- Total annual spend across all channel CSVs must sum to ~£20M (±5%)
- No sales exist before Sep 2025 (vehicles not available)
- Sales-pipeline-gen must read the actual media CSV files to model spend→traffic correlations

---

## How to Use

1. Open Claude Code in the project root (`rag-mmm-platform/`).
2. Start a tmux session: `tmux new -s synth-data`
3. Paste the Master Prompt below (or reference this file) to kick off the team.
4. The lead agent will create the team, define tasks, spawn 6 teammates, and orchestrate generation in dependency order.
5. Watch all 6 panes work simultaneously in tmux.
6. All output lands in `data/raw/`, `data/raw/contracts/`, and `data/mmm/`.

---

## Master Prompt (Give This to Claude Code)

```
Create a team of 6 agents to generate 20 synthetic datasets for the RAG-MMM platform. The data represents a fictional Chinese EV brand launching DEEPAL and AVATR vehicles in the UK, Germany, and France during calendar year 2025.

All generated data must land in:
- data/raw/*.csv (19 source-format CSV files)
- data/raw/contracts/*.md (7 vendor contract documents)
- data/mmm/*.csv (3 model-ready aggregated files)

Before any agent starts generating data, the first task is to create the shared config module at data/generators/config.py. Every generator must import from this config to ensure consistency.

---

TEAM STRUCTURE

Create a team called "synthetic-data-gen" with these 6 teammates:

1. Name: "config-engineer"
   Type: general-purpose
   Role: Build the master config and orchestrator

2. Name: "digital-media-gen"
   Type: general-purpose
   Role: Generate all 6 digital media platform CSVs

3. Name: "traditional-media-gen"
   Type: general-purpose
   Role: Generate TV, OOH, Print, Radio CSVs

4. Name: "sales-pipeline-gen"
   Type: general-purpose
   Role: Generate Vehicle Sales, Test Drives, Configurator, Leads CSVs

5. Name: "external-context-gen"
   Type: general-purpose
   Role: Generate competitor spend, economic indicators, events, SLA, and contract documents

6. Name: "validator"
   Type: general-purpose
   Role: Build validators, aggregate MMM-ready data, run consistency checks

---

TASK DEFINITIONS (create these in the task list)

### Phase 1 — Foundation (must complete before Phase 2)

TASK 1: "Create master config module"
  Owner: config-engineer
  Description: |
    Create data/generators/config.py with all shared constants, parameters, and helper functions.
    Every other generator will import from this file.

    The config must include:

    DATE RANGE:
    - Start: 2025-01-01
    - End: 2025-12-31
    - UK launch date: 2025-09-01 (DEEPAL S07)
    - S05 preview: 2025-12-01

    MARKETS & BUDGET SPLIT:
    - UK (GB): 72% of total budget — primary market
    - Germany (DE): 20%
    - France (FR): 8%
    - Total annual budget: ~£20M (UK portion)

    VEHICLE MODELS:
    - DEEPAL_S07: Main launch vehicle. Available from Sep 2025.
      Trims: Pure (£27,990), Design (£31,990), Intelligence (£35,990)
    - DEEPAL_S05: Preview/pre-order from Dec 2025. SUV-coupe.
    - AVATR_12: Premium SUV. Limited volume. From Sep 2025.
    - AVATR_11: Premium sedan. Very limited. From Oct 2025.

    CHANNEL BUDGETS (UK annual):
    - TV (Linear + BVOD): £6,000,000
    - OOH/DOOH: £3,000,000
    - YouTube: £2,400,000
    - Meta (Facebook + Instagram): £2,000,000
    - Google Ads (Search + PMax): £1,600,000
    - DV360 (Programmatic Display): £1,400,000
    - TikTok: £1,000,000
    - LinkedIn: £400,000
    - Print: £600,000
    - Radio: £400,000
    - Events & Sponsorships: £600,000
    - TOTAL: £20,000,000

    SEASONAL MULTIPLIERS (monthly index, 1.0 = average):
    - Jan: 0.30 (pre-launch quiet)
    - Feb: 0.30
    - Mar: 0.40 (plate change month — some teaser activity)
    - Apr: 0.35
    - May: 0.40
    - Jun: 0.50 (pre-launch build-up begins)
    - Jul: 0.70 (pre-launch ramp)
    - Aug: 0.90 (heavy pre-launch)
    - Sep: 2.50 (LAUNCH MONTH — plate change + launch)
    - Oct: 1.80 (post-launch momentum)
    - Nov: 1.20 (sustained)
    - Dec: 0.80 (holiday slowdown, S05 preview)

    UK DEALER LIST (50 dealers):
    Generate 50 realistic UK dealer entries with:
    - dealer_id: DLR001-DLR050
    - dealer_name: Use real UK dealer group names (Lookers, Stoneacre, Parks Motor Group,
      Ancaster, Hendy, JCT600, Vertu Motors, Marshall, Inchcape, Arnold Clark, etc.)
      Each group may have 2-5 locations.
    - region: London, South East, South West, East, West Midlands, East Midlands,
      Yorkshire, North West, North East, Scotland, Wales
    - city: Realistic city for each region
    - is_launch_dealer: True for ~15 dealers (London + major cities, open Sep 1)
    - opening_date: Launch dealers = 2025-09-01, others staggered Sep-Nov 2025

    CAMPAIGN NAME TEMPLATES:
    - Meta: "{market}_{model}_Meta_{objective}_{quarter}" e.g. "UK_S07_Meta_Awareness_Q3"
    - Google: "{market}_{model}_Google_{campaign_type}_{quarter}"
    - DV360: "{market}_{model}_DV360_{tactic}_{quarter}"
    - TikTok: "{market}_{model}_TikTok_{format}_{quarter}"
    - YouTube: "{market}_{model}_YT_{format}_{quarter}"
    - LinkedIn: "{market}_{model}_LI_{objective}_{quarter}"
    - TV: "{broadcaster}_{daypart}_{spot_length}s_{week}"

    HELPER FUNCTIONS to include:
    - get_daily_budget(channel, date) -> float: Returns daily spend based on monthly
      multiplier + channel budget. Adds ±15% daily noise.
    - get_weekly_budget(channel, week_start) -> float: Sums daily for the week.
    - apply_adstock(spend_series, decay_rate) -> series: Geometric adstock transformation.
    - apply_saturation(x, alpha, gamma) -> float: Hill function saturation curve.
    - generate_campaign_name(channel, market, model, **kwargs) -> str
    - is_pre_launch(date) -> bool: True if before 2025-09-01
    - get_active_models(date) -> list: Which vehicles are available on a given date

    RANDOM SEED: np.random.seed(42) — all generators must use this or derived seeds.

    Also create data/generators/__init__.py (empty) and data/generators/generate_all.py
    as a stub orchestrator that will import and run all generators in order.

    Create the directory structure:
    - data/generators/
    - data/raw/
    - data/raw/contracts/
    - data/mmm/


TASK 2: "Create generate_all.py orchestrator"
  Owner: config-engineer
  Blocked by: Task 1
  Description: |
    Create data/generators/generate_all.py that:
    1. Imports and runs all generator modules in dependency order
    2. Prints progress as each dataset is generated
    3. Runs validators at the end
    4. Prints summary statistics (row counts, file sizes, total spend checks)

    Execution order:
    1. config (already loaded on import)
    2. external_data.generate() — economic indicators, competitor spend
    3. events.generate() — event calendar
    4. digital_media.generate() — 6 CSVs
    5. traditional_media.generate() — 4 CSVs
    6. sales_pipeline.generate() — 4 CSVs (reads media spend CSVs for correlation)
    7. contracts.generate() — 7 markdown docs
    8. aggregate_mmm_data() — reads all raw CSVs, outputs 3 MMM files
    9. validators.validate_all() — cross-checks everything

    The script should be runnable as:
      python data/generators/generate_all.py


### Phase 2 — Independent Generators (can run in parallel after Phase 1)

TASK 3: "Generate 6 digital media CSVs"
  Owner: digital-media-gen
  Blocked by: Task 1
  Description: |
    Create data/generators/digital_media.py with a generate() function that produces
    6 CSV files in data/raw/. Import all constants from config.py.

    FILE 1: data/raw/meta_ads.csv (~8,000 rows)
    Daily × campaign × platform (Facebook/Instagram)
    Columns: date, campaign_name, campaign_id, platform, objective (awareness/traffic/
    lead_gen/conversions), market, model, impressions, clicks, ctr, cpm, cpc, spend,
    reach, frequency, video_views, video_view_rate, leads, link_clicks,
    landing_page_views, cost_per_lead
    Constraints:
    - Annual spend sums to ~£2,000,000 (UK portion)
    - Awareness campaigns: CTR 0.5-1.5%, CPM £4-6
    - Lead gen campaigns: CTR 1-3%, CPM £6-10, cost_per_lead £15-40
    - Traffic campaigns: CTR 1-2%, CPC £0.30-0.80
    - ~10 campaigns active at various times
    - Pre-launch (Jan-Aug): only awareness + teaser, much lower spend
    - Post-launch (Sep+): full funnel active

    FILE 2: data/raw/google_ads.csv (~6,000 rows)
    Daily × campaign × keyword group
    Columns: date, campaign_name, campaign_id, campaign_type (search/pmax/display),
    market, model, keyword_group, impressions, clicks, ctr, avg_cpc, spend,
    conversions, conversion_rate, cost_per_conversion, quality_score,
    impression_share, search_impression_share
    Constraints:
    - Annual spend: ~£1,600,000
    - Brand search: CTR 5-15%, CPC £0.50-1.50, quality score 7-9
    - Generic search ("electric SUV"): CTR 1-3%, CPC £2-5, quality score 5-7
    - PMax: blended metrics, CTR 2-5%
    - Conversions = configurator starts + test drive bookings
    - Brand search volume spikes at launch and after TV flights

    FILE 3: data/raw/dv360.csv (~4,000 rows)
    Daily × line item
    Columns: date, insertion_order, line_item_name, line_item_id, market, model,
    creative_size, exchange, impressions, clicks, ctr, cpm, spend, viewable_impressions,
    viewability_rate, video_completions, video_completion_rate
    Constraints:
    - Annual spend: ~£1,400,000
    - Display CTR: 0.05-0.30%
    - Video completion rate: 60-80%
    - Viewability: 70%+ (target)
    - Creative sizes: 300x250, 728x90, 160x600, 320x50, video_pre-roll

    FILE 4: data/raw/tiktok_ads.csv (~3,000 rows)
    Daily × campaign
    Columns: date, campaign_name, campaign_id, objective, market, model, impressions,
    clicks, ctr, cpm, spend, video_views, video_view_rate, avg_watch_time_seconds,
    shares, comments, likes, profile_visits, website_clicks
    Constraints:
    - Annual spend: ~£1,000,000
    - CPM: £1-3 (cheapest reach)
    - CTR: 0.3-1.0% (low click intent)
    - High engagement: shares/comments/likes
    - Video view rate: 15-30%
    - Avg watch time: 3-8 seconds
    - Skews younger audience, brand awareness focus

    FILE 5: data/raw/youtube_ads.csv (~4,000 rows)
    Daily × campaign × format (TrueView/Bumper/Shorts)
    Columns: date, campaign_name, campaign_id, format, market, model, impressions,
    views, view_rate, clicks, ctr, cpv, cpm, spend, video_played_25, video_played_50,
    video_played_75, video_played_100, earned_views, earned_subscribers
    Constraints:
    - Annual spend: ~£2,400,000
    - TrueView: view rate 30-50%, CPV £0.01-0.04
    - Bumper (6s): CPM £3-6, no skip
    - Shorts: CPM £1-2, view rate 10-20%
    - Earned views ~5-10% of paid views

    FILE 6: data/raw/linkedin_ads.csv (~1,500 rows)
    Daily × campaign
    Columns: date, campaign_name, campaign_id, objective, market, model,
    impressions, clicks, ctr, cpm, cpc, spend, leads, cost_per_lead,
    social_actions, follower_gains, company_page_clicks
    Constraints:
    - Annual spend: ~£400,000
    - CPM: £12-25 (premium B2B)
    - CTR: 0.3-0.8%
    - Cost per lead: £30-80
    - Fleet/B2B focused — targets fleet managers
    - Lower volume but high-value leads

    IMPORTANT: All datasets must use the seasonal multipliers from config.py.
    Pre-launch months (Jan-Aug) should have minimal spend (teaser/awareness only).
    Post-launch (Sep-Dec) ramps to full spend. Daily spend should have ±15% noise.
    Campaign names must follow the templates in config.py.


TASK 4: "Generate 4 traditional media CSVs"
  Owner: traditional-media-gen
  Blocked by: Task 1
  Description: |
    Create data/generators/traditional_media.py with a generate() function that
    produces 4 CSV files in data/raw/. Import all constants from config.py.

    FILE 1: data/raw/tv_performance.csv (~300 rows)
    Weekly × broadcaster
    Columns: date_week_start, broadcaster (ITV, Channel4, Sky, ITV_BVOD, Channel4_BVOD,
    Sky_BVOD), daypart (peak/off-peak/daytime/late_night), market, spot_length_seconds,
    spots_aired, grps, reach_000, reach_pct, avg_frequency, cpp, spend, programme_name
    Constraints:
    - Annual spend: ~£6,000,000
    - Split: Linear ~70%, BVOD ~30%
    - GRPs: 50-150 per week during active flights
    - Reach: 20-40% of adult population per week
    - Frequency: 3-6 per week
    - Peak CPP: £25,000-40,000. Off-peak: £8,000-15,000
    - Flights: 2-week on / 1-week off pattern during active period
    - Major flights: Sep launch, Oct sustain, Nov Christmas
    - Spot lengths: 60s (launch hero), 30s (main), 10s (reminder)
    - Programme examples: ITV (Coronation Street, This Morning), C4 (Gogglebox, Grand Designs),
      Sky (Sky Sports, Sky News)

    FILE 2: data/raw/ooh_performance.csv (~150 rows)
    Per-campaign period (2-week cycles)
    Columns: campaign_name, campaign_id, start_date, end_date, market, format
    (classic_48sheet/classic_96sheet/digital_d6/digital_large/bus_shelter/
    transport_rail/transport_underground), vendor (JCDecaux/ClearChannel),
    sites_booked, impressions, reach_000, frequency, spend, region, city
    Constraints:
    - Annual spend: ~£3,000,000
    - Digital ~55%, Classic ~45%
    - Major bursts: Sep-Oct launch (heavy London + major cities)
    - Always-on DOOH in key locations (dealer proximity)
    - London transport network: Underground, rail stations
    - Motorway D48/D96 for national reach

    FILE 3: data/raw/print_performance.csv (~100 rows)
    Per-insertion
    Columns: date, publication, edition, format (full_page/half_page/dps/
    cover_wrap/advertorial), market, model, rate_card_cost, negotiated_cost,
    spend, circulation, readership_000, page_number, creative_id
    Constraints:
    - Annual spend: ~£600,000
    - Publications: Autocar, What Car?, Top Gear Magazine, Auto Express,
      Sunday Times Driving, The Telegraph Motoring, CAR Magazine
    - Heavy in Sep-Oct (launch features + advertorials)
    - Some pre-launch teaser ads in Jul-Aug automotive press
    - Negotiated cost = 50-70% of rate card

    FILE 4: data/raw/radio_performance.csv (~60 rows)
    Per-flight (1-2 week campaigns)
    Columns: campaign_name, start_date, end_date, station, station_group
    (Global/Bauer/Wireless), market, daypart, spots_per_day, total_spots,
    reach_000, frequency, cpm, spend, region
    Constraints:
    - Annual spend: ~£400,000
    - Regional focus around dealer openings
    - Stations: Capital FM, Heart, Classic FM, LBC, talkSPORT, local stations
    - Daypart: Breakfast drive 60%, daytime 25%, evening drive 15%
    - 30s spots standard
    - Flights coincide with dealer opening events in specific regions


TASK 5: "Generate external context datasets"
  Owner: external-context-gen
  Blocked by: Task 1
  Description: |
    Create data/generators/external_data.py and data/generators/events.py,
    each with a generate() function.

    FILE 1: data/raw/competitor_spend.csv (~360 rows)
    Monthly × competitor × channel
    Columns: year_month, competitor, channel (tv/digital/ooh/print/radio/total),
    estimated_spend_gbp, share_of_voice_pct, source
    Constraints:
    - Competitors: BYD, Tesla, MG, Hyundai_Ioniq, Xpeng
    - BYD: Biggest spender (~£30M annual), heavy TV
    - Tesla: Minimal traditional (~£5M), strong organic/digital
    - MG: Strong value messaging (~£15M)
    - Hyundai Ioniq: Established brand (~£20M across Ioniq range)
    - Xpeng: New entrant like us (~£8M)
    - Our brand should be competitive but not the biggest spender
    - Source column: "Nielsen Ad Intel Estimate"

    FILE 2: data/raw/economic_indicators.csv (~36 rows)
    Monthly × country (UK only for now, 12 months × 3 indicators sets)
    Columns: year_month, country, smmt_total_registrations, smmt_bev_registrations,
    bev_market_share_pct, consumer_confidence_index, bank_rate_pct,
    avg_petrol_price_ppl, avg_electricity_price_pkwh, unemployment_rate_pct,
    cpi_index, new_car_avg_transaction_price_gbp
    Constraints:
    - Use realistic 2025 trajectories:
      - Bank rate: Start 4.50%, declining to ~3.75% by Dec (expected cuts)
      - BEV share: ~22% in Jan, trending toward 28% by Dec (ZEV mandate)
      - Consumer confidence: -15 to -8 (improving slowly)
      - Petrol: 140-155p/litre
      - Electricity: 24-28p/kWh
    - SMMT total registrations: ~1.8M annual, seasonal (Mar and Sep peaks)

    FILE 3: data/raw/events.csv (~15 rows)
    Per-event
    Columns: event_name, event_type (motor_show/test_drive_event/sponsorship/
    dealer_launch/fleet_event/press_event), start_date, end_date, location,
    market, estimated_attendance, media_impressions, spend, leads_generated,
    test_drives_completed, description
    Constraints:
    - Goodwood Festival of Speed: Jul 2025 (pre-launch reveal)
    - London Motor Show (if applicable) or Fully Charged Live
    - 5 dealer launch events (Sep-Oct, major cities)
    - 2 fleet showcase events (Oct-Nov)
    - 2 press launch events (Aug-Sep)
    - 1 Christmas showcase (Dec, shopping centres)
    - Total events spend: ~£600,000

    FILE 4: data/raw/sla_tracking.csv (~50 rows)
    Monthly × contract
    Columns: year_month, vendor, contract_type, metric_name, contracted_value,
    actual_value, variance_pct, in_compliance, notes
    Constraints:
    - Track SLA compliance for TV (GRP delivery), OOH (site availability),
      Digital (viewability, brand safety), Agency (reporting timeliness)
    - Most months in compliance (85%+)
    - A few realistic misses: OOH site unavailable, TV under-delivery in one flight,
      viewability dip in Q4


TASK 6: "Generate 4 sales pipeline CSVs"
  Owner: sales-pipeline-gen
  Blocked by: Task 1, Task 3, Task 4
  Description: |
    Create data/generators/sales_pipeline.py with a generate() function.
    This generator MUST read the media spend CSVs (from Tasks 3+4) to create
    realistic correlations between spend and pipeline metrics.

    CRITICAL RELATIONSHIPS TO MODEL:
    - Ad spend → website traffic (7-14 day lag for digital, 1-3 day for TV)
    - Website traffic → configurator starts (2-5% of sessions)
    - Configurator completes → leads (30-40% completion rate)
    - Leads → test drive bookings (45% of qualified leads)
    - Test drives → sales (15-25% conversion within 90 days)
    - Add 20-30% unexplained variance (noise) to all relationships

    FILE 1: data/raw/vehicle_sales.csv (~4,600 rows)
    Per-unit, daily
    Columns: sale_id, sale_date, market, dealer_id, dealer_name, dealer_region,
    model, trim, colour, sale_type (retail/fleet/salary_sacrifice),
    list_price_gbp, transaction_price_gbp, discount_pct, finance_type
    (cash/pcp/hp/lease), finance_term_months, lead_source
    (website/test_drive/walk_in/fleet_enquiry/referral), days_from_lead,
    days_from_test_drive, customer_postcode_area (first 2-4 chars only)
    Constraints:
    - Total units: UK ~2,800, DE ~1,200, FR ~600
    - Pre-launch (Jan-Aug): 0 sales (cars not available yet)
    - Sep: Launch spike (~30% of annual UK sales in Sep-Oct)
    - Model split: S07 ~70%, Avatr 12 ~20%, Avatr 11 ~8%, S05 ~2% (Dec only)
    - Sale type: Retail 55%, Fleet 30%, Salary Sacrifice 15%
    - Finance: PCP 45%, Lease 25%, HP 15%, Cash 15%
    - Colours: Aurora Green (25%), Pearl White (20%), Nebula Grey (20%),
      Midnight Black (15%), Cosmos Blue (12%), Sunset Orange (8%)
    - Discounts: 0-3% in Sep-Oct (high demand), 3-7% in Nov-Dec
    - Launch dealers get 60% of Sep sales, evening out by Nov

    FILE 2: data/raw/website_analytics.csv (~5,000 rows)
    Daily × channel × device
    Columns: date, channel (organic_search/paid_search/social_paid/social_organic/
    direct/display/email/referral/video), device (desktop/mobile/tablet),
    market, sessions, users, new_users, bounce_rate, pages_per_session,
    avg_session_duration_seconds, goal_completions (configurator_start/
    test_drive_booking/brochure_download/dealer_locator), events_count
    Constraints:
    - Monthly sessions: 80K-150K (post-launch), 10K-30K (pre-launch)
    - Desktop 35%, Mobile 55%, Tablet 10%
    - Paid search traffic correlates with Google Ads spend
    - Social paid correlates with Meta + TikTok spend
    - Display correlates with DV360 spend
    - Organic search grows over time as brand awareness increases
    - Bounce rate: Paid search 35-50%, Social 55-70%, Direct 25-40%
    - Avg session duration: 2-5 minutes

    FILE 3: data/raw/configurator_sessions.csv (~12,000 rows)
    Per-session
    Columns: session_id, start_timestamp, market, device, referral_source,
    model_selected, trim_selected, colour_selected, wheels_selected,
    interior_selected, accessories_added, finance_option_viewed,
    monthly_payment_viewed, completed (bool), completion_time_seconds,
    lead_submitted (bool), utm_source, utm_medium, utm_campaign
    Constraints:
    - 30-40% completion rate
    - Most popular config: S07 Design, Aurora Green, 19" wheels
    - Finance calculator viewed by 60% of completers
    - Average completion time: 4-8 minutes
    - Lead submitted by 25% of completers
    - UTM parameters should map back to campaign names in media CSVs

    FILE 4: data/raw/leads.csv (~10,000 rows)
    Per-lead
    Columns: lead_id, created_date, market, source (website_configurator/
    website_test_drive/meta_lead_form/google_lead/linkedin_lead/
    event_signup/dealer_walk_in/phone_enquiry/fleet_enquiry),
    model_interest, dealer_id, lead_status (NEW/CONTACTED/QUALIFIED/
    TD_BOOKED/TD_COMPLETED/NEGOTIATION/WON/LOST), status_date,
    days_in_pipeline, assigned_dealer, lead_score (1-100),
    contact_attempts, first_response_hours
    Constraints:
    - Pipeline: NEW(100%) → CONTACTED(85%) → QUALIFIED(60%) →
      TD_BOOKED(45%) → TD_COMPLETED(35%) → NEGOTIATION(20%) → WON(12%)/LOST
    - First response time: median 2 hours, 90th percentile 24 hours
    - Lead score correlates with conversion probability
    - Source distribution: website 40%, social 25%, events 10%, dealer 15%, fleet 10%
    - Pre-launch leads (Jun-Aug) are "register interest" — convert at lower rate

    FILE 5: data/raw/test_drives.csv (~8,000 rows)
    Per-booking
    Columns: booking_id, booking_date, test_drive_date, market, dealer_id,
    dealer_name, model, source (website/dealer/event/fleet_day),
    status (BOOKED/CONFIRMED/COMPLETED/NO_SHOW/CANCELLED),
    lead_id (FK to leads), feedback_score (1-5, if completed),
    feedback_text (short), duration_minutes, sale_within_90_days (bool),
    days_to_sale
    Constraints:
    - 22% no-show rate
    - 10% cancellation rate
    - 68% completion rate
    - Of completed: 15-25% convert to sale within 90 days
    - Feedback score: mean 4.2, std 0.6
    - Weekend bookings: 45% of total
    - Duration: 30-60 minutes


TASK 7: "Generate vendor contract documents"
  Owner: external-context-gen
  Blocked by: Task 1
  Description: |
    Create data/generators/contracts.py with a generate() function that produces
    7 realistic vendor contract documents as markdown files in data/raw/contracts/.
    These will be used to test the RAG pipeline's ability to parse unstructured documents.

    Each contract should be 3-8 pages equivalent in markdown, with:
    - Formal legal language and clause numbering
    - Parties, dates, signatures placeholders
    - Specific commercial terms (rates, volumes, penalties)
    - Cross-references between clauses
    - Appendices with rate cards or technical specifications

    CONTRACT 1: data/raw/contracts/ITV_Airtime_Agreement.md
    - Parties: ITV plc and [Our Brand] UK Ltd
    - Term: 12 months from 2025-07-01
    - Annual commitment: £2,500,000 (linear) + £800,000 (ITVX/BVOD)
    - Rate card with CPP by daypart
    - Make-good provisions for under-delivery
    - Cancellation terms: 8 weeks notice for linear, 2 weeks for BVOD
    - Brand safety exclusions: no adjacency to gambling, alcohol

    CONTRACT 2: data/raw/contracts/Sky_Airtime_Agreement.md
    - Parties: Sky Media and [Our Brand] UK Ltd
    - Annual commitment: £1,800,000 (linear) + £600,000 (Sky Go/AdSmart)
    - AdSmart addressable targeting provisions
    - Sports inventory premium rates
    - Similar structure to ITV but different commercial terms

    CONTRACT 3: data/raw/contracts/Sky_BVOD_Addendum.md
    - Addendum to Sky agreement
    - Specific BVOD/AdSmart targeting capabilities
    - CPM-based pricing (vs CPP for linear)
    - Frequency capping provisions
    - Data sharing and measurement clauses

    CONTRACT 4: data/raw/contracts/JCDecaux_OOH_Contract.md
    - Parties: JCDecaux UK Ltd and [Our Brand] UK Ltd
    - Annual commitment: £1,800,000
    - Site list by format (D6, 48-sheet, transport)
    - Impression guarantees and make-good terms
    - Installation and production responsibilities
    - Digital content change frequency (hourly rotation)
    - Force majeure: site damage, planning permission issues

    CONTRACT 5: data/raw/contracts/ClearChannel_DOOH_Agreement.md
    - Parties: Clear Channel UK and [Our Brand] UK Ltd
    - Annual commitment: £1,200,000
    - Focus on digital out-of-home
    - Programmatic DOOH provisions (Hivestack/Vistar integration)
    - Audience measurement methodology
    - Environmental/sustainability commitments

    CONTRACT 6: data/raw/contracts/Channel4_Media_Partnership.md
    - Parties: Channel 4 and [Our Brand] UK Ltd
    - Annual commitment: £800,000 (airtime) + £200,000 (partnership/content)
    - Branded content provisions (Channel 4 creative partnership)
    - All 4 streaming inclusion
    - Sustainability messaging alignment (Channel 4's brand values)
    - Talent usage rights for branded content

    CONTRACT 7: data/raw/contracts/MediaAgency_Terms_of_Business.md
    - Parties: [Agency Name] Media Ltd and [Our Brand] UK Ltd
    - Agency commission: 3% on media, 15% on production
    - Scope of services: planning, buying, trafficking, reporting
    - Payment terms: 30 days from invoice
    - Audit rights: annual media audit
    - Data ownership and IP provisions
    - KPI framework and performance bonuses
    - Termination: 90 days notice, handover provisions


### Phase 3 — Aggregation & Validation (after all generators complete)

TASK 8: "Build validators and aggregate MMM-ready data"
  Owner: validator
  Blocked by: Task 3, Task 4, Task 5, Task 6, Task 7
  Description: |
    Create data/generators/validators.py with a validate_all() function.
    Also add an aggregate_mmm_data() function (can be in validators.py or a
    separate aggregator module).

    VALIDATION CHECKS:
    1. File existence: All 19 CSVs + 7 contracts exist
    2. Row counts: Each file within expected range (±20%)
    3. Budget totals: Sum of all channel spend ≈ £20M (±5%)
       - Meta: ~£2M
       - Google: ~£1.6M
       - DV360: ~£1.4M
       - TikTok: ~£1M
       - YouTube: ~£2.4M
       - LinkedIn: ~£400K
       - TV: ~£6M
       - OOH: ~£3M
       - Print: ~£600K
       - Radio: ~£400K
       - Events: ~£600K
    4. Sales totals: UK ~2,800, DE ~1,200, FR ~600 (±10%)
    5. Date ranges: All files cover 2025-01-01 to 2025-12-31
    6. No orphaned foreign keys:
       - dealer_ids in sales exist in config dealer list
       - lead_ids in test_drives exist in leads
       - Campaign names in website analytics UTMs match media CSVs
    7. Conversion funnel makes sense:
       - Leads > test drives > sales
       - Configurator sessions > completed > lead_submitted
    8. Seasonal pattern present: Sep-Oct should have highest activity
    9. No negative values in spend, impressions, clicks
    10. CTR = clicks/impressions (within rounding tolerance)

    MMM AGGREGATION:
    Create 3 files in data/mmm/:

    1. data/mmm/weekly_channel_spend.csv
    Columns: week_start, tv_spend, ooh_spend, print_spend, radio_spend,
    meta_spend, google_spend, dv360_spend, tiktok_spend, youtube_spend,
    linkedin_spend, events_spend, total_spend
    - Aggregate daily digital spend to weekly
    - Sum traditional media to weekly
    - 52 rows (one per week of 2025)

    2. data/mmm/weekly_sales.csv
    Columns: week_start, uk_units, de_units, fr_units, total_units,
    uk_revenue, de_revenue, fr_revenue, total_revenue,
    uk_test_drives, uk_leads, uk_web_sessions
    - 52 rows

    3. data/mmm/model_ready.csv
    Columns: week_start + all channel spend columns +
    adstock-transformed versions (tv_adstock, meta_adstock, etc.) +
    sales columns + external factors (bev_share, consumer_confidence,
    bank_rate, competitor_total_spend)
    - 52 rows, fully joined and ready for MMM regression
    - Apply adstock transformation using config.py helper
    - TV decay: 0.85 (long tail)
    - Digital decay: 0.40 (fast)
    - OOH decay: 0.70 (medium)
    - Print decay: 0.60
    - Radio decay: 0.50

    Print a summary report showing:
    - Total rows generated per file
    - Total spend by channel
    - Total sales by market
    - Any validation failures


---

DEPENDENCY GRAPH:
Task 1 (config) → blocks everything
Task 2 (orchestrator) → blocked by Task 1
Task 3 (digital media) → blocked by Task 1
Task 4 (traditional media) → blocked by Task 1
Task 5 (external context) → blocked by Task 1
Task 6 (sales pipeline) → blocked by Tasks 1, 3, 4
Task 7 (contracts) → blocked by Task 1
Task 8 (validators + MMM) → blocked by Tasks 3, 4, 5, 6, 7

EXECUTION FLOW:
Phase 1: config-engineer does Tasks 1+2
Phase 2: digital-media-gen (Task 3), traditional-media-gen (Task 4),
         external-context-gen (Tasks 5+7) run IN PARALLEL
Phase 3: sales-pipeline-gen (Task 6) runs after 3+4 complete
Phase 4: validator (Task 8) runs after everything else

---

IMPORTANT GUIDELINES FOR ALL AGENTS:
1. Import from data.generators.config — never hardcode values that exist in config
2. Use numpy random with seed for reproducibility
3. All monetary values in GBP (£) for UK market, EUR (€) for DE/FR
4. Date format: ISO 8601 (YYYY-MM-DD)
5. CSV files should have headers, UTF-8 encoding, standard comma delimiter
6. No PII — all names/addresses are fictional
7. Keep files under 300 lines each — split into helpers if needed
8. Print progress messages during generation
9. Handle the case where data/raw/ might not exist (create dirs)
10. Each generator module should be independently runnable for testing:
    if __name__ == "__main__": generate()
```

---

## Quick Reference: Budget Allocation

| Channel | Annual (UK) | Monthly Peak (Sep) | Monthly Trough (Jan) |
|---------|-------------|---------------------|----------------------|
| TV | £6,000,000 | ~£1,250,000 | ~£150,000 |
| OOH | £3,000,000 | ~£625,000 | ~£75,000 |
| YouTube | £2,400,000 | ~£500,000 | ~£60,000 |
| Meta | £2,000,000 | ~£417,000 | ~£50,000 |
| Google | £1,600,000 | ~£333,000 | ~£40,000 |
| DV360 | £1,400,000 | ~£292,000 | ~£35,000 |
| TikTok | £1,000,000 | ~£208,000 | ~£25,000 |
| Events | £600,000 | ~£125,000 | ~£15,000 |
| Print | £600,000 | ~£125,000 | ~£15,000 |
| Radio | £400,000 | ~£83,000 | ~£10,000 |
| LinkedIn | £400,000 | ~£83,000 | ~£10,000 |
| **Total** | **£20,000,000** | **~£4,167,000** | **~£500,000** |

## Quick Reference: Sales Funnel

```
Website Sessions (post-launch ~120K/month)
  → Configurator Starts (2-5% of sessions)
    → Configurator Completes (30-40% of starts)
      → Leads Submitted (25% of completes)
        → Test Drives Booked (45% of qualified leads)
          → Test Drives Completed (68% show rate)
            → Sales (15-25% of completed TDs within 90 days)
```

## Quick Reference: Seasonal Pattern

```
Jan ████░░░░░░░░░░░░░░░░ 0.30  (pre-launch quiet)
Feb ████░░░░░░░░░░░░░░░░ 0.30
Mar █████░░░░░░░░░░░░░░░ 0.40  (plate change teaser)
Apr ████░░░░░░░░░░░░░░░░ 0.35
May █████░░░░░░░░░░░░░░░ 0.40
Jun ██████░░░░░░░░░░░░░░ 0.50  (build-up begins)
Jul █████████░░░░░░░░░░░ 0.70  (pre-launch ramp)
Aug ███████████░░░░░░░░░ 0.90  (heavy pre-launch)
Sep █████████████████████ 2.50  *** LAUNCH ***
Oct █████████████████░░░░ 1.80  (post-launch)
Nov ██████████████░░░░░░░ 1.20  (sustained)
Dec ██████████░░░░░░░░░░░ 0.80  (holiday + S05 preview)
```

---

## Verification Commands

Run these after all agents complete to confirm successful generation.

### File existence check

```bash
# All 19 raw CSVs
for f in meta_ads google_ads dv360 tiktok_ads youtube_ads linkedin_ads \
         tv_performance ooh_performance print_performance radio_performance \
         competitor_spend economic_indicators events sla_tracking \
         vehicle_sales website_analytics configurator_sessions leads test_drives; do
  [ -f "data/raw/${f}.csv" ] && echo "OK  data/raw/${f}.csv" || echo "MISSING  data/raw/${f}.csv"
done

# 7 contracts
for f in ITV_Airtime_Agreement Sky_Airtime_Agreement Sky_BVOD_Addendum \
         JCDecaux_OOH_Contract ClearChannel_DOOH_Agreement \
         Channel4_Media_Partnership MediaAgency_Terms_of_Business; do
  [ -f "data/raw/contracts/${f}.md" ] && echo "OK  data/raw/contracts/${f}.md" || echo "MISSING  data/raw/contracts/${f}.md"
done

# 3 MMM aggregation files
for f in weekly_channel_spend weekly_sales model_ready; do
  [ -f "data/mmm/${f}.csv" ] && echo "OK  data/mmm/${f}.csv" || echo "MISSING  data/mmm/${f}.csv"
done
```

### Row count check

```bash
echo "=== Raw CSV Row Counts ==="
for f in data/raw/*.csv; do
  rows=$(($(wc -l < "$f") - 1))
  printf "%-45s %6d rows\n" "$f" "$rows"
done

echo ""
echo "=== MMM CSV Row Counts ==="
for f in data/mmm/*.csv; do
  rows=$(($(wc -l < "$f") - 1))
  printf "%-45s %6d rows\n" "$f" "$rows"
done

echo ""
echo "=== Contract Documents ==="
for f in data/raw/contracts/*.md; do
  lines=$(wc -l < "$f")
  printf "%-55s %4d lines\n" "$f" "$lines"
done
```

### Budget total check (quick Python)

```bash
python3 -c "
import pandas as pd, glob

total = 0
for f in glob.glob('data/raw/*.csv'):
    df = pd.read_csv(f)
    if 'spend' in df.columns:
        s = df['spend'].sum()
        total += s
        print(f'{f:45s} £{s:>12,.0f}')
print(f\"{'TOTAL':45s} £{total:>12,.0f}\")
print(f'Target: £20,000,000  Variance: {((total/20_000_000)-1)*100:+.1f}%')
"
```

### Sales total check

```bash
python3 -c "
import pandas as pd

df = pd.read_csv('data/raw/vehicle_sales.csv')
print('Sales by market:')
print(df.groupby('market').size().to_string())
print(f'Total: {len(df)}')
print(f'Expected: UK ~2800, DE ~1200, FR ~600 = ~4600')
"
```

### Run the built-in validator

```bash
python data/generators/generate_all.py --validate-only
# Or run validators directly:
python -c "from data.generators.validators import validate_all; validate_all()"
```

---

## To Execute This Prompt

When you're ready to generate all synthetic data:

```bash
# 1. Start tmux
tmux new -s synth-data

# 2. Open Claude Code in the project root
cd /path/to/rag-mmm-platform

# 3. Copy the "Master Prompt" section (between the ``` delimiters above)
#    and paste it into Claude Code

# 4. Watch all 6 agent panes generate data simultaneously

# 5. After completion, run the verification commands above
```
