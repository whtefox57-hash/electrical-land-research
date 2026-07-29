"""STEP 9 — outputs.

  outputs/az_candidates.gpkg          all layers + scored candidates
  outputs/az_top25.csv                top 25 private, with google_maps_url
                                      and a blank county_assessor_note
  outputs/az_excluded_high_score.csv  non-acquirable high scorers
"""
from __future__ import annotations

import os
import shutil
import sys

import fiona
import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_WGS84, DATA, OUTPUTS

SCORED = os.path.join(DATA, "az_candidates_scored.gpkg")
OWN = os.path.join(DATA, "az_ownership.gpkg")
POW = os.path.join(DATA, "az_power.gpkg")
WAT = os.path.join(DATA, "az_water.gpkg")
GPKG = os.path.join(OUTPUTS, "az_candidates.gpkg")

CSV_FIELDS = [
    "rank", "cand_id", "cand_name", "cand_type", "composite_score",
    "score_max_available", "score_rescaled_to_100", "score_basis",
    "lat", "lon", "google_maps_url", "county_assessor_note",
    "land_status", "acquirable", "land_status_note", "adjacency_note",
    "parcel_acres",
    "county_gis", "municipality", "jurisdiction",
    "serving_utility", "utility_type", "utility_type_detail",
    "utility_type_basis", "utility_assignment_confidence",
    "n_retail_territories_overlapping", "all_overlapping_utilities",
    "utility_website", "utility_phone",
    "est_capacity_mw", "capacity_basis", "capacity_confidence",
    "substation_mva_published", "size_class", "triggers",
    "ars_41_1519_tier", "cdc_program_status",
    "retired_mw_on_site", "last_retire_year", "years_since_retirement",
    "interconnection_rights_flag", "retire_types", "technologies", "fuels",
    "dist_nearest_substation_km", "nearest_substation_name",
    "nearest_substation_kv", "nearest_substation_status",
    "substations_within_5km", "max_kv_within_5km",
    "dist_nearest_transmission_km", "nearest_transmission_kv",
    "nearest_transmission_owner", "tx_lines_within_5km_total",
    "tx_lines_within_5km_lt100kv", "tx_lines_within_5km_100_229kv",
    "tx_lines_within_5km_230_344kv", "tx_lines_within_5km_gte345kv",
    "site_sub_kv", "min_volt_kv", "lines_count",
    "max_volt_provenance", "min_volt_provenance",
    "in_ama", "in_ina", "ama_ina_name", "groundwater_basin",
    "groundwater_subbasin", "municipal_water_available", "cws_provider",
    "nearest_surface_water_km", "nearest_surface_water_name",
    "nearest_surface_water_basis", "registered_wells_within_5km",
    "water_risk_score", "water_risk_basis", "water_cap_note", "water_cap_kind",
    "political_risk_score", "political_prior_basis",
    "pol_moratorium_pts", "pol_no_ordinance_pts", "pol_no_opposition_pts",
    "pol_prior_industrial_pts", "prior_industrial_use_basis",
    "pol_dist_resid_pts", "dist_to_residential_km",
    "dist_to_residential_basis",
    "broadband_providers_PROXY", "broadband_fiber_providers_PROXY",
    "broadband_basis", "bg_geoid",
    "sc_interconnection_raw", "interconnection_basis",
    "sc_substation_proximity_raw", "sc_substation_voltage_raw",
    "sc_transmission_raw", "sc_water_raw", "sc_political_raw",
    "sc_broadband_raw",
    "sc_interconnection_norm", "sc_substation_proximity_norm",
    "sc_substation_voltage_norm", "sc_transmission_norm", "sc_water_norm",
    "sc_political_norm", "sc_broadband_norm",
]


def prep(df):
    df = df.copy()
    df["google_maps_url"] = [
        f"https://www.google.com/maps/search/?api=1&query={la:.6f},{lo:.6f}"
        for la, lo in zip(df["lat"], df["lon"])]
    df["county_assessor_note"] = ""      # intentionally blank, for the user
    for c in CSV_FIELDS:
        if c not in df.columns:
            df[c] = None
    return df


