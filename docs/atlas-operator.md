# National Parcel Suitability Atlas — operator guide

This page extends the existing private Syncranicity Deal Desk. It does not replace its listing register, source research, buyer profiles, data-center histories, founder locks or capital decisions.

## Public-data release and scope

The map displays actual official parcel polygons within declared source partitions. National county boundaries are coverage context, not analyzed suitable land. All 50 states and D.C. belong in the coverage ledger; a county with a loaded partition is not a completed county. The universe of all U.S. parcels remains unknown until a licensed or sufficiently reconciled national source is available.

Map colors use versioned executable desktop rules, documented in `atlas-rules.md`. Ordinary parcels with only identity and geometry remain gray. Green requires supported mandatory desktop passes. No map color authorizes an option purchase. Hinds stays HOLD_NO_PAID_OPTION under its existing founder rules. The 52-factor model, 34-topic diligence and 16 paid-control proofs remain separate from this early desktop screen.

## Storage and ownership

- `atlas_parcels`: source parcel snapshots, full-resolution WGS84 geometry, raw APN strings, county FIPS, bounded spatial indexes and optimistic versions.
- `atlas_results`: reproducible results by parcel and versioned screening profile, input hash and evaluation date.
- `atlas_entities`: typed source access/layers, national county ledger metadata, coverage partitions, parcel identity links, candidate/site-parcel/envelope records, evidence, jurisdiction decisions, listing links and schedule receipts.
- `atlas_events`: prior snapshots, changes and concurrency guard records. Applied migrations are immutable.
- `atlas_runs`: idempotency keys and durable write receipts.
- `atlas_jobs`: processing states, leases and resumable checkpoints.
- `atlas_outbox`: qualifying events and separately recorded notification attempts and externally reported receipts.

These are separate from `origination_records`, `origination_events`, `origination_runs`, and the founder's workspace. Browser storage is not authoritative. Full national overlays require a dedicated spatial batch runner or partitioned geospatial processing service; Worker requests are bounded ingestion and query operations.

## Routes

Open `/?view=parcel-atlas`. Read `/api/atlas?view=workflow` and `/api/atlas?view=summary` first.

GET views: `summary`, `parcels` (viewport `bbox`), `parcel&id=...`, `entity&kind=...&id=...`, `run&id=...`, `backup&after=...`, `export&format=csv|geojson`, and `guide`. Profile IDs are `inference`, `hyperscale`, `urban-infill`, and `industrial-reuse`.

POST `/api/atlas` uses JSON and a supported action. This existing owner-private Site relies on Sites' authenticated visitor/service boundary and enforces same-origin writes. Do not make it public without a new authorization review.

### Import a verified batch

Send `action: import`, a unique stable `run_id`, up to 25 `parcels` and up to 100 `entities`. Read current versions before updating. Each record requires `expected_version`; use 0 for a new record. An unchanged retry of the same run returns the original receipt; a changed payload requires a new run ID. Do not overwrite unrelated fields or infer a missing layer as clean.

The parcel record includes `id`, `county_fips`, `apn`, `state`, `county`, `source_id`, `source_url`, `source_date`, `retrieved_at`, `geometry`, and lineage. Keep recorded, advertised and computed acreage separately. Source APNs must be strings. Preserve source object IDs and duplicate/overlapping interests for review. Stable identity is not proof that a listing offers the whole parcel.

Entity records are `{kind,id,expected_version,data}`. Sources must disclose access status, official documentation, rights, vintage, actual update frequency, tested fields, quota/cost exposure and remaining gaps. Source credentials never belong in these records.

Verify `readback_verified`, then GET the run receipt and representative parcel IDs from a fresh request. Advance collection or analyst-review cursors only after their own durable writes. An ingestion receipt is not individual analyst review.

### Refresh and match

`action: refresh` with `partition_id` retrieves one bounded batch from that partition's configured official public source. It must preserve the source denominator, unique identities, incomplete pages and source errors. Refresh failures create a failed job rather than reporting zero constraints or erasing stored parcels. Repeated invocations resume the checkpoint. One completed source partition does not establish complete county or national coverage.

