"""STEP 3 — power data.

  A. Substations          HIFLD national substations, Arizona
  B. Transmission lines   HIFLD national transmission, Arizona
  C. Plants/retirements   EIA-860 annual + EIA-860M monthly
  D. Utility territories  HIFLD Electric Retail Service Territories + type

Provenance warning carried into the outputs: hifld-geoplatform.opendata.
arcgis.com is SUNSET. The substation layer used here is a third-party
republication of the HIFLD schema, not a federal endpoint. Transmission lines
come from the Federal_User_Community org named in the brief. Both are recorded
with their exact URLs so the user can judge them.

Voltage sentinels: HIFLD uses -999999 for unknown voltage. Those are nulled,
never treated as numbers. MAX_INFER / MIN_INFER are HIFLD's own flags saying
the voltage was inferred rather than read — carried through as INFERRED.
"""
from __future__ import annotations

import glob
import os
import sys
import zipfile

import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (AZ_BBOX, CRS_WGS84, DATA, download, esri_query_all,
                    log_status, null_sentinels)

GPKG = os.path.join(DATA, "az_power.gpkg")

SUBSTATIONS = ("https://services6.arcgis.com/OO2s4OoyCZkYJ6oE/arcgis/rest/"
               "services/Substations/FeatureServer/0")
TRANSMISSION = ("https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/"
                "services/US_Electric_Power_Transmission_Lines/"
                "FeatureServer/0")
POWERPLANTS = ("https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/"
               "services/Power_Plants_in_the_US/FeatureServer/0")
TERRITORIES = ("https://services3.arcgis.com/OYP7N6mAJJCyH6hd/arcgis/rest/"
               "services/Electric_Retail_Service_Territories_HIFLD/"
               "FeatureServer/0")
TERRITORIES_XCHECK = ("https://services6.arcgis.com/BAJNi3EgCdtQ1BCG/arcgis/"
                      "rest/services/Electric_Retail_Service_Territories/"
                      "FeatureServer/0")

EIA860_URL = "https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip"
EIA860M_CANDIDATES = [
    f"https://www.eia.gov/electricity/data/eia860m/xls/{m}_generator{y}.xlsx"
    for y, m in [(2026, "may"), (2026, "april"), (2026, "march"),
                 (2026, "february"), (2026, "january"),
                 (2025, "december"), (2025, "november")]
]


def fetch(name, key, url, **kw):
    try:
        gj = esri_query_all(url, **kw)
        n = len(gj["features"])
        if n == 0:
            raise RuntimeError("query returned 0 features")
        gdf = gpd.GeoDataFrame.from_features(gj["features"], crs=CRS_WGS84)
        log_status(name, url, True, records=n, key=key)
        return gdf
    except Exception as exc:  # noqa: BLE001
        log_status(name, url, False, detail=str(exc), key=key)
        return None


# --------------------------------------------------------------------------
# A. SUBSTATIONS
# --------------------------------------------------------------------------
def step_a():
    print("\n[3A] SUBSTATIONS")
    g = fetch("HIFLD_Electric_Substations (AZ) [third-party republication of "
              "HIFLD schema; hifld-geoplatform opendata is SUNSET]",
              "substations", SUBSTATIONS, where="STATE='AZ'",
              out_fields="OBJECTID,ID,NAME,CITY,STATE,COUNTY,COUNTYFIPS,TYPE,"
                         "STATUS,LATITUDE,LONGITUDE,LINES,MAX_VOLT,MIN_VOLT,"
                         "MAX_INFER,MIN_INFER,SOURCE,SOURCEDATE,VAL_METHOD",
              page=1000)
    if g is None:
        return None

    # Sentinel handling. -999999 means "unknown", not a voltage.
    g["max_volt_kv"] = null_sentinels(g["MAX_VOLT"])
    g["min_volt_kv"] = null_sentinels(g["MIN_VOLT"])
    # HIFLD's own inference flags -> the literal string INFERRED.
    g["max_volt_provenance"] = g["MAX_INFER"].apply(
        lambda v: "INFERRED" if str(v).strip().upper() in ("Y", "YES", "1",
                                                           "TRUE") else "READ")
    g["min_volt_provenance"] = g["MIN_INFER"].apply(
        lambda v: "INFERRED" if str(v).strip().upper() in ("Y", "YES", "1",
                                                           "TRUE") else "READ")
    # LINES carries the same -999999 sentinel as the voltage fields. Coercing
    # without nulling let -999999 through into scoring and produced a
    # composite score of -1,818,114.
    g["lines_count"] = null_sentinels(g["LINES"], sentinels=(-999999, -999998,
                                                             -99999, -9999))

    print(f"  {len(g)} AZ substations")
    print(f"  max_volt known: {g['max_volt_kv'].notna().sum()}, "
          f"null/sentinel: {g['max_volt_kv'].isna().sum()}")
    print(f"  max_volt INFERRED by HIFLD: "
          f"{(g['max_volt_provenance'] == 'INFERRED').sum()}")
    print("  STATUS:", g["STATUS"].value_counts().to_dict())
    print("  voltage class counts (>=115kV is the Pop 2 gate):")
    for lo, hi in [(0, 69), (69, 115), (115, 230), (230, 345), (345, 500),
                   (500, 9999)]:
        n = ((g["max_volt_kv"] >= lo) & (g["max_volt_kv"] < hi)).sum()
        print(f"    {lo:4d}-{hi:4d} kV : {n:5d}")
    print(f"    >= 115 kV     : {(g['max_volt_kv'] >= 115).sum()}")
    g.to_file(GPKG, layer="substations", driver="GPKG")
    return g


