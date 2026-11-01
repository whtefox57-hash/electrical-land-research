# AZ UTILITY MAP

Generated 2026-07-29. Which category of utility serves a parcel determines who the user calls and what process applies. In Arizona that is not a formality — it decides whether there is an ACC docket at all.

## The four regimes

| utility_type | who regulates rates | how a large load gets served | who you call |
|---|---|---|---|
| `IOU_ACC_regulated` | Arizona Corporation Commission, five **elected** commissioners | tariff election (APS XHLF / E-34 / E-32 L) or a docketed special contract (the TEP–Project Blue model) | utility economic development, then the ACC docket |
| `SRP_public` | **Nobody external.** SRP's board is elected by landowners inside the district on an **acreage franchise** | SRP E-67 large-customer provision: new accounts ≥20 MW forecast load face minimum billing at the greater of actual demand or 80% of forecast | SRP staff, then the SRP board. **There is no ACC docket to intervene in.** |
| `coop` | member-governed; ACC jurisdiction over co-ops is limited | co-op board plus its G&T supplier — the wholesale contract usually binds harder than the retail tariff | co-op general manager AND the generation & transmission supplier |
| `municipal` | city council or district board | council/board decision, often bundled into a development agreement | city manager / district manager |

## Thresholds that actually exist

Read from `outputs/AZ_SIZE_THRESHOLDS.md`, unchanged:

- **APS XHLF** — ≥5,000 kW monthly maximum demand **and** ≥92% load factor.
  **In active revision** under Docket E-01345A-25-0105; hearings opened 18 May
  2026, decision expected before end of 2026, with roughly a 45% increase
  reported for that class and direct assignment of new generation costs. The
  eligibility floor itself is one of the things under revision — **do not quote
  XHLF terms to a developer as settled.**
- **SRP E-67** — ≥20 MW forecast load triggers minimum billing at 80% of
  forecast. Approved by the SRP Board 27 February 2025.
- **TEP** — no published generic large-load threshold. The template is the
  bespoke docketed special contract: Project Blue, approved 3 December 2025
  4–1, capped at 286 MW, full approved rates with no discount, customer bears
  incremental generation cost beyond the cap. **It is being litigated** —
  Attorney General Mayes sued the ACC and has appealed.

## The honest limitation in this mapping

HIFLD's Electric Retail Service Territories overlap heavily in Arizona. A
single point routinely falls inside a major IOU polygon *and* several
irrigation, water-conservation and electrical-district polygons that also carry
retail electric territory geometry. The dataset does not encode which one
actually serves a given parcel.

Of 255 candidates, **181 sit inside more than one retail territory polygon** and are flagged `AMBIGUOUS` in the CSV. For those rows `serving_utility` is the smallest (most specific) overlapping polygon, which is a reasonable default and is *not* a determination. The `all_overlapping_utilities` column lists every candidate provider — for several top-25 sites that list includes Arizona Public Service, which is very likely the true retail provider even where a small district polygon wins on size.

**Treat `serving_utility` as the first phone call, not as an answer.** One call to the county or to APS/TEP/SRP economic development resolves it definitively.

Federal power marketers (WAPA) and BIA projects were explicitly demoted: they publish enormous territory polygons but are wholesale, not the retail supplier a data center buys from. Leaving them in wrongly labelled 57 candidates 'federal'.

## Utility type across all candidates

| utility_type | candidates | private-land candidates |
|---|---:|---:|
| `municipal` | 116 | 88 |
| `IOU_ACC_regulated` | 68 | 43 |
| `coop` | 38 | 18 |
| `SRP_public` | 15 | 6 |
| `federal_wholesale_overlay` | 10 | 8 |
| `tribal_utility` | 5 | 0 |
| `UNKNOWN` | 3 | 3 |

## Serving utility for the top 25 private candidates

