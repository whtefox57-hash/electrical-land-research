# Manual data acquisition

## Why you are reading this

The session that built this repository had **no outbound network access to any
government or GIS host**. Every download in Step 2 failed. Rather than
improvise data, the pipeline was built to run against files you place by hand.

> ### Honesty flag on the URLs below
>
> **I could not open a single one of these pages in this session**, so I could
> not confirm they are current. The link-checking path (WebFetch) was blocked by
> the same policy as the downloads. The landing-page URLs come from your brief;
> the deep-link filename patterns come from my training data and **are the part
> most likely to be stale**, because EIA changes filenames every vintage.
>
> Treat every URL here as a **starting point to navigate from**, not a verified
> address. Always start at the landing page and click through to the current
> file. If a deep link 404s, that is expected — use the landing page.

## Where files go

Drop everything into `data/raw/`. Filenames do not need to match exactly — the
loaders match on patterns (`*Generator*.xlsx`, `*ubstation*.geojson`, …) and
will tell you the exact columns they saw if a match fails.

Then:

```bash
python3 scripts/acquire.py      # re-scans data/raw/, records manual files in the manifest
python3 scripts/build_screen.py # Steps 3-5
python3 scripts/verify.py       # Step 6
```

`acquire.py` records human-placed files with `"provenance": "manual"` in
`data/raw/MANIFEST.json`, so `METHOD.md` can always distinguish what an agent
downloaded from what you supplied.

---

## A. Electric substations  (REQUIRED)

**Landing page:** <https://atlas.eia.gov/> — search "Electric Substations".

Also try the ArcGIS REST endpoint the pipeline targets directly:

```
https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services
```

Open that in a browser with `?f=html` to list the hosted services and find the
substations layer. Then export GeoJSON, or use the layer's `/query` endpoint
with a Texas envelope.

- The old `hifld-geoplatform.opendata.arcgis.com` portal is **sunset** — do not
  use it. HIFLD Secure requires credentials.
- **Save as:** `data/raw/substations_tx.geojson` (or any `*ubstation*` file)
- **Fields needed:** `NAME`, `MAX_VOLT`, `MIN_VOLT`, `LINES`, `STATUS`
- **Watch for:** voltage fields use `-999999` for unknown. The loader converts
  these to null and they score 0 — they are never treated as real voltages.

## B. Electric power transmission lines  (REQUIRED)

Same source and same portal as A. Layer name is
`US_Electric_Power_Transmission_Lines`.

- **Save as:** `data/raw/transmission_tx.geojson`
- **Fields needed:** `VOLTAGE`, `VOLT_CLASS`, `OWNER`, `STATUS`

## C. EIA-860 and 860M generators  (REQUIRED — the most important dataset)

**Landing pages:**
- Annual: <https://www.eia.gov/electricity/data/eia860/>
- Monthly: <https://www.eia.gov/electricity/data/eia860m/>

Download the annual ZIP and extract **two** workbooks:

| File | Looks like | Why you need it |
|---|---|---|
| Generator file | `3_1_Generator_Y<year>.xlsx` | retirement dates + capacity |
| Plant file | `2___Plant_Y<year>.xlsx` | **latitude / longitude / county** |

> **This trips people up:** the Generator file has no coordinates. Without the
> Plant file, every Population 1 site is dropped for missing geometry — the
> pipeline will not invent a position. Get both.

Then grab the most recent 860M monthly workbook (`<month>_generator<year>.xlsx`).
860M is more current on *planned* retirements and does carry lat/lon in recent
vintages.

- **Save all of them into** `data/raw/`
- **Sheets used:** anything named Operable / Operating / Retired / Planned /
  Proposed / Canceled
- The loader auto-detects the header row (EIA puts 1–3 note rows above it) and
  prefers 860M over 860 when the same unit appears in both.

## D. Broadband — PROXY ONLY  (optional)

**Landing page:** <https://broadbandmap.fcc.gov/data-download>

Get fixed-broadband availability for Texas, then **also** get census block
groups so the counts can be joined spatially:

**TIGER block groups:** <https://www2.census.gov/geo/tiger/> → `TIGER<year>/BG/`
→ `tl_<year>_48_bg.zip` (48 = Texas)

- **Save as:** `data/raw/*broadband*.csv` and `data/raw/tl_*_48_bg.zip`
- Without **both**, broadband scores 0 for every candidate.
- **This is a proxy for fibre and nothing more.** Provider counts say nothing
  about long-haul routes, which are proprietary. A site can show four providers
  and have no carrier-grade route within twenty miles.

## E. Water  (optional — least critical, skip if it fights you)

**Landing page:** <https://www.twdb.texas.gov/mapping/gisdata.asp>

Major reservoirs and/or groundwater conservation districts.

- **Save as:** `data/raw/*eservoir*.zip` or `data/raw/*GCD*.zip`
- If absent, the water component scores 0 for every candidate and the practical
  maximum score becomes **95**. Scores are **not** rescaled to hide this, and
  `METHOD.md` says so explicitly.

## Counties  (strongly recommended)

**TIGER counties:** <https://www2.census.gov/geo/tiger/> → `TIGER<year>/COUNTY/`
→ `tl_<year>_us_county.zip`

- **Save as:** `data/raw/tl_<year>_us_county.zip`
- Without it, county names fall back to the source attribute rather than a real
  spatial join, and `county_method` in the output records that downgrade.
  `verify.py` cross-checks the two against each other when both exist.

---

## If you would rather not do this by hand

The blocker is this session's network policy, not the code. If you re-run the
agent in an environment whose egress policy allows these hosts, `acquire.py`
will fetch everything itself with no changes. The hosts that need allowing:

```
services2.arcgis.com     www.eia.gov            atlas.eia.gov
broadbandmap.fcc.gov     www2.census.gov        www.twdb.texas.gov
```
