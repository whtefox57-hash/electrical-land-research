# Standalone Vercel port

This branch starts from the exact Sites v30 tree (265adb393737db2ae421d578fcfe5bd42365fd77).
The existing Sites publication and its production data are unchanged.

## Deployment

- Framework: Next.js 16.2.6, Node.js 24, `npm ci`, `npm run build:vercel`.
- Vercel project: `syncranicity-deal-desk`, White Fox team.
- Vercel Authentication must protect **all** deployment URLs, including production and custom domains. This is the authentication authority, as Sites dispatch was for the original. The current team has one confirmed member, the owner. Adding team members would expand access and requires a separate access review.
- `DEPLOYMENT_AUTH_BOUNDARY=vercel-sso` asserts that platform configuration. It is not an authentication secret. Do not set it on an unprotected deployment.
- Caller-supplied `oai-authenticated-user-email` headers grant no access.
- `BLOB_STORE_ID` plus Vercel OIDC, or `BLOB_READ_WRITE_TOKEN`, must connect a **private** store.
- `ATLAS_SETTINGS_OWNER_EMAIL` and a 32-byte base64 `ATLAS_CREDENTIAL_ENCRYPTION_KEY` enable the credential vault. Existing saved CARTO credentials are not in Git and have not been transferred.

## Data migration is pending

The connector returned HTTP 403 when creating the private Blob store. No retry was made through another route.
The Sites database viewer rejected the main workspace row as too large. It cannot provide a complete database export through that interface. These are blockers, not successful migration steps.

The destination deliberately shows setup instructions until a verified current database exists. It never initializes from old checked-in research.
Transfer a complete live SQLite backup, including all 13 original tables. Retain the old database and compare per-table counts, versions and canonical row hashes before switching work. A workspace JSON export is incomplete. Existing active leases and schedules must not be redirected automatically; independently running copies can diverge.

`POST /api/migration` supports a first import of a complete SQLite database up to 4 MB, subject to platform body limits. It checks SQLite integrity and required tables, rejects an existing destination, creates with no-overwrite, and verifies readback. Larger production backups require a server-side transfer; that path is not yet implemented or verified. Do not represent the import endpoint as handling an arbitrarily large production database.

## Persistence model and limits

Each request reads an uncached private SQLite image into an isolated temporary directory. Existing SQL, JSON queries, atomic batches, snapshot rows, versions and idempotency receipts are retained. A write publishes the full image with the original ETag as an atomic precondition and verifies the returned ETag and bytes before returning success. A stale competing request returns conflict. Temporary files are cleaned up and are never durable authority.

This is a low-concurrency portability adapter, with a 96 MB image ceiling. It reads and writes a whole database image for each mutation and is unsuitable for high-rate national ingestion. Benchmark real database size/latency and storage costs before enabling unattended intake. Database writes against real Vercel Blob remain unverified until storage is provisioned. The transport follows the official Blob SDK API v13 contract without adding dependencies.

The app is online-first. The service worker caches only a generic offline response and local icons, never research, API responses, exports, keys or authenticated navigation pages. GitHub and Install app controls are available in the app bar. Browser installation still requires the owner's browser action and authentication.

## Checks

`npm run test:vercel` exercises rollback, stale versions, two competing snapshot writers, failed readback, private ETag transport, authentication boundaries and PWA cache limits. The expanded port, existing atlas-basemap, credential-vault and atlas-rules suites pass 45 checks. Production build/type checks are separate. Platform deployment protection must also be verified on the deployed URL.

Original Cloudflare/Vinext scripts are retained as source reference. Use the `:vercel` scripts for this branch. Existing automations and MCP registrations remain attached to the original Sites origin.
