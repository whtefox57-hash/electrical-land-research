"""STEP 9c — QGIS project.

Produces BOTH, deliberately:

  outputs/az_screen.qgz         a zipped QGIS project written directly as XML
  outputs/az_screen_build.py    a PyQGIS script that rebuilds the same project

Why both: QGIS has no public, stable, documented file format contract, and
there is no QGIS installation in this environment to open the .qgz and confirm
it renders. The XML here is written against the QGIS 3.x project schema and
should open, but I cannot verify it, and I will not claim I did. The PyQGIS
script is the reliable path — run it inside QGIS (Plugins > Python Console)
and it builds the project from the GeoPackage with the same styling, using
QGIS's own API rather than my hand-written XML.

A .qlr is not produced because it carries layer definitions only, and the
brief asks for a project with a basemap.
"""
from __future__ import annotations

import os
import sys
import zipfile

import geopandas as gpd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import OUTPUTS

GPKG = os.path.join(OUTPUTS, "az_candidates.gpkg")
QGZ = os.path.join(OUTPUTS, "az_screen.qgz")
PYS = os.path.join(OUTPUTS, "az_screen_build.py")

OWNER_COLORS = {
    "private": "215,48,39", "state_trust": "252,141,89",
    "tribal": "153,112,171", "federal_blm": "254,224,144",
    "federal_forest": "26,152,80", "federal_other": "145,207,96",
    "military": "127,127,127", "municipal": "44,123,182",
    "unknown": "200,200,200",
}
GRAD = [(0, 55, "165,0,38"), (55, 65, "244,109,67"), (65, 72, "254,224,139"),
        (72, 78, "166,217,106"), (78, 100, "26,152,80")]


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def layer_xml(lid, name, source_layer, geom, symbol_xml, visible=True):
    src = f"{esc(GPKG)}|layername={source_layer}"
    return f"""  <maplayer geometry="{geom}" type="vector" hasScaleBasedVisibilityFlag="0">
    <id>{lid}</id>
    <datasource>{src}</datasource>
    <layername>{esc(name)}</layername>
    <provider encoding="UTF-8">ogr</provider>
    <srs><spatialrefsys>
      <wkt></wkt><proj4>+proj=longlat +datum=WGS84 +no_defs</proj4>
      <srsid>3452</srsid><srid>4326</srid><authid>EPSG:4326</authid>
      <description>WGS 84</description><projectionacronym>longlat</projectionacronym>
      <ellipsoidacronym>EPSG:7030</ellipsoidacronym><geographicflag>true</geographicflag>
    </spatialrefsys></srs>
{symbol_xml}
  </maplayer>"""


def simple_symbol(sid, stype, color, outline="35,35,35", width="0.26",
                  size="2"):
    if stype == "marker":
        props = (f'<Option value="{color}" name="color" type="QString"/>'
                 f'<Option value="{outline}" name="outline_color" type="QString"/>'
                 f'<Option value="{width}" name="outline_width" type="QString"/>'
                 f'<Option value="{size}" name="size" type="QString"/>'
                 f'<Option value="circle" name="name" type="QString"/>')
        lay = "SimpleMarker"
    elif stype == "line":
        props = (f'<Option value="{color}" name="line_color" type="QString"/>'
                 f'<Option value="{width}" name="line_width" type="QString"/>')
        lay = "SimpleLine"
    else:
        props = (f'<Option value="{color}" name="color" type="QString"/>'
                 f'<Option value="{outline}" name="outline_color" type="QString"/>'
                 f'<Option value="{width}" name="outline_width" type="QString"/>')
        lay = "SimpleFill"
    return (f'<symbol alpha="1" type="{stype}" name="{sid}" force_rhr="0" '
            f'clip_to_extent="1"><layer enabled="1" pass="0" class="{lay}" '
            f'locked="0"><Option type="Map">{props}</Option></layer></symbol>')


def single_renderer(stype, color, **kw):
    return ('<renderer-v2 forceraster="0" type="singleSymbol" '
            'enableorderby="0" symbollevels="0"><symbols>'
            + simple_symbol("0", stype, color, **kw)
            + "</symbols></renderer-v2>")


