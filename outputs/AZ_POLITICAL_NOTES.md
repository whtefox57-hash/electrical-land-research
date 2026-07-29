# STEP 7 — ARIZONA POLITICAL RISK NOTES

**All sources checked 2026-07-29.** Jurisdiction-level research completed ahead
of the GIS work, since it needs no spatial data. Once candidates exist, each one
inherits its county and municipal row from here.

Every status below is READ from a cited source. Where status is unknown it says
UNKNOWN — those are the phone calls, not searches.

---

## The single most important structural fact

**In Arizona, a city rejection does not necessarily kill a project on
unincorporated county land.**

Project Blue is the proof. Tucson City Council voted **unanimously to reject** it
in **August 2025** — refusing annexation and city water. The project was built
anyway, because **Pima County had already approved the rezoning and sold the
developer the land**, and the site sits in unincorporated county. The developer
switched from water-cooled to **air-cooled** and proceeded. Construction began
**April 2026**.

For your strategy this cuts both ways, and you should hold both:

- **Opportunity.** County zoning authority over unincorporated land is the real
  gate. A parcel in unincorporated Pinal or Pima can be developable even where
  the nearest city is hostile.
- **Risk.** Proceeding over a city's objection buys litigation, referendum
  attempts, protest and sustained press. Project Blue has drawn an open-meeting-
  law lawsuit, an Attorney General suit against the ACC, an AG appeal, and
  ongoing demonstrations. A buyer will price that in.

Sources:
- https://azluminaria.org/2025/08/06/tucson-city-council-rejects-project-blue-amid-intense-community-pressure/
- https://azluminaria.org/2026/04/24/we-said-no-dozens-protest-as-construction-of-project-blue-data-center-begins/
- https://www.pima.gov/3552/Project-Blue-FAQ

---

## State level

