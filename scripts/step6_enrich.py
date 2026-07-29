"""STEP 5 (continued) — water, broadband proxy, and capacity fields.

Water risk rubric, applied verbatim from the brief (0-20):
    outside AMA, no cap                                        20
    in AMA, municipal water service available, no DC cap       12
    in AMA, groundwater only                                    6
    explicit groundwater cap, or documented denial of service    0

Capacity: the honest constraint. The HIFLD substation schema contains NO
capacity field — its columns are NAME, TYPE, STATUS, LINES, MAX_VOLT,
MIN_VOLT and administrative metadata. There is no MVA rating and no MW
rating. Voltage alone does not give servable load: that needs conductor
rating, transformer bank size and the utility's own planning limits, none of
which are in any acquired dataset.

So est_capacity_mw is populated ONLY for Pop 1 sites, from EIA-860's read
Nameplate Capacity (MW). For Pop 2 substations it is left NULL with
capacity_basis stating why. Inventing MW from kV would be fabrication.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_DIST, CRS_WGS84, DATA

WAT = os.path.join(DATA, "az_water.gpkg")
RAW = os.path.join(DATA, "az_candidates_raw.gpkg")
OUT = os.path.join(DATA, "az_candidates_enriched.gpkg")

# Per-project caps found in council packets / development agreements, not in
# any zoning code. Sourced from outputs/AZ_POLITICAL_NOTES.md.
JURISDICTION_WATER_CAPS = {
    "BUCKEYE": ("2,000 acre-feet/year cap written into the Tract Buckeye "
                "Technology Park development agreement (2,069 ac, up to 40 "
                "data centers, 1.8 GW). Precedent: Buckeye negotiates the "
                "constraint into the agreement rather than legislating it. "
                "Expect a hard annual water number to become contractually "
                "binding.", "development_agreement_cap"),
    "TUCSON": ("City of Tucson refused annexation and city water to Project "
               "Blue (Aug 2025) and in May 2026 told it to stop using Tucson "
               "Water even for construction. Documented denial of water "
               "service.", "documented_denial"),
}

SIZE_BUCKETS = [
    (0, 5, "sub_tariff", "below APS XHLF floor (5 MW)"),
    (5, 20, "xhlf_eligible", "APS XHLF >=5 MW and >=92% load factor"),
    (20, 100, "srp_minimum_bill",
     "SRP E-67 minimum billing (>=20 MW forecast load, 80% of forecast); "
     "Tucson draft 20 MW threshold if adopted"),
    (100, 286, "large_load", "bespoke utility negotiation territory"),
    (286, 1e9, "project_blue_scale",
     "at/above the 286 MW TEP-Project Blue special contract, the only "
     "ACC-approved AZ large-load contract to date"),
]


def bucket(mw):
    if pd.isna(mw):
        return ("NOT_DETERMINED",
                "cannot be assessed — no capacity figure available")
    for lo, hi, name, trig in SIZE_BUCKETS:
        if lo <= mw < hi:
            return name, trig
    return "NOT_DETERMINED", "cannot be assessed"


def main():
    print("STEP 5b — water, broadband, capacity\n" + "=" * 60)
    cand = gpd.read_file(RAW, layer="candidates_all").to_crs(CRS_DIST)
    ama = gpd.read_file(WAT, layer="ama_ina").to_crs(CRS_DIST)
    basin = gpd.read_file(WAT, layer="groundwater_basin").to_crs(CRS_DIST)
    subb = gpd.read_file(WAT, layer="groundwater_subbasin").to_crs(CRS_DIST)
    cws = gpd.read_file(WAT, layer="cws_service_area").to_crs(CRS_DIST)
    peren = gpd.read_file(WAT, layer="nhd_perennial").to_crs(CRS_DIST)
    wells = gpd.read_file(WAT, layer="well_registry").to_crs(CRS_DIST)
    bb = gpd.read_file(WAT, layer="fcc_broadband_blockgroups").to_crs(CRS_DIST)
    print(f"  ama={len(ama)} basins={len(basin)} cws={len(cws)} "
          f"perennial={len(peren)} wells={len(wells):,} bg={len(bb)}")

    def pip(target, col, newcol):
        j = gpd.sjoin(cand[["geometry"]], target[["geometry", col]],
                      predicate="within", how="left")
        j = j[~j.index.duplicated(keep="first")].reindex(cand.index)
        cand[newcol] = j[col]

    # ---- AMA / INA -------------------------------------------------------
    pip(ama, "BASIN_NAME", "ama_ina_name")
    cand["in_ama"] = np.where(
        cand["ama_ina_name"].astype(str).str.contains("AMA", na=False), "yes",
        "no")
    cand["in_ina"] = np.where(
        cand["ama_ina_name"].astype(str).str.contains("INA", na=False), "yes",
        "no")

    # ---- groundwater basin / sub-basin -----------------------------------
    pip(basin, "BASIN_NAME", "groundwater_basin")
    sub_col = "SUBBASIN_NAME" if "SUBBASIN_NAME" in subb.columns else next(
        (c for c in subb.columns if "SUB" in c.upper() and "NAME" in c.upper()),
        None)
    if sub_col:
        pip(subb, sub_col, "groundwater_subbasin")
    else:
        cand["groundwater_subbasin"] = None

    # ---- municipal water service ------------------------------------------
    j = gpd.sjoin(cand[["geometry"]],
                  cws[["geometry", "CWS_NAME", "OWNER_NAME", "POPULATION"]],
                  predicate="within", how="left")
    j = j[~j.index.duplicated(keep="first")].reindex(cand.index)
    cand["cws_provider"] = j["CWS_NAME"]
    cand["municipal_water_available"] = np.where(
        cand["cws_provider"].notna(), "yes", "no")

    # ---- nearest perennial surface water ----------------------------------
    n = gpd.sjoin_nearest(cand[["geometry"]],
                          peren[["geometry", "GNIS_Name"]], how="left",
                          distance_col="d")
    n = n[~n.index.duplicated(keep="first")].reindex(cand.index)
    cand["nearest_surface_water_km"] = n["d"] / 1000
    cand["nearest_surface_water_name"] = n["GNIS_Name"]
    cand["nearest_surface_water_basis"] = (
        "PERENNIAL NHD flowlines only (FCode 46006). Arizona NHD is 62% "
        "ephemeral and 26% intermittent; distance to an arbitrary flowline "
        "would usually be measuring a dry wash.")

    # ---- wells within 5 km -------------------------------------------------
    buf = cand[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(5000)
    wj = gpd.sjoin(buf, wells[["geometry"]], predicate="intersects",
                   how="left")
    cand["registered_wells_within_5km"] = (
        wj.groupby(level=0)["index_right"].count().reindex(
            cand.index).fillna(0).astype(int))

    # ---- water risk score ---------------------------------------------------
    juris = cand["jurisdiction"].astype(str).str.upper()
    cap_note, cap_kind = [], []
    for j_ in juris:
        hit = next((v for k, v in JURISDICTION_WATER_CAPS.items() if k in j_),
                   None)
        cap_note.append(hit[0] if hit else "")
        cap_kind.append(hit[1] if hit else "")
    cand["water_cap_note"] = cap_note
    cand["water_cap_kind"] = cap_kind

    score, basis = [], []
    for _, r in cand.iterrows():
        if r["water_cap_kind"] in ("development_agreement_cap",
                                   "documented_denial"):
            score.append(0)
            basis.append("0/20 — explicit cap or documented denial of water "
                         "service in this jurisdiction")
        elif r["in_ama"] == "yes":
            if r["municipal_water_available"] == "yes":
                score.append(12)
                basis.append("12/20 — inside AMA, inside a community water "
                             "system service area, no DC-specific cap found")
            else:
                score.append(6)
                basis.append("6/20 — inside AMA, groundwater only (no CWS "
                             "service area at this point)")
        else:
            score.append(20)
            basis.append("20/20 — outside any AMA, no cap found. NOTE: "
                         "outside-AMA means no Assured Water Supply "
                         "requirement, which is a regulatory freedom, NOT "
                         "evidence that water is physically available")
        basis[-1] = basis[-1]
    cand["water_risk_score"] = score
    cand["water_risk_basis"] = basis

    # ---- broadband proxy ----------------------------------------------------
    bj = gpd.sjoin(cand[["geometry"]],
                   bb[["geometry", "GEOID", "UniqueProviders",
                       "UniqueProvidersFiber"]],
                   predicate="within", how="left")
    bj = bj[~bj.index.duplicated(keep="first")].reindex(cand.index)
    cand["bg_geoid"] = bj["GEOID"]
    cand["broadband_providers_PROXY"] = bj["UniqueProviders"]
    cand["broadband_fiber_providers_PROXY"] = bj["UniqueProvidersFiber"]
    cand["broadband_basis"] = (
        "PROXY ONLY — FCC BDC Dec-2024 count of fixed broadband providers "
        "reporting availability in the containing census block group. This is "
        "NOT a fiber route map and says nothing about carrier-class fiber "
        "reaching the parcel or the cost to extend it.")

    # ---- capacity -----------------------------------------------------------
    is_p1 = cand["cand_type"] == "pop1_retired_plant"
    cand["est_capacity_mw"] = np.where(is_p1, cand["retired_mw_on_site"],
                                       np.nan)
    cand["substation_mva_published"] = np.nan  # HIFLD publishes none
    cand["capacity_basis"] = np.where(
        is_p1,
        "READ — sum of EIA-860 2024 'Nameplate Capacity (MW)' over units at "
        "this plant with an actual retirement year >=2010 or a coerced "
        "non-null 'Planned Retirement Year'. Treated as an upper bound on "
        "servable load because it reflects historic generator interconnection "
        "capacity, not a utility commitment to serve load.",
        "NOT DERIVABLE — the HIFLD substation schema carries no MVA and no MW "
        "rating (fields are NAME/TYPE/STATUS/LINES/MAX_VOLT/MIN_VOLT only). "
        "Servable load needs transformer bank size, conductor rating and the "
        "utility's planning limits, none of which are in any acquired "
        "dataset. Deriving MW from kV would be fabrication, so this is left "
        "null. Resolve via the serving utility's system planning group.")
    cand["capacity_confidence"] = np.where(
        is_p1,
        np.where(cand["retired_mw_on_site"] >= 200, "medium", "medium"),
        "low")

    sc = [bucket(v) for v in cand["est_capacity_mw"]]
    cand["size_class"] = [s[0] for s in sc]
    cand["triggers"] = [s[1] for s in sc]

    # A.R.S. 41-1519 investment tier, by county population band.
    big = cand["county_gis"].astype(str).str.upper().isin(["MARICOPA", "PIMA"])
    cand["ars_41_1519_tier"] = np.where(
        big, "$50,000,000 minimum new investment (county pop >800,000)",
        "$25,000,000 minimum new investment (county pop <=800,000)")
    cand["cdc_program_status"] = (
        "CLOSED to new applicants 1 Jul 2026 - 30 Jun 2029 (HB 4168 / SB "
        "1861), renewals included. Do not model the sales-and-use tax "
        "exemption as available.")

    print("\n  in_ama:", cand["in_ama"].value_counts().to_dict())
    print("  AMAs represented:",
          cand["ama_ina_name"].dropna().unique().tolist())
    print("  municipal_water_available:",
          cand["municipal_water_available"].value_counts().to_dict())
    print("  water_risk_score:",
          cand["water_risk_score"].value_counts().sort_index().to_dict())
    print("  size_class:", cand["size_class"].value_counts().to_dict())
    print(f"  est_capacity_mw populated: {cand['est_capacity_mw'].notna().sum()}"
          f" of {len(cand)} (Pop 1 only — see capacity_basis)")

    cand.to_crs(CRS_WGS84).to_file(OUT, layer="candidates_enriched",
                                   driver="GPKG")
    print(f"\n  wrote -> {os.path.basename(OUT)}")


if __name__ == "__main__":
    main()
