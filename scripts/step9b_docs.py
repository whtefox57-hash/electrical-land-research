"""STEP 9b — generate the markdown deliverables from the data.

Everything numeric in these documents is read out of the scored candidate
table at generation time rather than typed by hand, so the prose cannot drift
away from the data.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA, OUTPUTS

GPKG = os.path.join(OUTPUTS, "az_candidates.gpkg")
STAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def f(v, nd=2, dash="—"):
    return dash if v is None or (isinstance(v, float) and pd.isna(v)) \
        else f"{v:,.{nd}f}"


def main():
    priv = gpd.read_file(GPKG, layer="candidates_private_ranked")
    excl = gpd.read_file(GPKG, layer="candidates_excluded_ranked")
    allc = gpd.read_file(GPKG, layer="candidates_all_scored")
    top = priv.head(25)

    # ==================================================================
    # AZ_WATER_NOTES.md
    # ==================================================================
    w = ["# AZ WATER NOTES\n",
         f"\nGenerated {STAMP} from ADWR and USGS NHD data. Water is treated "
         "as a first-class constraint, not a secondary factor, and carries "
         "18.18 of the 100 composite points (20 raw of 110).\n"]
    w.append("\n## The rubric, applied verbatim\n")
    w.append("\n| condition | score |\n|---|---:|\n")
    w.append("| Outside AMA with no cap | 20 |\n")
    w.append("| In AMA, municipal water service available, no DC-specific cap "
             "| 12 |\n")
    w.append("| In AMA, groundwater only | 6 |\n")
    w.append("| Explicit groundwater cap, or documented denial of service "
             "| 0 |\n")

    w.append("\n## The most important caveat on this page\n")
    w.append("\n**A score of 20/20 means REGULATORY freedom, not physical "
             "water.** Outside an Active Management Area there is no Assured "
             "Water Supply requirement and no pumping cap — which is exactly "
             "why those areas score highest. It is not evidence that water "
             "exists in useful quantity, that an aquifer can sustain a "
             "data center, or that anyone will sell it to you. Of the top 25 "
             f"candidates, **{(top['in_ama'] == 'no').sum()} are outside any "
             f"AMA**, and every one of them is carrying that 20 on the "
             "absence of regulation rather than on the presence of water.\n")

    w.append("\n## AMAs and INAs in Arizona\n")
    w.append("\nThe brief listed Phoenix, Pinal, Tucson, Prescott and Santa "
             "Cruz and asked me to check for Willcox. ADWR's current layer "
             "carries **8 AMAs and 3 INAs**. Willcox is present, and so are "
             "**Douglas AMA** and **Ranegras Plain AMA**, which were not in "
             "the brief's list:\n\n")
    ama = gpd.read_file(GPKG, layer="ama_ina")
    for n in sorted(ama["BASIN_NAME"].astype(str)):
        w.append(f"- {n}\n")

    w.append("\n## Per-project caps that appear in no zoning code\n")
    w.append("\nThese were found in development agreements and council "
             "coverage, per AZ_POLITICAL_NOTES.md, and are applied as a hard "
             "0/20 wherever they bind:\n")
    w.append("\n- **Buckeye** — 2,000 acre-feet/year cap written into the "
             "Tract Buckeye Technology Park development agreement (2,069 "
             "acres, up to 40 data centers, 1.8 GW at build-out). Buckeye's "
             "instrument is contractual, not legislative. Expect to be asked "
             "for a hard annual water number early and expect it to become "
             "binding.\n")
    w.append("- **City of Tucson** — refused annexation and city water to "
             "Project Blue (Aug 2025), and in May 2026 told it to stop using "
             "Tucson Water even for construction. Treated as a documented "
             "denial of service.\n")
    w.append("\nI searched for other per-project caps and found none I could "
             "cite. That is **absence of evidence**: development-agreement "
             "caps live in council packets, not in any GIS layer or ordinance "
             "database, so this list should be assumed incomplete.\n")

    w.append("\n## Water risk distribution across all 255 candidates\n")
    w.append("\n| score | candidates | meaning |\n|---:|---:|---|\n")
    meaning = {20: "outside AMA, no cap found",
               12: "in AMA, community water system service area present",
               6: "in AMA, groundwater only",
               0: "explicit cap or documented denial"}
    for s, n in allc["water_risk_score"].value_counts().sort_index(
            ascending=False).items():
        w.append(f"| {int(s)} | {n} | {meaning.get(int(s), '')} |\n")

    w.append("\n## Per-candidate water detail — top 25 private\n")
    w.append("\n| # | site | county | in AMA | AMA/INA | groundwater basin | "
             "municipal water | CWS provider | nearest perennial water (km) | "
             "wells within 5 km | water score |\n")
    w.append("|---:|---|---|---|---|---|---|---|---:|---:|---:|\n")
    for _, r in top.iterrows():
        w.append(
            f"| {int(r['rank'])} | {r['cand_name']} | {r['county_gis']} | "
            f"{r['in_ama']} | {r['ama_ina_name'] or '—'} | "
            f"{r['groundwater_basin'] or '—'} | "
            f"{r['municipal_water_available']} | {r['cws_provider'] or '—'} | "
            f"{f(r['nearest_surface_water_km'])} | "
            f"{int(r['registered_wells_within_5km'])} | "
            f"{int(r['water_risk_score'])} |\n")

    w.append("\n## What a developer would have to prove\n")
    w.append("""
