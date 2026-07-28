# Week 1 visual review — Cowork prompt

Copy everything inside the fenced block below into Claude Cowork.

**Before you paste:**
1. Open Cowork in the `electrical-land-research` repo folder (the one containing
   `outputs/top25_candidates.csv`).
2. Have Chrome open. Signed into Google Maps is fine but not required.
3. Expect it to take a while — it is looking at 25 sites in satellite view, one
   at a time, and writing notes for each.
4. It is told to write `UNSURE` rather than guess. Sites marked `UNSURE` are the
   ones you should personally look at. Do not treat its `KILL` verdicts as final
   without a glance — it is screening for you, not deciding for you.

---

```
You are helping me finish Week 1 of a powered-land screen for large-load data
center development in Texas. The GIS work is already done. Your job is the
visual and judgment pass on top of it, and to write your findings back into the
repository as files.

Work in the current directory. It is a git repo containing:

  outputs/top25_candidates.csv   the 25 ranked candidate sites (51 columns)
  outputs/COUNTY_SUMMARY.csv     234 counties, sorted so the 38 containing a
                                 real retired/retiring plant come first
  outputs/tx_candidates.gpkg     GeoPackage, 5 layers, EPSG:3081
  outputs/preview_map.png        static overview map, top 25 labelled
  outputs/METHOD.md              full method, sources, and limitations
  scripts/build_qgis_project.py  PyQGIS script that builds outputs/screen.qgz
  DATA_STATUS.md                 record of which datasets downloaded and failed

READ outputs/METHOD.md FIRST, in full, before you look at any site. It tells you
what the scores do and do not mean. Sections 1, 4 and 10 matter most.

BACKGROUND — what I am actually looking for

Interconnection queues in ERCOT run 4-7 years. That makes land with EXISTING
electrical interconnection worth far more than raw land. Retired power plants
are the prize: the switchyard, the transmission lines, and often the
interconnection rights are already there. I am screening for parcels I can
physically go look at and then discuss with county economic development offices
and utility account managers.

So when you look at a site, the question is never "is this a nice piece of
land." It is: "could a 100-300 MW data center plausibly be energized here in
under three years, and can I buy or lease the dirt?"

WHAT THE SCORES ALREADY GOT WRONG — you are the check on this

The screen has known defects. Two matter for your review:

  1. NO REAL SUBSTATION DATA. Every substation source was blocked by network
     policy. The "substations" in this screen are DERIVED by clustering
     transmission line endpoints. 40 of the 90 scored points rest on that proxy.
     A node may be a splice or a segment split, not a substation. YOUR EYES ARE
     THE FIRST REAL VERIFICATION THAT A SWITCHYARD EXISTS AT ALL. This is the
     single most valuable thing you will do.

  2. TWO SITES IN THE TOP 25 ARE PROBABLY TRAPS. Jones (rank 19, Lubbock County)
     and Harrington (rank 17, Potter County) have no past retirement — their
     announced retirement years are 2058 and 2040. They should be fully
     operational plants today, not acquirable. Confirm this visually and kill
     them if confirmed. The column `retirement_beyond_horizon` flags them.

CRITICAL RULE — the same one that governed the data work

Never fabricate, estimate, or invent an observation. If satellite imagery is
unclear, obstructed, low resolution, or you cannot tell, write "UNSURE" or
"cannot determine" and say why. A blank cell with an honest reason is far more
useful to me than a confident guess. I am going to drive to some of these
places. If you tell me there is a switchyard and there is not, you have wasted
my day.

Never claim to have viewed something you did not view. If a link fails, record
the failure. Do not infer what a site looks like from its name, its score, its
county, or from what other sites look like.

---

STEP 1 — THE MAP

Try, in this order, and tell me which one you did:

  a. Open QGIS and build the project: run scripts/build_qgis_project.py from the
     QGIS Python console (Plugins > Python Console > Show Editor > open the file
     > Run). That writes outputs/screen.qgz. Then look at the map.
  b. If QGIS is not installed or you cannot drive it, say so plainly and instead
     open outputs/preview_map.png and read outputs/tx_candidates.gpkg directly
     with geopandas.

Either way, answer these in your notes:
  - Are the candidates clustered or spread across the state?
  - Do the high scorers sit on the 345 kV backbone, or are some isolated?
  - Anything that looks obviously wrong — a point in the Gulf, a point in New
    Mexico, a cluster that looks like a data artifact?

Do not skip this and do not pretend you did it.

---

STEP 2 — SATELLITE REVIEW OF ALL 25 SITES

Read outputs/top25_candidates.csv. Every row has a `google_maps_url` column
built from that site's own coordinates. Work through all 25 in rank order.

For each site:
  - Open the google_maps_url in Chrome.
  - Switch to satellite view. Zoom out to roughly a 2-3 km view first to see the
    context, then zoom in on the plant footprint.
  - Take a screenshot and save it to outputs/site_screenshots/ as
    rank<NN>_<site_name_slug>.png (e.g. rank01_big_brown.png).
  - Where Street View exists on an adjacent road, glance at it — it often
    resolves whether a switchyard is live.

Assess these seven things. Definitions matter — use them, do not freestyle:

  1. switchyard_visible  (YES / NO / UNSURE)
     A switchyard or substation reads as a rectangular fenced gravel or bare
     lot with lattice steel structures, transformer blocks, visible busbars, and
     multiple transmission lines converging on it. It is NOT the same as the
     plant buildings. This is the single most important observation. If you see
     one, note roughly how big it is and whether lines still run to it.

  2. plant_status  (STANDING / PARTIALLY_DEMOLISHED / CLEARED / OPERATING / UNSURE)
     Look for stacks, boiler houses, cooling towers, coal piles, conveyors.
     OPERATING means visible signs of live generation — steam or exhaust plumes,
     fresh coal or fuel stock, full parking lots, maintained grounds.
     CLEARED means the structures are gone and you can see slab or bare ground.
     The ideal for me is CLEARED or PARTIALLY_DEMOLISHED with the switchyard
     still intact — clean dirt, live interconnection.

  3. residential_encroachment  (NONE / LIGHT / HEAVY / UNSURE)
     Housing subdivisions, schools, churches within roughly 1 km. Note the
     direction and rough distance. Data centers generate noise complaints and
     zoning fights; a site ringed by houses is a hard site.

  4. rail_access  (YES / NEAR / NO / UNSURE)
     YES = a spur visibly enters the site. NEAR = a mainline within about 1 km
     but no spur. Rail is a nice-to-have, not a requirement.

  5. water_visible  (YES / NO / UNSURE)
     Cooling pond, reservoir, or river adjacent to or on the site. Note which.

  6. open_land  (rough acreage estimate, or UNSURE)
     How much contiguous open, buildable-looking land sits next to the
     switchyard. Use the Maps measure tool if you can; if you are eyeballing it,
     say so explicitly and give a range, not a point number.

  7. signs_of_recent_activity  (YES / NO / UNSURE)
     New construction, solar or battery installations on the footprint, graded
     pads, active vehicle presence, fresh laydown yards. Conversely: overgrown
     lots, collapsed roofs, rusted structures, flooded pits. If Google shows an
     imagery capture date, record it — imagery can be years stale and that
     changes how much weight this deserves.

Then give each site:

  visual_verdict  (KEEP / KILL / UNSURE)
  verdict_reason  one or two sentences, concrete and specific to what you saw

Verdict guidance:
  KILL if the plant is clearly still OPERATING (not acquirable), if there is no
  switchyard and no transmission infrastructure visible at all, if the site is
  boxed in by dense residential with no adjacent open land, or if the
  coordinates plainly do not land on an industrial site.
  KEEP if there is a visible switchyard AND meaningful open land.
  UNSURE for anything else. Use UNSURE freely. I would rather personally check
  ten sites than have you wrongly kill one good one.

Specific things to check while you are in there:
  - Jones (rank 19) and Harrington (rank 17): confirm whether they look
    operational. If yes, KILL and say what you saw that shows it.
  - Bexar County has four sites in the top 25 (J K Spruce, J T Deely,
    O W Sommers, V H Braunig). I believe these are one adjacent CPS Energy
    campus, not four independent opportunities. Check whether they share a
    footprint and say so explicitly — it changes whether Bexar is one phone call
    or four.
  - Any site where the imagery shows a solar farm or battery installation
    already built on the old plant footprint: that land is taken. Flag it loudly.

---

STEP 3 — WRITE IT ALL BACK TO FILES

Create these. Do not just report in chat — I need the files in the repo.

  1. outputs/top25_reviewed.csv
     Every column from top25_candidates.csv, unchanged, PLUS:
       switchyard_visible, plant_status, residential_encroachment, rail_access,
       water_visible, open_land_acres_est, signs_of_recent_activity,
       imagery_date_if_shown, visual_verdict, verdict_reason,
       screenshot_path, reviewed_at
     Do not alter, reorder, or recompute any existing column. Append only.

  2. outputs/SITE_NOTES.md
     One section per site in rank order. Heading with rank, name, county, score
     and MW. Then your observations in plain prose — what you actually saw, what
     you could not tell, and the verdict with its reason. Include the
     google_maps_url and the screenshot path in each section so I can jump
     straight there. Two to six sentences per site is right. This is the
     document I will read on a plane.

  3. outputs/site_screenshots/
     The 25 screenshots, named as specified above.

  4. outputs/WEEK2_CALLS.md
     See Step 4.

  5. Append a short section to outputs/METHOD.md titled
     "## 12. Visual review (Week 1)" recording: the date, that a Claude Cowork
     agent performed the satellite review rather than a human, which sites were
     killed and why, how many came back UNSURE, and — importantly — the
     limitations of an imagery-only review. Explicitly state that satellite
     review cannot establish parcel boundaries, ownership, easements,
     environmental liability, interconnection rights, or transformer headroom.
     Do not renumber or edit the existing sections of METHOD.md.

---

STEP 4 — PICK THE THREE COUNTIES TO CALL

Open outputs/COUNTY_SUMMARY.csv. It is sorted so counties containing a real
retired or retiring plant come first. IGNORE the `mean_score` column — it
averages across thousands of proxy nodes and is close to meaningless. Use
`pop1_candidates`, `total_retired_mw`, `total_site_mw` and `pop1_best_site`.

Now pick three counties for me to call, using your Step 2 findings, not just the
spreadsheet. A county whose only site you just marked KILL should not make the
list no matter what its MW total says.

Write outputs/WEEK2_CALLS.md containing, for each of the three:
  - County name, and the specific site or sites driving the pick
  - Retired and announced MW, and how many candidates survived your review
  - Why this county over the alternatives, in your own words
  - What to ask on the call. Be concrete and specific to the site. Good
    questions: is the interconnection agreement still active or was it
    terminated at retirement; what is the current transformer headroom at the
    connecting substation; is the parcel separable from the utility's retained
    land; is there an environmental or remediation encumbrance; what is the
    current zoning and has the county handled a large-load request before.
  - Who to contact: the county economic development office and the utility whose
    name appears in `nearest_line_owner` for that site. Search for the actual
    office name and a public contact page and include the URL. If you cannot
    find one, say so — do not invent a name, a person, a phone number or an
    email address. A fabricated contact is worse than a blank.

Also list, briefly, the next two counties as backups in case the first three
dead-end.

---

WHEN YOU ARE DONE

Commit everything to the current git branch with a clear message and push it.
Do not open a pull request unless I ask.

Then report to me in chat:
  - How many sites you marked KEEP, KILL, UNSURE
  - Every site you killed and the one-line reason
  - Every site you could not assess, and why
  - Whether the Bexar sites are one campus or four
  - Whether Jones and Harrington are operating
  - Your three counties
  - Anything you saw that the score got badly wrong in either direction —
    especially any site the score ranked low that looked excellent, since I only
    gave you the top 25 and a good site sitting at rank 30 is invisible to me

If Chrome, Google Maps, or QGIS blocks you, or imagery is unavailable for a
site, tell me exactly which site and what happened. Do not silently skip it and
do not fill the row with plausible-looking guesses.
```

