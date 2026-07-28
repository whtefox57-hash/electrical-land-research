"""
Dataset readers.

Every loader in this module obeys the same contract:

  * It reads a file that exists on disk. It never invents one.
  * Column names are resolved by fuzzy matching against known aliases, because
    HIFLD and EIA rename fields between vintages. If a REQUIRED field cannot be
    resolved, the loader raises MissingField with the columns it actually saw.
    It does not fall back to a default value.
  * Sentinel values (-999999 and friends) are converted to NaN, never treated
    as real measurements.
  * Every returned frame carries a `_source_file` column for provenance.
"""

from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import GEOGRAPHIC_CRS, NULL_SENTINELS, RAW, TX_BBOX, VOLTAGE_CLASSES  # noqa: E402


class MissingField(RuntimeError):
    """A required source field could not be located. Never silently defaulted."""


class MissingSource(RuntimeError):
    """A required source file is absent. Downstream steps must not proceed."""


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def pick(df: pd.DataFrame, aliases: list[str], *, required: bool = True,
         label: str = "") -> str | None:
    """Resolve a column by normalised alias match (exact first, then prefix)."""
    norm_map = {_norm(c): c for c in df.columns}
    for a in aliases:
        if (na := _norm(a)) in norm_map:
            return norm_map[na]
    for a in aliases:
        na = _norm(a)
        for nc, orig in norm_map.items():
            if nc.startswith(na) or na in nc:
                return orig
    if required:
        raise MissingField(
            f"could not resolve {label or aliases[0]!r}: tried {aliases}; "
            f"available columns = {list(df.columns)[:60]}"
        )
    return None


def denull(s: pd.Series) -> pd.Series:
    """Numeric coercion with sentinel removal. Sentinels become NaN."""
    out = pd.to_numeric(s, errors="coerce")
    return out.mask(out.isin(NULL_SENTINELS)).mask(out <= -9000)


