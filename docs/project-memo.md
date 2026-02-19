# Project Memo: RAG + MMM Platform for Digital Marketing

> **Version:** 1.0 | **Date:** February 2026 | **Status:** Active Development

---

## 1. Executive Summary

### What We're Building

An enterprise platform that combines two capabilities into a single marketing intelligence system:

- **RAG (Retrieval-Augmented Generation)** — Makes fragmented marketing documents (contracts, campaign data, competitor intel) searchable through natural language questions
- **MMM (Marketing Mix Modeling)** — Uses statistical models to measure how each pound spent across media channels drives sales, then optimises future budget allocation

### Why It Matters

Marketing teams sit on data that is scattered across campaign platforms, vendor contracts, sales pipelines, and economic reports. Today, answering a question like *"What was our cost-per-lead on TikTok during launch month?"* requires pulling data from multiple systems and manual analysis. RAG collapses this into a single query. Meanwhile, the perennial question *"Are we spending the right amount on the right channels?"* is answered by gut feel rather than measured evidence. MMM replaces intuition with data-driven budget recommendations.

### Who It's For

| Audience | Primary Use |
|----------|------------|
| Marketing leadership | Budget decisions, ROI reporting, strategic planning |
| Campaign managers | Quick answers from contracts, benchmarks, and past performance |
| Data science / analytics | Model-ready datasets, retrieval strategy comparison, MMM tuning |

### Current Status

| Component | Status |
|-----------|--------|
| Synthetic data pipeline | Complete — 19 CSVs + 7 contracts (~63K rows) |
| Data validation framework | Complete — 10 automated checks |
| MMM data aggregation | Complete — 3 weekly datasets (52 weeks x 11 channels) |
| Platform UI (React + Vite) | Complete — 3 pages with light/dark theming |
| Data Dashboard API (FastAPI) | Complete — file inventory, PRD checks, previews |
| RAG pipeline modules | Scaffolded — stubs with architecture defined |
| MMM modeling modules | Scaffolded — stubs with architecture defined |

---

## 2. The Scenario: UK Automotive Launch

### Overview

All platform development uses a realistic synthetic dataset simulating a UK market launch for two Chinese EV brands — **DEEPAL** and **AVATR** — across 2025:

| Detail | Value |
|--------|-------|
| Annual UK marketing budget | £20,000,000 |
| Date range | 1 Jan 2025 – 31 Dec 2025 |
| Primary launch | DEEPAL S07 on 1 Sep 2025 |
| Additional launches | AVATR 12 (Sep), AVATR 11 (Oct), DEEPAL S05 preview (Dec) |
| UK dealer network | 50 dealers across 10 regions (15 launch dealers) |
| Marketing channels | 11 (6 digital + 4 traditional + events) |
| Competitor brands tracked | 10 (Tesla, BMW, Audi, Mercedes-Benz, Hyundai, Kia, Volvo, Polestar, BYD, MG) |

### Why Synthetic Data?

- **Safe to share** — no real client data, no NDA concerns
- **Reproducible** — seeded random generation (`seed=42`), identical outputs every run
- **Realistic causal chains** — media spend drives website sessions, which drive configurator use, which drives leads, which drive test drives, which drive sales
- **Pipeline validation** — proves the full data flow works before connecting real sources

### Channel Budget Allocation

| Channel | Annual Budget | Type |
|---------|--------------|------|
| TV | £6,000,000 | Traditional |
| OOH (Out of Home) | £3,000,000 | Traditional |
| YouTube | £2,400,000 | Digital |
| Meta (Facebook/Instagram) | £2,200,000 | Digital |
| Google (Search + Display) | £1,800,000 | Digital |
| DV360 (Programmatic) | £1,400,000 | Digital |
| TikTok | £1,000,000 | Digital |
| LinkedIn | £600,000 | Digital |
| Print | £600,000 | Traditional |
| Events & Activations | £600,000 | Events |
| Radio | £400,000 | Traditional |
| **Total** | **£20,000,000** | |

