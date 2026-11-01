# Atlas integration QA — 2026-10-03

Existing Site: appgprj_6a9c555e97f48191a1d45c2cb55d4779. No replacement Site created.

## Diagnosis before changes
- Uploaded map JSON parsed (50 state outlines, 1,382 observations, 1,048 projects, 21 signals). Script syntax check passed; referenced element IDs all existed.
- Original attachment served unchanged through a temporary dev diagnostic route rendered successfully in Chrome: all geometry, clusters, filters and research panel visible. No application startup error observed.
- The uploaded SVG contained empty state/marker groups until JavaScript executed. Script-suppressed file viewers therefore render a blank map. User's iOS viewer was not directly observed, so this is the likely attachment cause, not a proven device-specific exception.
- Existing deployed Deal Desk parcel map reproduced “Interactive map unavailable on this device.” This confirms WebGL initialization failure in the test browser. The original dependency path included MapLibre plus external OSM raster tiles.

## Preservation
- Existing Site identity, audience, D1/R2 bindings, schema, migrations, APIs, models, source-update rules, research records, reports, documents and decision history retained.
- Only presentation files and a separate imported atlas data snapshot changed.
- Baseline live UI: 247 records, 2 Priority, 238 Watch, 7 Rejected.
- Local preview uses separately seeded local D1, never production migration replay.

## Implementation
- Native React SVG U.S. atlas; no external tiles, WebGL, network map libraries or API keys.
- Embedded reference geometry, observation clustering, search, state and category filters, opportunity/demand/regulatory modes, pan, wheel/pinch/button/keyboard zoom, clickable map and result details.
- 1,048 projects without coordinates remain searchable and explicitly unmapped.
- Live Deal Desk records projected from saved coordinates or boundary vertices; no invented centroids for unlocated records. Continental reference projection calibration maximum error vs supplied coordinates <0.42 SVG units. Exact geometry remains in existing parcel-detail view.
- Dossier “Show on map,” mobile Map navigation, same-record map/dossier links. Existing parcel map includes 8-second loading fallback.
- Supplied policy research kept distinct from verified/current data; snapshot and scope warnings displayed with sources.

## Preview checks
- TypeScript passes.
- Desktop: 50 state paths, 153 initial clusters, 30 saved-record locators; no horizontal overflow.
- Zoom changes 1.0x to 1.6x; CoreSite DC1 search yields one observation and clickable details.
- Arizona filter: 60 observations, 2 saved records. Benson links to existing dossier and back to focused map.
- 390px phone iframe: content width equals scroll width (373px excluding scrollbar), 50 state paths present, mobile Map navigation visible.

## First deployed check
- Same Site deployment succeeded, version 12. Browser loaded the new atlas with all 50 state paths; desktop pan/zoom and Arizona record filter passed.
- Live record count remains 247 (unchanged from baseline).
- Cross-origin mobile iframe from local preview correctly hit the sign-in wall. Replaced that QA approach with a same-origin, read-only responsive preview at /qa-mobile; this retains normal Site sharing and existing API identity checks.
- This is browser viewport testing, not physical-device Safari testing.
