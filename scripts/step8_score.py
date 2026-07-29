"""STEP 8 — score and rank.

THE WEIGHT ARITHMETIC, STATED EXPLICITLY.

The brief specifies these component maxima:

    existing interconnection        25
    substation proximity            15
    substation voltage              10
    transmission proximity/voltage  10
    water risk                      20
    political risk                  25
    broadband proxy                  5
    ---------------------------------
    raw total                      110

That is 110, not 100. The instruction is to "normalize so weights sum to
exactly 100", so every raw component is multiplied by 100/110 = 0.90909...

    component            raw    normalized max
    interconnection       25    22.727273
    substation proximity  15    13.636364
    substation voltage    10     9.090909
    transmission          10     9.090909
    water                 20    18.181818
    political             25    22.727273
    broadband              5     4.545455
    ------------------------------------
                         110   100.000000

If a component cannot be scored because its dataset failed, its weight is NOT
silently redistributed. The row carries score_max_available (the normalized
total actually assessable) and score_basis naming which components were
scored, plus score_rescaled_to_100 which rescales transparently.

Political risk: jurisdiction priors are READ from outputs/AZ_POLITICAL_NOTES.md.
The two components left TBD there — prior_industrial_use and
dist_to_residential_km — are computed here from the spatial data and flagged
as DERIVED.
"""
from __future__ import annotations

import os
import sys

import geopandas as gpd
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_DIST, CRS_WGS84, DATA, OUTPUTS

WAT = os.path.join(DATA, "az_water.gpkg")
ENR = os.path.join(DATA, "az_candidates_enriched.gpkg")
OUT = os.path.join(DATA, "az_candidates_scored.gpkg")

RAW_WEIGHTS = {
    "interconnection": 25, "substation_proximity": 15,
    "substation_voltage": 10, "transmission": 10,
    "water": 20, "political": 25, "broadband": 5,
}
RAW_TOTAL = sum(RAW_WEIGHTS.values())          # 110
NORM = 100.0 / RAW_TOTAL                        # 0.909090...

# Jurisdiction-level political priors, READ from AZ_POLITICAL_NOTES.md.
# Components: moratorium(8) + no restrictive ordinance(5) + no organised
# opposition(3). prior_industrial(5) and dist_residential(4) are computed.
POLITICAL_PRIORS = {
    "BUCKEYE":            (8, 5, 3, "READ — AZ_POLITICAL_NOTES.md"),
    "MARANA":             (8, 5, 0, "READ — AZ_POLITICAL_NOTES.md"),
    "PHOENIX":            (8, 0, 3, "READ — AZ_POLITICAL_NOTES.md"),
    "TUCSON":             (8, 0, 0, "READ — AZ_POLITICAL_NOTES.md"),
    "UNINCORPORATED PINAL COUNTY":   (8, 5, 0, "READ — AZ_POLITICAL_NOTES.md"),
    "UNINCORPORATED PIMA COUNTY":    (8, 5, 0, "READ — AZ_POLITICAL_NOTES.md"),
    "UNINCORPORATED COCHISE COUNTY": (2, 5, 3, "READ — AZ_POLITICAL_NOTES.md"),
}
# Counties where organised opposition is 'yes' by default per the notes.
OPPOSITION_COUNTIES = {"PIMA", "PINAL", "SANTA CRUZ"}


def political_prior(jurisdiction, county):
    j = str(jurisdiction or "").upper()
    c = str(county or "").upper()
    for k, v in POLITICAL_PRIORS.items():
        if k in j:
            return v
    # Not researched in AZ_POLITICAL_NOTES.md. Absence of a found moratorium
    # or ordinance is NOT evidence of permissiveness — flagged INFERRED.
    opp = 0 if c in OPPOSITION_COUNTIES else 3
    return (8, 5, opp,
            "INFERRED — jurisdiction not researched in AZ_POLITICAL_NOTES.md; "
            "no moratorium or DC ordinance found, which is absence of "
            "evidence rather than evidence of absence. Phone call required.")


def s_interconnection(r):
    """0-25 raw. Generator interconnection rights are the real asset."""
    if r["cand_type"] == "pop1_retired_plant":
        mw = r["retired_mw_on_site"]
        base = 25 if mw >= 500 else 20 if mw >= 200 else 15
        yrs = r["years_since_retirement"]
        if pd.notna(yrs) and yrs > 10:
            base -= 6  # rights may have lapsed
        return max(base, 0), "retired plant capacity + retirement recency"
    n = r["lines_count"]
    if pd.isna(n):
        return 0.0, "no line count published for this substation"
    # Capped at 12/25: a substation is a connection point, not a generator
    # interconnection right with reserved capacity.
    return float(min(12, n * 2)), "substation line count (capped 12/25)"


