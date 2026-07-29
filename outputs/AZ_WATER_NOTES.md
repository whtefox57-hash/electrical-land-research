# AZ WATER NOTES

Generated 2026-07-29 from ADWR and USGS NHD data. Water is treated as a first-class constraint, not a secondary factor, and carries 18.18 of the 100 composite points (20 raw of 110).

## The rubric, applied verbatim

| condition | score |
|---|---:|
| Outside AMA with no cap | 20 |
| In AMA, municipal water service available, no DC-specific cap | 12 |
| In AMA, groundwater only | 6 |
| Explicit groundwater cap, or documented denial of service | 0 |

## The most important caveat on this page

**A score of 20/20 means REGULATORY freedom, not physical water.** Outside an Active Management Area there is no Assured Water Supply requirement and no pumping cap — which is exactly why those areas score highest. It is not evidence that water exists in useful quantity, that an aquifer can sustain a data center, or that anyone will sell it to you. Of the top 25 candidates, **20 are outside any AMA**, and every one of them is carrying that 20 on the absence of regulation rather than on the presence of water.

## AMAs and INAs in Arizona

The brief listed Phoenix, Pinal, Tucson, Prescott and Santa Cruz and asked me to check for Willcox. ADWR's current layer carries **8 AMAs and 3 INAs**. Willcox is present, and so are **Douglas AMA** and **Ranegras Plain AMA**, which were not in the brief's list:

- DOUGLAS AMA
- HARQUAHALA INA
- HUALAPAI VALLEY INA
- JOSEPH CITY INA
- PHOENIX AMA
- PINAL AMA
- PRESCOTT AMA
- RANEGRAS PLAIN AMA
- SANTA CRUZ AMA
- TUCSON AMA
- WILLCOX AMA

## Per-project caps that appear in no zoning code

These were found in development agreements and council coverage, per AZ_POLITICAL_NOTES.md, and are applied as a hard 0/20 wherever they bind:

- **Buckeye** — 2,000 acre-feet/year cap written into the Tract Buckeye Technology Park development agreement (2,069 acres, up to 40 data centers, 1.8 GW at build-out). Buckeye's instrument is contractual, not legislative. Expect to be asked for a hard annual water number early and expect it to become binding.
- **City of Tucson** — refused annexation and city water to Project Blue (Aug 2025), and in May 2026 told it to stop using Tucson Water even for construction. Treated as a documented denial of service.

I searched for other per-project caps and found none I could cite. That is **absence of evidence**: development-agreement caps live in council packets, not in any GIS layer or ordinance database, so this list should be assumed incomplete.

## Water risk distribution across all 255 candidates

| score | candidates | meaning |
|---:|---:|---|
| 20 | 98 | outside AMA, no cap found |
| 12 | 81 | in AMA, community water system service area present |
| 6 | 57 | in AMA, groundwater only |
| 0 | 19 | explicit cap or documented denial |

## Per-candidate water detail — top 25 private

