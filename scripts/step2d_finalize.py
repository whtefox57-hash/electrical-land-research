"""STEP 2d — finalise the ownership universe.

Computes the adjacency_note flag: does a private polygon abut state trust or
tribal land? That matters both for expansion potential and for opposition.

Adjacency is tested in EPSG:26912 with a 50 m tolerance, which absorbs
digitising slop between polygons that are genuinely coincident on the ground.
"""
from __future__ import annotations

import json
import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_AREA, CRS_DIST, DATA, M2_PER_ACRE, OUTPUTS

GPKG = os.path.join(DATA, "az_ownership.gpkg")
TOUCH_TOL_M = 50.0


def main():
    print("STEP 2d — adjacency flags\n" + "=" * 60)
    sma = gpd.read_file(GPKG, layer="sma_az_fullres")
    print(f"  loaded {len(sma):,} ownership polygons")

    sma_m = sma.to_crs(CRS_DIST)
    priv = sma_m[sma_m["land_status"] == "private"].copy()
    state = sma_m[sma_m["land_status"] == "state_trust"]
    trib = sma_m[sma_m["land_status"] == "tribal"]
    print(f"  private={len(priv):,}  state_trust={len(state):,}  "
          f"tribal={len(trib):,}")

    # Buffer the private polygons once, then spatial-join against each class.
    probe = priv[["geometry"]].copy()
    probe["geometry"] = probe.geometry.buffer(TOUCH_TOL_M)

    adj_state = gpd.sjoin(probe, state[["geometry"]], predicate="intersects",
                          how="inner").index.unique()
    adj_trib = gpd.sjoin(probe, trib[["geometry"]], predicate="intersects",
                         how="inner").index.unique()
    print(f"  abuts state trust: {len(adj_state):,}")
    print(f"  abuts tribal     : {len(adj_trib):,}")

    def note(idx):
        bits = []
        if idx in set(adj_state):
            bits.append("abuts state_trust (ASLD auction land adjacent — "
                        "expansion path, also an opposition surface)")
        if idx in set(adj_trib):
            bits.append("abuts tribal land (BIA lease jurisdiction adjacent; "
                        "consultation expectations)")
        return "; ".join(bits) if bits else "no state_trust/tribal adjacency"

    s_state, s_trib = set(adj_state), set(adj_trib)
    priv["adjacency_note"] = [
        note(i) for i in priv.index
    ]
    priv["abuts_state_trust"] = [i in s_state for i in priv.index]
    priv["abuts_tribal"] = [i in s_trib for i in priv.index]

    priv_wgs = priv.to_crs("EPSG:4326")
    priv_wgs.to_file(GPKG, layer="private_land", driver="GPKG")

    ac = priv["acres_computed_equalarea"]
    print(f"\n  private acres total        : {ac.sum():,.0f}")
    print(f"  private acres abutting ST  : "
          f"{priv.loc[priv['abuts_state_trust'], 'acres_computed_equalarea'].sum():,.0f}")
    print(f"  private acres abutting trib: "
          f"{priv.loc[priv['abuts_tribal'], 'acres_computed_equalarea'].sum():,.0f}")

    # Size distribution of private polygons — relevant because a data center
    # campus needs contiguous acreage.
    print("\n  private polygon size distribution (acres):")
    for q in [0.5, 0.75, 0.9, 0.95, 0.99]:
        print(f"    p{int(q*100):02d}  {ac.quantile(q):12,.0f}")
    print(f"    max   {ac.max():12,.0f}")
    for thr in [100, 500, 1000, 2000, 5000]:
        n = (ac >= thr).sum()
        print(f"    >= {thr:5d} ac : {n:5,} polygons, "
              f"{ac[ac >= thr].sum():12,.0f} ac")

    with open(os.path.join(DATA, "step2d_adjacency.json"), "w") as fh:
        json.dump({
            "private_polygons": int(len(priv)),
            "abuts_state_trust": int(len(adj_state)),
            "abuts_tribal": int(len(adj_trib)),
            "touch_tolerance_m": TOUCH_TOL_M,
            "private_acres": float(ac.sum()),
        }, fh, indent=2)
    print("\nSTEP 2d complete.")


if __name__ == "__main__":
    main()
