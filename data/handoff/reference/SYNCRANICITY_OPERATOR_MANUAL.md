# Syncranicity Electric Land OS — Operator Manual

**Version:** 1.0  
**Company:** Syncranicity LLC  
**Operating doctrine:** nationwide, rural/open-land prior; aggressive collection; conservative killing; $5,000 learning cap; $10,000 cumulative soft-control exposure on the one live paid parcel; one primary position and two unpaid backups; advanced diligence buyer/sponsor funded.

## 1. Live architecture

### Canonical entry point

`https://syncranicity.vercel.app`

The Vercel homepage routes to the full control plane. Vercel retains the EIA secret and exposes only sanitized public-source endpoints. The secret value is never returned.

### Persistent hourly worker and full interface

`https://syncranicity-monitor-worker-kpdxfa.v2.appdeploy.ai/`

The external worker solves the Vercel Hobby hourly-cron limitation. It runs a public-source snapshot job each hour and a daily verification job. It stores only bounded public-source state and change history.

### Confidential operating data

Deals, exact parcel polygons, buyer dossiers, seller records, evidence claims, call records, source watches, state-law notes, control scenarios, and founder tasks stay in the browser's local vault. They are not written to the public worker database. Use **Export vault** after every material work session and preserve the JSON in encrypted company storage.

## 2. Non-negotiable rules

1. A generator, transmission line, substation, or utility-territory polygon is a **node signal**, not a parcel.
2. `available MW` remains null or unknown until an exact-parcel, exact-load utility artifact supports it.
3. A coordinate is not an APN.
4. An assessor owner field is not title or signing authority.
5. Broadband availability is not a diverse carrier-fiber route.
6. No paid control without exact parcel, authority path, access path, serving-utility process, use path, water path, environmental screen, lawful state lane, buyer-class fit, and capital path.
7. Weight-9 and weight-10 unknowns hold money.
8. AI may retrieve, extract, compare, rank, draft, and monitor. The founder approves every call, disclosure, spend, contract, promotion, extension, and kill. Qualified professionals own legal, title, survey, engineering, environmental, water, appraisal, tax, and reliance conclusions.

## 3. Daily workflow

### Step 1 — Command

Open **Command** and inspect:

- EIA period and node count.
- Hourly worker status and last check.
- Capacity guardrail.
- Current source failures.
- Two-state daily deep-dive rotation.

Select **Verify now** only when an immediate refresh is justified. Manual requests are throttled to prevent duplicate upstream calls.

### Step 2 — Node scout

Use **Node scout** to filter EIA-backed infrastructure signals. Generation MW is the generating unit's reported capacity, not available load capacity.

Promote a signal only when there is a reason to investigate its surrounding land. Promotion creates a local `WATCHLIST` deal. It does not recommend acquisition.

### Step 3 — Coordinate screen

Use **Coordinate screen** before manually gathering county records. The free screen currently orchestrates:

- Census geography.
- Published substations.
- Published transmission lines.
- Candidate retail utility territories.
- BLM/public surface-management signals.
- FEMA flood hazard.
- USGS elevation.
- USDA SSURGO soils.
- EPA Facility Registry proximity.
- National Wetlands Inventory.
- USFWS critical-habitat screening.
- USGS hydrography.
- FCC broadband proxy.
- Census TIGERweb roads.
- Census TIGERweb rail.
- Candidate parcel-service discovery.
- Candidate zoning, water, transportation, aviation, fiber, and environmental GIS-source discovery.

Every adapter returns `SUCCESS` or `FAILED`, an evidence grade, a summary, structured data, and a proof limitation. Failures remain visible. The aggregate result is a conservative **HOLD** pending exact parcel and human verification.

### Step 4 — Exact parcels

After locating the official county/state parcel service:

1. Select the linked deal.
2. Enter exact APN, jurisdiction, source name, source URL, source effective date, and owner-of-record field.
3. Paste or upload WGS84 Polygon/MultiPolygon GeoJSON.
4. Confirm official publisher only after verification.
5. Validate and add the parcel.

The app computes an approximate area as a geometry QA check and flags a material difference from stated acreage. This is not a survey. Use **Export for QGIS** to download all mapped parcels as GeoJSON.

### Step 5 — Deals and gates

In **Deals + gates**, assess every requirement across the eleven gates:

0. Buyer/project definition.
1. Demand and geography.
2. Exact parcel, ownership, access, and control.
3. Utility and power path.
4. Land use, entitlement, and politics.
5. Water, cooling, fire, and discharge.
6. Civil, environmental, and hazards.
7. Fiber, transportation, and labor.
8. Economics and buyer takeout.
9. Transferable evidence.
10. Execution and closing.

For each requirement record:

- Status: unknown, pass, soft fail, hard fail, or not applicable.
- Evidence grade: V0–V4.
- Exact note, contradiction, or cheapest next test.

Fatal hard failures override scores. Soft failures require a bounded cure/test. Weight-9/10 unknowns produce HOLD.

### Step 6 — Buyer intelligence

Use **Buyer intelligence** to reconstruct revealed preferences from actual deals. Record geography, first-phase and ultimate MW, service window, acreage, cooling/water, fiber, power architecture, transaction forms, evidence threshold, recent deals, failure signals, and source links.

For public companies, enter the SEC CIK and a valid SEC request contact email. The system retrieves current filings through the SEC submissions API. Filings prove disclosed historical behavior, not a confidential current mandate.

Keep contact readiness at `RESEARCH_ONLY` until a controlled or seller-authorized opportunity fits the buyer's documented pattern.

