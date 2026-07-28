# METHOD — Texas powered-land screen

**Run date: 2026-07-28.** All data downloaded that day.
Reproduce with `scripts/arcgis_download.py`, then `scripts/build_screen.py`,
then `scripts/verify.py`.

Read the two sections at the bottom — **"What is derived vs read"** and
**"What would make this screen wrong"** — before you act on any number here.

---

## 1. The headline caveat

**There is no substation dataset in this screen.** Every documented source and
every fallback was refused by the network policy of the machine that ran this.
Substation proximity and substation voltage are 40 of your 100 rubric points,
and Population 2 is defined entirely by that layer.

In its place, the substation layer is **derived from transmission line
endpoints** — see §4. It is a positional proxy, not a substation inventory.
FCC broadband (10 more points) was also unreachable and is **not scored at all**.

So: scores here are computed from **90 of your 100 rubric points**, rescaled to
0–100, and 40 of those 90 rest on a proxy. Population 1 (retired plants) is
sound and fully sourced. Population 2 is the weak half.

---

## 2. Sources

| Dataset | Source | URL | Downloaded | Status |
|---|---|---|---|---|
| Transmission lines | HIFLD-derived hosted service, ArcGIS org `FiaPA4ga0iQKduv3` | `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0` | 2026-07-28 | **OK** — 10,804 features intersecting the Texas bbox; service-reported count matched the paged download exactly |
| Generators, retirements | EIA-860 2024 (final) | `https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip` | 2026-07-28 | **OK** |
| Generators, retirements | EIA-860 2025 (early release) | `https://www.eia.gov/electricity/data/eia860/xls/eia8602025ER.zip` | 2026-07-28 | **OK** |
| Generators, retirements | EIA-860M June 2026 (monthly, most current) | `https://www.eia.gov/electricity/data/eia860m/xls/june_generator2026.xlsx` | 2026-07-28 | **OK** |
| County boundaries | TIGERweb Counties, same ArcGIS org | `.../TIGERweb_Counties_v1/FeatureServer/0`, filtered `STATE='48'` | 2026-07-28 | **OK** — 254 features |
| Reservoirs | TWDB major reservoirs (SWP 2012) | `https://www.twdb.texas.gov/mapping/gisdata/doc/Existing_Reservoirs.zip` | 2026-07-28 | **OK** — 211 features |
| Rivers | TWDB major rivers (NAD83) | `https://www.twdb.texas.gov/mapping/gisdata/doc/Major_Rivers_dd83.zip` | 2026-07-28 | **OK** — 3,171 features |
| Groundwater districts | TWDB GCD Nov 2019 | `https://www.twdb.texas.gov/mapping/gisdata/doc/GCD_Shapefiles.zip` | 2026-07-28 | Downloaded, **not used** in scoring |
| **Substations** | — | — | — | **FAILED — see §3** |
| **Broadband** | — | — | — | **FAILED — see §3** |

Raw files are in `data/raw/`, unmodified. They are excluded from git (see
`.gitignore`) because they are large and reproducible; nothing was saved that
was not downloaded.

---

## 3. What failed, and the exact errors

### Substations (dataset A)

| Host | Result |
|---|---|
| `services2.arcgis.com/FiaPA4ga0iQKduv3` | Reachable. **No substations layer exists in the org.** All 220 services enumerated; the only electric ones are `US_Electric_Power_Transmission_Lines`, `Power_Plants_in_the_US`, `Aggregation_of_Power_Plants_in_the_U_S__by_hexagon_bins`. Consistent with the HIFLD Secure migration. |
| `www.arcgis.com` (item search) | HTTP 403, CONNECT tunnel refused by egress policy |
| `services1.arcgis.com`, `services3`, `services7`, `services9` | HTTP 403, CONNECT refused |
| `hub.arcgis.com`, `opendata.arcgis.com`, `gisdata.arcgis.com` | HTTP 403, CONNECT refused |
| `atlas.eia.gov` | Reachable (200). Pulled DCAT-US 1.1 and DCAT-AP 2.0.1 catalogs: **89 datasets, zero substation entries.** `/search` is a JavaScript shell returning no server-side results. |
| `catalog.data.gov` CKAN API | Reachable, returns `{"message":"Not Found"}` — `package_search` no longer responds |
| `gis.ercot.com` | HTTP 403, CONNECT refused |
| `overpass-api.de`, `overpass.kumi.systems`, `overpass.osm.ch`, `overpass.private.coffee` | HTTP 403, CONNECT refused |
| `download.geofabrik.de` (OSM extracts) | HTTP 403, CONNECT refused |
| `data.geographic.texas.gov`, `data.tnris.org` | HTTP 403, CONNECT refused |

