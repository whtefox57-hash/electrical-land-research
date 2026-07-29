"""STEP 2 — Arizona land ownership / surface management.

Primary source: BLM Arizona State Office full-resolution Surface Management
Agency polygon layer (17,585 polygons, includes Private). This is preferred
over the BLM national CACHED layer, which generalises Arizona to 102 polygons
and collapses all private land into 2 multipart polygons — useless for site
screening.

Cross-checks acquired independently: ADEQ Land Ownership, BLM national cached
SMA, PAD-US Manager Name, Census TIGERweb AIANNH.

Every acreage is computed in EPSG:5070 (equal-area) and compared against the
source's own read ACRES field. Nothing here is estimated.
"""
from __future__ import annotations

import json
import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AZ_BBOX, CRS_AREA, CRS_WGS84, DATA, M2_PER_ACRE,
                    esri_query_all, get_json, log_status)

SMA_AZ = "https://gis.blm.gov/azarcgis/rest/services/lands/BLM_AZ_SMA/MapServer/0"
SMA_NATL = ("https://gis.blm.gov/arcgis/rest/services/lands/"
            "BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1")
ADEQ_OWN = ("https://services.arcgis.com/SzoH1oFM2apCSkx3/arcgis/rest/"
            "services/Land_Ownership/FeatureServer/0")
PADUS_MGR = ("https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/"
             "services/Manager_Name_PADUS/FeatureServer/0")
TIGER_AIANNH = ("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
                "AIANNHA/MapServer/0")
ASLD_JURIS = ("https://azgeo.az.gov/arcgis/rest/services/asld/"
              "ASLD_AdminBoundaries/MapServer/14")

# BLM AZ SMA CATEGORY -> our eight-class scheme. Read from the source's own
# CATEGORY domain (15 distinct values, enumerated 2026-07-29). No guessing.
CATEGORY_MAP = {
    "Private": "private",
    "State": "state_trust",
    "State Wildlife Area": "state_trust",
    "Indian Lands": "tribal",
    "BLM": "federal_blm",
    "Bankhead-Jones Act": "federal_blm",
    "USFS": "federal_forest",
    "NPS": "federal_other",
    "USFWS": "federal_other",
    "BR": "federal_other",          # Bureau of Reclamation
    "Military": "military",
    "County": "municipal",
    "Local or State Parks": "municipal",
    "Other": "unknown",
    "None": "unknown",
}

# Acquisition path by class. State trust is auction_only, NOT excluded —
# ASLD auctions are a real if slow path (A.R.S. Title 37).
ACQUIRABLE = {
    "private": "yes",
    "state_trust": "auction_only",
    "tribal": "lease_only_bia",
    "federal_blm": "no",
    "federal_forest": "no",
    "federal_other": "no",
    "military": "no",
    "municipal": "no",
    "unknown": "no",
}

# Known statewide breakdown supplied as a validation target. Note the source
# categories summed to 100.7% of Arizona's actual land area.
KNOWN = {
    "tribal": 28.33, "private": 17.01, "federal_blm": 16.64,
    "federal_forest": 15.21, "state_trust": 12.47, "federal_other": 6.35,
    "military": 3.64, "unknown": 0.31, "municipal": 0.03,
}
AZ_LAND_ACRES = 72_964_000  # Arizona total land area, USGS/Census


def fetch(name, url, where="1=1", fields="*", geom=None, page=1000,
          manual=""):
    """Fetch a layer, log the outcome, return a GeoDataFrame or None."""
    try:
        gj = esri_query_all(url, where=where, out_fields=fields,
                            geometry=geom, page=page)
        n = len(gj["features"])
        if n == 0:
            raise RuntimeError("query succeeded but returned 0 features")
        gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        log_status(name, url, True, records=n)
        return gdf
    except Exception as exc:  # noqa: BLE001
        log_status(name, url, False, detail=str(exc), manual_url=manual or url)
        return None