def main():
    print("STEP 9 — OUTPUTS\n" + "=" * 60)
    os.makedirs(OUTPUTS, exist_ok=True)

    priv = gpd.read_file(SCORED, layer="private_ranked")
    excl = gpd.read_file(SCORED, layer="excluded_ranked")
    allc = gpd.read_file(SCORED, layer="candidates_scored")

    priv = priv.sort_values("composite_score", ascending=False).reset_index(
        drop=True)
    priv["rank"] = priv.index + 1
    excl = excl.sort_values("composite_score", ascending=False).reset_index(
        drop=True)
    excl["rank"] = excl.index + 1

    # ---------- CSVs ----------
    top25 = prep(priv.head(25))
    top25[CSV_FIELDS].to_csv(os.path.join(OUTPUTS, "az_top25.csv"),
                             index=False)
    print(f"  az_top25.csv           {len(top25)} rows, "
          f"{len(CSV_FIELDS)} columns")

    ex10 = prep(excl.head(10))
    ex10[CSV_FIELDS].to_csv(
        os.path.join(OUTPUTS, "az_excluded_high_score.csv"), index=False)
    print(f"  az_excluded_high_score.csv {len(ex10)} rows")

    # Full ranked private list, for reference beyond the top 25.
    prep(priv)[CSV_FIELDS].to_csv(
        os.path.join(OUTPUTS, "az_all_private_ranked.csv"), index=False)
    print(f"  az_all_private_ranked.csv  {len(priv)} rows")

    # ---------- GeoPackage ----------
    if os.path.exists(GPKG):
        os.remove(GPKG)
    layers = [
        (prep(priv).drop(columns=[]), "candidates_private_ranked"),
        (prep(excl), "candidates_excluded_ranked"),
        (allc, "candidates_all_scored"),
    ]
    for gdf, name in layers:
        gdf.to_file(GPKG, layer=name, driver="GPKG")

    # Context layers so the package stands alone in QGIS.
    for src, lyr, dest in [
        (OWN, "sma_az_fullres", "land_ownership_all"),
        (OWN, "private_land", "land_private"),
        (POW, "substations", "substations"),
        (POW, "transmission_lines", "transmission_lines"),
        (POW, "retired_plants", "retired_plants"),
        (POW, "utility_territories", "utility_territories"),
        (WAT, "ama_ina", "ama_ina"),
        (WAT, "groundwater_basin", "groundwater_basin"),
        (WAT, "cws_service_area", "cws_service_area"),
        (WAT, "nhd_perennial", "nhd_perennial"),
        (WAT, "counties", "counties"),
        (WAT, "city_boundaries", "city_boundaries"),
    ]:
        try:
            g = gpd.read_file(src, layer=lyr)
            g.to_file(GPKG, layer=dest, driver="GPKG")
        except Exception as exc:  # noqa: BLE001
            print(f"    !! could not copy {lyr}: {exc}")

    ls = fiona.listlayers(GPKG)
    print(f"\n  az_candidates.gpkg     {len(ls)} layers")
    for l in ls:
        with fiona.open(GPKG, layer=l) as src:
            print(f"    {l:32s} {len(src):8,} features  {src.crs_wkt[:28]}...")

    print("\n  TOP 25 PRIVATE")
    print(f"  {'#':>3s} {'name':30s} {'score':>7s} {'county':12s} "
          f"{'utility':26s} {'kV':>6s} {'water':>6s}")
    for _, r in top25.iterrows():
        print(f"  {int(r['rank']):3d} {str(r['cand_name'])[:30]:30s} "
              f"{r['composite_score']:7.2f} {str(r['county_gis'])[:12]:12s} "
              f"{str(r['serving_utility'])[:26]:26s} "
              f"{(r['max_kv_within_5km'] if pd.notna(r['max_kv_within_5km']) else 0):6.0f} "
              f"{r['water_risk_score']:6.0f}")
    print("\nSTEP 9 CSV/GPKG complete.")


if __name__ == "__main__":
    main()