Spend is distributed seasonally — September (launch month) receives 2.5x the average monthly weighting, while January and February receive only 0.3x.

### Generated Data Summary

| File | Rows (approx.) | Key Columns | Purpose |
|------|----------------|-------------|---------|
| `meta_ads.csv` | 4,000–12,000 | date, campaign, spend, impressions, clicks, ctr, conversions | Meta campaign daily performance |
| `google_ads.csv` | 3,000–10,000 | date, campaign, spend, impressions, clicks, ctr, conversions | Google Ads daily performance |
| `dv360.csv` | 2,000–7,000 | date, campaign, spend, impressions, clicks, ctr | DV360 programmatic daily |
| `tiktok_ads.csv` | 1,500–5,000 | date, campaign, spend, impressions, clicks, ctr | TikTok daily performance |
| `youtube_ads.csv` | 2,000–7,000 | date, campaign, spend, impressions, views, view_rate | YouTube daily performance |
| `linkedin_ads.csv` | 800–3,000 | date, campaign, spend, impressions, clicks, ctr, leads | LinkedIn daily performance |
| `tv_performance.csv` | 100–600 | date_week_start, region, spend, grps, reach, spots_aired | TV weekly by region |
| `ooh_performance.csv` | 50–300 | start_date, end_date, format, spend, impressions | OOH campaign periods |
| `print_performance.csv` | 40–200 | date, publication, spend, reach | Print insertion schedule |
| `radio_performance.csv` | 20–120 | start_date, end_date, station, spend, spots_aired | Radio flight schedule |
| `vehicle_sales.csv` | 2,000–8,000 | date, model, market, dealer_id, price_gbp | Unit sales transactions |
| `website_analytics.csv` | 2,500–8,000 | date, sessions, source, pageviews | Website traffic daily |
| `configurator_sessions.csv` | 5,000–20,000 | date, model, completed | Online vehicle configurator usage |
| `leads.csv` | 4,000–16,000 | created_date, source, stage, dealer_id | Lead pipeline with funnel stage |
| `test_drives.csv` | 3,000–13,000 | booking_date, dealer_id, lead_id, outcome | Test drive bookings and results |
| `competitor_spend.csv` | 100–600 | year_month, brand, estimated_spend_gbp | Monthly competitor media spend |
| `economic_indicators.csv` | 12–60 | year_month, bank_rate_pct, consumer_confidence_index, cpi_index | Monthly UK economic data |
| `events.csv` | 8–30 | start_date, name, type, spend | Events calendar |
| `sla_tracking.csv` | 20–100 | year_month, metric, target, actual | Vendor SLA compliance |
| 7 vendor contracts (.md) | — | — | ITV, Sky, JCDecaux, ClearChannel, Channel4, Sky BVOD, Media Agency |

**MMM-ready aggregated datasets** (in `data/mmm/`):

| File | Dimensions | Content |
|------|-----------|---------|
| `weekly_channel_spend.csv` | 52 weeks x 12 columns | Weekly spend per channel + total |
| `weekly_sales.csv` | 52 weeks x ~8 columns | Weekly units, revenue, test drives, leads, web sessions |
| `model_ready.csv` | 52 weeks x 30+ columns | Joined spend + sales + adstock transforms + economic indicators + competitor spend + seasonal index |

---

## 3. RAG: Natural-Language Access to Marketing Knowledge

### The Problem

A marketing team managing 11 channels, 50 dealers, and £20M in spend generates thousands of data points and dozens of documents. Answering cross-document questions today requires manually locating the right file, finding the right row or paragraph, and piecing together an answer. This is slow, error-prone, and limits who can access insights.

### How RAG Works

