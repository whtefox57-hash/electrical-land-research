"""
Steps 3-5 -- build candidate sites, score them, write outputs.

Required sources: A (substations), B (transmission), C (EIA generators).
Optional sources: D (broadband proxy), E (water), counties, block groups.

If a REQUIRED source is missing the script refuses to run and names it. It will
not produce a partially-populated candidate set that looks complete.

Run:  python3 scripts/build_screen.py
"""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loaders  # noqa: E402
from config import (  # noqa: E402
    AS_OF_DATE, GEOGRAPHIC_CRS, INTERCONNECT_STALE_MULTIPLIER,
    MAX_POSSIBLE_SCORE, NEIGHBOURHOOD_M, OUTPUTS, POP1_MIN_RETIRED_MW,
    POP1_RETIRED_SINCE_YEAR, POP2_EXCLUSION_M, POP2_MIN_KV, RAW, RUBRIC,
    STALE_RETIREMENT_YEARS, TOP_N, WORKING_CRS,
)

GPKG = OUTPUTS / "tx_candidates.gpkg"
TOP_CSV = OUTPUTS / "top25_candidates.csv"
COUNTY_CSV = OUTPUTS / "COUNTY_SUMMARY.csv"
METHOD_MD = OUTPUTS / "METHOD.md"

# Fields computed by this script rather than read from source. Surfaced in
# METHOD.md so no derived number is ever mistaken for a source measurement.
DERIVED_FIELDS: list[str] = []


def derived(name: str, how: str) -> str:
    DERIVED_FIELDS.append(f"`{name}` -- {how}")
    return name


# ==========================================================================
# scoring primitives
# ==========================================================================
def band(value: float, bands: list[tuple[float, float]], default: float) -> float:
    """First band whose threshold the value meets or exceeds (descending)."""
    if pd.isna(value):
        return default
    for threshold, points in bands:
        if value >= threshold:
            return points
    return default


def band_below(value: float, bands: list[tuple[float, float]],
               default: float) -> float:
    """First band whose threshold the value is at or under (ascending)."""
    if pd.isna(value):
        return default
    for threshold, points in bands:
        if value <= threshold:
            return points
    return default


def score_interconnection(mw: float, years_since: float) -> float:
    cfg = RUBRIC["interconnection"]
    pts = band(mw, cfg["bands_mw"], 0)
    if not pd.isna(years_since) and years_since > STALE_RETIREMENT_YEARS:
        pts *= cfg["stale_multiplier"]
    return float(pts)


def score_sub_proximity(dist_m: float) -> float:
    cfg = RUBRIC["substation_proximity"]
    return float(band_below(dist_m, cfg["bands_m"], cfg["beyond"]))


def score_sub_voltage(kv: float) -> float:
    cfg = RUBRIC["substation_voltage"]
    return float(band(kv, cfg["bands_kv"], cfg["below"]))


def score_transmission(dist_m: float, kv: float) -> float:
    """tx_points = 15 * distance_factor * voltage_factor  (see config.RUBRIC)."""
    cfg = RUBRIC["transmission"]
    df_ = band_below(dist_m, cfg["distance_factors_m"], cfg["distance_factor_beyond"])
    vf = band(kv, cfg["voltage_factors_kv"], cfg["voltage_factor_below"])
    return float(cfg["max_points"] * df_ * vf)


def score_broadband(n: float) -> float:
    cfg = RUBRIC["broadband"]
    return float(band(n, [(float(a), b) for a, b in cfg["bands_count"]],
                      cfg["none_or_unknown"]))


def score_water(dist_m: float, available: bool) -> float:
    cfg = RUBRIC["water"]
    if not available:
        return float(cfg["unavailable_score"])
    return float(band_below(dist_m, cfg["bands_m"], cfg["beyond"]))


