"""
Build outputs/screen.qgz — RUN THIS FROM THE QGIS PYTHON CONSOLE.

Why a script and not a .qgz written directly:
    The container that produced these outputs has no QGIS installed, so a
    hand-authored .qgz project XML could not be opened or validated there.
    Shipping an untested project file that might fail to load is worse than
    shipping a script that provably builds one on your machine. This uses only
    long-stable PyQGIS APIs (manual renderer ranges rather than the
    createRenderer convenience wrappers, which have shifted between releases).

HOW TO RUN
    1. Open QGIS.
    2. Plugins > Python Console  (Ctrl+Alt+P)
    3. Click the "Show Editor" button, open this file, press Run.
       Or paste into the console:
           exec(open('/full/path/to/scripts/build_qgis_project.py').read())
    4. It loads every layer, styles them, adds an OpenStreetMap basemap at the
       bottom, and saves outputs/screen.qgz next to the GeoPackage.
       The project also stays open in your current QGIS session.

If your GeoPackage lives elsewhere, edit GPKG below.
"""
import os

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsFillSymbol,
    QgsGraduatedSymbolRenderer,
    QgsLineSymbol,
    QgsMarkerSymbol,
    QgsProject,
    QgsRasterLayer,
    QgsRendererRange,
    QgsSingleSymbolRenderer,
    QgsVectorLayer,
)

# Resolve paths relative to this script so it works wherever the repo sits.
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
ROOT = os.path.dirname(HERE) if os.path.basename(HERE) == "scripts" else HERE
GPKG = os.path.join(ROOT, "outputs", "tx_candidates.gpkg")
QGZ = os.path.join(ROOT, "outputs", "screen.qgz")

assert os.path.exists(GPKG), f"GeoPackage not found: {GPKG}"

project = QgsProject.instance()
project.clear()
project.setCrs(QgsCoordinateReferenceSystem("EPSG:3081"))


def add(layer_name, display):
    lyr = QgsVectorLayer(f"{GPKG}|layername={layer_name}", display, "ogr")
    if not lyr.isValid():
        print(f"  SKIP {layer_name} (not in GeoPackage)")
        return None
    project.addMapLayer(lyr)
    print(f"  loaded {display}: {lyr.featureCount()} features")
    return lyr


def graduated(lyr, field, bands, symbol_factory):
    """bands = [(low, high, label, kwargs_for_symbol_factory), ...]"""
    ranges = []
    for lo, hi, label, kw in bands:
        ranges.append(QgsRendererRange(lo, hi, symbol_factory(**kw), label))
    lyr.setRenderer(QgsGraduatedSymbolRenderer(field, ranges))
    lyr.triggerRepaint()


def marker(color, size, outline="35,35,35,255", width="0.2"):
    return QgsMarkerSymbol.createSimple({
        "name": "circle", "color": color, "outline_color": outline,
        "outline_width": width, "size": str(size)})


def line(color, width):
    return QgsLineSymbol.createSimple({"color": color, "width": str(width)})


print("Loading layers...")

# --- basemap first so it ends up at the BOTTOM of the layer order ---
osm = QgsRasterLayer(
    "type=xyz&url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png"
    "&zmax=19&zmin=0",
    "OpenStreetMap", "wms")
if osm.isValid():
    project.addMapLayer(osm)
    print("  loaded OpenStreetMap basemap")
else:
    print("  WARNING: OSM basemap failed to load (offline?). Add manually via "
          "Browser > XYZ Tiles > OpenStreetMap.")

counties = add("counties", "Texas counties")
water = add("water", "Water (TWDB reservoirs + major rivers)")
lines = add("transmission_lines", "Transmission lines (HIFLD)")
subs = add("substations_proxy", "Substations (DERIVED PROXY - line endpoints)")
if subs is None:
    subs = add("substations", "Substations")
cand = add("candidates", "Candidate sites (scored)")

# --- counties: hollow outline ---
if counties:
    counties.setRenderer(QgsSingleSymbolRenderer(
        QgsFillSymbol.createSimple({
            "color": "0,0,0,0", "outline_color": "110,110,110,180",
            "outline_width": "0.18"})))

