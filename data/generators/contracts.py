"""
Generate vendor contract documents as markdown files for RAG pipeline testing.

Produces 7 contracts in data/raw/contracts/:
    ITV_Airtime_Agreement.md
    Sky_Airtime_Agreement.md
    Sky_BVOD_Addendum.md
    JCDecaux_OOH_Contract.md
    ClearChannel_DOOH_Agreement.md
    Channel4_Media_Partnership.md
    MediaAgency_Terms_of_Business.md

Each contract: 3-8 pages equivalent, formal legal language, clause numbering,
specific commercial terms, appendices.
"""

import os

from data.generators.config import CONTRACTS_DIR


# ============================================================================
# Contract content generators
# ============================================================================

def _itv_airtime_agreement() -> str:
    return """# AIRTIME PURCHASE AGREEMENT

**Between:**
ITV plc ("the Broadcaster")
2 Waterhouse Square, 140 Holborn, London EC1N 2AE
Company No. 04967001

**And:**
DEEPAL UK Ltd ("the Advertiser")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Effective Date:** 1 July 2025
**Expiry Date:** 31 December 2025
**Agreement Reference:** ITV-DEEPAL-2025-0847

---

## 1. DEFINITIONS AND INTERPRETATION

1.1 In this Agreement, unless the context otherwise requires:

- **"Airtime"** means the broadcast advertising time purchased hereunder across ITV1, ITV2, ITVX, ITV3, ITV4, ITVBe and any successor channel;
- **"BVOD"** means Broadcaster Video on Demand, specifically the ITVX streaming platform;
- **"Campaign Period"** means the period from 1 August 2025 to 31 December 2025;
- **"Copy"** means the advertising material supplied by the Advertiser in conformity with Clearcast requirements;
- **"CPT"** means Cost Per Thousand adult viewers (16+);
- **"GRP"** means Gross Rating Point as measured by BARB;
- **"ITVX"** means the ITV streaming platform, formerly ITV Hub;
- **"Make-Good"** means the provision of replacement airtime where contracted delivery falls short;
- **"Pre-empt"** means the displacement of a booked spot by a higher-paying advertiser;
- **"TVR"** means Television Rating as measured by BARB;
- **"SOB"** means Share of Broadcast (share of category airtime).

1.2 Headings are for convenience only and shall not affect interpretation.

1.3 References to statutes include any statutory modification or re-enactment thereof.

## 2. SCOPE OF AGREEMENT

2.1 The Broadcaster agrees to sell, and the Advertiser agrees to purchase, airtime across ITV linear channels and ITVX as detailed in Schedule A.

2.2 This Agreement covers both linear broadcast and BVOD inventory, consolidated under a single trading arrangement.

2.3 The total contract value shall not exceed **£3,300,000** (Three Million Three Hundred Thousand Pounds Sterling), apportioned as follows:

| Component | Budget (GBP) | Share |
|-----------|-------------|-------|
| ITV1 Peak | £1,200,000 | 36.4% |
| ITV1 Off-Peak | £500,000 | 15.2% |
| ITV2/ITV3/ITV4 Portfolio | £400,000 | 12.1% |
| ITVX Pre-Roll | £500,000 | 15.2% |
| ITVX Mid-Roll | £200,000 | 6.1% |
| ITVX Sponsorship/Skins | £100,000 | 3.0% |
| Sponsorship (Linear) | £400,000 | 12.1% |
| **Total** | **£3,300,000** | **100%** |

## 3. COMMERCIAL TERMS

3.1 **Pricing Mechanism.** All linear airtime shall be traded on a CPT basis using the ITV Rate Card 2025 (Revision 3, dated 1 April 2025) less the discounts specified in Clause 3.2.

3.2 **Discount Structure:**

| Commitment Level | Linear Discount | BVOD Discount |
|-----------------|----------------|---------------|
| £1M – £2M | 15% | 10% |
| £2M – £3M | 20% | 12% |
| £3M+ | 25% | 15% |

3.3 Based on the total commitment of £3,300,000, the Advertiser qualifies for the **25% linear discount** and **15% BVOD discount** tiers.

3.4 **CPT Guarantees.** The Broadcaster guarantees the following maximum CPTs for the Campaign Period:

- ITV1 Peak (Adults 16-54): **£12.50**
- ITV1 Peak (All Adults): **£8.00**
- ITV1 Off-Peak (All Adults): **£4.50**
- Portfolio (All Adults): **£3.00**
- ITVX Pre-Roll (Adults 16-54): **£18.00**
- ITVX Mid-Roll (Adults 16-54): **£14.00**

3.5 **Volume Bonus.** If actual spend exceeds £3,000,000 by 31 December 2025, an additional 3% retrospective discount shall be applied across all linear bookings.

3.6 **Agency Commission.** Agency commission of 3% is included within all rates quoted and shall be payable to the Advertiser's appointed media agency (see Clause 11).

## 4. DELIVERY AND SCHEDULING

4.1 The Broadcaster shall schedule spots in accordance with the agreed campaign plan (Schedule B), targeting a minimum delivery of **95%** of contracted GRPs per month.

4.2 **Scheduling Priorities:**
- (a) Launch Week (1-7 September 2025): guaranteed 100% delivery with no pre-emption;
- (b) Peak months (September-November): minimum 3 spots per evening across ITV1;
- (c) Roadblock opportunities: first refusal for simultaneous transmission across ITV1/ITV2/ITVX during launch week.

4.3 **Spot Lengths.** The Advertiser may use the following spot lengths:
- 60-second (hero creative) — maximum 30% of total spots
- 30-second (standard) — minimum 50% of total spots
- 10-second (reminder) — maximum 20% of total spots

4.4 **Copy Rotation.** The Broadcaster shall rotate up to 5 (five) different copy versions per week across the schedule as directed by the Advertiser's agency.

## 5. BVOD SPECIFIC TERMS

5.1 ITVX inventory shall be served programmatically via the Broadcaster's ad server, with targeting capabilities as follows:
- (a) Demographic targeting (age, gender, socioeconomic group);
- (b) Geographic targeting (ITV region, postcode sector);
- (c) Contextual targeting (programme genre);
- (d) Behavioural targeting (auto intender segments, in-market audiences);
- (e) Frequency capping (configurable per user per day/week).

5.2 **Viewability Standard.** All BVOD impressions shall meet the MRC standard of 50% of pixels in view for a minimum of 2 continuous seconds.

5.3 **Completion Rate Target.** Video completion rates for ITVX pre-roll shall not fall below **85%**.

5.4 **Brand Safety.** The Broadcaster warrants that no Advertiser content shall appear adjacent to content rated 18+ or content containing extreme violence, explicit sexual content, or content that may reasonably be considered harmful to brand reputation.

## 6. REPORTING AND MEASUREMENT

6.1 The Broadcaster shall provide the following reports:

| Report | Frequency | Delivery |
|--------|-----------|----------|
| Spot delivery confirmation | Weekly | Email/Portal |
| BARB audience estimates | Monthly | CSV/Dashboard |
| ITVX campaign analytics | Weekly | Dashboard |
| Post-campaign evaluation | Per flight | PDF report |

6.2 All BARB data shall be based on consolidated 28-day viewing figures including BVOD playback.

6.3 The Advertiser may request an independent audit of delivery data at any time, with costs shared equally between the parties.

## 7. MAKE-GOOD AND COMPENSATION

7.1 If monthly GRP delivery falls below 95% of the contracted level, the Broadcaster shall provide make-good airtime within **5 working days** of notification, at no additional cost.

7.2 If make-good cannot be provided within the Campaign Period, a pro-rata credit shall be applied to the Advertiser's account at 110% of the under-delivered value.

7.3 **Pre-emption Compensation.** If the Advertiser's spots are pre-empted:
- (a) The Broadcaster shall provide 48 hours' notice where reasonably practicable;
- (b) Replacement spots of equivalent or greater value shall be offered within 7 days;
- (c) If no suitable replacement is available, a 120% credit shall be applied.

7.4 Technical failures resulting in non-transmission shall be compensated at 150% of the spot value.

## 8. PAYMENT TERMS

8.1 Invoices shall be issued monthly in arrears, based on actual spot transmissions confirmed by BARB.

8.2 Payment terms: **30 days** from date of invoice.

8.3 Late payment shall attract interest at the Bank of England base rate plus 4% per annum, calculated daily.

8.4 The Advertiser may withhold payment for any disputed spots pending resolution under Clause 7, provided written notice of dispute is given within 14 days of invoice receipt.

## 9. INTELLECTUAL PROPERTY

9.1 All Copy shall remain the intellectual property of the Advertiser.

9.2 The Advertiser grants the Broadcaster a non-exclusive licence to broadcast, stream, and archive the Copy for the purposes of fulfilling this Agreement and regulatory compliance (Ofcom retention requirements).

9.3 The Broadcaster shall not use the Copy for any purpose other than fulfilment of this Agreement without the Advertiser's prior written consent.

## 10. REGULATORY COMPLIANCE

10.1 The Advertiser warrants that all Copy shall comply with:
- (a) The UK Code of Broadcast Advertising (BCAP Code);
- (b) Clearcast clearance requirements;
- (c) The Communications Act 2003;
- (d) All applicable ASA rulings and guidance;
- (e) The Consumer Rights Act 2015 in relation to pricing claims.

10.2 The Advertiser shall obtain Clearcast approval for all Copy prior to submission of scheduling instructions.

10.3 The Broadcaster reserves the right to refuse or withdraw any Copy that does not meet regulatory requirements, with immediate effect and without liability.

## 11. AGENCY APPOINTMENT

11.1 The Advertiser confirms that [Agency Name TBC] is the appointed media buying agency for the duration of this Agreement.

11.2 The agency is authorised to issue scheduling instructions, approve make-goods, and receive reports on behalf of the Advertiser.

11.3 Notwithstanding the agency appointment, the Advertiser remains primarily liable for all payment obligations under this Agreement.

## 12. CONFIDENTIALITY

12.1 Both parties agree that the commercial terms of this Agreement, including pricing, discounts, and audience delivery data, are strictly confidential.

12.2 Neither party shall disclose Confidential Information to any third party without the prior written consent of the other, except:
- (a) To professional advisers under a duty of confidentiality;
- (b) As required by law, regulation, or court order;
- (c) To the appointed media agency (per Clause 11).

## 13. TERMINATION

13.1 Either party may terminate this Agreement by giving **60 days'** written notice.

13.2 The Broadcaster may terminate immediately if:
- (a) The Advertiser fails to pay any undisputed invoice within 60 days of the due date;
- (b) The Advertiser becomes insolvent or enters administration.

13.3 The Advertiser may terminate immediately if:
- (a) The Broadcaster fails to deliver more than 30% of contracted GRPs in any two consecutive months;
- (b) There is a material breach of brand safety provisions (Clause 5.4).

13.4 Upon termination, the Advertiser shall pay for all airtime transmitted up to the date of termination, and any pre-paid amounts for un-transmitted airtime shall be refunded within 30 days.

## 14. LIMITATION OF LIABILITY

14.1 Neither party's total aggregate liability under this Agreement shall exceed the total contract value (£3,300,000).

14.2 Neither party shall be liable for indirect, consequential, or special damages, including loss of profits, save in cases of fraud or wilful misconduct.

14.3 The limitations in this clause shall not apply to obligations of confidentiality (Clause 12) or indemnities (Clause 15).

## 15. INDEMNITY

15.1 The Advertiser shall indemnify and hold harmless the Broadcaster against any claims, damages, or costs arising from:
- (a) Breach of the Advertiser's warranties regarding Copy compliance;
- (b) Infringement of third-party intellectual property rights in the Copy;
- (c) Any misleading or unlawful claims made within the Copy.

## 16. FORCE MAJEURE

16.1 Neither party shall be liable for failure to perform obligations due to events beyond reasonable control, including but not limited to: natural disasters, government actions, pandemic restrictions, industrial action, or broadcast transmission failures caused by third-party infrastructure.

16.2 The affected party shall notify the other within 48 hours and use reasonable endeavours to mitigate the impact.

## 17. GOVERNING LAW AND DISPUTE RESOLUTION

17.1 This Agreement shall be governed by and construed in accordance with the laws of England and Wales.

17.2 Any dispute arising under this Agreement shall first be referred to senior management of both parties for resolution within 30 days.

17.3 If not resolved, disputes shall be referred to mediation under the Centre for Effective Dispute Resolution (CEDR) rules before either party may commence court proceedings.

17.4 The courts of England and Wales shall have exclusive jurisdiction.

---

## SCHEDULE A: CAMPAIGN PLAN SUMMARY

| Flight | Dates | Channels | Budget | Objective |
|--------|-------|----------|--------|-----------|
| Teaser | 1–31 Aug 2025 | ITV1, ITVX | £300,000 | Awareness build |
| Launch | 1–30 Sep 2025 | ITV1, ITV2, ITVX, Sponsorship | £1,200,000 | Launch impact |
| Sustain | 1–30 Oct 2025 | ITV1, ITVX | £600,000 | Consideration |
| Sustain | 1–30 Nov 2025 | ITV1, ITVX | £500,000 | Test drive conversion |
| AVATR/S05 | 1–31 Dec 2025 | ITV1, ITV2, ITVX | £700,000 | Portfolio awareness |

## SCHEDULE B: RATE CARD EXTRACT (POST-DISCOUNT)

| Daypart | Spot Length | Rate (Post 25% Disc.) | Target CPT |
|---------|------------|----------------------|-----------|
| ITV1 Peak | 30s | £26,250 | £8.00 |
| ITV1 Peak | 60s | £47,250 | £14.40 |
| ITV1 Off-Peak | 30s | £11,250 | £4.50 |
| ITV2 Peak | 30s | £3,750 | £3.00 |
| ITVX Pre-Roll | 30s | £15.30 CPM | £18.00 CPT |
| ITVX Mid-Roll | 30s | £11.90 CPM | £14.00 CPT |

---

**SIGNED** for and on behalf of **ITV plc**:

Name: ________________________
Title: Director of Advertising Revenue
Date: ________________________
Signature: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Marketing Director, UK & Europe
Date: ________________________
Signature: ________________________

**WITNESSED** by:

Name: ________________________
Address: ________________________
Date: ________________________
Signature: ________________________
"""


