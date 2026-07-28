"""
Step 6 verification. Reopens the written outputs and checks them against the
raw sources by an independent code path.

The MW spot check deliberately does NOT reuse build_screen's aggregation - it
re-reads the raw EIA workbooks and re-sums, so an error in the pipeline's
grouping would show up as a mismatch rather than being reproduced.
"""
from __future__ import annotations

import json
import zipfile

import fiona
import geopandas as gpd
import pandas as pd

GPKG = "outputs/tx_candidates.gpkg"
TOP = "outputs/top25_candidates.csv"
FAILS: list[str] = []
CHECKS: list[tuple[str, bool, str]] = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL':4s}] {name}" + (f" - {detail}" if detail else ""))


def independent_site_mw(plant_code):
    """Re-derive retired + announced MW for one plant straight from raw files."""
    total_ret, total_ann = 0.0, 0.0
    xl = pd.ExcelFile("data/raw/eia860m_june2026.xlsx")

    def hdr(sheet, require):
        for skip in range(6):
            p = xl.parse(sheet, skiprows=skip, nrows=3)
            if all(c in p.columns for c in require):
                return xl.parse(sheet, skiprows=skip)
        raise ValueError(sheet)

    r = hdr("Retired", ["Plant ID", "Retirement Year"])
    r = r[(r["Plant ID"] == plant_code)
          & (pd.to_numeric(r["Retirement Year"], errors="coerce") >= 2010)]
    total_ret += float(pd.to_numeric(r["Nameplate Capacity (MW)"],
                                     errors="coerce").fillna(0).sum())
    ret_ids = {str(x).strip() for x in r["Generator ID"]}

    # NB: blank 'Planned Retirement Year' cells arrive as empty strings, not
    # NaN, so a bare .notna() counts operating units as announced retirements.
    # Coerce to numeric first (this caught a real bug in this check itself).
    o = hdr("Operating", ["Plant ID", "Planned Retirement Year"])
    o = o[(o["Plant ID"] == plant_code)
          & pd.to_numeric(o["Planned Retirement Year"],
                          errors="coerce").notna()]
    total_ann += float(pd.to_numeric(o["Nameplate Capacity (MW)"],
                                     errors="coerce").fillna(0).sum())
    ann_ids = {str(x).strip() for x in o["Generator ID"]}

    # Units present only in the annual releases (not in 860M) still count.
    for zp, suffix in [("data/raw/eia8602025ER.zip", "Y2025_Early_Release"),
                       ("data/raw/eia8602024.zip", "Y2024")]:
        with zipfile.ZipFile(zp).open(f"3_1_Generator_{suffix}.xlsx") as fh:
            x2 = pd.ExcelFile(fh)

            def h2(sheet, require):
                for skip in range(6):
                    p = x2.parse(sheet, skiprows=skip, nrows=3)
                    if all(c in p.columns for c in require):
                        return x2.parse(sheet, skiprows=skip)
                raise ValueError(sheet)

            rr = h2("Retired and Canceled", ["Plant Code", "Status"])
            rr = rr[(rr["Plant Code"] == plant_code) & (rr["Status"] == "RE")
                    & (pd.to_numeric(rr["Retirement Year"], errors="coerce") >= 2010)]
            new = rr[~rr["Generator ID"].astype(str).str.strip().isin(ret_ids)]
            total_ret += float(pd.to_numeric(new["Nameplate Capacity (MW)"],
                                             errors="coerce").fillna(0).sum())
            ret_ids |= {str(x).strip() for x in new["Generator ID"]}

            oo = h2("Operable", ["Plant Code", "Planned Retirement Year"])
            oo = oo[(oo["Plant Code"] == plant_code)
                    & pd.to_numeric(oo["Planned Retirement Year"],
                                    errors="coerce").notna()]
            # A unit already recorded as retired must not also be counted as an
            # announced retirement from a stale older release.
            new = oo[~oo["Generator ID"].astype(str).str.strip()
                     .isin(ann_ids | ret_ids)]
            total_ann += float(pd.to_numeric(new["Nameplate Capacity (MW)"],
                                             errors="coerce").fillna(0).sum())
            ann_ids |= {str(x).strip() for x in new["Generator ID"]}

    return round(total_ret, 1), round(total_ann, 1)