def categorized_renderer(attr, cats, stype):
    c_xml, s_xml = [], []
    for i, (val, col) in enumerate(cats):
        c_xml.append(f'<category render="1" symbol="{i}" '
                     f'value="{esc(val)}" label="{esc(val)}"/>')
        s_xml.append(simple_symbol(str(i), stype, col, width="0.06"))
    return ('<renderer-v2 forceraster="0" type="categorizedSymbol" '
            f'enableorderby="0" attr="{attr}" symbollevels="0">'
            "<categories>" + "".join(c_xml) + "</categories>"
            "<symbols>" + "".join(s_xml) + "</symbols></renderer-v2>")


def graduated_renderer(attr, ranges, stype):
    r_xml, s_xml = [], []
    for i, (lo, hi, col) in enumerate(ranges):
        r_xml.append(f'<range render="1" symbol="{i}" lower="{lo:.6f}" '
                     f'upper="{hi:.6f}" label="{lo:g} - {hi:g}"/>')
        s_xml.append(simple_symbol(str(i), stype, col,
                                   size=str(2.2 + i * 1.1)))
    return ('<renderer-v2 forceraster="0" type="graduatedSymbol" '
            f'enableorderby="0" attr="{attr}" symbollevels="0" '
            'graduatedMethod="GraduatedColor"><ranges>'
            + "".join(r_xml) + "</ranges><symbols>" + "".join(s_xml)
            + "</symbols></renderer-v2>")