def _sky_airtime_agreement() -> str:
    return """# MEDIA SALES AGREEMENT

**Between:**
Sky Media, a division of Sky UK Limited ("the Broadcaster")
Grant Way, Isleworth, Middlesex, TW7 5QD
Company No. 02906991

**And:**
DEEPAL UK Ltd ("the Advertiser")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Effective Date:** 1 August 2025
**Expiry Date:** 31 December 2025
**Agreement Reference:** SKY-DEEPAL-2025-4291

---

## 1. DEFINITIONS

1.1 In this Agreement:

- **"AdSmart"** means Sky's addressable TV advertising technology enabling household-level targeting via the Sky set-top box and Sky Glass;
- **"CFlight"** means the cross-platform campaign measurement tool operated jointly by Sky, Channel 4, and ITV;
- **"Linear Airtime"** means conventional broadcast spots across Sky Sports, Sky Atlantic, Sky News, Sky Cinema, Sky One, and affiliated channels;
- **"Sky Go"** means Sky's streaming service for Sky subscribers including mobile, tablet, and connected TV access;
- **"Sky Glass"** means Sky's proprietary smart TV platform;
- **"BVOD Inventory"** means video advertising served across Sky Go, NOW TV, and Sky Glass on-demand;
- **"VOD"** means Video on Demand;
- **"Impression"** means a single served and verified ad view.

## 2. CONTRACT VALUE AND APPORTIONMENT

2.1 The total contract value is **£2,400,000** (Two Million Four Hundred Thousand Pounds), allocated as follows:

| Component | Budget (GBP) | Notes |
|-----------|-------------|-------|
| Sky Sports Linear | £600,000 | Premier League, F1, Golf |
| Sky Atlantic/Sky One | £400,000 | Drama & Entertainment |
| Sky News | £200,000 | News adjacency |
| Sky Cinema | £200,000 | Film premieres |
| AdSmart (Addressable) | £400,000 | Household-level targeting |
| Sky Go/NOW BVOD | £400,000 | Streaming pre-roll/mid-roll |
| Sponsorship | £200,000 | Programme sponsorship |
| **Total** | **£2,400,000** | |

## 3. ADSMART TARGETING SPECIFICATION

3.1 The Advertiser shall have access to the following AdSmart targeting attributes:

3.1.1 **Geographic:** Postcode-level targeting across 11.5 million Sky households.

3.1.2 **Demographic:** Age, gender, household composition, lifestage.

3.1.3 **Behavioural Segments (Experian Mosaic):**
- (a) "Prestige Positions" — affluent households, high disposable income;
- (b) "City Prosperity" — urban professionals, early tech adopters;
- (c) "Domestic Success" — families with children, multi-car households;
- (d) "Aspiring Homemakers" — younger couples, first car buyers.

3.1.4 **First-Party Data Segments:**
- Sky Auto Intenders (based on Sky content viewing of auto programming);
- Electric Vehicle Interest (based on EV-related content consumption);
- Premium Brand Affinity (based on subscription tier and viewing habits).

3.1.5 **Custom Segments:** The Advertiser may upload first-party data (CRM lists, website visitors) via Sky's clean room for matching against the Sky subscriber base, subject to a minimum match rate of 60%.

3.2 **Minimum Campaign Size for AdSmart:** £50,000 per flight, minimum 4-week duration.

3.3 **Targeting Accuracy Guarantee:** Sky guarantees a minimum **90%** on-target delivery rate for AdSmart campaigns, measured against the specified audience attributes.

## 4. PRICING AND DISCOUNTS

4.1 **Linear Pricing.** All linear spots are traded on a CPT basis per the Sky Media 2025 Rate Card (H2 edition), subject to the following discounts:

| Spend Tier | Discount |
|-----------|---------|
| £500K – £1M | 10% |
| £1M – £2M | 15% |
| £2M+ | 20% |

4.2 The Advertiser qualifies for the **20% discount tier** based on total commitment.

4.3 **AdSmart Pricing.** AdSmart inventory is priced on a CPM basis:

| Targeting Level | CPM (GBP) |
|----------------|----------|
| Broad demographic | £20.00 |
| Mosaic segment | £28.00 |
| Custom first-party | £35.00 |
| Postcode targeted | £32.00 |

4.4 **BVOD Pricing (Sky Go/NOW).**

| Format | CPM (GBP) |
|--------|----------|
| Pre-roll (15s/30s) | £22.00 |
| Mid-roll (30s) | £18.00 |
| Pause ads | £15.00 |
| Companion banner | £8.00 |

## 5. CAMPAIGN DELIVERY

5.1 **Linear Delivery Target.** The Broadcaster shall deliver a minimum of **95%** of contracted GRPs per calendar month, measured against BARB consolidated (28-day) data.

5.2 **AdSmart Delivery.** Impression delivery shall be reported weekly. The Broadcaster guarantees delivery of **100%** of contracted impressions within the flight period, subject to available inventory.

5.3 **Frequency Management.** Cross-platform frequency capping shall be applied using CFlight methodology:
- Maximum 8 exposures per household per week across all Sky platforms;
- Maximum 3 exposures per household per day;
- Sequential creative rotation available upon request.

5.4 **Premium Positioning.** The Advertiser shall receive:
- First-in-break positioning for a minimum of 40% of linear spots during launch month (September 2025);
- 100% share of voice within AdSmart automotive category during launch week (1-7 Sep);
- Guaranteed centre-break position for all 60-second spots.

## 6. SPONSORSHIP TERMS

6.1 The Advertiser shall sponsor **"Sky Sports F1 — Race Day"** for the period September to December 2025.

6.2 Sponsorship elements include:
- (a) Opening and closing bumpers (10 seconds each);
- (b) Programme junction idents;
- (c) Digital companion on Sky Sports app;
- (d) Social media amplification via @SkySportsF1;
- (e) Red button interactive feature.

6.3 Sponsorship budget: £200,000 inclusive of production costs for bumpers/idents (production delivered by Sky Creative).

6.4 The Advertiser shall have first refusal for renewal of this sponsorship for the 2026 season, exercisable by 31 October 2025.

## 7. REPORTING

7.1 The Broadcaster shall provide:

| Report | Frequency | Format |
|--------|-----------|--------|
| Linear spot log | Daily | CSV |
| AdSmart delivery dashboard | Real-time | Sky Portal |
| BARB audience estimates | Monthly | PDF + CSV |
| BVOD performance report | Weekly | Dashboard |
| CFlight cross-platform report | Monthly | PDF |
| Brand uplift study | Post-campaign | Research report |

7.2 A brand uplift study shall be conducted at no additional cost, measuring:
- Spontaneous and prompted brand awareness;
- Consideration;
- Test drive intent;
- Ad recall.

## 8. PAYMENT

8.1 Invoices shall be raised monthly in arrears based on actual delivery (BARB-confirmed for linear, impression-confirmed for digital).

8.2 Payment terms: **30 days** net.

8.3 All prices are exclusive of VAT, which shall be charged at the prevailing rate.

## 9. DATA AND PRIVACY

9.1 Where the Advertiser provides first-party data for AdSmart targeting, both parties shall comply with:
- (a) The UK General Data Protection Regulation (UK GDPR);
- (b) The Data Protection Act 2018;
- (c) The Privacy and Electronic Communications Regulations 2003 (PECR).

9.2 A separate Data Processing Agreement (DPA) shall be executed prior to any first-party data transfer.

9.3 Sky shall act as an independent data controller for the purposes of AdSmart targeting using its own subscriber data.

## 10. TERMINATION

10.1 Either party may terminate with **45 days'** written notice.

10.2 The Broadcaster may terminate immediately for non-payment exceeding 45 days past due.

10.3 Upon termination, undelivered AdSmart and BVOD impressions shall be refunded at cost within 30 days.

## 11. GENERAL

11.1 This Agreement shall be governed by the laws of England and Wales.

11.2 The entire agreement between the parties is contained herein and supersedes all prior negotiations and representations.

11.3 No amendment shall be effective unless in writing and signed by authorised representatives of both parties.

---

## APPENDIX 1: ADSMART SEGMENT DEFINITIONS

| Segment ID | Name | Description | Est. Reach |
|-----------|------|-------------|-----------|
| SKY-AUTO-001 | Auto Intenders | Heavy viewers of motoring content | 2.1M HH |
| SKY-AUTO-002 | EV Interest | Viewed EV-related content 3+ times in 90 days | 850K HH |
| SKY-PREM-001 | Premium Brand | Sky Q/Ultra subscribers, premium tier | 3.4M HH |
| SKY-DEMO-001 | ABC1 25-54 | Core demographic target | 4.8M HH |
| SKY-GEO-001 | Launch Markets | Top 15 dealer postcode areas | 1.2M HH |

## APPENDIX 2: CAMPAIGN FLIGHT PLAN

| Flight | Dates | Linear Budget | AdSmart Budget | BVOD Budget |
|--------|-------|--------------|---------------|-------------|
| Pre-Launch | 1-31 Aug | £200,000 | £100,000 | £100,000 |
| Launch | 1-30 Sep | £400,000 | £150,000 | £150,000 |
| Sustain 1 | 1-31 Oct | £200,000 | £80,000 | £80,000 |
| Sustain 2 | 1-30 Nov | £200,000 | £40,000 | £40,000 |
| Year-End | 1-31 Dec | £200,000 | £30,000 | £30,000 |

---

**SIGNED** for and on behalf of **Sky UK Limited (Sky Media)**:

Name: ________________________
Title: Head of Agency Sales
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Marketing Director, UK & Europe
Date: ________________________
"""


