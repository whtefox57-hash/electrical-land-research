# AZ METHOD

Generated 2026-07-29. Everything this screen rests on, what was derived versus read, and an explicit list of what would make it wrong.

## Projections

| purpose | CRS | validation |
|---|---|---|
| distance | **EPSG:26912** NAD83 / UTM 12N, metres | Phoenix→Tucson measured **170.45 km** against the 170.4 km reference; geodesic ground truth 170.51 km; error 61 m (0.036%) |
| area | **EPSG:5070** NAD83 / Conus Albers, equal-area | class totals reproduce the source `ACRES` field within 0.03% |
| storage | EPSG:4326 | |

Web Mercator `SHAPE_Area` was never used for area. At Arizona's latitude it overstates by roughly 1/cos²(lat) ≈ 44%. No distance was computed in degrees.

## Sources

23 datasets retrieved, 2 failed. Full log with timestamps in `DATA_STATUS.md`.

| dataset | records | retrieved (UTC) | endpoint |
|---|---:|---|---|
| ADEQ_Land_Ownership (cross-check) | 116 | 2026-07-29T13:15:56Z | `https://services.arcgis.com/SzoH1oFM2apCSkx3/arcgis/rest/services/Land_Ownership/FeatureServer/0` |
| ADWR Well Registry 2024 | 240104 | 2026-07-29T13:52:11Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/Well_Registry_2024/FeatureServer/0` |
| ADWR aaws_determinations | 5596 | 2026-07-29T13:45:49Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/AAWS_Issued_Determination_2024/FeatureServer/0` |
| ADWR ama_ina | 11 | 2026-07-29T13:45:17Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/AMA_INA_2024/FeatureServer/0` |
| ADWR city_boundaries | 91 | 2026-07-29T13:45:55Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/City_Boundaries_2024/FeatureServer/0` |
| ADWR counties | 15 | 2026-07-29T13:45:52Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/County_2024/FeatureServer/3` |
| ADWR cws_service_area | 750 | 2026-07-29T13:45:34Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/CWS_2024/FeatureServer/0` |
| ADWR groundwater_basin | 52 | 2026-07-29T13:45:23Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/Groundwater_Basin_2024/FeatureServer/0` |
| ADWR groundwater_subbasin | 85 | 2026-07-29T13:45:31Z | `https://services.arcgis.com/C34zQ7veRS0V1t04/arcgis/rest/services/Groundwater_Subbasin/FeatureServer/0` |
| ASLD_Public_Land_Ownership (azgeo.az.gov) [retry unpaged] | 108 | 2026-07-29T13:19:04Z | `https://azgeo.az.gov/arcgis/rest/services/asld/ASLD_AdminBoundaries/MapServer/14` |
| BLM_AZ_SMA_fullres (PRIMARY ownership) | 17585 | 2026-07-29T13:14:25Z | `https://gis.blm.gov/azarcgis/rest/services/lands/BLM_AZ_SMA/MapServer/0` |
| BLM_Natl_SMA_cached (cross-check, GENERALISED) [objectId batching] | 102 | 2026-07-29T13:20:26Z | `https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1` |
| Census_TIGERweb_AIANNH L2 (Federal American Indian Reservations) | 24 | 2026-07-29T13:18:57Z | `https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/AIANNHA/MapServer/2` |
| Census_TIGERweb_AIANNH L3 (Off-Reservation Trust Lands) | 9 | 2026-07-29T13:18:58Z | `https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/AIANNHA/MapServer/3` |
| EIA-860 annual 2024 |  | 2026-07-29T13:38:18Z | `https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip` |
| FCC Broadband Data Collection Dec-2024, AZ block groups (PROXY for fiber, not routes) | 4773 | 2026-07-29T13:54:40Z | `https://services8.arcgis.com/peDZJliSvYims39Q/arcgis/rest/services/FCC_Broadband_Data_Collection_December_2024_View/FeatureServer/3` |
| HIFLD_Electric_Power_Transmission_Lines (AZ bbox) | 1335 | 2026-07-29T13:37:23Z | `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0` |
| HIFLD_Electric_Retail_Service_Territories (AZ bbox) | 59 | 2026-07-29T13:37:53Z | `https://services3.arcgis.com/OYP7N6mAJJCyH6hd/arcgis/rest/services/Electric_Retail_Service_Territories_HIFLD/FeatureServer/0` |
| HIFLD_Electric_Retail_Service_Territories (cross-check copy) | 59 | 2026-07-29T13:38:02Z | `https://services6.arcgis.com/BAJNi3EgCdtQ1BCG/arcgis/rest/services/Electric_Retail_Service_Territories/FeatureServer/0` |
| HIFLD_Electric_Substations (AZ) [third-party republication of HIFLD schema; hifld-geoplatform opendata is SUNSET] | 901 | 2026-07-29T14:02:19Z | `https://services6.arcgis.com/OO2s4OoyCZkYJ6oE/arcgis/rest/services/Substations/FeatureServer/0` |
| PADUS_Manager_Name (cross-check) | 2915 | 2026-07-29T13:16:31Z | `https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Manager_Name_PADUS/FeatureServer/0` |
| USGS NHD Arizona perennial flowlines (FCode 46006) | 18992 | 2026-07-29T13:49:28Z | `https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/NHD_H_Arizona_State_GDB/FeatureServer/11` |
| USGS NHD Arizona waterbodies | 10489 | 2026-07-29T13:49:56Z | `https://services3.arcgis.com/0OPQIK59PJJqLK0A/arcgis/rest/services/NHD_H_Arizona_State_GDB/FeatureServer/16` |

