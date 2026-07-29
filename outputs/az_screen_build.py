"""Rebuild the Arizona powered-land screening project inside QGIS.

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
    "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    "&zmax=19&zmin=0", "OpenStreetMap", "wms")
if osm.isValid():
    proj.addMapLayer(osm)

LAYERS = [('Land ownership (all classes)', 'land_ownership_all', True), ('Private land (working universe)', 'land_private', True), ('AMA / INA boundaries', 'ama_ina', True), ('Community water system service areas', 'cws_service_area', True), ('Utility service territories', 'utility_territories', True), ('Counties', 'counties', True), ('NHD perennial streams', 'nhd_perennial', True), ('Transmission lines', 'transmission_lines', True), ('Substations (all)', 'substations', True), ('EXCLUDED high scorers (non-acquirable)', 'candidates_excluded_ranked', True), ('CANDIDATES private, graduated by score', 'candidates_private_ranked', True)]

OWNER_COLORS = {'private': '215,48,39', 'state_trust': '252,141,89', 'tribal': '153,112,171', 'federal_blm': '254,224,144', 'federal_forest': '26,152,80', 'federal_other': '145,207,96', 'military': '127,127,127', 'municipal': '44,123,182', 'unknown': '200,200,200'}
GRAD = [(0, 55, '165,0,38'), (55, 65, '244,109,67'), (65, 72, '254,224,139'), (72, 78, '166,217,106'), (78, 100, '26,152,80')]

for name, src, _styled in LAYERS:
    lyr = QgsVectorLayer(f"{GPKG}|layername={src}", name, "ogr")
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
            ranges.append(QgsRendererRange(lo, hi, sym, f"{lo:g} - {hi:g}"))
        lyr.setRenderer(
            QgsGraduatedSymbolRenderer("composite_score", ranges))

    proj.addMapLayer(lyr)

out = os.path.join(HERE, "az_screen_rebuilt.qgz")
proj.write(out)
print("wrote", out)
