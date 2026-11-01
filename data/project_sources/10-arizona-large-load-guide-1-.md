# Large-Load Electric Service in Arizona
### A Working Reference for Calls with Utility and County Economic Development Staff

**Compiled:** July 29, 2026
**Jurisdiction:** Arizona (Western Interconnection / WECC — *not* ERCOT)
**Audience assumption:** High legal and commercial literacy, no engineering background
**Companion document:** A separate ERCOT/Texas guide exists. Do not cross-apply. The two states are structurally opposite.

---

## READ THIS BEFORE YOUR FIRST CALL

If you have been reading about ERCOT, unlearn most of it. Four structural facts govern everything in Arizona.

**1. There is no independent system operator, no queue rule, and no interconnection protocol.** Arizona is in the Western Interconnection. WECC is the reliability entity, not a market operator. There is no ERCOT, no Batch Zero, no PGRR, no published allocation process. **There is no state-level rulebook telling a utility how to process your request.** What exists instead is a bilateral commercial negotiation with a single vertically integrated utility, conducted inside a tariff framework the Arizona Corporation Commission approves.

**2. Retail electricity is not deregulated.** One company sells you the electrons, delivers them, and owns the wires. You do not shop for a supplier. This collapses the Texas "TSP vs. REP" distinction entirely — and it means the utility's economic development staff *can* talk to you about price, unlike their Texas counterparts.
Source: <https://nectarclimate.com/rates/tucson-electric-power>

**3. Which utility territory you land in is the single largest variable in the deal.** APS and TEP are investor-owned and ACC-regulated. **SRP is a political subdivision of the state and is not ACC rate-regulated at all** — it is governed by an elected board where voting is weighted by acres owned. Co-ops (Trico, Sulphur Springs Valley, Mohave) are different again. Your legal analysis changes completely across a service-territory line that may not be visible on any map you're looking at.
Source: <https://www.azce.org/srp>

**4. Arizona counties zone. Arizona voters can refer a rezoning to the ballot.** Both are false in Texas and true here, and both have already stopped or nearly stopped Arizona data center projects in the last twelve months. The land use risk in Arizona is not a footnote — it is frequently the binding constraint.

**And the fact that reframes the economics right now:** Arizona's data center transaction privilege tax exemption is **paused**. The Arizona Commerce Authority may not accept new applications from **July 1, 2026 through June 30, 2029**. Developers rushed applications in before the window closed at the end of June. If you are underwriting a new project today, that incentive is not available to you.
Source: <https://www.multistate.us/insider/2026/6/22/state-data-center-policy-shifts-as-governors-impose-new-restrictions>

---

# PART 1 — GLOSSARY

Grouped by function. **Bold-flagged** entries mark the ones where a misuse is an instant tell — and several of the worst tells are ERCOT habits carried across the state line.

## 1.1 The institutions

**⚠️ ACC — Arizona Corporation Commission.** Five commissioners, **elected statewide** to four-year terms, currently an all-Republican majority. Unlike most state utility commissions, the ACC is a **constitutional body with plenary ratemaking authority** — its power comes from the Arizona Constitution, not from a statute the Legislature can amend. This is why the Legislature cannot simply impose large-load rules by statute, a limitation lawmakers openly acknowledge.
*Instant tell:* Calling it "the PUC" or "the Public Utility Commission." It is the Corporation Commission, or "the Commission," or "the ACC." Also: not knowing the commissioners are elected. That fact drives everything about how the body behaves.

**⚠️ APS — Arizona Public Service.** Subsidiary of Pinnacle West Capital Corporation (NYSE: PNW). Serves ~1.4 million customers in 11 of Arizona's 15 counties, including much of metro Phoenix. ACC-regulated. The largest player.

**⚠️ SRP — Salt River Project.** Two entities: the Salt River Valley Water Users' Association (1903, water) and the Salt River Project Agricultural Improvement and Power District (1937, power) — the latter a **political subdivision and taxing subdivision of the State of Arizona**. Serves central Arizona including large parts of Phoenix, Tempe, Mesa, Scottsdale, Chandler, Gilbert.
**SRP is not subject to ACC rate regulation.** Rates, investments, and day-to-day operations do not require ACC approval. SRP is governed by an elected Board (14 directors) and Council, and **voting is acreage-weighted — generally one acre, one vote — except for four at-large board seats elected one-landowner-one-vote.** Only eligible landowners inside SRP boundaries may vote. **SRP is subject to ACC jurisdiction only for siting approval of generation over 100 MW.**
*Instant tell:* Treating SRP like APS. If you tell a county economic development director you'll "take it to the Corporation Commission" for an SRP site, you have revealed you don't know the territory. And the acreage-weighted franchise is not trivia — it is why a large landholder's disposition toward your project matters institutionally, not just socially.

**TEP — Tucson Electric Power.** Investor-owned, ACC-regulated, subsidiary of UNS Energy (owned by Fortis). ~455,000 customers in the greater Tucson area. **UNS Electric / UniSource Energy Services (UNSE)** is the affiliated utility serving Mohave and Santa Cruz counties.

**Cooperatives and municipal utilities.** Trico Electric Cooperative, Sulphur Springs Valley Electric Cooperative, Mohave Electric, Navopache, Arizona G&T Cooperatives (the generation and transmission co-op), plus municipal systems. Distribution co-ops are ACC-regulated in Arizona, but they have their own line extension policies and their own boards. In the Marana project, **Trico is serving the north parcel and TEP the south** — two different utilities on one campus.

**⚠️ WECC — Western Electricity Coordinating Council.** The NERC Regional Entity for the Western Interconnection (14 western states, two Canadian provinces, northern Baja). WECC writes and enforces **reliability standards**. It is not a market operator, does not run studies for you, and does not allocate capacity.
*Instant tell:* Saying "WECC is like ERCOT." It isn't. There is no western equivalent of ERCOT's interconnection authority.

**Balancing Authority (BA).** The entity responsible for balancing load and generation in real time within a defined footprint. APS, SRP, and TEP each operate their own BA. **This is the closest structural analogue to "your grid operator" in Arizona — and it is your utility.**

**WestConnect / SWAT.** WestConnect is the regional transmission planning region covering the desert Southwest under FERC Order 1000. **SWAT — the Southwest Transmission Planning Group** — is the Arizona subregional planning forum. This is where multi-utility transmission gets coordinated, to the extent it does.

**⚠️ Markets+ / EDAM.** The two competing western day-ahead markets. **APS, SRP, TEP, and UniSource have all announced they will join SPP's Markets+**, targeting participation at or shortly after the 2027 launch. CAISO's EDAM is the competing option, and EDF/Aurora analysis argued APS residential customers could have saved substantially more under EDAM. **WEIM** (Western Energy Imbalance Market) is the existing real-time market most of them already participate in.
*In conversation:* Knowing that Arizona chose Markets+ over EDAM, and that it's contested, is a strong signal you follow the region rather than just the state.

**ADWR — Arizona Department of Water Resources.** **ADEQ — Arizona Department of Environmental Quality.** **ACA — Arizona Commerce Authority** (state economic development agency; administers the data center tax program). **RUCO — Residential Utility Consumer Office** (statutory ratepayer advocate; intervenes in rate cases). **AG — Attorney General**, currently Kris Mayes, who is actively litigating against the ACC on large-load contracts.

## 1.2 Measurement vocabulary

**⚠️ kV — kilovolt.** Voltage. In Arizona transmission you'll hear 69 kV, 115 kV, 230 kV, and 500 kV. **Note the difference from Texas: the CEC siting threshold is 115 kV, and 230 kV rather than 345 kV is the common high-voltage tier here.** Using Texas voltage classes ("we'd want to be on a 345") is a small but real tell.

**MW / MVA / power factor.** Same meanings as anywhere. MW is the rate of consumption and the unit that governs tariffs. MVA is apparent power — what equipment is rated for, always ≥ MW. Power factor is the ratio. **Arizona large-load tariffs contain explicit power factor requirements**, so this is a contract term here, not just an engineering concept.

**⚠️ Load factor** — average demand ÷ peak demand. In Arizona this is not just a descriptive statistic; **it is a tariff eligibility criterion.** APS's Rate Schedule XHLF is available to customers with monthly maximum demand of **5,000 kW or more and a load factor of 92% or higher**. Data centers qualify almost by definition.
*Instant tell:* Not knowing that "extra high load factor" is a defined rate class in Arizona rather than a description. If someone says "you'd be XHLF," they are naming a tariff.

**⚠️ Acre-foot (AF).** The unit of Arizona water. One acre-foot ≈ **325,851 gallons** — roughly what two to three Arizona households use in a year, depending on whose convention you use. **Every water conversation in Arizona is denominated in acre-feet per year.** Learn to think in AF/yr, not gallons per day.
*Calibration from real projects:* the Marana campus was represented at roughly **40 AF/yr air-cooled**, against about **2,000 AF/yr** for the agricultural use it replaced. Project Blue near Tucson was discussed at up to **five million gallons per day** (~5,600 AF/yr). The spread between air-cooled and water-cooled is two orders of magnitude, and it is the whole political fight.

## 1.3 The Arizona service and interconnection vocabulary

**⚠️ There is no "interconnection agreement" for load in the ERCOT sense.** What you will actually sign is some combination of: a **line extension agreement**, an **energy supply agreement**, and service under a **rate schedule (tariff)**. If you ask for "the LGIA" or "the interconnection agreement," you'll get a confused pause.

**⚠️ CC&N — Certificate of Convenience and Necessity.** The ACC grant of an exclusive **service territory** to a utility. This determines who serves you. **Do not confuse with CEC.**

