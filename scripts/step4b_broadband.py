"""Broadband proxy — FCC Broadband Data Collection, block-group level.

IMPORTANT, and repeated on every output that uses it: this is a PROXY.
`UniqueProviders` counts fixed broadband providers reporting SERVICE
AVAILABILITY to residential/small-business locations in a census block group.
It is NOT a map of fiber routes, and it says nothing about whether a
carrier-class fiber path reaches a specific parcel or what it would cost to
extend one. It is the weakest signal in the whole screen, which is why it
carries only 5 of the 100 points.

The FCC's own BDC download API requires registered credentials (returns 401
unauthenticated), so this uses the public Living Atlas republication of the
same BDC release.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_WGS84, DATA, esri_query_all, log_status

GPKG = os.path.join(DATA, "az_water.gpkg")
BDC = ("https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/"
       "FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/3")


def main():
    print("Broadband proxy — FCC BDC block groups")
    try:
        gj = esri_query_all(
            BDC, where="StateAbbr='AZ'",
            out_fields="OBJECTID,GEOID,CountyName,StateAbbr,TotalPop,"
                       "TotalBSLs,UniqueProviders,UniqueProvidersFiber,"
                       "UniqueProvidersCable,ServedBSLs",
            page=1000)
        g = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        if g.empty:
            raise RuntimeError("0 AZ block groups returned")
        g.to_file(GPKG, layer="fcc_broadband_blockgroups", driver="GPKG")
        log_status("FCC Broadband Data Collection Dec-2024, AZ block groups "
                   "(PROXY for fiber, not routes)", BDC, True, records=len(g),
                   key="fcc_bdc")
        print(f"  {len(g)} AZ block groups")
        print(f"  UniqueProviders      median={g['UniqueProviders'].median()}, "
              f"range {g['UniqueProviders'].min()}-{g['UniqueProviders'].max()}")
        print(f"  UniqueProvidersFiber median="
              f"{g['UniqueProvidersFiber'].median()}, "
              f"range {g['UniqueProvidersFiber'].min()}-"
              f"{g['UniqueProvidersFiber'].max()}")
    except Exception as exc:  # noqa: BLE001
        log_status("FCC Broadband Data Collection (AZ block groups)", BDC,
                   False, detail=str(exc),
                   manual_url="https://broadbandmap.fcc.gov/data-download "
                              "(FCC BDC API requires registered credentials; "
                              "returns 401 unauthenticated)",
                   key="fcc_bdc")


if __name__ == "__main__":
    main()