## Datasets that FAILED — and what was NOT substituted

### EIA-860M monthly
- endpoint: `https://www.eia.gov/electricity/data/eia860m/xls/may_generator2026.xlsx`
- time: 2026-07-29T13:40:35Z
- error: `ALL candidate months failed. may_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; april_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; march_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error pa`
- manual download: https://www.eia.gov/electricity/data/eia860m/

### EIA-860M parse
- endpoint: `/home/user/electrical-land-research/data/may_generator2026.xlsx`
- time: 2026-07-29T13:39:50Z
- error: `Excel file format cannot be determined, you must specify an engine manually.`
- manual download: /home/user/electrical-land-research/data/may_generator2026.xlsx

**EIA-860M was not silently replaced with the annual file.** The annual EIA-860 2024 release is used for retirements and is labelled as such. The consequence is concrete: any retirement announced after the 2024 annual release is **not** in this screen. Re-run once `/cneaf/electricity/` is back up.

## Derived vs read fields

| field | provenance |
|---|---|
| `land_status` | **READ** — `CATEGORY` from the BLM Arizona full-res SMA layer, mapped through a fixed table over its 15-value domain |
| `acquirable` | **DERIVED** from land_status |
| `adjacency_note` | **DERIVED** — 1-mile buffer intersect against state trust and tribal polygons |
| `parcel_acres` | **COMPUTED** in EPSG:5070 equal-area |
| `max_volt_kv / min_volt_kv` | **READ** from HIFLD, with -999999 sentinels nulled. HIFLD's own `MAX_INFER`/`MIN_INFER` flags are carried through as `INFERRED` in `max_volt_provenance` |
| `lines_count` | **READ** from HIFLD `LINES`, sentinels nulled |
| `retired_mw_on_site` | **READ** — sum of EIA-860 2024 `Nameplate Capacity (MW)` over qualifying units |
| `est_capacity_mw` | **READ** for Pop 1 (EIA nameplate). **NULL** for Pop 2 — see the capacity section below |
| `size_class / triggers` | **DERIVED** from est_capacity_mw against the buckets in AZ_SIZE_THRESHOLDS.md |
| `serving_utility` | **READ** from HIFLD territories, but the *choice* among overlapping polygons is **DERIVED** — see the ambiguity note |
| `utility_type` | **READ** from HIFLD `TYPE` where populated; **INFERRED** from the utility name where HIFLD says 'NOT AVAILABLE'. Which one applies is recorded per row in `utility_type_basis` |
| `in_ama / groundwater_basin` | **READ** — point-in-polygon against ADWR layers |
| `municipal_water_available` | **DERIVED** — point inside an ADWR community water system service area |
| `nearest_surface_water_km` | **COMPUTED** against **perennial-only** NHD flowlines (FCode 46006) |
| `water_risk_score` | **DERIVED** from the brief's rubric |
| `political_risk_score` | **READ** priors from AZ_POLITICAL_NOTES.md where the jurisdiction was researched; **INFERRED** defaults otherwise, recorded in `political_prior_basis` |
| `prior_industrial_use` | **DERIVED** — 5/5 for retired plant sites; ≤3/5 for substations, scored on electrical infrastructure density within 5 km |
| `dist_to_residential_km` | **DERIVED** — distance to nearest census block group at ≥200 persons/km² |
| `broadband_providers_PROXY` | **READ** from FCC BDC Dec-2024, but a **PROXY** — see below |

## Capacity — the biggest single gap

`est_capacity_mw` is populated for **7 of 255** candidates.

