# Texas powered-land GIS screen

A desktop screen that ranks Texas locations by how plausible it is that
large-scale electrical service already exists — or has a credible near-term path
— for data centre development.

The thesis: interconnection queues run 4–7 years, so a retired power plant with
live interconnection, or land beside a high-capacity substation, is worth far
more than raw acreage.

## Status: pipeline complete, data blocked

**Step 2 acquired nothing.** This session's network policy refused every
government and GIS host. No data was fabricated to compensate — see
[`BLOCKERS.md`](BLOCKERS.md) for the full failure record and
[`DATA_ACQUISITION.md`](DATA_ACQUISITION.md) for manual download instructions.

Everything else is built and tested. Drop the six source files into `data/raw/`
and the screen runs end to end.

## Run it

```bash
pip3 install -r requirements.txt

python3 scripts/acquire.py       # Step 2  -- downloads, or registers manual drops
python3 scripts/build_screen.py  # Steps 3-5 -- candidates, scores, outputs
python3 scripts/verify.py        # Step 6  -- adversarial checks + spot checks
```

Then open QGIS → Plugins → Python Console → run `scripts/load_in_qgis.py`.
That builds and saves `outputs/screen.qgz` on your machine.

## Outputs

| File | What it is |
|---|---|
| `outputs/tx_candidates.gpkg` | one layer per input dataset, plus a scored `candidates` layer |
| `outputs/top25_candidates.csv` | the top 25 with a `google_maps_url` per row and a blank `county_cad_note` for parcel IDs |
| `outputs/screen.qgz` | QGIS project — candidates graduated red-is-high, substations sized by kV, lines coloured by voltage class, OSM basemap |
| `outputs/METHOD.md` | sources, assumptions, derived-vs-read fields, limitations, and what would make this screen wrong |
| `outputs/COUNTY_SUMMARY.csv` | candidates by county — this drives which economic development offices you call first |

## Layout

```
scripts/config.py         <- TUNE THE RUBRIC HERE
scripts/acquire.py        Step 2, with fallbacks and a provenance manifest
scripts/loaders.py        defensive readers; raise rather than default
scripts/build_screen.py   Steps 3-5
scripts/verify.py         Step 6
scripts/load_in_qgis.py   PyQGIS project builder (run inside QGIS)
tests/test_smoke.py       58 code-path checks on SYNTHETIC fixtures
data/raw/                 source files, unchanged, + MANIFEST.json
outputs/                  generated
```

## Design rules this repo enforces in code

- **Nothing is written to `data/raw/` that did not arrive over the wire.** A
  failed source produces no file — not a stub, not an empty frame.
- **Required sources missing ⇒ the build refuses and exits non-zero**, naming
  what is absent. It never emits a partial candidate set that looks complete.
- **Unresolvable columns raise**, listing the columns actually seen. No silent
  defaulting when a field alias changes between vintages.
- **Sentinel values (`-999999`) become null**, never real voltages.
- **Every derived field is registered** and listed separately from source-read
  fields in `METHOD.md`.
- **Plants with no coordinates are dropped and counted**, never placed at a
  guessed position.

## About the smoke test

`tests/test_smoke.py` passes 58/58 — but read what that does and does not mean.
It runs **invented** fixtures through the real code to prove the branches work
and the invariants hold (no score above 100, staleness multiplier applies, the
2 km dedup fires, the GeoPackage reopens). It writes only to a temp directory
and asserts `data/raw/` and `outputs/` are untouched.

It says **nothing** about whether the screen is correct. That depends on real
source data this environment could not reach.

## The rubric is a first draft

The weights in `config.py` are a hypothesis, not a calibrated model. Nothing
here validates them against real substation headroom.

When your first Electrical Power Report comes back, compare what the power
engineer says about actual headroom against what the score predicted, and move
the weights toward whatever actually correlated. Three EPRs in, the rubric stops
being generic. That divergence is the moat — not the code.

## After it runs — the 20 minutes that matter

1. Open `screen.qgz`. Look at the map, not the spreadsheet.
2. Click every `google_maps_url` in `top25_candidates.csv`. In satellite view:
   is there a visible switchyard? Is it landlocked by residential? Is there
   rail? Has anyone touched it in ten years?
3. Kill anything that looks wrong. Trust your eyes over the score.
4. Open `COUNTY_SUMMARY.csv` and pick your top 3 counties. Those are your calls.
5. Read the "what would make this screen WRONG" section of `METHOD.md`.