def _sky_bvod_addendum() -> str:
    return """# ADDENDUM TO MEDIA SALES AGREEMENT
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
"""


def _jcdecaux_ooh_contract() -> str:
    return """# OUT-OF-HOME ADVERTISING CONTRACT

**Between:**
JCDecaux UK Ltd ("the Media Owner")
Knightsbridge, 33 Golden Square, London W1F 9JT
Company No. 01894552

**And:**
DEEPAL UK Ltd ("the Advertiser")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Effective Date:** 1 July 2025
**Expiry Date:** 31 December 2025
**Contract Reference:** JCD-DEEPAL-2025-OOH-1192

---

## 1. RECITALS

1.1 The Media Owner is the leading out-of-home advertising company in the United Kingdom, operating a portfolio of street furniture, transport, and large-format advertising sites.

1.2 The Advertiser wishes to promote the launch of the DEEPAL and AVATR electric vehicle brands in the UK market through a strategic out-of-home advertising campaign.

1.3 The parties have agreed terms for the provision of OOH advertising inventory as set out herein.

## 2. DEFINITIONS

- **"DOOH"** means Digital Out-of-Home, being electronic/digital display screens;
- **"OOH"** means Out-of-Home advertising, including both static (classic) and digital formats;
- **"Panel"** means a single advertising face, whether classic or digital;
- **"Posting Period"** means the period during which creative is displayed, typically 2 weeks for classic and 1-2 weeks for digital campaigns;
- **"Share of Time"** means the percentage of display time allocated to the Advertiser on a digital screen;
- **"SOT"** means Share of Time;
- **"Route"** means the Outsmart/JCDecaux audience measurement methodology.

## 3. CONTRACT VALUE

3.1 The total contract value is **£1,800,000** (One Million Eight Hundred Thousand Pounds), detailed as follows:

| Format | Sites | Duration | Budget (GBP) |
|--------|-------|----------|-------------|
| 96-sheet Classic | 50 | 12 weeks (Jul–Sep) | £400,000 |
| 48-sheet Classic | 100 | 8 weeks (Aug–Sep) | £300,000 |
| Digital 6-sheet (Cityscape) | 500 | 16 weeks (Aug–Nov) | £350,000 |
| Digital Large Format (Storm/Cromwell) | 20 | 8 weeks (Sep–Oct) | £250,000 |
| Bus Shelter 6-sheet | 300 | 8 weeks (Sep–Oct) | £200,000 |
| Rail Station Digital | 50 | 12 weeks (Sep–Nov) | £150,000 |
| Airport (Heathrow T2, T5) | 15 | 16 weeks (Aug–Nov) | £100,000 |
| Special Build (Waterloo Motion) | 1 | 4 weeks (Sep) | £50,000 |
| **Total** | | | **£1,800,000** |

## 4. SITE SELECTION

4.1 The Advertiser and Media Owner have jointly agreed the site list attached as **Appendix A** (Site Schedule).

4.2 Site selection priorities:
- (a) Proximity to dealer locations (within 2km radius of the 15 launch dealers);
- (b) Major arterial routes into London, Manchester, Birmingham, Edinburgh, and Glasgow;
- (c) High dwell-time environments (rail stations, airports, shopping centres);
- (d) Competitor dealer proximity (targeting Tesla, BMW, Audi showroom areas).

4.3 **Site Substitution.** If any contracted site becomes unavailable due to planning, maintenance, or third-party action, the Media Owner shall offer a substitute site of equivalent or greater audience delivery (measured by Route contacts) within the same metropolitan area.

4.4 The Advertiser shall have the right to approve or reject any substitute site within **3 working days** of notification. Failure to respond shall be deemed acceptance.

## 5. CREATIVE SPECIFICATIONS

### 5.1 Classic (Static) Formats

| Format | Dimensions (mm) | Bleed | Resolution |
|--------|-----------------|-------|-----------|
| 96-sheet | 12192 x 3048 | 25mm | 150 DPI |
| 48-sheet | 6096 x 3048 | 25mm | 150 DPI |
| 6-sheet | 1200 x 1800 | 10mm | 300 DPI |
| Bus Shelter | 1200 x 1800 | 10mm | 300 DPI |

### 5.2 Digital Formats

| Format | Resolution (px) | File Format | Max Size |
|--------|----------------|-------------|---------|
| Digital 6-sheet | 1080 x 1920 | MP4/JPG | 50MB |
| Large Format (16:9) | 1920 x 1080 | MP4/JPG | 100MB |
| Storm (Portrait) | 1080 x 1920 | MP4/JPG | 100MB |
| Airport Digital | 3840 x 2160 | MP4/JPG | 200MB |

5.2.1 Digital creatives may include motion content up to **10 seconds** duration, with no audio.

5.2.2 Maximum of **6 creative executions** may be rotated per digital campaign, with day-part scheduling available.

### 5.3 Special Build — Waterloo Motion

5.3.1 The Waterloo Motion installation is a bespoke large-format digital canvas at London Waterloo Station (departures concourse).

5.3.2 Specifications: 40m x 3m LED wall, custom creative required.

5.3.3 The Media Owner shall provide creative production support at no additional charge for the Waterloo Motion installation, including:
- (a) Technical feasibility consultation;
- (b) Content adaptation for non-standard aspect ratio;
- (c) On-site installation supervision.

## 6. AUDIENCE MEASUREMENT

6.1 All audience data shall be based on the **Route** methodology (Outsmart industry standard), providing:
- Impacts (number of times a creative is seen);
- Reach (unique individuals seeing the creative);
- Frequency (average number of times each individual is exposed);
- Cover (percentage of target audience reached).

6.2 The Media Owner shall provide audience estimates at point of sale and post-campaign actuals for all static formats.

6.3 For digital formats, the Media Owner shall additionally provide:
- Verified play-out reports (number of actual plays per screen);
- Dwell time estimates;
- Footfall data from JCDecaux SmartBRIC sensors (where available).

## 7. DIGITAL SPECIFIC TERMS

7.1 **Share of Time.** Digital screens shall display the Advertiser's creative for the following SOT:

| Format | SOT | Loop Length | Plays/Hour |
|--------|-----|------------|-----------|
| Digital 6-sheet | 1/6 | 60 seconds | 10 |
| Large Format | 1/4 | 40 seconds | 15 |
| Rail Station | 1/6 | 60 seconds | 10 |
| Airport | 1/8 | 80 seconds | 7.5 |

7.2 **Full Motion.** Where available, the Advertiser may utilise full-motion video (10 seconds maximum, no audio) at an additional premium of 15% above standard digital rates.

7.3 **Dynamic Content.** The Media Owner supports dynamic creative optimisation (DCO) triggered by:
- Time of day;
- Weather conditions (temperature, rain);
- Traffic conditions;
- Live data feeds (subject to technical feasibility assessment).

7.4 **Programmatic.** The Advertiser may purchase a portion of digital inventory programmatically via the JCDecaux VIOOH platform, subject to minimum spend of £25,000 per flight.

## 8. POSTING AND MAINTENANCE

8.1 **Classic Posting.** All classic sites shall be posted within **3 working days** of the contracted start date.

8.2 **Posting Compliance.** The Media Owner guarantees a minimum **95%** posting compliance rate, defined as the percentage of sites correctly posted with the contracted creative within the contracted period.

8.3 **Site Maintenance.** The Media Owner shall:
- Inspect all sites within 7 days of posting;
- Repair or replace damaged classic panels within 5 working days;
- Maintain digital screens with uptime of **98%** or greater;
- Provide photographic evidence of posting upon request.

8.4 **Fly-Posting Protection.** The Media Owner shall take reasonable steps to prevent fly-posting or vandalism of classic sites and shall replace affected panels within 48 hours of notification.

## 9. PAYMENT

9.1 Payment shall be made in three instalments:
- 30% upon contract execution (£540,000);
- 40% on 1 September 2025 (£720,000);
- 30% on 1 November 2025 (£540,000).

9.2 Payment terms: **30 days** from invoice date.

9.3 VAT at the prevailing rate shall be added to all invoices.

## 10. CANCELLATION AND AMENDMENT

10.1 **Classic sites:** 8 weeks' notice required for cancellation or significant amendment.

10.2 **Digital sites:** 2 weeks' notice required, subject to availability for reallocation.

10.3 Cancellation charges:
- More than 8 weeks before posting: no charge;
- 4-8 weeks before posting: 25% of affected budget;
- 2-4 weeks before posting: 50%;
- Less than 2 weeks: 100%.

## 11. EXCLUSIVITY

11.1 The Media Owner shall not accept bookings from direct EV competitors (as defined in Appendix B) on any site within **500 metres** of the Advertiser's contracted sites during the Campaign Period.

11.2 Excluded competitors: Tesla, BYD, MG Motor, Polestar, NIO, Xpeng, Omoda.

## 12. GOVERNING LAW

12.1 This Contract shall be governed by the laws of England and Wales.

---

## APPENDIX A: SITE SCHEDULE (EXTRACT — TOP 30 SITES)

| Site ID | Location | Format | Facing | Route Impacts/2wk |
|---------|----------|--------|--------|-------------------|
| JCD-LON-001 | Cromwell Road, SW7 | 96-sheet Digital | East | 2,450,000 |
| JCD-LON-002 | A4 Hammersmith Flyover | 96-sheet Classic | West | 1,890,000 |
| JCD-LON-003 | Old Street Roundabout | Large Digital | North | 1,720,000 |
| JCD-LON-004 | Vauxhall Cross | 48-sheet Classic | South | 1,550,000 |
| JCD-LON-005 | Waterloo Station | Motion Wall | All | 3,200,000 |
| JCD-MAN-001 | Piccadilly Gardens | Large Digital | West | 980,000 |
| JCD-MAN-002 | A56 Chester Road | 96-sheet Classic | North | 870,000 |
| JCD-MAN-003 | Deansgate | Digital 6-sheet x4 | Various | 640,000 |
| JCD-BHM-001 | Bull Ring (Selfridges) | Large Digital | East | 920,000 |
| JCD-BHM-002 | A38 Bristol Road | 96-sheet Classic | South | 750,000 |
| JCD-EDN-001 | Princes Street | Digital 6-sheet x6 | Various | 580,000 |
| JCD-EDN-002 | A8 Glasgow Road | 48-sheet Classic | West | 420,000 |
| JCD-GLA-001 | Buchanan Street | Digital 6-sheet x4 | Various | 510,000 |
| JCD-LDS-001 | A64 York Road | 96-sheet Classic | East | 680,000 |
| JCD-BRS-001 | Temple Meads Approach | 48-sheet Classic | North | 490,000 |
| JCD-LHR-001 | Heathrow T2 Arrivals | Digital Portrait | East | 1,100,000 |
| JCD-LHR-002 | Heathrow T5 Departures | Digital Landscape x3 | Various | 1,350,000 |
| JCD-WAT-001 | Waterloo SE Concourse | Rail Digital x8 | Various | 890,000 |
| JCD-KGX-001 | Kings Cross Western | Rail Digital x4 | South | 720,000 |
| JCD-EUS-001 | Euston Main Concourse | Rail Digital x6 | West | 810,000 |
| JCD-VIC-001 | Victoria Station | Rail Digital x4 | North | 760,000 |
| JCD-PAD-001 | Paddington Departures | Rail Digital x3 | East | 540,000 |
| JCD-LPL-001 | A580 East Lancs Road | 96-sheet Classic | West | 620,000 |
| JCD-NEW-001 | Grey Street, Newcastle | Digital 6-sheet x3 | Various | 380,000 |
| JCD-NOT-001 | A52 Derby Road | 48-sheet Classic | South | 450,000 |
| JCD-SHF-001 | A61 Penistone Road | 48-sheet Classic | North | 410,000 |
| JCD-CDF-001 | Queen Street Station | Digital 6-sheet x2 | Various | 290,000 |
| JCD-RDG-001 | A33 Relief Road | 48-sheet Classic | South | 520,000 |
| JCD-BRT-001 | Brighton Station | Digital 6-sheet x3 | Various | 340,000 |
| JCD-CAM-001 | A14 Milton Interchange | 48-sheet Classic | East | 480,000 |

## APPENDIX B: EXCLUDED COMPETITORS

Tesla Inc., BYD Auto Co., MG Motor UK Ltd, Polestar Automotive, NIO Inc., Xpeng Inc., Omoda Auto UK, VinFast, Zeekr.

---

**SIGNED** for and on behalf of **JCDecaux UK Ltd**:

Name: ________________________
Title: Commercial Director
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Marketing Director, UK & Europe
Date: ________________________
"""