def clip_to_texas(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    xmin, ymin, xmax, ymax = TX_BBOX
    if gdf.crs is None:
        raise MissingField("layer has no CRS; refusing to guess")
    g = gdf.to_crs(GEOGRAPHIC_CRS)
    return g.cx[xmin:xmax, ymin:ymax].copy()


def _read_any_vector(path: Path) -> gpd.GeoDataFrame:
    """Read geojson / gpkg / shapefile-in-zip."""
    if path.suffix.lower() == ".zip":
        return gpd.read_file(f"zip://{path}")
    return gpd.read_file(path)


def _find(patterns: list[str]) -> list[Path]:
    hits: list[Path] = []
    for p in patterns:
        hits.extend(sorted(RAW.glob(p)))
    return sorted(set(hits))


def voltage_class(kv: float) -> str:
    if pd.isna(kv):
        return "unknown"
    for name, lo, hi in VOLTAGE_CLASSES:
        if lo <= kv < hi:
            return name
    return "unknown"


# --------------------------------------------------------------------------
# A. substations
# --------------------------------------------------------------------------
SUBSTATION_FILES = ["substations_tx.geojson", "*ubstation*.geojson",
                    "*ubstation*.gpkg", "*ubstation*.zip"]


def load_substations(path: Path | None = None) -> gpd.GeoDataFrame:
    hits = [path] if path else _find(SUBSTATION_FILES)
    if not hits:
        raise MissingSource(
            "SOURCE A (substations) not present in data/raw/. "
            "See DATA_ACQUISITION.md section A."
        )
    src = hits[0]
    g = clip_to_texas(_read_any_vector(src))

    c_name = pick(g, ["NAME", "SUB_NAME", "station_name"], label="substation name")
    c_max = pick(g, ["MAX_VOLT", "MAXVOLT", "max_voltage", "MAX_KV"],
                 label="max voltage")
    c_min = pick(g, ["MIN_VOLT", "MINVOLT", "min_voltage", "MIN_KV"],
                 required=False)
    c_lines = pick(g, ["LINES", "NUM_LINES", "line_count"], required=False)
    c_status = pick(g, ["STATUS", "STATE_STATUS", "OP_STATUS"], required=False)
    c_county = pick(g, ["COUNTY", "COUNTYNAME", "CNTY"], required=False)

    out = gpd.GeoDataFrame(
        {
            "sub_name": g[c_name].astype("string"),
            "sub_max_kv": denull(g[c_max]),
            "sub_min_kv": denull(g[c_min]) if c_min else np.nan,
            "sub_lines": denull(g[c_lines]) if c_lines else np.nan,
            "sub_status": g[c_status].astype("string") if c_status else pd.NA,
            "sub_county_attr": g[c_county].astype("string") if c_county else pd.NA,
        },
        geometry=g.geometry.values,
        crs=g.crs,
    )
    # Substations are represented as points for distance work. Polygon inputs
    # are collapsed to representative points (recorded as derived in METHOD).
    if not (out.geometry.geom_type == "Point").all():
        out["geometry"] = out.geometry.representative_point()
    out["_source_file"] = src.name
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------
# B. transmission lines
# --------------------------------------------------------------------------
TRANSMISSION_FILES = ["transmission_tx.geojson", "*ransmission*.geojson",
                      "*ransmission*.gpkg", "*ransmission*.zip"]


def load_transmission(path: Path | None = None) -> gpd.GeoDataFrame:
    hits = [path] if path else _find(TRANSMISSION_FILES)
    if not hits:
        raise MissingSource(
            "SOURCE B (transmission lines) not present in data/raw/. "
            "See DATA_ACQUISITION.md section B."
        )
    src = hits[0]
    g = clip_to_texas(_read_any_vector(src))

    c_volt = pick(g, ["VOLTAGE", "VOLT_KV", "kv"], label="line voltage")
    c_class = pick(g, ["VOLT_CLASS", "VOLTAGE_CLASS"], required=False)
    c_owner = pick(g, ["OWNER", "OWNER_NAME", "OPERATOR"], required=False)
    c_status = pick(g, ["STATUS", "OP_STATUS"], required=False)

    kv = denull(g[c_volt])
    out = gpd.GeoDataFrame(
        {
            "line_kv": kv,
            "line_volt_class_src": g[c_class].astype("string") if c_class else pd.NA,
            "line_volt_class": [voltage_class(v) for v in kv],
            "line_owner": g[c_owner].astype("string") if c_owner else pd.NA,
            "line_status": g[c_status].astype("string") if c_status else pd.NA,
        },
        geometry=g.geometry.values,
        crs=g.crs,
    )
    out["_source_file"] = src.name
    return out.reset_index(drop=True)


# --------------------------------------------------------------------------
# C. EIA generators -- the important one
# --------------------------------------------------------------------------
GEN_ALIASES = {
    "plant_code": ["Plant Code", "Plant ID", "PlantCode", "EIA Plant Code"],
    "plant_name": ["Plant Name", "PlantName"],
    "generator_id": ["Generator ID", "GeneratorID", "Unit ID"],
    "state": ["State", "Plant State"],
    "county": ["County"],
    "capacity_mw": ["Nameplate Capacity (MW)", "Nameplate Capacity",
                    "Net Summer Capacity (MW)", "Capacity (MW)"],
    "status": ["Status", "Operating Status"],
    "technology": ["Technology", "Prime Mover", "Energy Source 1", "Energy Source"],
    "retire_year": ["Retirement Year", "Retired Year"],
    "retire_month": ["Retirement Month", "Retired Month"],
    "planned_retire_year": ["Planned Retirement Year"],
    "planned_retire_month": ["Planned Retirement Month"],
    "latitude": ["Latitude", "Lat"],
    "longitude": ["Longitude", "Lon", "Long"],
}

# EIA workbooks put 1-3 rows of notes above the real header.
def _read_excel_smart(path: Path, sheet: str) -> pd.DataFrame:
    last_err = None
    for skip in range(0, 6):
        try:
            df = pd.read_excel(path, sheet_name=sheet, skiprows=skip)
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
        cols = {_norm(c) for c in df.columns}
        if {"plantcode"} & cols or {"plantid"} & cols or {"plantname"} & cols:
            return df
    if last_err:
        raise MissingField(f"{path.name}:{sheet} unreadable: {last_err}")
    raise MissingField(
        f"{path.name}:{sheet} -- no header row containing Plant Code/ID found "
        f"in the first 6 rows"
    )


def _harvest(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Pull the fields we need from one generator sheet, tolerating absences."""
    rec: dict[str, pd.Series] = {}
    for key, aliases in GEN_ALIASES.items():
        required = key in ("plant_code", "capacity_mw")
        col = pick(df, aliases, required=required, label=key)
        rec[key] = df[col] if col is not None else pd.Series(pd.NA, index=df.index)
    out = pd.DataFrame(rec)
    for c in ("plant_code", "capacity_mw", "retire_year", "retire_month",
              "planned_retire_year", "planned_retire_month", "latitude",
              "longitude"):
        out[c] = denull(out[c])
    out["_sheet"] = source
    return out


def load_eia_generators() -> pd.DataFrame:
    """Union of EIA-860 annual and EIA-860M monthly generator records."""
    gen_files = _find(["*Generator*.xlsx", "*generator*.xlsx"])
    if not gen_files:
        raise MissingSource(
            "SOURCE C (EIA generators) not present in data/raw/. This is the "
            "single most important dataset for this screen -- the pipeline "
            "cannot produce Population 1 without it. "
            "See DATA_ACQUISITION.md section C."
        )

    frames: list[pd.DataFrame] = []
    for f in gen_files:
        try:
            sheets = pd.ExcelFile(f).sheet_names
        except Exception as exc:  # noqa: BLE001
            raise MissingField(f"cannot open {f.name}: {exc}") from exc
        for sh in sheets:
            low = sh.lower()
            if not any(k in low for k in
                       ("operable", "operating", "retired", "planned",
                        "proposed", "canceled")):
                continue
            try:
                df = _read_excel_smart(f, sh)
            except MissingField:
                continue
            frames.append(_harvest(df, f"{f.name}::{sh}"))

    if not frames:
        raise MissingField(
            f"found {[f.name for f in gen_files]} but no sheet yielded a "
            f"readable generator table"
        )

    gens = pd.concat(frames, ignore_index=True)
    gens = gens[gens["plant_code"].notna()]

    # Texas only. Prefer the explicit state field; fall back to nothing (we do
    # NOT guess state from coordinates here -- coordinates come from the Plant
    # file join, which happens later).
    st = gens["state"].astype("string").str.strip().str.upper()
    gens = gens[st.isin(["TX", "TEXAS"]) | st.isna()].copy()

    # 860M is more current than 860 on planned retirements: when the same
    # (plant, generator) appears in both, keep the record from the file whose
    # name looks monthly.
    gens["_is_860m"] = gens["_sheet"].str.contains(
        r"_generator\d{4}", case=False, regex=True
    )
    gens = (
        gens.sort_values("_is_860m", ascending=False)
        .drop_duplicates(subset=["plant_code", "generator_id"], keep="first")
        .reset_index(drop=True)
    )
    return gens


PLANT_ALIASES = {
    "plant_code": ["Plant Code", "Plant ID"],
    "plant_name": ["Plant Name"],
    "state": ["State", "Plant State"],
    "county": ["County"],
    "latitude": ["Latitude"],
    "longitude": ["Longitude"],
}


def load_eia_plants() -> pd.DataFrame:
    """Plant-level coordinates. The 860 Generator file has no lat/lon."""
    files = [f for f in _find(["*Plant*.xlsx", "*plant*.xlsx"])
             if "generator" not in f.name.lower()]
    frames = []
    for f in files:
        for sh in pd.ExcelFile(f).sheet_names:
            try:
                df = _read_excel_smart(f, sh)
            except MissingField:
                continue
            rec = {}
            ok = True
            for key, aliases in PLANT_ALIASES.items():
                col = pick(df, aliases, required=False)
                if col is None and key in ("plant_code", "latitude", "longitude"):
                    ok = False
                    break
                rec[key] = df[col] if col is not None else pd.Series(
                    pd.NA, index=df.index)
            if not ok:
                continue
            p = pd.DataFrame(rec)
            for c in ("plant_code", "latitude", "longitude"):
                p[c] = denull(p[c])
            p["_source_file"] = f.name
            frames.append(p)
    if not frames:
        return pd.DataFrame(
            columns=list(PLANT_ALIASES) + ["_source_file"]
        )
    plants = pd.concat(frames, ignore_index=True)
    plants = plants[plants["plant_code"].notna()]
    return plants.drop_duplicates(subset=["plant_code"], keep="first")


# --------------------------------------------------------------------------
# D. broadband proxy
# --------------------------------------------------------------------------
def load_broadband() -> pd.DataFrame | None:
    files = _find(["*bdc*.csv", "*broadband*.csv", "*bdc*.json"])
    if not files:
        return None
    src = files[0]
    df = pd.read_json(src) if src.suffix == ".json" else pd.read_csv(
        src, dtype=str, low_memory=False)
    geo = pick(df, ["block_geoid", "geoid", "census_block_geoid", "block_fips"],
               label="block geoid")
    cnt = pick(df, ["provider_count", "providers", "num_providers",
                    "provider_id_count"], required=False)
    out = pd.DataFrame({"block_geoid": df[geo].astype(str).str.zfill(15)})
    if cnt is not None:
        out["provider_count"] = pd.to_numeric(df[cnt], errors="coerce")
    else:
        prov = pick(df, ["provider_id", "frn", "brand_name"], label="provider id")
        out["provider_id"] = df[prov].astype(str)
        out = (out.groupby("block_geoid")["provider_id"].nunique()
               .reset_index(name="provider_count"))
    # Aggregate block -> block group (first 12 digits of the 15-digit block id)
    out["bg_geoid"] = out["block_geoid"].str[:12]
    bg = (out.groupby("bg_geoid")["provider_count"].max()
          .reset_index(name="broadband_providers"))
    bg["_source_file"] = src.name
    return bg


def load_block_groups() -> gpd.GeoDataFrame | None:
    files = _find(["*bg*.zip", "*blockgroup*.zip", "tl_*_48_bg*.zip"])
    for f in files:
        try:
            g = clip_to_texas(_read_any_vector(f))
        except Exception:  # noqa: BLE001
            continue
        col = pick(g, ["GEOID", "GEOID20", "GEOID10"], required=False)
        if col is None:
            continue
        g = g[[col, "geometry"]].rename(columns={col: "bg_geoid"})
        g["bg_geoid"] = g["bg_geoid"].astype(str)
        return g
    return None


# --------------------------------------------------------------------------
# E. water (optional)
# --------------------------------------------------------------------------
def load_water() -> gpd.GeoDataFrame | None:
    files = _find(["*eservoir*.zip", "*eservoir*.shp", "*water*.zip",
                   "*river*.zip", "*GCD*.zip"])
    frames = []
    for f in files:
        try:
            g = clip_to_texas(_read_any_vector(f))
        except Exception:  # noqa: BLE001
            continue
        if g.empty:
            continue
        frames.append(gpd.GeoDataFrame(
            {"water_source": f.name}, geometry=g.geometry.values, crs=g.crs))
    if not frames:
        return None
    return gpd.GeoDataFrame(pd.concat(frames, ignore_index=True),
                            crs=frames[0].crs)


# --------------------------------------------------------------------------
# counties
# --------------------------------------------------------------------------
def load_counties() -> gpd.GeoDataFrame | None:
    files = _find(["*county*.zip", "*counties*.zip", "tl_*_us_county*.zip",
                   "*county*.geojson"])
    for f in files:
        try:
            g = clip_to_texas(_read_any_vector(f))
        except Exception:  # noqa: BLE001
            continue
        name = pick(g, ["NAME", "NAMELSAD", "CNTY_NM"], required=False)
        if name is None:
            continue
        return gpd.GeoDataFrame({"county_name": g[name].astype(str)},
                                geometry=g.geometry.values, crs=g.crs)
    return None