| # | site | county | in AMA | AMA/INA | groundwater basin | municipal water | CWS provider | nearest perennial water (km) | wells within 5 km | water score |
|---:|---|---|---|---|---|---|---|---:|---:|---:|
| 1 | Cholla | NAVAJO | no | JOSEPH CITY INA | JOSEPH CITY INA | no | nan | 19.67 | 688 | 20 |
| 2 | Springerville | APACHE | no | nan | LITTLE COLORADO RIVER PLATEAU | no | nan | 14.06 | 62 | 20 |
| 3 | Coronado | APACHE | no | nan | LITTLE COLORADO RIVER PLATEAU | no | nan | 12.52 | 137 | 20 |
| 4 | PEACOCK | MOHAVE | no | nan | BIG SANDY | no | nan | 14.42 | 26 | 20 |
| 5 | NORTH GILA | YUMA | no | nan | YUMA | no | nan | 2.69 | 324 | 20 |
| 6 | Ocotillo | MARICOPA | yes | PHOENIX AMA | PHOENIX AMA | yes | CITY OF TEMPE WATER MGMT DIV | 5.49 | 1464 | 12 |
| 7 | GILA RIVER | MARICOPA | no | nan | GILA BEND | yes | GILA BEND, TOWN OF | 13.27 | 180 | 20 |
| 8 | GREENLEE | GREENLEE | no | nan | DUNCAN VALLEY | no | nan | 9.45 | 47 | 20 |
| 9 | SUGARLOAF | NAVAJO | no | nan | LITTLE COLORADO RIVER PLATEAU | no | nan | 5.68 | 24 | 20 |
| 10 | BROWNING | MARICOPA | yes | PHOENIX AMA | PHOENIX AMA | yes | CITY OF MESA | 20.07 | 217 | 12 |
| 11 | TAP318004 | MOHAVE | no | nan | SACRAMENTO VALLEY | yes | KINGMAN MUNICIPAL WATER | 40.11 | 394 | 20 |
| 12 | WESTWING | MARICOPA | yes | PHOENIX AMA | PHOENIX AMA | yes | EPCOR  WATER ARIZONA INC- (NE AGUA FRIA ) | 19.57 | 346 | 12 |
| 13 | YUCCA | YUMA | no | nan | YUMA | no | nan | 2.44 | 653 | 20 |
| 14 | TAP318005 | MOHAVE | no | nan | SACRAMENTO VALLEY | yes | VALLEY PIONEERS WC, INC | 36.09 | 71 | 20 |
| 15 | CEDAR MOUNTAIN | COCONINO | no | nan | COCONINO PLATEAU | no | nan | 33.20 | 1 | 20 |
| 16 | GILA | YUMA | no | nan | YUMA | yes | YUMA, CITY OF | 5.21 | 490 | 20 |
| 17 | HOODOO WASH | YUMA | no | nan | LOWER GILA | no | nan | 18.47 | 47 | 20 |
| 18 | TAP310930 | MOHAVE | no | nan | SACRAMENTO VALLEY | yes | KINGMAN MUNICIPAL WATER | 40.37 | 381 | 20 |
| 19 | VERDE | YAVAPAI | no | nan | VERDE RIVER | no | nan | 3.17 | 22 | 20 |
| 20 | MCCONNICO | MOHAVE | no | nan | SACRAMENTO VALLEY | no | nan | 45.83 | 94 | 20 |
| 21 | HASSAYAMPA | MARICOPA | yes | PHOENIX AMA | PHOENIX AMA | no | nan | 10.06 | 418 | 6 |
| 22 | HARQUAHALA | MARICOPA | no | HARQUAHALA INA | HARQUAHALA INA | no | nan | 27.98 | 168 | 20 |
| 23 | TAP310954 | MARICOPA | no | nan | GILA BEND | no | nan | 29.57 | 87 | 20 |
| 24 | CORBELL | MARICOPA | yes | PHOENIX AMA | PHOENIX AMA | yes | TOWN OF GILBERT | 4.79 | 419 | 12 |
| 25 | GRIFFITH | MOHAVE | no | nan | SACRAMENTO VALLEY | no | nan | 42.80 | 34 | 20 |

## What a developer would have to prove

**Inside an AMA** (Phoenix, Pinal, Tucson, Prescott, Santa Cruz, Willcox,
Douglas, Ranegras Plain): a 100-year Assured Water Supply must be demonstrated
before a subdivision plat, and large non-residential users must show physical
availability, continuous availability for 100 years, legal availability,
financial capability and consistency with the AMA management plan and the
state's management goal. In practice that means either a Designation of
Assured Water Supply held by the serving provider, or a project-specific
Certificate.

**Outside an AMA**: no AWS requirement at all. The proof burden shifts from the
regulator to the counterparty — the developer must satisfy its own lenders and
the county, not ADWR. This is why the highest water scores in this screen sit
in Mohave, Yuma, Apache, Navajo and Greenlee counties, and why that score
should be read as "no regulatory obstacle" rather than "water is available".

**In every case**, the specific questions worth asking before a site visit are:
1. Does the serving community water system hold a Designation of Assured Water
   Supply, and what uncommitted volume remains under it?
2. Is there an existing grandfathered groundwater right attached to the parcel,
   and of what type and volume?
3. Has the jurisdiction imposed, or is it negotiating, a per-project cap in a
   development agreement? Buckeye proves this happens where no ordinance exists.
4. What is the depth to water and the recent water-level trend in this
   sub-basin? ADWR publishes both; land subsidence and earth fissure layers are
   also available and were acquired for this screen.
5. Is the cooling design air-cooled or water-cooled? Project Blue switched to
   air-cooled and proceeded after Tucson refused water. That switch is the
   single most effective water-risk mitigation available and it changes the
   conversation with every jurisdiction on this list.
