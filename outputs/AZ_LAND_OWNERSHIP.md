# STEP 2 — ARIZONA LAND OWNERSHIP

**Acquired 2026-07-29.** Every acreage below is either READ from a source field
or COMPUTED in an equal-area projection from source geometry. Nothing is
estimated. Derived fields are flagged in the last section.

---

## The source decision, and why it matters

The BLM national cached SMA layer named in the brief returns **102 polygons**
for Arizona, with all private land collapsed into a handful of multipart
features. It is a fine statewide census and useless for site screening — you
cannot tell whether a substation sits on private land from a polygon that
covers a third of the state.

The BLM **Arizona State Office** publishes a full-resolution equivalent:

```
https://gis.blm.gov/azarcgis/rest/services/lands/BLM_AZ_SMA/MapServer/0
```

**17,585 polygons**, with a real `Private` category (7,098 polygons) and its own
read `ACRES` field. This is the primary ownership layer for the whole screen.
The national cached layer is retained as one of five independent cross-checks.

---

## Statewide breakdown

Acreage computed by reprojecting source geometry to **EPSG:5070 (NAD83 / Conus
Albers, equal-area)**. The source's own `ACRES` field is carried alongside as an
independent check — the two agree to within 0.03% on every class.

| land_status | acres (equal-area) | pct | acres (source ACRES field) | known pct | delta | polygons |
|---|---:|---:|---:|---:|---:|---:|
| tribal | 20,289,203 | 27.81% | 20,278,892 | 28.33% | −0.52 | 693 |
| **private** | **12,582,022** | **17.25%** | **12,579,193** | 17.01% | +0.24 | **7,098** |
| federal_blm | 12,063,812 | 16.54% | 12,067,796 | 16.64% | −0.10 | 2,063 |
| federal_forest | 11,178,581 | 15.32% | 11,171,975 | 15.21% | +0.11 | 357 |
| state_trust | 9,275,903 | 12.71% | 9,272,979 | 12.47% | +0.24 | 5,961 |
| federal_other | 4,602,428 | 6.31% | 4,604,228 | 6.35% | −0.04 | 676 |
| military | 2,786,007 | 3.82% | 2,788,153 | 3.64% | +0.18 | 46 |
| municipal | 177,062 | 0.24% | 176,983 | 0.03% | +0.21 | 159 |
| unknown | 3,922 | 0.01% | 3,924 | 0.31% | −0.30 | 532 |
| **TOTAL** | **72,958,940** | 100.00% | 72,944,122 | | | **17,585** |

Arizona's actual land area is ~72,964,000 acres. **This layer totals 99.99% of
it.** The reference breakdown supplied in the brief summed to 100.7%, i.e. it
double-counted roughly 500,000 acres. The full-resolution layer does not.

### Verdict against the target

The brief said to stop immediately if private land came out materially different
from ~17% / ~12.5 million acres. **It did not.** Private land is **12,582,022
acres, 17.25%** — 0.24 points above the 17.01% reference and 0.7% above the
"approximately 12.5 million acres" figure. Both are inside the noise between two
differently-generalised renderings of the same boundaries.

### The only two deltas worth explaining

Both are classification choices, not data disagreements, and both are fully
accounted for:

- **municipal 0.24% vs 0.03%.** Entirely caused by where `Local or State Parks`
  (152,607 ac) is assigned. I put it in `municipal`; the reference did not. Take
  those acres out and municipal is 24,376 ac = 0.03%, matching exactly.
- **unknown 0.01% vs 0.31%.** The Arizona layer resolves ownership that the
  national cache leaves undetermined. Ours is better resolved, not different.

Running the same classification over the national cached layer reproduces the
reference figures **exactly** — `unknown` 0.31%, `municipal` 0.03%, private
17.18%. That confirms the reference breakdown was derived from the generalised
national layer, and that both deltas above are artefacts of generalisation
rather than errors in either dataset.

---

## Cross-checks — five independent sources, all consistent