# --------------------------------------------------------------------------
# B. TRANSMISSION LINES
# --------------------------------------------------------------------------
def step_b():
    print("\n[3B] TRANSMISSION LINES")
    g = fetch("HIFLD_Electric_Power_Transmission_Lines (AZ bbox)",
              "transmission", TRANSMISSION, geometry=AZ_BBOX,
              out_fields="OBJECTID,ID,TYPE,STATUS,OWNER,VOLTAGE,VOLT_CLASS,"
                         "INFERRED,SUB_1,SUB_2,SHAPE__Length",
              page=500)
    if g is None:
        return None
    g["voltage_kv"] = null_sentinels(g["VOLTAGE"])
    g["voltage_provenance"] = g["INFERRED"].apply(
        lambda v: "INFERRED" if str(v).strip().upper() in ("Y", "YES", "1",
                                                           "TRUE") else "READ")
    print(f"  {len(g)} transmission line segments in AZ bbox")
    print(f"  voltage known: {g['voltage_kv'].notna().sum()}, "
          f"null/sentinel: {g['voltage_kv'].isna().sum()}")
    print(f"  voltage INFERRED by HIFLD: "
          f"{(g['voltage_provenance'] == 'INFERRED').sum()}")
    print("  VOLT_CLASS:", g["VOLT_CLASS"].value_counts().to_dict())
    print("  STATUS:", g["STATUS"].value_counts().to_dict())
    g.to_file(GPKG, layer="transmission_lines", driver="GPKG")
    return g


# --------------------------------------------------------------------------
# C. POWER PLANTS AND RETIREMENTS — EIA-860 / 860M
# --------------------------------------------------------------------------
def _find_header_row(path, sheet, required):
    """Detect the header row by looking for known column names.

    The EIA header offset is NOT stable across releases, so skiprows is never
    hardcoded. Scans the first 12 rows for one containing all required names.
    """
    probe = pd.read_excel(path, sheet_name=sheet, header=None, nrows=12,
                          dtype=str)
    for i in range(len(probe)):
        vals = {str(v).strip().lower() for v in probe.iloc[i].tolist()}
        if all(any(r.lower() == v for v in vals) for r in required):
            return i
    raise RuntimeError(
        f"could not locate header row in {os.path.basename(path)}[{sheet}] "
        f"containing all of {required}; first rows were "
        f"{probe.head(4).to_dict('records')}")


def step_c():
    print("\n[3C] POWER PLANTS AND RETIREMENTS (EIA)")
    zpath = os.path.join(DATA, "eia8602024.zip")
    try:
        download(EIA860_URL, zpath)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(os.path.join(DATA, "eia860_2024"))
        log_status("EIA-860 annual 2024", EIA860_URL, True,
                   key="eia860_annual")
    except Exception as exc:  # noqa: BLE001
        log_status("EIA-860 annual 2024", EIA860_URL, False, detail=str(exc),
                   manual_url="https://www.eia.gov/electricity/data/eia860/",
                   key="eia860_annual")
        return None, None

    files = glob.glob(os.path.join(DATA, "eia860_2024", "**", "*.xlsx"),
                      recursive=True)
    print("  extracted:", [os.path.basename(f) for f in files])

    gen_f = next((f for f in files
                  if os.path.basename(f).lower().startswith("3_1_generator")),
                 None)
    plant_f = next((f for f in files
                    if os.path.basename(f).lower().startswith("2___plant")),
                   None)
    if not gen_f or not plant_f:
        log_status("EIA-860 expected workbooks", EIA860_URL, False,
                   detail=f"missing generator/plant workbook in {files}",
                   key="eia860_workbooks")
        return None, None

    xl = pd.ExcelFile(gen_f)
    print("  generator sheets:", xl.sheet_names)

    # Plant-level attributes (county, lat/lon).
    hdr = _find_header_row(plant_f, 0, ["Plant Code", "Plant Name", "State"])
    plants = pd.read_excel(plant_f, sheet_name=0, header=hdr)
    plants.columns = [str(c).strip() for c in plants.columns]
    print(f"  plant workbook header row {hdr}, {len(plants)} rows")

    # Match sheets by PREFIX, not equality. In the 2024 release the retired
    # sheet is named "Retired and Canceled" — an equality test silently drops
    # it, which would leave Pop 1 with zero retired units.
    frames = {}
    for sheet in xl.sheet_names:
        s = sheet.strip().lower()
        if s.startswith(("operable", "retired", "proposed", "canceled")):
            h = _find_header_row(gen_f, sheet,
                                 ["Plant Code", "Generator ID", "Status"])
            df = pd.read_excel(gen_f, sheet_name=sheet, header=h)
            df.columns = [str(c).strip() for c in df.columns]
            df["eia_sheet"] = sheet
            frames[sheet] = df
            print(f"  sheet '{sheet}': header row {h}, {len(df)} rows")
    if not frames:
        log_status("EIA-860 generator sheets", gen_f, False,
                   detail=f"no Operable/Retired/Proposed sheet in "
                          f"{xl.sheet_names}", key="eia860_sheets")
        return None, None

    gens = pd.concat(frames.values(), ignore_index=True)
    gens = gens[gens["State"].astype(str).str.strip().str.upper() == "AZ"]
    print(f"  Arizona generator records: {len(gens)}")
    return gens, plants