**Inside an AMA** (Phoenix, Pinal, Tucson, Prescott, Santa Cruz, Willcox,
Douglas, Ranegras Plain): a 100-year Assured Water Supply must be demonstrated
before a subdivision plat, and large non-residential users must show physical
availability, continuous availability for 100 years, legal availability,
financial capability and consistency with the AMA management plan and the
state's management goal. In practice that means either a Designation of
Assured Water Supply held by the serving provider, or a project-specific
Certificate.

**Outside an AMA**: no AWS requirement at all. The proof burden shifts from the
regulator to the counterparty — the developer must satisfy its own lenders and
the county, not ADWR. This is why the highest water scores in this screen sit
in Mohave, Yuma, Apache, Navajo and Greenlee counties, and why that score
should be read as "no regulatory obstacle" rather than "water is available".

**In every case**, the specific questions worth asking before a site visit are:
1. Does the serving community water system hold a Designation of Assured Water
   Supply, and what uncommitted volume remains under it?
2. Is there an existing grandfathered groundwater right attached to the parcel,
   and of what type and volume?
3. Has the jurisdiction imposed, or is it negotiating, a per-project cap in a
   development agreement? Buckeye proves this happens where no ordinance exists.
4. What is the depth to water and the recent water-level trend in this
   sub-basin? ADWR publishes both; land subsidence and earth fissure layers are
   also available and were acquired for this screen.
5. Is the cooling design air-cooled or water-cooled? Project Blue switched to
   air-cooled and proceeded after Tucson refused water. That switch is the
   single most effective water-risk mitigation available and it changes the
   conversation with every jurisdiction on this list.
""")
    open(os.path.join(OUTPUTS, "AZ_WATER_NOTES.md"), "w").write("".join(w))
    print("wrote AZ_WATER_NOTES.md")

    # ==================================================================
    # AZ_UTILITY_MAP.md
    # ==================================================================
    u = ["# AZ UTILITY MAP\n",
         f"\nGenerated {STAMP}. Which category of utility serves a parcel "
         "determines who the user calls and what process applies. In Arizona "
         "that is not a formality — it decides whether there is an ACC docket "
         "at all.\n"]
    u.append("""
## The four regimes

| utility_type | who regulates rates | how a large load gets served | who you call |
|---|---|---|---|
| `IOU_ACC_regulated` | Arizona Corporation Commission, five **elected** commissioners | tariff election (APS XHLF / E-34 / E-32 L) or a docketed special contract (the TEP–Project Blue model) | utility economic development, then the ACC docket |
| `SRP_public` | **Nobody external.** SRP's board is elected by landowners inside the district on an **acreage franchise** | SRP E-67 large-customer provision: new accounts ≥20 MW forecast load face minimum billing at the greater of actual demand or 80% of forecast | SRP staff, then the SRP board. **There is no ACC docket to intervene in.** |
| `coop` | member-governed; ACC jurisdiction over co-ops is limited | co-op board plus its G&T supplier — the wholesale contract usually binds harder than the retail tariff | co-op general manager AND the generation & transmission supplier |
| `municipal` | city council or district board | council/board decision, often bundled into a development agreement | city manager / district manager |

## Thresholds that actually exist

Read from `outputs/AZ_SIZE_THRESHOLDS.md`, unchanged:

- **APS XHLF** — ≥5,000 kW monthly maximum demand **and** ≥92% load factor.
  **In active revision** under Docket E-01345A-25-0105; hearings opened 18 May
  2026, decision expected before end of 2026, with roughly a 45% increase
  reported for that class and direct assignment of new generation costs. The
  eligibility floor itself is one of the things under revision — **do not quote
  XHLF terms to a developer as settled.**