```
 Documents               Chunks + Embeddings        Index              Query + Response
┌──────────────┐        ┌──────────────────┐     ┌──────────┐     ┌──────────────────────┐
│ CSVs         │───────>│ Split documents   │────>│ Vector   │────>│ User asks a question │
│ Contracts    │ Stage 1│ into chunks,      │  S2 │ store    │  S3 │ in plain English;    │
│ Reports      │        │ compute vector    │     │ (indexed │     │ system retrieves     │
│ Competitor   │        │ embeddings for    │     │  for     │     │ relevant chunks and  │
│ intel        │        │ each chunk        │     │  search) │     │ generates an answer  │
└──────────────┘        └──────────────────┘     └──────────┘     └──────────────────────┘
                         Stage 1–2                 Stage 3          Stage 4
```

**Stage 1 — Document Processing**: Raw files (CSVs, markdown contracts, reports) are parsed and split into manageable chunks (default: 1,024 tokens with 50-token overlap).

**Stage 2 — Embedding Generation**: Each chunk is converted into a numerical vector using OpenAI's `text-embedding-3-small` model. These vectors capture semantic meaning — similar content produces similar vectors.

**Stage 3 — Index & Retrieval**: Vectors are stored in a searchable index. When a user asks a question, the system converts the question into a vector and finds the most relevant chunks.

**Stage 4 — Response Generation**: Retrieved chunks are passed to a large language model (Claude Opus 4.6) which synthesises a coherent answer grounded in the actual data.

### Digital Marketing Use Cases

These are example queries the platform will support, grounded in the actual synthetic dataset:

**Campaign Performance**
- *"What are our CPM benchmarks for Meta vs YouTube?"*
  → Meta CPM ranges £3.50–£16.00; YouTube CPM ranges £6.00–£15.00 (from `config.py` benchmarks)
- *"Which digital channels had the highest click-through rates?"*
  → Google Search leads at 2–6% CTR, followed by TikTok at 0.5–1.8% (from `DIGITAL_BENCHMARKS`)

**Contract Intelligence**
- *"Summarise the ITV airtime contract terms and cost-per-thousand rates"*
  → Pulls from `ITV_Airtime_Agreement.md` vendor contract
- *"What are the SLA terms in the JCDecaux OOH contract?"*
  → Searches `JCDecaux_OOH_Contract.md` for service level clauses

**Sales Pipeline**
- *"Which dealers had the highest lead-to-sale conversion in Q4?"*
  → Cross-references `leads.csv` and `vehicle_sales.csv` by `dealer_id`
- *"What's the configurator-to-test-drive conversion rate for the DEEPAL S07?"*
  → Joins `configurator_sessions.csv` and `test_drives.csv`

**Competitive Intelligence**
- *"What were competitor spend levels during our launch month (September)?"*
  → Retrieves from `competitor_spend.csv` — e.g., BMW £2M–£4M/month, Tesla £800K–£2M/month
- *"How does our LinkedIn CPM compare to industry benchmarks?"*
  → Our range: £20–£45 CPM (from `DIGITAL_BENCHMARKS`)

### Seven Retrieval Strategies

The platform implements seven retrieval approaches, each suited to different query types:

| Strategy | How It Works | Best For |
|----------|-------------|----------|
| **Vector** | Semantic similarity search across all chunks | General questions, exploratory queries |
| **Summary** | Searches document-level summaries first, then drills into chunks | "Summarise the TV contract" — broad document questions |
| **Recursive** | Follows parent-child relationships between document sections | Multi-section documents like vendor contracts |
| **Metadata** | Filters by structured attributes (channel, date, market) before searching | "Meta campaigns in September" — scoped queries |
| **Chunk Decoupling** | Embeds smaller sub-chunks but retrieves the full parent chunk for context | When precision and context both matter |
| **Hybrid** | Combines vector similarity with BM25 keyword matching | Queries with specific terms (campaign IDs, dealer names) |
| **Planner** | LLM decomposes complex queries into sub-queries, runs each, then merges | Multi-part questions that span different data sources |

### Technology Stack