def s_sub_prox(r):
    d = r["dist_nearest_substation_km"]
    if pd.isna(d):
        return np.nan
    for thr, v in [(0.1, 15), (1, 14), (2, 12), (5, 9), (10, 5), (20, 2)]:
        if d <= thr:
            return v
    return 0.0


def s_sub_volt(r):
    kv = r["max_kv_within_5km"]
    if pd.isna(kv):
        return np.nan
    for thr, v in [(500, 10), (345, 9), (230, 8), (115, 6), (69, 3)]:
        if kv >= thr:
            return v
    return 0.0


def s_transmission(r):
    d, kv = r["dist_nearest_transmission_km"], r["nearest_transmission_kv"]
    if pd.isna(d):
        return np.nan
    dc = 5 if d <= 1 else 4 if d <= 3 else 3 if d <= 5 else 2 if d <= 10 \
        else 1 if d <= 20 else 0
    if pd.isna(kv):
        return float(dc)  # distance only; voltage unknown
    vc = 5 if kv >= 500 else 4 if kv >= 345 else 3 if kv >= 230 \
        else 2 if kv >= 115 else 1 if kv >= 69 else 0
    return float(dc + vc)


def s_broadband(r):
    f = r["broadband_fiber_providers_PROXY"]
    if pd.isna(f):
        return np.nan
    return float(5 if f >= 4 else 4 if f >= 3 else 3 if f >= 2
                 else 2 if f >= 1 else 0)