The proxy's own diagnostics confirmed these as organization policy denials
(`connect_rejected … gateway answered 403 to CONNECT`), which its documentation
says must not be retried or routed around.

**To fix it:** obtain the substation layer on a machine with open network access
and drop it in `data/raw/` with `substation` in the filename
(`.geojson`, `.gpkg`, `.shp`, `.zip`, or `.csv` with lat/lon columns).
`build_screen.py` auto-detects it via `find_real_substations()`, maps common
field spellings, replaces the proxy, restores the full 25+15 points, and rebuilds
Population 2 from real substations. No code change needed. Suggested sources are
in `DATA_STATUS.md`.

### FCC broadband (dataset D)

| Host | Result |
|---|---|
| `broadbandmap.fcc.gov` | Timeout, 0 bytes, on both HTTP/2 and HTTP/1.1 |
| `www.fcc.gov`, `api.fcc.gov` | HTTP 403, CONNECT refused |
| `us-fcc.app.box.com` (BDC bulk host) | HTTP 403, CONNECT refused |
| `opendata.fcc.gov` | Reachable (200), not mined — a Form 477 fallback would be a different vintage and definition from BDC and was not worth substituting silently |

Broadband is **excluded from the scoring denominator**, not scored zero.
`broadband_providers` is present in the outputs and is explicitly null;
`broadband_note` records why.

---

## 4. The derived substation proxy — how it works and where it lies to you

Transmission lines terminate at substations and switchyards, so a line endpoint
is a strong positional indicator of one.

1. Every line's first and last vertex is extracted (MultiLineStrings exploded
   first): **21,776 endpoints from 10,804 lines**.
2. Endpoints are projected to EPSG:3081 and clustered by buffering each by
   125 m, dissolving, and exploding — so endpoints within **250 m** merge into
   one node. Result: **7,305 clusters, 4,680 of them inside Texas.**
3. Each node gets: `max_voltage_kv` / `min_voltage_kv` (highest and lowest
   voltage among lines terminating there), `n_line_ends`, `n_inferred`, and
   `sub_name` from the source `SUB_1`/`SUB_2` fields where those are not
   placeholders.
4. `proxy_confidence`: `high` = 3+ line ends and a name; `medium` = 2+ ends;
   `low` = a single end. Population 2 uses only high and medium — **451
   low-confidence single-endpoint nodes were dropped**, since a lone endpoint is
   more likely a segment split or a border clip than a substation.

**Where this proxy is wrong:**

- **A node is not a confirmed substation.** Taps, splices, and points where the
  source simply split one line into two segments all produce nodes.
- **Voltage is the line's voltage, not the substation's transformer rating.** A
  real substation's max voltage is at least the highest line reaching it, so this
  **under-reports** wherever a high side exists whose line is unmapped. It says
  nothing at all about transformer capacity or available headroom — which is the
  number that actually decides whether you can get service.
- **4,328 of 10,804 source lines carry `INFERRED='Y'`** (geometry inferred by
  the publisher), so their endpoints are correspondingly less certain. The count
  per node is retained as `n_inferred`.
- **Naming is sparse.** `SUB_1` is `NOT AVAILABLE` on 1,695 lines and `SUB_2` on
  5,616; many more are `UNKNOWN<digits>`. All are nulled, never scored.
- **Population 2 is largely self-referential.** Its members *are* proxy nodes,
  so their `dist_substation_m` is 0 by construction and they all take the full
  25 proximity points. Note this is inherent in the rubric as written — defining
  Population 2 as substations means every Population 2 site scores maximum on
  substation proximity, real data or not. They are differentiated only by
  voltage, transmission and water. **Treat Population 2 as map context, not as a
  ranking, until real substation data lands.**

---

## 5. Candidate construction

**Population 1** — Texas plants with retired or announced-retirement capacity
≥ 50 MW.

Unit records are unioned across all three EIA releases — 860M June 2026
(`Retired`, and `Operating` rows carrying a planned retirement year), 860 2025ER
and 860 2024 (`Retired and Canceled` with `Status='RE'`, and `Operable` rows
with a planned retirement year) — then deduplicated on
`(plant_code, generator_id)`, **preferring the most current release**
(860M > 2025ER > 2024). Retirements are included from **2010** onward.

