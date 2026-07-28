"""
Central configuration for the Texas powered-land GIS screen.

TUNE THE RUBRIC HERE. Everything the scoring model depends on lives in this
file so that weights can be recalibrated without touching pipeline logic.

Rubric provenance: the weights below are the FIRST-DRAFT rubric supplied in the
project brief. They are a hypothesis, not a calibrated model. Nothing in this
repository validates them against real substation headroom.
"""

from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
OUTPUTS = ROOT / "outputs"

for _p in (RAW, INTERIM, OUTPUTS):
    _p.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Projection
# --------------------------------------------------------------------------
# The brief specified EPSG:3081 and described it as "Texas Centric Albers".
# That description belongs to EPSG:3083 (NAD83 / Texas Centric Albers Equal
# Area). EPSG:3081 is NAD83 / Texas State Mapping System, a Lambert Conformal
# Conic projection. BOTH are metre-based and both are appropriate for
# statewide Texas distance work, so the specified value is honoured as the
# default. Set TXLAND_CRS=3083 in the environment to switch.
#
# This discrepancy is recorded in outputs/METHOD.md at run time.
WORKING_CRS = int(os.environ.get("TXLAND_CRS", 3081))
GEOGRAPHIC_CRS = 4326

# Texas bounding box in WGS84 (xmin, ymin, xmax, ymax). Used to clip national
# datasets and to build ArcGIS REST envelope queries. Deliberately generous.
TX_BBOX = (-107.0, 25.5, -93.4, 36.7)

# --------------------------------------------------------------------------
# Screening thresholds (Step 3)
# --------------------------------------------------------------------------
# Population 1: plants with retired / announced-retirement capacity at or above
# this many MW. These carry existing interconnection.
POP1_MIN_RETIRED_MW = 50.0

# Population 1 only counts retirements from this year onward, plus any
# announced future retirement regardless of year.
POP1_RETIRED_SINCE_YEAR = 2010

# Population 2: substations at or above this max voltage (kV) that are not
# within POP2_EXCLUSION_M of a Population 1 site.
POP2_MIN_KV = 138.0
POP2_EXCLUSION_M = 2000.0

# Neighbourhood radius for "count within X km" metrics.
NEIGHBOURHOOD_M = 5000.0

# Interconnection rights can lapse. Retirements older than this are flagged and
# penalised by INTERCONNECT_STALE_MULTIPLIER.
STALE_RETIREMENT_YEARS = 10
INTERCONNECT_STALE_MULTIPLIER = 0.5

TOP_N = 25

# As-of date for all "years since retirement" arithmetic. Pinned via env var
# for reproducible reruns; otherwise the run date. Recorded in METHOD.md.
AS_OF_DATE = _dt.date.fromisoformat(
    os.environ.get("TXLAND_AS_OF", _dt.date.today().isoformat())
)

# --------------------------------------------------------------------------
# SCORING RUBRIC -- TUNE HERE
# --------------------------------------------------------------------------
# Each block is (threshold, points), evaluated top-down; the first matching
# threshold wins. Distance thresholds are metres, voltage thresholds are kV,
# capacity thresholds are MW.
#
# Total possible = 30 + 25 + 15 + 15 + 10 + 5 = 100.
# NOTE: if the water layer (source E) is unavailable, the water component
# scores 0 for every candidate and the practical maximum becomes 95. The
# screen does NOT rescale to compensate -- see METHOD.md.
RUBRIC: dict = {
    # ---- Existing interconnection (0-30) --------------------------------
    # Keyed on retired-or-announced MW aggregated to plant level.
    "interconnection": {
        "max_points": 30,
        "bands_mw": [
            (500.0, 30),
            (200.0, 22),
            (50.0, 14),
            (0.0, 0),
        ],
        # Applied when years_since_retirement > STALE_RETIREMENT_YEARS.
        "stale_multiplier": INTERCONNECT_STALE_MULTIPLIER,
    },
    # ---- Substation proximity (0-25) ------------------------------------
    "substation_proximity": {
        "max_points": 25,
        "bands_m": [
            (1000.0, 25),
            (3000.0, 18),
            (5000.0, 10),
            (10000.0, 3),
        ],
        "beyond": 0,
    },
    # ---- Substation voltage (0-15) --------------------------------------
    # Uses the max voltage of the NEAREST substation.
    "substation_voltage": {
        "max_points": 15,
        "bands_kv": [
            (345.0, 15),
            (230.0, 12),
            (138.0, 8),
            (69.0, 3),
        ],
        "below": 0,
    },
    # ---- Transmission proximity x voltage (0-15) ------------------------
    # FORMULA (documented per the brief):
    #
    #     tx_points = 15 * distance_factor * voltage_factor
    #
    # where distance_factor is selected from the nearest transmission line's
    # distance and voltage_factor from that same line's kV. The product form
    # is deliberate: a 500 kV line 40 km away is worth nothing to a site, and
    # a 69 kV line at the fence line is worth little either. Both conditions
    # must hold for the component to pay out. A site scores the full 15 only
    # when a >=345 kV line is within 1 km.
    "transmission": {
        "max_points": 15,
        "distance_factors_m": [
            (1000.0, 1.00),
            (3000.0, 0.80),
            (5000.0, 0.55),
            (10000.0, 0.25),
        ],
        "distance_factor_beyond": 0.0,
        "voltage_factors_kv": [
            (345.0, 1.00),
            (230.0, 0.85),
            (138.0, 0.65),
            (69.0, 0.35),
        ],
        "voltage_factor_below": 0.15,
    },
    # ---- Broadband providers in block group (0-10) ----------------------
    # PROXY for fibre availability. See METHOD.md -- this is not a fibre route.
    "broadband": {
        "max_points": 10,
        "bands_count": [
            (4, 10),
            (3, 7),
            (2, 4),
            (1, 1),
        ],
        "none_or_unknown": 0,
    },
    # ---- Water proximity (0-5) ------------------------------------------
    "water": {
        "max_points": 5,
        "bands_m": [
            (2000.0, 5),
            (5000.0, 4),
            (10000.0, 2),
            (25000.0, 1),
        ],
        "beyond": 0,
        # Set automatically at run time when source E is missing.
        "unavailable_score": 0,
    },
}

MAX_POSSIBLE_SCORE = sum(v["max_points"] for v in RUBRIC.values())

# --------------------------------------------------------------------------
# Voltage classes used for transmission line grouping and styling
# --------------------------------------------------------------------------
VOLTAGE_CLASSES: list[tuple[str, float, float]] = [
    ("under_100kv", 0.0, 100.0),
    ("100_161kv", 100.0, 162.0),
    ("220_287kv", 162.0, 300.0),
    ("345kv", 300.0, 400.0),
    ("500kv_plus", 400.0, 10_000.0),
]

# HIFLD and several EIA extracts use large negative sentinels for "unknown".
# Treated as missing, never as a real value.
NULL_SENTINELS = (-999999, -999999.0, -99999, -9999, -888888)