def _clearchannel_dooh_agreement() -> str:
    return """# DIGITAL OUT-OF-HOME ADVERTISING AGREEMENT

**Between:**
Clear Channel UK Ltd ("the Media Owner")
33 Golden Square, London W1F 9JT
Company No. 03045498

**And:**
DEEPAL UK Ltd ("the Advertiser")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Contract Reference:** CC-DEEPAL-2025-DOOH-0723
**Effective Date:** 1 August 2025
**Expiry Date:** 31 December 2025

---

## 1. INTRODUCTION AND SCOPE

1.1 Clear Channel UK operates a national network of digital out-of-home (DOOH) screens, including the Adshel Live digital 6-sheet network, Storm large-format digital displays, and Malls Live digital screens in shopping centres.

1.2 This Agreement covers the provision of programmatic and directly booked DOOH advertising inventory to the Advertiser for the UK launch of the DEEPAL and AVATR electric vehicle brands.

## 2. CONTRACT VALUE

2.1 Total contract value: **£1,200,000** (One Million Two Hundred Thousand Pounds).

| Format | Inventory | Budget (GBP) |
|--------|-----------|-------------|
| Adshel Live (Digital 6-sheet) | 3,500+ screens nationally | £400,000 |
| Storm (Large Format Digital) | 30 premium locations | £300,000 |
| Malls Live (Shopping Centre) | 200+ screens | £200,000 |
| Programmatic DOOH (via LAAP) | Variable | £200,000 |
| Bespoke Activations | TBC | £100,000 |
| **Total** | | **£1,200,000** |

## 3. PROGRAMMATIC DOOH (LAAP PLATFORM)

3.1 The Advertiser may purchase a portion of DOOH inventory programmatically through Clear Channel's **LAAP** (Launch and Amplify Platform) or via third-party DSPs integrated with the Clear Channel SSP.

3.2 **Supported DSPs:** The Trade Desk, DV360, Xandr, Hivestack, Vistar Media.

3.3 **Programmatic Buying Models:**

| Model | Description | Min. Spend |
|-------|-------------|-----------|
| Guaranteed PMP | Private marketplace deal, reserved inventory | £25,000/flight |
| Preferred PMP | Priority access, not guaranteed | £10,000/flight |
| Open Exchange | Real-time bidding on available screens | £5,000/flight |

3.4 **Audience-Based Buying.** Clear Channel supports audience-based targeting using:
- (a) CACI Acorn consumer classifications;
- (b) Experian Mosaic segments;
- (c) Custom audiences derived from mobile location data (anonymised);
- (d) Proximity-based targeting (geo-fencing around competitor locations, charging stations, etc.).

3.5 **Trigger-Based Campaigns.** The Media Owner supports programmatic campaigns triggered by:
- Weather conditions (e.g., display "Range Anxiety?" creative when temperature drops below 5°C);
- Time of day (commuter vs. leisure messaging);
- Traffic flow data (congestion-triggered messaging);
- Sports results (e.g., post-F1 race creative rotation);
- Stock market / petrol price feeds.

## 4. DIRECTLY BOOKED CAMPAIGNS

4.1 Non-programmatic campaigns shall be booked via the Clear Channel sales team with a minimum **2 weeks'** lead time.

4.2 **Adshel Live Network Bookings:**
- National coverage: 3,500+ screens;
- Regional packages available (London, Midlands, North, Scotland);
- Posting periods: 1-week or 2-week cycles;
- Standard SOT: 1/6 (10-second slot in 60-second loop).

4.3 **Storm Bookings:**
- 30 premium large-format screens across UK cities;
- Full-motion video (15 seconds max);
- Domination packages available (100% SOT for limited periods);
- Minimum booking: 1 week.

4.4 **Malls Live:**
- 200+ screens in 40 shopping centres;
- Portrait format (1080 x 1920);
- Proximity to retail EV charging points where available;
- Ideal for consideration/conversion messaging.

## 5. PRICING

5.1 **Directly Booked Rates:**

| Format | Rate Basis | Rate (GBP) |
|--------|-----------|-----------|
| Adshel Live — National 2-week | Package | £45,000 |
| Adshel Live — London 2-week | Package | £18,000 |
| Adshel Live — Regional 2-week | Package | £12,000 |
| Storm — per screen per week | Unit | £4,000 |
| Storm — Domination (per screen/wk) | Unit | £12,000 |
| Malls Live — National 2-week | Package | £22,000 |
| Malls Live — per centre per week | Unit | £800 |

5.2 **Programmatic CPMs:**

| Targeting | CPM (GBP) |
|-----------|----------|
| Run of Network (RON) | £3.50 |
| Audience-targeted | £6.00 |
| Geo-fenced (500m radius) | £8.00 |
| Trigger-based | £10.00 |
| Domination (100% SOT) | £15.00 |

5.3 **Discount Structure:**

| Annual Commitment | Discount |
|------------------|---------|
| £250K – £500K | 5% |
| £500K – £1M | 10% |
| £1M+ | 15% |

5.4 The Advertiser qualifies for the **15% discount** tier based on total commitment of £1,200,000.

## 6. MEASUREMENT AND VERIFICATION

6.1 **Audience Measurement.** All audience data is based on the Route methodology, the UK OOH industry's audience measurement system.

6.2 **Digital Verification.** The Media Owner shall provide:
- Proof of play reports for all digital campaigns (100% census data from screen CMS);
- Independent verification via Hivestack verification tags where requested;
- SOT compliance monitoring with weekly reporting.

6.3 **Impression Delivery Guarantee.** The Media Owner guarantees delivery of **90%** of contracted impressions within the booked period. Shortfall shall be compensated via extended posting or credit at the contracted rate.

6.4 **Footfall Attribution.** For bespoke activations near dealer locations, the Media Owner shall provide footfall attribution studies using mobile location data (via partner: Locomizer), measuring:
- Exposed vs. control group visitation to dealer;
- Uplift in dealer footfall attributable to OOH exposure;
- Visit frequency and dwell time analysis.

## 7. CREATIVE SPECIFICATIONS

7.1 **Adshel Live / Malls Live:**
- Resolution: 1080 x 1920 (portrait);
- Format: JPEG or MP4;
- Duration: 10 seconds (static or motion);
- File size: max 50MB.

7.2 **Storm Large Format:**
- Resolution: 1920 x 1080 (landscape) or 1080 x 1920 (portrait);
- Format: MP4 (H.264);
- Duration: 15 seconds;
- File size: max 100MB.

7.3 All creative must comply with the Committee of Advertising Practice (CAP) Code and be approved by the Media Owner's compliance team within **2 working days** of submission.

## 8. BESPOKE ACTIVATIONS

8.1 The Advertiser has allocated £100,000 for bespoke DOOH activations. Proposed activations include:

8.1.1 **Interactive Touchscreen Experience** (2 locations — Westfield London, Trafford Centre):
- 65" touchscreen kiosk adjacent to charging stations;
- Interactive vehicle configurator;
- QR code for test drive booking;
- Budget: £40,000 (production + placement).

8.1.2 **Anamorphic 3D Creative** (1 location — Piccadilly Lights):
- 3D forced-perspective creative showing the DEEPAL S07 "driving out" of the screen;
- 2-week booking;
- Budget: £45,000 (inclusive of creative production).

8.1.3 **AR Bus Shelter** (5 locations — London):
- Augmented reality experience triggered via mobile device;
- Users can "see" the S07 parked next to the bus shelter;
- Budget: £15,000.

## 9. PAYMENT TERMS

9.1 Payment: **30 days** from invoice date.

9.2 Invoicing schedule:
- Direct bookings: invoiced on campaign start date;
- Programmatic: invoiced monthly in arrears based on verified delivery.

## 10. TERMINATION

10.1 Either party may terminate with **30 days'** written notice.

10.2 Non-refundable commitments:
- Production costs for bespoke activations already commissioned;
- Direct bookings within 2 weeks of posting date.

## 11. DATA PROTECTION

11.1 All mobile location data used for audience targeting and measurement is aggregated and anonymised in compliance with UK GDPR and ICO guidance.

11.2 No personally identifiable information (PII) is collected, stored, or processed as part of DOOH campaign delivery.

## 12. GOVERNING LAW

12.1 This Agreement is governed by the laws of England and Wales.

---

## APPENDIX: STORM SITE LIST

| Site ID | Location | Format | Facing | Weekly Impacts |
|---------|----------|--------|--------|---------------|
| CC-STM-001 | Piccadilly Circus | Piccadilly Lights | South | 4,200,000 |
| CC-STM-002 | Waterloo IMAX | Large Digital | North | 1,800,000 |
| CC-STM-003 | Shepherd's Bush | Storm Portrait | East | 920,000 |
| CC-STM-004 | Deansgate, Manchester | Storm Landscape | West | 680,000 |
| CC-STM-005 | New Street, Birmingham | Storm Portrait | South | 720,000 |
| CC-STM-006 | Buchanan Galleries, Glasgow | Storm Portrait | North | 480,000 |
| CC-STM-007 | The Headrow, Leeds | Storm Landscape | East | 540,000 |
| CC-STM-008 | Queen Street, Cardiff | Storm Portrait | West | 320,000 |
| CC-STM-009 | Churchill Way, Bristol | Storm Landscape | South | 460,000 |
| CC-STM-010 | Haymarket, Edinburgh | Storm Portrait | East | 390,000 |

---

**SIGNED** for and on behalf of **Clear Channel UK Ltd**:

Name: ________________________
Title: Director of Sales
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Marketing Director, UK & Europe
Date: ________________________
"""


