# Atlas desktop screening contract

Implementation: `lib/atlas-rules.mjs`. Rule version: `ATLAS_DESKTOP_2026-10-31_v1`.

The engine implements the October 30 Parcel Atlas assignment's desktop color semantics. It does not replace the existing 52-factor policy, 34-topic diligence, 16 paid-control proofs, founder decisions or capital caps. No score or map color is a construction, approval or sale probability. It never promotes paid-control status. A current `HOLD_NO_PAID_OPTION` value supplied in `paid_control_status` is retained.

## Public functions

- `profiles`: four versioned scenarios (`inference`, `hyperscale`, `urban-infill`, `industrial-reuse`). The default inference hypothesis is 20–30 facility MW. IT load and acreage requirements are not invented. Buyer-specific or parcel-specific requirements belong in a sourced layout brief.
- `rulesConfig`: machine-readable rule identities, fields, scope, evidence, thresholds, authority, freshness, reasons and next steps.
- `screenParcel(parcel, profileId = 'inference', nowISO)`: pure deterministic evaluation. Supply an explicit timestamp for reproducibility. Unknown profile IDs and invalid evaluation dates throw.
- `geometryMetrics(geometry)`: accepts a Polygon, MultiPolygon or Feature in WGS84 longitude/latitude. Returns preliminary spherical area, component areas, bounding box and geodesic bounding-box dimensions, with validity issues. Dimensions are not a fit test or buildable envelope. Invalid or unresolved geometry yields null area; the function never silently repairs source coordinates.
- `matchListing(parcel, listing)`: conservative identity reconciliation. It does not establish current availability or qualify a notification.

## Minimum parcel inputs

`id`, raw string `apn`, five-character string `county_fips`, `geometry`, attributable `source_url`, `source_date`, and `retrieved_at` establish a dated source polygon. A `geometry_version` and `snapshot_id` preserve input lineage. The string APN is never converted to a number. `identity_conflict: true` blocks a clean identity result. Geometry alone is not sufficient for green or amber.

Both plain records and GeoJSON Features are accepted. In a Feature, raw attributes belong in `properties` and legal geometry in `geometry`. The engine does not mutate input records.

## Shared evidence shape

Every mandatory assessment uses:

| Field | Meaning |
|---|---|
| `status` | `PASS`, `FAIL`, `CURABLE`, `UNKNOWN`, or justified `NOT_APPLICABLE` |
| `source_url` | Attributable HTTP(S), `library-file:` or registered `source:` reference |
| `reason` or `summary` | Specific assessment and scope explanation |
| `effective_date` | Evidence or source effective date, ISO date or timestamp |
| `retrieved_at` | Actual source retrieval timestamp |
| `reviewed_at` | Optional dated revalidation; does not renew physical/residential vintage |
| `scope_match` | Explicit `true` only after exact-parcel applicability review |
| `profile_ids` | Optional list limiting the assessment to specified profiles |
| `evidence_level` | Existing V0–V4 classification; engine does not automatically upgrade it |
| `expires_at` | Optional earlier deadline; expired evidence becomes unknown |
| `conflicting`, `truncated`, `error` | A conflict, partial response or service failure blocks a pass |

`NOT_APPLICABLE` additionally requires `not_applicable_reason`. The entire geometry, authority, physical, residential, layout or context category cannot be waived. A particular physical layer may be inapplicable only with its own sourced explanation.

## Mandatory assessments

`jurisdiction`: shared evidence plus `resolved: true` and a nonempty `authorities` array naming every controlling authority. A county name is not an authority determination.

`coverage.physical`: shared evidence, `complete: true`, and `layer_coverage` entries for `flood`, `wetlands`, `terrain`, `protected_land`, `roads` and `buildings`. Entries are `COMPLETE`, or `NOT_APPLICABLE` accompanied by the same key in `layer_explanations`. The importer must validate coverage, pagination, source counts and vintages before asserting complete. The certificate's effective date must reflect the earliest material unresolved source vintage; retaining individual layer versions is required upstream.

`coverage.residential`: shared evidence and `complete: true`. Separate `residential` attributes contain:

- `nearest_confirmed_m` and `nearest_possible_m`: measured values, or explicit null when no corresponding class was found within the documented surveyed extent. Missing is not zero.
- `counts`: keys `250`, `500`, `1000`, `1609.344`, each containing nonnegative integer `confirmed` and `possible` building counts. Counts must be monotonic. A known nonzero count requires a corresponding nearest distance.
- `measurement_reference: 'parcel_boundary'`, `count_unit: 'buildings'`, `sensitive_use_review_complete: true`.
- `dense_adjacency` or `mitigation_review_required`: true produces a curable condition. These flags require attributable review; distance alone never produces a legal rejection or basis-point penalty.

These four bands are research distances, not legal setbacks. Dwelling units are a separate statistic and must not be substituted for classified building counts. Equipment-to-receptor distances, on-site homes, homes on several sides and pending subdivisions remain separate evidence fields retained by the registry.

`layout`: shared evidence plus `version`, matching `profile_id` and `profile_version`, matching `facility_mw`, explicit `area_requirement_acres`, `threshold_authority`, boolean `fits`, and `systems_considered` containing `building`, `electrical`, `cooling`, `backup`, `stormwater`, `access`, `construction`. `requested_facility_mw` on the parcel must agree when supplied. The inference profile cannot silently accept a 1,000 MW request.

