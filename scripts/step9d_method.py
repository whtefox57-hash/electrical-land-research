"""STEP 9d — AZ_METHOD.md, AZ_FINDINGS_SUMMARY.md, AZ_COUNTIES_TO_CALL.md."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, OUTPUTS, STATUS_LOG

GPKG = os.path.join(OUTPUTS, "az_candidates.gpkg")
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    priv = gpd.read_file(GPKG, layer="candidates_private_ranked")
    excl = gpd.read_file(GPKG, layer="candidates_excluded_ranked")
    allc = gpd.read_file(GPKG, layer="candidates_all_scored")
    top = priv.head(25)
    recs = [json.loads(l) for l in open(STATUS_LOG) if l.strip()]
    latest = {}
    for r in recs:
        latest[r.get("key") or r["dataset"]] = r
    ok = sorted([r for r in latest.values() if r["status"] == "SUCCESS"],
                key=lambda x: x["dataset"])
    bad = [r for r in latest.values() if r["status"] != "SUCCESS"]

    # =================================================================
    # AZ_METHOD.md
    # =================================================================
    m = [f"# AZ METHOD\n\nGenerated {STAMP}. Everything this screen rests on, "
         "what was derived versus read, and an explicit list of what would "
         "make it wrong.\n"]

    m.append("\n## Projections\n\n")
    m.append("| purpose | CRS | validation |\n|---|---|---|\n")
    m.append("| distance | **EPSG:26912** NAD83 / UTM 12N, metres | "
             "Phoenix→Tucson measured **170.45 km** against the 170.4 km "
             "reference; geodesic ground truth 170.51 km; error 61 m "
             "(0.036%) |\n")
    m.append("| area | **EPSG:5070** NAD83 / Conus Albers, equal-area | class "
             "totals reproduce the source `ACRES` field within 0.03% |\n")
    m.append("| storage | EPSG:4326 | |\n")
    m.append("\nWeb Mercator `SHAPE_Area` was never used for area. At "
             "Arizona's latitude it overstates by roughly 1/cos²(lat) ≈ 44%. "
             "No distance was computed in degrees.\n")

    m.append("\n## Sources\n\n")
    m.append(f"{len(ok)} datasets retrieved, {len(bad)} failed. Full log with "
             "timestamps in `DATA_STATUS.md`.\n\n")
    m.append("| dataset | records | retrieved (UTC) | endpoint |\n")
    m.append("|---|---:|---|---|\n")
    for r in ok:
        m.append(f"| {r['dataset']} | {r.get('records') or ''} | "
                 f"{r['timestamp']} | `{r['url']}` |\n")

    m.append("\n## Datasets that FAILED — and what was NOT substituted\n")
    for r in bad:
        m.append(f"\n### {r['dataset']}\n")
        m.append(f"- endpoint: `{r['url']}`\n- time: {r['timestamp']}\n")
        m.append(f"- error: `{r['detail'][:400]}`\n")
        m.append(f"- manual download: {r['manual_download_url']}\n")
    m.append("\n**EIA-860M was not silently replaced with the annual file.** "
             "The annual EIA-860 2024 release is used for retirements and is "
             "labelled as such. The consequence is concrete: any retirement "
             "announced after the 2024 annual release is **not** in this "
             "screen. Re-run once `/cneaf/electricity/` is back up.\n")

    m.append("\n## Derived vs read fields\n\n")
    m.append("| field | provenance |\n|---|---|\n")
    for fld, prov in [
        ("land_status", "**READ** — `CATEGORY` from the BLM Arizona full-res "
                        "SMA layer, mapped through a fixed table over its "
                        "15-value domain"),
        ("acquirable", "**DERIVED** from land_status"),
        ("adjacency_note", "**DERIVED** — 1-mile buffer intersect against "
                           "state trust and tribal polygons"),
        ("parcel_acres", "**COMPUTED** in EPSG:5070 equal-area"),
        ("max_volt_kv / min_volt_kv", "**READ** from HIFLD, with -999999 "
                                      "sentinels nulled. HIFLD's own "
                                      "`MAX_INFER`/`MIN_INFER` flags are "
                                      "carried through as `INFERRED` in "
                                      "`max_volt_provenance`"),
        ("lines_count", "**READ** from HIFLD `LINES`, sentinels nulled"),
        ("retired_mw_on_site", "**READ** — sum of EIA-860 2024 `Nameplate "
                               "Capacity (MW)` over qualifying units"),
        ("est_capacity_mw", "**READ** for Pop 1 (EIA nameplate). **NULL** for "
                            "Pop 2 — see the capacity section below"),
        ("size_class / triggers", "**DERIVED** from est_capacity_mw against "
                                  "the buckets in AZ_SIZE_THRESHOLDS.md"),
        ("serving_utility", "**READ** from HIFLD territories, but the "
                            "*choice* among overlapping polygons is "
                            "**DERIVED** — see the ambiguity note"),
        ("utility_type", "**READ** from HIFLD `TYPE` where populated; "
                         "**INFERRED** from the utility name where HIFLD "
                         "says 'NOT AVAILABLE'. Which one applies is recorded "
                         "per row in `utility_type_basis`"),
        ("in_ama / groundwater_basin", "**READ** — point-in-polygon against "
                                       "ADWR layers"),
        ("municipal_water_available", "**DERIVED** — point inside an ADWR "
                                      "community water system service area"),
        ("nearest_surface_water_km", "**COMPUTED** against **perennial-only** "
                                     "NHD flowlines (FCode 46006)"),
        ("water_risk_score", "**DERIVED** from the brief's rubric"),
        ("political_risk_score", "**READ** priors from AZ_POLITICAL_NOTES.md "
                                 "where the jurisdiction was researched; "
                                 "**INFERRED** defaults otherwise, recorded "
                                 "in `political_prior_basis`"),
        ("prior_industrial_use", "**DERIVED** — 5/5 for retired plant sites; "
                                 "≤3/5 for substations, scored on electrical "
                                 "infrastructure density within 5 km"),
        ("dist_to_residential_km", "**DERIVED** — distance to nearest census "
                                   "block group at ≥200 persons/km²"),
        ("broadband_providers_PROXY", "**READ** from FCC BDC Dec-2024, but a "
                                      "**PROXY** — see below"),
    ]:
        m.append(f"| `{fld}` | {prov} |\n")

    m.append("""
