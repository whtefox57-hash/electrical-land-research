"""Shared helpers for the Arizona powered-land screen.

Two rules encoded here:
  1. Every network fetch is logged to DATA_STATUS.md — success or failure, with
     the exact error text and a manual download URL. No silent failures.
  2. CRS is explicit everywhere. Distances in EPSG:26912 (NAD83 / UTM 12N,
     metres). Areas in EPSG:5070 (NAD83 / Conus Albers, equal-area).
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUTPUTS = os.path.join(ROOT, "outputs")
STATUS_LOG = os.path.join(DATA, "data_status_log.jsonl")

# Distances: NAD83 / UTM zone 12N, metres. Validated against the
# Phoenix->Tucson 170.4 km check (measured 170.45 km, 0.036% error).
CRS_DIST = "EPSG:26912"
# Areas: NAD83 / Conus Albers, equal-area. NEVER use UTM or Web Mercator
# for area — Web Mercator SHAPE_Area is inflated by ~1/cos^2(lat).
CRS_AREA = "EPSG:5070"
CRS_WGS84 = "EPSG:4326"

# Arizona bounding box (WGS84), generous margin.
AZ_BBOX = (-115.0, 31.2, -108.9, 37.1)

M2_PER_ACRE = 4046.8564224

os.makedirs(DATA, exist_ok=True)
os.makedirs(OUTPUTS, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_status(dataset: str, url: str, ok: bool, detail: str = "",
               manual_url: str = "", records: int | None = None) -> None:
    """Append one dataset attempt to the status log."""
    rec = {
        "timestamp": _now(),
        "dataset": dataset,
        "url": url,
        "status": "SUCCESS" if ok else "FAILED",
        "detail": str(detail)[:2000],
        "manual_download_url": manual_url or url,
        "records": records,
    }
    with open(STATUS_LOG, "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    flag = "OK  " if ok else "FAIL"
    print(f"  [{flag}] {dataset}"
          + (f" ({records} records)" if records is not None else "")
          + (f" -- {detail}" if detail and not ok else ""))


def get_json(url: str, params: dict | None = None, timeout: int = 120,
             retries: int = 3) -> dict:
    """GET returning parsed JSON. Raises on failure; caller logs."""
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001 - we surface the exact text
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"{type(last).__name__}: {last}")


def download(url: str, dest: str, timeout: int = 300, retries: int = 3) -> str:
    """Stream a file to disk. Raises on failure; caller logs."""
    last = None
    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                tmp = dest + ".part"
                with open(tmp, "wb") as fh:
                    for chunk in r.iter_content(1 << 20):
                        fh.write(chunk)
                os.replace(tmp, dest)
            return dest
        except Exception as exc:  # noqa: BLE001
            last = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"{type(last).__name__}: {last}")


def esri_query_all(layer_url: str, where: str = "1=1", out_fields: str = "*",
                   geometry: tuple | None = None, page: int = 1000,
                   out_sr: int = 4326, timeout: int = 180,
                   max_pages: int = 400) -> dict:
    """Page an ArcGIS REST FeatureServer/MapServer layer into one GeoJSON dict.

    ArcGIS caps returns at maxRecordCount (often 1000-2000). We page with
    resultOffset until exceededTransferLimit clears and no features return.
    """
    feats: list = []
    offset = 0
    pages = 0
    while pages < max_pages:
        params = {
            "where": where,
            "outFields": out_fields,
            "returnGeometry": "true",
            "outSR": out_sr,
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        if geometry:
            params.update({
                "geometry": ",".join(str(c) for c in geometry),
                "geometryType": "esriGeometryEnvelope",
                "inSR": 4326,
                "spatialRel": "esriSpatialRelIntersects",
            })
        js = get_json(layer_url.rstrip("/") + "/query", params=params,
                      timeout=timeout)
        if "error" in js:
            raise RuntimeError(f"ArcGIS error: {js['error']}")
        batch = js.get("features", []) or []
        feats.extend(batch)
        pages += 1
        if len(batch) < page:
            break
        offset += len(batch)
    return {"type": "FeatureCollection", "features": feats}


def null_sentinels(series, sentinels=(-999999, -999998, -99999, -9999, 0)):
    """Null ArcGIS/HIFLD missing-value sentinels.

    HIFLD voltage fields use -999999 for unknown. Zero is also not a real
    transmission voltage. Never let a sentinel become a number.
    """
    import pandas as pd
    s = pd.to_numeric(series, errors="coerce")
    return s.where(~s.isin(list(sentinels)))
