"""
Paginated ArcGIS REST FeatureServer downloader.

Downloads a layer as GeoJSON, clipped to a bounding box, paging with
resultOffset because hosted services cap records per request
(maxRecordCount, typically 1000-2000).

Writes the raw concatenated FeatureCollection to disk unchanged apart from
the page stitching. No field is altered, dropped or derived here.
"""
import json
import sys
import time
import urllib.parse

import requests

# Texas bounding box in WGS84 (EPSG:4326), generous margin.
# xmin, ymin, xmax, ymax
TX_BBOX = (-107.0, 25.5, -93.3, 36.8)

session = requests.Session()
session.headers.update({"User-Agent": "powered-land-screen/1.0 (research)"})


def service_info(base_url):
    r = session.get(base_url, params={"f": "json"}, timeout=120)
    r.raise_for_status()
    return r.json()


def layer_count(layer_url, where="1=1", geometry=None):
    params = {"where": where, "returnCountOnly": "true", "f": "json"}
    if geometry:
        params.update(_geom_params(geometry))
    r = session.get(layer_url + "/query", params=params, timeout=180)
    r.raise_for_status()
    return r.json().get("count")


def _geom_params(bbox):
    return {
        "geometry": ",".join(str(v) for v in bbox),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
    }


def download_layer(layer_url, out_path, bbox=TX_BBOX, where="1=1",
                   page_size=None, out_sr=4326):
    """Page through a layer and write one GeoJSON FeatureCollection."""
    info = session.get(layer_url, params={"f": "json"}, timeout=120).json()
    name = info.get("name")
    max_rec = info.get("maxRecordCount", 1000)
    page = page_size or min(max_rec, 1000)
    total = layer_count(layer_url, where=where, geometry=bbox)
    print(f"  layer '{name}'  maxRecordCount={max_rec}  matching features={total}")

    features = []
    offset = 0
    while True:
        params = {
            "where": where,
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": str(out_sr),
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page,
        }
        params.update(_geom_params(bbox))
        for attempt in range(5):
            try:
                r = session.get(layer_url + "/query", params=params, timeout=300)
                r.raise_for_status()
                js = r.json()
                break
            except Exception as e:  # noqa: BLE001
                if attempt == 4:
                    raise
                wait = 2 ** (attempt + 1)
                print(f"    retry {attempt+1} after {wait}s ({e})")
                time.sleep(wait)
        if "error" in js:
            raise RuntimeError(f"service error: {js['error']}")
        batch = js.get("features", [])
        features.extend(batch)
        print(f"    offset={offset:>7}  got={len(batch):>5}  total={len(features):>7}")
        exceeded = js.get("properties", {}).get("exceededTransferLimit") or js.get(
            "exceededTransferLimit"
        )
        if not batch or (len(batch) < page and not exceeded):
            break
        offset += len(batch)
        if total and len(features) >= total:
            break

    fc = {"type": "FeatureCollection", "features": features}
    with open(out_path, "w") as fh:
        json.dump(fc, fh)
    print(f"  wrote {out_path}  features={len(features)}  expected={total}")
    if total is not None and len(features) != total:
        print(f"  WARNING: count mismatch (got {len(features)}, service said {total})")
    return len(features), total


if __name__ == "__main__":
    layer_url, out_path = sys.argv[1], sys.argv[2]
    where = sys.argv[3] if len(sys.argv) > 3 else "1=1"
    download_layer(layer_url, out_path, where=where)