# --- water: blue, subtle ---
if water:
    water.setRenderer(QgsSingleSymbolRenderer(
        QgsFillSymbol.createSimple({
            "color": "150,195,235,110", "outline_color": "90,150,205,190",
            "outline_width": "0.2"})))

# --- transmission lines coloured by voltage class ---
if lines:
    graduated(lines, "voltage_kv", [
        (0.0,   69.0,  "under 69 kV",   dict(color="190,190,190,200", width=0.20)),
        (69.0,  138.0, "69-137 kV",     dict(color="120,175,120,220", width=0.30)),
        (138.0, 230.0, "138-229 kV",    dict(color="235,175,60,235",  width=0.45)),
        (230.0, 345.0, "230-344 kV",    dict(color="235,110,30,240",  width=0.60)),
        (345.0, 1000.0, "345 kV and up", dict(color="200,25,25,255",  width=0.85)),
    ], line)

# --- substations sized by voltage ---
if subs:
    graduated(subs, "max_voltage_kv", [
        (0.0,   69.0,   "under 69 kV",    dict(color="205,205,205,200", size=1.4)),
        (69.0,  138.0,  "69-137 kV",      dict(color="150,200,150,220", size=2.0)),
        (138.0, 230.0,  "138-229 kV",     dict(color="245,200,90,235",  size=2.8)),
        (230.0, 345.0,  "230-344 kV",     dict(color="245,140,50,240",  size=3.6)),
        (345.0, 1000.0, "345 kV and up",  dict(color="215,45,45,255",   size=4.6)),
    ], marker)

# --- candidates graduated by score, red = high ---
if cand:
    graduated(cand, "score", [
        (0.0,  40.0,  "0-40 (low)",       dict(color="255,245,210,255", size=2.6)),
        (40.0, 60.0,  "40-60",            dict(color="253,205,130,255", size=3.4)),
        (60.0, 75.0,  "60-75",            dict(color="250,150,75,255",  size=4.2)),
        (75.0, 90.0,  "75-90",            dict(color="228,80,45,255",   size=5.2)),
        (90.0, 100.01, "90-100 (highest)", dict(color="165,10,20,255",   size=6.4)),
    ], marker)
    # Label only the strong candidates - there are ~2,700 points in this layer
    # and labelling all of them makes the map unreadable.
    from qgis.core import (QgsPalLayerSettings, QgsTextFormat,
                           QgsVectorLayerSimpleLabeling)
    fmt = QgsTextFormat()
    fmt.setSize(9)
    settings = QgsPalLayerSettings()
    settings.isExpression = True
    settings.fieldName = 'CASE WHEN "score" >= 83 THEN "site_name" END'
    settings.setFormat(fmt)
    # Placement enum moved into a nested class in QGIS 3.26+; support both.
    try:
        settings.placement = QgsPalLayerSettings.Placement.AroundPoint
    except AttributeError:
        settings.placement = QgsPalLayerSettings.AroundPoint
    cand.setLabeling(QgsVectorLayerSimpleLabeling(settings))
    cand.setLabelsEnabled(True)

# --- layer order: basemap at the bottom, candidates on top ---
order = [lyr for lyr in [cand, subs, lines, water, counties, osm] if lyr]
root = project.layerTreeRoot()
root.setHasCustomLayerOrder(True)
root.setCustomLayerOrder(order)

# --- zoom to candidates ---
if cand:
    try:
        from qgis.utils import iface
        iface.mapCanvas().setExtent(cand.extent())
        iface.mapCanvas().refresh()
    except Exception:
        pass

os.makedirs(os.path.dirname(QGZ), exist_ok=True)
ok = project.write(QGZ)
print(f"\n{'WROTE' if ok else 'FAILED to write'} {QGZ}")
print("Layer order (top to bottom):",
      " > ".join(lyr.name() for lyr in order))
print("\nNOTE: the substation layer is a DERIVED PROXY built from transmission")
print("line endpoints, not a substation dataset. See outputs/METHOD.md.")