| # | site | county | serving utility (most specific) | type | ACC-regulated | confidence | all overlapping retail territories |
|---:|---|---|---|---|---|---|---|
| 1 | Cholla | NAVAJO | ARIZONA PUBLIC SERVICE CO | `IOU_ACC_regulated` | YES | single | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 2 | Springerville | APACHE | NAVOPACHE ELECTRIC COOP, INC | `coop` | limited | single | NAVOPACHE ELECTRIC COOP, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 3 | Coronado | APACHE | NAVOPACHE ELECTRIC COOP, INC | `coop` | limited | single | NAVOPACHE ELECTRIC COOP, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 4 | PEACOCK | MOHAVE | MOHAVE ELECTRIC COOPERATIVE, INC. | `coop` | limited | single | MOHAVE ELECTRIC COOPERATIVE, INC.; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 5 | NORTH GILA | YUMA | WELLTON-MOHAWK IRR & DRAIN DIST | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION; WELLTON-MOHAWK IRR & DRAIN |
| 6 | Ocotillo | MARICOPA | CITY OF MESA - (AZ) | `municipal` | NO — public power | **AMBIGUOUS** | BUCKEYE WATER C&D DISTRICT; CITY OF MESA - (AZ); ELECTRICAL DIST NO8 MARICOPA; GILA RIVER INDIA |
| 7 | GILA RIVER | MARICOPA | BUCKEYE WATER C&D DISTRICT | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; BUCKEYE WATER C&D DISTRICT; ELECTRICAL DIST NO8 MARICOPA; GILA RIVER |
| 8 | GREENLEE | GREENLEE | DUNCAN VALLEY ELEC COOP, INC | `coop` | limited | **AMBIGUOUS** | DUNCAN VALLEY ELEC COOP, INC; MORENCI WATER AND ELECTRIC |
| 9 | SUGARLOAF | NAVAJO | ARIZONA PUBLIC SERVICE CO | `IOU_ACC_regulated` | YES | single | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 10 | BROWNING | MARICOPA | CITY OF MESA - (AZ) | `municipal` | NO — public power | **AMBIGUOUS** | BUCKEYE WATER C&D DISTRICT; CITY OF MESA - (AZ); ELECTRICAL DIST NO8 MARICOPA; GILA RIVER INDIA |
| 11 | TAP318004 | MOHAVE | UNS ELECTRIC, INC | `IOU_ACC_regulated` | YES | single | UNS ELECTRIC, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 12 | WESTWING | MARICOPA | BUCKEYE WATER C&D DISTRICT | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; BUCKEYE WATER C&D DISTRICT; ELECTRICAL DIST NO8 MARICOPA; GILA RIVER |
| 13 | YUCCA | YUMA | WELLTON-MOHAWK IRR & DRAIN DIST | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION; WELLTON-MOHAWK IRR & DRAIN |
| 14 | TAP318005 | MOHAVE | UNS ELECTRIC, INC | `IOU_ACC_regulated` | YES | single | UNS ELECTRIC, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 15 | CEDAR MOUNTAIN | COCONINO | ARIZONA PUBLIC SERVICE CO | `IOU_ACC_regulated` | YES | single | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 16 | GILA | YUMA | WELLTON-MOHAWK IRR & DRAIN DIST | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION; WELLTON-MOHAWK IRR & DRAIN |
| 17 | HOODOO WASH | YUMA | WELLTON-MOHAWK IRR & DRAIN DIST | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION; WELLTON-MOHAWK IRR & DRAIN |
| 18 | TAP310930 | MOHAVE | UNS ELECTRIC, INC | `IOU_ACC_regulated` | YES | single | UNS ELECTRIC, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 19 | VERDE | YAVAPAI | ARIZONA PUBLIC SERVICE CO | `IOU_ACC_regulated` | YES | single | ARIZONA PUBLIC SERVICE CO; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 20 | MCCONNICO | MOHAVE | UNS ELECTRIC, INC | `IOU_ACC_regulated` | YES | single | UNS ELECTRIC, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |
| 21 | HASSAYAMPA | MARICOPA | BUCKEYE WATER C&D DISTRICT | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; BUCKEYE WATER C&D DISTRICT; ELECTRICAL DIST NO8 MARICOPA; GILA RIVER |
| 22 | HARQUAHALA | MARICOPA | BUCKEYE WATER C&D DISTRICT | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; BUCKEYE WATER C&D DISTRICT; ELECTRICAL DIST NO8 MARICOPA; GILA RIVER |
| 23 | TAP310954 | MARICOPA | BUCKEYE WATER C&D DISTRICT | `municipal` | NO — public power | **AMBIGUOUS** | ARIZONA PUBLIC SERVICE CO; BUCKEYE WATER C&D DISTRICT; ELECTRICAL DIST NO8 MARICOPA; GILA RIVER |
| 24 | CORBELL | MARICOPA | CITY OF MESA - (AZ) | `municipal` | NO — public power | **AMBIGUOUS** | BUCKEYE WATER C&D DISTRICT; CITY OF MESA - (AZ); ELECTRICAL DIST NO8 MARICOPA; GILA RIVER INDIA |
| 25 | GRIFFITH | MOHAVE | UNS ELECTRIC, INC | `IOU_ACC_regulated` | YES | single | UNS ELECTRIC, INC; WAPA-- WESTERN AREA POWER ADMINISTRATION |