def step_c_860m():
    """EIA-860M monthly. Recorded as a failure if unreachable — never
    silently substituted with the annual file."""
    print("\n[3C-M] EIA-860M monthly")
    last_err = {}
    for url in EIA860M_CANDIDATES:
        dest = os.path.join(DATA, os.path.basename(url))
        try:
            download(url, dest, retries=2)
            # A size check alone is NOT enough: EIA serves a ~67 KB HTML error
            # page under the .xlsx URL when /cneaf/electricity/ is down, which
            # sails past any size threshold. Verify the ZIP magic bytes that
            # every real .xlsx starts with.
            with open(dest, "rb") as fh:
                magic = fh.read(4)
            if magic[:2] != b"PK":
                head = open(dest, "rb").read(200).decode("utf-8", "replace")
                os.remove(dest)
                raise RuntimeError(
                    f"not an xlsx — got {magic!r} "
                    f"({os.path.getsize(dest) if os.path.exists(dest) else 0} "
                    f"bytes of HTML error page). First bytes: "
                    f"{head[:120]!r}")
            log_status(f"EIA-860M monthly ({os.path.basename(url)})", url,
                       True, key="eia860m")
            return dest
        except Exception as exc:  # noqa: BLE001
            last_err[url] = str(exc)
    log_status("EIA-860M monthly", EIA860M_CANDIDATES[0], False,
               detail="ALL candidate months failed. "
                      + "; ".join(f"{os.path.basename(u)}: {e[:120]}"
                                  for u, e in last_err.items()),
               manual_url="https://www.eia.gov/electricity/data/eia860m/",
               key="eia860m")
    return None


# --------------------------------------------------------------------------
# D. UTILITY SERVICE TERRITORIES
# --------------------------------------------------------------------------
def step_d():
    print("\n[3D] UTILITY SERVICE TERRITORIES")
    g = fetch("HIFLD_Electric_Retail_Service_Territories (AZ bbox)",
              "territories", TERRITORIES, geometry=AZ_BBOX,
              out_fields="OBJECTID,ID,NAME,TYPE,STATE,REGULATED,CNTRL_AREA,"
                         "PLAN_AREA,HOLDING_CO,WEBSITE,TELEPHONE,SOURCE,"
                         "SOURCEDATE",
              page=200)
    if g is None:
        return None
    print(f"  {len(g)} territories intersecting AZ bbox")
    print("  TYPE:", g["TYPE"].value_counts().to_dict())
    g.to_file(GPKG, layer="utility_territories", driver="GPKG")

    x = fetch("HIFLD_Electric_Retail_Service_Territories (cross-check copy)",
              "territories_xcheck", TERRITORIES_XCHECK, geometry=AZ_BBOX,
              out_fields="OBJECTID,NAME,TYPE,STATE", page=200)
    if x is not None:
        print(f"  cross-check copy: {len(x)} territories "
              f"({'MATCH' if len(x) == len(g) else 'DIFFERS'})")
    return g


def main():
    print("STEP 3 — POWER DATA\n" + "=" * 60)
    step_a()
    step_b()
    gens, plants = step_c()
    if gens is not None:
        gens.to_pickle(os.path.join(DATA, "eia860_az_generators.pkl"))
        plants.to_pickle(os.path.join(DATA, "eia860_plants.pkl"))
    step_c_860m()
    step_d()
    print("\nSTEP 3 acquisition complete.")


if __name__ == "__main__":
    main()
