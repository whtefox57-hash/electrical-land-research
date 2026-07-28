# Step 2 data acquisition status

Run date: **2026-07-28**. Environment: Claude Code remote container (Linux), all
outbound HTTPS through a policy-enforcing egress proxy.

Nothing in this file is estimated. Counts are read directly from the downloaded
files. Where a dataset failed, the failure is recorded verbatim.

---

## Step 1 — environment: PASS

Python 3.11.15 venv at `.venv/`. All required packages import:

| package | version |
|---|---|
| geopandas | 1.1.4 |
| pandas | 3.0.5 |
| requests | 2.34.2 |
| shapely | 2.1.2 |
| pyproj | 3.7.2 |
| fiona | 1.10.1 |
| openpyxl | 3.1.5 |
| matplotlib | 3.11.1 |

QGIS is **not** installed in this container. That only affects how output 3 is
produced — see "Impact" below.

---

## Downloaded successfully

| # | Dataset | File | Size | Verified content |
|---|---|---|---|---|
| B | Electric power transmission lines | `data/raw/transmission_lines_tx.geojson` | 19.8 MB | **10,804** features intersecting the Texas bbox. Service reported 10,804 matching; paged download returned exactly 10,804. |
| C | EIA-860 2024 (final) | `data/raw/eia8602024.zip` | 22.1 MB | 13 files incl. `3_1_Generator_Y2024.xlsx`, `2___Plant_Y2024.xlsx` |
| C | EIA-860 2025 (early release) | `data/raw/eia8602025ER.zip` | 23.3 MB | see breakdown below |
| C | EIA-860M June 2026 (monthly) | `data/raw/eia860m_june2026.xlsx` | 13.9 MB | 7 sheets; **463** TX rows on `Retired`, **561** TX rows on `Planned` |
| — | Texas county boundaries | `data/raw/counties_tx.geojson` | — | **254** features (correct count for Texas) |
| E | TWDB existing reservoirs | `data/raw/twdb_Existing_Reservoirs.zip` | 15.1 MB | not yet unpacked |
| E | TWDB major rivers | `data/raw/twdb_Major_Rivers_dd83.zip` | 1.9 MB | not yet unpacked |
| E | TWDB groundwater conservation districts | `data/raw/twdb_GCD_Shapefiles.zip` | 5.4 MB | not yet unpacked |

### Transmission line fields available (read from service schema, not derived)
`ID, TYPE, STATUS, NAICS_CODE, NAICS_DESC, SOURCE, SOURCEDATE, VAL_METHOD,
VAL_DATE, OWNER, VOLTAGE, VOLT_CLASS, INFERRED, SUB_1, SUB_2`

`SUB_1` / `SUB_2` name the substation at each end of a line. They are **names
only, with no coordinates** — see the substation blocker below.

### EIA-860 2025ER Texas breakdown (counts read directly from the file)

- `Retired and Canceled` sheet, Texas: **374** generator rows
  (Status `RE` retired = 253, `CN` canceled = 104, `IP` indefinitely postponed = 17)
- Texas rows with Status `RE` and retirement year >= 2010: **150** generator rows
- Those roll up to **67 distinct plants**
- **All 67 have latitude/longitude** in `2___Plant_Y2025_Early_Release.xlsx` — zero missing
- `Operable` sheet, Texas rows carrying a planned retirement year: **36** rows across **17 plants**

Preliminary size bands, 2025ER source only, plant-level sum of nameplate MW,
retirements from 2010 onward. This is a **lower bound** — it does not yet include
860M, the 2024 final file, or announced retirements:

| band | plants |
|---|---|
| >= 500 MW | 13 |
| 200–499 MW | 8 |
| 50–199 MW | 7 |
| **total >= 50 MW (Population 1 floor)** | **28** |

---

## BLOCKED — dataset A: electric substations

**This is the critical failure.** Every documented source and every fallback is
refused by this container's egress policy. I did not substitute anything for it.