def _channel4_media_partnership() -> str:
    return """# MEDIA PARTNERSHIP AGREEMENT

**Between:**
Channel Four Television Corporation ("the Broadcaster" / "Channel 4")
124 Horseferry Road, London, SW1P 2TX

**And:**
DEEPAL UK Ltd ("the Partner")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Agreement Reference:** C4-DEEPAL-2025-PART-0156
**Effective Date:** 1 August 2025
**Expiry Date:** 28 February 2026
**Total Value:** £1,000,000 (One Million Pounds)

---

## 1. PARTNERSHIP OVERVIEW

1.1 This Agreement establishes a media partnership between Channel 4 and DEEPAL UK Ltd for the launch and sustained promotion of the DEEPAL and AVATR electric vehicle brands in the United Kingdom.

1.2 The partnership combines traditional airtime buying with content integration, branded content production, and digital innovation, reflecting Channel 4's commitment to supporting new entrants in the UK automotive market.

1.3 **Partnership Objectives:**
- (a) Build brand awareness for DEEPAL/AVATR among Channel 4's core audience (16-34, progressive, urban);
- (b) Position DEEPAL as an innovative, accessible EV brand aligned with Channel 4's sustainability values;
- (c) Drive measurable outcomes: website visits, configurator starts, test drive bookings;
- (d) Create culturally relevant content that extends beyond traditional advertising.

## 2. FINANCIAL SUMMARY

| Component | Budget (GBP) | Share |
|-----------|-------------|-------|
| Linear Airtime (C4, E4, More4, Film4) | £500,000 | 50% |
| Channel 4 Streaming (Free) Airtime | £200,000 | 20% |
| Branded Content Production | £150,000 | 15% |
| Digital & Social Amplification | £100,000 | 10% |
| Research & Measurement | £50,000 | 5% |
| **Total** | **£1,000,000** | **100%** |

## 3. LINEAR AIRTIME

3.1 The Broadcaster shall provide linear advertising airtime across the Channel 4 portfolio with the following targets:

| Channel | Share of Budget | Target GRPs (A16-34) |
|---------|----------------|---------------------|
| Channel 4 | 60% | 400 |
| E4 | 20% | 200 |
| More4 | 10% | 80 |
| Film4 | 10% | 70 |

3.2 **Scheduling Requirements:**
- Launch week (1-7 Sep): roadblock across C4/E4 at 21:00;
- Gogglebox sponsorship bumpers (Sep-Dec) — see Clause 5;
- First-in-break positioning for minimum 40% of spots;
- 60-second hero creative permitted during first 4 weeks.

3.3 **CPT Rates (Post-Partnership Discount):**

| Daypart | CPT A16-34 | CPT All Adults |
|---------|-----------|---------------|
| Peak | £9.00 | £5.50 |
| Off-Peak | £4.50 | £2.80 |
| E4 All Day | £6.00 | £3.20 |

## 4. CHANNEL 4 STREAMING

4.1 Video advertising on the Channel 4 streaming platform (formerly All 4) shall be delivered across the following formats:

| Format | CPM (GBP) | Budget |
|--------|----------|--------|
| Pre-roll (15s/30s) | £20.00 | £100,000 |
| Mid-roll (30s) | £16.00 | £60,000 |
| Sponsor idents (5s) | £12.00 | £25,000 |
| Pause ads | £10.00 | £15,000 |

4.2 **Targeting Capabilities:**
- Age, gender, location (postcode sector);
- Genre targeting (auto, technology, entertainment);
- Custom audience segments via Channel 4 Brandwatch;
- Registered user targeting (Channel 4 has 28 million registered users with first-party data).

4.3 **Frequency Capping:** Maximum 6 exposures per user per week across all streaming formats.

## 5. PROGRAMME SPONSORSHIP — GOGGLEBOX

5.1 The Partner shall sponsor **Gogglebox** (Series 24, September-December 2025) across Channel 4 and Channel 4 Streaming.

5.2 **Sponsorship Elements:**
- Opening credit (5 seconds): "Gogglebox is brought to you in association with DEEPAL — Electric for Everyone";
- Closing credit (5 seconds): brand logo, URL, and tagline;
- Part bumpers (3 seconds × 2 per episode);
- Online player branding on episode pages;
- Social media co-branded posts (minimum 4 per month via @C4Gogglebox).

5.3 **Sponsorship Value:** £120,000 (included within the linear airtime budget).

5.4 **Audience Profile:** Gogglebox delivers an average audience of 4.2 million viewers (BARB), with a 16-34 index of 125. The programme is Channel 4's most-watched entertainment format.

5.5 **Exclusivity:** No other automotive brand shall sponsor Gogglebox during the contracted period.

## 6. BRANDED CONTENT

6.1 The Broadcaster's branded content division (4Studio) shall produce the following content:

### 6.1.1 Short-Form Series: "The Electric Switch" (6 × 5-minute episodes)

- **Concept:** Real people consider switching from petrol/diesel to EV, featuring the DEEPAL S07. Documentary-style, following participants through research, test drives, and decision-making.
- **Distribution:** Channel 4 Streaming, YouTube (4Studio channel), social media.
- **Budget:** £80,000 (inclusive of production, talent, and post-production).
- **Timeline:** Filming August 2025, air date September 2025.

### 6.1.2 Long-Form Documentary: "China to UK: The EV Revolution" (1 × 30 minutes)

- **Concept:** Documentary exploring the journey of Chinese EV brands entering the UK market, featuring DEEPAL/AVATR factory visit, engineering insights, and UK customer perspectives.
- **Distribution:** Channel 4 linear (late-night slot), Channel 4 Streaming.
- **Budget:** £70,000 (inclusive of international filming).
- **Timeline:** Filming Jul-Aug 2025, air date October 2025.
- **Editorial Independence:** Channel 4 retains full editorial control per Ofcom broadcasting code. The Partner shall have review rights for factual accuracy but not editorial direction.

## 7. DIGITAL AND SOCIAL AMPLIFICATION

7.1 The Broadcaster shall provide the following digital support:

| Activity | Budget | Deliverables |
|----------|--------|-------------|
| Channel 4 social posts | £30,000 | 24 posts across Instagram, TikTok, X |
| Influencer collaboration | £40,000 | 3 influencers, 2 posts each |
| Paid social promotion | £20,000 | Boosting branded content |
| Email marketing | £10,000 | 2 dedicated sends to EV-interested users |

7.2 **Influencer Selection.** Influencers shall be jointly approved by both parties, with a focus on:
- Tech/automotive reviewers with 100K+ followers;
- Sustainability/lifestyle creators aligned with DEEPAL brand values;
- Diversity of voices reflecting Channel 4's commitment to underrepresented communities.

7.3 **Social Media Guidelines.** All social content shall comply with ASA guidelines on influencer advertising (clearly labelled as #ad or #sponsored).

## 8. RESEARCH AND MEASUREMENT

8.1 The Broadcaster shall commission and fund the following research:

| Study | Methodology | Timing | Budget |
|-------|-------------|--------|--------|
| Brand uplift study | Online survey (pre/post) | Sep + Dec | £20,000 |
| Content effectiveness | Channel 4 Streaming analytics | Monthly | £10,000 |
| Cross-platform reach | CFlight + Channel 4 data | Post-campaign | £10,000 |
| Audience sentiment | Social listening (Brandwatch) | Ongoing | £10,000 |

8.2 **Key Performance Indicators:**

| KPI | Target |
|-----|--------|
| Spontaneous brand awareness (16-34) | +5pp vs. baseline |
| Prompted brand awareness (16-34) | +15pp vs. baseline |
| Consideration (16-34) | +8pp vs. baseline |
| Branded content views (total) | 2,000,000 |
| Social engagement rate | >3% |
| Website referrals from C4 properties | 50,000 |

## 9. INTELLECTUAL PROPERTY

9.1 All branded content produced under Clause 6 shall be jointly owned by the Broadcaster and the Partner.

9.2 The Partner is granted a perpetual, worldwide licence to use the branded content for:
- Own-channel distribution (social media, website, YouTube);
- Dealer showroom playback;
- Internal presentations and awards submissions.

9.3 The Partner may not license the content to third parties without the Broadcaster's written consent.

9.4 The Broadcaster retains the right to include the content in its public-service archive and on-demand catalogue indefinitely.

## 10. REGULATORY AND COMPLIANCE

10.1 All advertising content shall comply with the BCAP Code and be Clearcast-approved prior to transmission.

10.2 All branded content shall comply with Ofcom Rules on product placement and sponsorship (Section Nine of the Ofcom Broadcasting Code).

10.3 The Broadcaster confirms that all branded content under Clause 6 shall be produced by the 4Studio team, editorially independent from the Channel 4 sales team, in accordance with the Broadcaster's obligations as a public-service broadcaster.

## 11. PAYMENT

11.1 Payment schedule:
- 25% on execution (£250,000);
- 25% on 1 September 2025 (£250,000);
- 25% on 1 November 2025 (£250,000);
- 25% on completion/reconciliation (£250,000).

11.2 Payment terms: **30 days** from invoice date.

## 12. TERM AND TERMINATION

12.1 This Agreement runs from 1 August 2025 to 28 February 2026 (to allow for post-campaign reporting and content distribution).

12.2 Either party may terminate with **60 days'** notice, subject to commitment on production costs already incurred for branded content.

12.3 The Broadcaster may terminate immediately if the Partner engages in conduct that materially damages the Broadcaster's public-service reputation.

## 13. GOVERNING LAW

13.1 This Agreement is governed by the laws of England and Wales.

---

**SIGNED** for and on behalf of **Channel Four Television Corporation**:

Name: ________________________
Title: Director of Digital & Client Revenue
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Marketing Director, UK & Europe
Date: ________________________
"""