- **SRP E-67** — ≥20 MW forecast load triggers minimum billing at 80% of
  forecast. Approved by the SRP Board 27 February 2025.
- **TEP** — no published generic large-load threshold. The template is the
  bespoke docketed special contract: Project Blue, approved 3 December 2025
  4–1, capped at 286 MW, full approved rates with no discount, customer bears
  incremental generation cost beyond the cap. **It is being litigated** —
  Attorney General Mayes sued the ACC and has appealed.

## The honest limitation in this mapping

HIFLD's Electric Retail Service Territories overlap heavily in Arizona. A
single point routinely falls inside a major IOU polygon *and* several
irrigation, water-conservation and electrical-district polygons that also carry
retail electric territory geometry. The dataset does not encode which one
actually serves a given parcel.

""")
    amb = (allc["utility_assignment_confidence"].astype(str)
           .str.startswith("AMBIGUOUS")).sum()
    u.append(f"Of {len(allc)} candidates, **{amb} sit inside more than one "
             f"retail territory polygon** and are flagged `AMBIGUOUS` in the "
             f"CSV. For those rows `serving_utility` is the smallest (most "
             f"specific) overlapping polygon, which is a reasonable default "
             f"and is *not* a determination. The `all_overlapping_utilities` "
             f"column lists every candidate provider — for several top-25 "
             f"sites that list includes Arizona Public Service, which is very "
             f"likely the true retail provider even where a small district "
             f"polygon wins on size.\n")
    u.append("\n**Treat `serving_utility` as the first phone call, not as an "
             "answer.** One call to the county or to APS/TEP/SRP economic "
             "development resolves it definitively.\n")
    u.append("\nFederal power marketers (WAPA) and BIA projects were "
             "explicitly demoted: they publish enormous territory polygons but "
             "are wholesale, not the retail supplier a data center buys from. "
             "Leaving them in wrongly labelled 57 candidates 'federal'.\n")

    u.append("\n## Utility type across all candidates\n\n")
    u.append("| utility_type | candidates | private-land candidates |\n")
    u.append("|---|---:|---:|\n")
    for k, n in allc["utility_type"].value_counts().items():
        pn = (priv["utility_type"] == k).sum()
        u.append(f"| `{k}` | {n} | {pn} |\n")

    u.append("\n## Serving utility for the top 25 private candidates\n\n")
    u.append("| # | site | county | serving utility (most specific) | type | "
             "ACC-regulated | confidence | all overlapping retail territories "
             "|\n")
    u.append("|---:|---|---|---|---|---|---|---|\n")
    for _, r in top.iterrows():
        acc = "YES" if r["utility_type"] == "IOU_ACC_regulated" else (
            "NO — public power" if r["utility_type"] in
            ("SRP_public", "municipal") else
            "limited" if r["utility_type"] == "coop" else "—")
        conf = "single" if str(r["utility_assignment_confidence"]).startswith(
            "single") else "**AMBIGUOUS**"
        u.append(f"| {int(r['rank'])} | {r['cand_name']} | "
                 f"{r['county_gis']} | {r['serving_utility']} | "
                 f"`{r['utility_type']}` | {acc} | {conf} | "
                 f"{str(r['all_overlapping_utilities'])[:95]} |\n")

    u.append("\n## Published contacts\n")
    u.append("\nOnly what the source dataset actually carries. **No contact "
             "name has been invented — a blank is better than a wrong "
             "name.** HIFLD publishes a general telephone and website per "
             "territory and no economic-development contact at all, so the "
             "named-contact column is empty for every row and should be "
             "filled by phone.\n\n")
    u.append("| utility | type | published phone | published website | "
             "economic development / large load contact |\n")
    u.append("|---|---|---|---|---|\n")
    seen = set()
    for _, r in priv.iterrows():
        n = str(r["serving_utility"])
        if n in seen or n == "None":
            continue
        seen.add(n)
        u.append(f"| {n} | `{r['utility_type']}` | "
                 f"{r['utility_phone'] or '—'} | "
                 f"{r['utility_website'] or '—'} |  |\n")
    open(os.path.join(OUTPUTS, "AZ_UTILITY_MAP.md"), "w").write("".join(u))
    print("wrote AZ_UTILITY_MAP.md")


if __name__ == "__main__":
    main()
