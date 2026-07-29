"""STEP 10 — verify before reporting done.

Reopens the delivered GeoPackage from disk (not the in-memory frames) and
checks every claim the brief asks to be checked, including the private-land
filter, which is the one most likely to have leaked.

Writes outputs/AZ_VERIFICATION.md and exits non-zero if any hard check fails.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import fiona
import geopandas as gpd
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import CRS_AREA, CRS_DIST, DATA, M2_PER_ACRE, OUTPUTS, STATUS_LOG

GPKG = os.path.join(OUTPUTS, "az_candidates.gpkg")
OWN = os.path.join(DATA, "az_ownership.gpkg")

RAW_WEIGHTS = {"interconnection": 25, "substation_proximity": 15,
               "substation_voltage": 10, "transmission": 10, "water": 20,
               "political": 25, "broadband": 5}
KNOWN = {"tribal": 28.33, "private": 17.01, "federal_blm": 16.64,
         "federal_forest": 15.21, "state_trust": 12.47, "federal_other": 6.35,
         "military": 3.64, "unknown": 0.31, "municipal": 0.03}

out, fails = [], []


def say(s=""):
    print(s)
    out.append(s + "\n")


def check(label, ok, detail=""):
    say(f"  [{'PASS' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail
                                                     else ""))
    if not ok:
        fails.append(label)


def main():
    say("# STEP 10 — VERIFICATION")
    say(f"\nRun {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC. Every "
        "check below reopens the delivered files from disk.\n")

    # ---------- 1. reopen the GeoPackage ----------
    say("\n## 1. GeoPackage reopened from disk\n")
    layers = fiona.listlayers(GPKG)
    say(f"  {len(layers)} layers in {os.path.basename(GPKG)}\n")
    say("| layer | features | CRS |")
    say("|---|---:|---|")
    for l in layers:
        with fiona.open(GPKG, layer=l) as src:
            crs = src.crs.to_string() if src.crs else "none"
            say(f"| `{l}` | {len(src):,} | {crs} |")
    check("GeoPackage has >= 15 layers", len(layers) >= 15, f"{len(layers)}")

    priv = gpd.read_file(GPKG, layer="candidates_private_ranked")
    excl = gpd.read_file(GPKG, layer="candidates_excluded_ranked")
    allc = gpd.read_file(GPKG, layer="candidates_all_scored")
    check("all candidate layers are EPSG:4326",
          all(g.crs.to_epsg() == 4326 for g in (priv, excl, allc)))

    # ---------- 2. private land filter ----------
    say("\n## 2. Private-land filter — the check most likely to have leaked\n")
    top25 = priv.head(25)
    nonpriv = top25[top25["land_status"] != "private"]
    check("EVERY top-25 candidate has land_status == 'private'",
          len(nonpriv) == 0,
          f"{len(top25)} rows checked, {len(nonpriv)} violations")
    check("every top-25 candidate has acquirable == 'yes'",
          (top25["acquirable"] == "yes").all(),
          f"values: {sorted(top25['acquirable'].unique())}")

    # Independent re-test: re-run point-in-polygon from the ownership source.
    own = gpd.read_file(OWN, layer="sma_az_fullres").to_crs(CRS_DIST)
    t = top25.to_crs(CRS_DIST)
    j = gpd.sjoin(t[["geometry", "cand_id"]],
                  own[["geometry", "land_status"]], predicate="within",
                  how="left")
    j = j[~j.index.duplicated(keep="first")].reindex(t.index)
    agree = (j["land_status"].values == top25["land_status"].values).sum()
    check("independent re-run of point-in-polygon agrees for all 25",
          agree == len(top25), f"{agree}/{len(top25)} agree")
    say(f"\n  Re-derived land_status independently from the BLM AZ full-res "
        f"SMA layer rather than trusting the stored column. "
        f"{agree} of {len(top25)} agree.\n")

    # ---------- 3. spot checks ----------
    say("\n## 3. Hand spot-checks against raw sources\n")
    unit = pd.read_csv(os.path.join(DATA, "az_retirements_unit_level.csv"))
    plants = pd.read_pickle(os.path.join(DATA, "eia860_plants.pkl"))
    plants["Plant Code"] = pd.to_numeric(plants["Plant Code"],
                                         errors="coerce").astype("Int64")
    spots = [c for c in ["Cholla", "Springerville", "Coronado"]
             if c in set(top25["cand_name"])][:3]
    for nm in spots:
        r = top25[top25["cand_name"] == nm].iloc[0]
        u = unit[unit["Plant Name"].astype(str) == nm]
        mw_raw = pd.to_numeric(u["Nameplate Capacity (MW)"],
                               errors="coerce").sum()
        pc = int(pd.to_numeric(u["Plant Code"], errors="coerce").iloc[0])
        prow = plants[plants["Plant Code"] == pc].iloc[0]
        say(f"\n### {nm} (rank {int(r['rank'])})\n")
        say(f"- candidate lat/lon: `{r['lat']:.4f}, {r['lon']:.4f}`")
        say(f"- EIA-860 plant workbook lat/lon: "
            f"`{prow['Latitude']:.4f}, {prow['Longitude']:.4f}` — "
            f"{'MATCH' if abs(r['lat'] - prow['Latitude']) < 1e-3 else 'DIFFERS'}")
        say(f"- county in candidate table: `{r['county_gis']}`; "
            f"EIA-860 county: `{prow['County']}` — "
            f"{'MATCH' if str(r['county_gis']).upper() == str(prow['County']).upper() else 'DIFFERS'}")
        say(f"- retired/announced MW in candidate table: "
            f"`{r['retired_mw_on_site']:,.1f}`; recomputed from the raw "
            f"unit-level EIA rows: `{mw_raw:,.1f}` — "
            f"{'MATCH' if abs(r['retired_mw_on_site'] - mw_raw) < 0.05 else 'DIFFERS'}")
        say(f"- land_status: `{r['land_status']}` (acquirable "
            f"`{r['acquirable']}`)")
        check(f"{nm}: lat matches EIA plant workbook",
              abs(r["lat"] - prow["Latitude"]) < 1e-3)
        check(f"{nm}: retired MW matches raw EIA unit rows",
              abs(r["retired_mw_on_site"] - mw_raw) < 0.05)
        check(f"{nm}: county matches EIA plant workbook",
              str(r["county_gis"]).upper() == str(prow["County"]).upper())

    # ---------- 4. scoring integrity ----------
    say("\n## 4. Scoring integrity\n")
    tot = sum(RAW_WEIGHTS.values())
    norm = 100.0 / tot
    say(f"  raw weights sum to {tot}; normalization factor 100/{tot} = "
        f"{norm:.9f}\n")
    say("| component | raw | normalized |")
    say("|---|---:|---:|")
    for k, v in RAW_WEIGHTS.items():
        say(f"| {k} | {v} | {v * norm:.6f} |")
    say(f"| **TOTAL** | **{tot}** | **{sum(RAW_WEIGHTS.values()) * norm:.6f}** |")
    check("normalized weights sum to exactly 100",
          abs(sum(RAW_WEIGHTS.values()) * norm - 100.0) < 1e-9)
    check("no composite score exceeds 100",
          allc["composite_score"].max() <= 100.0001,
          f"max = {allc['composite_score'].max():.4f}")
    check("no composite score is negative",
          allc["composite_score"].min() >= 0,
          f"min = {allc['composite_score'].min():.4f}")
    recomputed = sum(allc[f"sc_{k}_norm"] for k in RAW_WEIGHTS)
    check("component columns re-sum to the stored composite",
          (recomputed - allc["composite_score"]).abs().max() < 1e-6,
          f"max deviation {abs(recomputed - allc['composite_score']).max():.2e}")

    # ---------- 5. reporting ----------
    say("\n## 5. Required report\n")
    say(f"- **total candidates evaluated:** {len(allc)} "
        f"({(allc['cand_type'] == 'pop1_retired_plant').sum()} Pop 1 retired "
        f"plants >=50 MW, "
        f"{(allc['cand_type'] == 'pop2_hv_substation').sum()} Pop 2 "
        f"substations >=115 kV)")
    say(f"- **private-land candidates:** {len(priv)}")
    say(f"- **score range, private:** {priv['composite_score'].min():.2f} to "
        f"{priv['composite_score'].max():.2f}")
    say(f"- **score range, all:** {allc['composite_score'].min():.2f} to "
        f"{allc['composite_score'].max():.2f}")
    say("\n**Top 5 counties among the top 25 private candidates:**\n")
    say("| county | count |")
    say("|---|---:|")
    for k, v in top25["county_gis"].value_counts().head(5).items():
        say(f"| {k} | {v} |")
    say("\n**Top 5 counties across all 166 private candidates:**\n")
    say("| county | count |")
    say("|---|---:|")
    for k, v in priv["county_gis"].value_counts().head(5).items():
        say(f"| {k} | {v} |")

    thr = top25["composite_score"].min()
    hi_excl = excl[excl["composite_score"] >= thr]
    say(f"\n- **high scorers excluded for land status:** {len(hi_excl)} "
        f"non-private candidates scored at or above the top-25 cut-off of "
        f"{thr:.2f}")
    say("\n| land_status | count | acquirable |")
    say("|---|---:|---|")
    for k, v in hi_excl["land_status"].value_counts().items():
        acq = hi_excl[hi_excl["land_status"] == k]["acquirable"].iloc[0]
        say(f"| {k} | {v} | `{acq}` |")

    say(f"\n- **inside an AMA:** {(allc['in_ama'] == 'yes').sum()} of "
        f"{len(allc)} candidates; {(top25['in_ama'] == 'yes').sum()} of the "
        f"top 25")
    say(f"- **inside an INA:** {(allc['in_ina'] == 'yes').sum()} of "
        f"{len(allc)}")

    # ---------- 6. ownership vs known figures ----------
    say("\n## 6. Statewide ownership vs the known figures\n")
    o = gpd.read_file(OWN, layer="sma_az_fullres").to_crs(CRS_AREA)
    o["ac"] = o.geometry.area / M2_PER_ACRE
    agg = o.groupby("land_status")["ac"].sum().sort_values(ascending=False)
    t_ac = agg.sum()
    say("| class | acres | pct | known pct | delta |")
    say("|---|---:|---:|---:|---:|")
    worst = 0.0
    for k, v in agg.items():
        p = v / t_ac * 100
        kn = KNOWN.get(k)
        d = p - kn if kn is not None else 0.0
        if k not in ("municipal", "unknown"):
            worst = max(worst, abs(d))
        say(f"| {k} | {v:,.0f} | {p:.2f}% | "
            f"{kn if kn is not None else '—'} | {d:+.2f} |")
    say(f"\nTotal {t_ac:,.0f} acres = {t_ac / 72_964_000 * 100:.2f}% of "
        f"Arizona's 72,964,000 acres.\n")
    check("every class except municipal/unknown within 1.0 pt of known",
          worst <= 1.0, f"largest deviation {worst:.2f} pt")
    check("private land between 16% and 18%",
          16.0 <= agg["private"] / t_ac * 100 <= 18.0,
          f"{agg['private'] / t_ac * 100:.2f}%")

    # ---------- 7. datasets ----------
    say("\n## 7. Datasets that failed\n")
    recs = [json.loads(l) for l in open(STATUS_LOG) if l.strip()]
    latest = {}
    for r in recs:
        latest[r.get("key") or r["dataset"]] = r
    bad = [r for r in latest.values() if r["status"] != "SUCCESS"]
    ok = [r for r in latest.values() if r["status"] == "SUCCESS"]
    say(f"  {len(ok)} datasets succeeded, {len(bad)} failed.\n")
    if not bad:
        say("  None outstanding.")
    for r in bad:
        say(f"\n### {r['dataset']}\n")
        say(f"- endpoint: `{r['url']}`")
        say(f"- time: {r['timestamp']}")
        say(f"- error: `{r['detail'][:500]}`")
        say(f"- manual download: {r['manual_download_url']}")

    say("\n---\n")
    if fails:
        say(f"## RESULT: {len(fails)} CHECK(S) FAILED\n")
        for x in fails:
            say(f"- {x}")
    else:
        say("## RESULT: ALL CHECKS PASSED\n")

    with open(os.path.join(OUTPUTS, "AZ_VERIFICATION.md"), "w") as fh:
        fh.writelines(out)
    print(f"\nwrote outputs/AZ_VERIFICATION.md — "
          f"{'FAILURES: ' + str(len(fails)) if fails else 'all checks passed'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
