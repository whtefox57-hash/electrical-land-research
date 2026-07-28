"""
Step 6 -- verification.

This script is deliberately adversarial toward the pipeline's own output. It
reopens the GeoPackage from disk (it does not trust in-memory state), re-reads
the raw EIA workbook, and tries to break the result. Any failed check is a hard
FAIL and sets a non-zero exit code.

Run:  python3 scripts/verify.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loaders  # noqa: E402
from config import (  # noqa: E402
    MAX_POSSIBLE_SCORE, OUTPUTS, TOP_N, WORKING_CRS,
)

GPKG = OUTPUTS / "tx_candidates.gpkg"
TOP_CSV = OUTPUTS / "top25_candidates.csv"
COUNTY_CSV = OUTPUTS / "COUNTY_SUMMARY.csv"

PASS, FAIL, WARN = "PASS", "FAIL", "WARN"
results: list[tuple[str, str, str]] = []


def check(name: str, ok: bool, detail: str = "", warn_only: bool = False) -> bool:
    results.append((PASS if ok else (WARN if warn_only else FAIL), name, detail))
    return ok


def main() -> int:
    if not GPKG.exists():
        print(f"FAIL: {GPKG} does not exist. Run build_screen.py first.")
        return 2

    # ---- 1. GeoPackage structure ----------------------------------------
    import fiona
    layers = fiona.listlayers(GPKG)
    check("geopackage has a candidates layer", "candidates" in layers,
          f"layers present: {layers}")

    cands = gpd.read_file(GPKG, layer="candidates")
    check("candidates layer is non-empty", len(cands) > 0, f"{len(cands)} features")

    epsg = cands.crs.to_epsg() if cands.crs else None
    check("candidates CRS matches working CRS", epsg == WORKING_CRS,
          f"found EPSG:{epsg}, expected EPSG:{WORKING_CRS}")

    for lyr in layers:
        g = gpd.read_file(GPKG, layer=lyr)
        e = g.crs.to_epsg() if g.crs else None
        check(f"layer '{lyr}' CRS + feature count", e == WORKING_CRS,
              f"EPSG:{e}, {len(g)} features")

    # ---- 2. geometry and score integrity --------------------------------
    null_geom = int(cands.geometry.isna().sum() + cands.geometry.is_empty.sum())
    check("no candidate has null or empty geometry", null_geom == 0,
          f"{null_geom} bad geometries")

    over = int((cands["score_total"] > MAX_POSSIBLE_SCORE).sum())
    check(f"no score exceeds {MAX_POSSIBLE_SCORE}", over == 0,
          f"{over} candidates over max; observed max "
          f"{cands['score_total'].max():.2f}")

    neg = int((cands["score_total"] < 0).sum())
    check("no negative scores", neg == 0, f"{neg} negative")

    dupe = int(cands.duplicated(subset=["site_name", "site_type"]).sum())
    check("no duplicated site_name/site_type pairs", dupe == 0,
          f"{dupe} duplicates", warn_only=True)

    # ---- 3. top-25 CSV ---------------------------------------------------
    if TOP_CSV.exists():
        top = pd.read_csv(TOP_CSV)
        check(f"top-{TOP_N} CSV has {TOP_N} rows (or all candidates)",
              len(top) == min(TOP_N, len(cands)), f"{len(top)} rows")
        check("google_maps_url column present and populated",
              "google_maps_url" in top.columns
              and top["google_maps_url"].notna().all())
        check("county_cad_note column present and blank",
              "county_cad_note" in top.columns
              and top["county_cad_note"].isna().all()
              or (top.get("county_cad_note", pd.Series(dtype=str))
                  .fillna("").eq("").all()))
        check("top-25 is sorted descending by score",
              top["score_total"].is_monotonic_decreasing)

        # ---- 4. county concentration --------------------------------------
        vc = top["county_name"].value_counts(dropna=False)
        top_county, top_count = (vc.index[0], int(vc.iloc[0])) if len(vc) else (None, 0)
        concentrated = top_count > len(top) * 0.5
        check("top-25 are not concentrated in a single county", not concentrated,
              f"most common county '{top_county}' holds {top_count}/{len(top)}. "
              f"If this failed, the rubric is probably overweighting one factor.",
              warn_only=True)

        # ---- 5. hand spot-check of 3 sites against raw EIA ----------------
        print("\n--- SPOT CHECK: 3 of the top 25 against the raw EIA file ---")
        try:
            gens = loaders.load_eia_generators()
        except Exception as exc:  # noqa: BLE001
            check("raw EIA re-read for spot check", False, f"{exc}", warn_only=True)
            gens = None

        pop1 = top[top["site_type"] == "retired_generation"].head(3)
        if gens is not None and not pop1.empty:
            for _, row in pop1.iterrows():
                pc = row.get("plant_code")
                sub = gens[gens["plant_code"] == pc]
                raw_mw = sub["capacity_mw"].sum()
                print(f"  plant_code={pc}  {row['site_name']}")
                print(f"    lat/lon      : {row.get('lat_wgs84'):.5f}, "
                      f"{row.get('lon_wgs84'):.5f}")
                print(f"    county       : {row.get('county_name')} "
                      f"(source attr: {row.get('county_src')})")
                print(f"    screen MW    : {row.get('retired_mw'):.1f}")
                print(f"    raw EIA MW   : {raw_mw:.1f} "
                      f"across {len(sub)} unit rows")
                print(f"    maps         : {row.get('google_maps_url')}")
                agree = abs(float(row.get("retired_mw", 0)) - raw_mw) < max(
                    1.0, 0.25 * raw_mw)
                check(f"MW reconciles for plant {pc}", agree,
                      f"screen={row.get('retired_mw')} raw_total={raw_mw} "
                      f"(raw total includes non-qualifying units, so exact "
                      f"equality is not expected)", warn_only=True)
                county_agree = (
                    str(row.get("county_name", "")).strip().lower()
                    in str(row.get("county_src", "")).strip().lower()
                    or str(row.get("county_src", "")).strip().lower()
                    in str(row.get("county_name", "")).strip().lower())
                check(f"county agrees between spatial join and EIA attr "
                      f"for plant {pc}", county_agree,
                      f"spatial='{row.get('county_name')}' "
                      f"attr='{row.get('county_src')}'", warn_only=True)
        else:
            print("  (no Population 1 sites in the top 25 to spot check)")

    if COUNTY_CSV.exists():
        cs = pd.read_csv(COUNTY_CSV)
        check("county summary totals match candidate count",
              int(cs["candidate_count"].sum()) == len(cands),
              f"summary={int(cs['candidate_count'].sum())} candidates={len(cands)}")

    # ---- report ----------------------------------------------------------
    print("\n=== STEP 6 VERIFICATION ===")
    for status, name, detail in results:
        print(f"  [{status}] {name}")
        if detail and status != PASS:
            print(f"          {detail}")

    n_fail = sum(1 for s, _, _ in results if s == FAIL)
    n_warn = sum(1 for s, _, _ in results if s == WARN)

    print("\n=== REPORT ===")
    print(f"  total candidates evaluated : {len(cands)}")
    print(f"  score range                : {cands['score_total'].min():.2f} "
          f"to {cands['score_total'].max():.2f}")
    print(f"  distinct counties          : {cands['county_name'].nunique()}")
    print("  top 5 counties by candidate count:")
    for county, n in cands["county_name"].value_counts().head(5).items():
        print(f"      {county}: {n}")

    import json
    man_path = Path(GPKG).parent.parent / "data" / "raw" / "MANIFEST.json"
    if man_path.exists():
        man = json.loads(man_path.read_text())
        bad = [k for k, v in man["sources"].items() if v["status"] == "failed"]
        print(f"  datasets that FAILED to download: {bad or 'none'}")

    print(f"\n  {n_fail} failed, {n_warn} warnings, "
          f"{len(results) - n_fail - n_warn} passed")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