- 665 rows across releases → **289 unique (plant, generator)** after dedup
- → **131 Texas plants** with any retired/announced capacity
- → **56 plants at or above 50 MW**

Coordinates come from the EIA Plant file (860) or the sheet itself (860M).
**Zero units were dropped for missing coordinates.**

**Population 2** — proxy nodes ≥ 138 kV, of confidence high/medium, more than
2,000 m from any Population 1 site: 4,680 nodes → 2,801 at ≥138 kV → **2,704**
after the exclusion buffer.

**Total candidates evaluated: 2,760.**

### A note on the EIA files that will bite you if you re-run this

The header row offset is **not stable across EIA releases**: 860 2024 puts
headers on row 2 (`skiprows=1`), 860 2025ER on row 3 (`skiprows=2`). Hardcoding
either silently consumes the first data row as column names. The loader detects
the offset by looking for known columns instead.

Also, blank `Planned Retirement Year` cells arrive as **empty strings, not
nulls**. A bare `.notna()` therefore counts operating units as announced
retirements — this produced a real false 206 MW on Decker Creek during
development, caught by `verify.py`. All year fields are coerced with
`pd.to_numeric(..., errors='coerce')` before any null test.

---

## 6. Distances

All geometry reprojected to **EPSG:3081** (NAD83 / Texas State Mapping System,
metres) before any measurement. No distance is computed in degrees.
Point-to-line distances are true perpendicular distances to the line geometry,
not to vertices.

---

## 7. Scoring

Rubric weights live in the `CONFIG` dict at the top of `scripts/build_screen.py`.

| Factor | Weight | Status |
|---|---|---|
| Existing interconnection | 30 | **scored** — real EIA data |
| Substation proximity | 25 | scored **against the proxy** |
| Substation voltage | 15 | scored **against the proxy** |
| Transmission proximity + voltage | 15 | **scored** — real HIFLD data |
| Broadband | 10 | **EXCLUDED** — source unreachable |
| Water proximity | 5 | **scored** — real TWDB data |

Available total = **90**. Final score = `score_raw / 90 × 100`, so scores read
0–100 and stay comparable. `score_max_available` (90) and `score_basis` are
carried on every row so the composition is never lost. Component scores are
also kept individually (`score_interconnection`, `score_substation_prox`,
`score_substation_volt`, `score_transmission`, `score_water`) so you can
re-weight without re-running the spatial work.

**Interconnection** uses plant-level `retired_mw + announced_mw`:
≥500 MW → 30, 200–499 → 22, 50–199 → 14. A **0.5 multiplier** applies where the
latest retirement is more than 10 years before the screen year
(`interconnection_stale_flag`).

**Substation proximity** on distance to nearest node: ≤1 km → 25, ≤3 km → 18,
≤5 km → 10, ≤10 km → 3, beyond → 0.

**Substation voltage** uses the **max voltage among nodes within 5 km**, falling
back to the nearest node's voltage if none are within 5 km — a derived
interpretation, since the rubric did not specify which of the two it meant:
≥345 kV → 15, 230–344 → 12, 138–229 → 8, 69–137 → 3.

**Transmission (0–15)** — formula, as requested:

```
score = 15 × distance_factor × voltage_factor
distance_factor: ≤500 m → 1.00, ≤1 km → 0.85, ≤2 km → 0.65,
                 ≤5 km → 0.40, ≤10 km → 0.15, beyond → 0
voltage_factor:  ≥345 kV → 1.00, ≥230 → 0.85, ≥138 → 0.65,
                 ≥69 → 0.35, below or unknown → 0.15
```

Evaluated for **every line within 10 km and maximised**, not just the nearest
line. Rationale: a site 3 km from a 345 kV line is a better large-load prospect
than one 200 m from a 69 kV lateral, and scoring only the nearest line inverts
that. `dist_transmission_m` and `nearest_line_kv` still report the nearest line
for reference, so a low `nearest_line_kv` alongside a high `score_transmission`
is expected, not a bug.

**Water (0–5)**: ≤1 km → 5, ≤5 km → 4, ≤10 km → 3, ≤25 km → 1. Distance is to
the nearest TWDB major reservoir or major river. This is a **proximity** measure
only — it implies nothing about water rights, availability, or whether you could
ever get an allocation.

---

## 8. What is derived vs read