def _media_agency_tob() -> str:
    return """# TERMS OF BUSINESS
## MEDIA PLANNING AND BUYING AGENCY AGREEMENT

**Between:**
Zenith Media UK Ltd ("the Agency")
Chancery House, 53-64 Chancery Lane, London WC2A 1QS
Company No. 02456178
Part of Publicis Groupe

**And:**
DEEPAL UK Ltd ("the Client")
Great West House, Great West Road, Brentford, TW8 9DF
Company No. 15234567

**Effective Date:** 1 January 2025
**Initial Term:** 12 months (1 January 2025 – 31 December 2025)
**Agreement Reference:** ZEN-DEEPAL-2025-TOB-001

---

## 1. APPOINTMENT AND SCOPE

1.1 The Client appoints the Agency as its media planning and buying agency for the United Kingdom and European markets (initially UK, Germany, France), on a non-exclusive basis for the Initial Term.

1.2 **Scope of Services:**

| Service Area | Description |
|-------------|-------------|
| Media Strategy | Annual media strategy development, channel planning, budget allocation |
| Media Planning | Campaign planning across all channels (digital, TV, OOH, print, radio) |
| Media Buying | Negotiation, booking, and stewardship of all media |
| Digital Activation | Programmatic buying, search, social, content distribution |
| Performance Reporting | Weekly/monthly reporting, dashboards, post-campaign analysis |
| Ad Tech Management | DSP management, pixel implementation, data integration |
| Competitive Intelligence | Quarterly competitive spend analysis and SOV reporting |
| Vendor Management | Liaison with media owners, contract negotiation, SLA monitoring |
| Compliance | Clearcast submissions, ASA pre-clearance, BCAP compliance |

1.3 **Excluded Services:** Creative production, brand strategy, PR, events management (unless specifically commissioned as a project).

## 2. FEES AND REMUNERATION

### 2.1 Commission Structure

2.1.1 The Agency shall be remunerated on a **commission basis** applied to net media spend:

| Media Type | Commission Rate |
|-----------|----------------|
| TV (linear + BVOD) | 3.0% |
| OOH (classic + DOOH) | 3.0% |
| Print | 3.0% |
| Radio | 3.0% |
| Digital (programmatic, social, search) | 3.0% |
| Events media | 2.0% |

2.1.2 Commission is calculated on **net media spend** (gross spend less all discounts, rebates, and credits).

2.1.3 For avoidance of doubt, the commission rate of **3%** applies uniformly across all media types except events media (2%).

### 2.2 Performance Bonus

2.2.1 A performance bonus of up to **15% of total commission** shall be payable, subject to the Agency meeting agreed KPIs:

| KPI | Weight | Threshold | Target | Stretch |
|-----|--------|-----------|--------|---------|
| Media efficiency (CPT vs. benchmark) | 25% | -5% | -10% | -15% |
| Campaign delivery (GRP/impression delivery %) | 25% | 90% | 95% | 98% |
| Reporting timeliness | 15% | 5 days | 3 days | 2 days |
| Cost savings (negotiated discounts) | 20% | £200K | £350K | £500K |
| Innovation (new formats/approaches) | 15% | 1 initiative | 2 initiatives | 3 initiatives |

2.2.2 Performance shall be assessed quarterly, with the annual bonus calculated as a weighted average of quarterly scores.

2.2.3 Bonus payment: within 45 days of annual performance review (target: February 2026 for 2025 performance).

### 2.3 Project Fees

2.3.1 Work outside the standard scope of services (Clause 1.2) may be commissioned as projects, subject to written agreement on scope and fees.

2.3.2 Standard day rates for project work:

| Role | Day Rate (GBP) |
|------|---------------|
| Strategy Director | £1,500 |
| Planning Director | £1,200 |
| Planning Manager | £800 |
| Digital Specialist | £900 |
| Data Analyst | £700 |
| Junior Planner/Buyer | £500 |

## 3. MEDIA BUYING OBLIGATIONS

### 3.1 Buying Standards

3.1.1 The Agency shall conduct all media buying in accordance with:
- (a) ISBA/IPA Framework for Media Agency Trading;
- (b) ISBA Media Services Contract principles;
- (c) The IPA Media Futures Group guidelines;
- (d) Applicable law and regulation.

3.1.2 The Agency warrants that it shall:
- Negotiate the best available rates on behalf of the Client;
- Disclose all material commercial arrangements with media owners;
- Not accept undisclosed rebates, incentives, or benefits from media owners;
- Pass through all volume discounts and credits to the Client.

### 3.2 Transparency

3.2.1 The Agency shall provide full transparency on:
- (a) All media owner rates (gross and net);
- (b) All discounts, rebates, and incentives received or receivable;
- (c) All programmatic fees including DSP technology fees, data costs, and ad serving fees;
- (d) Any inventory arbitrage arrangements (which are prohibited without Client consent);
- (e) All third-party costs passed through to the Client.

3.2.2 The Client shall have the right to conduct an **annual media audit** (at the Client's cost) to verify:
- Rate compliance against agreed terms;
- Rebate pass-through;
- Programmatic transparency;
- Competitive benchmarking of rates achieved.

3.2.3 The Agency shall co-operate fully with any audit and provide all requested documentation within **15 working days** of request.

### 3.3 Programmatic Trading Principles

3.3.1 All programmatic media shall be bought in the Client's own DSP seat (or a clearly ring-fenced Agency seat).

3.3.2 The Agency shall not engage in:
- (a) Inventory arbitrage (buying and reselling at a markup);
- (b) Undisclosed principal trading;
- (c) Barter arrangements without Client consent;
- (d) Use of Agency Trading Desks with non-transparent margin structures.

3.3.3 Programmatic supply chain fees shall be disclosed:

| Fee Component | Typical Range | Disclosure |
|--------------|--------------|-----------|
| DSP technology fee | 10-15% | Monthly |
| Data/audience costs | 5-10% | Monthly |
| Verification (IAS/DV) | 2-3% | Monthly |
| Ad serving | 1-2% | Monthly |
| Agency tech fee | 0% (included in commission) | N/A |

## 4. TEAM STRUCTURE AND SERVICE LEVELS

### 4.1 Dedicated Team

4.1.1 The Agency shall provide the following dedicated team:

| Role | Name | Allocation |
|------|------|-----------|
| Account Director | TBC | 60% |
| Senior Planner | TBC | 80% |
| Digital Planner/Buyer | TBC | 100% |
| Programmatic Manager | TBC | 50% |
| AV Buyer (TV/VOD) | TBC | 40% |
| OOH Specialist | TBC | 30% |
| Data Analyst | TBC | 40% |

4.1.2 Named individuals shall be confirmed within **2 weeks** of contract execution.

4.1.3 The Agency shall not reassign any team member at Director level or above without the Client's prior written consent and a minimum **30-day** transition period.

### 4.2 Service Level Agreements

| Service | SLA | Measurement |
|---------|-----|-------------|
| Response to briefs | 5 working days | Timestamp |
| Campaign launch (from approved plan) | 10 working days | Timestamp |
| Weekly report delivery | By 12:00 Tuesday | Email timestamp |
| Monthly report delivery | Within 3 working days of month-end | Email timestamp |
| Issue escalation (P1) | 2-hour response | Email/call log |
| Issue escalation (P2) | 8-hour response | Email/call log |
| Billing queries | 5 working days to resolve | Ticket system |

### 4.3 Reporting

4.3.1 **Weekly Flash Report:** Delivered by Tuesday 12:00, covering:
- Spend pacing vs. plan (by channel);
- Key campaign metrics (impressions, clicks, CPT, CPV);
- Highlights and lowlights;
- Recommended optimisations.

4.3.2 **Monthly Performance Report:** Delivered within 3 working days of month-end:
- Full channel-by-channel performance;
- Budget reconciliation;
- Audience delivery vs. target;
- Competitive SOV analysis;
- Recommendations for next month.

4.3.3 **Quarterly Business Review:** Face-to-face presentation covering:
- Strategic performance review;
- Market trends and insights;
- Budget reallocation recommendations;
- Innovation pipeline;
- Performance bonus progress.

## 5. DATA AND TECHNOLOGY

5.1 **Data Ownership.** All campaign data generated during the term of this Agreement is the property of the Client, including but not limited to:
- Audience data and segments;
- Conversion data and attribution models;
- Creative performance data;
- Site lists and rate card information negotiated on behalf of the Client.

5.2 **Data Portability.** Upon termination or expiry, the Agency shall provide all Client data in machine-readable format within **30 working days**, including:
- All DSP campaign data (log-level data where available);
- All analytics and attribution data;
- All media plans and rate cards;
- All audience segments and targeting configurations.

5.3 **Technology Stack.** The Agency shall utilise the following technology stack (subject to Client approval for changes):

| Function | Platform |
|----------|----------|
| DSP (Display/Video) | DV360 |
| DSP (OOH) | Hivestack / VIOOH |
| Search | Google Ads / Microsoft Ads |
| Social | Meta Business Suite, TikTok Ads, LinkedIn Campaign Manager |
| Measurement | Google Analytics 4, Campaign Manager 360 |
| Attribution | Google Attribution / Custom MMM |
| Brand Safety | IAS (Integral Ad Science) |
| Viewability | MOAT |
| Competitive | Nielsen Ad Intel / Pathmatics |
| Reporting | Looker Studio / Tableau |

## 6. CONFIDENTIALITY

6.1 Both parties acknowledge that in the course of this engagement, they may have access to Confidential Information including but not limited to:
- Media rates and trading terms;
- Marketing strategies and plans;
- Sales data and commercial targets;
- Product launch timelines;
- Customer data and research.

6.2 Neither party shall disclose Confidential Information without prior written consent, except:
- To employees and subcontractors on a need-to-know basis under equivalent confidentiality obligations;
- As required by law, regulation, or court order;
- To professional advisers under a duty of confidentiality.

6.3 Confidentiality obligations survive termination for a period of **3 years**.

## 7. INTELLECTUAL PROPERTY

7.1 Media plans, strategies, and analyses produced by the Agency specifically for the Client are the Client's intellectual property upon payment.

7.2 The Agency retains ownership of its proprietary tools, methodologies, and pre-existing IP.

## 8. TERMINATION

8.1 Either party may terminate this Agreement by giving **90 days'** written notice.

8.2 The Client may terminate immediately upon:
- (a) Material breach not remedied within 30 days of written notice;
- (b) Breach of transparency obligations (Clause 3.2);
- (c) Undisclosed conflicts of interest;
- (d) Insolvency of the Agency.

8.3 **Transition Obligations.** Upon termination, the Agency shall:
- Provide a full handover to the incoming agency or Client within 60 days;
- Transfer all campaign data per Clause 5.2;
- Fulfil all outstanding media commitments already booked;
- Provide a final billing reconciliation within 45 days.

## 9. LIABILITY AND INSURANCE

9.1 The Agency's total liability under this Agreement shall not exceed the greater of:
- (a) Total fees paid in the preceding 12 months; or
- (b) £500,000.

9.2 The Agency shall maintain:
- Professional indemnity insurance: £5,000,000;
- Public liability insurance: £2,000,000;
- Employers' liability insurance: as required by law.

9.3 The Agency shall provide evidence of insurance cover upon request.

## 10. CONFLICTS OF INTEREST

10.1 The Agency confirms that as of the Effective Date, it does not represent any direct competitor of the Client in the UK EV market.

10.2 Should the Agency be approached by a competing brand, it shall:
- (a) Notify the Client within 5 working days;
- (b) Propose appropriate conflict management measures (e.g., separate teams, Chinese walls);
- (c) Obtain the Client's written consent before accepting the competing account.

10.3 Direct competitors are defined as: Tesla, BYD, MG Motor, Polestar, NIO, Xpeng, Omoda, VinFast, Zeekr, and any other brand primarily selling battery electric vehicles in the UK market.

## 11. GOVERNING LAW

11.1 This Agreement is governed by the laws of England and Wales.

11.2 Disputes shall first be referred to senior management for resolution. If unresolved within 30 days, disputes shall be referred to arbitration under LCIA rules.

---

## APPENDIX A: ANNUAL MEDIA BUDGET ALLOCATION

| Channel | Annual Budget (GBP) | Agency Commission (3%) |
|---------|--------------------|-----------------------|
| TV (Linear) | £6,000,000 | £180,000 |
| BVOD | £1,600,000 | £48,000 |
| YouTube | £2,400,000 | £72,000 |
| Meta | £2,000,000 | £60,000 |
| Google (Search + Display) | £1,600,000 | £48,000 |
| DV360 (Programmatic) | £1,400,000 | £42,000 |
| TikTok | £1,000,000 | £30,000 |
| LinkedIn | £400,000 | £12,000 |
| OOH | £3,000,000 | £90,000 |
| Print | £600,000 | £18,000 |
| Radio | £400,000 | £12,000 |
| Events | £600,000 | £12,000 (2%) |
| **Total** | **£20,000,000** | **£624,000** |

## APPENDIX B: PERFORMANCE SCORECARD TEMPLATE

| Quarter | KPI 1: Efficiency | KPI 2: Delivery | KPI 3: Reporting | KPI 4: Savings | KPI 5: Innovation | Score |
|---------|------------------|-----------------|------------------|----------------|-------------------|-------|
| Q1 | | | | | | /100 |
| Q2 | | | | | | /100 |
| Q3 | | | | | | /100 |
| Q4 | | | | | | /100 |
| **Annual** | | | | | | **/100** |

Bonus payable: Score ≥ 60 = 50% bonus; Score ≥ 80 = 100% bonus; Score ≥ 90 = 115% bonus (stretch).

---

**SIGNED** for and on behalf of **Zenith Media UK Ltd**:

Name: ________________________
Title: Managing Director
Date: ________________________

**SIGNED** for and on behalf of **DEEPAL UK Ltd**:

Name: ________________________
Title: Chief Marketing Officer, Europe
Date: ________________________

**WITNESSED** by:

Name: ________________________
Title: ________________________
Date: ________________________
"""