- **Framework**: LlamaIndex (orchestration, chunking, index management)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **LLM**: Claude Opus 4.6 (response generation)
- **Chunk size**: 1,024 tokens, 50-token overlap

---

## 4. MMM: Data-Driven Budget Optimisation

### The Problem

With £20M spread across 11 channels, the marketing team needs to answer: *Which channels are actually driving sales, and how should we reallocate budget?* Traditional reporting shows correlation (spend went up, sales went up) but not causation. MMM uses statistical modeling to isolate each channel's true contribution.

### How MMM Works

```
Weekly Data                 Transforms               Regression           Outputs
┌───────────────┐    ┌────────────────────┐    ┌──────────────┐    ┌──────────────────┐
│ Channel spend │───>│ Adstock: model     │───>│ Fit model:   │───>│ Channel ROI      │
│ (11 channels) │    │ carryover effects  │    │ which inputs │    │ Contribution %   │
│               │    │                    │    │ predict      │    │ Marginal returns │
│ Sales units   │    │ Saturation: model  │    │ sales?       │    │ Optimal budget   │
│ (weekly)      │    │ diminishing returns│    │              │    │ allocation       │
│               │    │                    │    │              │    │                  │
│ External      │    │ Seasonal index     │    │              │    │ What-if          │
│ factors       │    │                    │    │              │    │ scenarios        │
└───────────────┘    └────────────────────┘    └──────────────┘    └──────────────────┘
```

### Key Concepts Explained

**Adstock (Carryover Effect)**
A TV ad doesn't only affect sales on the day it airs — its impact decays over subsequent weeks. Adstock models this memory effect with a decay rate:

| Channel | Decay Rate | Meaning |
|---------|-----------|---------|
| TV | 0.85 | Very long carryover — 85% of impact carries to next week |
| Events | 0.80 | Strong residual effect from live experiences |
| Print | 0.75 | Magazine/newspaper ads have lasting shelf life |
| OOH | 0.70 | Billboard exposure accumulates over campaign period |
| Radio | 0.65 | Moderate carryover from repeated audio exposure |
| YouTube | 0.60 | Video content has moderate staying power |
| DV360 | 0.55 | Programmatic display decays moderately |
| Meta | 0.50 | Social feed content is replaced quickly |
| LinkedIn | 0.50 | Professional feed — similar to Meta |
| TikTok | 0.45 | Short-form video has fast turnover |
| Google | 0.40 | Search is intent-driven, minimal carryover |

Formula: `adstock[t] = spend[t] + decay_rate × adstock[t-1]`

**Saturation (Diminishing Returns)**
The first £1M on TV has more impact than the sixth £1M. The Hill saturation function models this ceiling effect using two parameters per channel (alpha for steepness, gamma for the inflection point).

Formula: `saturation(x) = x^alpha / (x^alpha + gamma^alpha)`

**Seasonal Index**
A multiplier applied per month to account for known demand patterns (e.g., September launch month = 2.5x; January post-holiday = 0.3x).

### Digital Marketing Use Cases

**ROI Measurement**
- *"What is the marginal ROI of an extra £100K on TikTok vs TV?"*
  → Compare channel response curves at current spend levels
- *"How much sales lift did September's launch spend on Meta generate?"*
  → Isolate Meta's contribution during launch month using the adstock-transformed spend

**Budget Optimisation**
- *"What's the optimal budget split across 11 channels for Q1 2026?"*
  → Run the optimiser with a total budget constraint and channel-level min/max bounds
- *"If we cut radio budget by 50%, what's the expected sales impact?"*
  → Simulate the scenario using fitted response curves

**Channel Dynamics**
- *"What is the carryover effect of TV spend vs digital?"*
  → TV (0.85 decay) vs Google (0.40 decay) — TV impact persists roughly twice as long
- *"Which channels are approaching saturation at current spend levels?"*
  → Compare current spend to the saturation inflection point per channel

### Technology Stack