**Read directly from source, unaltered:**
`plant_code`, `plant_name`, `county_eia`, `latitude`, `longitude`,
`nameplate_mw` (per unit), `technology`, retirement and planned-retirement
years, transmission `VOLTAGE`/`OWNER`/`STATUS`/`VOLT_CLASS`/`SUB_1`/`SUB_2`,
county names and boundaries, reservoir and river geometry.

**Derived by computation** (all reproducible from the raw files):

| Field | How |
|---|---|
| `retired_mw`, `announced_mw`, `site_mw` | plant-level sums of unit nameplate MW after cross-release dedup |
| `latest_retire_year`, `years_since_retirement` | max unit retirement year; screen year minus that |
| `n_units` | count of deduplicated units per plant |
| `retirement_beyond_horizon` | flag: no past retirement **and** announced retirement after 2036 |
| `interconnection_stale_flag` | latest retirement more than 10 years old |
| everything in the proxy substation layer | §4 |
| `dist_substation_m`, `nearest_substation_kv`, `nearest_substation_name` | nearest-neighbour against the **proxy** layer |
| `substations_within_5km`, `max_substation_kv_within_5km` | spatial join, 5 km buffer, against the **proxy** layer |
| `dist_transmission_m`, `nearest_line_kv`, `nearest_line_owner` | nearest-neighbour against transmission lines |
| `lines_within_5km`, `lines_5km_*` | spatial join, 5 km buffer, binned by voltage class |
| `score_transmission`, `max_line_kv_within_10km` | §7 formula, maximised over 10 km |
| `county` | **spatial join to TIGER counties**, independent of EIA's `county_eia`. Both are kept; they agree on all Population 1 sites in the top 25 |
| `dist_water_m` | nearest-neighbour to reservoirs + rivers |
| all `score_*`, `score_raw`, `score` | §7 |
| `google_maps_url` | built from the site's own lat/lon |

**Null by declaration, not measured:** `broadband_providers` (with
`broadband_note` giving the reason). `county_cad_note` is deliberately blank for
your parcel IDs.

**Values converted to null rather than scored:** transmission `VOLTAGE` uses
`-999999` as a missing sentinel — **348 features** were nulled. Substation names
of `NOT AVAILABLE`, `UNKNOWN`, `UNKNOWN<digits>`, `N/A` were nulled. No sentinel
was ever treated as a number.

**Nothing was estimated, interpolated, or synthesised.** No coordinate in these
outputs was invented; every one traces to an EIA plant record or to source line
geometry.

---

## 9. Results summary

- Candidates evaluated: **2,760** (56 Population 1, 2,704 Population 2)
- Score range, all candidates: **24.7 – 100.0**; top 25: **83.3 – 100.0**
- **All 25 of the top 25 are Population 1** — retired or retiring plants. The
  proxy did not flood the ranking.
- The top 25 span **19 counties**; the most concentrated is Bexar with 4
  (J K Spruce, J T Deely, O W Sommers, V H Braunig — all CPS Energy sites on
  adjacent land, so this is a genuine cluster, not a rubric artefact).
- `verify.py`: **19/19 checks pass**, including an independent re-derivation of
  retired/announced MW for the top 3 sites straight from the raw workbooks.

---

## 10. What would make this screen WRONG

Ranked by how likely it is to burn you.

1. **The substation layer is not real.** 40 of 90 scored points rest on line
   endpoints. If a node is a splice rather than a substation, that site's 25
   proximity points are fiction. **Do not quote substation proximity or voltage
   to anyone until you have the real layer.**
2. **Line voltage is not substation capacity, and neither is transformer
   headroom.** Nothing here measures whether a substation has spare capacity to
   serve a 100 MW+ load. A 345 kV substation with zero headroom scores exactly
   like one with 500 MW available. This is the single biggest gap between this
   screen and reality, and it is what an Electrical Power Report actually tells
   you.
3. **Retired interconnection rights may be gone.** The screen flags retirements
   older than 10 years and halves their score, but that is a guess at a legal
   reality that varies by utility and by ERCOT queue position. Rights may have
   been released, resold, or reduced. Some of these sites may have had their
   interconnection agreements terminated entirely.
4. **The land may not be for sale, or may not be separable.** A retired unit
   often sits on a parcel still hosting operating units, a switchyard the
   utility keeps, or ash ponds and remediation obligations. Bexar County's four
   sites are one campus. `county_cad_note` is blank for a reason — parcel
   verification is not in this screen.