def main():
    print("STEP 8 — SCORE AND RANK\n" + "=" * 60)
    print(f"  raw component total = {RAW_TOTAL}; normalization factor "
          f"100/{RAW_TOTAL} = {NORM:.9f}")
    for k, v in RAW_WEIGHTS.items():
        print(f"    {k:22s} raw {v:3d} -> normalized max {v * NORM:9.6f}")
    print(f"    {'TOTAL':22s} raw {RAW_TOTAL:3d} -> "
          f"{sum(RAW_WEIGHTS.values()) * NORM:9.6f}")

    cand = gpd.read_file(ENR, layer="candidates_enriched").to_crs(CRS_DIST)
    bb = gpd.read_file(WAT, layer="fcc_broadband_blockgroups").to_crs(CRS_DIST)

    # ---- dist_to_residential_km (the first TBD) --------------------------
    # Residential proxy: census block groups whose population density exceeds
    # 200 persons/km2. Block groups tile the state, so density is what
    # separates a subdivision from open desert.
    bb = bb.copy()
    bb["area_km2"] = bb.geometry.area / 1e6
    bb["pop_density"] = pd.to_numeric(bb["TotalPop"],
                                      errors="coerce") / bb["area_km2"]
    resid = bb[bb["pop_density"] >= 200]
    print(f"\n  residential proxy: {len(resid)} of {len(bb)} block groups at "
          f">=200 persons/km2")
    nr = gpd.sjoin_nearest(cand[["geometry"]], resid[["geometry"]],
                           how="left", distance_col="d")
    nr = nr[~nr.index.duplicated(keep="first")].reindex(cand.index)
    cand["dist_to_residential_km"] = nr["d"] / 1000
    cand["dist_to_residential_basis"] = (
        "DERIVED — distance to nearest census block group with population "
        "density >=200/km2 (FCC BDC Dec-2024 TotalPop / equal-area block "
        "group area). A density proxy, not a parcel-level land use survey.")

    def s_dist_resid(d):
        if pd.isna(d):
            return np.nan
        # 0.3 km ~ the 300 ft noise-study trigger in Phoenix's ordinance.
        return 4.0 if d >= 5 else 3.0 if d >= 2 else 2.0 if d >= 1 \
            else 1.0 if d >= 0.3 else 0.0
    cand["pol_dist_resid_pts"] = cand["dist_to_residential_km"].apply(
        s_dist_resid)

    # ---- prior_industrial_use (the second TBD) ---------------------------
    def s_prior_ind(r):
        if r["cand_type"] == "pop1_retired_plant":
            return 5.0
        n = r["substations_within_5km"]
        return 3.0 if n >= 3 else 2.0 if n >= 1 else 1.0
    cand["pol_prior_industrial_pts"] = cand.apply(s_prior_ind, axis=1)
    cand["prior_industrial_use_basis"] = np.where(
        cand["cand_type"] == "pop1_retired_plant",
        "DERIVED — site is a retired generating station: unambiguous prior "
        "industrial use (5/5)",
        "DERIVED — site is an existing substation; scored on density of "
        "electrical infrastructure within 5 km as an industrial-corridor "
        "proxy (max 3/5, since the substation parcel itself is not evidence "
        "the surrounding land is industrial)")

    # ---- political total --------------------------------------------------
    pri = [political_prior(j, c) for j, c in
           zip(cand["jurisdiction"], cand["county_gis"])]
    cand["pol_moratorium_pts"] = [p[0] for p in pri]
    cand["pol_no_ordinance_pts"] = [p[1] for p in pri]
    cand["pol_no_opposition_pts"] = [p[2] for p in pri]
    cand["political_prior_basis"] = [p[3] for p in pri]
    cand["political_risk_score"] = (
        cand["pol_moratorium_pts"] + cand["pol_no_ordinance_pts"]
        + cand["pol_no_opposition_pts"] + cand["pol_prior_industrial_pts"]
        + cand["pol_dist_resid_pts"])

    # ---- raw components ----------------------------------------------------
    ic = cand.apply(s_interconnection, axis=1)
    cand["sc_interconnection_raw"] = [x[0] for x in ic]
    cand["interconnection_basis"] = [x[1] for x in ic]
    cand["sc_substation_proximity_raw"] = cand.apply(s_sub_prox, axis=1)
    cand["sc_substation_voltage_raw"] = cand.apply(s_sub_volt, axis=1)
    cand["sc_transmission_raw"] = cand.apply(s_transmission, axis=1)
    cand["sc_water_raw"] = cand["water_risk_score"].astype(float)
    cand["sc_political_raw"] = cand["political_risk_score"].astype(float)
    cand["sc_broadband_raw"] = cand.apply(s_broadband, axis=1)

    comps = {
        "interconnection": "sc_interconnection_raw",
        "substation_proximity": "sc_substation_proximity_raw",
        "substation_voltage": "sc_substation_voltage_raw",
        "transmission": "sc_transmission_raw",
        "water": "sc_water_raw",
        "political": "sc_political_raw",
        "broadband": "sc_broadband_raw",
    }

    # ---- normalize, with explicit handling of unscoreable components ------
    total = pd.Series(0.0, index=cand.index)
    maxavail = pd.Series(0.0, index=cand.index)
    basis_bits = pd.Series("", index=cand.index)
    for name, col in comps.items():
        w = RAW_WEIGHTS[name] * NORM
        raw = cand[col]
        # Hard bounds check. A -999999 sentinel that escaped nulling once
        # produced a composite of -1,818,114; fail loudly rather than rank on
        # a poisoned number.
        bad = raw.notna() & ((raw < 0) | (raw > RAW_WEIGHTS[name]))
        if bad.any():
            raise RuntimeError(
                f"component '{name}' out of bounds [0,{RAW_WEIGHTS[name]}] "
                f"for {int(bad.sum())} rows; observed min={raw.min()}, "
                f"max={raw.max()}. Refusing to score — check for an unnulled "
                f"sentinel in the source field.")
        got = raw.notna()
        contrib = (raw / RAW_WEIGHTS[name] * w).where(got, 0.0)
        total += contrib
        maxavail += np.where(got, w, 0.0)
        cand[f"sc_{name}_norm"] = contrib
        basis_bits = basis_bits + np.where(
            got, f"{name}:{w:.3f} ", f"{name}:UNSCORED ")

    cand["score_raw_sum"] = total
    cand["score_max_available"] = maxavail
    cand["score_basis"] = basis_bits.str.strip()
    # Transparent rescale to a 100-point frame when a component is missing.
    cand["score_rescaled_to_100"] = np.where(
        maxavail > 0, total / maxavail * 100.0, np.nan)
    cand["composite_score"] = cand["score_raw_sum"]

    print(f"\n  components unscored (dataset gaps):")
    for name, col in comps.items():
        n = cand[col].isna().sum()
        if n:
            print(f"    {name:22s} {n:4d} candidates unscored")
    print(f"  score_max_available distribution: "
          f"{cand['score_max_available'].round(2).value_counts().to_dict()}")

    priv = cand[cand["land_status"] == "private"].copy()
    nonpriv = cand[cand["land_status"] != "private"].copy()
    priv = priv.sort_values("composite_score", ascending=False)
    nonpriv = nonpriv.sort_values("composite_score", ascending=False)

    print(f"\n  PRIVATE candidates: {len(priv)}, score range "
          f"{priv['composite_score'].min():.2f} - "
          f"{priv['composite_score'].max():.2f}")
    print(f"  NON-PRIVATE (excluded): {len(nonpriv)}, score range "
          f"{nonpriv['composite_score'].min():.2f} - "
          f"{nonpriv['composite_score'].max():.2f}")
    assert cand["composite_score"].max() <= 100.0001, "score exceeded 100"
    assert abs(sum(RAW_WEIGHTS.values()) * NORM - 100.0) < 1e-9

    cand.to_crs(CRS_WGS84).to_file(OUT, layer="candidates_scored",
                                   driver="GPKG")
    priv.to_crs(CRS_WGS84).to_file(OUT, layer="private_ranked", driver="GPKG")
    nonpriv.to_crs(CRS_WGS84).to_file(OUT, layer="excluded_ranked",
                                      driver="GPKG")
    print(f"\n  wrote -> {os.path.basename(OUT)}")
    print("\nSTEP 8 complete.")


if __name__ == "__main__":
    main()
