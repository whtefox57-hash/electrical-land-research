# STEP 10 — VERIFICATION

Run 2026-07-29 14:07:37 UTC. Every check below reopens the delivered files from disk.


## 1. GeoPackage reopened from disk

  15 layers in az_candidates.gpkg

| layer | features | CRS |
|---|---:|---|
| `candidates_private_ranked` | 166 | EPSG:4326 |
| `candidates_excluded_ranked` | 89 | EPSG:4326 |
| `candidates_all_scored` | 255 | EPSG:4326 |
| `land_ownership_all` | 17,585 | EPSG:4326 |
| `land_private` | 7,098 | EPSG:4326 |
| `substations` | 901 | EPSG:4326 |
| `transmission_lines` | 1,335 | EPSG:4326 |
| `retired_plants` | 14 | EPSG:4326 |
| `utility_territories` | 59 | EPSG:4326 |
| `ama_ina` | 11 | EPSG:4326 |
| `groundwater_basin` | 52 | EPSG:4326 |
| `cws_service_area` | 750 | EPSG:4326 |
| `nhd_perennial` | 18,992 | EPSG:4326 |
| `counties` | 15 | EPSG:4326 |
| `city_boundaries` | 91 | EPSG:4326 |
  [PASS] GeoPackage has >= 15 layers — 15
  [PASS] all candidate layers are EPSG:4326

## 2. Private-land filter — the check most likely to have leaked

  [PASS] EVERY top-25 candidate has land_status == 'private' — 25 rows checked, 0 violations
  [PASS] every top-25 candidate has acquirable == 'yes' — values: ['yes']
  [PASS] independent re-run of point-in-polygon agrees for all 25 — 25/25 agree

  Re-derived land_status independently from the BLM AZ full-res SMA layer rather than trusting the stored column. 25 of 25 agree.


## 3. Hand spot-checks against raw sources


### Cholla (rank 1)

- candidate lat/lon: `34.9394, -110.3033`
- EIA-860 plant workbook lat/lon: `34.9394, -110.3033` — MATCH
- county in candidate table: `NAVAJO`; EIA-860 county: `Navajo` — MATCH
- retired/announced MW in candidate table: `1,128.8`; recomputed from the raw unit-level EIA rows: `1,128.8` — MATCH
- land_status: `private` (acquirable `yes`)
  [PASS] Cholla: lat matches EIA plant workbook
  [PASS] Cholla: retired MW matches raw EIA unit rows
  [PASS] Cholla: county matches EIA plant workbook

### Springerville (rank 2)

- candidate lat/lon: `34.3186, -109.1639`
- EIA-860 plant workbook lat/lon: `34.3186, -109.1639` — MATCH
- county in candidate table: `APACHE`; EIA-860 county: `Apache` — MATCH
- retired/announced MW in candidate table: `849.6`; recomputed from the raw unit-level EIA rows: `849.6` — MATCH
- land_status: `private` (acquirable `yes`)
  [PASS] Springerville: lat matches EIA plant workbook
  [PASS] Springerville: retired MW matches raw EIA unit rows
  [PASS] Springerville: county matches EIA plant workbook

### Coronado (rank 3)

- candidate lat/lon: `34.5789, -109.2708`
- EIA-860 plant workbook lat/lon: `34.5789, -109.2708` — MATCH
- county in candidate table: `APACHE`; EIA-860 county: `Apache` — MATCH
- retired/announced MW in candidate table: `821.8`; recomputed from the raw unit-level EIA rows: `821.8` — MATCH
- land_status: `private` (acquirable `yes`)
  [PASS] Coronado: lat matches EIA plant workbook
  [PASS] Coronado: retired MW matches raw EIA unit rows
  [PASS] Coronado: county matches EIA plant workbook

## 4. Scoring integrity

  raw weights sum to 110; normalization factor 100/110 = 0.909090909

| component | raw | normalized |
|---|---:|---:|
| interconnection | 25 | 22.727273 |
| substation_proximity | 15 | 13.636364 |
| substation_voltage | 10 | 9.090909 |
| transmission | 10 | 9.090909 |
| water | 20 | 18.181818 |
| political | 25 | 22.727273 |
| broadband | 5 | 4.545455 |
| **TOTAL** | **110** | **100.000000** |
  [PASS] normalized weights sum to exactly 100
  [PASS] no composite score exceeds 100 — max = 93.6364
  [PASS] no composite score is negative — min = 39.0909
  [PASS] component columns re-sum to the stored composite — max deviation 0.00e+00

## 5. Required report

- **total candidates evaluated:** 255 (7 Pop 1 retired plants >=50 MW, 248 Pop 2 substations >=115 kV)
- **private-land candidates:** 166
- **score range, private:** 39.09 to 93.64
- **score range, all:** 39.09 to 93.64

**Top 5 counties among the top 25 private candidates:**

| county | count |
|---|---:|
| MARICOPA | 8 |
| MOHAVE | 6 |
| YUMA | 4 |
| NAVAJO | 2 |
| APACHE | 2 |

**Top 5 counties across all 166 private candidates:**

| county | count |
|---|---:|
| MARICOPA | 60 |
| PIMA | 35 |
| PINAL | 29 |
| MOHAVE | 11 |
| GILA | 7 |

- **high scorers excluded for land status:** 24 non-private candidates scored at or above the top-25 cut-off of 70.91

| land_status | count | acquirable |
|---|---:|---|
| federal_blm | 8 | `no` |
| state_trust | 5 | `auction_only` |
| tribal | 4 | `lease_only_bia` |
| federal_forest | 4 | `no` |
| federal_other | 3 | `no` |

- **inside an AMA:** 157 of 255 candidates; 5 of the top 25
- **inside an INA:** 26 of 255

## 6. Statewide ownership vs the known figures

| class | acres | pct | known pct | delta |
|---|---:|---:|---:|---:|
| tribal | 20,289,203 | 27.81% | 28.33 | -0.52 |
| private | 12,582,022 | 17.25% | 17.01 | +0.24 |
| federal_blm | 12,063,812 | 16.54% | 16.64 | -0.10 |
| federal_forest | 11,178,581 | 15.32% | 15.21 | +0.11 |
| state_trust | 9,275,903 | 12.71% | 12.47 | +0.24 |
| federal_other | 4,602,428 | 6.31% | 6.35 | -0.04 |
| military | 2,786,007 | 3.82% | 3.64 | +0.18 |
| municipal | 177,062 | 0.24% | 0.03 | +0.21 |
| unknown | 3,922 | 0.01% | 0.31 | -0.30 |

Total 72,958,940 acres = 99.99% of Arizona's 72,964,000 acres.

  [PASS] every class except municipal/unknown within 1.0 pt of known — largest deviation 0.52 pt
  [PASS] private land between 16% and 18% — 17.25%

## 7. Datasets that failed

  23 datasets succeeded, 2 failed.


### EIA-860M monthly

- endpoint: `https://www.eia.gov/electricity/data/eia860m/xls/may_generator2026.xlsx`
- time: 2026-07-29T13:40:35Z
- error: `ALL candidate months failed. may_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; april_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; march_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; february_generator2026.xlsx: `
- manual download: https://www.eia.gov/electricity/data/eia860m/

### EIA-860M parse

- endpoint: `/home/user/electrical-land-research/data/may_generator2026.xlsx`
- time: 2026-07-29T13:39:50Z
- error: `Excel file format cannot be determined, you must specify an engine manually.`
- manual download: /home/user/electrical-land-research/data/may_generator2026.xlsx

---

## RESULT: ALL CHECKS PASSED