### Step 7 — Seller motivation

Use **Seller motivation** only after cheap site screens. Score willingness, timing, carrying pressure, structural flexibility, cooperation, and authority separately. Grade the evidence.

Authority can override motivation. Public statements and posts are leads to verify, not proof. Do not infer or record sensitive personal traits.

### Step 8 — Alternate-use downside

Use **Alternate use** to build a separate downside case for agriculture, rural residential/recreation, ordinary industrial, logistics, energy, telecom, resources, conservation, subdivision/land banking, or continuation of existing use.

The engine calculates:

- Conservative Alternate-Use Net Value (CAUNV).
- Alternate-Use Coverage Ratio (AUCR).
- Liquidity-Adjusted Floor (LAF).
- Downside label.

Use P25 closed-sale value where possible. Listings are asking prices, not value. Do not count another speculative electric use as independent downside.

### Step 9 — Control optimizer

Use **Control optimizer** before paying for any instrument. Enter nonrefundable consideration, legal/title/escrow, travel/admin, extensions, access/restoration, other at-risk amounts, contract days, and P90 decision time.

The engine calculates:

- Worst-Case Controllable Cost (WCC).
- Clock adequacy: contract days / (1.25 × P90 days to next decision).
- Mandatory rights missing.
- Eligibility against the $10,000 cap.
- Decision Preservation Score.

The recommended instrument is the cheapest eligible scenario, not automatically an option.

### Step 10 — Evidence ledger

Use **Evidence ledger** to convert narratives into exact claims. Record source, publisher, dates, exact APN, scope/exclusions, grade, expiration, contradiction status, confidentiality, reliance/assignment rights, and next verification.

Every buyer-facing sentence must trace to a claim ID. Remove or label unsupported sentences.

### Step 11 — Stage 2 calls

Use **Stage 2 calls** for Model A founder-led verification. The app contains full packets for:

1. Assessor/GIS/planning.
2. Utility large-load intake.
3. Utility planning/engineering.
4. Water/wastewater/fire/discharge.
5. Fiber.
6. Title/escrow/counsel.
7. Seller.
8. Buyer site-specific fit.

Each packet includes opening language, priority questions, required written output, stop signals, and follow-up email. Create a call record, verify the contact on the day of the call, schedule it, record facts/refusals/unknowns, attach document references, and assign the next action.

The **call debt** metric treats overdue founder-dependent calls as blocked work. Preparing indefinitely does not count as progress.

### Step 12 — Monitoring

Use **Monitoring** to record mutable utility, PUC, local-government, listing, buyer, seller, water, environmental, fiber/logistics, and legal sources. Each watch needs geography/company, URL, cadence, importance, evidence grade, last check, last material change, and manual fallback.

The automated cadence is:

- Hourly public-source snapshot/change detection.
- Daily verification and two-state rotation.
- Event-driven ChatGPT condition watch for material developments.
- Day-of-decision rechecks for every mutable source that drives money or an external claim.

### Step 13 — State law

Use **State law** as a transaction kill switch. Research may run in all 50 states. Seller solicitation, public marketing, negotiation, assignment compensation, and binding control remain disabled until the operating lane is cleared for that state.

`DATA_ONLY` is not approval. `CLEARED` should be used only after a current state-specific legal conclusion identifies the permissible role, broker involvement, disclosures, foreign qualification, recording, escrow, tax, and closing mechanics.

### Step 14 — Progress

Use **Progress** to prevent research theater. The dashboard tracks:

- Truth events.
- Activity-to-truth index.
- Founder call debt.
- Recorded capital exposure.
- Funnel from node signals to monetization.
- Resolved gates, calls, evidence claims, and kills.
- 7-, 14-, 28-, 45-, 60-, 75-, and 90-day milestones.

A cheap, documented kill is progress. A large report that does not change the decision state is not.

## 4. Evidence grades

- **V0:** unknown or conflicting.
- **V1:** proxy, inference, listing, seller statement, or unverified catalog result.
- **V2:** reliable secondary source, public screening layer, or dated founder note.
- **V3:** current official public record tied to the relevant geography/use.
- **V4:** executed, parcel-specific official/professional evidence with appropriate scope and rights.

Buyer dossier evidence uses B0–B4 on the same escalating logic.

## 5. Backups and disaster recovery

1. Select **Export vault** after every material session.
2. Save the JSON in encrypted company storage using a dated filename.
3. Preserve the last seven daily exports and one monthly archive.
4. Test **Import vault** monthly in a separate browser profile.
5. Never place the EIA key, personal owner data, signed contracts, or confidential buyer material into source code, public map tiles, public repositories, or unrestricted links.

## 6. What remains inherently human or professional

No free or paid automation can conclusively supply every transaction fact. Human/professional escalation remains required for:

- Counties with no usable parcel API or stale geometry.
- Marketable title and signing authority.
- Legal and physical access.
- Available MW, service timing, upgrade scope, tariff/credit, and utility commitments.
- Unpublished seller conditions and owner truthfulness.
- Informal political sentiment and emerging opposition not yet public.
- Water rights, physical yield, quality, fire flow, and discharge.
- Carrier route diversity and construction quotation.
- Survey, geotechnical, wetlands, species, cultural, contamination, air, civil, and drainage conclusions.
- Appraisal, tax, brokerage, licensing, securities, entity, option, assignment, recording, and closing advice.

The system's job at those boundaries is to produce a precise HOLD, call packet, scope, maximum spend, deadline, and stop condition—not a fabricated answer.
