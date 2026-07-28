"""
Texas powered-land candidate screen.

Builds candidate sites from EIA-860/860M retirement data and (proxy or real)
substations, computes proximity metrics in EPSG:3081, scores them, and writes
the Step 5 outputs.

PROVENANCE RULES FOLLOWED HERE
  - Nothing is estimated or synthesised. Every value is either read from a
    source file or computed geometrically from source geometry.
  - Fields computed rather than read carry a 'derived' note in METHOD.md and,
    where the derivation is non-obvious, a *_derived or is_proxy flag column.
  - Sentinel values in the source (-999999 voltage, 'NOT AVAILABLE' names) are
    converted to null, never to a number.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import zipfile

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import Point

# --------------------------------------------------------------------------
# CONFIG — tune here.
# --------------------------------------------------------------------------
CONFIG = {
    "screen_year": 2026,          # 'years since retirement' is measured from this
    "retired_since": 2010,        # Population 1 lower bound on retirement year
    "min_site_mw": 50.0,          # Population 1 capacity threshold
    "pop2_min_kv": 138.0,         # Population 2 substation voltage threshold
    "pop2_exclude_within_m": 2000.0,   # drop substations this close to a Pop 1 site
    "stale_interconnect_years": 10,    # older than this -> 0.5 multiplier
    "stale_multiplier": 0.5,

    # The rubric puts no upper bound on how far in the future an "announced
    # retirement" may be, so a unit slated to retire in 2058 scores identically
    # to one that shut down in 2018. Those plants are operating today and are
    # not acquirable. Sites beyond this horizon are FLAGGED, not dropped —
    # set 'announced_horizon_drop' to True to exclude them instead.
    "announced_horizon_years": 10,
    "announced_horizon_drop": False,
    "proxy_cluster_tol_m": 250.0,      # line-endpoint clustering radius

    # Rubric weights. 'available' is set at runtime — a factor whose source
    # dataset failed is excluded from the rescale denominator rather than
    # silently scored 0.
    "weights": {
        "interconnection":  30,
        "substation_prox":  25,
        "substation_volt":  15,
        "transmission":     15,
        "broadband":        10,
        "water":             5,
    },

    # Interconnection: plant-level retired + announced MW -> points
    "interconnection_bands": [(500, 30), (200, 22), (50, 14)],

    # Substation proximity: metres -> points
    "sub_prox_bands": [(1000, 25), (3000, 18), (5000, 10), (10000, 3)],

    # Substation voltage: kV -> points
    "sub_volt_bands": [(345, 15), (230, 12), (138, 8), (69, 3)],

    # Transmission score = 15 * distance_factor * voltage_factor, maximised over
    # every line within 10 km (not just the nearest). Rationale: a site 3 km from
    # a 345 kV line is a better large-load prospect than one 200 m from a 69 kV
    # lateral, and scoring only the nearest line would invert that.
    "tx_dist_factor": [(500, 1.00), (1000, 0.85), (2000, 0.65),
                       (5000, 0.40), (10000, 0.15)],
    "tx_volt_factor": [(345, 1.00), (230, 0.85), (138, 0.65), (69, 0.35)],
    "tx_volt_factor_floor": 0.15,

    # Broadband providers in block group -> points (unused if FCC data absent)
    "broadband_bands": [(4, 10), (3, 7), (2, 4), (1, 1)],

    # Water: metres to nearest major reservoir/river -> points
    "water_bands": [(1000, 5), (5000, 4), (10000, 3), (25000, 1)],

    "search_radius_m": 5000.0,    # 'count within 5 km' radius
    "top_n": 25,
}

TX_ALBERS = "EPSG:3081"   # NAD83 / Texas State Mapping System (metres)
WGS84 = "EPSG:4326"

RAW = "data/raw"
OUT = "outputs"

# Placeholder strings the HIFLD/EIA sources use instead of nulls.
NULL_TOKENS = {"NOT AVAILABLE", "UNKNOWN", "NA", "N/A", "", "NONE", "NULL"}

REPORT: dict = {"generated": dt.date.today().isoformat(), "notes": [], "failures": []}


def note(msg: str) -> None:
    print(msg)
    REPORT["notes"].append(msg)


def band_score(value, bands, default=0):
    """First band whose threshold the value meets or exceeds -> its score."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return default
    for thresh, score in bands:
        if value >= thresh:
            return score
    return default


