"""STEP 3C (analysis) — Arizona retirements, aggregated to plant level.

Every AZ unit retired since 2010 or carrying an announced retirement.

The two documented EIA gotchas, both handled explicitly:

  1. Header offset is not stable across releases -> detected by scanning for
     known column names (see step3_power._find_header_row), never hardcoded.
  2. Blank "Planned Retirement Year" arrives as an EMPTY STRING, not null.
     A bare .notna() therefore counts operating units as announced
     retirements. Every year column is coerced with
     pd.to_numeric(errors='coerce') BEFORE any null test.

EIA-860M (monthly) is joined on Plant Code + Generator ID to pick up
retirement announcements newer than the annual release.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_WGS84, DATA, log_status

GPKG = os.path.join(DATA, "az_power.gpkg")
RETIRE_SINCE = 2010
NAMED = ["Navajo", "Cholla", "Coronado", "Apache", "Springerville"]


def coerce_year(s):
    """Coerce a year column to numeric. Empty strings -> NaN, not 0."""
    return pd.to_numeric(s, errors="coerce")


def main():
    print("STEP 3C analysis — Arizona retirements\n" + "=" * 60)
    gens = pd.read_pickle(os.path.join(DATA, "eia860_az_generators.pkl"))
    plants = pd.read_pickle(os.path.join(DATA, "eia860_plants.pkl"))

    # Demonstrate the empty-string trap on the real data before fixing it.
    raw = gens["Planned Retirement Year"]
    naive = raw.notna().sum()
    coerced = coerce_year(raw).notna().sum()
    blanks = (raw.astype(str).str.strip() == "").sum()
    print(f"  'Planned Retirement Year': naive .notna() -> {naive} rows; "
          f"after to_numeric(coerce) -> {coerced} rows "
          f"({blanks} empty strings that a bare .notna() would have "
          f"miscounted as announced retirements)")

    for c in ["Retirement Year", "Retirement Month", "Planned Retirement Year",
              "Planned Retirement Month", "Operating Year"]:
        if c in gens.columns:
            gens[c] = coerce_year(gens[c])
    gens["Nameplate Capacity (MW)"] = pd.to_numeric(
        gens["Nameplate Capacity (MW)"], errors="coerce")

    # ---- EIA-860M overlay ----------------------------------------------
    m_path = next((os.path.join(DATA, f) for f in os.listdir(DATA)
                   if f.endswith(".xlsx") and "generator" in f.lower()), None)
    mon = None
    if m_path:
        try:
            probe = pd.read_excel(m_path, sheet_name=0, header=None, nrows=10,
                                  dtype=str)
            hdr = None
            for i in range(len(probe)):
                vals = {str(v).strip().lower() for v in probe.iloc[i].tolist()}
                if "plant id" in vals and "generator id" in vals:
                    hdr = i
                    break
            if hdr is None:
                raise RuntimeError("no header row with 'Plant ID' + "
                                   "'Generator ID' in first 10 rows")
            mon = pd.read_excel(m_path, sheet_name=0, header=hdr)
            mon.columns = [str(c).strip() for c in mon.columns]
            mon = mon[mon["Plant State"].astype(str).str.upper() == "AZ"]
            for c in mon.columns:
                if "Retirement Year" in c:
                    mon[c] = coerce_year(mon[c])
            print(f"  EIA-860M: header row {hdr}, {len(mon)} AZ generator rows "
                  f"from {os.path.basename(m_path)}")
            log_status(f"EIA-860M parsed ({os.path.basename(m_path)})", m_path,
                       True, records=len(mon), key="eia860m_parsed")
        except Exception as exc:  # noqa: BLE001
            log_status("EIA-860M parse", m_path or "n/a", False,
                       detail=str(exc), key="eia860m_parsed")
            mon = None

    # ---- select retirements --------------------------------------------
    ret_actual = gens[gens["Retirement Year"].notna()
                      & (gens["Retirement Year"] >= RETIRE_SINCE)].copy()
    ret_actual["retire_type"] = "retired"
    ret_actual["retire_year"] = ret_actual["Retirement Year"]

    ann = gens[gens["Planned Retirement Year"].notna()
               & gens["Retirement Year"].isna()].copy()
    ann["retire_type"] = "announced"
    ann["retire_year"] = ann["Planned Retirement Year"]

    ret = pd.concat([ret_actual, ann], ignore_index=True)
    print(f"\n  units retired >= {RETIRE_SINCE}: {len(ret_actual)}")
    print(f"  units with announced retirement : {len(ann)}")

    # Overlay 860M announcements not present in the annual file.
    if mon is not None:
        pr = next((c for c in mon.columns
                   if c.lower().startswith("planned retirement year")), None)
        if pr:
            m_ann = mon[mon[pr].notna()][["Plant ID", "Generator ID", pr]]
            m_ann.columns = ["Plant Code", "Generator ID", "m860_planned_year"]
            key = ["Plant Code", "Generator ID"]
            for c in key:
                ret[c] = ret[c].astype(str).str.strip()
                m_ann[c] = m_ann[c].astype(str).str.strip()
            existing = set(map(tuple, ret[key].values))
            new = m_ann[~m_ann[key].apply(tuple, axis=1).isin(existing)]
            print(f"  EIA-860M adds {len(new)} announced retirements not in "
                  f"the annual release")
            ret = ret.merge(m_ann, on=key, how="left")

    # ---- attach plant location -----------------------------------------
    pl = plants[plants["State"].astype(str).str.upper() == "AZ"][
        ["Plant Code", "Plant Name", "County", "Latitude", "Longitude",
         "Balancing Authority Code", "Utility Name", "Sector Name"]].copy()
    # Plant Code is float64 in the generator sheets and int64 in the plant
    # workbook. Casting straight to str gives "113.0" vs "113" and the merge
    # silently yields zero matches — every coordinate comes back null. Coerce
    # both through numeric to a nullable integer first.
    pl["Plant Code"] = pd.to_numeric(pl["Plant Code"],
                                     errors="coerce").astype("Int64")
    ret["Plant Code"] = pd.to_numeric(ret["Plant Code"],
                                      errors="coerce").astype("Int64")
    matched = ret["Plant Code"].isin(set(pl["Plant Code"].dropna())).sum()
    print(f"  plant-location join: {matched}/{len(ret)} unit rows matched a "
          f"plant record")
    if matched == 0:
        raise RuntimeError("plant join matched nothing — refusing to emit "
                           "candidates with no coordinates")
    ret = ret.merge(pl.drop(columns=["Plant Name"]), on="Plant Code",
                    how="left", suffixes=("", "_plant"))

    # ---- aggregate to plant level --------------------------------------
    ret["Nameplate Capacity (MW)"] = pd.to_numeric(
        ret["Nameplate Capacity (MW)"], errors="coerce")
    agg = ret.groupby(["Plant Code", "Plant Name"]).agg(
        retired_mw=("Nameplate Capacity (MW)", "sum"),
        n_units=("Generator ID", "count"),
        county=("County", "first"),
        latitude=("Latitude", "first"),
        longitude=("Longitude", "first"),
        utility_name=("Utility Name", "first"),
        ba_code=("Balancing Authority Code", "first"),
        first_retire_year=("retire_year", "min"),
        last_retire_year=("retire_year", "max"),
        retire_types=("retire_type", lambda s: ",".join(sorted(set(s)))),
        technologies=("Technology", lambda s: "; ".join(sorted(
            {str(x) for x in s if str(x) != "nan"}))),
        fuels=("Energy Source 1", lambda s: ",".join(sorted(
            {str(x) for x in s if str(x) != "nan"}))),
        statuses=("Status", lambda s: ",".join(sorted(set(map(str, s))))),
    ).reset_index().sort_values("retired_mw", ascending=False)

    print(f"\n  plants with retired/announced capacity: {len(agg)}")
    print(f"  plants >= 50 MW (the Pop 1 gate): "
          f"{(agg['retired_mw'] >= 50).sum()}")

    print("\n  TOP 20 BY RETIRED/ANNOUNCED MW")
    print(f"  {'plant':32s} {'MW':>9s} {'yr':>6s} {'type':>18s} "
          f"{'county':14s} {'lat':>8s} {'lon':>10s}")
    for _, r in agg.head(20).iterrows():
        print(f"  {str(r['Plant Name'])[:32]:32s} {r['retired_mw']:9,.1f} "
              f"{str(int(r['last_retire_year']) if pd.notna(r['last_retire_year']) else '?'):>6s} "
              f"{r['retire_types']:>18s} {str(r['county'])[:14]:14s} "
              f"{r['latitude'] if pd.notna(r['latitude']) else float('nan'):8.4f} "
              f"{r['longitude'] if pd.notna(r['longitude']) else float('nan'):10.4f}")

    # ---- verify the five named plants against the data ------------------
    print("\n  NAMED PLANTS — verified against the workbook, not assumed:")
    allaz = gens.copy()
    for nm in NAMED:
        hit = allaz[allaz["Plant Name"].astype(str).str.contains(
            nm, case=False, na=False)]
        if hit.empty:
            print(f"    {nm:16s} NOT FOUND in EIA-860 2024 Arizona records")
            continue
        for pc, grp in hit.groupby(["Plant Code", "Plant Name"]):
            ry = grp["Retirement Year"].dropna()
            py = grp["Planned Retirement Year"].dropna()
            mw = grp["Nameplate Capacity (MW)"].sum()
            print(f"    {nm:16s} {str(pc[1])[:26]:26s} code={pc[0]} "
                  f"units={len(grp)} nameplate={mw:,.1f} MW "
                  f"status={sorted(set(grp['Status'].astype(str)))} "
                  f"retired_yrs={sorted(set(ry.astype(int))) if len(ry) else '-'} "
                  f"planned_yrs={sorted(set(py.astype(int))) if len(py) else '-'}")

    agg.to_csv(os.path.join(DATA, "az_retirements_plant_level.csv"),
               index=False)
    ret.to_csv(os.path.join(DATA, "az_retirements_unit_level.csv"), index=False)

    geo = agg.dropna(subset=["latitude", "longitude"])
    gdf = gpd.GeoDataFrame(
        geo, geometry=gpd.points_from_xy(geo["longitude"], geo["latitude"]),
        crs=CRS_WGS84)
    gdf.to_file(GPKG, layer="retired_plants", driver="GPKG")
    print(f"\n  {len(gdf)} plants have coordinates "
          f"({len(agg) - len(gdf)} missing lat/lon)")
    print("\nSTEP 3C analysis complete.")


if __name__ == "__main__":
    main()