## Capacity — the biggest single gap

`est_capacity_mw` is populated for **7 of 255** candidates.

The HIFLD substation schema carries **no capacity field at all**: its columns
are NAME, TYPE, STATUS, LINES, MAX_VOLT, MIN_VOLT and administrative metadata.
There is no MVA rating and no MW rating. Servable load depends on transformer
bank size, conductor rating and the utility's own planning limits, none of
which appear in any dataset acquired here.

Deriving MW from kV would have been fabrication, so **248 candidates carry a
null capacity and `size_class = NOT_DETERMINED`**, with `capacity_basis`
explaining why on every row. The brief's instruction — record MVA and do not
silently convert — could not even be exercised, because no MVA is published.

That gap is resolved by one phone call per site to the serving utility's system
planning group, not by any public dataset I could find.

## The broadband field is a proxy, not fiber

`broadband_providers_PROXY` counts fixed broadband providers reporting
availability in the containing census block group (FCC BDC, December 2024). It
is **not** a fiber route map and says nothing about carrier-class fiber
reaching a parcel or the cost to extend it. It carries 4.55 of 100 points,
deliberately the smallest weight. 84 candidates fall outside any block group
with data and score `UNSCORED` on this component; those rows carry
`score_max_available = 95.45` and `score_rescaled_to_100`.

## Assumptions
""")
    m.append(f"""
1. A point falling inside an ownership polygon inherits that polygon's status.
   Candidates are **points** (plant sites, substation sites), not parcels. A
   substation on a private inholding surrounded by BLM land reads as private
   here, and for acquisition purposes the relevant parcel may be neither.
2. Retired generator interconnection capacity is a meaningful proxy for future
   load-serving capability. It is an upper bound at best — a retired generator
   interconnection is not a commitment to serve load, and the two are
   physically different (export vs import).
3. Ten years is the flag threshold for interconnection rights lapsing. That is
   the brief's number, applied as given, not a legal determination.
4. Block-group population density ≥200/km² approximates "residential". It is a
   density proxy, not a land use survey.
5. Absence of a found moratorium equals absence of a moratorium. **This one is
   load-bearing and probably wrong — see below.**

## What would make this screen WRONG

These are ordered by how much damage each would do.