# ==========================================================================
# Step 3 -- candidate construction
# ==========================================================================
def build_population_1(gens: pd.DataFrame, plants: pd.DataFrame) -> gpd.GeoDataFrame:
    """Plants with retired or announced-retirement capacity >= threshold."""
    g = gens.copy()

    has_actual = g["retire_year"].notna()
    has_planned = g["planned_retire_year"].notna()

    # Per the brief: actual retirements from POP1_RETIRED_SINCE_YEAR onward,
    # plus every announced future retirement regardless of year. Retirements
    # before the cutoff are deliberately excluded -- their interconnection
    # rights are the least likely to have survived.
    keep = ((has_actual & (g["retire_year"] >= POP1_RETIRED_SINCE_YEAR))
            | has_planned)
    g = g[keep].copy()
    if g.empty:
        return gpd.GeoDataFrame(
            columns=["plant_code", "geometry"], geometry="geometry",
            crs=f"EPSG:{GEOGRAPHIC_CRS}")

    g["eff_retire_year"] = g["retire_year"].fillna(g["planned_retire_year"])
    g["eff_retire_month"] = g["retire_month"].fillna(
        g["planned_retire_month"]).fillna(6)
    g["retirement_is_announced"] = g["retire_year"].isna() & has_planned

    agg = g.groupby("plant_code").agg(
        plant_name=("plant_name", "first"),
        county_attr=("county", "first"),
        retired_mw=("capacity_mw", "sum"),
        unit_count=("capacity_mw", "size"),
        eff_retire_year=("eff_retire_year", "max"),
        eff_retire_month=("eff_retire_month", "max"),
        any_announced=("retirement_is_announced", "any"),
        technology=("technology", "first"),
        gen_lat=("latitude", "first"),
        gen_lon=("longitude", "first"),
        source_sheets=("_sheet", lambda s: "; ".join(sorted(set(s))[:4])),
    ).reset_index()

    agg = agg[agg["retired_mw"] >= POP1_MIN_RETIRED_MW].copy()

    # Coordinates: prefer the EIA Plant file, fall back to any lat/lon carried
    # on the generator record (860M has them; 860 annual does not).
    if not plants.empty:
        agg = agg.merge(
            plants[["plant_code", "latitude", "longitude", "county"]],
            on="plant_code", how="left", suffixes=("", "_plant"))
    else:
        agg["latitude"] = np.nan
        agg["longitude"] = np.nan
        agg["county"] = pd.NA

    agg["lat"] = agg["latitude"].fillna(agg["gen_lat"])
    agg["lon"] = agg["longitude"].fillna(agg["gen_lon"])

    missing = agg["lat"].isna() | agg["lon"].isna()
    if missing.any():
        print(f"  WARNING: {int(missing.sum())} Population 1 plants dropped for "
              f"missing coordinates (no fabricated positions): "
              f"{agg.loc[missing, 'plant_name'].head(10).tolist()}")
    agg = agg[~missing].copy()

    derived("retired_mw", "sum of EIA nameplate MW over qualifying units per plant")
    derived("eff_retire_year",
            "max of actual Retirement Year, else Planned Retirement Year")

    agg["site_type"] = "retired_generation"
    agg["site_name"] = agg["plant_name"]
    agg["county_src"] = agg["county"].fillna(agg["county_attr"])
    geom = [Point(xy) for xy in zip(agg["lon"], agg["lat"])]
    return gpd.GeoDataFrame(agg, geometry=geom, crs=f"EPSG:{GEOGRAPHIC_CRS}")