`action: reconcile` consumes a bounded changed-listing batch from the existing register. Raw county/APN identity plus independently corroborated offered scope is required for VERIFIED. Marketing pins and address-only matches remain a review queue. Preserve many-to-many links, assemblies, portions and relists.

A qualifying notification requires a relevant availability/material-change event, a verified offered-land match, a current green profile and deduplication. Gray/amber leads go to review. Available MW stays null without current scope-matched utility evidence. An outbox card is not proof of delivery.

### Notification receipts

`delivery_attempt` claims an attempt only after rechecking current listing, matching and screening evidence. `delivery_confirm` records an external channel, timestamp and receipt as DELIVERY_REPORTED. Provider verification is not integrated, so delivery_confirmed stays false. Do not mark messages delivered based on a saved task or an in-app card. A control test must be labeled a test and must never enter the real candidate inventory or opportunities count.

## Scheduled continuation

An unattended task must retrieve the exact Site using Sites `get_site`, verify owner-only access, and obtain supported fresh service access. Use `OAI-Sites-Authorization: Bearer TOKEN` only to this Site. Never persist a token in source, prompt, query parameter, logs, user files or browser code.

The requested daily health/progress report is 8:15 AM America/Phoenix. A separate condition watch may check qualifying outbox events at most hourly. Create them only after writers/readback are verified. Record actual task IDs, enabled state, next run and results; a null next run is unverified. Existing listing intake and land-history tasks retain their responsibilities and schedules. A saved schedule is not a successful run, and task-cap failures remain visible dependencies.

Every run reports new/changed parcels, source records versus distinct identities, valid geometries, profiles processed, color counts, matched/unmatched listings, attempted/confirmed alerts, source failures, denominators and next cursors. Report even with zero qualifying opportunities.

## Back up and restore

Page through `view=backup` until `next_cursor` is null. Save every page plus source manifests, rules version, processing checkpoints and receipts. Raw licensed exports require source permission. The canonical repository preserves executable code and migration history; runtime data remains in the Site database.

Restore requires validating provenance and comparing current versions, then using new version-checked import batches. Never replace the founder workspace or drop tables to restore the atlas. Recompute screening from retained inputs and explicit evaluation time. Verify representative geometry, identities, listing links and counts after restoration. A restricted data retention window overrides raw archival convenience.

## Outstanding external dependencies

Public parcel services do not provide universal national entitlement, comprehensive residential occupancy, utility capacity, title clearance or buyer commitment. Regrid bulk licensing differs from REST/MCP access; confirm current scope, retention and included quota before use. Existing RealEstateAPI validation does not establish a free national listing feed or approved metered consumption. LandSearch's inbound feed is not an outbound listing API. No data purchase, subscription, seller contact or external commitment is authorized by this implementation.

Source outages, missing residential/elevation/planning layers, incomplete spatial envelopes, unavailable notification receipts and national inventory gaps must remain explicit. Do not lower acceptance criteria to call the national objective complete.

## CARTO key settings

The Parcel Atlas Settings tab accepts a write-only CARTO API key. The owner may save, replace or remove it through the same-origin /api/atlas/carto-key endpoint. Sites authenticates the request and the route additionally checks the configured owner email. Service callers cannot manage this credential.

The key is encrypted with AES-256-GCM and a fresh nonce, stored separately from atlas records in a private R2 object. ATLAS_CREDENTIAL_ENCRYPTION_KEY and ATLAS_SETTINGS_OWNER_EMAIL are production hosting secrets; never copy them into source, atlas entities, browser storage or backups. Preserve the encryption secret across deployments. Metadata responses contain only configured status and update time. There is no key-reveal endpoint. Removing a key deletes the active encrypted object. Saving a key does not call CARTO, verify an entitlement, ingest a dataset or authorize metered usage.