| Item | Status | Date | Source |
|---|---|---|---|
| **CDC tax exemption** | **PAUSED — ACA barred from accepting applications 1 Jul 2026 – 30 Jun 2029, renewals included** | signed 13 Jun 2026, effective 1 Jul 2026 | [AZ Capitol Times](https://azcapitoltimes.com/news/2026/07/09/data-centers-dominated-2026-session-lawmakers-answered-with-3-year-tax-incentive-pause/) |
| Statewide construction moratorium | **NONE** — the pause is fiscal only; building continues | Jul 2026 | [AZFamily](https://www.azfamily.com/2026/06/10/arizona-budget-deal-includes-3-year-pause-data-center-tax-exemptions/) |
| Governor's posture | Hobbs sought **full elimination** of the exemption in her executive budget; settled for the 3-year pause | 2026 session | [Deseret](https://www.deseret.com/politics/2026/01/22/tuscon-fights-back-against-data-center-proposal-after-chandler-rejected-another-proposal-last-year/) |
| ACC posture | Large-load workshop published 20 Apr 2026; consistent direction — large loads pay their own way, explicit cost-shift protection for other ratepayers | Apr 2026 | [ACC](https://www.azcc.gov/news/home/2026/04/20/acc-large-load-data-center-workshop-highlights) |
| Attorney General | **Actively litigating** against the ACC over the TEP–Project Blue special contract; appeal filed | Feb 2026 onward | [Tucson Sentinel](https://www.tucsonsentinel.com/local/report/021926_mayes_tep_rate/ag-mayes-sues-corp-comm-over-tep-project-blue-electric-deal) |

**Read on the state climate:** data centers "dominated the 2026 session". The
political trend line is clearly restrictive, but the restriction landed on
**subsidy**, not on **permission**. Nobody at state level has moved to stop
construction. That distinction is the most useful thing on this page.

---

## Pima County

| Field | Value |
|---|---|
| `moratorium_status` | **none** |
| `dc_ordinance_status` | UNKNOWN — no county-level DC-specific ordinance found |
| `county_zoning_authority` | **Yes, and exercised** — approved Project Blue rezoning and sold the land |
| `recent_dc_activity` | **Project Blue APPROVED** and under construction since Apr 2026 |
| `organized_opposition` | **Yes, intense** — No Desert Data Center Coalition originated here |
| Litigation | Open-meeting-law suit filed Jan 2026, first hearing 6 Feb 2026; separate suit over the approval process |

**How a conversation would go:** the county has already demonstrated it will
approve and sell, and has absorbed a year of sustained public anger for doing it.
Staff will engage on a technically sound proposal, but every step will be public,
litigated and slow, and the Board knows precisely what it costs them politically.

Sources: [Project Blue FAQ](https://www.pima.gov/3552/Project-Blue-FAQ) ·
[KOLD lawsuit](https://www.kold.com/2026/01/16/new-lawsuit-threatens-project-blue-pima-county/) ·
[Tucson.com](https://tucson.com/news/local/government-politics/article_4401b26e-8205-43f5-83cf-47997013be25.html)

## City of Tucson

| Field | Value |
|---|---|
| `moratorium_status` | **none** — considered and **explicitly rejected** on legal advice |
| `dc_ordinance_status` | **DRAFTED, advancing** — UDC amendment for Large-Scale Data Centers, at Mayor and Council |
| Key requirements if adopted | PAD or PCD zoning mandatory (forces Council review of every project); public documentation of adequate **water and power** |
| `recent_dc_activity` | **REJECTED Project Blue** unanimously, Aug 2025 — refused annexation and water |
| Water posture | Told Project Blue to **stop using Tucson Water even for construction**, May 2026 |
| `organized_opposition` | **Yes, the strongest in the state** |

**How a conversation would go:** unproductive for a data center inside city
limits, and I would not spend your time there. Tucson has refused annexation,
refused water, refused construction water, and is building a code specifically to
require Council sign-off on each project. Its value to you is as a **signal about
the surrounding county**, not as a venue.

Sources: [City of Tucson UDC amendment](https://www.tucsonaz.gov/Departments/Planning-Development-Services/Planning-Initiatives/Data-Centers-Unified-Development-Code-Amendment) ·
[KJZZ](https://www.kjzz.org/fronteras-desk/2026-04-06/tucson-leaders-will-discuss-a-proposal-on-data-center-restrictions-this-week) ·
[Tucson Sentinel — construction water](https://www.tucsonsentinel.com/local/report/050526_project_blue_water/)

## Town of Marana

| Field | Value |
|---|---|
| `moratorium_status` | **none** |
| `dc_ordinance_status` | UNKNOWN |
| `recent_dc_activity` | **APPROVED** — Council voted **unanimously** to rezone ~600 acres of farmland for Beal Infrastructure data centers |
| Referendum challenge | **FAILED** — 2,800 signatures submitted Feb 2026; town declined to continue verification; papers did not meet statutory requirements and the 30-day window had passed. **No public vote will occur.** |
| Political aftermath | **Three residents launched Council campaigns** in response |
| `organized_opposition` | Yes — No Desert Data Center Coalition active here |

**How a conversation would go:** currently the most receptive jurisdiction in
southern Arizona at staff and Council level — a unanimous approval that survived
a referendum attempt. But the backlash is converting into electoral challenges,
so **that receptiveness has a shelf life tied to the next Council election.**
Timing matters more here than anywhere else on this list.

Sources: [Tucson Sentinel — referendum fails](https://www.tucsonsentinel.com/local/report/021826_data_referendum_fails/marana-rejects-referendums-against-project-blue-data-center-rezoning) ·
[AZPM — council runs](https://news.azpm.org/s/102502-marana-data-center-vote-sparks-backlash-three-residents-launch-council-runs/) ·
[Axios](https://www.axios.com/local/phoenix/2026/02/10/data-center-opponents-marana-citizen-referendum-ballot)

## City of Phoenix

| Field | Value |
|---|---|
| `moratorium_status` | **none** |
| `dc_ordinance_status` | **ADOPTED 2 Jul 2025** (Z-TA-2-25-Y) |
| Requirements | Special Permit required in C-2, C-3, CP/GCP, A-1, A-2; half-mile spacing from high-capacity transit; noise study and mitigation within 300 ft of residential; **utility will-serve letter** |
| `recent_dc_activity` | Menlo Equities Ahwatukee campus — 5 buildings, ~1M sq ft, ~40.6 acres, **construction underway**; rezoning dates from **1997**, predating the guardrails |
| Council behaviour 2026 | Approved easement abandonments for the Ahwatukee project **8–1** on 1 Jul 2026 over resident objection; separately **delayed** another DC rezone vote |
| Legal exposure | **Facing legal pressure over the new rules**, Mar 2026 |
| `organized_opposition` | Yes, neighbourhood-level (Ahwatukee) — noise, heat, air quality |

**How a conversation would go:** procedural rather than hostile. Phoenix has
written rules and will apply them; a project that satisfies the Special Permit
standards and arrives with a will-serve letter gets a fair hearing. The
Ahwatukee fight is about a **1997 entitlement the current code cannot reach**,
which is a useful precedent — legacy zoning is durable.

Sources: [City of Phoenix](https://www.phoenix.gov/newsroom/pdd-news/city-of-phoenix-updates-zoning-to-safeguard-health-and-safety-as.html) ·
[Staff report Z-TA-2-25-Y](https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/staffreports/z-ta-2-25-y-data-center.pdf) ·
[Ahwatukee.com](https://www.ahwatukee.com/news/data-center-request-sparks-council-hand-wringing/article_fe96541b-6e93-4727-ae0d-727984a244bb.html) ·
[AZFamily — legal pressure](https://www.azfamily.com/2026/03/26/phoenix-faces-growing-legal-pressure-over-new-data-center-rules/)

## City of Buckeye

| Field | Value |
|---|---|
| `moratorium_status` | **none** |
| `dc_ordinance_status` | No general ordinance found; control exercised **per-project via development agreement** |
| `recent_dc_activity` | **APPROVED with conditions** — Tract Buckeye Technology Park, 2,069 acres, up to 40 data centers, **1.8 GW at build-out**, ~$20bn |
| Water condition | **2,000 acre-feet/year cap written into the development agreement** |
| Water source | Developer intends to **self-supply via on-site groundwater wells**, later transferring the system to the city |

**How a conversation would go:** the most transactional in the state. Buckeye
approves at very large scale and negotiates the constraint into the agreement
rather than legislating it. Expect to be asked for a hard number on annual water
use early, and expect it to end up contractually binding.

Sources: [City of Buckeye](https://www.buckeyeaz.gov/business-development/economic-development/data-centers-fact-vs-fiction) ·
[Grist](https://grist.org/technology/arizona-water-data-centers-semiconducters/)

## Pinal County

| Field | Value |
|---|---|
| `moratorium_status` | UNKNOWN — none found |
| `dc_ordinance_status` | UNKNOWN |
| `recent_dc_activity` | **La Osa (Vermaland), near Eloy — scaled back ~80% after opposition.** As proposed: 3,300 acres, 59 data centers, two on-site gas plants, utility-scale BESS. Would have been the largest in Arizona. |
| `organized_opposition` | **Yes** — resident opposition sufficient to force an 80% reduction |

**How a conversation would go:** the county has not said no, but residents have
demonstrated they can shrink a project dramatically. A right-sized proposal is
viable; a 3,000-acre one is not. **On-site gas generation appears to have been a
significant part of what drew opposition** — worth separating from the data
center itself in any pitch.

Source: [KJZZ](https://www.kjzz.org/fronteras-desk/2026-05-28/largest-proposed-data-center-in-arizona-to-be-scaled-back-80-after-opposition)

## Cochise County

| Field | Value |
|---|---|
| `moratorium_status` | **PROPOSED / under discussion** — Board Chair Antenori issued a public statement on the status of a data center moratorium discussion |
| `dc_ordinance_status` | UNKNOWN |

I could not establish whether this progressed to adoption, expiry or abandonment.
**This is a phone call.**

Source: [Cochise County](https://www.cochise.az.gov/CivicAlerts.aspx?AID=415)

## City of Chandler

| Field | Value |
|---|---|
| `moratorium_status` | UNKNOWN |
| `dc_ordinance_status` | UNKNOWN |
| `recent_dc_activity` | **REJECTED a data center proposal in 2025** |

Confirmed rejection, but I could not establish whether any standing rule
followed. **Phone call.**

Source: [Deseret](https://www.deseret.com/politics/2026/01/22/tuscon-fights-back-against-data-center-proposal-after-chandler-rejected-another-proposal-last-year/)

---

## Organised opposition — statewide

**No Desert Data Center Coalition** — https://nodesertdatacenter.com/ — slogan
"NOT. ONE. DROP."

- Formed summer 2025 to oppose Project Blue phase 1
- Based in southern Arizona; explicitly states its fight "knows no borders"
- Has **travelled nationally to share its organising playbook** — treat its
  tactics as portable to any Arizona jurisdiction, not as a Tucson-only risk
- Tactics used to date: mass turnout at hearings, **open-meeting-law litigation**
  (filed Jan 2026, first hearing 6 Feb 2026), **citizen referendum** (Marana,
  2,800 signatures), protest at construction sites, teach-ins
- Named organiser in coverage: Vivek Bharathan

**Scoring implication:** for any candidate in Pima, Pinal or Santa Cruz County,
`organized_opposition` should be **yes** by default — losing the 3 points in the
political rubric — unless you have specific evidence otherwise. Elsewhere in the
state, absence of a chapter is not evidence of safety; it is evidence that
nothing has been proposed there yet.

Sources: [nodesertdatacenter.com](https://nodesertdatacenter.com/) ·
[Nonprofit Quarterly](https://nonprofitquarterly.org/not-one-drop-how-an-arizona-community-came-together-to-fight-a-data-center/) ·
[calonews](https://www.calonews.com/arizona/amid-proposals-and-deals-a-grassroots-movement-to-stop-data-centers-intensifies-in-arizona/article_c89b16b4-1b48-450b-936f-4704f32ce8e9.html)

---

## Provisional political risk scores

Applying your 0–25 rubric. These are **jurisdiction-level priors** to be adjusted
per candidate once `dist_to_residential_km` and `prior_industrial_use` are known
from the GIS work. Both of those are set to the neutral value here and flagged.

| Jurisdiction | Morat. (8) | No restrictive ord. (5) | Prior industrial (5) | Dist. resid. (4) | No opposition (3) | **Total** |
|---|---|---|---|---|---|---|
| Buckeye | 8 | 5 | TBD | TBD | 3 | **16 + TBD** |
| Marana | 8 | 5 | TBD | TBD | 0 | **13 + TBD** |
| Pinal County (uninc.) | 8 | 5 | TBD | TBD | 0 | **13 + TBD** |
| Phoenix | 8 | 0 | TBD | TBD | 3 | **11 + TBD** |
| Pima County (uninc.) | 8 | 5 | TBD | TBD | 0 | **13 + TBD** |
| Cochise County | 2 | 5 | TBD | TBD | 3 | **10 + TBD** |
| City of Tucson | 8 | 0 | TBD | TBD | 0 | **8 + TBD** |
| Chandler | UNKNOWN | UNKNOWN | TBD | TBD | 3 | **UNKNOWN** |

Two notes on reading this table. **Tucson scores 8 on "no moratorium" despite
being the most hostile jurisdiction in the state** — because the rubric measures
moratorium status, and Tucson deliberately chose not to enact one. That is a
genuine limitation of the rubric, not a data error, and I would not let the
number override the narrative. Second, **Pima County unincorporated scores the
same as Marana** despite a far uglier public fight, because the rubric has no
term for litigation exposure. Consider adding one.

---

## Jurisdictions requiring a phone call, not a search

Per your instruction, the explicit list:

1. **Cochise County** — moratorium discussion status and outcome
2. **Chandler** — whether any ordinance followed the 2025 rejection
3. **Mesa** — ordinance status
4. **Tempe** — ordinance status
5. **Goodyear** — ordinance status
6. **Casa Grande** — ordinance status
7. **Marana** — whether an ordinance is being drafted post-referendum
8. **Pinal County** — county-level ordinance status, and what specifically drove
   the La Osa reduction
9. **Pima County** — whether any county DC ordinance is in drafting
10. **All remaining rural counties** — Yuma, Mohave, Coconino, Navajo, Apache,
    Gila, Graham, Greenlee, La Paz, Santa Cruz, Yavapai. Nothing found for any
    of them, which most likely means nothing has been proposed there yet rather
    than that they are permissive.

---

## APPENDED 2026-07-29 — the two TBD components, now computed

**Do not edit above this line.** The provisional scores table left
`prior_industrial_use` (5 pts) and `dist_to_residential_km` (4 pts) as TBD for
the GIS work. Both are now computed. Method and results:

**`prior_industrial_use` (0–5) — DERIVED**
- 5/5 where the candidate is a retired generating station. A retired power
  plant is unambiguous prior industrial use.
- ≤3/5 where the candidate is a substation, scored on density of electrical
  infrastructure within 5 km as an industrial-corridor proxy (3 if ≥3
  substations within 5 km, 2 if 1–2, else 1). Capped at 3 because a substation
  parcel is not evidence that the surrounding land is industrial.

**`dist_to_residential_km` (0–4) — DERIVED**
- Distance to the nearest census block group with population density
  ≥200 persons/km², computed in EPSG:26912 from FCC BDC Dec-2024 `TotalPop`
  over equal-area block group area.
- Banding: ≥5 km → 4; 2–5 km → 3; 1–2 km → 2; 0.3–1 km → 1; <0.3 km → 0. The
  0.3 km break is set at Phoenix's 300-foot noise-study trigger.
- This is a density proxy, not a parcel-level land use survey.

### A finding that materially affects how the table above should be read

**All 25 of the top-scoring private candidates fall in jurisdictions this
document did not research.** None is in Pima, Tucson, Marana, Phoenix, Buckeye,
Pinal, Cochise or Chandler. They are in unincorporated Navajo, Apache, Mohave,
Yuma, Coconino, Greenlee, Yavapai and Maricopa county, plus Kingman, Tempe,
Mesa, Gilbert and Gila Bend.

Every one of them therefore receives the default 8/8 on moratorium status and
5/5 on "no restrictive ordinance" **solely because nothing was found** — the
condition this document already warned about in its closing section
("Absence of evidence, not evidence of absence").

The rubric cannot distinguish a jurisdiction verified permissive from one
nobody has studied. Those candidates carry
`political_prior_basis = "INFERRED — jurisdiction not researched..."` in the
output CSVs, and this is recorded in AZ_METHOD.md as the single most likely way
the screen is wrong.

The observation in the original table — that Tucson scores 8/8 on moratorium
despite being the most hostile jurisdiction in the state — is the same
weakness seen from the other side. The suggestion to add a litigation-exposure
term is endorsed; it is not implemented here because doing so would change a
rubric supplied as an input.
