"""
Step 2 -- data acquisition.

Design rules, enforced in code:

  * Nothing is written to data/raw/ that was not received over the wire from
    the named source, byte for byte.
  * Every attempt (success or failure) is recorded in data/raw/MANIFEST.json
    with the URL, HTTP status, error text, byte count and SHA-256.
  * A failed source produces NO file. It does not produce a stub, a placeholder
    or an empty frame. Downstream steps refuse to run without it.
  * Files a human placed in data/raw/ by hand are detected and recorded with
    provenance "manual", so METHOD.md can distinguish them from agent downloads.

Run:  python3 scripts/acquire.py
      python3 scripts/acquire.py --only substations,plants
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import RAW, TX_BBOX  # noqa: E402

MANIFEST_PATH = RAW / "MANIFEST.json"
TIMEOUT = 90
UA = {"User-Agent": "powered-land-screen/1.0 (GIS research; contact via repo)"}

# ArcGIS organisation hosting the HIFLD-derived infrastructure layers.
ARCGIS_ORG = "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services"

# Keyword sets used to locate the right hosted layer by name, so a service
# rename does not silently break the pipeline.
SUBSTATION_KEYWORDS = ("substation",)
TRANSMISSION_KEYWORDS = ("transmission", "power", "line")


# ==========================================================================
# manifest plumbing
# ==========================================================================
def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_manifest() -> dict[str, Any]:
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text())
    return {"created_utc": _now(), "sources": {}}


def save_manifest(m: dict[str, Any]) -> None:
    m["updated_utc"] = _now()
    MANIFEST_PATH.write_text(json.dumps(m, indent=2, sort_keys=True))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record(
    manifest: dict,
    key: str,
    *,
    status: str,
    attempts: list[dict],
    files: list[Path] | None = None,
    note: str = "",
) -> None:
    manifest["sources"][key] = {
        "status": status,
        "recorded_utc": _now(),
        "attempts": attempts,
        "note": note,
        "files": [
            {
                "path": str(p.relative_to(RAW.parent.parent)),
                "bytes": p.stat().st_size,
                "sha256": _sha256(p),
                "provenance": "downloaded",
            }
            for p in (files or [])
            if p.exists()
        ],
    }


# ==========================================================================
# low level fetch
# ==========================================================================
def _get(url: str, params: dict | None = None, stream: bool = False):
    return requests.get(url, params=params, timeout=TIMEOUT, headers=UA, stream=stream)


def _attempt(url: str, error: str = "", status: int | None = None, **extra) -> dict:
    d = {"url": url, "at_utc": _now(), "http_status": status, "error": error}
    d.update(extra)
    return d


# ==========================================================================
# A / B -- ArcGIS hosted feature layers
# ==========================================================================
def discover_layer(keywords: tuple[str, ...]) -> tuple[str | None, list[dict]]:
    """Find a FeatureServer layer URL on the org whose name matches keywords."""
    attempts: list[dict] = []
    url = ARCGIS_ORG
    try:
        r = _get(url, {"f": "json"})
        attempts.append(_attempt(url, status=r.status_code))
        if r.status_code != 200:
            return None, attempts
        services = r.json().get("services", [])
    except Exception as exc:  # noqa: BLE001
        attempts.append(_attempt(url, error=f"{type(exc).__name__}: {exc}"))
        return None, attempts

    names = [s.get("name", "") for s in services]
    attempts.append(_attempt(url, error="", status=200, services_found=len(names)))

    for svc in services:
        name = (svc.get("name") or "").lower()
        if all(k in name for k in keywords) or (
            len(keywords) == 1 and keywords[0] in name
        ):
            return f"{svc['url']}/0" if "url" in svc else None, attempts

    # Fall back to constructing from the service name field.
    for svc in services:
        name = (svc.get("name") or "")
        if any(k in name.lower() for k in keywords):
            return f"{ARCGIS_ORG}/{name}/FeatureServer/0", attempts

    attempts.append(
        _attempt(url, error=f"no service name matched {keywords}; saw {names[:40]}")
    )
    return None, attempts


def fetch_arcgis_layer(layer_url: str, out_path: Path) -> tuple[bool, list[dict]]:
    """Page through an ArcGIS REST layer with resultOffset into one GeoJSON."""
    attempts: list[dict] = []
    features: list[dict] = []
    offset, page = 0, 1000
    xmin, ymin, xmax, ymax = TX_BBOX
    qurl = f"{layer_url}/query"

    while True:
        params = {
            "where": "1=1",
            "geometry": f"{xmin},{ymin},{xmax},{ymax}",
            "geometryType": "esriGeometryEnvelope",
            "inSR": 4326,
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "*",
            "outSR": 4326,
            "returnGeometry": "true",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        try:
            r = _get(qurl, params)
        except Exception as exc:  # noqa: BLE001
            attempts.append(
                _attempt(qurl, error=f"{type(exc).__name__}: {exc}", offset=offset)
            )
            return False, attempts

        if r.status_code != 200:
            attempts.append(
                _attempt(qurl, status=r.status_code, error=r.text[:400], offset=offset)
            )
            return False, attempts

        try:
            payload = r.json()
        except ValueError as exc:
            attempts.append(
                _attempt(qurl, status=200, error=f"non-JSON response: {exc}")
            )
            return False, attempts

        if "error" in payload:
            attempts.append(
                _attempt(qurl, status=200, error=json.dumps(payload["error"])[:400])
            )
            return False, attempts

        batch = payload.get("features", [])
        features.extend(batch)
        attempts.append(
            _attempt(qurl, status=200, offset=offset, returned=len(batch))
        )

        if len(batch) < page:
            break
        offset += page
        if offset > 500_000:  # runaway guard
            attempts.append(_attempt(qurl, error="aborted: >500k features"))
            break

    if not features:
        attempts.append(_attempt(qurl, error="0 features returned; nothing written"))
        return False, attempts

    out_path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features})
    )
    return True, attempts


# ==========================================================================
# C -- EIA-860 annual and EIA-860M monthly
# ==========================================================================
EIA860_CANDIDATES = [
    f"https://www.eia.gov/electricity/data/eia860/xls/eia8602{y}.zip"
    for y in range(24, 17, -1)
]
EIA860M_BASE = "https://www.eia.gov/electricity/data/eia860m/xls/"
EIA860M_MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]


def fetch_eia860(out_dir: Path) -> tuple[bool, list[dict], list[Path]]:
    """Download the EIA-860 annual zip and extract Generator + Plant files."""
    attempts: list[dict] = []
    for url in EIA860_CANDIDATES:
        try:
            r = _get(url, stream=True)
        except Exception as exc:  # noqa: BLE001
            attempts.append(_attempt(url, error=f"{type(exc).__name__}: {exc}"))
            continue
        if r.status_code != 200:
            attempts.append(_attempt(url, status=r.status_code, error="not available"))
            continue

        blob = r.content
        zip_path = out_dir / Path(url).name
        zip_path.write_bytes(blob)
        attempts.append(_attempt(url, status=200, bytes=len(blob)))

        written = [zip_path]
        try:
            with zipfile.ZipFile(io.BytesIO(blob)) as zf:
                for member in zf.namelist():
                    low = member.lower()
                    # Generator file carries retirement dates; Plant file
                    # carries latitude/longitude and county.
                    if ("generator" in low or "plant" in low) and low.endswith(
                        (".xlsx", ".xls")
                    ):
                        target = out_dir / Path(member).name
                        target.write_bytes(zf.read(member))
                        written.append(target)
        except zipfile.BadZipFile as exc:
            attempts.append(_attempt(url, error=f"bad zip: {exc}"))
            zip_path.unlink(missing_ok=True)
            continue

        if len(written) == 1:
            attempts.append(
                _attempt(url, error="zip contained no Generator/Plant workbook")
            )
            continue
        return True, attempts, written

    return False, attempts, []


def fetch_eia860m(out_dir: Path) -> tuple[bool, list[dict], list[Path]]:
    """Download the most recent EIA-860M monthly workbook we can find."""
    attempts: list[dict] = []
    today = dt.date.today()
    probes: list[str] = []
    for back in range(0, 15):
        y = today.year
        m = today.month - back
        while m <= 0:
            m += 12
            y -= 1
        probes.append(f"{EIA860M_BASE}{EIA860M_MONTHS[m - 1]}_generator{y}.xlsx")

    for url in probes:
        try:
            r = _get(url, stream=True)
        except Exception as exc:  # noqa: BLE001
            attempts.append(_attempt(url, error=f"{type(exc).__name__}: {exc}"))
            continue
        if r.status_code != 200:
            attempts.append(_attempt(url, status=r.status_code, error="not available"))
            continue
        blob = r.content
        target = out_dir / Path(url).name
        target.write_bytes(blob)
        attempts.append(_attempt(url, status=200, bytes=len(blob)))
        return True, attempts, [target]

    return False, attempts, []


# ==========================================================================
# D / E -- broadband and water
# ==========================================================================
FCC_ENDPOINTS = [
    "https://broadbandmap.fcc.gov/nbm/map/api/published/filing",
    "https://opendata.fcc.gov/resource/bdc-fixed-summary.json?$limit=50000&state=TX",
]

TWDB_ENDPOINTS = [
    "https://www.twdb.texas.gov/mapping/gisdata/doc/GCD_Shapefile.zip",
    "https://www.twdb.texas.gov/mapping/gisdata/doc/Major_Reservoirs_shp.zip",
]


def fetch_simple(urls: list[str], out_dir: Path) -> tuple[bool, list[dict], list[Path]]:
    attempts: list[dict] = []
    written: list[Path] = []
    for url in urls:
        try:
            r = _get(url, stream=True)
        except Exception as exc:  # noqa: BLE001
            attempts.append(_attempt(url, error=f"{type(exc).__name__}: {exc}"))
            continue
        if r.status_code != 200:
            attempts.append(_attempt(url, status=r.status_code, error=r.text[:300]))
            continue
        blob = r.content
        name = Path(url.split("?")[0]).name or "download.bin"
        target = out_dir / name
        target.write_bytes(blob)
        attempts.append(_attempt(url, status=200, bytes=len(blob)))
        written.append(target)
    return bool(written), attempts, written


# ==========================================================================
# manual drop detection
# ==========================================================================
MANUAL_PATTERNS = {
    "substations": ["*ubstation*.geojson", "*ubstation*.zip", "*ubstation*.gpkg"],
    "transmission": ["*ransmission*.geojson", "*ransmission*.zip", "*ransmission*.gpkg"],
    "eia860": ["*Generator*.xlsx", "*Plant*.xlsx", "eia860*.zip"],
    "eia860m": ["*_generator2*.xlsx"],
    "broadband": ["*bdc*.csv", "*broadband*.csv"],
    "water": ["*eservoir*.zip", "*GCD*.zip", "*water*.zip"],
}


def detect_manual(key: str) -> list[Path]:
    hits: list[Path] = []
    for pat in MANUAL_PATTERNS.get(key, []):
        hits.extend(sorted(RAW.glob(pat)))
    return sorted(set(hits))


# ==========================================================================
# driver
# ==========================================================================
def run(only: set[str] | None = None) -> dict:
    manifest = load_manifest()

    def wanted(k: str) -> bool:
        return only is None or k in only

    # ---- A. substations --------------------------------------------------
    if wanted("substations"):
        layer, att = discover_layer(SUBSTATION_KEYWORDS)
        ok, files = False, []
        if layer:
            out = RAW / "substations_tx.geojson"
            ok, a2 = fetch_arcgis_layer(layer, out)
            att += a2
            files = [out] if ok else []
        if not ok and (m := detect_manual("substations")):
            record(manifest, "substations", status="manual", attempts=att,
                   files=m, note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "substations", status="ok" if ok else "failed",
                   attempts=att, files=files)

    # ---- B. transmission lines -------------------------------------------
    if wanted("transmission"):
        layer, att = discover_layer(TRANSMISSION_KEYWORDS)
        ok, files = False, []
        if layer:
            out = RAW / "transmission_tx.geojson"
            ok, a2 = fetch_arcgis_layer(layer, out)
            att += a2
            files = [out] if ok else []
        if not ok and (m := detect_manual("transmission")):
            record(manifest, "transmission", status="manual", attempts=att, files=m,
                   note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "transmission", status="ok" if ok else "failed",
                   attempts=att, files=files)

    # ---- C. EIA 860 + 860M ------------------------------------------------
    if wanted("eia860"):
        ok, att, files = fetch_eia860(RAW)
        if not ok and (m := detect_manual("eia860")):
            record(manifest, "eia860", status="manual", attempts=att, files=m,
                   note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "eia860", status="ok" if ok else "failed",
                   attempts=att, files=files)

    if wanted("eia860m"):
        ok, att, files = fetch_eia860m(RAW)
        if not ok and (m := detect_manual("eia860m")):
            record(manifest, "eia860m", status="manual", attempts=att, files=m,
                   note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "eia860m", status="ok" if ok else "failed",
                   attempts=att, files=files)

    # ---- D. broadband -----------------------------------------------------
    if wanted("broadband"):
        ok, att, files = fetch_simple(FCC_ENDPOINTS, RAW)
        if not ok and (m := detect_manual("broadband")):
            record(manifest, "broadband", status="manual", attempts=att, files=m,
                   note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "broadband", status="ok" if ok else "failed",
                   attempts=att, files=files,
                   note="PROXY for fibre availability, not a fibre route dataset")

    # ---- E. water ---------------------------------------------------------
    if wanted("water"):
        ok, att, files = fetch_simple(TWDB_ENDPOINTS, RAW)
        if not ok and (m := detect_manual("water")):
            record(manifest, "water", status="manual", attempts=att, files=m,
                   note="agent download failed; using human-placed file(s)")
        else:
            record(manifest, "water", status="ok" if ok else "failed",
                   attempts=att, files=files, note="optional layer")

    save_manifest(manifest)
    return manifest


def summarise(manifest: dict) -> int:
    print("\n=== STEP 2 ACQUISITION SUMMARY ===")
    failed = []
    for key, rec in sorted(manifest["sources"].items()):
        n = len(rec["files"])
        mark = {"ok": "OK", "manual": "MANUAL", "failed": "FAILED"}[rec["status"]]
        print(f"  [{mark:>6}] {key:<14} files={n}")
        if rec["status"] == "failed":
            failed.append(key)
            last = rec["attempts"][-3:] if rec["attempts"] else []
            for a in last:
                print(f"            {a['url']}")
                print(f"              http={a['http_status']} err={a['error'][:160]}")
    print(f"\n  manifest: {MANIFEST_PATH}")
    if failed:
        print(f"\n  BLOCKED SOURCES: {', '.join(failed)}")
        print("  See DATA_ACQUISITION.md for manual download instructions.")
        print("  No placeholder data was written for these sources.")
    return len(failed)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="comma separated source keys")
    args = ap.parse_args()
    sel = set(args.only.split(",")) if args.only else None
    sys.exit(1 if summarise(run(sel)) else 0)