The HIFLD substation schema carries **no capacity field at all**: its columns
are NAME, TYPE, STATUS, LINES, MAX_VOLT, MIN_VOLT and administrative metadata.
There is no MVA rating and no MW rating. Servable load depends on transformer
bank size, conductor rating and the utility's own planning limits, none of
which appear in any dataset acquired here.

Deriving MW from kV would have been fabrication, so **248 candidates carry a
null capacity and `size_class = NOT_DETERMINED`**, with `capacity_basis`
explaining why on every row. The brief's instruction — record MVA and do not
silently convert — could not even be exercised, because no MVA is published.

That gap is resolved by one phone call per site to the serving utility's system
planning group, not by any public dataset I could find.

## The broadband field is a proxy, not fiber

`broadband_providers_PROXY` counts fixed broadband providers reporting
availability in the containing census block group (FCC BDC, December 2024). It
is **not** a fiber route map and says nothing about carrier-class fiber
reaching a parcel or the cost to extend it. It carries 4.55 of 100 points,
deliberately the smallest weight. 84 candidates fall outside any block group
with data and score `UNSCORED` on this component; those rows carry
`score_max_available = 95.45` and `score_rescaled_to_100`.

## Assumptions

1. A point falling inside an ownership polygon inherits that polygon's status.
   Candidates are **points** (plant sites, substation sites), not parcels. A
   substation on a private inholding surrounded by BLM land reads as private
   here, and for acquisition purposes the relevant parcel may be neither.
2. Retired generator interconnection capacity is a meaningful proxy for future
   load-serving capability. It is an upper bound at best — a retired generator
   interconnection is not a commitment to serve load, and the two are
   physically different (export vs import).
3. Ten years is the flag threshold for interconnection rights lapsing. That is
   the brief's number, applied as given, not a legal determination.
4. Block-group population density ≥200/km² approximates "residential". It is a
   density proxy, not a land use survey.
5. Absence of a found moratorium equals absence of a moratorium. **This one is
   load-bearing and probably wrong — see below.**

## What would make this screen WRONG

These are ordered by how much damage each would do.

1. **The political scores on the top 25 are inferred, not researched.** All 25
   top candidates sit in jurisdictions that AZ_POLITICAL_NOTES.md did not
   cover, so each receives the default 8/8 moratorium and 5/5 no-ordinance
   score purely because nothing was found. A jurisdiction nobody has studied
   scores identically to one verified permissive. If Mohave, Yuma, Navajo,
   Apache or Greenlee county has quietly adopted a data center ordinance, the
   affected candidates are overscored by up to 13 of 22.7 political points and
   the ranking reorders substantially. **This is the single most likely way
   the screen is wrong.**
2. **Capacity is unknown for 248 of 255 candidates.** The ranking is driven by
   proximity and voltage, which are availability signals, not capacity
   signals. A 500 kV substation with no spare transformer capacity outranks a
   230 kV one with plenty. Nothing in the data distinguishes them.
3. **Utility assignment is ambiguous for 181 of 255 candidates.** HIFLD retail
   territories overlap heavily in Arizona. Where a small irrigation-district
   polygon beat a large IOU polygon on specificity, the named utility may be
   wrong even though the *list* of overlapping candidates is right.
4. **The substation layer is a third-party republication.** hifld-geoplatform
   opendata is sunset; the layer used carries the HIFLD schema and 77,946
   national records but is not a federal endpoint. Currency is unverified.
   185 of 901 Arizona substations have no usable voltage, and 168 have a
   voltage HIFLD itself flags as inferred.
5. **Water scores reward the absence of regulation.** 20/20 means "outside any
   AMA", which is a regulatory freedom, not physical water availability.
   20 of the top 25 score 20 on that basis. A site
   with no AWS obligation and no water is scored better than one inside the
   Phoenix AMA with a designated provider.
6. **Points are not parcels.** No parcel geometry, ownership name, or
   assessor record was acquired. `county_assessor_note` is deliberately blank
   for you to fill. Nothing here establishes that the land at a given point is
   for sale, or who owns it.
7. **EIA-860M is missing**, so retirements announced since the 2024 annual
   release are absent. A newly announced 500 MW retirement would likely enter
   the top 5 and is simply not here.
8. **Ephemeral-stream reality.** Surface water uses perennial NHD only. If you
   reintroduce intermittent or ephemeral flowlines, every
   `nearest_surface_water_km` collapses toward zero and becomes meaningless.
9. **The CDC tax exemption is closed** to new applicants 1 Jul 2026 – 30 Jun
   2029. No score here assumes it. If a buyer already holds certification, the
   economics differ materially from what this screen implies.