`envelope`: validated derived accounting with `validated: true`, `union_applied: true`, `geometry_version`, `profile_id`, `profile_version`, `method`, `source_url`, `computed_at`, nonempty `source_versions`, and `gross_acres`, `excluded_union_acres`, `usable_acres`, `largest_block_acres`, `components_acres`. The gross area, excluded union, usable sum and largest component must reconcile. The provisional reconciliation tolerance is max(0.01 acre, 1% of computed gross), not a survey accuracy guarantee. All areas remain null if the accounting or versions fail. A large fragmented total does not replace one sufficiently large contiguous component.

The engine does not perform a full GIS polygon union/difference. A spatial processor must produce the exact applicable exclusion union and components, preserve the source geometry, and justify `validated` and `union_applied`. Summed flood/wetland/easement areas are not a union. Do not set these certificates merely to obtain green. The UI must distinguish candidate envelope geometry from the legal parcel.

`restrictions`: shared evidence covering known use restrictions. A fatal `FAIL` must have `fatal: true`, `reopening_criteria`, and `authority_type` of `adopted_rule`, `documented_buyer_requirement` or `professional_assessment`. A conflict without established fatal scope remains curable. A stale or unattributed claim remains unknown.

`context`: shared evidence for the infrastructure or buyer basis. It does not establish available MW, connection rights or a sale commitment. Optional `conditions` is an array of additional scoped mandatory evidence; unresolved conditions prevent green.

## Color precedence and utility evidence

1. A supported fatal scenario failure produces RED even if other inputs remain unknown.
2. Any unknown, stale, conflicted or incomplete mandatory evidence produces GRAY.
3. Supported curable conditions with complete mandatory inputs produce AMBER.
4. Supported passes on all mandatory categories produce GREEN, labeled `Desktop candidate – capacity unconfirmed`.

`power` and `planning` use the shared evidence shape. A dark outline additionally requires current exact-load `power` in `UTILITY_PATH`, `FEASIBILITY`, `STUDY`, `CONTRACT` or `ENERGIZED` stage, a matching `load_facility_mw`, and current `planning` with `use_path_reviewed: true`. An application or nearby line is not a utility path. A dark outline is not reserved service or final approval.

`available_mw` is returned only for current scope-matched `STUDY`, `CONTRACT` or `ENERGIZED` evidence explicitly marked `capacity_confirmed: true`; retain the evidence stage so a study is not described as a contract. Other values remain null. Expired or mismatched utility evidence removes the dark outline and yields `STALE_OR_UNVERIFIED`, while independently current desktop evidence can remain green. The conservative green label is retained even with a stronger utility badge.

Provisional maximum review ages: identity/physical 365 days; authority/residential/layout/context 180 days; restrictions, extra conditions, utility and planning 90 days. Earlier explicit expiries control. These are configurable only through a new rule version and recorded reprocessing, not a claim that a regulation expires in 90 days.

## Listing identity

Use county plus raw `apn`/`apns`, or matching `provider` and `provider_parcel_id`. County disagreement or a raw-APN conflict is `CONFLICTING`. Leading zeros and internal punctuation are preserved; only outer whitespace is trimmed.

A verified whole-parcel link also needs both source references, `offered_scope: 'whole_parcel'`, `scope_verified: true`, and exact polygon corroboration or advertised/computed acreage within the explicitly provisional 2% tolerance. Ring orientation/order may differ; boundary coordinates are compared at 1e-7 degree precision. A materially different polygon remains conflicting, including when its bounding box or total area happens to match.

Assembly listings may supply `parcels: [{county_fips, apn, advertised_acres, geometry, ...}]` to corroborate each constituent. The assembly's total area cannot validate one constituent. Proposed portions stay `PROBABLE` pending a scoped subparcel geometry review. A marketing pin or address alone is `UNRESOLVED`. These matching states are identity decisions, not source popularity, seller willingness or current availability.

## Geometry limits and validation

The preliminary metric implementation checks ring closure, finite WGS84 coordinates, duplicate consecutive vertices, self crossings, outside/touching holes, overlapping holes and overlapping/touching MultiPolygon components. It handles small antimeridian-crossing parcels and computes sphere-based area and lengths rather than using square degrees. Legitimate touching component cases are conservatively sent to review. Full ellipsoidal survey calculation, repair, overlay operations, width-of-buildable-envelope and rights-of-way analysis remain GIS tasks.

More than 20,000 vertices or 2,000,000 topology comparisons returns a named offline-validation issue and null metrics, protecting bounded request processing. Larger real polygons remain preserved upstream rather than silently simplified for analysis. Display simplification must not be fed into legal-area analysis without a recorded geometry version.

## Verification

Run `node --test tests/atlas-rules.test.mjs`. Synthetic fixtures exist only in that test file. Tests cover all color outcomes, evidence attribution/expiry, missing and stale layers, source failures, residential semantics, fragmented and unreconciled envelope areas, profile changes, exact utility load scope, polygon/hole/multipart/antimeridian metrics, invalid geometry, APN leading zeros, assemblies, portions and misplaced pin leads. End-to-end persistence, outbox delivery, source pagination and worker recovery require the separate registry/integration tests.