1. **The political scores on the top 25 are inferred, not researched.** All 25
   top candidates sit in jurisdictions that AZ_POLITICAL_NOTES.md did not
   cover, so each receives the default 8/8 moratorium and 5/5 no-ordinance
   score purely because nothing was found. A jurisdiction nobody has studied
   scores identically to one verified permissive. If Mohave, Yuma, Navajo,
   Apache or Greenlee county has quietly adopted a data center ordinance, the
   affected candidates are overscored by up to 13 of 22.7 political points and
   the ranking reorders substantially. **This is the single most likely way
   the screen is wrong.**
2. **Capacity is unknown for 248 of 255 candidates.** The ranking is driven by
   proximity and voltage, which are availability signals, not capacity
   signals. A 500 kV substation with no spare transformer capacity outranks a
   230 kV one with plenty. Nothing in the data distinguishes them.
3. **Utility assignment is ambiguous for {(allc['utility_assignment_confidence'].astype(str).str.startswith('AMBIGUOUS')).sum()} of {len(allc)} candidates.** HIFLD retail
   territories overlap heavily in Arizona. Where a small irrigation-district
   polygon beat a large IOU polygon on specificity, the named utility may be
   wrong even though the *list* of overlapping candidates is right.
4. **The substation layer is a third-party republication.** hifld-geoplatform
   opendata is sunset; the layer used carries the HIFLD schema and 77,946
   national records but is not a federal endpoint. Currency is unverified.
   185 of 901 Arizona substations have no usable voltage, and 168 have a
   voltage HIFLD itself flags as inferred.
5. **Water scores reward the absence of regulation.** 20/20 means "outside any
   AMA", which is a regulatory freedom, not physical water availability.
   {(top['in_ama'] == 'no').sum()} of the top 25 score 20 on that basis. A site
   with no AWS obligation and no water is scored better than one inside the
   Phoenix AMA with a designated provider.
6. **Points are not parcels.** No parcel geometry, ownership name, or
   assessor record was acquired. `county_assessor_note` is deliberately blank
   for you to fill. Nothing here establishes that the land at a given point is
   for sale, or who owns it.
7. **EIA-860M is missing**, so retirements announced since the 2024 annual
   release are absent. A newly announced 500 MW retirement would likely enter
   the top 5 and is simply not here.
8. **Ephemeral-stream reality.** Surface water uses perennial NHD only. If you
   reintroduce intermittent or ephemeral flowlines, every
   `nearest_surface_water_km` collapses toward zero and becomes meaningless.
9. **The CDC tax exemption is closed** to new applicants 1 Jul 2026 – 30 Jun
   2029. No score here assumes it. If a buyer already holds certification, the
   economics differ materially from what this screen implies.
""")
    open(os.path.join(OUTPUTS, "AZ_METHOD.md"), "w").write("".join(m))
    print("wrote AZ_METHOD.md")

    # =================================================================
    # AZ_COUNTIES_TO_CALL.md
    # =================================================================
    byc = top.groupby("county_gis").agg(
        n=("rank", "size"), best=("composite_score", "max"),
        mean=("composite_score", "mean"), water=("water_risk_score", "mean"),
        mw=("retired_mw_on_site", "sum")).sort_values(
        ["n", "best"], ascending=False)

    c = [f"# THREE COUNTIES TO CALL\n\nGenerated {STAMP}.\n"]
    c.append("\n## The recommendation\n")
    c.append("""
| priority | county | why | what to ask |
|---|---|---|---|
| **1** | **Navajo County** | Holds **Cholla**, the highest-scoring private site in Arizona at **93.64/100**. 1,128.8 MW of retired and announced coal capacity, 500 kV within 5 km, APS territory (ACC-regulated, a known and dockated process), outside any AMA, unincorporated. This is the single best combination of existing interconnection and low regulatory friction in the state. | Is there a county data center ordinance or moratorium, adopted or drafting? What is the zoning on the Cholla parcel and what did APS retain of the interconnection? |
| **2** | **Apache County** | Holds **Springerville (92.73)** and **Coronado (90.91)** — ranks 2 and 3, and **1,671 MW of announced retirement by 2032** between them. Highest mean score of any county in the top 25 (91.82). Both unincorporated, both outside any AMA, both scoring a full 25/25 on political risk. | Same ordinance question. Then: are the 2032 retirement dates firm, and would the owners (TEP at Springerville, SRP at Coronado) consider a site sale or lease ahead of retirement? |
| **3** | **Mohave County** | The **volume** play: **6 of the top 25** — more than any county except Maricopa — and unlike Maricopa every one scores a full **20/20 on water** (all outside any AMA). Mean score 74.09. Served by Mohave Electric Co-op and UNS Electric. No data center controversy on record. | Ordinance status; then which of PEACOCK, TAP318004/5, TAP310930, MCCONNICO, GRIFFITH have transformer capacity headroom — the one thing this screen cannot tell you. |