def main():
    print("STEP 2 — LAND OWNERSHIP\n" + "=" * 60)
    os.makedirs(DATA, exist_ok=True)

    # ---------- PRIMARY ----------
    print("\n[primary] BLM Arizona full-resolution SMA")
    sma = fetch("BLM_AZ_SMA_fullres (PRIMARY ownership)", SMA_AZ,
                fields="OBJECTID,OWNER,CATEGORY,DESC_,ADMIN_DEPT_CODE,"
                       "ADMIN_AGENCY_CODE,ADMIN_TYPE,ACRES",
                page=1000)
    if sma is None:
        print("\nFATAL: primary ownership layer unavailable. "
              "Cannot build a private-land universe. Stopping.")
        sys.exit(1)

    sma["land_status"] = sma["CATEGORY"].map(CATEGORY_MAP)
    unmapped = sma[sma["land_status"].isna()]["CATEGORY"].unique().tolist()
    if unmapped:
        print(f"  !! unmapped CATEGORY values: {unmapped} -> 'unknown'")
        sma["land_status"] = sma["land_status"].fillna("unknown")
    sma["acquirable"] = sma["land_status"].map(ACQUIRABLE)

    # Area computed properly in an equal-area CRS, independent of the
    # source ACRES field so the two can be compared.
    sma_ea = sma.to_crs(CRS_AREA)
    sma["acres_computed_equalarea"] = sma_ea.geometry.area / M2_PER_ACRE
    sma["acres_source_field"] = pd.to_numeric(sma["ACRES"], errors="coerce")

    sma.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                layer="sma_az_fullres", driver="GPKG")
    print(f"  saved {len(sma)} polygons -> data/az_ownership.gpkg")

    # ---------- CROSS-CHECKS ----------
    print("\n[cross-check] independent ownership sources")
    checks = {}

    natl = fetch("BLM_Natl_SMA_cached (cross-check, GENERALISED)", SMA_NATL,
                 where="ADMIN_ST='AZ'",
                 fields="OBJECTID,ADMIN_ST,ADMIN_UNIT_NAME,ADMIN_UNIT_TYPE,"
                        "ADMIN_DEPT_CODE,ADMIN_AGENCY_CODE",
                 page=2000)
    if natl is not None:
        natl.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                     layer="blm_natl_sma_cached", driver="GPKG")
        checks["blm_natl_cached"] = natl

    adeq = fetch("ADEQ_Land_Ownership (cross-check)", ADEQ_OWN,
                 fields="OBJECTID,CATEGORY,DESC_", page=1000)
    if adeq is not None:
        adeq.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                     layer="adeq_land_ownership", driver="GPKG")
        checks["adeq"] = adeq

    padus = fetch("PADUS_Manager_Name (cross-check)", PADUS_MGR,
                  where="State_Nm='AZ'",
                  fields="OBJECTID,Mang_Name,Mang_Type,Unit_Nm,State_Nm,"
                         "GIS_Acres,Des_Tp",
                  page=1000)
    if padus is not None:
        padus.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                      layer="padus_manager_name", driver="GPKG")
        checks["padus"] = padus

    aiannh = fetch("Census_TIGERweb_AIANNH (tribal cross-check)",
                   TIGER_AIANNH, geom=AZ_BBOX,
                   fields="OID,NAME,BASENAME,MTFCC,AIANNHCE", page=1000)
    if aiannh is not None:
        aiannh.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                       layer="census_aiannh", driver="GPKG")
        checks["aiannh"] = aiannh

    # ASLD — Arizona State Land Department's own jurisdiction layer.
    asld = fetch("ASLD_Land_Jurisdiction (azgeo.az.gov)", ASLD_JURIS,
                 page=1000,
                 manual="https://azgeo.az.gov/arcgis/rest/services/asld/"
                        "ASLD_AdminBoundaries/MapServer/14")
    if asld is not None:
        asld.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                     layer="asld_land_jurisdiction", driver="GPKG")
        checks["asld"] = asld

    # ---------- BREAKDOWN ----------
    print("\n" + "=" * 60)
    print("ARIZONA LAND OWNERSHIP BREAKDOWN")
    print("=" * 60)
    agg = sma.groupby("land_status").agg(
        acres_computed=("acres_computed_equalarea", "sum"),
        acres_source=("acres_source_field", "sum"),
        n_polygons=("OBJECTID", "count"),
    ).sort_values("acres_computed", ascending=False)
    tot_c = agg["acres_computed"].sum()

    print(f"\n{'class':16s} {'acres(equal-area)':>18s} {'pct':>7s} "
          f"{'acres(src fld)':>15s} {'known%':>7s} {'delta':>7s} {'n':>6s}")
    for cls, row in agg.iterrows():
        pct = row["acres_computed"] / tot_c * 100
        kn = KNOWN.get(cls)
        d = f"{pct - kn:+.2f}" if kn is not None else "n/a"
        print(f"{cls:16s} {row['acres_computed']:18,.0f} {pct:6.2f}% "
              f"{row['acres_source']:15,.0f} "
              f"{(f'{kn:.2f}%' if kn is not None else 'n/a'):>7s} {d:>7s} "
              f"{int(row['n_polygons']):6d}")
    print(f"{'TOTAL':16s} {tot_c:18,.0f} {100.0:6.2f}% "
          f"{agg['acres_source'].sum():15,.0f}")
    print(f"\nArizona actual land area: {AZ_LAND_ACRES:,} acres")
    print(f"This layer totals {tot_c/AZ_LAND_ACRES*100:.2f}% of it "
          f"(reference categories summed to 100.7%).")

    agg.to_csv(os.path.join(DATA, "ownership_breakdown.csv"))

    # ---------- PRIVATE UNIVERSE ----------
    priv = sma[sma["land_status"] == "private"].copy()
    priv.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                 layer="private_land", driver="GPKG")
    print(f"\nPRIVATE LAND UNIVERSE: {len(priv):,} polygons, "
          f"{priv['acres_computed_equalarea'].sum():,.0f} acres "
          f"(equal-area) / {priv['acres_source_field'].sum():,.0f} acres "
          f"(source ACRES field)")

    # ---------- CROSS-CHECK COMPARISON ----------
    print("\n" + "-" * 60)
    print("CROSS-CHECK: independent private/tribal acreage")
    if "adeq" in checks:
        a = checks["adeq"].to_crs(CRS_AREA)
        a["ac"] = a.geometry.area / M2_PER_ACRE
        ap = a[a["CATEGORY"].astype(str).str.contains("Private", case=False,
                                                     na=False)]["ac"].sum()
        print(f"  ADEQ private          : {ap:,.0f} acres "
              f"({len(checks['adeq'])} polys total, generalised)")
    if "aiannh" in checks:
        t = checks["aiannh"].to_crs(CRS_AREA)
        # clip-free gross area; AIANNH extends past the state line
        print(f"  Census AIANNH in bbox : {len(checks['aiannh'])} areas, "
              f"{t.geometry.area.sum()/M2_PER_ACRE:,.0f} acres gross "
              f"(includes out-of-state portions, not clipped)")
    if "padus" in checks:
        p = checks["padus"]
        print(f"  PAD-US AZ features    : {len(p)} "
              f"(protected-areas inventory; does not enumerate private land)")

    summary = {
        "breakdown": {k: {"acres_equalarea": float(v["acres_computed"]),
                          "acres_source_field": float(v["acres_source"]),
                          "pct": float(v["acres_computed"] / tot_c * 100),
                          "n_polygons": int(v["n_polygons"])}
                      for k, v in agg.iterrows()},
        "total_acres_equalarea": float(tot_c),
        "az_land_acres_reference": AZ_LAND_ACRES,
        "private_polygons": int(len(priv)),
        "cross_checks_acquired": sorted(checks.keys()),
    }
    with open(os.path.join(DATA, "step2_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("\nSTEP 2 complete.")


if __name__ == "__main__":
    main()
