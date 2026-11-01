# Syncranicity Daily Electric-Land Scan — September 7, 2026

## Portfolio decision

- **Primary:** Benson/Fenner, Cochise County, Arizona — **PRIORITY / GIS_BLOCKED / HOLD before payment**
- **Unpaid backup #1:** Union Center Business Park, Evanston, Wyoming — **PRIORITY / GIS_IN_PROGRESS**
- **Unpaid backup #2:** San Juan legacy-energy corridor, New Mexico — **WATCH / DEVELOP**

No new parcel qualifies for paid control. Capital deployed remains **$0**; paid-control exposure remains **$0**.

## Material changes

1. **The live node-scout endpoint is healthy after an initial timeout.** At 2026-09-07T15:53:45Z it reported a complete June 2026 EIA operable-generator pull: 28,237 source rows, 3,975 `NODE_LEAD_ONLY` records, and 250 records returned. Every returned `available_mw` remains null. Generation capacity is not load-serving capacity. [Node scout](https://syncranicity.vercel.app/api/node-scout?limit=250)

2. **Oklahoma now has a specific ≥75 MW large-load process.** The Data Center Customer Ratepayer Protection Act applies to new data-center, AI-computing and crypto facilities contracting for at least 75 MW after July 1, 2026. It also requires post-purchase notice when qualifying land is bought outside a municipality or industrial development park. MidAmerica Industrial Park therefore has a cleaner process signal than raw rural land, but the statute does not prove service availability or exempt a project from other filings. [Oklahoma Corporation Commission, updated July 29, 2026](https://oklahoma.gov/occ/divisions/public-utility/energy/electric-utility/data-center-customer-ratepayer-protection-act.html)

3. **MidAmerica Industrial Park is a strong political-first discovery area, but not yet a parcel.** The public-trust park advertises 1,500 acres that can be parceled, three onsite transmission substations, five distribution stations, GRDA service, park water, rail and highway access. Exact offered tract, APN, price, control form and exact-load utility evidence are absent. [MidAmerica competitive advantages](https://maip.com/site-selection/competitive-advantages/)

4. **Iowa produced a supported rejection and a seller-data discrepancy.** Maquoketa and its consultant ended preliminary data-center discussions August 18 after a heavily contested public process. Separately, active listing ID 12585916 at 0 200th Avenue says $250,000 and 10 acres in structured fields, while its remarks say 44.5 acres at $25,000 per acre. The state certified-site page says 61.44 acres remain available. This is not a defined data-center opportunity. [City-discussion update](https://www.kwqc.com/2026/08/19/maquoketa-halts-early-discussions-potential-data-center-development/), [listing](https://www.ruhlcommercial.com/property-search/property/?id=12585916), [state site record](https://opportunityiowa.gov/business/buildings-sites/highway-61-industrial-park)

5. **Salix remains a buyer-intelligence case, not a Syncranicity lead.** MidAmerican Energy's affiliate obtained options on roughly 900 acres and identified Google as a prospective customer. A September 2 report says residents filed formal resistance to Salix's motion to dismiss the annexation challenge. Woodbury County's moratorium applies to unincorporated land; the disputed annexation determines which body controls land use. No court outcome, zoning approval, water plan or utility commitment was found. [September 2 litigation update](https://www.ktiv.com/2026/09/03/new-legal-move-made-stop-data-centers-google-sets-up-data-center-website/), [MidAmerican/Google disclosure](https://www.ktiv.com/2026/08/03/google-considering-data-center-salix-iowa-according-midamerican-energy/)

## Ranked Priority candidates and county-GIS status

### 1. Benson/Fenner — infrastructure-first

**Why it remains Priority:** traceable active offering, resolved Cochise County jurisdiction, rural/open-land profile, plausible control economics, and attributable SSVEC/AEPCO process signal.

**Buyer stage:** deeper diligence, not initial marketing. A regional colocation, powered-industrial or developer-led first phase is only a hypothesis; no AWS-specific fit or MW claim is supported.

**Strongest objection:** the approximately 90-acre offered portion is not yet reconciled to parent APN 120-02-003A, the reported road/50-foot easement and rail/I-10 constraints have not been translated into a usable layout, and parcel-specific utility deliverability is unknown.

**Cheapest next proof:** seller/broker-provided current survey and division map, then SSVEC's response to an exact-parcel, phased-load inquiry authorized by the owner. Spend no option money first.

**GIS status:** `GIS_BLOCKED / HUMAN_VERIFICATION_NEEDED`. Existing official-map findings are retained; no favorable clearance is inferred from missing title, easement or utility evidence.

### 2. Union Center, PIN 15201840400301 — infrastructure-first

**Why it remains Priority:** active public listing, city seller, sale/lease path, industrial zoning, exact official parcel located, I-80/rail/fiber/municipal utility signals, and a strong conventional-industrial downside floor.

**September 7 GIS readback:** the official parcel service again returned one full polygon for PIN 15201840400301, City of Evanston ownership, Union Center Third Addition Lot 3 Block 1, and 21.44837 acres. Query used the exact PIN and returned EPSG:4326 geometry. This still conflicts with the 18.26-acre offering and 29 contiguous acres. [Official parcel layer](https://services7.arcgis.com/TsVLs9I3Mz0rNgK9/arcgis/rest/services/March_26_Parcel_Map/FeatureServer/0), [property record](https://properties.zoomprospector.com/statewy/property/1700-Union-Road-Evanston-Wyoming/E54ECF68-ADCB-458C-B9E1-BF3F1A3119C7)

**GIS status:** `GIS_IN_PROGRESS / HUMAN_VERIFICATION_NEEDED`. Prior whole-polygon city zoning result remains LI-D. FEMA's official flood-hazard service returned query errors for both full-polygon and bounding-envelope requests, so flood is `BLOCKED`, not cleared. Easements, title, legal access, fiber diversity and exact offered geometry remain `NOT_PUBLISHED / NOT_REVIEWED`.

**Buyer stage:** initial interest only for a smaller modular/edge or powered-industrial use. Available MW is **UNKNOWN**.

**Cheapest next proof:** city confirmation of the 18.26-acre boundary, the adjoining acreage/PINs behind the 29-acre claim, and the permitted control process; then Rocky Mountain Power's exact-parcel service process.

**No third Priority candidate.** San Juan remains an unpaid research backup until an exact privately controllable parcel is identified.

## NODE_LEAD_ONLY

No new generator-derived node was promoted to a parcel category.

- **Walter Scott Jr Energy Center, Pottawattamie County, Iowa:** endpoint units show 805.8 MW and 705.9 MW of generation. Existing Council Bluffs data-center activity makes the corridor worth watching, but no open-land parcel or service artifact was paired with it.
- **Traverse Wind Project, Custer County, Oklahoma:** endpoint signal is 999 MW of generation. Wind generation, rural acreage and transmission proximity do not establish retail delivery, firmness or capacity.
- **Louisa Generating Station, Louisa County, Iowa:** endpoint signal is 745.6 MW of generation. Cheapest falsification is service-territory and parcel screening around existing industrial land; no seller search should start from generation alone.

## Buyer intelligence and four-decision review

**MidAmerican Energy / Google — revealed behavior.** The Salix sequence shows a utility affiliate taking options on a large multi-owner assembly and planning to transfer the position to an eventual electric customer. The live defects—annexation litigation, rezoning, public opposition and absent published water/power figures—also show why options are not equivalent to a construction-ready site.

**Buyer process update.** Public AWS role descriptions confirm that acquisition recommendations are based on multidisciplinary technical studies, preliminary design, cost/schedule effects, market and financial analysis, and cross-functional approval across energy, fiber, design, construction, legal and tax. They do not disclose current acquisition mandates or universal parcel cutoffs. [AWS site-risk role](https://www.amazon.jobs/en/jobs/10469434/site-risk-due-diligence-manager-risk-and-resiliency), [AWS supply-solutions role](https://www.amazon.jobs/en-gb/jobs/10522639/colocation-business-development-manager-data-center-supply-solutions)

**Four decisions:**

- **Benson:** initial-interest case is plausible; kill/hold decision remains **HOLD**; deeper diligence is justified only through free survey/division/access and utility-process evidence; build/investment is **NOT READY**. A buyer can presently source alternatives without paying Syncranicity because no transferable utility or entitlement artifact exists.
- **Union Center:** initial-interest case is plausible for a smaller modular buyer; kill/hold is **HOLD** on geometry and utility evidence; deeper diligence is worth one free city clarification; build/investment is **NOT READY**. Main substitutes are serviced municipal industrial parks, including MidAmerica, with larger expansion land.
- **MidAmerica:** strong market/administrative signal, but Stage A remains **UNRESOLVED** because there is no exact tract, price or control instrument. It is a substitute that weakens the buyer case for paying a premium for a less-defined parcel elsewhere.

## Political-first additions — neutral evidence record

Numerical W/F/C political scores and rankings are not assigned here; the underlying dated evidence is preserved instead.

- **MidAmerica/Pryor:** current DC-specific government/park support and a 15-year operating comparable are documented. Contradictions are material: a July 28 community meeting reported concerns about infrastructure, resources and project secrecy, and February reporting documented Google's 1.1-billion-gallon annual water use for July 2024–June 2025. Independent positive community evidence strong enough for the addendum's strict new-sourcing gate was not found. Result: no new political-first parcel sourcing. [Community meeting](https://ktul.com/news/local/residents-gather-in-mayes-county-to-discuss-proposed-data-centers-07-28-2026), [water reporting](https://www.readfrontier.org/stories/as-data-centers-boom-in-oklahoma-so-does-water-demand/)
- **Maquoketa:** a recent comparable project discussion ended after public opposition; the city is reviewing heavy-industrial rules. Result: `REJECTED / LEARNING` for the current data-center strategy, with reopening only after adopted DC-specific rules and a new public proposal establish a materially different process.
- **Salix:** utility options and a named prospective buyer are outweighed for Syncranicity sourcing by unresolved annexation authority, litigation, rezoning, organized opposition and the county moratorium. Result: `HARD HOLD` for political-first sourcing until a court/annexation resolution and a defined local approval path.

## Seller motivation and downside

- **Benson:** motivation remains medium-high based on long exposure, price history and the 90/103/115-acre discrepancies, but distress is not proven. The same discrepancies prevent payment.
- **Union Center:** the city refreshed the listing September 1 and offers negotiable sale/lease terms. This supports transaction intent, not distress. At $1 million, only low-cost exclusivity/option/lease control could fit the capital doctrine after geometry and utility clarification.
- **Maquoketa, listing 12585916:** inconsistent acreage and pricing may create negotiation leverage, but current DC political/process risk overwhelms it. Alternate-use floor is comparatively strong: I-3 heavy-industrial use, highway access, municipal utilities and fiber support manufacturing, distribution or conventional industrial resale. Save only for a non-DC buyer or a documented policy/process reset.

## Two-state deep dive conclusions

**Oklahoma:** prioritize established industrial parks over raw county land. MidAmerica has the strongest official infrastructure/process package reviewed today, but no exact tract and no exact-load utility artifact. The ≥75 MW statute adds notice and documentation obligations; GRDA's status and the Act's application to a specific project need counsel/utility interpretation before control. No Oklahoma parcel enters Priority.

**Iowa:** buyer demand is real, but jurisdictional process is the dominant risk. Maquoketa withdrew; Salix is litigating annexation; Woodbury County has a one-year moratorium for unincorporated land; Linn County adopted DC-specific rules in February. Exact authority, annexation status and current local code must precede parcel sourcing. No Iowa parcel enters Priority.

## Killed, held and catalyst queue

- **REJECTED / LEARNING:** Maquoketa's 2026 data-center concept—discussions ceased after opposition. Reopen only on a documented new sponsor plus adopted DC-specific rules and community process.
- **HARD HOLD:** Salix 900-acre assembly—already optioned by a utility affiliate; annexation litigation and authority remain unresolved.
- **WATCH / DEVELOP:** MidAmerica's 1,500-acre availability—real park-level offering, but no exact tract/APN/price/control instrument.
- **HOLD:** Benson—survey/division, easement/layout and SSVEC path unresolved.
- **HOLD:** Union Center—offered geometry, flood service, easements/title, fiber diversity and power path unresolved.
- **SAVE FOR CATALYST:** SunZia local-load thesis and generic Palo Verde-adjacent land; generation/export infrastructure is not local load capacity.

## Exact founder actions

1. **Spend $0 and authorize no outreach today.**
2. **Approve or defer one Tuesday Benson evidence request** limited to the current survey/division map, exact offered legal description/APN(s), recorded 50-foot road/access instrument, rail/I-10 boundary constraints and well documentation. This unlocks whether a utility inquiry is worth making.
3. **Only after Benson's tract is defined, approve or defer the exact-parcel SSVEC service-process inquiry.** Do not state or request speculative 50/100/500 MW; use phased-load scenarios clearly labeled as hypotheses.
4. **Do not contact MidAmerica, Maquoketa or Salix.** None has a decision-sized founder gap today.

## Source, coverage and delivery failures

- FEMA NFHL layer 28 returned HTTP/query errors for Union Center full-polygon and envelope intersection attempts; flood remains `BLOCKED`.
- The accessible Large-Load Buyer Watch task/dossiers were not available in this run; buyer evidence was refreshed independently. No cross-chat sync is claimed.
- The exact prior AWS report remained unavailable; public job descriptions were used only as process evidence.
- The live system status reports `persistent_store_configured: false`; no authenticated research-ingestion route was exposed. [System status](https://syncranicity.vercel.app/api/system-status)
- Coverage completed: EIA/node inventory, Oklahoma utility/regulatory/industrial-park signals, Iowa planning/annexation/moratorium/community evidence, water, fiber/logistics, active parcel listings, buyer options and public buyer-process evidence. Detailed county GIS was limited to the existing Priority queue; the remaining national queue is unprocessed, not completed.

**Delivery: UNSYNCED / MANUAL_INGESTION_REQUIRED**

- Producer/task ID: `national-electric-land-deep-scan`
- Run ID: `national-electric-land-deep-scan/2026-09-07`
- Produced: `2026-09-07T15:58:00Z`
- Changed records: `OK-MAYES-MAIP-UNRESOLVED`, `IA-JACKSON-MAQUOKETA-HWY61-12585916`, `IA-WOODBURY-SALIX-900AC`, `WY-UINTA-UNION-CENTER-15201840400301`
- Category changes: Maquoketa concept `WATCH -> REJECTED/LEARNING`; MidAmerica `DISCOVERY -> WATCH/DEVELOP`; Salix `DISCOVERY -> HARD HOLD`; Union Center remains `PRIORITY/GIS_IN_PROGRESS`
- Capital deployed: `$0`; paid-control exposure: `$0`