---

## Optional add-on: fetch the substation data while you are in there

If you also want the agent to close the biggest gap in the screen, append this
to the prompt. It only works if you can reach one of these sources.

```
BONUS TASK — get me the substation layer.

The screen is missing real substation data; it currently uses a derived proxy
built from transmission line endpoints. Try to download a Texas electric
substations layer, in this order:

  1. https://atlas.eia.gov  — search "substations", export GeoJSON or Shapefile
  2. https://www.arcgis.com/home/search.html?q=electric%20substations
     — filter to Feature Layer, find a HIFLD-derived substations layer, export
  3. https://overpass-turbo.eu — paste this query, Run, then Export > GeoJSON:

     [out:json][timeout:600];
     area["ISO3166-2"="US-TX"][admin_level=4]->.tx;
     ( node["power"="substation"](area.tx);
       way["power"="substation"](area.tx);
       relation["power"="substation"](area.tx); );
     out center tags;

Save whatever you get into data/raw/ with the word "substation" in the filename
(.geojson, .gpkg, .shp, .zip, or .csv with lat/lon columns). Then re-run:

     python scripts/build_screen.py && python scripts/verify.py

It auto-detects the file, maps common field spellings, replaces the proxy,
restores the full 25 + 15 substation rubric points, and rebuilds Population 2
from real substations. No code change needed.

If the top 25 changes as a result, redo Step 2 for any site that is newly in the
list, and tell me which sites entered and which dropped out. Record which source
you actually got the data from and the date, and add it to the source table in
outputs/METHOD.md section 2.

If all three sources fail, say so and stop — do not substitute anything else.
```