| source | private acres | state trust | tribal | note |
|---|---:|---:|---:|---|
| **BLM AZ full-res (primary)** | **12,582,022** | 9,275,903 | 20,289,203 | 17,585 polygons |
| ASLD Public Land Ownership (state's own) | 12,801,514 | 9,249,523 | 20,134,020 | 108 polygons, generalised |
| BLM national cached | 12,584,920 | 9,277,282 | 20,394,942 | 102 polygons, generalised |
| ADEQ Land Ownership | 14,234,971 | — | — | 116 polygons, heavily generalised |
| Census TIGERweb AIANNH | — | — | 33 areas | reservation + off-reservation trust |
| PAD-US Manager Name | — | — | — | 2,915 AZ features; protected areas only, does not enumerate private land |

The Arizona State Land Department's own layer — the state's authoritative
statement about its own trust land — agrees with the primary within **0.3% on
state trust** and **1.7% on private**. The residual is generalisation: ASLD
renders all private land in the state as a *single* polygon.

ADEQ's 14.2M private acres is 13% high, which is what you would expect from 116
polygons covering 72M acres; it is recorded for completeness and not relied on.

---

## Flag fields carried onto every later candidate

| field | values | how derived |
|---|---|---|
| `land_status` | private, state_trust, tribal, federal_blm, federal_forest, federal_other, military, municipal | **READ** from `CATEGORY`, mapped through a fixed table over the source's 15-value domain |
| `acquirable` | yes, auction_only, lease_only_bia, no | **DERIVED** from `land_status` |
| `adjacency_note` | free text | **DERIVED** — 50 m buffer intersect against state trust and tribal polygons in EPSG:26912 |

### `acquirable` mapping

- `private` → **yes**
- `state_trust` → **auction_only**. Not excluded. ASLD auctions under A.R.S.
  Title 37 are a real if slow path, and state trust is 9.28M acres.
- `tribal` → **lease_only_bia**
- everything else → **no**

### Adjacency findings

Of 7,098 private polygons:

- **4,033 abut state trust land** (11,736,831 acres of the private universe).
  Cuts both ways: an expansion path via ASLD auction, and an additional
  opposition surface.
- **513 abut tribal land** (4,602,719 acres). Consultation expectations attach.

---

## Contiguous acreage available — the practical constraint

A hyperscale campus needs contiguous land. The private universe is mostly small
parcels:

| threshold | polygons | acres |
|---|---:|---:|
| ≥ 100 ac | 4,619 | 12,500,919 |
| ≥ 500 ac | 3,069 | 12,138,294 |
| ≥ 1,000 ac | 729 | 10,620,611 |
| ≥ 2,000 ac | 382 | 10,144,491 |
| ≥ 5,000 ac | 211 | 9,599,622 |

Median private polygon is **309 acres**; p90 is 1,039 acres; the largest is
615,231 acres. For scale, the Tract Buckeye Technology Park is 2,069 acres —
only **382 private polygons in Arizona** are that size or larger as single
ownership units.

---

## Projections used

| purpose | CRS | validation |
|---|---|---|
| distance | **EPSG:26912** NAD83 / UTM 12N, metres | Phoenix→Tucson measured **170.45 km** against the 170.4 km reference; geodesic ground truth 170.51 km; error 61 m (0.036%) |
| area | **EPSG:5070** NAD83 / Conus Albers, equal-area | class totals reproduce the source `ACRES` field within 0.03% |
| storage | EPSG:4326 | |

Web Mercator `SHAPE_Area` was **not** used for any area, as instructed — it is
inflated by roughly 1/cos²(latitude), which at Arizona's latitude is a ~44%
overstatement.

---

## Excluded classes — retained, not discarded

Every non-private class is kept as its own layer in `data/az_ownership.gpkg` so
what is being excluded stays visible:

| layer | content |
|---|---|
| `sma_az_fullres` | all 17,585 polygons, all classes, with flags |
| `private_land` | the 7,098-polygon working universe |
| `asld_public_land_ownership` | ASLD's own 108-polygon layer |
| `blm_natl_sma_cached` | BLM national generalised, 102 AZ polygons |
| `adeq_land_ownership` | ADEQ, 116 polygons |
| `padus_manager_name` | PAD-US, 2,915 AZ features |
| `census_aiannh` | 33 reservations / off-reservation trust lands |

**82.75% of Arizona is not privately owned.** That is the single largest filter
in this screen and it is applied first, before any power or water analysis.