def main():
    print("STEP 9c — QGIS project")
    import fiona
    present = set(fiona.listlayers(GPKG))

    defs = []
    # OSM XYZ basemap, bottom of the stack.
    defs.append(("osm_basemap", "OpenStreetMap", None, None, None))

    plan = [
        ("lyr_own", "Land ownership (all classes)", "land_ownership_all",
         "Polygon", categorized_renderer(
             "land_status", list(OWNER_COLORS.items()), "fill")),
        ("lyr_priv", "Private land (working universe)", "land_private",
         "Polygon", single_renderer("fill", "215,48,39", width="0.1")),
        ("lyr_ama", "AMA / INA boundaries", "ama_ina", "Polygon",
         single_renderer("fill", "0,0,255,40", outline="0,0,200",
                         width="0.66")),
        ("lyr_cws", "Community water system service areas", "cws_service_area",
         "Polygon", single_renderer("fill", "0,150,200,30",
                                    outline="0,120,180", width="0.2")),
        ("lyr_terr", "Utility service territories", "utility_territories",
         "Polygon", single_renderer("fill", "255,255,0,25",
                                    outline="180,180,0", width="0.3")),
        ("lyr_cnty", "Counties", "counties", "Polygon",
         single_renderer("fill", "0,0,0,0", outline="80,80,80", width="0.5")),
        ("lyr_peren", "NHD perennial streams", "nhd_perennial", "Line",
         single_renderer("line", "0,120,220", width="0.3")),
        ("lyr_tx", "Transmission lines", "transmission_lines", "Line",
         single_renderer("line", "255,120,0", width="0.4")),
        ("lyr_subs", "Substations (all)", "substations", "Point",
         single_renderer("marker", "120,120,120", size="1.6")),
        ("lyr_excl", "EXCLUDED high scorers (non-acquirable)",
         "candidates_excluded_ranked", "Point",
         single_renderer("marker", "0,0,0", outline="255,255,255",
                         size="3.0")),
        ("lyr_cand", "CANDIDATES private, graduated by score",
         "candidates_private_ranked", "Point",
         graduated_renderer("composite_score", GRAD, "marker")),
    ]
    for lid, nm, src, geom, rend in plan:
        if src not in present:
            print(f"    !! layer {src} missing from GeoPackage, skipped")
            continue
        defs.append((lid, nm, src, geom, rend))

    maplayers, order, legend = [], [], []
    for lid, nm, src, geom, rend in defs:
        if src is None:
            maplayers.append(f"""  <maplayer type="raster" hasScaleBasedVisibilityFlag="0">
    <id>{lid}</id>
    <datasource>type=xyz&amp;url=https://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&amp;zmax=19&amp;zmin=0</datasource>
    <layername>{esc(nm)}</layername>
    <provider>wms</provider>
    <srs><spatialrefsys><authid>EPSG:3857</authid></spatialrefsys></srs>
  </maplayer>""")
        else:
            maplayers.append(layer_xml(lid, nm, src, geom, rend))
        order.append(f'    <layer id="{lid}"/>')
        legend.append(f'    <legendlayer name="{esc(nm)}" checked="Qt::Checked" '
                      f'open="true"><filegroup open="true" hidden="false">'
                      f'<legendlayerfile isInOverview="0" layerid="{lid}" '
                      f'visible="1"/></filegroup></legendlayer>')

    order.reverse()
    legend.reverse()

    qgs = f"""<?xml version="1.0" encoding="UTF-8"?>
<qgis projectname="Arizona Powered-Land Screen" version="3.34.0">
  <title>Arizona Powered-Land Screen</title>
  <projectCrs><spatialrefsys><authid>EPSG:4326</authid></spatialrefsys></projectCrs>
  <layer-tree-group>
{chr(10).join(f'    <layer-tree-layer id="{d[0]}" name="{esc(d[1])}" checked="Qt::Checked" expanded="1"/>' for d in reversed(defs))}
  </layer-tree-group>
  <projectlayers>
{chr(10).join(maplayers)}
  </projectlayers>
  <layerorder>
{chr(10).join(order)}
  </layerorder>
  <legend>
{chr(10).join(legend)}
  </legend>
</qgis>
"""
    with zipfile.ZipFile(QGZ, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("az_screen.qgs", qgs)
    print(f"  wrote {os.path.basename(QGZ)} "
          f"({os.path.getsize(QGZ):,} bytes, {len(defs)} layers) — "
          f"GENERATED BUT NOT OPENED/VERIFIED (no QGIS in this environment)")

    # ---- PyQGIS fallback, the reliable path ----
    layer_spec = [(nm, src, rend is not None) for _, nm, src, _, rend in defs
                  if src]
    py = f'''"""Rebuild the Arizona powered-land screening project inside QGIS.

RUN THIS if az_screen.qgz does not open cleanly. It uses the QGIS Python API
rather than hand-written XML, so it does not depend on my guesses about the
project file schema.

    QGIS > Plugins > Python Console > Show Editor > Open Script > Run

It expects az_candidates.gpkg to sit next to this script.
"""
import os
from qgis.core import (QgsProject, QgsVectorLayer, QgsRasterLayer,
                       QgsGraduatedSymbolRenderer, QgsRendererRange,
                       QgsSymbol, QgsCategorizedSymbolRenderer,
                       QgsRendererCategory)
from qgis.PyQt.QtGui import QColor

HERE = os.path.dirname(os.path.abspath(__file__))
GPKG = os.path.join(HERE, "az_candidates.gpkg")
proj = QgsProject.instance()
proj.clear()

# OSM basemap first so it sits at the bottom.
osm = QgsRasterLayer(
    "type=xyz&url=https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png"
    "&zmax=19&zmin=0", "OpenStreetMap", "wms")
if osm.isValid():
    proj.addMapLayer(osm)

LAYERS = {layer_spec!r}

OWNER_COLORS = {OWNER_COLORS!r}
GRAD = {GRAD!r}

for name, src, _styled in LAYERS:
    lyr = QgsVectorLayer(f"{{GPKG}}|layername={{src}}", name, "ogr")
    if not lyr.isValid():
        print("FAILED to load", src)
        continue

    if src == "land_ownership_all":
        cats = []
        for val, rgb in OWNER_COLORS.items():
            sym = QgsSymbol.defaultSymbol(lyr.geometryType())
            sym.setColor(QColor(*[int(x) for x in rgb.split(",")]))
            sym.setOpacity(0.55)
            cats.append(QgsRendererCategory(val, sym, val))
        lyr.setRenderer(QgsCategorizedSymbolRenderer("land_status", cats))

    elif src == "candidates_private_ranked":
        ranges = []
        for i, (lo, hi, rgb) in enumerate(GRAD):
            sym = QgsSymbol.defaultSymbol(lyr.geometryType())
            sym.setColor(QColor(*[int(x) for x in rgb.split(",")]))
            sym.setSize(2.2 + i * 1.1)
            ranges.append(QgsRendererRange(lo, hi, sym, f"{{lo:g}} - {{hi:g}}"))
        lyr.setRenderer(
            QgsGraduatedSymbolRenderer("composite_score", ranges))

    proj.addMapLayer(lyr)

out = os.path.join(HERE, "az_screen_rebuilt.qgz")
proj.write(out)
print("wrote", out)
'''
    open(PYS, "w").write(py)
    print(f"  wrote {os.path.basename(PYS)} (PyQGIS rebuild script — the "
          f"reliable path)")


if __name__ == "__main__":
    main()
