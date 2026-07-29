"""STEP 4 — water, as a first-class layer.

Source: Arizona Department of Water Resources' own ArcGIS org
(services.arcgis.com/C34zQ7veRS0V1t04), plus USGS NHD for Arizona.

Layers acquired:
  AMA_and_INA           8 AMAs + 3 INAs. The brief listed Phoenix, Pinal,
                        Tucson, Prescott, Santa Cruz and asked me to check for
                        Willcox. Willcox IS present, and so are DOUGLAS and
                        RANEGRAS PLAIN — three AMAs beyond the brief's list.
  Groundwater_Basin     52 basins
  Groundwater_Subbasin  sub-basins
  CWS Service Area      750 community water systems -> municipal_water_available
  AAWS determinations   5,596 Assured Water Supply issued determinations
  Well Registry         240k registered wells
  NHD perennial         nearest_surface_water_km

On surface water: Arizona's NHD has 1,015,756 flowlines, of which 627,761 are
EPHEMERAL and 261,454 INTERMITTENT. Only 18,992 (1.9%) are perennial. Distance
to "nearest NHD flowline" is therefore close to meaningless here — it would
usually be measuring a dry wash. This screen uses PERENNIAL ONLY (FCode 46006)
and says so on every derived field.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AZ_BBOX, CRS_WGS84, DATA, esri_query_all, log_status)

GPKG = os.path.join(DATA, "az_water.gpkg")
ADWR = "https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services"
NHD = ("https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/"
       "NHD_H_Arizona_State_GDB/FeatureServer")

LAYERS = [
    ("ama_ina", f"{ADWR}/AMA_INA_2024/FeatureServer/0",
     "OBJECTID,BASIN_NAME,NAME_ABBR,BASIN_NAME_GWSI", "1=1", 2000),
    ("groundwater_basin", f"{ADWR}/Groundwater_Basin_2024/FeatureServer/0",
     "OBJECTID,BASIN_NAME,NAME_ABBR,BASIN_NAME_GWSI", "1=1", 2000),
    ("groundwater_subbasin", f"{ADWR}/Groundwater_Subbasin/FeatureServer/0",
     "*", "1=1", 2000),
    ("cws_service_area", f"{ADWR}/CWS_2024/FeatureServer/0",
     "OBJECTID,ADEQ_ID,CWS_NAME,STATUS,AMA,OWNER_NAME,COUNTY,POPULATION,"
     "CITY_SRVD,RIGHT_TYPE", "1=1", 1000),
    ("aaws_determinations",
     f"{ADWR}/AAWS_Issued_Determination_2024/FeatureServer/0",
     "OBJECTID,SUBDIVISION,FILE_NO,FILE_TYPE,WATER_PROVIDER,SYSTEM_NAME,"
     "ISSUED_DT,TOTAL_DEMAND,GW,EFFLUENT,SW,CAP,COLORADO_RIVER,COUNTY",
     "1=1", 1000),
    ("counties", f"{ADWR}/County_2024/FeatureServer/3",
     "OBJECTID,NAME,CODE,AREA_ACRES", "1=1", 2000),
    ("city_boundaries", f"{ADWR}/City_Boundaries_2024/FeatureServer/0",
     "OBJECTID,NAME,INC,POP", "1=1", 2000),
]


def fetch(layer, name, url, fields, where, page, **kw):
    try:
        gj = esri_query_all(url, where=where, out_fields=fields, page=page,
                            **kw)
        n = len(gj["features"])
        if n == 0:
            raise RuntimeError("query returned 0 features")
        g = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        g.to_file(GPKG, layer=layer, driver="GPKG")
        log_status(name, url, True, records=n, key=layer)
        return g
    except Exception as exc:  # noqa: BLE001
        log_status(name, url, False, detail=str(exc), key=layer)
        return None


def main():
    print("STEP 4 — WATER\n" + "=" * 60)

    for layer, url, fields, where, page in LAYERS:
        g = fetch(layer, f"ADWR {layer}", url, fields, where, page)
        if g is not None and layer == "ama_ina":
            print("    AMAs and INAs found:")
            for n in sorted(g["BASIN_NAME"].astype(str)):
                print(f"      {n}")

    # --- NHD perennial flowlines -----------------------------------------
    print("\n  NHD perennial flowlines (FCode 46006) — perennial ONLY, "
          "because 62% of Arizona NHD is ephemeral wash")
    fetch("nhd_perennial", "USGS NHD Arizona perennial flowlines (FCode 46006)",
          f"{NHD}/11", "OBJECTID,GNIS_Name,LengthKM,FType,FCode,ReachCode",
          "FCode=46006", 1000)

    # --- NHD waterbodies (lakes/reservoirs) ------------------------------
    fetch("nhd_waterbody", "USGS NHD Arizona waterbodies",
          f"{NHD}/16", "OBJECTID,GNIS_Name,FType,FCode,AreaSqKm",
          "FCode IN (39004,39009,39010,43601,43617)", 1000)

    # --- Well registry ----------------------------------------------------
    print("\n  ADWR Well Registry (240k records — minimal field set)")
    fetch("well_registry", "ADWR Well Registry 2024",
          f"{ADWR}/Well_Registry_2024/FeatureServer/0",
          "OBJECTID,REGISTRY_ID,WELLTYPE,WELL_TYPE_GROUP,WELL_DEPTH,"
          "WATER_LEVEL,PUMPRATE,INSTALLED",
          "1=1", 2000)

    print("\nSTEP 4 acquisition complete.")
    import fiona
    print("  layers in az_water.gpkg:", fiona.listlayers(GPKG))


if __name__ == "__main__":
    main()