- **Statistical modeling**: statsmodels (OLS/Bayesian regression)
- **Machine learning**: scikit-learn (feature engineering, cross-validation)
- **Transforms**: Custom `apply_adstock()` and `apply_saturation()` functions
- **Data**: 52-week aggregated datasets with 11 spend channels + sales + external factors

---

## 5. Platform Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                               │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────────┐ │
│  │  RAG Chat    │  │  MMM Dashboard   │  │  Data Management      │ │
│  │  /rag        │  │  /mmm            │  │  /data                │ │
│  └──────┬───────┘  └────────┬─────────┘  └───────────┬───────────┘ │
│         │  React + Vite (port 3001)                   │            │
└─────────┼──────────────────┼──────────────────────────┼────────────┘
          │                  │                          │
          ▼                  ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI (port 8000)                              │
│  /health  /api/raw/dashboard/summary  /api/raw/dashboard/files      │
│  /api/raw/dashboard/prd-checks  /api/raw/dashboard/file/{name}      │
└─────────┬──────────────────┬──────────────────────────┬────────────┘
          │                  │                          │
          ▼                  ▼                          ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐
│  RAG Pipeline    │ │  MMM Pipeline    │ │  Data Generators         │
│  (LlamaIndex)    │ │  (statsmodels)   │ │  (config.py → 7 modules) │
│  4 stages        │ │  3 stages        │ │  19 CSVs + 7 contracts   │
│  7 strategies    │ │  Adstock/Sat.    │ │  + 3 MMM-ready datasets  │
│  [scaffolded]    │ │  [scaffolded]    │ │  [complete]              │
└──────────────────┘ └──────────────────┘ └──────────────────────────┘
```

### Component Status

| Component | Location | Status | Key Files |
|-----------|----------|--------|-----------|
| **Platform UI** | `ui/platform/` | Complete | `App.jsx` (sidebar + router), `pages/RagChat.jsx`, `pages/MmmDashboard.jsx`, `pages/DataManagement.jsx` |
| **Raw Data Dashboard** | `ui/raw-data-dashboard/` | Complete | Standalone Vite app (port 3000) |
| **API Server** | `src/platform/api/` | Complete | `main.py` (FastAPI), `data_profiles.py` |
| **Data Generators** | `data/generators/` | Complete | `config.py`, `digital_media.py`, `traditional_media.py`, `sales_pipeline.py`, `contracts.py`, `events.py`, `external_data.py` |
| **Data Validators** | `data/generators/validators.py` | Complete | 10 validation checks + MMM aggregation |
| **RAG Pipeline** | `src/rag/` | Scaffolded | `data_processing/`, `embeddings/`, `retrieval/`, `common/` |
| **MMM Pipeline** | `src/mmm/` | Scaffolded | `data_ingestion/`, `modeling/`, `optimization/`, `common/` |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Styled landing page with service status (supports light/dark theme) |
| `/health` | GET | JSON health check: `{"status": "ok"}` |
| `/docs` | GET | Auto-generated Swagger API documentation |
| `/api/raw/dashboard/summary` | GET | Full data inventory with file profiles and PRD checks |
| `/api/raw/dashboard/files` | GET | File listing with row counts and sizes |
| `/api/raw/dashboard/prd-checks` | GET | PRD conformance check results |
| `/api/raw/dashboard/file/{name}` | GET | Preview rows from a specific data file (param: `rows=1..200`) |

### UI Pages

| Page | Route | Description |
|------|-------|-------------|
| **RAG Chat** | `/rag` | Conversational interface with suggested queries, chat history, markdown response rendering |
| **MMM Dashboard** | `/mmm` | KPI cards (11 channels, £20M budget), channel table with budget and status, placeholder for model outputs |
| **Data Management** | `/data` | Dataset inventory with category badges, row counts, status indicators, live API integration |

### Environment Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | (required) | API key for embeddings |
| `CHUNK_SIZE` | 1024 | Token count per document chunk |
| `CHUNK_OVERLAP` | 50 | Token overlap between consecutive chunks |
| `EMBED_MODEL` | text-embedding-3-small | OpenAI embedding model |
| `LLM_MODEL` | claude-opus-4-6 | Language model for RAG responses |
| `MMM_DATE_COLUMN` | date | Date column name for MMM input |
| `MMM_TARGET_COLUMN` | sales | Target variable for MMM regression |
| `MMM_ADSTOCK_MAX_LAG` | 8 | Maximum lag weeks for adstock transform |

---

## 6. Data Pipeline Deep-Dive

### Generator Architecture

All generators import from a single source of truth — `data/generators/config.py` — which defines:

- **Seed** (42) for reproducibility
- **Date range** (1 Jan – 31 Dec 2025)
- **Budget allocations** per channel (summing to exactly £20M, assertion-checked)
- **Channel benchmarks** (CPM, CTR, CPC ranges per channel)
- **Seasonal multipliers** (monthly weights, normalised)
- **50 UK dealers** with region, group, launch status, and capacity
- **Campaign naming templates** per channel and objective
- **Adstock decay rates** and **saturation parameters** per channel

### Generation Pipeline (7 Steps)

The orchestrator (`generate_all.py`) runs generators in dependency order:

1. **Load configuration** — master config with all constants
2. **External data** — economic indicators (bank rate, CPI, consumer confidence), competitor spend (10 brands)
3. **Events calendar** — 17 UK events (motor shows, launch events, dealer roadshows, promotions)
4. **Digital media** — 6 CSVs: Meta, Google, DV360, TikTok, YouTube, LinkedIn (daily granularity)
5. **Traditional media** — 4 CSVs: TV (weekly by region), OOH (campaign periods), Print (per insertion), Radio (flight schedule)
6. **Sales pipeline** — 5 CSVs: vehicle sales, website analytics, configurator sessions, leads, test drives (reads generated media data for causal chain)
7. **Vendor contracts** — 7 markdown documents: ITV, Sky, Sky BVOD, JCDecaux, ClearChannel, Channel4, Media Agency

### Causal Chain

The synthetic data models a realistic cause-and-effect relationship:

```
Media Spend (11 channels)
    │
    ▼