**⚠️ CEC — Certificate of Environmental Compatibility.** The ACC approval required to **build** a power plant of **100 MW or more** or an above-ground transmission line designed for **115 kV or higher**. Statutory basis: A.R.S. §§ 40-360 through 40-360.13; rules at A.A.C. R14-3-101 to R14-3-220.
Process: application → referred to the **Arizona Power Plant and Transmission Line Siting Committee** within five days → public hearing with **intervenor status, sworn testimony, and cross-examination** → Committee votes to grant or deny → forwarded to the ACC for a final vote at an open meeting. **The ACC has 180 days from filing to issue the CEC.** Statutory criteria under A.R.S. § 40-360.06 include existing development plans, fish and wildlife, noise, scenic and historic and archaeological sites, and "the total environment of the area."
*Instant tell:* Not knowing the CEC exists. It is the Arizona analogue to a Texas CCN for transmission, it is genuinely adversarial, and it is a real schedule risk if your project requires new high-voltage line. **This is also the single hook that gives the ACC authority over SRP** — SRP needs a CEC for generation over 100 MW even though its rates are unregulated.
Sources: <https://openei.org/wiki/RAPID/Roadmap/8-AZ-a> | <https://azcc.gov/arizona-power-plant/arizona-power-plant> | <https://www.aps.com/en/About/Construction-and-Power-Line-Siting/Power-Line-Siting/CEC-Process>

**⚠️ Advance in aid of construction vs. Contribution in aid of construction.** Both are defined terms in A.A.C. R14-2-201 and govern line extensions under **R14-2-207**:
- **Advance** — funds provided under a line extension agreement **the value of which may be refundable**.
- **Contribution (CIAC)** — funds provided under a line extension agreement or service connection tariff **the value of which is not refundable**.
- **The five-year rule:** if after five years from the utility's receipt of the advance the advance has not been totally refunded, **it converts to a non-refundable contribution.**
- Facilities installed under a line extension are **the sole property of the utility**, regardless of who paid.
*Instant tell:* Using "CIAC" the way Texas people do, as a catch-all for "money I give the utility." In Arizona the refundable/non-refundable distinction is a defined regulatory term with a five-year clock attached, and getting your money characterized as an advance rather than a contribution is worth real money. **This is a lawyer's edge on a call.**
Source: <https://regulations.justia.com/states/arizona/title-14/chapter-2/article-2/r14-2-207/>

**⚠️ ESA — Energy Supply Agreement.** The bespoke, negotiated contract between a utility and a very large customer, filed with and approved by the ACC. This is the central instrument in Arizona large-load practice. The ACC has described its approach as a **"hybrid" of utility-specific extra-high-load-factor tariffs combined with energy supply agreements** — the tariff providing the framework, the ESA providing the project-specific terms.
Typical customer-protection provisions the ACC has itemized: **longer contract terms, minimum-bill terms, power factor requirements, termination provisions, collateral and credit requirements, and direct cost assignment of generation.**
*In conversation:* "Would we be looking at an ESA, or straight tariff service?" is one of the highest-signal questions you can ask in Arizona.
Source: <https://azcc.gov/news/home/2026/04/17/chairman-myers--highlights-from-large-load-users-development-workshop>

**⚠️ XHLF — Extra High Load Factor.** APS Rate Schedule XHLF. Available to customers with **monthly maximum demand ≥ 5,000 kW and load factor ≥ 92%**. Charges are unbundled into basic service, demand (transmission, generation capacity, delivery at secondary/primary/transmission voltage), and energy components. **APS proposed in its June 2025 rate case to change XHLF eligibility criteria and minimum bill requirements and to raise XHLF rates by more than 45%.**

**Minimum bill / minimum billing demand.** A contractual floor: you pay for a stated percentage of contracted capacity whether or not you use it. Standard practice nationally is 80–90% of contracted capacity. This is how the utility de-risks building for you.

**Formula rates.** A mechanism allowing annual rate adjustments without a full rate case. APS requested formula rates in its 2025 filing specifically so that **if extra-large customers cause costs to rise, those costs get assigned to them annually.** The ACC approved a formula-rate policy in 2025.

**Bring-your-own-generation / bring-your-own-capacity / "subscription" model.** Structures where the large customer finances and contracts directly for new generation. APS has floated a subscription model for the data-center-focused second phase of a proposed ~2 GW gas plant, in which large users would cover capital costs in exchange for long-term rates and would absorb the construction and financing risk. The ACC has expressed interest in bring-your-own-capacity programs. **Nothing here is a finalized program — treat it as a live negotiation concept, not a tariff you can elect.**

**Direct cost assignment.** Assigning the cost of specific new generation or transmission to the customer that caused it, rather than rolling it into general rates. The organizing principle of current ACC policy: the ACC's stated position is that "cost causers" should pay all the costs they cause.

## 1.4 The land use vocabulary

**⚠️ Arizona counties have zoning authority.** Boards of Supervisors adopt zoning ordinances and grant rezonings, special use permits, and industrial use permits in unincorporated areas. Planning and Zoning Commissions recommend; **the Board of Supervisors decides.**
*Instant tell:* Assuming the Texas rule (no county zoning). In Arizona this is backwards, and a project in unincorporated Pinal or Pima County goes through a genuine discretionary land use process with public hearings.

**⚠️ Referendum.** Arizona voters can refer a municipal or county rezoning ordinance to the ballot by petition. This is a live, used mechanism — opponents of the Marana data center rezoning gathered **more than 2,800 signatures**. The referendum failed on a technicality: the petitions did not include the **full legal description** of the properties, which Arizona law requires for zoning ordinances, and a Pima County Superior Court judge upheld the town's rejection in **May 2026**.
*Why this matters enormously:* the project survived on a drafting defect in the opposition's petition, not on the merits. Assume the next opposition group will get the legal description right. **Referendum exposure is a real, quantifiable, Arizona-specific closing risk, and it runs after your entitlement.**
Sources: <https://www.tucsonagenda.com/p/no-vote-on-marana-data-centers> | <https://tucson.com/news/local/government-politics/article_760d3cf3-e35b-4821-ac21-dca881e818a4.html>

**Annexation.** Cities can annex adjacent land, bringing it under municipal zoning and municipal water service. **The Tucson City Council voted to block the Project Blue annexation; Pima County then approved the project 3–2.** Annexation is a strategic variable — it can be a path to water service or a path to a hostile council.

**Data center ordinance.** A new and spreading instrument. **Marana adopted one — notably the only such ordinance adopted by a town that had no data centers at the time — and it prohibits the use of potable water for cooling.** That single provision forced the project to be air-cooled. Tucson and Pima County have been drafting their own zoning amendments, with a Data Centers Technical Advisory Committee and an Ad Hoc Committee on Large Quantity Water Users.

## 1.5 The water vocabulary — the part that is genuinely unique to Arizona

**⚠️ Groundwater Management Act of 1980 / A.R.S. Title 45.** The framework. Three tiers of management: statewide general provisions; **Irrigation Non-Expansion Areas (INAs)**; and **Active Management Areas (AMAs)**, the most heavily regulated.

**⚠️ AMA — Active Management Area.** As of early 2026 there are **eight**. The original four (Phoenix, Pinal, Prescott, Tucson) plus Santa Cruz, Douglas, Willcox, and — newly designated in **January 2026** — **Ranegras Plain** in La Paz and Yuma counties, where ADWR found withdrawals exceeding natural recharge by roughly **900 percent** and one well down over 240 feet since the 1980s.
Management goals differ: **safe-yield by 2025** for Phoenix, Prescott, and Tucson; preservation of the agricultural economy for Pinal; maintenance of safe-yield for Santa Cruz.
*Instant tell:* Not knowing whether your site is inside an AMA. It is the first water question, it determines the entire regulatory posture, and AMA boundaries follow **groundwater basins, not county lines.**

**⚠️ Assured Water Supply (AWS) vs. Adequate Water Supply.** The AWS program operates **inside** AMAs; the Adequate program operates **outside**. Both evaluate a **100-year** supply.
**Critical nuance most people get wrong:** the AWS program gates **subdivided land offered for sale or lease** — it is a subdivision and platting requirement. A standalone industrial user like a data center is generally **not** a subdivision and is therefore not gated by AWS in the same way. This is why the phrase "they can't get a Certificate of Assured Water Supply" is often a red herring when applied to a data center.
Related terms: **DAWS** (Designation of Assured Water Supply, held by a water provider — developments inside a designated provider's service area don't need their own determination); **CAWS** (Certificate of Assured Water Supply, held by a subdivider); **CAGRD** (Central Arizona Groundwater Replenishment District — the replenishment mechanism, which by statute serves **member lands** (subdivisions) and **member service areas** (municipal providers), and therefore generally does **not** cover a self-supplying standalone industrial user).
Source: <https://www.azwater.gov/aaws/aaws-overview>

**⚠️ A.R.S. § 45-515 — General Industrial Use Permit.** **This is the instrument by which a self-supplying data center pumps groundwater inside an AMA.** It is one of several groundwater withdrawal permit types (alongside dewatering, mineral extraction, poor-quality groundwater, and others).
The statutory conditions for issuance are restrictive and worth knowing: the applicant must generally show that **uncommitted municipal and industrial CAP water is not available** at the relevant point at or below current M&I CAP rates; that **other surface water or effluent of adequate quality is not available** at a cost not exceeding groundwater cost by more than 25%; and that **irrigation grandfathered rights on nearby land are not available for purchase at a reasonable price or acquirable by eminent domain**, and the applicant does not already hold unused grandfathered rights usable for the purpose.
*In conversation:* "Would we be looking at a 45-515 general industrial use permit, or service from a designated provider?" is the water equivalent of asking about LPC/MPC in Texas. It immediately separates you from people who have only read headlines.
Sources: <https://www.azleg.gov/ars/45/00515.htm> | <https://new.azwater.gov/dictionary/groundwater-withdrawal-permit-0>

