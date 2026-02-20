# ADDENDUM TO MEDIA SALES AGREEMENT
## BVOD AND ADSMART TARGETING SPECIFICATION

**Reference:** SKY-DEEPAL-2025-4291-ADD-01
**Parent Agreement:** Sky Media Sales Agreement dated 1 August 2025
**Effective Date:** 1 August 2025

This Addendum supplements and forms part of the Media Sales Agreement between Sky UK Limited (Sky Media) and DEEPAL UK Ltd. In the event of conflict between this Addendum and the Parent Agreement, the terms of this Addendum shall prevail in relation to BVOD and AdSmart matters.

---

## 1. PURPOSE

1.1 This Addendum sets out the detailed technical and operational specifications for the delivery of BVOD and AdSmart campaigns under the Parent Agreement, including advanced targeting configurations, creative specifications, measurement methodology, and data handling procedures.

## 2. ADVANCED TARGETING CONFIGURATIONS

### 2.1 Layered Targeting

2.1.1 The Advertiser may combine up to **3 targeting layers** simultaneously:

| Layer | Options | Example |
|-------|---------|---------|
| Layer 1: Demographic | Age, gender, HH income | ABC1 Adults 25-54 |
| Layer 2: Behavioural | Viewing habits, purchase intent | Auto Intenders + EV Interest |
| Layer 3: Geographic | Region, postcode, DMA | Top 15 dealer postcodes |

2.1.2 Each additional targeting layer reduces estimated reach by approximately 40-60%.

2.1.3 Minimum viable audience size for AdSmart: **200,000 households** after all targeting layers applied.

### 2.2 Sequential Messaging

2.2.1 The Broadcaster offers sequential creative delivery ("storytelling") across AdSmart:

- **Step 1 (Awareness):** 30-second brand introduction — delivered to full target audience;
- **Step 2 (Consideration):** 30-second product feature — delivered to households that viewed Step 1;
- **Step 3 (Action):** 15-second call-to-action — delivered to households that viewed Steps 1 and 2.

2.2.2 Minimum interval between sequential steps: **48 hours**.

2.2.3 Maximum decay between steps: **14 days** (households not reached within 14 days are excluded from subsequent steps).

### 2.3 Competitive Exclusion

2.3.1 The Broadcaster guarantees that no other automotive advertiser shall be served within the same AdSmart pod as the Advertiser's creative.

2.3.2 For the launch week (1-7 September 2025), the Advertiser shall have exclusive access to the "Auto Intenders" and "EV Interest" AdSmart segments within Sky Sports and Sky Atlantic programming.

### 2.4 Daypart Controls

2.4.1 AdSmart delivery may be restricted to specific dayparts:

| Daypart | Hours | Index (Auto) |
|---------|-------|-------------|
| Morning | 06:00 – 09:30 | 85 |
| Daytime | 09:30 – 17:30 | 70 |
| Early Peak | 17:30 – 20:00 | 120 |
| Peak | 20:00 – 22:30 | 145 |
| Late Peak | 22:30 – 00:00 | 110 |
| Overnight | 00:00 – 06:00 | 40 |

2.4.2 The Advertiser requests a weighting towards Early Peak and Peak dayparts, with a minimum of **65%** of impressions delivered between 17:30 and 22:30.

## 3. CREATIVE SPECIFICATIONS

### 3.1 Video Formats

| Attribute | Specification |
|-----------|--------------|
| File Format | MP4 (H.264/H.265) |
| Resolution | 1920x1080 (Full HD) minimum |
| Aspect Ratio | 16:9 |
| Frame Rate | 25fps (PAL) |
| Audio | Stereo, -24 LKFS (EBU R128) |
| Max File Size | 500MB per creative |
| Spot Lengths | 10s, 15s, 20s, 30s, 60s |

### 3.2 AdSmart-Specific Requirements

3.2.1 All AdSmart creatives must include a **2-second static end frame** containing the brand logo and URL, to ensure legibility during any buffering or transition delay.

3.2.2 Creatives must not contain:
- (a) Flashing images exceeding 3 flashes per second (Ofcom/Harding test);
- (b) QR codes (due to screen resolution variance across devices);
- (c) Time-limited offers shorter than 7 days (due to delivery lag).

### 3.3 Interactive Overlay

3.3.1 AdSmart supports clickable overlay elements on Sky Glass devices:
- "Learn More" CTA linking to a microsite;
- "Book a Test Drive" CTA linking to dealer locator;
- "Watch Full Film" CTA for extended content.

3.3.2 Interactive overlays are charged at £3.00 CPM premium above standard AdSmart rates.

## 4. MEASUREMENT AND ATTRIBUTION

### 4.1 Primary Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| Completion Rate | % of impressions viewed to 100% | ≥ 90% |
| Viewability (BVOD) | MRC standard, 50% pixels/2 seconds | ≥ 95% |
| On-Target % (AdSmart) | % delivered to specified segment | ≥ 90% |
| Frequency | Avg. exposures per reached HH | 4-6x |
| Incremental Reach | Additional reach vs. linear only | Report |

### 4.2 Attribution Methodology

4.2.1 The Broadcaster shall provide a matched panel attribution study at no additional charge, measuring:
- Website visit uplift (via pixel-matched panel);
- Search query uplift (via partnership with search data provider);
- Footfall uplift to dealer locations (via partnership with location data provider);
- Sales correlation analysis (subject to Advertiser providing anonymised sales data).

4.2.2 Panel size: minimum 200,000 matched households (exposed vs. control).

4.2.3 The attribution study shall be delivered within **6 weeks** of campaign completion.

### 4.3 Cross-Platform Deduplication

4.3.1 The Broadcaster shall use CFlight methodology to provide deduplicated reach and frequency across:
- Sky linear channels;
- AdSmart (addressable);
- Sky Go / NOW (BVOD);
- ITVX (where co-invested under separate ITV agreement).

## 5. DATA HANDLING

### 5.1 Clean Room Environment

5.1.1 All first-party data matching shall be conducted within Sky's clean room environment, operated on the InfoSum platform.

5.1.2 Data matching process:
- (a) Advertiser uploads hashed customer identifiers (email SHA-256 or mobile SHA-256);
- (b) Sky matches against subscriber base within the clean room;
- (c) Match rates and segment sizes are returned without exposing individual records;
- (d) Matched segments are activated for AdSmart targeting within 48 hours.

5.1.3 Minimum viable segment size post-matching: **50,000 households**.

### 5.2 Data Retention

5.2.1 Advertiser data within the clean room shall be purged **30 days** after the campaign end date unless otherwise agreed in writing.

5.2.2 Campaign performance data (aggregated, non-PII) shall be retained for **24 months** for benchmarking and optimisation purposes.

## 6. OPERATIONAL SLA

| Metric | SLA | Remedy |
|--------|-----|--------|
| Campaign setup (from brief) | 5 working days | Escalation to Head of Ad Ops |
| Creative QA | 2 working days | Express lane available |
| Targeting change requests | 3 working days | N/A |
| Reporting dashboard uptime | 99.5% | Monthly credit for downtime |
| Issue resolution (P1 critical) | 4 hours | Dedicated account manager |
| Issue resolution (P2 standard) | 24 hours | Standard support queue |

## 7. ACCEPTANCE

This Addendum is accepted and forms part of the Parent Agreement.

**SIGNED** for and on behalf of **Sky UK Limited (Sky Media)**:

Name: ________________________
Title: Head of AdSmart & Advanced Advertising
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Head of Media, UK & Europe
Date: ________________________