## Published contacts

Only what the source dataset actually carries. **No contact name has been invented — a blank is better than a wrong name.** HIFLD publishes a general telephone and website per territory and no economic-development contact at all, so the named-contact column is empty for every row and should be filled by phone.

| utility | type | published phone | published website | economic development / large load contact |
|---|---|---|---|---|
| ARIZONA PUBLIC SERVICE CO | `IOU_ACC_regulated` | NOT AVAILABLE | https://www.aps.com/en/Residential/Home |  |
| NAVOPACHE ELECTRIC COOP, INC | `coop` | NOT AVAILABLE | NOT AVAILABLE |  |
| MOHAVE ELECTRIC COOPERATIVE, INC. | `coop` | NOT AVAILABLE | NOT AVAILABLE |  |
| WELLTON-MOHAWK IRR & DRAIN DIST | `municipal` | NOT AVAILABLE | NOT AVAILABLE |  |
| CITY OF MESA - (AZ) | `municipal` | NOT AVAILABLE | NOT AVAILABLE |  |
| BUCKEYE WATER C&D DISTRICT | `municipal` | NOT AVAILABLE | https://www.bwcdd.com/ |  |
| DUNCAN VALLEY ELEC COOP, INC | `coop` | NOT AVAILABLE | NOT AVAILABLE |  |
| UNS ELECTRIC, INC | `IOU_ACC_regulated` | NOT AVAILABLE | http://www.uns.com/ |  |
| ELECTRICAL DIST NO2 PINAL COUNTY | `municipal` | NOT AVAILABLE | NOT AVAILABLE |  |
| SALT RIVER PROJECT | `SRP_public` | NOT AVAILABLE | NOT AVAILABLE |  |
| USBIA-SAN CARLOS PROJECT | `federal_wholesale_overlay` | NOT AVAILABLE | NOT AVAILABLE |  |
| WAPA-- WESTERN AREA POWER ADMINISTRATION | `federal_wholesale_overlay` | NOT AVAILABLE | NOT AVAILABLE |  |
| DIXIE ESCALANTE R E A, INC | `coop` | (435) 439-5311 | https://www.dixiepower.com |  |
| TUCSON ELECTRIC POWER CO | `IOU_ACC_regulated` | NOT AVAILABLE | http://www.uns.com/ |  |
| SULPHUR SPRINGS VALLEY E C INC | `coop` | NOT AVAILABLE | NOT AVAILABLE |  |
| TRICO ELECTRIC COOPERATIVE INC | `coop` | NOT AVAILABLE | NOT AVAILABLE |  |
| nan | `UNKNOWN` | nan | nan |  |
