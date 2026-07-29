"""STEP 2c — BLM national cached SMA via OBJECTID batching.

The service 500s on any request using resultOffset>0 with geometry. Working
around it by asking for the AZ OBJECTID list first, then fetching in batches
of 20 explicit objectIds. All 102 AZ polygons retrieve this way.

This layer is the GENERALISED national cache: 102 polygons for the whole
state, private land collapsed to a handful of multipart features. It is used
here ONLY as a statewide census cross-check, never for site screening.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_AREA, CRS_WGS84, DATA, M2_PER_ACRE, get_json, log_status

URL = ("https://gis.blm.gov/arcgis/rest/services/lands/"
       "BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1")

# BLM national agency codes -> our scheme.
AGENCY_MAP = {
    "PVT": "private", "ST": "state_trust", "BIA": "tribal", "BLM": "federal_blm",
    "USFS": "federal_forest", "NPS": "federal_other", "FWS": "federal_other",
    "USBR": "federal_other", "DOD": "military", "ARMY": "military",
    "NAVY": "military", "USAF": "military", "USACE": "military",
    "LG": "municipal", "OTHFE": "federal_other", "UND": "unknown",
}


def main():
    print("STEP 2c — BLM national cached SMA (objectId batching)")
    try:
        ids = get_json(URL + "/query",
                       params={"where": "ADMIN_ST='AZ'", "returnIdsOnly": "true",
                               "f": "json"}, timeout=120).get("objectIds") or []
        if not ids:
            raise RuntimeError("returnIdsOnly gave no objectIds for ADMIN_ST='AZ'")
        feats = []
        for i in range(0, len(ids), 20):
            batch = ids[i:i + 20]
            js = get_json(URL + "/query", timeout=300, params={
                "objectIds": ",".join(map(str, batch)),
                "outFields": "OBJECTID,ADMIN_ST,ADMIN_UNIT_NAME,"
                             "ADMIN_UNIT_TYPE,ADMIN_DEPT_CODE,ADMIN_AGENCY_CODE",
                "returnGeometry": "true", "outSR": 4326, "f": "geojson"})
            if "error" in js:
                raise RuntimeError(f"ArcGIS error on batch {i}: {js['error']}")
            feats.extend(js.get("features", []))
        g = gpd.GeoDataFrame.from_features(feats, crs=CRS_WGS84)
        g["land_status"] = g["ADMIN_AGENCY_CODE"].map(AGENCY_MAP).fillna("unknown")
        g.to_file(os.path.join(DATA, "az_ownership.gpkg"),
                  layer="blm_natl_sma_cached", driver="GPKG")
        log_status("BLM_Natl_SMA_cached (cross-check, GENERALISED) "
                   "[objectId batching]", URL, True, records=len(g))

        ea = g.to_crs(CRS_AREA)
        g["ac"] = ea.geometry.area / M2_PER_ACRE
        agg = g.groupby("land_status")["ac"].sum().sort_values(ascending=False)
        tot = agg.sum()
        print(f"\n  {len(g)} polygons, {tot:,.0f} acres total")
        print(f"  {'class':16s} {'acres':>14s} {'pct':>7s}")
        for k, v in agg.items():
            print(f"  {k:16s} {v:14,.0f} {v/tot*100:6.2f}%")
        pd.DataFrame({"acres": agg, "pct": agg / tot * 100}).to_csv(
            os.path.join(DATA, "blm_natl_cached_breakdown.csv"))
    except Exception as exc:  # noqa: BLE001
        log_status("BLM_Natl_SMA_cached (cross-check) [objectId batching]",
                   URL, False, detail=str(exc))


if __name__ == "__main__":
    main()