# ============================================================================
# Public API
# ============================================================================

_CONTRACTS = [
    ("ITV_Airtime_Agreement.md", _itv_airtime_agreement),
    ("Sky_Airtime_Agreement.md", _sky_airtime_agreement),
    ("Sky_BVOD_Addendum.md", _sky_bvod_addendum),
    ("JCDecaux_OOH_Contract.md", _jcdecaux_ooh_contract),
    ("ClearChannel_DOOH_Agreement.md", _clearchannel_dooh_agreement),
    ("Channel4_Media_Partnership.md", _channel4_media_partnership),
    ("MediaAgency_Terms_of_Business.md", _media_agency_tob),
]


def generate() -> dict:
    """
    Generate all vendor contract markdown files.

    Returns:
        dict mapping filename to (content_str, output_path) tuples.
    """
    results = {}

    for filename, content_fn in _CONTRACTS:
        content = content_fn().strip() + "\n"
        path = os.path.join(CONTRACTS_DIR, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        word_count = len(content.split())
        page_equiv = round(word_count / 350, 1)  # ~350 words per page
        results[filename] = (content, path)
        print(f"  [contracts] {filename}: ~{word_count} words (~{page_equiv} pages) -> {path}")

    return results


if __name__ == "__main__":
    print("Generating vendor contract documents...")
    results = generate()
    print(f"\nDone. Generated {len(results)} contracts.")
    total_words = sum(len(c.split()) for c, _ in results.values())
    print(f"Total: ~{total_words} words (~{round(total_words / 350, 1)} pages)")