5. **Announced retirements far in the future are not opportunities.** Five sites
   have no past retirement and a retirement announced after 2036 — Jones (2058),
   Harrington (2040), Hale Community Wind Farm (2044), Madero Grid (2042),
   Ignacio Grid Energy Storage System (2042). Two of them, **Jones (rank 19) and
   Harrington (rank 17), are in your top 25.** They are operating today and are
   not acquirable. The rubric as written puts no upper bound on how far out an
   announced retirement may be, so they score as though already shut. They are
   flagged in `retirement_beyond_horizon`; set `announced_horizon_drop=True` in
   CONFIG to exclude them.
6. **Nameplate MW is not deliverable capacity, and MW retired is not MW you can
   have.** Nameplate is a plate rating; summer capability is lower, and what the
   interconnection will actually support is a separate question again. Battery
   and wind "retirements" in this set carry nameplate figures that mean something
   quite different from a retired coal unit's.
7. **Broadband is entirely unmeasured.** No fiber signal of any kind is in these
   scores. Long-haul routes are proprietary regardless; even with FCC data it
   would have been a weak proxy.
8. **Water proximity is not water access.** See §7.
9. **Vintage mismatch.** Transmission geometry is HIFLD-derived with per-feature
   `SOURCEDATE` values that were not audited and may be years old. EIA data is
   current to June 2026. A substation built in 2025 may be missing entirely.
10. **The 2 km Population 2 exclusion buffer is arbitrary,** as are the 250 m
    clustering tolerance and the 50 MW floor. All are in CONFIG. Changing the
    clustering tolerance changes the node count and therefore every substation
    distance in the file.
11. **The rubric itself is untested.** It is a first draft written before anyone
    looked at these counties. Nothing here has been calibrated against a real
    Electrical Power Report or a single conversation with a utility account
    manager. Weights are guesses.
12. **Ignore `mean_score` in the county summary.** It averages across proxy
    nodes and is close to meaningless — a county holding nothing but proxy nodes
    scores identically to one holding a gigawatt of retired coal. The file is
    sorted by `pop1_candidates` then `total_site_mw` for exactly this reason.
    Use `total_retired_mw`, `pop1_candidates` and `pop1_best_site`; only 38 of
    the 234 counties contain a real retired or retiring plant at all.

---

## 11. Outputs

| File | What |
|---|---|
| `outputs/tx_candidates.gpkg` | 5 layers, all EPSG:3081: `candidates` (2,760), `substations_proxy` (4,680), `transmission_lines` (10,804), `counties` (254), `water` (3,382) |
| `outputs/top25_candidates.csv` | Top 25, 51 columns, with `google_maps_url` and blank `county_cad_note` |
| `outputs/COUNTY_SUMMARY.csv` | 234 counties, **sorted so counties containing a real retired/retiring plant come first** (38 of them). Columns split Population 1 from Population 2: `pop1_candidates`, `total_retired_mw`, `total_announced_mw`, `total_site_mw`, `pop1_mean_score`, `pop1_best_site`, `max_score`, then `pop2_candidates`, `candidates`, `mean_score` |
| `outputs/preview_map.png` | Static overview, top 25 labelled. No basemap — a sanity check, not the deliverable |
| `scripts/build_qgis_project.py` | **PyQGIS script that builds `outputs/screen.qgz`.** Run it from the QGIS Python console |
| `outputs/_run_report.json` | Machine-readable run log and failure list |

### Why there is no screen.qgz in this repo

The container that produced these outputs **has no QGIS installed**, so a
hand-authored `.qgz` XML could not be opened or validated. Shipping an untested
project file that might fail to load is worse than shipping a script that
provably builds one on your machine — so the fallback your brief allowed was
taken.

**To get your map:** open QGIS → `Plugins > Python Console` (Ctrl+Alt+P) →
Show Editor → open `scripts/build_qgis_project.py` → Run. Or paste:

```python
exec(open('/full/path/to/scripts/build_qgis_project.py').read())
```

It loads all five layers, styles candidates graduated by score (pale yellow →
dark red, sized by score), substations sized and coloured by voltage,
transmission coloured by voltage class, adds an **OpenStreetMap XYZ basemap at
the bottom**, labels sites scoring ≥83, sets project CRS to EPSG:3081, zooms to
the candidates, and writes `outputs/screen.qgz`. It uses manual renderer ranges
rather than the `createRenderer` convenience wrappers, whose signatures have
shifted between QGIS releases.
