"""STEP 2b — retry the three cross-checks that failed on first attempt.

Diagnosed causes, all fixed here rather than recorded as dead:
  BLM national cached SMA : 500 when serving geometry at page>=100. The AZ
                            polygons are enormous multipart geometries. Page 50
                            works.
  Census AIANNH           : layer 0 is Alaska Native Regional Corporations.
                            Federal American Indian Reservations is layer 2,
                            Off-Reservation Trust Lands is layer 3.
  ASLD Public Land Ownership : service rejects resultOffset entirely
                            ("Pagination is not supported"). Only 108 features,
                            so one unpaged request returns everything.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AZ_BBOX, CRS_AREA, CRS_WGS84, DATA, M2_PER_ACRE,
                    esri_query_all, get_json, log_status)

GPKG = os.path.join(DATA, "az_ownership.gpkg")


def save(gdf, layer):
    gdf.to_file(GPKG, layer=layer, driver="GPKG")


def unpaged(url, where="1=1", fields="*", geom=None):
    """Single request, no resultOffset — for services rejecting pagination."""
    params = {"where": where, "outFields": fields, "returnGeometry": "true",
              "outSR": 4326, "f": "geojson"}
    if geom:
        params.update({"geometry": ",".join(str(c) for c in geom),
                       "geometryType": "esriGeometryEnvelope", "inSR": 4326,
                       "spatialRel": "esriSpatialRelIntersects"})
    js = get_json(url.rstrip("/") + "/query", params=params, timeout=300)
    if "error" in js:
        raise RuntimeError(f"ArcGIS error: {js['error']}")
    return js


def main():
    print("STEP 2b — cross-check retries\n" + "=" * 60)

    # --- 1. BLM national cached SMA, page 50 ---
    url = ("https://gis.blm.gov/arcgis/rest/services/lands/"
           "BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1")
    try:
        gj = esri_query_all(url, where="ADMIN_ST='AZ'",
                            out_fields="OBJECTID,ADMIN_ST,ADMIN_UNIT_NAME,"
                                       "ADMIN_UNIT_TYPE,ADMIN_DEPT_CODE,"
                                       "ADMIN_AGENCY_CODE",
                            page=50, timeout=300)
        g = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        save(g, "blm_natl_sma_cached")
        log_status("BLM_Natl_SMA_cached (cross-check, GENERALISED) [retry "
                   "page=50]", url, True, records=len(g))
        ea = g.to_crs(CRS_AREA)
        g["ac"] = ea.geometry.area / M2_PER_ACRE
        print("\n  BLM national cached, AZ, by agency code:")
        for k, v in g.groupby("ADMIN_AGENCY_CODE")["ac"].sum(
                ).sort_values(ascending=False).items():
            print(f"    {str(k):10s} {v:14,.0f} ac")
        print(f"    {'TOTAL':10s} {g['ac'].sum():14,.0f} ac  "
              f"({len(g)} polygons)")
    except Exception as exc:  # noqa: BLE001
        log_status("BLM_Natl_SMA_cached (cross-check) [retry page=50]", url,
                   False, detail=str(exc))

    # --- 2. Census AIANNH, correct layer indices ---
    base = ("https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/"
            "AIANNHA/MapServer")
    parts = []
    for lid, label in [(2, "Federal American Indian Reservations"),
                       (3, "Off-Reservation Trust Lands")]:
        u = f"{base}/{lid}"
        try:
            gj = esri_query_all(u, out_fields="OID,NAME,BASENAME,MTFCC",
                                geometry=AZ_BBOX, page=500)
            g = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
            g["aiannh_layer"] = label
            parts.append(g)
            log_status(f"Census_TIGERweb_AIANNH L{lid} ({label})", u, True,
                       records=len(g))
        except Exception as exc:  # noqa: BLE001
            log_status(f"Census_TIGERweb_AIANNH L{lid} ({label})", u, False,
                       detail=str(exc))
    if parts:
        aia = gpd.GeoDataFrame(pd.concat(parts, ignore_index=True),
                               crs=CRS_WGS84)
        save(aia, "census_aiannh")
        print(f"\n  Census AIANNH intersecting AZ bbox: {len(aia)} areas")
        for n in sorted(aia["NAME"].astype(str))[:40]:
            print(f"    {n}")

    # --- 3. ASLD Public Land Ownership, unpaged ---
    u = ("https://azgeo.az.gov/arcgis/rest/services/asld/"
         "ASLD_AdminBoundaries/MapServer/14")
    try:
        gj = unpaged(u, fields="FID,OWNER,CATEGORY,DESC_,Area_Acres,MANAGER,"
                               "EDIT_DATE")
        g = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        save(g, "asld_public_land_ownership")
        log_status("ASLD_Public_Land_Ownership (azgeo.az.gov) [retry unpaged]",
                   u, True, records=len(g))
        ea = g.to_crs(CRS_AREA)
        g["ac"] = ea.geometry.area / M2_PER_ACRE
        print("\n  ASLD Public Land Ownership (state's own layer, "
              f"{len(g)} generalised polygons):")
        agg = g.groupby("CATEGORY").agg(ac=("ac", "sum"),
                                        src=("Area_Acres", "sum"),
                                        n=("FID", "count"))
        for k, r in agg.sort_values("ac", ascending=False).iterrows():
            print(f"    {str(k):24s} {r['ac']:14,.0f} ac  "
                  f"(src field {r['src']:14,.0f})  n={int(r['n'])}")
    except Exception as exc:  # noqa: BLE001
        log_status("ASLD_Public_Land_Ownership (azgeo.az.gov) [retry unpaged]",
                   u, False, detail=str(exc))

    print("\nSTEP 2b complete.")


if __name__ == "__main__":
    main()
