# Step 2 blocker report

**Date:** 2026-07-28
**Result: 0 of 6 datasets downloaded. 0 bytes written to `data/raw/`.**

Per the standing rule in the brief — never fabricate, estimate or synthesise —
nothing was invented to fill the gap. No stub files, no placeholder frames, no
"representative" coordinates. `data/raw/` contains only `MANIFEST.json`, which
is the record of the failures themselves.

## What failed and why

Every dataset failed for the **same single reason**: this session's egress proxy
refused the CONNECT for every government and GIS host. This is an organisation
network policy on the execution environment, not a problem with the endpoints,
the URLs, or the code.

| # | Dataset | Host | Result |
|---|---|---|---|
| A | Electric substations | `services2.arcgis.com` | CONNECT refused |
| B | Transmission lines | `services2.arcgis.com` | CONNECT refused |
| C | EIA-860 annual | `www.eia.gov` | CONNECT refused |
| C | EIA-860M monthly | `www.eia.gov` | CONNECT refused |
| D | FCC broadband | `broadbandmap.fcc.gov`, `opendata.fcc.gov` | CONNECT refused |
| E | TWDB water | `www.twdb.texas.gov` | CONNECT refused |

Exact error, identical across all attempts:

```
ProxyError: HTTPSConnectionPool(host='www.eia.gov', port=443):
Max retries exceeded — Caused by ProxyError(...)
```

The proxy's own diagnostic endpoint gives the underlying cause:

```
gateway answered 403 to CONNECT (policy denial or upstream failure)
```

## Hosts confirmed blocked

Probed directly, all refused:

```
services2.arcgis.com    services1.arcgis.com    www.arcgis.com
www.eia.gov             atlas.eia.gov           api.eia.gov
catalog.data.gov        www.data.gov            www2.census.gov
broadbandmap.fcc.gov    opendata.fcc.gov        www.twdb.texas.gov
```

Only `github.com`, `pypi.org` and related package registries are reachable.

## Fallbacks attempted

The brief's fallback chain was followed and exhausted:

1. Primary ArcGIS REST endpoint — blocked.
2. EIA Atlas (`atlas.eia.gov`) — blocked.
3. `data.gov` catalog — blocked.
4. Seven annual EIA-860 vintages (2024 back to 2018) — all blocked.
5. Fifteen monthly EIA-860M candidates — all blocked.
6. Two FCC endpoints, two TWDB endpoints — all blocked.

I also tried the separate `WebFetch` egress path, purely to **verify the
download URLs** rather than to retrieve data. It returned HTTP 403 from the same
policy. So I could not even confirm the manual URLs in `DATA_ACQUISITION.md` are
current — and that document flags them as unverified rather than implying
otherwise.

The proxy documentation is explicit that a 403 on CONNECT is an organisation
policy denial and must be reported rather than worked around, so no attempt was
made to route around it.

## What was NOT done, deliberately

- No coordinates were estimated for any Texas plant or substation.
- No retirement capacities were recalled from training data and written to disk.
- No sample, demo or "representative" dataset was substituted.
- The pipeline **refuses to run** without sources A, B and C, exits non-zero,
  and names what is missing. Verified:

```
$ python3 scripts/build_screen.py
REFUSING TO BUILD -- required sources are absent:
  * SOURCE A (substations) not present in data/raw/. ...
  * SOURCE B (transmission lines) not present in data/raw/. ...
  * SOURCE C (EIA generators) not present in data/raw/. ...
No outputs were written. Nothing was estimated or synthesised.
EXIT=2
```

## Two ways forward

1. **Fastest:** download the six datasets by hand and drop them in `data/raw/`.
   Follow `DATA_ACQUISITION.md`, then run the three commands. Nothing in the
   code needs to change.
2. **Cleanest:** re-run this agent in an environment whose network policy
   permits the hosts listed above. `acquire.py` will fetch everything itself,
   unmodified.
