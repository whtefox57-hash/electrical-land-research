"""
Builds outputs/screen.qgz on YOUR machine, from YOUR QGIS install.

WHY THIS AND NOT A PRE-BUILT .qgz
---------------------------------
A .qgz is a zipped QGIS project XML whose schema is tied to the QGIS version
that wrote it. This repository was built in an environment with no QGIS, so any
.qgz written here would have been hand-forged XML that had never been opened by
QGIS once. That is exactly the kind of artefact that looks fine until it fails
in front of you. The brief allows a PyQGIS script instead; this is it.

HOW TO RUN
----------
1. Open QGIS.
2. Plugins -> Python Console  (Ctrl+Alt+P)
3. Click the "Show Editor" button, then the open-file icon, and pick this file.
4. Press Run (the green triangle).

It reads outputs/tx_candidates.gpkg, styles everything, and saves
outputs/screen.qgz next to it. Re-run it any time you rebuild the screen.

If you moved the repo, set GPKG below to an absolute path.
"""

import os

from qgis.core import (
    QgsCategorizedSymbolRenderer, QgsClassificationQuantile, QgsFillSymbol,
    QgsGradientColorRamp, QgsGraduatedSymbolRenderer, QgsLineSymbol,
    QgsMarkerSymbol, QgsProject, QgsRasterLayer, QgsRendererCategory,
    QgsRendererRange, QgsVectorLayer,
)
from qgis.PyQt.QtGui import QColor

# --------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GPKG = os.path.join(REPO, "outputs", "tx_candidates.gpkg")
QGZ = os.path.join(REPO, "outputs", "screen.qgz")

if not os.path.exists(GPKG):
    raise SystemExit(
        f"GeoPackage not found: {GPKG}\n"
        f"Run  python3 scripts/build_screen.py  first."
    )

project = QgsProject.instance()
project.clear()

# --------------------------------------------------------------------------
# 1. Basemap FIRST so it lands at the bottom of the layer tree.
#    (addMapLayer inserts at the top, so earliest-added ends up lowest.)
# --------------------------------------------------------------------------
osm = QgsRasterLayer(
    "type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png"
    "&zmax=19&zmin=0",
    "OpenStreetMap",
    "wms",
)
if osm.isValid():
    project.addMapLayer(osm)
else:
    print("WARNING: OSM basemap failed to load (offline?). Continuing without it.")


def add(layer_name, style_fn, label=None):
    lyr = QgsVectorLayer(f"{GPKG}|layername={layer_name}", label or layer_name,
                         "ogr")
    if not lyr.isValid():
        print(f"  skip: layer '{layer_name}' not in the GeoPackage")
        return None
    style_fn(lyr)
    project.addMapLayer(lyr)
    print(f"  loaded {lyr.name()}  ({lyr.featureCount()} features)")
    return lyr


# --------------------------------------------------------------------------
# 2. Counties / water -- quiet context layers
# --------------------------------------------------------------------------
def style_counties(lyr):
    lyr.setRenderer(lyr.renderer().clone())
    sym = QgsFillSymbol.createSimple(
        {"color": "0,0,0,0", "outline_color": "120,120,120,140",
         "outline_width": "0.2"})
    lyr.renderer().setSymbol(sym)


def style_water(lyr):
    sym = QgsFillSymbol.createSimple(
        {"color": "80,140,200,90", "outline_color": "80,140,200,160",
         "outline_width": "0.2"})
    lyr.renderer().setSymbol(sym)


add("counties", style_counties)
add("water", style_water)


# --------------------------------------------------------------------------
# 3. Transmission lines -- categorised by voltage class
# --------------------------------------------------------------------------
VOLT_COLOURS = {
    "500kv_plus": ("#7a0177", 1.10, "500 kV +"),
    "345kv": ("#c51b8a", 0.90, "345 kV"),
    "220_287kv": ("#f768a1", 0.70, "220-287 kV"),
    "100_161kv": ("#fbb4b9", 0.50, "100-161 kV"),
    "under_100kv": ("#d9d9d9", 0.30, "under 100 kV"),
    "unknown": ("#bdbdbd", 0.25, "unknown"),
}


def style_lines(lyr):
    cats = []
    for value, (colour, width, label) in VOLT_COLOURS.items():
        sym = QgsLineSymbol.createSimple({"color": colour, "width": str(width)})
        cats.append(QgsRendererCategory(value, sym, label))
    lyr.setRenderer(QgsCategorizedSymbolRenderer("line_volt_class", cats))


add("transmission_lines", style_lines, "Transmission lines (by kV)")


# --------------------------------------------------------------------------
# 4. Substations -- graduated SIZE by max voltage
# --------------------------------------------------------------------------
def style_subs(lyr):
    base = QgsMarkerSymbol.createSimple(
        {"name": "square", "color": "255,190,60,200",
         "outline_color": "60,40,0,220", "outline_width": "0.2"})
    bands = [(0, 69, 1.2, "< 69 kV"), (69, 138, 1.8, "69-137 kV"),
             (138, 230, 2.6, "138-229 kV"), (230, 345, 3.4, "230-344 kV"),
             (345, 10000, 4.4, ">= 345 kV")]
    ranges = []
    for lo, hi, size, label in bands:
        s = base.clone()
        s.setSize(size)
        ranges.append(QgsRendererRange(lo, hi, s, label))
    lyr.setRenderer(QgsGraduatedSymbolRenderer("sub_max_kv", ranges))


add("substations", style_subs, "Substations (sized by max kV)")


# --------------------------------------------------------------------------
# 5. Candidates -- graduated colour by score, RED = HIGH
# --------------------------------------------------------------------------
def style_candidates(lyr):
    base = QgsMarkerSymbol.createSimple(
        {"name": "circle", "size": "3.6",
         "outline_color": "20,20,20,255", "outline_width": "0.4"})
    renderer = QgsGraduatedSymbolRenderer("score_total")
    renderer.setSourceSymbol(base.clone())
    # pale (low score) -> saturated red (high score)
    ramp = QgsGradientColorRamp(QColor("#fee5d9"), QColor("#a50f15"))
    renderer.setSourceColorRamp(ramp)
    try:
        renderer.setClassificationMethod(QgsClassificationQuantile())
        renderer.updateClasses(lyr, 5)
    except Exception:
        renderer.updateClasses(
            lyr, QgsGraduatedSymbolRenderer.Quantile, 5)
    lyr.setRenderer(renderer)
    lyr.setOpacity(0.95)


cand = add("candidates", style_candidates, "CANDIDATES (red = high score)")

# --------------------------------------------------------------------------
# 6. Zoom to candidates, save the project
# --------------------------------------------------------------------------
if cand is not None:
    try:
        from qgis.utils import iface
        iface.mapCanvas().setExtent(cand.extent())
        iface.mapCanvas().refresh()
        iface.setActiveLayer(cand)
    except Exception:
        pass

project.write(QGZ)
print(f"\nSaved QGIS project -> {QGZ}")
print("Open it directly next time: File -> Open Project.")
