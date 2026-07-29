# DATA_STATUS — every dataset attempted
Regenerated 2026-07-29 13:41:12 UTC from `data/data_status_log.jsonl` (20 attempt records, 14 distinct datasets).
**12 succeeded · 2 failed (final state).**
A dataset listed as SUCCESS here was read from the network in this run. Nothing in this project is estimated, synthesised or substituted: where a source failed, the dependent field is left empty and the failure is recorded below.

---

## FAILED — unresolved

### EIA-860M monthly
- **Attempted:** `https://www.eia.gov/electricity/data/eia860m/xls/may_generator2026.xlsx`
- **Timestamp:** 2026-07-29T13:40:35Z
- **Error:** `ALL candidate months failed. may_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; april_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; march_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; february_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; january_generator2026.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; december_generator2025.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El; november_generator2025.xlsx: not an xlsx — got b'<!do' (0 bytes of HTML error page). First bytes: '<!doctype html>\r\n<html>\r\n<head>\r\n\t<title>El`
- **Manual download:** https://www.eia.gov/electricity/data/eia860m/

### EIA-860M parse
- **Attempted:** `/home/user/electrical-land-research/data/may_generator2026.xlsx`
- **Timestamp:** 2026-07-29T13:39:50Z
- **Error:** `Excel file format cannot be determined, you must specify an engine manually.`
- **Manual download:** /home/user/electrical-land-research/data/may_generator2026.xlsx

---

## SUCCEEDED

| dataset | records | timestamp (UTC) | endpoint |
|---|---:|---|---|
| ADEQ_Land_Ownership (cross-check) | 116 | 2026-07-29T13:15:56Z | `https://services.arcgis.com/SzoH1oFM2apCSkx3/arcgis/rest/services/Land_Ownership/FeatureServer/0` |
| ASLD_Public_Land_Ownership (azgeo.az.gov) [retry unpaged] | 108 | 2026-07-29T13:19:04Z | `https://azgeo.az.gov/arcgis/rest/services/asld/ASLD_AdminBoundaries/MapServer/14` |
| BLM_AZ_SMA_fullres (PRIMARY ownership) | 17585 | 2026-07-29T13:14:25Z | `https://gis.blm.gov/azarcgis/rest/services/lands/BLM_AZ_SMA/MapServer/0` |
| BLM_Natl_SMA_cached (cross-check, GENERALISED) [objectId batching] | 102 | 2026-07-29T13:20:26Z | `https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1` |
| Census_TIGERweb_AIANNH L2 (Federal American Indian Reservations) | 24 | 2026-07-29T13:18:57Z | `https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/AIANNHA/MapServer/2` |
| Census_TIGERweb_AIANNH L3 (Off-Reservation Trust Lands) | 9 | 2026-07-29T13:18:58Z | `https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/AIANNHA/MapServer/3` |
| EIA-860 annual 2024 |  | 2026-07-29T13:38:18Z | `https://www.eia.gov/electricity/data/eia860/xls/eia8602024.zip` |
| HIFLD_Electric_Power_Transmission_Lines (AZ bbox) | 1335 | 2026-07-29T13:37:23Z | `https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0` |
| HIFLD_Electric_Retail_Service_Territories (AZ bbox) | 59 | 2026-07-29T13:37:53Z | `https://services3.arcgis.com/OYP7N6mAJJCyH6hd/arcgis/rest/services/Electric_Retail_Service_Territories_HIFLD/FeatureServer/0` |
| HIFLD_Electric_Retail_Service_Territories (cross-check copy) | 59 | 2026-07-29T13:38:02Z | `https://services6.arcgis.com/BAJNi3EgCdtQ1BCG/arcgis/rest/services/Electric_Retail_Service_Territories/FeatureServer/0` |
| HIFLD_Electric_Substations (AZ) [third-party republication of HIFLD schema; hifld-geoplatform opendata is SUNSET] | 901 | 2026-07-29T13:37:18Z | `https://services6.arcgis.com/OO2s4OoyCZkYJ6oE/arcgis/rest/services/Substations/FeatureServer/0` |
| PADUS_Manager_Name (cross-check) | 2915 | 2026-07-29T13:16:31Z | `https://services.arcgis.com/v01gqwM5QqNysAAi/arcgis/rest/services/Manager_Name_PADUS/FeatureServer/0` |

---

## Failures later resolved by retry

Recorded so the diagnosis is not lost. Each of these failed first, was diagnosed, and then succeeded on a corrected request.

- **BLM_Natl_SMA_cached (cross-check, GENERALISED)** — 2026-07-29T13:15:22Z
  - error: `HTTPError: 500 Server Error: Internal Server Error for url: https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1/query?where=ADMIN_ST%3D%27AZ%27&outFields=OBJECTID%2CADMIN_ST%2CADMIN_UNIT_NAME%2CADMIN_UNIT_TYPE%2CADMIN_DEPT_CODE%2CADMIN_AGENCY_CODE&returnGeometry=true&outSR=4326&f=geojson&resultOffset=0&resultRecordCount=2000`

- **Census_TIGERweb_AIANNH (tribal cross-check)** — 2026-07-29T13:16:32Z
  - error: `ArcGIS error: {'code': 400, 'message': 'Failed to execute query.', 'details': []}`

- **ASLD_Land_Jurisdiction (azgeo.az.gov)** — 2026-07-29T13:16:33Z
  - error: `ArcGIS error: {'code': 400, 'message': 'Pagination is not supported.', 'details': []}`

- **BLM_Natl_SMA_cached (cross-check) [retry page=50]** — 2026-07-29T13:18:53Z
  - error: `HTTPError: 500 Server Error: Internal Server Error for url: https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer/1/query?where=ADMIN_ST%3D%27AZ%27&outFields=OBJECTID%2CADMIN_ST%2CADMIN_UNIT_NAME%2CADMIN_UNIT_TYPE%2CADMIN_DEPT_CODE%2CADMIN_AGENCY_CODE&returnGeometry=true&outSR=4326&f=geojson&resultOffset=50&resultRecordCount=50`