| Host tried | Result |
|---|---|
| `services2.arcgis.com/FiaPA4ga0iQKduv3` (the HIFLD-derived org) | Reachable, but **the org has no substations layer**. I enumerated all 220 services; only `US_Electric_Power_Transmission_Lines`, `Power_Plants_in_the_US` and `Aggregation_of_Power_Plants_in_the_U_S__by_hexagon_bins` are electric. Consistent with substations having moved to HIFLD Secure. |
| `www.arcgis.com` (item search) | `403` — CONNECT tunnel refused by egress policy |
| `services1/3/7.arcgis.com` | `403` — CONNECT tunnel refused by egress policy |
| `hub.arcgis.com` | `403` — CONNECT tunnel refused by egress policy |
| `atlas.eia.gov` (EIA Energy Atlas) | Reachable (200). Pulled its DCAT-US 1.1 and DCAT-AP 2.0.1 catalogs: **89 datasets, zero substation entries**. Its `/search` route is a JavaScript shell that returns no server-side results. |
| `catalog.data.gov` CKAN API | Reachable but `{"message":"Not Found"}` — the CKAN `package_search` action no longer responds |
| `gis.ercot.com` | `403` — CONNECT tunnel refused by egress policy |
| `overpass-api.de` (OpenStreetMap fallback) | `403` — CONNECT tunnel refused by egress policy |

Proxy-side confirmation for the denials, from `$HTTPS_PROXY/__agentproxy/status`:

```
connect_rejected www.arcgis.com:443
connect_rejected services1.arcgis.com:443
connect_rejected services3.arcgis.com:443
connect_rejected services7.arcgis.com:443
connect_rejected hub.arcgis.com:443
connect_rejected gis.ercot.com:443
connect_rejected overpass-api.de:443
```

Per the proxy's own documentation these are organization policy denials and must
not be retried or routed around.

### Manual download routes for you

I have **not** verified these fetch a file, because the hosts are unreachable from
here. They are pointers, not confirmed URLs:

- **EIA Energy Atlas — Electric Substations**: <https://atlas.eia.gov/> → search
  "substations". EIA republishes the HIFLD substation layer; its hosted service
  sits on an `arcgis.com` host this container cannot reach but your machine can.
- **HIFLD Secure**: <https://gii.dhs.gov/hifld> — requires credentials you said you
  don't have.
- **ArcGIS Online item search**: <https://www.arcgis.com/home/search.html?q=electric%20substations>

Once you have it, drop the file in `data/raw/` and I will wire it in — the
downloader and the distance code are written to accept it.

---

## BLOCKED — dataset D: FCC broadband

| Host tried | Result |
|---|---|
| `broadbandmap.fcc.gov` | timeout, 0 bytes, both HTTP/2 and HTTP/1.1 |
| `www.fcc.gov` | `403` — egress policy denial |
| `api.fcc.gov` | `403` — egress policy denial |
| `us-fcc.app.box.com` (BDC bulk host) | `403` — egress policy denial |
| `opendata.fcc.gov` | reachable (200), not yet mined for a Form 477 fallback |

Manual route (unverified from here): <https://broadbandmap.fcc.gov/data-download>
— bulk BDC downloads require a free FCC account, which is likely why the
programmatic hosts are locked down.

---

## Impact on the Step 4 rubric

The rubric allocates **40 of 100 points** to substations:

- Substation proximity — 25 pts
- Substation voltage — 15 pts

Both are **uncomputable** without dataset A. Broadband is a further **10 pts**,
also uncomputable. So **50 of 100 points are unavailable**, and Population 2
(substations >= 138 kV not near a retired plant) **cannot be built at all** —
it is defined entirely by the missing layer.

Scoring as written would silently award 0 to every candidate on half the rubric.
That is not a degraded score, it is a misleading one: it would rank sites by
retired MW and transmission proximity while presenting itself as a 100-point
screen. I am not going to ship that under the original labels.

---

## What I have not done yet

Nothing from Steps 3–6. I stopped here as instructed, before building candidates
or scoring, so the substation gap can be closed first.