## Why not Maricopa, despite having the most sites

Maricopa has 8 of the top 25, more than any other county. It is third on this
list rather than first for three reasons that the composite score already
partly reflects:

- **Water.** Maricopa's top-25 sites average **14.25/20** on water against
  20/20 for Mohave, Yuma, Apache, Navajo and Greenlee. Most sit inside the
  Phoenix AMA with its Assured Water Supply regime.
- **Political.** Mean political score 20.88 versus 25.00 in Apache. Phoenix has
  an **adopted** data center ordinance (Z-TA-2-25-Y, 2 July 2025) requiring a
  Special Permit, half-mile transit spacing, a noise study within 300 ft of
  residential, and a **utility will-serve letter**. Buckeye scores 0/20 on
  water because of the 2,000 AF/yr Tract cap.
- **Competition.** It is where everyone else is already looking.

Maricopa is not a bad place to transact — Phoenix's rules are procedural rather
than hostile, and a project that satisfies them gets a fair hearing. It is
simply not where the *screen* says the unexploited value is.

## Why not Pima or Pinal

Pima (35) and Pinal (29) have the second and third largest private candidate
counts statewide, and **neither places a single site in the top 25.** That is
the screen working as intended: both counties carry the organised-opposition
penalty by default per AZ_POLITICAL_NOTES.md, both sit largely inside AMAs, and
Pima carries the Project Blue litigation overhang — an open-meeting-law suit,
an Attorney General suit against the ACC, and an AG appeal.

Pima County has demonstrated it will approve and sell over a city's objection.
That is genuinely an opportunity. But it costs a year of sustained public anger
and a buyer will price that in.

## The caveat that applies to all three

**Every one of these three counties scores well partly because nobody has
researched it.** AZ_POLITICAL_NOTES.md covers Pima, Tucson, Marana, Phoenix,
Buckeye, Pinal, Cochise and Chandler. Navajo, Apache and Mohave appear only in
the closing list of "rural counties — nothing found for any of them, which most
likely means nothing has been proposed there yet rather than that they are
permissive."

So all three inherit the default 8/8 for "no moratorium" and 5/5 for "no
restrictive ordinance" on the strength of an absence. **That is exactly why
these are phone calls and not conclusions.** One call to each county planning
department either confirms the score or collapses it.