**Grandfathered rights.** Three types derived from historic use: **irrigation grandfathered rights** (land irrigated with groundwater 1975–1980, conveyable only with the land), **Type 1 non-irrigation** (capped at three acre-feet per acre per year), and **Type 2 non-irrigation** (usable only for non-irrigation purposes). **Retiring farmland and converting or purchasing the associated rights is the standard Arizona play** for industrial water, and it is why agricultural land with a documented irrigation history is worth more than raw desert.

**Non-exempt vs. exempt wells.** Non-exempt wells have pump capacity greater than **35 gallons per minute** and require a right or permit inside an AMA. Drilling a new non-exempt well in an AMA triggers a **hydrologic impact analysis** by ADWR staff for well spacing and well impact.

**CAP — Central Arizona Project.** The canal delivering Colorado River water to central and southern Arizona. **Colorado River water used by an Arizona data center comes out of Arizona's allocation.** Politically radioactive in the current environment.

**Effluent / reclaimed water.** Non-potable, and increasingly the preferred answer. Marana's structure is instructive: **Marana Water serving office operations only, with Cortaro Marana Irrigation District providing industrial, irrigation, and fire suppression water.**

**Municipal water use ordinances.** Mesa, Avondale, and Phoenix water utilities have adopted ordinances **capping industrial usage and requiring developers to purchase supplemental supplies to exceed the caps.** Mesa reported large water users had provided roughly **7,800 acre-feet** of additional supplies. **This is a fourth regulatory layer beyond ADWR, the AMA, and zoning.**
Source: <https://grist.org/technology/arizona-water-data-centers-semiconducters/>

## 1.6 Air, tax, and other terms

**⚠️ Air permitting is split four ways in Arizona.** **Maricopa County Air Quality Department, Pima County Department of Environmental Quality, and Pinal County Air Quality Control District** each administer Clean Air Act major and minor New Source Review and Part 70 (Title V) permitting **within their counties**. **ADEQ** covers everywhere else except tribal lands. **EPA Region 9** covers most tribal lands, with the Navajo Nation and Gila River Indian Community issuing some permits themselves.
*Instant tell:* Assuming ADEQ is your air permitting agency. In Maricopa, Pima, or Pinal County it is not — it's the county department, and their processes and staff differ.
Source: <https://azdeq.gov/AQComplianceAssistance>

**⚠️ CDC — Computer Data Center program (A.R.S. § 41-1519).** The Arizona Commerce Authority program providing **Transaction Privilege Tax (TPT) and Use Tax exemptions at state, county, and local levels** on qualifying data center equipment. Certification runs **10 years**, or **20 years** for a "Sustainable Redevelopment Project." **Currently suspended — see Part 5.**

**TPT — Transaction Privilege Tax.** Arizona's sales-tax analogue. Technically a tax on the privilege of doing business, levied on the seller, but functionally the sales tax.

**GPLET — Government Property Lease Excise Tax.** A structure in which a municipality takes title to a project and leases it back, substituting an excise tax for property tax. Powerful and politically sensitive; primarily an urban redevelopment tool.

**FTZ — Foreign Trade Zone.** Arizona's distinctive property tax play: property in an activated FTZ is **reclassified**, producing a reduction in state real and personal property taxes commonly cited at up to **72.9%**, and in some cases higher. **This is Arizona's closest analogue to a Texas Chapter 312 abatement, and it is underused by people who don't know about it.**

**Qualified Facility Tax Credit.** Refundable Arizona income tax credits — up to 10% of qualified capital investment, with per-job components, and a maximum credit of $30 million per taxpayer per year. Job thresholds of 25 net new qualifying jobs in urban areas, 5 in rural. Requires pre-approval from the ACA.

---

# PART 2 — THE PROCESS, STEP BY STEP

## 2.1 The honest framing

There is no published, mandatory sequence in Arizona. **What follows is the observed practice, assembled from utility disclosures, ACC filings, and the record of actual projects.** The absence of a codified process is itself the most important process fact: it means timing, terms, and even whether you get studied at all are matters of **utility discretion inside a regulated tariff framework**, subject to ACC review only at the points marked below.

APS and SRP have each **developed their own internal queue processes** for screening prospective data center customers. Those processes are not published rules. **Ask what theirs is. That question alone will distinguish you.**

## 2.2 The table

| # | Step | Who initiates | Who reviews / decides | Document | Cost | Duration | Principal failure mode |
|---|---|---|---|---|---|---|---|
| 0 | Determine service territory | Developer | — | Territory maps; CC&N | Internal | Days | Discovering mid-diligence you're in SRP (no ACC recourse) or split across two utilities |
| 1 | Site control | Developer | — | Deed, lease, option, PSA | Land cost | Weeks–months | Buying before confirming water rights history and transmission adjacency |
| 2 | Utility inquiry / queue entry | Developer | Utility (internal, discretionary) | Utility's own large-customer application | Utility-specific | Weeks | Being placed in the "speculative" bucket — utilities report 8–10 GW of speculative projects |
| 3 | Feasibility / capacity screening | Utility | Utility | Non-binding capacity assessment | Study fee (utility-specific) | 1–6 months | No headroom; nearest adequate transmission far away |
| 4 | Zoning / entitlement | Developer | **County Board of Supervisors** or **City Council** | Rezoning, special use permit, industrial use permit, development agreement | Application fees; consultants; impact fees | **3–12+ months** | Denial; conditions (e.g., no potable water for cooling); **referendum after approval** |
| 5 | Water strategy | Developer | ADWR; municipal provider; irrigation district; **city water ordinance** | § 45-515 permit, provider service agreement, effluent agreement, grandfathered right acquisition | Water rights acquisition; permit costs | **6–24 months** | § 45-515 conditions not satisfiable; provider cap; no non-potable source |
| 6 | Tariff / ESA negotiation | Developer + utility | **ACC** (for APS/TEP/UNSE/co-ops); **SRP Board** (for SRP) | Rate schedule election; **Energy Supply Agreement**; collateral and credit documents | Collateral; credit support | **6–18 months**, plus ACC docket time | Terms unacceptable; ACC approval contested (see AG litigation, Part 7) |
| 7 | Line extension agreement | Developer | Utility (rules per A.A.C. R14-2-207) | Line extension agreement; advance or contribution | **Advance / CIAC — the largest single number** | Months | Cost estimate far above model; characterized as non-refundable contribution rather than refundable advance |
| 8 | Generation / transmission buildout | Utility | **ACC via CEC** if plant ≥100 MW or line ≥115 kV; Siting Committee hearing | CEC application; ten-year transmission plan filing (A.R.S. § 40-360.02, due Jan 31 annually) | Embedded in rates or directly assigned | **180 days statutory for CEC**; construction 2–5+ yrs | CEC intervenors; equipment lead times; ROW acquisition |
| 9 | Air permit | Developer | **County AQ department** (Maricopa/Pima/Pinal) or ADEQ | Minor NSR / Title V for backup generators | Permit fees | Months | Public comment; nonattainment issues in Maricopa |
| 10 | Construction & energization | Developer + utility | Utility; local building official | Building permits; certificate of occupancy; service commencement | — | 18 months–5 yrs | Substation and transformer lead times |
| 11 | Operation | — | Utility; ACC (rate proceedings) | Minimum bill obligations; power factor; term | Demand + energy + adjustors; **formula rate adjustments** | Contract term (often 10–20 yrs) | Minimum bill exposure if ramp slips; formula rate escalation |

Sources: A.A.C. R14-2-207 <https://regulations.justia.com/states/arizona/title-14/chapter-2/article-2/r14-2-207/>; ACC siting <https://azcc.gov/arizona-power-plant/arizona-power-plant>; ACC large load workshop <https://www.azcc.gov/news/home/2026/04/20/acc-large-load-data-center-workshop-highlights>; APS rate case <https://www.aps.com/en/Utility/Regulatory-and-Legal/Rate-case>.

## 2.3 The narrative

**You own a piece of land.** The first question in Arizona is not "how much power" — it is **"whose territory am I in, and what's the water history of this parcel."** Both are threshold questions and both can be answered in an afternoon. Territory determines your entire regulatory path. Water history determines whether you have an asset or a liability: a parcel with a documented 1975–1980 irrigation history carries grandfathered rights that a raw desert parcel does not, and in an AMA that difference is often decisive. The Marana project sits on former agricultural parcels; the Buckeye project sits on land previously zoned for 9,700 homes. **In Arizona, the prior use of the land is part of the water asset.**

**You approach the utility.** One conversation, not two — the same entity handles delivery and supply. You'll be routed to a large-customer or economic development group. They are screening: utilities collectively report roughly **8–10 gigawatts of speculative projects** in their pipelines, and both APS and SRP have built internal processes specifically to sort real from speculative. **Your job on that first call is to be legible as real** — site control, capital, timeline, and a credible answer on water.