def main():
    # --- GeoPackage structure ---
    layers = fiona.listlayers(GPKG)
    check("GeoPackage opens and has layers", len(layers) >= 4,
          f"{len(layers)} layers: {layers}")

    counts = {}
    for lyr in layers:
        g = gpd.read_file(GPKG, layer=lyr)
        counts[lyr] = len(g)
        crs_ok = g.crs is not None and g.crs.to_epsg() == 3081
        check(f"layer '{lyr}' CRS is EPSG:3081", crs_ok,
              f"{g.crs.to_epsg() if g.crs else None}, {len(g)} features")

    cand = gpd.read_file(GPKG, layer="candidates")

    # --- geometry and score integrity ---
    nullgeom = int(cand.geometry.isna().sum() + cand.geometry.is_empty.sum())
    check("no candidate has null/empty geometry", nullgeom == 0,
          f"{nullgeom} bad geometries")
    over = int((cand["score"] > 100).sum())
    check("no score above 100", over == 0, f"max score {cand['score'].max()}")
    under = int((cand["score"] < 0).sum())
    check("no negative score", under == 0, f"min score {cand['score'].min()}")

    # --- top 25 ---
    top = pd.read_csv(TOP)
    check("top25 has 25 rows", len(top) == 25, f"{len(top)} rows")
    check("top25 ranks are 1..25 with no gaps",
          list(top["rank"]) == list(range(1, 26)))
    nc = top["county"].nunique()
    check("top 25 are NOT all in one county", nc > 1,
          f"{nc} distinct counties; most common: "
          f"{top['county'].value_counts().head(3).to_dict()}")
    check("every top25 row has a google_maps_url",
          top["google_maps_url"].notna().all() and
          top["google_maps_url"].str.startswith("https://").all())
    check("county_cad_note column present and blank",
          "county_cad_note" in top.columns and
          top["county_cad_note"].fillna("").eq("").all())

    # --- coordinate sanity: inside the Texas envelope ---
    inbox = ((top["latitude"].between(25.5, 36.8))
             & (top["longitude"].between(-107.0, -93.3)))
    check("all top25 coordinates fall inside the Texas envelope", inbox.all(),
          f"{int((~inbox).sum())} outside")

    # --- county cross-check: spatial join vs EIA's own county field ---
    p1 = top[top["population"] == 1].copy()
    p1["a"] = p1["county"].str.replace(" County", "", regex=False).str.upper().str.strip()
    p1["b"] = p1["county_eia"].astype(str).str.upper().str.strip()
    mism = p1[p1["a"] != p1["b"]]
    check("spatial-join county agrees with EIA county field on all Pop 1 top25",
          len(mism) == 0,
          "mismatches: " + ", ".join(
              f"{r.site_name}: map={r.county} eia={r.county_eia}"
              for r in mism.itertuples()) if len(mism) else "all agree")

    # --- hand spot check of 3 sites against raw EIA ---
    print("\n--- independent MW re-derivation for 3 of the top 25 ---")
    for r in top.head(3).itertuples():
        ret, ann = independent_site_mw(int(r.plant_code))
        ok = (abs(ret - r.retired_mw) < 0.05) and (abs(ann - r.announced_mw) < 0.05)
        check(f"spot check {r.site_name} (plant {int(r.plant_code)})", ok,
              f"pipeline retired={r.retired_mw} announced={r.announced_mw} | "
              f"raw re-read retired={ret} announced={ann} | "
              f"county={r.county} lat/lon={r.latitude},{r.longitude}")

    # --- summary report ---
    print("\n=== SUMMARY ===")
    print(f"total candidates evaluated : {len(cand)}")
    print(f"  Population 1 (retired/retiring plants): "
          f"{int((cand['population']==1).sum())}")
    print(f"  Population 2 (>=138 kV substation nodes): "
          f"{int((cand['population']==2).sum())}")
    print(f"score range (all candidates): {cand['score'].min()} - "
          f"{cand['score'].max()}")
    print(f"score range (top 25)        : {top['score'].min()} - "
          f"{top['score'].max()}")
    print(f"score basis                 : {cand['score_basis'].iloc[0]}")
    print("\ntop 5 counties in the top 25 by candidate count:")
    print(top["county"].value_counts().head(5).to_string())

    cs = pd.read_csv("outputs/COUNTY_SUMMARY.csv")
    print("\ntop 5 counties by mean score (COUNTY_SUMMARY, Pop 1 present only):")
    p1c = set(top[top["population"] == 1]["county"])
    print(cs[cs["county"].isin(p1c)].head(5).to_string(index=False))

    try:
        rep = json.load(open("outputs/_run_report.json"))
        print("\ndatasets that failed to download:")
        for f in rep.get("failures", []):
            print("  -", f)
        print("  - FCC broadband (dataset D): all fcc.gov hosts policy-denied")
    except FileNotFoundError:
        pass

    nfail = sum(1 for _, ok, _ in CHECKS if not ok)
    print(f"\n{len(CHECKS) - nfail}/{len(CHECKS)} checks passed")
    return nfail


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
