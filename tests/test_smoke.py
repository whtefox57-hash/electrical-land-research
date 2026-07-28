"""
CODE-PATH SMOKE TEST -- USES SYNTHETIC FIXTURES.

################ READ THIS BEFORE TRUSTING ANY NUMBER BELOW ################
#                                                                          #
#  Every input in this file is MADE UP. The plants, substations, lines and  #
#  coordinates are invented to exercise branches of the pipeline. NONE of   #
#  it is real Texas data and none of it is a screening result.              #
#                                                                          #
#  This test exists to answer one question: "does the code run and are its  #
#  invariants intact?" It cannot tell you whether the screen is correct,    #
#  because correctness depends on real source data this environment could   #
#  not reach.                                                               #
#                                                                          #
#  Hard quarantine: all writes go to a temporary directory. The test        #
#  asserts that data/raw/ and outputs/ are untouched.                       #
#                                                                          #
############################################################################

Run:  python3 tests/test_smoke.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LineString, Point, Polygon

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import build_screen as bs  # noqa: E402
from config import MAX_POSSIBLE_SCORE, OUTPUTS, RAW  # noqa: E402

WGS = "EPSG:4326"
failures: list[str] = []


def expect(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        print(f"         {detail}")
        failures.append(name)


# ==========================================================================
# 1. Rubric arithmetic, checked against hand-computed values
# ==========================================================================
def test_scoring_math() -> None:
    print("\n-- rubric arithmetic --")
    expect("600 MW recent retirement -> 30",
           bs.score_interconnection(600, 3.0) == 30)
    expect("250 MW recent -> 22", bs.score_interconnection(250, 3.0) == 22)
    expect("100 MW recent -> 14", bs.score_interconnection(100, 3.0) == 14)
    expect("30 MW -> 0", bs.score_interconnection(30, 3.0) == 0)
    expect("250 MW retired 14 yrs ago -> 22*0.5 = 11",
           bs.score_interconnection(250, 14.0) == 11)
    expect("future retirement is not stale",
           bs.score_interconnection(600, -2.0) == 30)

    expect("substation 800 m -> 25", bs.score_sub_proximity(800) == 25)
    expect("substation 2.9 km -> 18", bs.score_sub_proximity(2900) == 18)
    expect("substation 4.9 km -> 10", bs.score_sub_proximity(4900) == 10)
    expect("substation 9.9 km -> 3", bs.score_sub_proximity(9900) == 3)
    expect("substation 40 km -> 0", bs.score_sub_proximity(40000) == 0)

    expect("345 kV -> 15", bs.score_sub_voltage(345) == 15)
    expect("230 kV -> 12", bs.score_sub_voltage(230) == 12)
    expect("138 kV -> 8", bs.score_sub_voltage(138) == 8)
    expect("69 kV -> 3", bs.score_sub_voltage(69) == 3)
    expect("12 kV -> 0", bs.score_sub_voltage(12) == 0)
    expect("unknown voltage -> 0 (never guessed)",
           bs.score_sub_voltage(np.nan) == 0)

    expect("500 kV line at 500 m -> full 15",
           abs(bs.score_transmission(500, 500) - 15.0) < 1e-9)
    expect("500 kV line at 40 km -> 0",
           bs.score_transmission(40000, 500) == 0)
    expect("69 kV line at 500 m -> 15*1.0*0.35 = 5.25",
           abs(bs.score_transmission(500, 69) - 5.25) < 1e-9)
    expect("345 kV at 4 km -> 15*0.55*1.0 = 8.25",
           abs(bs.score_transmission(4000, 345) - 8.25) < 1e-9)

    expect("4 providers -> 10", bs.score_broadband(4) == 10)
    expect("2 providers -> 4", bs.score_broadband(2) == 4)
    expect("unknown providers -> 0", bs.score_broadband(np.nan) == 0)

    expect("water unavailable -> 0", bs.score_water(1000, False) == 0)
    expect("water 1 km available -> 5", bs.score_water(1000, True) == 5)

    expect("rubric maximum is 100", MAX_POSSIBLE_SCORE == 100,
           f"got {MAX_POSSIBLE_SCORE}")


# ==========================================================================
# 2. Synthetic fixtures  (INVENTED -- see banner)
# ==========================================================================
def make_fixtures():
    # Four fake plants near Abilene-ish longitudes. Values chosen to hit
    # specific rubric branches, not to resemble any real facility.
    gens = pd.DataFrame({
        "plant_code": [101, 101, 102, 103, 104],
        "plant_name": ["FAKE Alpha", "FAKE Alpha", "FAKE Bravo",
                       "FAKE Charlie", "FAKE Delta"],
        "generator_id": ["1", "2", "1", "1", "1"],
        "state": ["TX"] * 5,
        "county": ["Fakeston", "Fakeston", "Testerly", "Testerly", "Fakeston"],
        "capacity_mw": [300.0, 300.0, 250.0, 120.0, 30.0],
        "status": ["RE", "RE", "RE", "OP", "RE"],
        "technology": ["Coal", "Coal", "Gas", "Gas", "Gas"],
        "retire_year": [2020.0, 2020.0, 2012.0, np.nan, 2019.0],
        "retire_month": [6.0, 6.0, 3.0, np.nan, 1.0],
        "planned_retire_year": [np.nan, np.nan, np.nan, 2029.0, np.nan],
        "planned_retire_month": [np.nan, np.nan, np.nan, 12.0, np.nan],
        "latitude": [np.nan] * 5,
        "longitude": [np.nan] * 5,
        "_sheet": ["FAKE::Retired"] * 5,
    })
    plants = pd.DataFrame({
        "plant_code": [101, 102, 103, 104],
        "plant_name": ["FAKE Alpha", "FAKE Bravo", "FAKE Charlie", "FAKE Delta"],
        "state": ["TX"] * 4,
        "county": ["Fakeston", "Testerly", "Testerly", "Fakeston"],
        "latitude": [32.40, 32.60, 31.90, 32.10],
        "longitude": [-99.70, -99.30, -98.80, -99.50],
        "_source_file": "FAKE_plant.xlsx",
    })

    # Substations: one right on plant 101, one 138 kV far away (Population 2),
    # one low-voltage that must NOT qualify for Population 2.
    subs = gpd.GeoDataFrame({
        "sub_name": ["FAKE Sub On-Site", "FAKE Sub Remote HV",
                     "FAKE Sub Lowvolt", "FAKE Sub Near Bravo"],
        "sub_max_kv": [345.0, 345.0, 69.0, 138.0],
        "sub_min_kv": [138.0, 138.0, 12.0, 69.0],
        "sub_lines": [6.0, 4.0, 2.0, 3.0],
        "sub_status": ["IN SERVICE"] * 4,
        "sub_county_attr": ["Fakeston", "Rangeland", "Rangeland", "Testerly"],
    }, geometry=[Point(-99.7008, 32.4004), Point(-98.20, 33.10),
                 Point(-98.25, 33.15), Point(-99.2960, 32.6010)], crs=WGS)

    lines = gpd.GeoDataFrame({
        "line_kv": [345.0, 138.0, np.nan],
        "line_volt_class": ["345kv", "100_161kv", "unknown"],
        "line_volt_class_src": ["345", "138", None],
        "line_owner": ["FAKE Utility A", "FAKE Utility B", "FAKE Utility C"],
        "line_status": ["IN SERVICE"] * 3,
    }, geometry=[
        LineString([(-99.85, 32.40), (-99.55, 32.41)]),
        LineString([(-99.40, 32.60), (-99.20, 32.61)]),
        LineString([(-98.30, 33.10), (-98.10, 33.12)]),
    ], crs=WGS)

    counties = gpd.GeoDataFrame({
        "county_name": ["Fakeston", "Testerly", "Rangeland"],
    }, geometry=[
        Polygon([(-100.0, 32.0), (-99.4, 32.0), (-99.4, 32.5), (-100.0, 32.5)]),
        Polygon([(-99.4, 31.5), (-98.6, 31.5), (-98.6, 32.9), (-99.4, 32.9)]),
        Polygon([(-98.6, 32.9), (-98.0, 32.9), (-98.0, 33.4), (-98.6, 33.4)]),
    ], crs=WGS)

    return gens, plants, subs, lines, counties


# ==========================================================================
# 3. Pipeline behaviour on the synthetic fixtures
# ==========================================================================
def test_pipeline() -> None:
    print("\n-- pipeline on synthetic fixtures --")
    gens, plants, subs, lines, counties = make_fixtures()

    pop1 = bs.build_population_1(gens, plants)
    names = sorted(pop1["site_name"].tolist())
    expect("Population 1 keeps Alpha(600MW), Bravo(250MW), Charlie(planned)",
           names == ["FAKE Alpha", "FAKE Bravo", "FAKE Charlie"], f"got {names}")
    expect("Delta (30 MW) excluded by the 50 MW floor",
           "FAKE Delta" not in names)
    alpha = pop1[pop1["site_name"] == "FAKE Alpha"].iloc[0]
    expect("Alpha units aggregated to 600 MW", alpha["retired_mw"] == 600.0,
           f"got {alpha['retired_mw']}")

    pop2 = bs.build_population_2(subs, pop1)
    p2names = sorted(pop2["site_name"].tolist())
    expect("Population 2 excludes the substation on top of a Pop-1 site",
           "FAKE Sub On-Site" not in p2names, f"got {p2names}")
    expect("Population 2 excludes sub-138 kV substations",
           "FAKE Sub Lowvolt" not in p2names, f"got {p2names}")
    expect("Population 2 keeps the remote 345 kV substation",
           "FAKE Sub Remote HV" in p2names, f"got {p2names}")

    keep = ["site_name", "site_type", "plant_code", "retired_mw", "unit_count",
            "eff_retire_year", "eff_retire_month", "county_src", "technology",
            "geometry"]
    frames = [df.reindex(columns=[k for k in keep if k in df.columns]
                         + ["geometry"]).loc[:, lambda d: ~d.columns.duplicated()]
              for df in (pop1, pop2) if not df.empty]
    cands = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs=WGS)

    c = bs.compute_metrics(cands, subs, lines, None, counties, None, None)
    c = bs.apply_scores(c)

    expect("every candidate scored", c["score_total"].notna().all())
    expect("no score exceeds the rubric maximum",
           bool((c["score_total"] <= MAX_POSSIBLE_SCORE).all()),
           f"max {c['score_total'].max()}")
    expect("no negative scores", bool((c["score_total"] >= 0).all()))
    expect("no null geometry", int(c.geometry.isna().sum()) == 0)
    expect("output is sorted descending", c["score_total"].is_monotonic_decreasing)
    expect("water component is 0 when the layer is absent",
           bool((c["score_water"] == 0).all()))

    alpha_row = c[c["site_name"] == "FAKE Alpha"].iloc[0]
    expect("on-site substation distance is sub-kilometre",
           alpha_row["nearest_sub_dist_m"] < 1000,
           f"{alpha_row['nearest_sub_dist_m']:.0f} m")
    expect("Alpha's nearest substation voltage read as 345 kV",
           alpha_row["nearest_sub_sub_max_kv"] == 345.0)
    expect("Alpha county resolved by spatial join to Fakeston",
           alpha_row["county_name"] == "Fakeston",
           f"got {alpha_row['county_name']}")

    bravo = c[c["site_name"] == "FAKE Bravo"].iloc[0]
    expect("Bravo (retired 2012) flagged as stale interconnection",
           bool(bravo["stale_interconnection_flag"]),
           f"years_since={bravo['years_since_retirement']:.1f}")
    expect("Bravo interconnection score halved to 11",
           bravo["score_interconnection"] == 11,
           f"got {bravo['score_interconnection']}")

    charlie = c[c["site_name"] == "FAKE Charlie"].iloc[0]
    expect("Charlie (announced 2029) not flagged stale",
           not bool(charlie["stale_interconnection_flag"]))

    return c


# ==========================================================================
# 4. Output writing, into a temp dir only
# ==========================================================================
def test_outputs(c) -> None:
    print("\n-- output writing (temp dir only) --")
    raw_before = sorted(p.name for p in RAW.glob("*"))
    out_before = sorted(p.name for p in OUTPUTS.glob("*"))

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        bs.GPKG = tmp / "tx_candidates.gpkg"
        bs.TOP_CSV = tmp / "top25_candidates.csv"
        bs.COUNTY_CSV = tmp / "COUNTY_SUMMARY.csv"
        bs.METHOD_MD = tmp / "METHOD.md"
        top = bs.write_outputs(c, {"substations": None}, {"sources": {}},
                               {"water_note": "(synthetic test)"})

        expect("GeoPackage written", bs.GPKG.exists())
        expect("top-N CSV written", bs.TOP_CSV.exists())
        expect("county summary written", bs.COUNTY_CSV.exists())
        expect("METHOD.md written", bs.METHOD_MD.exists())

        t = pd.read_csv(bs.TOP_CSV)
        expect("google_maps_url is a usable maps link",
               t["google_maps_url"].str.startswith(
                   "https://www.google.com/maps?q=").all(),
               f"e.g. {t['google_maps_url'].iloc[0]}")
        expect("county_cad_note exists and is blank for manual entry",
               "county_cad_note" in t.columns
               and t["county_cad_note"].fillna("").eq("").all())
        expect("METHOD.md names the derived fields",
               "DERIVED by this pipeline" in bs.METHOD_MD.read_text())
        expect("METHOD.md contains the 'what would make this WRONG' section",
               "WRONG" in bs.METHOD_MD.read_text())

        reread = gpd.read_file(bs.GPKG, layer="candidates")
        expect("GeoPackage reopens with the same feature count",
               len(reread) == len(c), f"{len(reread)} vs {len(c)}")

    expect("QUARANTINE: data/raw/ untouched by this test",
           sorted(p.name for p in RAW.glob("*")) == raw_before)
    expect("QUARANTINE: outputs/ untouched by this test",
           sorted(p.name for p in OUTPUTS.glob("*")) == out_before)


if __name__ == "__main__":
    print(__doc__.split("Run:")[0])
    test_scoring_math()
    c = test_pipeline()
    test_outputs(c)
    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} FAILED: {failures}")
        sys.exit(1)
    print("All code-path checks passed on SYNTHETIC data.")
    print("This says nothing about whether the screen is correct -- that")
    print("requires the real sources, which could not be downloaded here.")
    sys.exit(0)