**You entitle the site.** This is where Arizona diverges hardest from Texas. If you are in unincorporated county, you need the Board of Supervisors. If you are in a city or town, you need the Council. Either way it is a discretionary land use decision with public hearings, and in the current environment those hearings are crowded. Pima County approved Project Blue 3–2 after Tucson blocked annexation. Marana approved 661 acres unanimously after hours of debate — and then faced a referendum drive and two lawsuits. Pinal County held a lengthy public hearing on the La Osa project in May 2026 and pushed the decision to August 2026.
**And note the ordering problem:** in Arizona your entitlement is subject to referendum *after* it is granted. There is a window where you have a rezoning and do not yet have certainty. Price that.

**You solve water, probably before you solve power.** Inside an AMA you need a lawful source: service from a designated provider, an irrigation district, effluent, purchased or converted grandfathered rights, or a § 45-515 general industrial use permit — and § 45-515 requires you to demonstrate that CAP water, other surface water or effluent, and nearby irrigation grandfathered rights are all unavailable or uneconomic first. Outside an AMA the state permitting burden is far lighter, but you are exposed to whatever the local politics and the aquifer allow, and ADWR has shown it will **designate new AMAs** where declines are severe — Ranegras Plain in January 2026 being the live example. **A site outside an AMA today is not necessarily outside an AMA in five years.**

**You negotiate the tariff and the ESA.** The framework is the extra-high-load-factor rate schedule; the project-specific terms live in the Energy Supply Agreement. Expect: a long term, a minimum bill, power factor requirements, termination provisions, collateral and credit requirements, and direct assignment of the cost of any new generation built for you. For APS and TEP this agreement goes to the ACC. **For SRP it goes to the SRP Board.** Both are public processes; neither is quick.

**The utility builds — and if it needs a big line or a big plant, that goes to the Siting Committee.** A transmission line at 115 kV or above, or a plant at 100 MW or more, requires a Certificate of Environmental Compatibility. That is a contested proceeding with intervenors, sworn testimony, and cross-examination, and the ACC has 180 days from filing. **This is the step most likely to surprise a developer coming from Texas**, where transmission CCNs are comparatively routine.

**You pay for the extension.** Under A.A.C. R14-2-207 you'll advance funds under a line extension agreement. Whether those funds are a **refundable advance** or a **non-refundable contribution** is a negotiated and tariff-driven question — and if an advance isn't fully refunded within **five years**, it converts to a non-refundable contribution by rule. Either way, **the facilities are the utility's property.**

**You operate under a minimum bill.** The commercial architecture is designed so the utility is made whole regardless of whether you ramp on schedule. That is the point of the minimum bill and the collateral, and it means **your ramp risk is your risk, contractually, in a way that is more explicit here than in a queue-based market.**

---

# PART 3 — THE THRESHOLDS

Arizona has **no statutory 75 MW threshold.** There is no equivalent of Texas PURA § 37.0561. The thresholds that actually matter are tariff thresholds, siting thresholds, and water thresholds — and they are scattered across different bodies of law.

| Threshold | What it triggers | Source |
|---|---|---|
| **5,000 kW (5 MW) + 92% load factor** | Eligibility for APS Rate Schedule **XHLF**. **APS proposed changing these eligibility criteria and the minimum bill in its 2025 rate case** — verify current status | APS Rate Schedule XHLF; APS 2025 rate case testimony |
| **35 gallons per minute** | Well is **non-exempt** — requires a groundwater right or permit inside an AMA, and triggers a hydrologic impact analysis for a new well | A.R.S. Title 45; ADWR |
| **100 MW** | Power plant requires a **CEC** from the ACC via the Siting Committee. **This is also the only ACC jurisdictional hook over SRP** | A.R.S. §§ 40-360 et seq. |
| **115 kV** | Above-ground transmission line requires a **CEC** | A.R.S. § 40-360(10), § 40-360.03 |
| **Inside vs. outside an AMA** | Determines whether the full groundwater permitting regime applies. Not a MW threshold, but the most consequential binary in an Arizona site analysis | A.R.S. Title 45 |
| **$25M–$50M capital investment** (location-dependent), some categories $200M | Historic CDC program eligibility thresholds — **academic while the moratorium runs** | A.R.S. § 41-1519 |
| **25 jobs urban / 5 jobs rural** | Qualified Facility Tax Credit thresholds | ACA |

**What this means practically.** In Texas, 75 MW is a bright line that changes your legal universe. In Arizona there is no such line — **the "large load" category is defined by tariff and by utility practice, not by statute.** A 60 MW project and a 600 MW project follow the same *process*; they differ in negotiating leverage, in whether new generation is required, and in how much political attention they attract.

**The corollary is that phasing works differently here.** In ERCOT, aggregation rules at a single site behind common points of interconnection are designed to defeat structuring around the threshold. In Arizona there is no threshold to structure around — but there is also no protection: a utility can decline to serve on your timeline at any size if it doesn't have capacity, and you have no protocol to point to. **Your leverage is commercial and political, not procedural.**

**One genuine open question worth raising on calls:** whether the ACC will adopt a generally applicable large-load rule or threshold. Docket **E-00000A-25-0069** was opened by Commissioner Kevin Thompson in 2025 and the Commission held its first workshop on **April 16, 2026**. Commissioners have described the current approach as a deliberate "hybrid" of tariffs plus ESAs rather than a codified rule. **As of July 29, 2026 I found no adopted generic large-load rule.** Ask whether one is coming.

---

# PART 4 — WHO DECIDES WHAT

