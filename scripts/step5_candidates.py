"""STEP 5 — build candidate sites.

Two populations, deduplicated:
  Pop 1  plants with retired or announced-retirement capacity >= 50 MW
  Pop 2  substations with max voltage >= 115 kV, not within 2 km of a Pop 1 site

Land status is assigned by point-in-polygon against the Step 2 ownership
layer. PRIVATE LAND ONLY forms the working universe, but every non-private
candidate is retained in a separate table so the user can see what is being
excluded and why.

All distances in EPSG:26912 (metres), validated Phoenix->Tucson 170.45 km.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_DIST, CRS_WGS84, DATA, M2_PER_ACRE

OWN = os.path.join(DATA, "az_ownership.gpkg")
POW = os.path.join(DATA, "az_power.gpkg")
WAT = os.path.join(DATA, "az_water.gpkg")
OUT = os.path.join(DATA, "az_candidates_raw.gpkg")

POP1_MIN_MW = 50.0
POP2_MIN_KV = 115.0
DEDUP_M = 2000.0

# Size buckets, taken verbatim from outputs/AZ_SIZE_THRESHOLDS.md.
SIZE_BUCKETS = [
    (0, 5, "sub_tariff", "below APS XHLF floor"),
    (5, 20, "xhlf_eligible", "APS XHLF (if >=92% load factor)"),
    (20, 100, "srp_minimum_bill",
     "SRP E-67 minimum billing; Tucson draft threshold if adopted"),
    (100, 286, "large_load", "bespoke utility negotiation territory"),
    (286, 1e9, "project_blue_scale",
     "at/above the only ACC-approved AZ special contract to date (286 MW)"),
]


def size_class(mw):
    if pd.isna(mw):
        return None, None
    for lo, hi, name, trig in SIZE_BUCKETS:
        if lo <= mw < hi:
            return name, trig
    return None, None


# Federal power marketers and BIA projects. These appear as retail service
# territory polygons covering enormous areas, but WAPA is a federal WHOLESALE
# marketer — it is not who a data center developer buys retail load from.
# Letting them win an overlap wrongly labelled 57 candidates "federal".
FEDERAL_OVERLAY = ("WAPA", "WESTERN AREA POWER", "USBIA", "BUREAU OF INDIAN")

# Tribal utility authorities. Retained and labelled, not silently bucketed.
TRIBAL_UTIL = ("NAVAJO TRIBAL UTILITY", "TOHONO O'ODHAM UTILITY",
               "AHA MACAV", "GILA RIVER INDIAN UTILITY", "AK-CHIN ELECTRIC",
               "COLORADO RIVER INDIAN")


def classify_utility(name, typ):
    """Return (utility_type, detail, basis).

    utility_type uses the brief's enum. `basis` distinguishes a value READ
    from HIFLD's TYPE field from one INFERRED from the utility's name, which
    is necessary wherever HIFLD carries TYPE='NOT AVAILABLE'.
    """
    n = str(name or "").upper()
    t = str(typ or "").upper()

    # SRP is the single most important special case in Arizona: public power,
    # NOT ACC-regulated, board elected by landowners on an acreage franchise.
    if "SALT RIVER PROJECT" in n:
        return ("SRP_public",
                "Salt River Project — public power, NOT ACC-regulated; board "
                "elected by landowners on an acreage franchise. No ACC docket "
                "to intervene in.", "READ (name)")
    if any(k in n for k in TRIBAL_UTIL):
        return ("tribal_utility",
                "Tribal utility authority — service on tribal land, BIA "
                "jurisdiction.", "READ (name)")
    if any(k in n for k in FEDERAL_OVERLAY):
        return ("federal_wholesale_overlay",
                "Federal power marketer / BIA project. Not a retail supplier "
                "for a large load.", "READ (name)")

    if "INVESTOR OWNED" in t:
        return ("IOU_ACC_regulated",
                "Investor-owned utility, rates set by the Arizona Corporation "
                "Commission (five elected members).", "READ (HIFLD TYPE)")
    if "COOPERATIVE" in t:
        return ("coop", "Electric cooperative.", "READ (HIFLD TYPE)")
    if "MUNICIPAL" in t:
        return ("municipal", "Municipal electric utility.", "READ (HIFLD TYPE)")
    if "POLITICAL SUBDIVISION" in t:
        return ("municipal",
                "Arizona electrical/power district — a political subdivision, "
                "public power, not ACC rate-regulated.",
                "READ (HIFLD TYPE)")

    # HIFLD TYPE is 'NOT AVAILABLE' for many Arizona entities. Infer from the
    # name and say so.
    if "COOP" in n or "ELECTRIC ASSN" in n or " E C " in f" {n} ":
        return ("coop", "Electric cooperative.", "INFERRED (from name)")
    if n.startswith("CITY OF") or n.startswith("TOWN OF"):
        return ("municipal", "Municipal electric utility.",
                "INFERRED (from name)")
    if any(k in n for k in ("ELECTRICAL DIST", "POWER DISTRICT",
                            "IRRIGATION DISTRICT", "IRR & DRAIN",
                            "WATER C&D", "CONSERV. DIST", "M W C DIST",
                            "IRR PROJ", "UTILITY ENTERPRISES")):
        return ("municipal",
                "Arizona district / political subdivision — public power, not "
                "ACC rate-regulated.", "INFERRED (from name)")
    return ("UNKNOWN", "Serving utility not classifiable from HIFLD TYPE or "
                       "name — phone call required.", "UNKNOWN")


def nearest(pts, targets, valcols=()):
    """Nearest target to each point. Returns distance in metres + columns."""
    if targets.empty:
        out = pd.DataFrame(index=pts.index)
        out["dist_m"] = np.nan
        for c in valcols:
            out[c] = np.nan
        return out
    j = gpd.sjoin_nearest(pts[["geometry"]], targets, how="left",
                          distance_col="dist_m")
    j = j[~j.index.duplicated(keep="first")].reindex(pts.index)
    keep = ["dist_m"] + [c for c in valcols if c in j.columns]
    return j[keep]


def count_within(pts, targets, radius, valcol=None):
    """Count targets within radius; optionally max of a value column."""
    if targets.empty:
        return pd.Series(0, index=pts.index), pd.Series(np.nan, index=pts.index)
    buf = pts[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(radius)
    cols = ["geometry"] + ([valcol] if valcol and valcol in targets else [])
    j = gpd.sjoin(buf, targets[cols], predicate="intersects", how="left")
    cnt = j.groupby(level=0).size()
    # sjoin with no match still yields one row with NaN index_right
    nomatch = j["index_right"].isna().groupby(level=0).all()
    cnt[nomatch[nomatch].index] = 0
    mx = (j.groupby(level=0)[valcol].max() if valcol and valcol in targets
          else pd.Series(np.nan, index=pts.index))
    return (cnt.reindex(pts.index).fillna(0).astype(int),
            mx.reindex(pts.index))


def main():
    print("STEP 5 — CANDIDATE SITES\n" + "=" * 60)

    own = gpd.read_file(OWN, layer="sma_az_fullres").to_crs(CRS_DIST)
    subs = gpd.read_file(POW, layer="substations").to_crs(CRS_DIST)
    lines = gpd.read_file(POW, layer="transmission_lines").to_crs(CRS_DIST)
    plants = gpd.read_file(POW, layer="retired_plants").to_crs(CRS_DIST)
    terr = gpd.read_file(POW, layer="utility_territories").to_crs(CRS_DIST)
    counties = gpd.read_file(WAT, layer="counties").to_crs(CRS_DIST)
    cities = gpd.read_file(WAT, layer="city_boundaries").to_crs(CRS_DIST)
    print(f"  ownership={len(own):,} subs={len(subs)} lines={len(lines)} "
          f"plants={len(plants)} territories={len(terr)}")

    # ---------------- Pop 1 ----------------
    pop1 = plants[plants["retired_mw"] >= POP1_MIN_MW].copy()
    pop1["cand_type"] = "pop1_retired_plant"
    pop1["cand_name"] = pop1["Plant Name"]
    pop1["retired_mw_on_site"] = pop1["retired_mw"]
    print(f"\n  Pop 1 (retired/announced >= {POP1_MIN_MW:.0f} MW): {len(pop1)}")
    for _, r in pop1.iterrows():
        print(f"    {str(r['Plant Name'])[:34]:34s} {r['retired_mw']:9,.1f} MW "
              f"{str(r['county'])[:12]:12s} {r['retire_types']}")

    # ---------------- Pop 2 ----------------
    hv = subs[subs["max_volt_kv"] >= POP2_MIN_KV].copy()
    print(f"\n  substations >= {POP2_MIN_KV:.0f} kV: {len(hv)}")
    if not pop1.empty:
        near1 = gpd.sjoin_nearest(hv[["geometry"]], pop1[["geometry"]],
                                  how="left", distance_col="d")
        near1 = near1[~near1.index.duplicated(keep="first")]
        hv["dist_to_pop1_m"] = near1["d"]
        pop2 = hv[hv["dist_to_pop1_m"] >= DEDUP_M].copy()
        dropped = len(hv) - len(pop2)
    else:
        pop2 = hv.copy()
        dropped = 0
    pop2["cand_type"] = "pop2_hv_substation"
    pop2["cand_name"] = pop2["NAME"]
    pop2["retired_mw_on_site"] = 0.0
    print(f"  Pop 2 after dropping {dropped} within {DEDUP_M:.0f} m of a "
          f"Pop 1 site: {len(pop2)}")

    # ---------------- combine ----------------
    keep1 = ["geometry", "cand_type", "cand_name", "retired_mw_on_site",
             "county", "latitude", "longitude", "last_retire_year",
             "first_retire_year", "retire_types", "technologies", "fuels",
             "utility_name", "ba_code", "n_units", "Plant Code"]
    keep2 = ["geometry", "cand_type", "cand_name", "retired_mw_on_site",
             "NAME", "COUNTY", "max_volt_kv", "min_volt_kv", "lines_count",
             "STATUS", "max_volt_provenance", "min_volt_provenance", "ID"]
    a = pop1[[c for c in keep1 if c in pop1.columns]].copy()
    b = pop2[[c for c in keep2 if c in pop2.columns]].copy()
    b = b.rename(columns={"COUNTY": "county", "max_volt_kv": "site_sub_kv",
                          "ID": "hifld_id"})
    cand = gpd.GeoDataFrame(pd.concat([a, b], ignore_index=True),
                            geometry="geometry", crs=CRS_DIST)
    cand["cand_id"] = [f"AZ{i:04d}" for i in range(1, len(cand) + 1)]
    print(f"\n  combined candidates: {len(cand)}")

    # ---------------- land status ----------------
    own_small = own[["geometry", "land_status", "acquirable", "CATEGORY",
                     "acres_computed_equalarea"]]
    j = gpd.sjoin(cand[["geometry", "cand_id"]], own_small,
                  predicate="within", how="left")
    j = j[~j.index.duplicated(keep="first")].reindex(cand.index)
    cand["land_status"] = j["land_status"]
    cand["acquirable"] = j["acquirable"]
    cand["parcel_acres"] = j["acres_computed_equalarea"]

    # Points falling in no polygon (slivers//state line) -> nearest polygon.
    miss = cand["land_status"].isna()
    if miss.any():
        nj = gpd.sjoin_nearest(cand.loc[miss, ["geometry"]], own_small,
                               how="left", distance_col="d")
        nj = nj[~nj.index.duplicated(keep="first")].reindex(
            cand.index[miss])
        cand.loc[miss, "land_status"] = nj["land_status"]
        cand.loc[miss, "acquirable"] = nj["acquirable"]
        cand.loc[miss, "parcel_acres"] = nj["acres_computed_equalarea"]
        cand.loc[miss, "land_status_note"] = (
            "INFERRED — point fell outside all ownership polygons; assigned "
            "from nearest polygon")
        print(f"  {miss.sum()} candidates fell outside all ownership polygons "
              f"-> nearest-polygon assignment, flagged INFERRED")
    cand["land_status_note"] = cand.get("land_status_note",
                                        pd.Series(index=cand.index,
                                                  dtype=object)).fillna(
        "READ — point-in-polygon against BLM AZ full-res SMA")

    print("\n  land_status of all candidates:")
    for k, v in cand["land_status"].value_counts().items():
        print(f"    {k:16s} {v:5d}")

    # ---------------- adjacency ----------------
    st = own[own["land_status"] == "state_trust"][["geometry"]]
    tb = own[own["land_status"] == "tribal"][["geometry"]]
    probe = cand[["geometry"]].copy()
    probe["geometry"] = probe.geometry.buffer(1609.34)  # 1 mile
    s_idx = set(gpd.sjoin(probe, st, predicate="intersects",
                          how="inner").index)
    t_idx = set(gpd.sjoin(probe, tb, predicate="intersects",
                          how="inner").index)
    cand["adjacency_note"] = [
        "; ".join(filter(None, [
            "state_trust within 1 mi (ASLD auction expansion path)"
            if i in s_idx else "",
            "tribal land within 1 mi (BIA jurisdiction; consultation)"
            if i in t_idx else ""])) or "no state_trust/tribal within 1 mi"
        for i in cand.index]

    # ---------------- power metrics ----------------
    print("\n  computing power proximity metrics...")
    ns = nearest(cand, subs[["geometry", "max_volt_kv", "NAME", "STATUS"]],
                 ("max_volt_kv", "NAME", "STATUS"))
    cand["dist_nearest_substation_km"] = ns["dist_m"] / 1000
    cand["nearest_substation_kv"] = ns["max_volt_kv"]
    cand["nearest_substation_name"] = ns["NAME"]
    cand["nearest_substation_status"] = ns["STATUS"]

    c5, mx5 = count_within(cand, subs, 5000, "max_volt_kv")
    cand["substations_within_5km"] = c5
    cand["max_kv_within_5km"] = mx5

    nl = nearest(cand, lines[["geometry", "voltage_kv", "OWNER", "VOLT_CLASS"]],
                 ("voltage_kv", "OWNER", "VOLT_CLASS"))
    cand["dist_nearest_transmission_km"] = nl["dist_m"] / 1000
    cand["nearest_transmission_kv"] = nl["voltage_kv"]
    cand["nearest_transmission_owner"] = nl["OWNER"]

    for lo, hi, lab in [(0, 100, "lt100kv"), (100, 230, "100_229kv"),
                        (230, 345, "230_344kv"), (345, 1e6, "gte345kv")]:
        sel = lines[(lines["voltage_kv"] >= lo) & (lines["voltage_kv"] < hi)]
        c, _ = count_within(cand, sel, 5000)
        cand[f"tx_lines_within_5km_{lab}"] = c
    c_any, _ = count_within(cand, lines, 5000)
    cand["tx_lines_within_5km_total"] = c_any

    # ---------------- interconnection age ----------------
    CURRENT_YEAR = 2026
    cand["years_since_retirement"] = np.where(
        cand["last_retire_year"].notna()
        & (cand["last_retire_year"] <= CURRENT_YEAR),
        CURRENT_YEAR - cand["last_retire_year"], np.nan)
    cand["interconnection_rights_flag"] = np.where(
        cand["years_since_retirement"] > 10,
        "STALE >10yr — interconnection rights may have lapsed",
        np.where(cand["years_since_retirement"].notna(),
                 "recent retirement — rights more likely intact",
                 "n/a — no retirement on site"))

    # ---------------- county / municipality ----------------
    cj = gpd.sjoin(cand[["geometry"]], counties[["geometry", "NAME"]],
                   predicate="within", how="left")
    cj = cj[~cj.index.duplicated(keep="first")].reindex(cand.index)
    cand["county_gis"] = cj["NAME"]
    mj = gpd.sjoin(cand[["geometry"]], cities[["geometry", "NAME", "INC"]],
                   predicate="within", how="left")
    mj = mj[~mj.index.duplicated(keep="first")].reindex(cand.index)
    cand["municipality"] = mj["NAME"]
    cand["jurisdiction"] = np.where(cand["municipality"].notna(),
                                    cand["municipality"],
                                    "UNINCORPORATED " +
                                    cand["county_gis"].astype(str) + " COUNTY")

    # ---------------- serving utility ----------------
    terr = terr.copy()
    terr["terr_area_km2"] = terr.geometry.area / 1e6
    terr["is_overlay"] = terr["NAME"].astype(str).str.upper().apply(
        lambda n: any(k in n for k in FEDERAL_OVERLAY))
    tj = gpd.sjoin(cand[["geometry"]],
                   terr[["geometry", "NAME", "TYPE", "REGULATED", "HOLDING_CO",
                         "WEBSITE", "TELEPHONE", "CNTRL_AREA", "terr_area_km2",
                         "is_overlay"]],
                   predicate="within", how="left")

    # Overlap resolution. A point commonly falls inside several territory
    # polygons. Alphabetical collapse is arbitrary and made APS beat SRP
    # every time. Instead: drop federal wholesale overlays (WAPA/USBIA)
    # unless nothing else covers the point, then take the SMALLEST polygon,
    # which is the most specific retail territory.
    tj["_rank"] = tj["is_overlay"].fillna(True).astype(int)
    tj = tj.sort_values(["_rank", "terr_area_km2"])
    # REINDEX, never .values — tj has been sorted, so its row order no longer
    # matches cand's. Assigning .values here silently scrambled every
    # candidate's utility (it labelled Navajo, Cholla and Springerville all
    # as Tucson Electric Power).
    tj_first = tj[~tj.index.duplicated(keep="first")].reindex(cand.index)

    cand["serving_utility"] = tj_first["NAME"]
    cand["utility_hifld_type"] = tj_first["TYPE"]
    cand["utility_regulated_field"] = tj_first["REGULATED"]
    cand["utility_website"] = tj_first["WEBSITE"]
    cand["utility_phone"] = tj_first["TELEPHONE"]
    cls = [classify_utility(n, t) for n, t in
           zip(tj_first["NAME"], tj_first["TYPE"])]
    cand["utility_type"] = [c[0] for c in cls]
    cand["utility_type_detail"] = [c[1] for c in cls]
    cand["utility_type_basis"] = [c[2] for c in cls]

    # HIFLD retail territories overlap heavily in Arizona: a point routinely
    # sits inside a major IOU polygon AND several irrigation/water/electrical
    # district polygons. Which one actually serves a given parcel is not
    # resolvable from this dataset, so the ambiguity is reported rather than
    # hidden behind a single confident answer.
    # fillna on a bool column yields object dtype; cast before inverting or
    # `~` produces labels rather than a boolean mask.
    is_ov = tj["is_overlay"].fillna(True).astype(bool)
    n_overlap = tj.loc[~is_ov].groupby(level=0).size()
    cand["n_retail_territories_overlapping"] = (
        n_overlap.reindex(cand.index).fillna(0).astype(int))
    cand["utility_assignment_confidence"] = np.where(
        cand["n_retail_territories_overlapping"] <= 1, "single territory",
        "AMBIGUOUS — multiple overlapping retail territories; confirm the "
        "serving utility by phone before relying on this")

    allu = tj.groupby(level=0)["NAME"].apply(
        lambda s: "; ".join(sorted({str(x) for x in s if pd.notna(x)})))
    cand["all_overlapping_utilities"] = allu.reindex(cand.index).fillna("")

    print("\n  serving utility (most specific retail territory):")
    for k, v in cand["serving_utility"].value_counts().head(15).items():
        print(f"    {str(k)[:44]:46s} {v:5d}")
    print("\n  utility_type:")
    for k, v in cand["utility_type"].value_counts().items():
        print(f"    {k:28s} {v:5d}")
    print("  utility_type_basis:")
    for k, v in cand["utility_type_basis"].value_counts().items():
        print(f"    {str(k):28s} {v:5d}")

    cand = cand.to_crs(CRS_WGS84)
    cand["lon"] = cand.geometry.x
    cand["lat"] = cand.geometry.y
    cand.to_file(OUT, layer="candidates_all", driver="GPKG")
    print(f"\n  wrote {len(cand)} candidates -> {os.path.basename(OUT)}")
    print(f"  PRIVATE: {(cand['land_status'] == 'private').sum()}  "
          f"non-private retained separately: "
          f"{(cand['land_status'] != 'private').sum()}")
    print("\nSTEP 5 (geometry/power) complete.")


if __name__ == "__main__":
    main()
