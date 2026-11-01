# Syncranicity Automation — Implementation Matrix

| Layer | Production implementation | Current status | Evidence boundary / next escalation |
|---|---|---|---|
| Vercel EIA gateway | Secret-backed EIA API routes, pagination, health, orchestration, no secret output | LIVE | Generator data never equals available load capacity |
| Hourly scheduling | External AppDeploy cron at minute 17 each hour | LIVE | Avoids Vercel Hobby hourly-cron restriction |
| Daily verification | External worker daily verification + Vercel daily EIA refresh | LIVE | Monthly EIA data is checked frequently but changes only when source changes |
| Persistent public-source state | Database worker state, fingerprint, last check/change, bounded node snapshot, change archive | LIVE | Confidential deal data excluded |
| National node scout | All-state EIA generator signals, map, promotion to research | LIVE | NODE_LEAD_ONLY; no parcel/capacity claim |
| Transmission/substations | Free published ArcGIS queries around coordinates | LIVE SCREEN | Proximity/voltage only; no MVA/MW headroom |
| Utility territory | Free point-in-polygon candidate territories | LIVE SCREEN | Overlaps are not an exact service determination |
| Geography/jurisdiction | Census coordinate geography | LIVE SCREEN | Not zoning or title |
| Public/special land | BLM surface-management screen | LIVE SCREEN | Absence is not private title |
| Flood | FEMA NFHL point screen | LIVE SCREEN | Does not resolve unmapped drainage or survey elevation |
| Elevation/topography | USGS elevation point query | LIVE SCREEN | Not grading or survey work |
| Soils | USDA SSURGO point/component query | LIVE SCREEN | Not geotechnical/foundation proof |
| Hydrography | USGS NHD flowline/waterbody screen | LIVE SCREEN | Not water rights, supply, quality, fire flow, or discharge |
| Wetlands | USFWS National Wetlands Inventory | LIVE SCREEN | Not jurisdictional delineation |
| Critical habitat | Official-USFWS service discovery and point screen | LIVE/FAIL-VISIBLE | Formal IPaC, survey, consultation, and legal review remain later |
| Environmental facilities | EPA FRS proximity screen | LIVE SCREEN | Not Phase I/II or contamination extent |
| Broadband | FCC BDC area proxy | LIVE SCREEN | Not carrier fiber, routes, diversity, latency, or quote |
| Roads | Census TIGERweb road screen | LIVE SCREEN | Not legal access, bridge, turn, or heavy-haul proof |
| Rail | Census TIGERweb rail screen | LIVE SCREEN | Not service, ownership, siding rights, or capacity |
| Parcel-source discovery | ArcGIS catalog search by state/county | LIVE ASSISTED | Every candidate source must be verified as official/current |
| Other local GIS discovery | Zoning, water, DOT, aviation, fiber, and environment catalog search | LIVE ASSISTED | Catalog hits are not authoritative conclusions |
| Exact APN geometry | Polygon/MultiPolygon GeoJSON intake, source/date/authority fields, area QA | LIVE FOUNDER INPUT | County adapter/manual record gathering needed where no free feed exists |
| QGIS pipeline | Download all exact parcels as WGS84 GeoJSON | LIVE | Advanced spatial work is performed in QGIS |
| Full gate framework | 11 gates, approximately 100 weighted requirements, hard/soft/monitor classes | LIVE | Founder/professional evidence required to pass gates |
| Fatal-flaw engine | Hard kill, soft kill, weight-9/10 HOLD, evidence coverage | LIVE | Human confirmation for consequential kills |
| Buyer intelligence | Revealed-preference dossier + SEC submissions evidence | LIVE ASSISTED | Non-SEC deals/permits/utility records enter through daily research and founder review |
| Direct-buyer boundary | Research/anonymous/control/direct-ready states | LIVE | Generic buyer-discovery calls are not the default |
| Seller motivation | Separate willingness/timing/carry/structure/cooperation/authority scores | LIVE | Sensitive traits prohibited; authority can override score |
| Alternate-use floor | CAUNV, AUCR, LAF, category and downside labels | LIVE | Not an appraisal; closed comps and professional review later |
| Control-instrument optimizer | WCC, clock adequacy, mandatory rights, eligibility, Decision Preservation Score | LIVE | Counsel must approve state-specific instrument |
| Evidence ledger | Claim IDs, source, date, APN, scope, grade, expiry, contradiction, rights | LIVE | Reliance/assignment rights must come from issuer/counsel |
| Stage 2 Model A | Eight full call packets, call records, outcomes, written follow-ups, call debt | LIVE | Founder calls; professionals own conclusions |
| Source monitoring registry | URL, category, geography, cadence, importance, grade, last check/change, fallback | LIVE LOCAL | Automated non-EIA web research also runs through ChatGPT condition watches |
| State legal adapter | All 50 states; DATA_ONLY/AMBER/RED/CONDITIONAL/CLEARED lanes | LIVE | No state becomes CLEARED from generic internet research alone |
| Deal state machine | WATCHLIST through MONETIZED plus HOLD/KILLED | LIVE | One paid position rule remains founder-enforced |
| Capital ledger | Spent, committed, strike price, $5k learning and $10k control caps | LIVE | Actual bookkeeping remains in LLC bank/accounting system |
| Progress/anti-theater | Funnel, truth events, call debt, exposure, 90-day milestones | LIVE | Metrics depend on truthful recordkeeping |
| Confidential persistence | Browser-local vault with JSON export/import | LIVE | Not cross-device cloud sync; encrypted company backup required |
| Public map privacy | Public-source nodes are public; exact parcels/deal records exist only in local browser | LIVE BOUNDARY | App-level authentication can be added before multi-user use |
| Listings | Local watch records and daily external research | PARTIAL | No lawful free nationwide real-time listing feed exists |
| Nationwide owner/title | County-by-county official records and title escalation | ASSISTED/HUMAN | No free uniform authoritative national title/owner source |
| Available MW | Explicitly prohibited from inference | HUMAN/UTILITY | Exact-parcel, exact-load utility evidence required |
| Zoning/use determination | Local GIS discovery, full gate, planning call packet | ASSISTED/HUMAN | Written local determination/counsel later |
| Physical water | Hydrography, source discovery, full gate, water call packet | ASSISTED/HUMAN | Provider/right/hydrology evidence required |
| Fiber diversity | FCC proxy, local-source discovery, fiber call packet | ASSISTED/HUMAN | Route-level carrier engineering and quote required |
| Political ground truth | Public monitoring, watch registry, planning call packet | ASSISTED/HUMAN | Private sentiment and future votes cannot be automated reliably |
| Professional reports | Scope, evidence, rights, expiry and task tracking | ORCHESTRATED | Engineer/title/survey/environmental/water/appraisal/legal issuer required |