Website Sessions (organic + paid traffic)
    │
    ▼
Configurator Sessions (online vehicle configuration)
    │
    ▼
Leads (multiple sources: web, dealer, chat, social, events)
    │
    ▼
Test Drives (booked and completed)
    │
    ▼
Vehicle Sales (by model, market, dealer, trim, finance type)
```

The `sales_pipeline.py` generator reads the already-generated media CSVs to ensure spend levels causally influence downstream funnel metrics.

### Digital Channel Benchmarks

| Channel | CPM (£) | CTR | CPC (£) | Conv. Rate |
|---------|---------|-----|---------|------------|
| Meta | 3.50 – 16.00 | 0.8% – 2.5% | 0.40 – 1.80 | 1.0% – 4.0% |
| Google | 3.00 – 10.00 | 2.0% – 6.0% | 0.50 – 3.50 | 2.0% – 6.0% |
| DV360 | 2.00 – 8.00 | 0.3% – 1.2% | 0.30 – 1.50 | 0.5% – 2.0% |
| TikTok | 4.00 – 10.00 | 0.5% – 1.8% | 0.30 – 1.20 | 0.8% – 2.5% |
| YouTube | 6.00 – 15.00 | 0.4% – 1.2% | — | — |
| LinkedIn | 20.00 – 45.00 | 0.3% – 1.0% | 3.00 – 8.00 | 1.0% – 3.5% |

YouTube uses cost-per-view (£0.02–£0.08) and view rate (25%–55%) as primary metrics instead of CPC/conversion rate.

### Traditional Channel Benchmarks

| Channel | Key Metric | Range |
|---------|-----------|-------|
| TV (30s spot) | Cost per spot | £20,000 – £45,000 |
| TV (60s spot) | Cost per spot | £35,000 – £80,000 |
| OOH | Cost per panel/week | £200 – £2,000 |
| Print | Cost per page | £5,000 – £30,000 |
| Radio (30s spot) | Cost per spot | £100 – £800 |

### Validation Framework (10 Checks)

| # | Check | What It Verifies |
|---|-------|-----------------|
| 1 | File existence | All 19 CSVs and 7 contracts are present |
| 2 | Row counts | Each file has rows within expected ranges |
| 3 | Budget totals | Total spend within 5% of £20M; per-channel within 15% |
| 4 | Sales totals | Unit sales by market match expectations (~2,800 GB, ~1,200 DE, ~600 FR) |
| 5 | Date ranges | All dates fall within 2025 |
| 6 | Foreign keys | No orphaned dealer_ids or lead_ids across tables |
| 7 | Conversion funnel | Each pipeline stage has fewer records than the previous stage |
| 8 | Seasonal patterns | September/October appear in top 3 spend and sales months |
| 9 | No negative values | Spend, impressions, clicks, and similar columns have no negatives |
| 10 | CTR consistency | Calculated CTR (clicks/impressions) matches reported CTR within 1% |

### MMM-Ready Data Preparation

The validator module also produces 3 aggregated datasets for modeling:

- **`weekly_channel_spend.csv`** — 52 weeks x 11 channel spend columns + total. Digital channels aggregated from daily CSVs; traditional channels mapped from campaign-period data.
- **`weekly_sales.csv`** — 52 weeks with units sold (total + per market), revenue, test drives, leads, web sessions.
- **`model_ready.csv`** — Joined spend + sales + adstock-transformed spend for all channels + economic indicators (bank rate, CPI, consumer confidence, BEV market share) + weekly competitor spend + seasonal index.

---

## 7. Roadmap & Next Steps

### Phase 1: Foundation (Current — Complete)

- [x] Synthetic data generators — 19 CSVs + 7 vendor contracts
- [x] Validation framework — 10 automated quality checks
- [x] MMM data aggregation — 3 weekly model-ready datasets
- [x] Platform UI — React + Vite with sidebar navigation, light/dark theme
- [x] Data Dashboard API — FastAPI with file inventory, previews, PRD checks
- [x] Raw Data Dashboard — standalone data inventory viewer
- [x] Reference documentation — LlamaIndex guides, RAG methodology docs

### Phase 2: RAG Pipeline (Next)

- [ ] Implement document processing — parse CSVs, markdown contracts, reports into LlamaIndex documents
- [ ] Build embedding pipeline — batch generate embeddings with `text-embedding-3-small`
- [ ] Create vector index — store and load from persistent index
- [ ] Implement 7 retrieval strategies with common interface
- [ ] Connect RAG Chat UI to live retrieval pipeline via API
- [ ] Evaluate retrieval quality (hit rate, MRR) across strategies

### Phase 3: MMM Pipeline

- [ ] Implement data ingestion — load weekly aggregated datasets
- [ ] Build adstock and saturation transforms with configurable parameters per channel
- [ ] Fit regression model (OLS baseline, then Bayesian)
- [ ] Extract channel contributions, ROI, and marginal response curves
- [ ] Implement budget optimiser with constraints
- [ ] Connect MMM Dashboard UI to model outputs via API

### Phase 4: Integration & Production

- [ ] Connect to real data sources (replace synthetic pipeline)
- [ ] Add authentication and role-based access
- [ ] Deploy API and UI to production environment
- [ ] Set up automated data refresh and model retraining
- [ ] Integrate RAG + MMM — e.g., ask natural-language questions about model outputs

---

*This memo covers the rag-mmm-platform project as of February 2026. For technical setup and commands, see the project [CLAUDE.md](../CLAUDE.md). For the raw data dashboard specification, see [docs/prd/](prd/).*