## Ranked by county, top 25 private candidates
""")
    c.append("\n| county | sites in top 25 | best score | mean score | "
             "mean water | retired/announced MW in top 25 |\n")
    c.append("|---|---:|---:|---:|---:|---:|\n")
    for k, r in byc.iterrows():
        c.append(f"| {k} | {int(r['n'])} | {r['best']:.2f} | "
                 f"{r['mean']:.2f} | {r['water']:.1f} | {r['mw']:,.0f} |\n")
    open(os.path.join(OUTPUTS, "AZ_COUNTIES_TO_CALL.md"), "w").write("".join(c))
    print("wrote AZ_COUNTIES_TO_CALL.md")

    # =================================================================
    # AZ_FINDINGS_SUMMARY.md
    # =================================================================
    s = [f"# ARIZONA POWERED-LAND SCREEN — FINDINGS\n\nGenerated {STAMP}. "
         "Private land only. Every number below is read from source data or "
         "computed from it; nothing is estimated.\n"]

    s.append("\n## Headline\n\n")
    s.append(f"- **{len(allc)} candidate sites evaluated** — "
             f"{(allc['cand_type'] == 'pop1_retired_plant').sum()} retired or "
             f"announced-retirement plants ≥50 MW, plus "
             f"{(allc['cand_type'] == 'pop2_hv_substation').sum()} substations "
             f"≥115 kV more than 2 km from one.\n")
    s.append(f"- **{len(priv)} sit on private land** and form the working "
             f"universe. **{len(excl)} do not** and are retained separately.\n")
    s.append(f"- Score range on private land: **{priv['composite_score'].min():.2f} "
             f"to {priv['composite_score'].max():.2f}** out of 100.\n")
    s.append(f"- **24 non-private candidates scored at or above the top-25 "
             f"cut-off** and were excluded on land status alone — including "
             f"**Navajo Generating Station at 91.82**, which would have "
             f"ranked 2nd overall.\n")
    s.append(f"- **{(top['in_ama'] == 'no').sum()} of the top 25 are outside "
             f"any AMA.** Read that as regulatory freedom, not available "
             f"water.\n")
    s.append("- **The Arizona CDC tax exemption is closed to new applicants "
             "1 Jul 2026 – 30 Jun 2029.** Nothing here assumes it.\n")

    s.append("\n## Top 25 private candidates\n\n")
    s.append("| # | site | type | score | county | jurisdiction | serving "
             "utility | utility type | max kV ≤5 km | dist to nearest sub "
             "(km) | retired MW | water | political | map |\n")
    s.append("|---:|---|---|---:|---|---|---|---|---:|---:|---:|---:|---:|---|\n")
    for _, r in top.iterrows():
        gm = (f"https://www.google.com/maps/search/?api=1&query="
              f"{r['lat']:.6f},{r['lon']:.6f}")
        kv = r["max_kv_within_5km"]
        s.append(
            f"| {int(r['rank'])} | **{r['cand_name']}** | "
            f"{'retired plant' if r['cand_type'] == 'pop1_retired_plant' else 'substation'} | "
            f"**{r['composite_score']:.2f}** | {r['county_gis']} | "
            f"{r['jurisdiction']} | {r['serving_utility']} | "
            f"`{r['utility_type']}` | {kv:,.0f} | "
            f"{r['dist_nearest_substation_km']:.2f} | "
            f"{r['retired_mw_on_site']:,.0f} | "
            f"{int(r['water_risk_score'])}/20 | "
            f"{r['political_risk_score']:.0f}/25 | [map]({gm}) |\n")

    s.append("\n## The five sites that actually matter\n")
    s.append("""
Ranks 4 onward are substations — real interconnection points, but with no
published capacity and no retired generation behind them. The first three are
different in kind: they are retiring coal plants with existing high-voltage
interconnection, and they are where the value is.