def build_population_2(subs: gpd.GeoDataFrame,
                       pop1: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """High-voltage substations not already represented by a Population 1 site."""
    hv = subs[subs["sub_max_kv"] >= POP2_MIN_KV].copy()
    if hv.empty:
        return gpd.GeoDataFrame(
            columns=["site_name", "geometry"], geometry="geometry", crs=subs.crs)

    if not pop1.empty:
        near = gpd.sjoin_nearest(
            hv.to_crs(WORKING_CRS), pop1.to_crs(WORKING_CRS)[["geometry"]],
            how="left", distance_col="_d")
        near = near[~near.index.duplicated(keep="first")]
        hv = hv.loc[near[(near["_d"].isna()) | (near["_d"] > POP2_EXCLUSION_M)].index]

    out = hv.copy()
    out["site_type"] = "hv_substation"
    out["site_name"] = out["sub_name"]
    out["retired_mw"] = 0.0
    out["eff_retire_year"] = np.nan
    out["unit_count"] = 0
    out["county_src"] = out["sub_county_attr"]
    out["plant_code"] = pd.NA
    return out.reset_index(drop=True)


# ==========================================================================
# Step 3 -- spatial metrics
# ==========================================================================
def nearest_metric(cands: gpd.GeoDataFrame, target: gpd.GeoDataFrame,
                   value_cols: list[str], prefix: str) -> pd.DataFrame:
    """Distance to nearest target feature plus selected attributes of it."""
    joined = gpd.sjoin_nearest(
        cands[["geometry"]], target[value_cols + ["geometry"]],
        how="left", distance_col=f"{prefix}_dist_m")
    joined = joined[~joined.index.duplicated(keep="first")]
    cols = {f"{prefix}_dist_m": joined[f"{prefix}_dist_m"]}
    for c in value_cols:
        cols[f"{prefix}_{c}"] = joined[c]
    return pd.DataFrame(cols, index=cands.index)


def count_within(cands: gpd.GeoDataFrame, target: gpd.GeoDataFrame,
                 radius_m: float) -> pd.DataFrame:
    buf = cands[["geometry"]].copy()
    buf["geometry"] = buf.geometry.buffer(radius_m)
    buf["_cid"] = buf.index
    hit = gpd.sjoin(target, buf, how="inner", predicate="intersects")
    return hit


def compute_metrics(cands: gpd.GeoDataFrame, subs: gpd.GeoDataFrame,
                    lines: gpd.GeoDataFrame, water: gpd.GeoDataFrame | None,
                    counties: gpd.GeoDataFrame | None,
                    bgs: gpd.GeoDataFrame | None,
                    broadband: pd.DataFrame | None) -> gpd.GeoDataFrame:
    c = cands.to_crs(WORKING_CRS).copy()
    s = subs.to_crs(WORKING_CRS)
    t = lines.to_crs(WORKING_CRS)

    # --- substations ------------------------------------------------------
    c = c.join(nearest_metric(c, s, ["sub_max_kv", "sub_name"], "nearest_sub"))
    derived("nearest_sub_dist_m", f"geodesic distance in EPSG:{WORKING_CRS}")

    hits = count_within(c, s, NEIGHBOURHOOD_M)
    c["subs_within_5km"] = (hits.groupby("_cid").size()
                            .reindex(c.index).fillna(0).astype(int))
    c["max_kv_within_5km"] = (hits.groupby("_cid")["sub_max_kv"].max()
                              .reindex(c.index))
    derived("subs_within_5km", f"count of substations intersecting a "
                               f"{NEIGHBOURHOOD_M:.0f} m buffer")

    # --- transmission -----------------------------------------------------
    c = c.join(nearest_metric(c, t, ["line_kv", "line_owner"], "nearest_line"))
    lhits = count_within(c, t, NEIGHBOURHOOD_M)
    c["lines_within_5km"] = (lhits.groupby("_cid").size()
                             .reindex(c.index).fillna(0).astype(int))
    by_class = (lhits.groupby(["_cid", "line_volt_class"]).size()
                .unstack(fill_value=0))
    for cls in by_class.columns:
        c[f"lines_5km_{cls}"] = by_class[cls].reindex(c.index).fillna(0).astype(int)
    derived("lines_5km_<class>", "count of transmission lines within 5 km by "
                                 "voltage class")

    # --- county -----------------------------------------------------------
    if counties is not None:
        cj = gpd.sjoin(c[["geometry"]], counties.to_crs(WORKING_CRS),
                       how="left", predicate="within")
        cj = cj[~cj.index.duplicated(keep="first")]
        c["county_name"] = cj["county_name"]
        c["county_method"] = "spatial join to county polygons"
    else:
        c["county_name"] = c.get("county_src")
        c["county_method"] = "source attribute (no county polygon layer loaded)"
    derived("county_name", "spatial join where a county layer was available, "
                           "otherwise copied from the source attribute")

    # --- broadband --------------------------------------------------------
    if bgs is not None and broadband is not None:
        bj = gpd.sjoin(c[["geometry"]], bgs.to_crs(WORKING_CRS),
                       how="left", predicate="within")
        bj = bj[~bj.index.duplicated(keep="first")]
        c["bg_geoid"] = bj["bg_geoid"]
        c = c.merge(broadband[["bg_geoid", "broadband_providers"]],
                    on="bg_geoid", how="left")
        c["broadband_available"] = True
    else:
        c["bg_geoid"] = pd.NA
        c["broadband_providers"] = np.nan
        c["broadband_available"] = False

    # --- water ------------------------------------------------------------
    if water is not None and not water.empty:
        c = c.join(nearest_metric(c, water.to_crs(WORKING_CRS),
                                  ["water_source"], "nearest_water"))
        c["water_available"] = True
    else:
        c["nearest_water_dist_m"] = np.nan
        c["water_available"] = False

    # --- retirement age ---------------------------------------------------
    def years_since(row) -> float:
        y = row.get("eff_retire_year")
        if pd.isna(y):
            return np.nan
        m = row.get("eff_retire_month")
        m = int(m) if not pd.isna(m) and 1 <= m <= 12 else 6
        return (AS_OF_DATE - dt.date(int(y), m, 1)).days / 365.25

    c["years_since_retirement"] = c.apply(years_since, axis=1)
    c["stale_interconnection_flag"] = (
        c["years_since_retirement"] > STALE_RETIREMENT_YEARS)
    derived("years_since_retirement",
            f"({AS_OF_DATE} minus effective retirement date) / 365.25")
    return c


# ==========================================================================
# Step 4 -- scoring
# ==========================================================================
def apply_scores(c: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    water_ok = bool(c["water_available"].any())

    c["score_interconnection"] = [
        score_interconnection(mw, ys)
        for mw, ys in zip(c["retired_mw"].fillna(0), c["years_since_retirement"])
    ]
    c["score_sub_proximity"] = [score_sub_proximity(d)
                                for d in c["nearest_sub_dist_m"]]
    c["score_sub_voltage"] = [score_sub_voltage(v)
                              for v in c["nearest_sub_sub_max_kv"]]
    c["score_transmission"] = [
        score_transmission(d, v)
        for d, v in zip(c["nearest_line_dist_m"], c["nearest_line_line_kv"])
    ]
    c["score_broadband"] = [score_broadband(n) for n in c["broadband_providers"]]
    c["score_water"] = [score_water(d, water_ok)
                        for d in c["nearest_water_dist_m"]]

    parts = ["score_interconnection", "score_sub_proximity", "score_sub_voltage",
             "score_transmission", "score_broadband", "score_water"]
    c["score_total"] = c[parts].sum(axis=1).round(2)
    derived("score_total", "sum of the six rubric components in config.RUBRIC")

    if (c["score_total"] > MAX_POSSIBLE_SCORE + 1e-6).any():
        raise AssertionError("a candidate scored above the rubric maximum")
    return c.sort_values("score_total", ascending=False).reset_index(drop=True)


# ==========================================================================
# Step 5 -- outputs
# ==========================================================================
def write_outputs(c: gpd.GeoDataFrame, layers: dict[str, gpd.GeoDataFrame],
                  manifest: dict, notes: dict) -> gpd.GeoDataFrame:
    GPKG.unlink(missing_ok=True)
    for name, g in layers.items():
        if g is not None and not g.empty:
            g.to_crs(WORKING_CRS).to_file(GPKG, layer=name, driver="GPKG")
    c.to_file(GPKG, layer="candidates", driver="GPKG")

    wgs = c.to_crs(GEOGRAPHIC_CRS)
    c["lat_wgs84"] = wgs.geometry.y
    c["lon_wgs84"] = wgs.geometry.x
    c["google_maps_url"] = [
        f"https://www.google.com/maps?q={la:.6f},{lo:.6f}"
        for la, lo in zip(c["lat_wgs84"], c["lon_wgs84"])
    ]
    c["county_cad_note"] = ""

    top = c.head(TOP_N).copy()
    top.drop(columns=["geometry"]).to_csv(TOP_CSV, index=False)

    summary = (c.groupby("county_name", dropna=False)
               .agg(candidate_count=("score_total", "size"),
                    total_retired_mw=("retired_mw", "sum"),
                    mean_score=("score_total", "mean"),
                    max_score=("score_total", "max"))
               .reset_index()
               .sort_values(["candidate_count", "mean_score"], ascending=False))
    summary["mean_score"] = summary["mean_score"].round(2)
    summary.to_csv(COUNTY_CSV, index=False)

    write_method(c, top, manifest, notes)
    return top


def write_method(c: gpd.GeoDataFrame, top: gpd.GeoDataFrame, manifest: dict,
                 notes: dict) -> None:
    src_lines = []
    for key, rec in sorted(manifest.get("sources", {}).items()):
        files = ", ".join(f["path"] for f in rec["files"]) or "(none)"
        urls = sorted({a["url"] for a in rec["attempts"]})[:3]
        src_lines.append(
            f"### {key}\n\n"
            f"- status: **{rec['status']}**\n"
            f"- recorded: {rec['recorded_utc']}\n"
            f"- files: {files}\n"
            f"- endpoints tried: {', '.join(urls) if urls else 'n/a'}\n"
            f"- note: {rec.get('note') or '-'}\n"
        )

    counties = c["county_name"].nunique(dropna=True)
    top_counties = top["county_name"].value_counts().head(5).to_dict()

    METHOD_MD.write_text(f"""# METHOD -- Texas powered-land screen

Generated: {dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
As-of date for retirement arithmetic: **{AS_OF_DATE}**
Working CRS: **EPSG:{WORKING_CRS}**

## What this screen is

A first-pass desktop filter that ranks Texas locations by how plausible it is
that large electrical service already exists or could be obtained without
waiting out a full interconnection queue. It is a tool for deciding **where to
drive and who to call**. It is not a feasibility study and it carries no
information about actual available headroom at any substation.

## Projection note

The brief specified EPSG:3081 and described it as "Texas Centric Albers". That
name belongs to EPSG:3083 (NAD83 / Texas Centric Albers Equal Area). EPSG:3081
is NAD83 / Texas State Mapping System, a Lambert Conformal Conic projection.
Both are metre-based and both are appropriate for statewide Texas distance
work, so the specified 3081 was used. Set `TXLAND_CRS=3083` to switch.

## Sources

Every entry below is generated from `data/raw/MANIFEST.json`, which records the
actual HTTP result of each attempt.

{"".join(src_lines)}

## Candidate construction

- **Population 1** -- EIA plants whose retired or announced-retirement capacity
  sums to >= {POP1_MIN_RETIRED_MW:.0f} MW, counting actual retirements from
  {POP1_RETIRED_SINCE_YEAR} onward plus all announced future retirements.
- **Population 2** -- substations with max voltage >= {POP2_MIN_KV:.0f} kV that
  are not within {POP2_EXCLUSION_M:.0f} m of a Population 1 site.
- Populations are unioned; Population 2 is deduplicated against Population 1 by
  the {POP2_EXCLUSION_M:.0f} m rule above.

## Fields read directly from source

Plant name, plant code, county attribute, nameplate capacity, operating status,
retirement year/month, planned retirement year/month, latitude/longitude,
substation name, substation max/min voltage, line count, line voltage, line
owner, line status.

## Fields DERIVED by this pipeline (not read from source)

{chr(10).join("- " + d for d in sorted(set(DERIVED_FIELDS)))}

## Scoring

The rubric lives in `scripts/config.py` as `RUBRIC` and is the first-draft
rubric from the project brief. **It is a hypothesis, not a calibrated model.**
Nothing in this repository validates it against real engineering outcomes.

Transmission component formula:

    tx_points = 15 * distance_factor * voltage_factor

The product form is deliberate -- a 500 kV line 40 km away is worth nothing,
and a 69 kV line at the fence line is worth little. Both conditions must hold.

Maximum achievable total: **{MAX_POSSIBLE_SCORE}**
{notes.get("water_note", "")}

## Results at a glance

- candidates evaluated: {len(c)}
- score range: {c["score_total"].min():.2f} to {c["score_total"].max():.2f}
- distinct counties represented: {counties}
- top-25 county concentration: {top_counties}

## Known limitations

1. **Broadband is a proxy.** Provider counts by block group say nothing about
   long-haul fibre routes, which are proprietary. A site can show four
   providers and have no carrier-grade route within twenty miles.
2. **No headroom data.** Nothing here knows whether a substation has spare
   capacity. A 345 kV substation at the fence line can still be full.
3. **Interconnection rights are assumed, never verified.** Retired-plant
   interconnection agreements may be terminated, partially released, or already
   optioned by another developer. Sites with
   `stale_interconnection_flag = True` are the most suspect.
4. **Point geometry.** Plants and substations are single points. A large plant
   site is not a point, and the parcel you would actually buy may be a
   kilometre from the plotted coordinate.
5. **Nameplate is not deliverable capacity.** Retired MW is a proxy for the
   size of the interconnection, not a guarantee of what can be re-energised.
6. **No land ownership, zoning, water rights, or price.** None of that is in
   this screen.
7. **EIA vintage lag.** Annual EIA-860 trails reality by roughly a year;
   860M is more current but still monthly.

## What would make this screen WRONG

- **The rubric weights are guesses.** If substation headroom turns out to be
  the dominant constraint, then substation *proximity* -- which this screen
  weights at 25 points -- is nearly irrelevant, and the ranking is noise.
- **If retired-plant interconnection rights routinely lapse on retirement**,
  then the entire 30-point interconnection component is measuring a thing that
  does not exist, and Population 1 should be discarded.
- **If ERCOT queue position rather than physical proximity governs timeline**,
  a site with no substation nearby but an early queue slot beats everything
  ranked here.
- **If the EIA county or coordinate fields are wrong for a given plant**, that
  row is wrong in a way this screen cannot detect. Spot-check before driving.
- **If the top 25 cluster in one county**, that is evidence of a rubric
  artefact rather than a real geographic finding. Current concentration is
  shown above.
- **Any site where the plotted point is not the land you can buy** -- adjacent
  parcels may be unavailable, landlocked, or already optioned.

## Reproducing

```
python3 scripts/acquire.py       # Step 2
python3 scripts/build_screen.py  # Steps 3-5
python3 scripts/verify.py        # Step 6
```
""")


# ==========================================================================
# driver
# ==========================================================================
def main() -> int:
    print("=== STEPS 3-5 ===")
    missing: list[str] = []
    subs = lines_ = gens = plants = None
    try:
        subs = loaders.load_substations()
    except loaders.MissingSource as e:
        missing.append(str(e))
    try:
        lines_ = loaders.load_transmission()
    except loaders.MissingSource as e:
        missing.append(str(e))
    try:
        gens = loaders.load_eia_generators()
        plants = loaders.load_eia_plants()
    except loaders.MissingSource as e:
        missing.append(str(e))

    if missing:
        print("\nREFUSING TO BUILD -- required sources are absent:\n")
        for m in missing:
            print(f"  * {m}\n")
        print("No outputs were written. Nothing was estimated or synthesised.")
        return 2

    water = loaders.load_water()
    counties = loaders.load_counties()
    bgs = loaders.load_block_groups()
    broadband = loaders.load_broadband()

    notes = {}
    if water is None:
        notes["water_note"] = (
            "\n**Water layer (source E) was unavailable, so the water component "
            "scored 0 for every candidate and the practical maximum is 95. "
            "Scores were NOT rescaled to compensate.**")
        print("  NOTE: water layer absent -> water component is 0 for all; max 95")

    pop1 = build_population_1(gens, plants)
    pop2 = build_population_2(subs, pop1)
    print(f"  Population 1 (retired generation): {len(pop1)}")
    print(f"  Population 2 (HV substations):     {len(pop2)}")

    keep = ["site_name", "site_type", "plant_code", "retired_mw", "unit_count",
            "eff_retire_year", "eff_retire_month", "county_src", "technology",
            "geometry"]
    frames = [df.reindex(columns=[k for k in keep if k in df.columns] +
                         ["geometry"]).loc[:, lambda d: ~d.columns.duplicated()]
              for df in (pop1, pop2) if not df.empty]
    cands = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True),
                             crs=f"EPSG:{GEOGRAPHIC_CRS}")
    cands = cands[cands.geometry.notna() & ~cands.geometry.is_empty].copy()

    c = compute_metrics(cands, subs, lines_, water, counties, bgs, broadband)
    c = apply_scores(c)

    manifest = json.loads((RAW / "MANIFEST.json").read_text()) \
        if (RAW / "MANIFEST.json").exists() else {"sources": {}}
    layers = {"substations": subs, "transmission_lines": lines_,
              "water": water, "counties": counties}
    top = write_outputs(c, layers, manifest, notes)

    print(f"\n  candidates: {len(c)}   score range: "
          f"{c['score_total'].min():.1f}-{c['score_total'].max():.1f}")
    print(f"  wrote {GPKG.name}, {TOP_CSV.name}, {COUNTY_CSV.name}, "
          f"{METHOD_MD.name}")
    print(f"  top-25 counties: {top['county_name'].value_counts().head().to_dict()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