| Actor | Controls | Does NOT control | Timeline | How influenced |
|---|---|---|---|---|
| **ACC** | Rates and tariffs for APS/TEP/UNSE/co-ops; approval of **Energy Supply Agreements**; **CEC** siting for plants ≥100 MW and lines ≥115 kV; CC&N service territories; formula rate policy; biennial transmission assessment | **SRP's rates** (only SRP siting ≥100 MW); does not run interconnection studies; does not zone; does not permit water | Rate cases ~12–18 months; **CEC statutory 180 days**; ESA dockets months | **Five elected commissioners.** Formal intervention, docketed comments, open meetings. RUCO and the AG intervene routinely. This is a political body and behaves like one |
| **APS / TEP / UNSE** | Whether and when to serve; internal queue and screening; capacity assessment; line extension terms; ESA terms; construction schedule | Cannot set rates without ACC approval; cannot exceed ACC-approved tariffs; cannot zone or permit water | Screening months; buildout years | **Commercially.** They earn a return on capital deployed for you. APS reported ~7.5% sales growth in Q1 2026 driven by large-load additions — they want the load, on their terms |
| **SRP** | Everything APS controls, **plus its own rates and its own capital plan, without ACC review** | Needs ACC **CEC** for generation ≥100 MW | Board decisions on its own calendar | **Elected Board and Council, acreage-weighted voting** (one acre ≈ one vote; four at-large seats one-landowner-one-vote). A fundamentally different influence map — landholding is enfranchisement |
| **County Board of Supervisors** | **Zoning, rezoning, special use permits, industrial use permits** in unincorporated areas; plats; road agreements; county share of incentives; **county air quality permitting in Maricopa, Pima, Pinal** | Cannot set electric rates; cannot permit groundwater | P&Z twice monthly; rezoning 3–12 months | Elected. Public hearings are genuinely contested. Pima approved Project Blue 3–2; Pinal deferred La Osa from May to **August 26, 2026** |
| **City / Town Council** | Zoning inside limits; annexation; building permits; **municipal water service and water use ordinances**; data center ordinances; development agreements; impact fees | Cannot set electric rates (unless a municipal utility) | Council twice monthly; rezoning 2–6 months | Elected. **Tucson blocked Project Blue's annexation. Marana's ordinance banned potable water for cooling.** Councils are currently the most active regulators of data centers in Arizona |
| **Arizona voters (referendum)** | **Can refer a rezoning ordinance to the ballot by petition** | Nothing else in this chain | Petition window post-adoption; election cycle | Signature gathering. Marana: 2,800+ signatures, defeated on legal-description defect, upheld by Pima County Superior Court May 2026 |
| **ADWR** | AMA designation; groundwater withdrawal permits including **§ 45-515 general industrial use**; well spacing and impact analysis; AWS/Adequate determinations; grandfathered right administration | Does not regulate water quality (that's ADEQ); does not zone | AMA designations: multi-month formal process; permits months | Technical and administrative. **Director Tom Buschatzke.** ADWR designated Ranegras Plain AMA in January 2026 — this agency is actively expanding its footprint |
| **Municipal / irrigation district water provider** | Whether to serve you, at what volume, under what conditions; caps and supplemental supply requirements | — | Negotiated | Commercial and political. Mesa, Avondale, Phoenix have industrial usage caps requiring purchased supplemental supplies |
| **Maricopa / Pima / Pinal County AQ; ADEQ elsewhere** | Air permits for backup generators — minor NSR, Title V | Does not regulate noise, light, water use, or electrical infrastructure | Months; **public notice and comment on minor source permits** | Formal permit process. Note EPA has proposed eliminating the federal 30-day public notice requirement for minor source permits; ADEQ said in July 2026 it is evaluating |
| **Arizona Commerce Authority** | CDC certification, Qualified Facility pre-approval, FTZ coordination | Cannot grant local property tax relief | 60 days for CDC certification decision — **but not accepting CDC applications July 1, 2026–June 30, 2029** | Documentary |
| **Governor** | Executive orders (e.g., E.O. 2025-13 streamlining energy infrastructure on state trust lands); **veto**; budget negotiation; task forces | No direct authority over ACC ratemaking; no direct authority over local zoning | — | **Gov. Hobbs (D) sought full repeal of the data center tax exemption and got a 3-year pause. She vetoed H.B. 2774 (2025), which would have exempted co-located SMRs from environmental compatibility review and local zoning.** She is on the November 2026 ballot |
| **Attorney General** | Litigation. **Currently suing the ACC** over the TEP/Project Blue ESA | Cannot set rates | Litigation timelines | **AG Mayes filed three rehearing requests in ACC matters in March 2026 alone, plus a Maricopa County Superior Court suit, and is intervening in both the APS and TEP rate cases** |
| **Arizona State Land Department** | State trust land — a substantial share of Arizona acreage; leases and sales must serve trust beneficiaries | — | Auction and lease processes | E.O. 2025-13 directed streamlining for energy infrastructure |
| **Tribal nations** | Sovereign authority on tribal lands. **EPA Region 9 issues most air permits there**; Navajo Nation and Gila River Indian Community issue some themselves | — | Sovereign processes | Government-to-government. Entirely outside the state framework |

## 4.1 The four structural insights

**First: the ACC is elected, and that changes its behavior.** A commission facing voters responds to residential bill politics in a way an appointed body does not. The current commissioners have been publicly pro-data-center while simultaneously emphasizing ratepayer protection — Chairman Myers framing it as "Arizona remains a preferred location... while our regulatory policies continue to protect other ratepayers." Read that as a stable but conditional posture: **support continues as long as the cost-causer principle visibly holds.**

**Second: SRP is a different country.** No ACC rate review. An elected board with acreage-weighted voting. ACC jurisdiction only for generation siting over 100 MW. If your site is in SRP territory, your regulatory strategy, your escalation path, and your political map are all different — and the AG, RUCO, and the ACC intervention machinery are largely unavailable to your opponents *and* to you.

**Third: local government is the real gatekeeper, and it is currently mobilized.** In Texas the county is mostly a cheerleader with no zoning power. In Arizona the county and city hold genuine veto points, and 2025–2026 produced organized opposition in Tucson, Chandler, Marana, Pima County, and Pinal County. Data centers were mentioned in at least **84 legislative hearings, caucus meetings, and floor sessions** between January and June 2026, and more than **50 energy bills** were introduced. **A county economic development director's read on their own Board of Supervisors is the most valuable thing they can give you.**

**Fourth: the legal architecture of the ESA is itself under challenge.** The AG's position is that by approving an agreement permitting a utility and a customer to adjust a rate schedule between themselves, the ACC **delegated its constitutional ratemaking authority to private parties** — something the Arizona Constitution and Supreme Court prohibit. TEP's position is that no deviation from Commission-approved tariffs is permitted without ACC authorization and any future rate change goes through a public ACC process. **This is not a peripheral dispute. It goes to whether the central contracting instrument in Arizona large-load practice is lawful as structured.** For a law student, this is the most interesting thing happening in the state.

---

# PART 5 — ECONOMICS

## 5.1 What you pay

**Study and application fees.** Utility-specific and not published as state rules. Ask directly.

**Line extension: advance or contribution.** Governed by A.A.C. R14-2-207 and each utility's line extension tariff. The negotiating objective is to have as much as possible characterized as a **refundable advance in aid of construction** rather than a non-refundable **contribution**. Watch the **five-year conversion rule**: an advance not fully refunded within five years of the utility's receipt becomes a non-refundable contribution by operation of the rule. Facilities are the utility's property regardless.

**Collateral and credit support.** The ACC has itemized collateral and credit requirements as standard customer-protection provisions in large-load tariffs and ESAs. APS explicitly lists "minimum bill and collateral requirements" among its tools. Expect letters of credit or parent guaranties sized to the utility's exposure.

**Minimum bill.** The most important recurring commercial term. You pay for a floor percentage of contracted capacity regardless of consumption. **This converts your construction and ramp risk into a fixed obligation.** If your building is late, you pay anyway.

**Rates.** Under XHLF the charge stack is unbundled into basic service, demand components (transmission, generation capacity, and delivery at secondary, primary, or transmission voltage), and energy components (fuel and system benefits), plus adjustors. **Taking service at transmission voltage carries a dramatically lower delivery demand charge than primary or secondary** — in the current published XHLF schedule the difference between transmission-level and secondary-level delivery demand charges is more than an order of magnitude. That is a design decision worth modeling early.

**Direct assignment of new generation.** Where new generation must be built for you, the ACC's stated policy direction is direct assignment rather than socialization. APS's 2025 rate case explicitly proposed "rate changes to support directly assigning the costs associated with new and incremental generation (production demand and energy)."

**Formula rates.** APS requested annual formula rate adjustments so that costs caused by extra-large customers get assigned to them yearly without a full rate case. **From your side, this is an escalator with no negotiated cap.** Model it.

## 5.2 The pending rate cases — do not underwrite off current tariffs

**APS.** Filed June 2025. Requested revenue increase of approximately **$662 million (~16%)**, roughly 14–15% for residential (about **$20/month** on a typical 1,000 kWh bill), and **more than 45% for extra-large energy users like data centers.** Includes the formula rate mechanism and changes to XHLF eligibility and minimum bill requirements. **Public hearings before the ACC began May 18, 2026. A final decision is expected before the end of 2026.**
Sources: <https://www.aps.com/en/Utility/Regulatory-and-Legal/Rate-case> | <https://cryptobriefing.com/arizona-aps-rate-hike-data-centers/>

**TEP.** Docket 25-0103. Requested roughly **13–14%** revenue increase, about **$16/month** for a median residential customer. Evidentiary hearing before the ALJ began **April 22, 2026**, running roughly three weeks; **closing arguments due July 2026**; TEP requested new rates effective **September 2026**. The Attorney General's office suggested 4% would be appropriate. TEP's filing attributes pressure to "high power users" including data centers, manufacturing, and mines.
Sources: <https://azluminaria.org/2026/05/25/tep-rate-case-what-tucson-customers-need-to-know/> | <https://azcc.gov/news/home/2026/02/17/tep-rate-case-timeline-update>

**The practical implication:** the tariff you would sign under today is not the tariff you will operate under. **Both major IOU rate structures are mid-flight, and the large-load class is where the increases are concentrated.** Any pro forma built on published current XHLF rates is already wrong.

## 5.3 The tax layer — and the thing that changed last month

**⚠️ The CDC / TPT exemption is suspended.** The FY2027 state budget (**HB 4168 / SB 1861**, signed by Governor Hobbs in June 2026) imposes a **three-year moratorium prohibiting the Arizona Commerce Authority from accepting applications for the data center sales tax exemption from July 1, 2026 through June 30, 2029.**

Background you should carry: the program dates to **2013** (Hobbs voted for it as a state senator), was renewed for ten years in **2021**, and was previously authorized to accept applications through **December 31, 2033**. It provides TPT and use tax exemptions at state, county, and local levels on qualifying equipment, for **10 years**, or **20 years** for a Sustainable Redevelopment Project. The Arizona Department of Revenue estimates the exemption costs roughly **$38 million per year** in foregone revenue.

Governor Hobbs sought **full repeal**; Republicans opposed; the moratorium was the compromise, **set to lift in 2029 if the incentives aren't eliminated in a future session.** Developers filed a rush of applications before the June 30 cutoff. The Data Center Coalition's state policy VP said publicly that the outcome would make operators "question Arizona's long-term commitment to the program."

**How to hold this on a call:** do not say the exemption is "gone" — say applications are **paused through June 30, 2029**, and that projects certified before July 1, 2026 retain their certifications. Then ask what the county or city can do instead.
Sources: <https://www.multistate.us/insider/2026/6/22/state-data-center-policy-shifts-as-governors-impose-new-restrictions> | <https://azcapitoltimes.com/news/2026/07/09/data-centers-dominated-2026-session-lawmakers-answered-with-3-year-tax-incentive-pause/> | <https://www.azcommerce.com/incentives/computer-data-center-program/>

**What remains available:**

| Tool | What it does | Who grants it |
|---|---|---|
| **Foreign Trade Zone reclassification** | Property tax reduction commonly cited at up to **72.9%** on state real and personal property taxes; in some cases higher | FTZ grantee + ACA coordination + local |
| **GPLET** | Municipality takes title and leases back; excise tax substitutes for property tax | City council |
| **Qualified Facility Tax Credit** | Refundable income tax credits up to 10% of qualified capital investment, per-job components, $30M/taxpayer/year cap; 25 urban / 5 rural job thresholds | ACA (pre-approval required) |
| **Quality Jobs Tax Credit** | Per-job income tax credits | ACA |
| **Local development agreements / impact fee treatment** | Negotiated; Marana's project generated nearly $1M in one-time impact fees | City or county |

**Note the structural contrast with Texas.** Texas offers Chapter 312 abatements from cities, counties, and special districts (school districts statutorily excluded) and excludes data centers from JETI by NAICS code. **Arizona has no direct Chapter 312 analogue** — its property tax play is the FTZ reclassification, which is a different mechanism with different administration and which most Texas-trained developers have never encountered. Raising FTZ by name on an Arizona call is a strong signal.

## 5.4 Curtailment, flexibility, and what they're worth

**There is no Arizona equivalent of SB 6's mandatory curtailment regime.** No statutory firm-load-shed equipment requirement, no LPC/MPC construct, no PCLR. Flexibility in Arizona is **contractual**, negotiated into the ESA, and priced bilaterally.

What exists instead:
- **Bring-your-own-capacity / subscription structures**, in which the large customer finances new generation and takes construction and financing risk in exchange for long-term rates and faster service. APS has described a subscription model for a data-center-focused phase of a proposed ~2 GW gas plant, likely in the **2031–2033** window. The ACC has expressed interest. **None of this is a filed, electable program yet.**
- **Interruptible or curtailable provisions** negotiated into individual ESAs.
- **The Arizona Energy Promise Task Force** (36 members, April 2026 report, 31 policy recommendations) made recommendations on bring-your-own-capacity, tax incentives, and energy efficiency — while noting that implementation is "solely within the jurisdiction of the relevant ratemaking body."

**The valuation consequence.** In ERCOT, flexibility buys you a defined quantity of additional MW under a published protocol. **In Arizona, flexibility buys you negotiating position and speed.** That is genuinely less legible to a lender — there is no protocol document to point at — but it is also more tractable, because it is a contract you can negotiate rather than a rule you must accept.

## 5.5 Where money is made and lost

**Made:**
- **Territory arbitrage.** APS, SRP, TEP, and the co-ops have different capacity positions, different governance, different rate structures, and different politics. The same site logic produces different answers across a territory line.
- **Water history.** A parcel with documented 1975–1980 irrigation history carries grandfathered rights. Retiring farmland is the standard Arizona water play, and buying the water with the dirt is where the value is.
- **Air-cooled design.** Marana: ~40 AF/yr air-cooled versus ~2,000 AF/yr for the prior agricultural use, and a claimed 95% reduction. **Air cooling is not just an ESG position in Arizona — it is the thing that makes entitlement politically possible.** Marana's ordinance made it mandatory.
- **Transmission-voltage service.** The delivery demand charge differential between transmission and secondary service under XHLF is very large.
- **FTZ and GPLET structuring**, now that the state TPT exemption is paused.
- **Being genuinely early on Batch-1-equivalent capacity.** APS reports ~4.5 GW committed and ~20 GW uncommitted. **The committed tier is the real market.**

**Lost:**
- **Entitlement failure or referendum.** The Arizona-specific risk with no Texas analogue.
- **Water discovered late.** Water permitting timelines in Arizona routinely rival or exceed electrical timelines. Discovering at month nine that your site needs a § 45-515 permit whose statutory conditions you cannot satisfy is a project-killer.
- **Minimum bill against a slipped ramp.** You pay for capacity you can't use.
- **Formula rate escalation.** An uncapped annual adjustment mechanism aimed specifically at your rate class.
- **CEC delay.** 180 statutory days plus a contested hearing, if new high-voltage line is required.
- **Assuming the tax exemption.** It is paused until June 30, 2029.
- **Political risk.** Hobbs is on the November 2026 ballot; the 2027 session is expected to revisit water use and cost allocation; Democratic leaders have named both as priorities.

---

# PART 6 — THE CONVERSATION LAYER

## 6.1 Twenty questions that mark you as a participant

**Threshold and territory**

**1. "Whose territory is this parcel in — and does the transmission and the distribution come from the same entity?"**
*Why:* Names the first-order variable and anticipates split-service situations like Marana, where Trico serves one parcel and TEP the other. *Reveals:* Whether you have one counterparty or two.

**2. "If we're in SRP, what does the approval path look like — is this a Board matter, and on what cadence?"**
*Why:* Demonstrates you know SRP isn't ACC-regulated. *Reveals:* The real timeline and the real decision-maker.

**3. "What's your internal screening process for large-load requests, and what moves a project from speculative to committed in your queue?"**
*Why:* APS and SRP have each built internal queue processes and have reported 8–10 GW of speculative projects collectively. Asking about *their* process, by name, shows you know there isn't a state one. *Reveals:* Exactly what they need from you.

**4. "What's the nearest adequate transmission, at what voltage, and would serving us require any new 115 kV-or-above line?"**
*Why:* Ties the engineering question directly to the CEC trigger. *Reveals:* Whether you're facing a Siting Committee proceeding.

**5. "If a CEC is required, what's your read on the intervenor landscape in that corridor?"**
*Why:* Treats the CEC as the contested proceeding it is. *Reveals:* Schedule risk nobody volunteers.

**Commercial structure**

**6. "Would we be on XHLF, or are we looking at an ESA — or both?"**
*Why:* Uses the ACC's own "hybrid" framing. *Reveals:* Whether your project is standard-tariff-sized or bespoke.

**7. "Given APS proposed changing XHLF eligibility and minimum bill in the rate case, what do you expect the post-decision tariff to look like?"**
*Why:* Shows you know the tariff is mid-flight and a decision is expected before year-end 2026. *Reveals:* Their internal read on the rate case.

**8. "How is the minimum billing demand typically set as a percentage of contracted capacity, and is there any ramp accommodation in the first years?"**
*Why:* Names the term that governs your downside. *Reveals:* Real negotiating room.

**9. "On the line extension — how much of that would be a refundable advance versus a non-refundable contribution under your R14-2-207 tariff?"**
*Why:* Cites the rule and uses the defined terms correctly. **This is the highest-leverage technical question on this list**, because it's real money and most developers don't know the distinction exists. *Reveals:* Whether there's structuring room.

**10. "What collateral and credit support would you expect, and would a parent guaranty work or do you need an LC?"**
*Why:* Anticipates a standard ACC-itemized protection. *Reveals:* The capital timing.

**11. "If new generation is required for us, are you thinking direct assignment, or is there a subscription or bring-your-own-capacity structure in play?"**
*Why:* Uses the ACC's and APS's own vocabulary for the live concept. *Reveals:* Whether the utility is genuinely ready to do this or is still conceptual.

**12. "How would formula rates apply to our class, and is there any mechanism to cap or predict the annual adjustment?"**
*Why:* Identifies the escalator aimed at you. *Reveals:* Whether anyone has thought about the customer side of formula rates.

**Water**

**13. "Is this parcel inside an AMA, and if so, which one?"**
*Why:* The first water question, and the one that determines everything after. *Reveals:* Whether they know their own geography — many county staff will, some won't.

**14. "Does the parcel have irrigation grandfathered rights from the 1975–1980 period, and are they conveyable with the land?"**
*Why:* Names the actual mechanism by which Arizona industrial water gets assembled. *Reveals:* Whether the land is a water asset or a water liability.

**15. "Would we be looking at service from a designated provider, an irrigation district, effluent, or a 45-515 general industrial use permit?"**
*Why:* Lays out the four real options by name. **This question, more than any other, signals that you have done Arizona homework rather than generic data center homework.** *Reveals:* The realistic water path and its timeline.

**16. "Does the serving municipality have an industrial water use cap or a supplemental supply requirement?"**
*Why:* Mesa, Avondale, and Phoenix all do. *Reveals:* A fourth regulatory layer most people miss.

**Land use and politics**

**17. "Is this parcel in the county or in a city or town — and if county, what's the Board of Supervisors' recent record on projects like this?"**
*Why:* Correctly assumes counties zone, and asks for the political read that is the county EDC's real product. *Reveals:* Whether you're walking into a La Osa situation.

**18. "Does the jurisdiction have a data center ordinance, and does it restrict potable water for cooling?"**
*Why:* Marana's does, and it dictated the entire cooling design. *Reveals:* A design constraint you need before you draw anything.

**19. "What's the referendum exposure on a rezoning here, and how long is the window after Council or Board action?"**
*Why:* Names the Arizona-specific post-entitlement risk. Marana survived one on a legal-description defect. *Reveals:* Whether local counsel has thought about petition-proofing.

**20. "With the CDC exemption paused until mid-2029, what's actually available locally — FTZ reclassification, a GPLET, a development agreement?"**
*Why:* States the moratorium accurately with its end date, then pivots to what's left. *Reveals:* Whether the jurisdiction has real tools or just enthusiasm.

## 6.2 Ten questions that mark you as inexperienced

| Don't ask | Why it lands badly | Ask instead |
|---|---|---|
| **1.** "Which retail provider would we use?" | Arizona is not deregulated. One utility does supply and delivery. | "Would service be under standard tariff or an ESA, and what's the all-in delivered cost structure?" |
| **2.** "What's the ISO interconnection queue look like?" | There is no ISO and no state queue. Instant tell that you came from ERCOT or PJM and didn't adjust. | "What's *your* internal large-load queue process, and where would we sit in it?" |
| **3.** "Can we get an interconnection agreement / LGIA?" | Not the instrument. Load service in Arizona runs on a line extension agreement plus a rate schedule plus, at scale, an ESA. | "What documents would we actually sign — line extension, ESA, service agreement?" |
| **4.** "When does the PUC approve this?" | It's the **Corporation Commission**, it's constitutional, its members are elected — and for SRP it has no rate jurisdiction at all. | "Does this need to go to the Commission, or is it a Board matter?" |
| **5.** "Do we need a CC&N?" | A CC&N is the *utility's* service territory certificate. You never get one. You may need the utility to get a **CEC**. | "Would serving us require a CEC — new plant over 100 MW or line at 115 kV or above?" |
| **6.** "What's the county zoning process — oh wait, counties don't zone, right?" | They do. This is the Texas rule and it is wrong here. | "Is this parcel zoned for our use, or do we need a rezoning or industrial use permit from the Board of Supervisors?" |
| **7.** "We'll just get a Certificate of Assured Water Supply." | AWS gates **subdivided land offered for sale or lease**. A standalone industrial user generally isn't a subdivision and the CAWS path may not even apply. | "Are we inside an AMA, and is the path a designated provider, an irrigation district, effluent, or a 45-515 permit?" |
| **8.** "We'll pump our own groundwater — it's our land." | Inside an AMA you need a right or permit, non-exempt wells over 35 gpm trigger a hydrologic impact analysis, and § 45-515 requires you to show CAP water, surface water, effluent, and nearby grandfathered rights are all unavailable or uneconomic first. | "What's the realistic path to a 45-515 permit here, and has ADWR issued any in this sub-basin recently?" |
| **9.** "ADEQ handles our air permit for the generators, right?" | Not in Maricopa, Pima, or Pinal County — those counties run their own delegated programs. Not on tribal land — that's EPA Region 9. | "Who's our air permitting authority here, and what's the current posture on minor source permits for backup generation?" |
| **10.** "Is the data center sales tax exemption still available?" | Applications are suspended July 1, 2026–June 30, 2029. Asking as if nothing happened signals you haven't read anything from the last two months. | "With CDC applications paused through mid-2029, what does the local incentive package look like — FTZ, GPLET, development agreement?" |

**One meta-note on tone.** Arizona utility and county staff are, right now, fielding a great deal of hostile public attention. Volunteering your own constraints early — cooling technology, water target in acre-feet per year, capital timing — reads as good faith and gets you further than vocabulary. **The single most credibility-building thing you can say on an Arizona call is a specific, low number of acre-feet per year.**

---

# PART 7 — CURRENT STATE, MID-2026

*Date-stamped. This section will stale first.*

## 7.1 The numbers

| Figure | Date | Source |
|---|---|---|
| **APS: ~4.5 GW committed large-load in queue; ~20 GW uncommitted** | Q1–Q2 2026 | Pinnacle West / newsdata |
| **APS: ~30 data centers in queue requesting a combined ~18 GW** | June 2026 | Datacenterdynamics |
| **APS: expects large-customer peak demand ~13.1 GW in 2026** | April 2026 (ACC workshop) | <https://www.azcc.gov/news/home/2026/04/20/acc-large-load-data-center-workshop-highlights> |
| APS: contractually committed to serve **4.7 GW** new large-customer load over the next decade, ~2/3 data centers | August 2025 | Power Engineering |
| APS record peak demand: **~8.5 GW** | 2025 | Power Engineering |
| APS: data centers ~**5%** of total peak demand in 2025 | 2025 | APS |
| APS Q1 2026 sales growth: **~7.5%**, driven by large-load additions | Q1 2026 | newsdata |
| **SRP: 59 large-load customers, ~7,000 MW combined** | April 2026 (ACC workshop) | ACC |
| SRP: ~20 data centers of varying sizes | April 2026 | The Center Square |
| **TEP/UNSE: one data center under contract at ~286 MW forecast; other prospective projects ~800 MW** | April 2026 | ACC |
| **All utilities: ~8–10 GW of speculative projects in queue** | April 2026 | ACC |
| **If every proposed APS and SRP data center advances: ~29,000 MW** — roughly tripling those two utilities' demand | April 2026 (Arizona Energy Promise Task Force) | Governor's Office task force report |
| Arizona: ~**98** data centers operating, **86** planned or under construction; **7th** nationally | July 2026 (Hobbs, citing Pew) | Arizona Capitol Times |
| CDC exemption cost: ~**$38 million/year** foregone revenue | 2026 | Arizona Dept. of Revenue |

**Read the ratio.** APS alone: ~4.5 GW committed against ~20 GW uncommitted and ~18 GW of data center requests. As in Texas, **the queue is a wish list, not a pipeline** — but unlike Texas, Arizona has no state-mandated financial security regime forcing it to reveal itself. The sorting is happening through utility discretion and commercial terms instead.

## 7.2 Timeline of the last twelve months

| Date | Event |
|---|---|
| **June 2025** | APS files rate case: ~$662M / ~16% revenue increase, **45%+ for XHLF**, formula rate mechanism, XHLF eligibility and minimum bill changes |
| **June 2025** | TEP files rate case (Docket 25-0103), ~13–14% |
| **August 2025** | APS, SRP announce Transwestern Desert Southwest pipeline capacity agreements; APS anchor customer. TEP, UniSource, City of Mesa in negotiation |
| **September 2025** | Gov. Hobbs E.O. 2025-13 — streamline energy infrastructure on state trust lands |
| **2025** | Commissioner Kevin Thompson opens ACC large-load docket **E-00000A-25-0069** |
| **Fall 2025** | Tucson City Council blocks Project Blue annexation; **Pima County approves 3–2** |
| **December 2025** | ACC approves TEP/Humphrey's Peak Power (Project Blue) **Energy Supply Agreement 4–1** (Docket E-01933A-25-0187) |
| **January 6, 2026** | **Marana Town Council unanimously rezones 661 acres** for Beale Infrastructure data center campus; Marana ordinance bars potable water for cooling; project proposed air-cooled at ~40 AF/yr |
| **January 12–14, 2026** | ADWR designates **Ranegras Plain AMA** — Arizona's 8th. Hobbs announces push for data center fees to fund Colorado River conservation ($30M seed) |
| **January 20–21, 2026** | ACC denies AG Mayes's rehearing request on the TEP ESA (automatic denial, 20-day statutory period) |
| **February 19, 2026** | **AG Mayes files suit in Maricopa County Superior Court** challenging the ACC's ESA approval as an unconstitutional delegation of ratemaking authority |
| **February–March 2026** | Referendum drive against Marana rezoning: 2,800+ signatures; town clerk rejects for lack of full legal description; group withdraws petitions |
| **March 2026** | AG Mayes files **three rehearing requests in three separate ACC matters in one month**; intervenes in APS and TEP rate cases |
| **April 2026** | **Arizona Energy Promise Task Force** report — 36 members, 31 recommendations, the 29,000 MW figure |
| **April 16, 2026** | **ACC Large Load Users Development Workshop** — Staff, RUCO, Data Center Coalition, IPPs, Goldwater Institute, TEP, SRP, APS |
| **April 22, 2026** | TEP rate case evidentiary hearing begins before the ALJ (~3 weeks) |
| **May 2026** | Pima County Superior Court upholds Marana's rejection of the referendum petitions |
| **May 18, 2026** | **APS rate case public hearings begin** |
| **May 27, 2026** | Pinal County holds lengthy public hearing on **La Osa Data Center**; decision deferred |
| **June 2026** | **Gov. Hobbs signs FY2027 budget (HB 4168 / SB 1861)** containing the **three-year CDC moratorium**. Also signs a bill imposing **new reporting requirements on utilities connecting data centers**. Vetoes a bill inspired by the Marana referendum dispute |
| **June 2026** | APS announces plans for a ~2 GW gas plant with a data-center-focused second phase under a **subscription model** (2031–2033) |
| **June 30, 2026** | **Last day the ACA could accept CDC applications.** Rush of filings reported |
| **July 1, 2026** | **CDC moratorium takes effect** |
| **July 2026** | TEP rate case closing arguments due |
| **July 16, 2026** | EPA proposes eliminating the federal 30-day public notice requirement for minor source air permits — the permit type most Arizona data centers use for backup generation. ADEQ says it is evaluating |

## 7.3 What's coming

| Date | Expected | Confidence |
|---|---|---|
| **August 26, 2026** | Pinal County Board of Supervisors returns to the **La Osa** rezoning | High — publicly scheduled |
| **September 2026** | TEP's requested effective date for new rates | Medium — subject to ACC decision |
| **Before end of 2026** | **ACC decision in the APS rate case**, including XHLF rates, eligibility, minimum bill, and formula rates | Medium-high |
| **November 2026** | **Statewide election.** Hobbs vs. Biggs for Governor; legislative control in play | Certain event, uncertain outcome |
| **Ongoing** | AG Mayes's Superior Court challenge to the TEP ESA | Unresolved — **status as of July 29, 2026 not confirmed** |
| **January 2027** | Legislature convenes. Expected: data center water use, cost-shift prevention, SMR siting, possible further action on incentives | Medium |
| **2027 (at or shortly after launch)** | **APS, SRP, TEP, UniSource join SPP Markets+** | Medium-high — announced intent |
| **June 30, 2029** | **CDC moratorium lifts** — unless the exemption is eliminated in a future session | Statutory, but explicitly conditional |
| **2031–2033** | APS's proposed data-center-focused generation phase under a subscription model | Low — conceptual |

## 7.4 What changed most in the last twelve months

**The tax posture flipped.** Thirteen years of an open-ended incentive ended in a three-year pause, and the Governor's stated preference was elimination. Whatever your view of the merits, **the direction of state fiscal policy toward this asset class reversed in June 2026.**

**Local government became the primary regulator.** Marana adopted a data center ordinance before it had a data center. Tucson and Pima County are drafting zoning amendments. Municipal water utilities adopted industrial usage caps. **The action moved from the ACC to city councils and boards of supervisors.**

**Referendum became a live tool.** It failed once, on a technicality, and was upheld in court. Assume competence next time.

**The ESA's legal foundation came under attack.** The AG's delegation argument, if it succeeds, would unsettle the primary contracting mechanism for large loads in Arizona.

**Water regulation expanded.** A new AMA was designated in January 2026 in a basin where withdrawals ran ~900% over recharge. ADWR is willing to act.

**The rate structure for your class is being rewritten.** A 45%+ increase for XHLF customers is pending before the Commission, alongside formula rates that would escalate annually.

## 7.5 The most important open questions right now

**1. What the ACC does in the APS rate case.** XHLF rates, eligibility criteria, minimum bill, and formula rates all turn on it, and a decision is expected before the end of 2026. **Every economic assumption in a current Arizona pro forma is contingent on this.**

**2. Whether the AG's delegation challenge succeeds.** I could not confirm the status of the Maricopa County Superior Court case as of July 29, 2026. If the ESA structure is found to be an unlawful delegation, the mechanism by which large loads have been contracting in Arizona needs reconstruction.

**3. Whether the ACC adopts a generic large-load rule.** Docket E-00000A-25-0069 remains open; the Commission's stated posture is the tariff-plus-ESA hybrid rather than a codified rule. **No adopted generic rule found as of July 29, 2026.**

---

# PART 8 — RED FLAGS AND OPEN QUESTIONS

## 8.1 What makes a site a non-starter

**Water — check this first, before power**
- **Inside an AMA with no grandfathered rights, no designated provider service, no irrigation district, no effluent source, and no realistic § 45-515 path.** The statutory conditions for a general industrial use permit require showing CAP water, other surface water or effluent, and acquirable nearby irrigation grandfathered rights are all unavailable or uneconomic — that is a real burden, not a formality.
- **Inside a municipal service area with an industrial usage cap you can't meet** without purchasing supplemental supplies you can't source.
- **Outside an AMA in a basin with severe declines.** Ranegras Plain shows ADWR will designate. A rule-of-capture site today can become a permitted site tomorrow.
- **A water-cooled design in a jurisdiction with, or drafting, a potable-water-for-cooling prohibition.**

**Land use**
- **A rezoning requirement in a jurisdiction with an organized opposition** — currently Tucson, Pima County, parts of Pinal, and increasingly Marana.
- **Referendum exposure with no petition-proofing strategy.**
- **A site whose entitlement depends on annexation by a hostile council.**

**Electric**
- **No adequate transmission without a new 115 kV+ line**, which puts you into a contested CEC proceeding with a 180-day statutory clock plus intervenors.
- **A utility with no available capacity on your timeline and no obligation to create it for you.** There is no protocol to appeal to.
- **A site straddling two utilities' territories** without a coordination plan.

**Commercial**
- **A capital structure that can't carry a minimum bill through a slipped ramp.**
- **A pro forma that assumes current published XHLF rates** while a 45%+ increase and formula rates are pending.
- **A pro forma that assumes the CDC exemption.** Paused until June 30, 2029.

**Political**
- **A project that needs the 2027 legislative session to go its way.** Both parties have named data centers as a priority, in opposite directions, in an election year.

## 8.2 Where the sources don't answer — call a consultant or the utility

**1. The utility's actual internal queue process and current capacity position.** Not published. This is the single highest-value call. APS and SRP each built one; ask what it is and where you'd sit.

**2. Real cost of a line extension for a specific site.** Only the utility knows, and the refundable/non-refundable split is negotiated.

**3. Whether the ESA structure survives the AG's challenge.** Watch Maricopa County Superior Court and ACC Docket E-01933A-25-0187.

**4. Whether ADWR would issue a § 45-515 permit in your sub-basin, and on what conditions.** Highly site- and basin-specific. Arizona water counsel, not a generalist.

**5. Whether your parcel carries grandfathered rights, and whether they're conveyable and usable for your purpose.** A title and water rights question that requires records work.

**6. SRP Board disposition.** No docket to read. Political and relationship intelligence.

**7. The final shape of XHLF post-rate-case.** Pending.

**8. Whether the ACC will adopt a generic large-load rule or threshold.** Docket E-00000A-25-0069 open.

**9. Referendum petition-proofing.** After Marana, the drafting standard for a rezoning ordinance's legal description is a live tactical question for Arizona municipal counsel.

**10. What the 2026 utility reporting bill actually requires.** Hobbs signed it; I could not pin down the bill number or the specific reporting obligations. **Verify.**

**11. Whether an FTZ is realistically available at your site.** Depends on the grantee, the zone boundaries, and activation. Ask the local economic development office by name.

**12. Markets+ implications for large-load customers.** The market design's effect on retail large-load rates in a vertically integrated state is genuinely unclear and largely unwritten.

## 8.3 The honest summary

Texas responded to the large-load wave by writing rules: a statute, five rulemakings, a protocol overhaul, a batch study, a threshold, and a schedule of fees. **Arizona has responded by not writing rules** — deliberately. The ACC's stated position is that utility-specific tariffs combined with individually negotiated and Commission-approved energy supply agreements provide "certainty... flexibility and additional customer protections" better than a generic rule would.

That is a defensible policy choice, and it produces a genuinely different practice. In Texas you read the protocol and calculate. In Arizona you negotiate, and the questions that matter are: whose territory, whose water, whose zoning, and what will the Commission approve.

**For someone with a real estate and contracts background and no engineering training, Arizona is the better fit.** The binding constraints here — land entitlement, water rights, negotiated contracts, elected bodies — are all things you were trained to handle. The one thing Arizona demands that Texas does not is genuine local political literacy, county by county. That is not something you can read your way into. It is what the phone calls are for.

---

## APPENDIX — Primary sources, bookmarked

**Arizona Corporation Commission**
- eDocket (all filings) — <https://edocket.azcc.gov/>
- Large Load Users Workshop highlights (Apr 2026) — <https://www.azcc.gov/news/home/2026/04/20/acc-large-load-data-center-workshop-highlights>
- Chairman Myers on the workshop — <https://azcc.gov/news/home/2026/04/17/chairman-myers--highlights-from-large-load-users-development-workshop>
- Power Plant & Transmission Line Siting Committee — <https://azcc.gov/arizona-power-plant/arizona-power-plant>
- Siting FAQs and forms — <https://azcc.gov/arizona-power-plant/FAQs-and-forms>
- Electric utilities / ten-year transmission plans — <https://www.azcc.gov/utilities/industry-types/electric/home>
- Key dockets: **E-00000A-25-0069** (large load users), **E-01933A-25-0187** (TEP ESA / Project Blue), TEP rate case **25-0103**

**Rules and statutes**
- A.A.C. R14-2-201 (definitions: advance vs. contribution) — <https://regulations.justia.com/states/arizona/title-14/chapter-2/article-2/r14-2-201/>
- A.A.C. R14-2-207 (line extensions) — <https://regulations.justia.com/states/arizona/title-14/chapter-2/article-2/r14-2-207/>
- A.R.S. § 45-515 (general industrial use permits) — <https://www.azleg.gov/ars/45/00515.htm>
- Arizona transmission siting overview (RAPID) — <https://openei.org/wiki/RAPID/Roadmap/8-AZ-a>

**Utilities**
- APS rate case — <https://www.aps.com/en/Utility/Regulatory-and-Legal/Rate-case>
- APS data center position — <https://www.aps.com/en/Utility/Company-wide-Events-and-Messages/Data_Centers_How_Were_Protecting_Customers_While_Planning-for_Big_Energy_Needs>
- APS rates, schedules, adjustors (XHLF tariff) — <https://www.aps.com/en/Utility/Regulatory-and-Legal/Rates-Schedules-and-Adjustors>
- APS CEC process — <https://www.aps.com/en/About/Construction-and-Power-Line-Siting/Power-Line-Siting/CEC-Process>
- Trico Rules, Regulations & Line Extension Policies — <https://trico.coop/wp-content/uploads/2025/08/Trico-RRLEP-062117-Edited-032825.pdf>

**Water**
- ADWR Assured and Adequate Water Supply overview — <https://www.azwater.gov/aaws/aaws-overview>
- ADWR AMA overview — <https://www.azwater.gov/ama/active-management-area-overview>
- ADWR Groundwater Code overview (PDF) — <https://www.azwater.gov/sites/default/files/media/Arizona%20Groundwater_Code_1.pdf>
- Ranegras Plain AMA designation (Jan 2026) — <https://www.azwater.gov/news/articles/2026-01-14>
- ADWR legislative affairs tracker — <https://www.azwater.gov/legislative-affairs>
- Phoenix AMA groundwater model updates — <https://www.azwater.gov/phoenix-ama-groundwater-supply-updates>

**Air**
- ADEQ air quality permitting and county delegation — <https://azdeq.gov/AQComplianceAssistance>
- Maricopa County Air Quality permitting — <https://www.maricopa.gov/4058/Permitting>
- Pima County DEQ air program — <https://www.pima.gov/397/Air-Program>

**Tax and incentives**
- Arizona Commerce Authority — Computer Data Center Program — <https://www.azcommerce.com/incentives/computer-data-center-program/>
- Moratorium summary (HB 4168 / SB 1861) — <https://www.multistate.us/insider/2026/6/22/state-data-center-policy-shifts-as-governors-impose-new-restrictions>

**Analysis and reporting**
- Snell & Wilmer, Building in Arizona's Data Center Boom — <https://www.swlaw.com/publication/building-in-arizonas-data-center-boom-how-federal-executive-orders-state-regulation-and-national-security-policy-are-reshaping-the-rules-for-developers/>
- Holland & Hart / SWCA, Siting Energy and Transmission Line Projects in Arizona — <https://www.hollandhart.com/webfiles/Siting_Energy_And_Transmission_Line_Projects_In_AZ_HollandHart_SWCA_2025.pdf>
- Arizona Capitol Times, 2026 session recap — <https://azcapitoltimes.com/news/2026/07/09/data-centers-dominated-2026-session-lawmakers-answered-with-3-year-tax-incentive-pause/>
- AG Mayes v. ACC coverage — <https://azcapitoltimes.com/news/2026/04/09/attorney-general-mayes-sparks-turf-war-with-arizona-corporation-commission/>
- Marana referendum ruling — <https://www.tucsonagenda.com/p/no-vote-on-marana-data-centers>
- Grist on Arizona water and data centers — <https://grist.org/technology/arizona-water-data-centers-semiconducters/>
- Coalition for Sonoran Desert Protection (opposition tracking) — <https://www.sonorandesert.org/2026/05/28/data-centers-update/>