| site | county | MW | status | why it matters |
|---|---|---:|---|---|
| **Cholla** | Navajo | 1,128.8 | units retired 2015 and 2020; remainder announced **2025** | Highest score in the state. APS territory — ACC-regulated, so there is a docket and a known process. 500 kV within 5 km. Outside any AMA. Unincorporated. |
| **Springerville** | Apache | 849.6 announced (2,179.2 total nameplate) | announced **2032** | Only part of the plant is retiring, so the site stays live and staffed. 345 kV. Long lead time is a negotiating advantage, not a problem. |
| **Coronado** | Apache | 821.8 | announced **2032** | 500 kV. SRP-owned generation, but the retail territory is Navopache co-op — so the conversation is with a co-op **and** its G&T supplier, not the ACC. |
| **Navajo (NGS)** | Coconino | 2,409.3 | retired **2019** | **EXCLUDED — tribal land, `lease_only_bia`.** Scored 91.82, would have been 2nd overall. The largest retired interconnection in Arizona is not purchasable, only leasable through BIA. |
| **Apache Station** | Cochise | — | **no retirement recorded** | The brief listed it as of interest. **The data does not support that.** EIA-860 2024 shows 11 units, 826.3 MW nameplate, statuses OP/P/SB/U and **no retirement year and no planned retirement year.** Verified against the workbook rather than assumed. |
""")

    s.append("\n## What you are structurally excluded from\n\n")
    s.append("Top 10 non-acquirable sites that would otherwise have scored "
             "into contention:\n\n")
    s.append("| # | site | score | land status | acquirable | county | "
             "would have ranked |\n")
    s.append("|---:|---|---:|---|---|---|---|\n")
    allsorted = allc.sort_values("composite_score", ascending=False
                                 ).reset_index(drop=True)
    for i, r in excl.head(10).iterrows():
        wr = int(allsorted[allsorted["cand_id"] == r["cand_id"]].index[0]) + 1
        s.append(f"| {i + 1} | {r['cand_name']} | {r['composite_score']:.2f} | "
                 f"`{r['land_status']}` | `{r['acquirable']}` | "
                 f"{r['county_gis']} | {wr} of {len(allc)} overall |\n")
    s.append("\n**State trust land is not a dead end.** 5 of these are "
             "`auction_only` — ASLD auctions under A.R.S. Title 37 are a real "
             "if slow path, and state trust is 9.28 million acres.\n")

    s.append("\n## Scoring\n\nThe brief's components sum to 110, not 100, so "
             "every one is multiplied by 100/110 = 0.909090…\n\n")
    s.append("| component | raw | normalized | rationale |\n")
    s.append("|---|---:|---:|---|\n")
    for k, v, why in [
        ("existing interconnection", 25, "the actual asset"),
        ("substation proximity", 15, "availability signal"),
        ("substation voltage", 10, "availability signal"),
        ("transmission proximity/voltage", 10, "availability signal"),
        ("water risk", 20, "elevated for Arizona, deliberately"),
        ("political risk", 25, "jurisdiction priors + 2 computed components"),
        ("broadband proxy", 5, "folded down — the weakest signal"),
    ]:
        s.append(f"| {k} | {v} | {v * 100 / 110:.4f} | {why} |\n")
    s.append(f"| **TOTAL** | **110** | **100.0000** | |\n")
    s.append("\n84 candidates lack broadband data. Their weight is **not** "
             "redistributed: those rows carry `score_max_available = 95.45` "
             "and a transparently rescaled `score_rescaled_to_100`.\n")

    s.append("\n## Files\n\n")
    s.append("| file | what it is |\n|---|---|\n")
    for fn, d in [
        ("az_top25.csv", "the 25 ranked private candidates, 107 columns, with "
                         "`google_maps_url` and a blank `county_assessor_note`"),
        ("az_all_private_ranked.csv", "all 166 private candidates ranked"),
        ("az_excluded_high_score.csv", "the 10 highest-scoring non-acquirable "
                                       "sites"),
        ("az_candidates.gpkg", "15 layers — candidates, ownership, power, "
                               "water, boundaries"),
        ("AZ_COUNTIES_TO_CALL.md", "the three counties, with what to ask"),
        ("AZ_WATER_NOTES.md", "per-candidate AMA, basin, caps, and what a "
                              "developer must prove"),
        ("AZ_UTILITY_MAP.md", "who serves what, which regime applies, "
                              "published contacts only"),
        ("AZ_LAND_OWNERSHIP.md", "the Step 2 ownership filter and its "
                                 "cross-checks"),
        ("AZ_METHOD.md", "sources, assumptions, derived vs read, and what "
                         "would make this wrong"),
        ("AZ_VERIFICATION.md", "Step 10 checks, all re-run from disk"),
        ("DATA_STATUS.md", "every dataset attempted, with errors"),
        ("az_screen.qgz / az_screen_build.py", "QGIS project and a PyQGIS "
                                               "rebuild script"),
    ]:
        s.append(f"| `{fn}` | {d} |\n")

    s.append("\n## Read this before acting on the ranking\n")
    s.append(f"""
1. **All 25 top candidates have INFERRED political scores.** None sits in a
   jurisdiction that AZ_POLITICAL_NOTES.md researched. Their near-perfect
   political scores come from *nothing having been found*, which is not the
   same as nothing existing. This is the most likely way the ranking is wrong.
2. **Capacity is unknown for 248 of 255 sites.** HIFLD publishes no MVA and no
   MW for substations. The ranking measures *access* to the grid, not *room*
   on it.
3. **{(allc['utility_assignment_confidence'].astype(str).str.startswith('AMBIGUOUS')).sum()} of {len(allc)} candidates sit in overlapping utility territories.**
   `serving_utility` is a best guess among them; `all_overlapping_utilities`
   lists the alternatives, and for several top-25 sites APS is in that list.
4. **These are points, not parcels.** No assessor data was acquired. Nothing
   here says the land is for sale or who owns it.
""")
    open(os.path.join(OUTPUTS, "AZ_FINDINGS_SUMMARY.md"), "w").write("".join(s))
    print("wrote AZ_FINDINGS_SUMMARY.md")


if __name__ == "__main__":
    main()