def band_score_below(value, bands, default=0):
    """First band whose threshold the value is at or under -> its score."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return default
    for thresh, score in bands:
        if value <= thresh:
            return score
    return default


def clean_token(s):
    if pd.isna(s):
        return None
    t = str(s).strip()
    if t.upper() in NULL_TOKENS or t.upper().startswith("UNKNOWN"):
        return None
    return t


# --------------------------------------------------------------------------
# 1. Transmission lines
# --------------------------------------------------------------------------
def load_transmission():
    g = gpd.read_file(f"{RAW}/transmission_lines_tx.geojson")
    n0 = len(g)
    # VOLTAGE uses -999999 as a missing sentinel. Convert to NaN; never score it.
    v = pd.to_numeric(g["VOLTAGE"], errors="coerce")
    bad = (v <= 0) | v.isna()
    g["voltage_kv"] = v.where(~bad, np.nan)
    note(f"transmission: {n0} features; {int(bad.sum())} with missing/sentinel "
         f"voltage set to null (source used -999999)")
    g["SUB_1_clean"] = g["SUB_1"].map(clean_token)
    g["SUB_2_clean"] = g["SUB_2"].map(clean_token)
    return g.to_crs(TX_ALBERS)


# --------------------------------------------------------------------------
# 2. Substations — real file if supplied, else derived proxy
# --------------------------------------------------------------------------
def find_real_substations():
    """Pick up a user-supplied substation file if one has been dropped in."""
    if not os.path.isdir(RAW):
        return None
    for fn in sorted(os.listdir(RAW)):
        low = fn.lower()
        if "substation" not in low:
            continue
        if low.endswith((".geojson", ".json", ".gpkg", ".shp", ".zip", ".csv")):
            return os.path.join(RAW, fn)
    return None


def load_real_substations(path):
    """Load a user-supplied substations file, mapping common field spellings."""
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
        loncol = next((c for c in df.columns if c.lower() in
                       ("longitude", "lon", "long", "x")), None)
        latcol = next((c for c in df.columns if c.lower() in
                       ("latitude", "lat", "y")), None)
        if not loncol or not latcol:
            raise ValueError(f"{path}: cannot find lat/lon columns")
        g = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df[loncol], df[latcol]), crs=WGS84)
    else:
        src = f"zip://{path}" if path.lower().endswith(".zip") else path
        g = gpd.read_file(src)
        if g.crs is None:
            g.set_crs(WGS84, inplace=True)

    cols = {c.lower(): c for c in g.columns}

    def pick(*names):
        for n in names:
            if n in cols:
                return cols[n]
        return None

    mx = pick("max_volt", "maxvolt", "max_voltage", "voltage", "max_kv")
    mn = pick("min_volt", "minvolt", "min_voltage", "min_kv")
    nm = pick("name", "sub_name", "substation", "id")
    st = pick("status")
    ln = pick("lines", "num_lines", "line_count")

    out = gpd.GeoDataFrame(geometry=g.geometry, crs=g.crs)
    out["sub_name"] = g[nm].map(clean_token) if nm else None
    for tgt, srccol in (("max_voltage_kv", mx), ("min_voltage_kv", mn)):
        if srccol:
            vals = pd.to_numeric(g[srccol], errors="coerce")
            out[tgt] = vals.where(vals > 0, np.nan)   # -999999 sentinels -> null
        else:
            out[tgt] = np.nan
    out["status"] = g[st].map(clean_token) if st else None
    out["n_lines"] = pd.to_numeric(g[ln], errors="coerce") if ln else np.nan
    out["is_proxy"] = False
    out["source_note"] = f"user-supplied file {os.path.basename(path)}"

    # Clip to Texas so distances are not driven by out-of-state features.
    tx = gpd.read_file(f"{RAW}/counties_tx.geojson").to_crs(TX_ALBERS)
    out = out.to_crs(TX_ALBERS)
    out = gpd.sjoin(out, tx[["geometry"]], predicate="intersects",
                    how="inner").drop(columns=["index_right"])
    return out.reset_index(drop=True)


def derive_proxy_substations(lines):
    """
    DERIVED LAYER — not a substation dataset.

    Transmission lines terminate at substations and switchyards, so the endpoint
    of a line is a strong positional indicator of one. This clusters every line
    endpoint within `proxy_cluster_tol_m` and treats each cluster as one node.

    Node attributes:
      max_voltage_kv  = highest voltage among lines terminating at the node
      n_line_ends     = how many line ends fall in the cluster
      sub_name        = names from the source SUB_1/SUB_2 fields, where present

    Known weaknesses, carried into METHOD.md:
      - A node is not confirmed to be a substation. Taps, splices and points
        where the source split one line into two segments also produce nodes.
      - Voltage is the line's voltage, NOT the substation's transformer rating.
        A substation's true max voltage is >= the highest line reaching it, so
        this under-reports where a high side exists but its line is unmapped.
      - 4,328 of the source lines are flagged INFERRED='Y' (geometry inferred),
        so their endpoints are correspondingly less certain.
    """
    ends = []
    for row in lines.itertuples():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        parts = list(geom.geoms) if geom.geom_type == "MultiLineString" else [geom]
        for part in parts:
            coords = list(part.coords)
            if len(coords) < 2:
                continue
            ends.append((Point(coords[0]), row.voltage_kv, row.SUB_1_clean,
                         row.INFERRED))
            ends.append((Point(coords[-1]), row.voltage_kv, row.SUB_2_clean,
                         row.INFERRED))

    ep = gpd.GeoDataFrame(
        {"voltage_kv": [e[1] for e in ends],
         "sub_name": [e[2] for e in ends],
         "inferred": [e[3] for e in ends]},
        geometry=[e[0] for e in ends], crs=TX_ALBERS)
    note(f"proxy substations: {len(ep)} line endpoints extracted from "
         f"{len(lines)} lines")

    # Cluster: buffer, dissolve, explode -> one polygon per cluster.
    tol = CONFIG["proxy_cluster_tol_m"]
    blobs = gpd.GeoDataFrame(
        geometry=list(ep.geometry.buffer(tol / 2.0).union_all().geoms),
        crs=TX_ALBERS).reset_index(names="cluster_id")
    ep = gpd.sjoin(ep, blobs, predicate="within",
                   how="left").drop(columns=["index_right"])

    agg = ep.groupby("cluster_id").agg(
        max_voltage_kv=("voltage_kv", "max"),
        min_voltage_kv=("voltage_kv", "min"),
        n_line_ends=("voltage_kv", "size"),
        n_inferred=("inferred", lambda s: int((s == "Y").sum())),
    )
    names = (ep.dropna(subset=["sub_name"]).groupby("cluster_id")["sub_name"]
               .agg(lambda s: "; ".join(sorted(set(s))[:3])))
    agg["sub_name"] = names
    # Node position = mean of its member endpoints.
    xy = ep.groupby("cluster_id").geometry.apply(
        lambda s: Point(s.x.mean(), s.y.mean()))

    subs = gpd.GeoDataFrame(agg.reset_index(), geometry=xy.values, crs=TX_ALBERS)
    subs["status"] = None
    subs["n_lines"] = subs["n_line_ends"]
    subs["is_proxy"] = True
    # A cluster holding a single line end is more likely an artefact of the
    # source splitting one line into segments, or a line clipped at the state
    # border, than a real substation. Two or more ends meeting is a much
    # stronger signal. Recorded as confidence, and used to gate Population 2.
    subs["proxy_confidence"] = np.where(
        (subs["n_line_ends"] >= 3) & subs["sub_name"].notna(), "high",
        np.where(subs["n_line_ends"] >= 2, "medium", "low"))
    subs["source_note"] = ("DERIVED from transmission line endpoints; not a "
                           "substation dataset")

    # Keep only nodes inside Texas.
    tx = gpd.read_file(f"{RAW}/counties_tx.geojson").to_crs(TX_ALBERS)
    before = len(subs)
    subs = gpd.sjoin(subs, tx[["geometry"]], predicate="intersects",
                     how="inner").drop(columns=["index_right"])
    note(f"proxy substations: {before} clusters -> {len(subs)} inside Texas "
         f"(tolerance {tol:.0f} m)")
    return subs.reset_index(drop=True)


# --------------------------------------------------------------------------
# 3. EIA retirement data -> Population 1
# --------------------------------------------------------------------------
def _read_zip_sheet(zpath, member, sheet, require):
    """
    Read a sheet out of an EIA zip, finding the header row by inspection.

    The header offset is NOT stable across releases: EIA-860 2024 puts the
    header on the second row (skiprows=1) while the 2025 early release puts it
    on the third (skiprows=2). Hardcoding either one silently yields a frame
    whose first data row has been consumed as column names, so the offset is
    detected by looking for columns we know must be present.
    """
    with zipfile.ZipFile(zpath).open(member) as fh:
        xl = pd.ExcelFile(fh)
        for skip in range(0, 6):
            probe = xl.parse(sheet, skiprows=skip, nrows=3)
            if all(c in probe.columns for c in require):
                return xl.parse(sheet, skiprows=skip)
    raise ValueError(
        f"{zpath}:{member}:{sheet} - no header row in the first 6 rows "
        f"contains all of {require}")


def load_eia_units():
    """
    Union of every Texas generating unit that has retired since `retired_since`
    or carries an announced retirement date, across all three EIA releases.

    Deduplicated on (plant_code, generator_id), preferring the most current
    release: 860M June 2026 > 860 2025ER > 860 2024 final.
    """
    frames = []

    # --- EIA-860M June 2026 (most current) ---
    xl = pd.ExcelFile(f"{RAW}/eia860m_june2026.xlsx")

    def sheet(name, require):
        for skip in range(0, 6):
            probe = xl.parse(name, skiprows=skip, nrows=3)
            if all(c in probe.columns for c in require):
                return xl.parse(name, skiprows=skip)
        raise ValueError(f"860M:{name} - no header row containing {require}")

    r = sheet("Retired", ["Plant ID", "Plant State", "Retirement Year"])
    r = r[r["Plant State"] == "TX"].copy()
    r["retire_year"] = pd.to_numeric(r["Retirement Year"], errors="coerce")
    r = r[r["retire_year"] >= CONFIG["retired_since"]]
    r["status_class"] = "retired"
    frames.append(_norm_860m(r, "EIA-860M 2026-06 Retired"))

    o = sheet("Operating", ["Plant ID", "Plant State", "Planned Retirement Year"])
    o = o[o["Plant State"] == "TX"].copy()
    o["retire_year"] = pd.to_numeric(o["Planned Retirement Year"], errors="coerce")
    o = o[o["retire_year"].notna()]
    o["status_class"] = "announced"
    frames.append(_norm_860m(o, "EIA-860M 2026-06 Operating (planned retirement)"))

    # --- EIA-860 annual releases ---
    for zpath, suffix, label in [
        (f"{RAW}/eia8602025ER.zip", "Y2025_Early_Release", "EIA-860 2025ER"),
        (f"{RAW}/eia8602024.zip", "Y2024", "EIA-860 2024 final"),
    ]:
        gen_member = f"3_1_Generator_{suffix}.xlsx"
        plant_member = f"2___Plant_{suffix}.xlsx"
        plant = _read_zip_sheet(zpath, plant_member, "Plant",
                                ["Plant Code", "Latitude", "Longitude"])
        coords = plant[["Plant Code", "Latitude", "Longitude", "County",
                        "Plant Name"]].copy()

        ret = _read_zip_sheet(zpath, gen_member, "Retired and Canceled",
                              ["Plant Code", "Status", "Retirement Year"])
        ret = ret[(ret["State"] == "TX") & (ret["Status"] == "RE")].copy()
        ret["retire_year"] = pd.to_numeric(ret["Retirement Year"], errors="coerce")
        ret = ret[ret["retire_year"] >= CONFIG["retired_since"]]
        ret["status_class"] = "retired"
        frames.append(_norm_860(ret, coords, f"{label} Retired"))

        op = _read_zip_sheet(zpath, gen_member, "Operable",
                             ["Plant Code", "Planned Retirement Year"])
        op = op[op["State"] == "TX"].copy()
        op["retire_year"] = pd.to_numeric(op["Planned Retirement Year"],
                                          errors="coerce")
        op = op[op["retire_year"].notna()]
        op["status_class"] = "announced"
        frames.append(_norm_860(op, coords, f"{label} Operable (planned)"))

    units = pd.concat(frames, ignore_index=True)
    units["generator_id"] = units["generator_id"].astype(str).str.strip()
    before = len(units)
    units = units.drop_duplicates(subset=["plant_code", "generator_id"],
                                  keep="first")
    note(f"EIA units: {before} rows across releases -> {len(units)} unique "
         f"(plant, generator) after dedup, preferring most current release")

    missing = units["latitude"].isna() | units["longitude"].isna()
    if missing.any():
        note(f"WARNING: {int(missing.sum())} units lack coordinates and are "
             f"dropped: {sorted(units.loc[missing,'plant_name'].unique())[:10]}")
        units = units[~missing]
    return units


def _norm_860m(df, src):
    return pd.DataFrame({
        "plant_code": pd.to_numeric(df["Plant ID"], errors="coerce"),
        "plant_name": df["Plant Name"],
        "generator_id": df["Generator ID"],
        "county_eia": df["County"],
        "latitude": pd.to_numeric(df["Latitude"], errors="coerce"),
        "longitude": pd.to_numeric(df["Longitude"], errors="coerce"),
        "nameplate_mw": pd.to_numeric(df["Nameplate Capacity (MW)"],
                                      errors="coerce"),
        "technology": df["Technology"],
        "retire_year": df["retire_year"],
        "status_class": df["status_class"],
        "source": src,
    })


def _norm_860(df, coords, src):
    m = df.merge(coords, on="Plant Code", how="left", suffixes=("", "_p"))
    return pd.DataFrame({
        "plant_code": pd.to_numeric(m["Plant Code"], errors="coerce"),
        "plant_name": m["Plant Name"],
        "generator_id": m["Generator ID"],
        "county_eia": m["County"],
        "latitude": pd.to_numeric(m["Latitude"], errors="coerce"),
        "longitude": pd.to_numeric(m["Longitude"], errors="coerce"),
        "nameplate_mw": pd.to_numeric(m["Nameplate Capacity (MW)"],
                                      errors="coerce"),
        "technology": m["Technology"],
        "retire_year": m["retire_year"],
        "status_class": m["status_class"],
        "source": src,
    })


def build_population1(units):
    """Aggregate units to plant level and keep plants over the MW threshold."""
    g = units.groupby("plant_code")
    agg = pd.DataFrame({
        "plant_name": g["plant_name"].first(),
        "county_eia": g["county_eia"].first(),
        "latitude": g["latitude"].first(),
        "longitude": g["longitude"].first(),
        "retired_mw": g.apply(
            lambda d: d.loc[d.status_class == "retired", "nameplate_mw"].sum(),
            include_groups=False),
        "announced_mw": g.apply(
            lambda d: d.loc[d.status_class == "announced", "nameplate_mw"].sum(),
            include_groups=False),
        "n_units": g.size(),
        "latest_retire_year": g["retire_year"].max(),
        "earliest_retire_year": g["retire_year"].min(),
        "technologies": g["technology"].agg(
            lambda s: "; ".join(sorted({str(x) for x in s.dropna()})[:4])),
        "eia_sources": g["source"].agg(lambda s: "; ".join(sorted(set(s)))),
    }).reset_index()

    agg["site_mw"] = agg["retired_mw"] + agg["announced_mw"]
    keep = agg[agg["site_mw"] >= CONFIG["min_site_mw"]].copy()
    note(f"Population 1: {len(agg)} TX plants with retired/announced capacity; "
         f"{len(keep)} at or above {CONFIG['min_site_mw']:.0f} MW")

    keep["years_since_retirement"] = (
        CONFIG["screen_year"] - keep["latest_retire_year"])

    # Flag sites whose only retirement signal is decades away.
    horizon = CONFIG["screen_year"] + CONFIG["announced_horizon_years"]
    keep["retirement_beyond_horizon"] = (
        (keep["retired_mw"] <= 0) & (keep["latest_retire_year"] > horizon))
    n_far = int(keep["retirement_beyond_horizon"].sum())
    if n_far:
        far = keep.loc[keep["retirement_beyond_horizon"],
                       ["plant_name", "latest_retire_year"]]
        note(f"NOTE: {n_far} site(s) have no past retirement and an announced "
             f"retirement after {horizon} - operating today, not acquirable: "
             + "; ".join(f"{r.plant_name} ({int(r.latest_retire_year)})"
                         for r in far.itertuples()))
        if CONFIG["announced_horizon_drop"]:
            keep = keep[~keep["retirement_beyond_horizon"]]
            note(f"  dropped (announced_horizon_drop=True) -> {len(keep)} sites")

    keep["population"] = 1
    keep["site_name"] = keep["plant_name"]
    return gpd.GeoDataFrame(
        keep,
        geometry=gpd.points_from_xy(keep["longitude"], keep["latitude"]),
        crs=WGS84).to_crs(TX_ALBERS).reset_index(drop=True)


def build_population2(subs, pop1):
    """Substations >= threshold kV that are not adjacent to a Population 1 site."""
    hv = subs[subs["max_voltage_kv"] >= CONFIG["pop2_min_kv"]].copy()
    if bool(subs["is_proxy"].iloc[0]):
        before = len(hv)
        hv = hv[hv["proxy_confidence"].isin(["high", "medium"])]
        note(f"Population 2: dropped {before - len(hv)} low-confidence proxy "
             f"nodes holding a single line end (likely segment splits, not "
             f"substations)")
    near = gpd.sjoin_nearest(
        hv, pop1[["geometry"]], how="left", distance_col="_d")
    near = near.groupby(near.index)["_d"].min()
    hv["_dist_to_pop1"] = near
    out = hv[hv["_dist_to_pop1"] > CONFIG["pop2_exclude_within_m"]].copy()
    note(f"Population 2: {len(subs)} substation nodes -> {len(hv)} at or above "
         f"{CONFIG['pop2_min_kv']:.0f} kV -> {len(out)} beyond "
         f"{CONFIG['pop2_exclude_within_m']:.0f} m from a Population 1 site")

    out = out.rename(columns={"sub_name": "site_name"})
    out["site_name"] = out["site_name"].fillna("Unnamed node")
    out["plant_code"] = np.nan
    out["plant_name"] = None
    out["retired_mw"] = 0.0
    out["announced_mw"] = 0.0
    out["site_mw"] = 0.0
    out["n_units"] = 0
    out["latest_retire_year"] = np.nan
    out["years_since_retirement"] = np.nan
    out["technologies"] = None
    out["eia_sources"] = None
    out["county_eia"] = None
    out["retirement_beyond_horizon"] = False
    out["population"] = 2
    return out.drop(columns=["_dist_to_pop1"]).reset_index(drop=True)


# --------------------------------------------------------------------------
# 4. Spatial metrics
# --------------------------------------------------------------------------
def compute_metrics(cand, subs, lines, water, counties):
    r = CONFIG["search_radius_m"]

    # --- nearest substation ---
    n = gpd.sjoin_nearest(
        cand[["geometry"]], subs[["geometry", "max_voltage_kv", "sub_name"]],
        how="left", distance_col="dist_substation_m")
    n = n[~n.index.duplicated(keep="first")]
    cand["dist_substation_m"] = n["dist_substation_m"].round(1)
    cand["nearest_substation_kv"] = n["max_voltage_kv"]
    cand["nearest_substation_name"] = n["sub_name"]

    # --- substations within radius ---
    buf = gpd.GeoDataFrame(geometry=cand.geometry.buffer(r), crs=TX_ALBERS)
    j = gpd.sjoin(subs[["geometry", "max_voltage_kv"]], buf,
                  predicate="within", how="inner")
    cand["substations_within_5km"] = (
        j.groupby("index_right").size().reindex(cand.index).fillna(0).astype(int))
    cand["max_substation_kv_within_5km"] = (
        j.groupby("index_right")["max_voltage_kv"].max().reindex(cand.index))

    # --- nearest transmission line ---
    ln = gpd.sjoin_nearest(
        cand[["geometry"]], lines[["geometry", "voltage_kv", "OWNER"]],
        how="left", distance_col="dist_line_m")
    ln = ln[~ln.index.duplicated(keep="first")]
    cand["dist_transmission_m"] = ln["dist_line_m"].round(1)
    cand["nearest_line_kv"] = ln["voltage_kv"]
    cand["nearest_line_owner"] = ln["OWNER"].map(clean_token)

    # --- lines within radius, by voltage class ---
    jl = gpd.sjoin(lines[["geometry", "voltage_kv"]], buf,
                   predicate="intersects", how="inner")
    cand["lines_within_5km"] = (
        jl.groupby("index_right").size().reindex(cand.index).fillna(0).astype(int))

    def vclass(v):
        if pd.isna(v):
            return "unknown"
        if v >= 345:
            return "345kV_plus"
        if v >= 230:
            return "230_344kV"
        if v >= 138:
            return "138_229kV"
        if v >= 69:
            return "69_137kV"
        return "under_69kV"

    jl = jl.assign(vc=jl["voltage_kv"].map(vclass))
    pivot = (jl.groupby(["index_right", "vc"]).size().unstack(fill_value=0)
               .reindex(cand.index).fillna(0).astype(int))
    for col in ["345kV_plus", "230_344kV", "138_229kV", "69_137kV",
                "under_69kV", "unknown"]:
        cand[f"lines_5km_{col}"] = pivot[col] if col in pivot.columns else 0

    # --- best transmission opportunity within 10 km ---
    buf10 = gpd.GeoDataFrame(geometry=cand.geometry.buffer(10000), crs=TX_ALBERS)
    j10 = gpd.sjoin(lines[["geometry", "voltage_kv"]], buf10,
                    predicate="intersects", how="inner")
    if len(j10):
        # Element-wise line-to-candidate distance for each joined pair.
        pos = cand.index.get_indexer(j10["index_right"].to_numpy())
        d = shapely.distance(np.asarray(j10.geometry.values),
                             np.asarray(cand.geometry.values)[pos])
        j10 = j10.assign(_d=d)
        j10["_score"] = j10.apply(
            lambda row: CONFIG["weights"]["transmission"]
            * band_score_below(row["_d"], CONFIG["tx_dist_factor"], 0.0)
            * band_score(row["voltage_kv"], CONFIG["tx_volt_factor"],
                         CONFIG["tx_volt_factor_floor"]), axis=1)
        best = j10.groupby("index_right").agg(
            _s=("_score", "max"), _kv=("voltage_kv", "max"))
        cand["score_transmission"] = best["_s"].reindex(cand.index).fillna(0.0)
        cand["max_line_kv_within_10km"] = best["_kv"].reindex(cand.index)
    else:
        cand["score_transmission"] = 0.0
        cand["max_line_kv_within_10km"] = np.nan

    # --- county by spatial join (independent of EIA's own county field) ---
    cj = gpd.sjoin(cand[["geometry"]], counties[["geometry", "NAME"]],
                   predicate="within", how="left")
    cj = cj[~cj.index.duplicated(keep="first")]
    cand["county"] = cj["NAME"]

    # --- water ---
    if water is not None and len(water):
        w = gpd.sjoin_nearest(cand[["geometry"]], water[["geometry"]],
                              how="left", distance_col="dist_water_m")
        w = w[~w.index.duplicated(keep="first")]
        cand["dist_water_m"] = w["dist_water_m"].round(1)
    else:
        cand["dist_water_m"] = np.nan

    # --- broadband: FCC unavailable, column kept explicitly null ---
    cand["broadband_providers"] = np.nan
    cand["broadband_note"] = "FCC BDC unreachable (egress policy) - not scored"
    return cand


# --------------------------------------------------------------------------
# 5. Scoring
# --------------------------------------------------------------------------
def score(cand, have_broadband, have_water, subs_are_proxy):
    W = CONFIG["weights"]

    # Interconnection, with the stale-rights multiplier.
    raw = cand["site_mw"].map(lambda mw: band_score(mw, CONFIG["interconnection_bands"]))
    stale = cand["years_since_retirement"] > CONFIG["stale_interconnect_years"]
    cand["interconnection_stale_flag"] = stale.fillna(False)
    cand["score_interconnection"] = np.where(
        cand["interconnection_stale_flag"], raw * CONFIG["stale_multiplier"], raw)

    cand["score_substation_prox"] = cand["dist_substation_m"].map(
        lambda d: band_score_below(d, CONFIG["sub_prox_bands"]))

    volt_for_score = cand["max_substation_kv_within_5km"].fillna(
        cand["nearest_substation_kv"])
    cand["score_substation_volt"] = volt_for_score.map(
        lambda v: band_score(v, CONFIG["sub_volt_bands"]))

    if have_broadband:
        cand["score_broadband"] = cand["broadband_providers"].map(
            lambda n: band_score(n, CONFIG["broadband_bands"]))
    else:
        cand["score_broadband"] = 0.0

    if have_water:
        cand["score_water"] = cand["dist_water_m"].map(
            lambda d: band_score_below(d, CONFIG["water_bands"]))
    else:
        cand["score_water"] = 0.0

    available = ["interconnection", "substation_prox", "substation_volt",
                 "transmission"]
    if have_broadband:
        available.append("broadband")
    if have_water:
        available.append("water")

    denom = sum(W[k] for k in available)
    parts = [f"score_{k}" for k in available]
    cand["score_raw"] = cand[parts].sum(axis=1)
    cand["score_max_available"] = denom
    cand["score"] = (cand["score_raw"] / denom * 100).round(1)
    cand["score_basis"] = (
        f"rescaled from {denom} available points to 0-100; "
        f"excluded: {', '.join(k for k in W if k not in available) or 'none'}"
        + ("; substation factors use DERIVED proxy nodes" if subs_are_proxy else ""))
    note(f"scoring: {denom} of {sum(W.values())} rubric points available, "
         f"rescaled to 0-100. Excluded factors: "
         f"{[k for k in W if k not in available] or 'none'}")
    return cand.sort_values("score", ascending=False).reset_index(drop=True)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    lines = load_transmission()
    counties = gpd.read_file(f"{RAW}/counties_tx.geojson").to_crs(TX_ALBERS)

    real = find_real_substations()
    if real:
        subs = load_real_substations(real)
        subs_are_proxy = False
        note(f"substations: using REAL user-supplied file {real} "
             f"({len(subs)} features in Texas)")
    else:
        subs = derive_proxy_substations(lines)
        subs_are_proxy = True
        REPORT["failures"].append(
            "Electric substations (dataset A): no source reachable; using "
            "DERIVED proxy nodes from transmission line endpoints.")

    # Water
    water = None
    try:
        res = gpd.read_file(
            f"zip://{RAW}/twdb_Existing_Reservoirs.zip").to_crs(TX_ALBERS)
        riv = gpd.read_file(
            f"zip://{RAW}/twdb_Major_Rivers_dd83.zip").to_crs(TX_ALBERS)
        water = gpd.GeoDataFrame(
            geometry=pd.concat([res.geometry, riv.geometry], ignore_index=True),
            crs=TX_ALBERS)
        note(f"water: {len(res)} reservoirs + {len(riv)} major river features")
    except Exception as e:  # noqa: BLE001
        REPORT["failures"].append(f"TWDB water layers failed to load: {e}")
        note(f"WARNING: water layer failed: {e}")

    units = load_eia_units()
    pop1 = build_population1(units)
    pop2 = build_population2(subs, pop1)

    keep_cols = ["site_name", "plant_code", "plant_name", "county_eia",
                 "retired_mw", "announced_mw", "site_mw", "n_units",
                 "latest_retire_year", "years_since_retirement",
                 "retirement_beyond_horizon", "technologies",
                 "eia_sources", "population", "geometry"]
    cand = gpd.GeoDataFrame(
        pd.concat([pop1[keep_cols], pop2[keep_cols]], ignore_index=True),
        crs=TX_ALBERS)
    note(f"candidates: {len(pop1)} Population 1 + {len(pop2)} Population 2 "
         f"= {len(cand)} total")

    cand = compute_metrics(cand, subs, lines, water, counties)
    cand = score(cand, have_broadband=False, have_water=water is not None,
                 subs_are_proxy=subs_are_proxy)

    cand["latitude"] = cand.to_crs(WGS84).geometry.y.round(6)
    cand["longitude"] = cand.to_crs(WGS84).geometry.x.round(6)
    cand["google_maps_url"] = (
        "https://www.google.com/maps?q=" + cand["latitude"].astype(str)
        + "," + cand["longitude"].astype(str))
    cand["county_cad_note"] = ""
    cand["substation_data_is_proxy"] = subs_are_proxy
    cand.insert(0, "rank", np.arange(1, len(cand) + 1))

    write_outputs(cand, subs, lines, counties, water, subs_are_proxy)
    return cand, subs, lines


def write_outputs(cand, subs, lines, counties, water, subs_are_proxy):
    gpkg = f"{OUT}/tx_candidates.gpkg"
    if os.path.exists(gpkg):
        os.remove(gpkg)
    cand.to_file(gpkg, layer="candidates", driver="GPKG")
    subs.to_file(gpkg, layer="substations_proxy" if subs_are_proxy
                 else "substations", driver="GPKG")
    lines.to_file(gpkg, layer="transmission_lines", driver="GPKG")
    counties.to_file(gpkg, layer="counties", driver="GPKG")
    if water is not None:
        water.to_file(gpkg, layer="water", driver="GPKG")
    note(f"wrote {gpkg}")

    top = cand.head(CONFIG["top_n"]).drop(columns=["geometry"])
    top.to_csv(f"{OUT}/top{CONFIG['top_n']}_candidates.csv", index=False)
    note(f"wrote {OUT}/top{CONFIG['top_n']}_candidates.csv ({len(top)} rows)")

    # County summary. Population 1 and 2 are broken out on purpose: sorting the
    # combined set by mean score puts counties holding nothing but proxy nodes
    # (0 MW, identical scores) above counties with GW of real retired capacity,
    # which is the opposite of useful for deciding who to call.
    flat = cand.drop(columns=["geometry"])
    cs = (flat.groupby("county")
          .agg(candidates=("rank", "size"),
               total_retired_mw=("retired_mw", "sum"),
               total_announced_mw=("announced_mw", "sum"),
               mean_score=("score", "mean"),
               max_score=("score", "max")))
    p1 = flat[flat["population"] == 1].groupby("county")
    cs["pop1_candidates"] = p1.size().reindex(cs.index).fillna(0).astype(int)
    cs["pop1_mean_score"] = p1["score"].mean().reindex(cs.index).round(2)
    cs["pop1_best_site"] = (
        p1.apply(lambda d: d.loc[d["score"].idxmax(), "site_name"],
                 include_groups=False).reindex(cs.index))
    cs["total_site_mw"] = cs["total_retired_mw"] + cs["total_announced_mw"]
    cs["pop2_candidates"] = cs["candidates"] - cs["pop1_candidates"]

    cs = (cs.reset_index()[
        ["county", "pop1_candidates", "total_retired_mw", "total_announced_mw",
         "total_site_mw", "pop1_mean_score", "pop1_best_site", "max_score",
         "pop2_candidates", "candidates", "mean_score"]]
        .round(2)
        .sort_values(["pop1_candidates", "total_site_mw"], ascending=False))
    cs.to_csv(f"{OUT}/COUNTY_SUMMARY.csv", index=False)
    note(f"wrote {OUT}/COUNTY_SUMMARY.csv ({len(cs)} counties; "
         f"{int((cs['pop1_candidates']>0).sum())} contain a retired/retiring "
         f"plant, sorted so those come first)")

    with open(f"{OUT}/_run_report.json", "w") as fh:
        json.dump(REPORT, fh, indent=2)


if __name__ == "__main__":
    main()
