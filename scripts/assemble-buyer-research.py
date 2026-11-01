import json, re, csv, math
from pathlib import Path

DEST=Path(__file__).resolve().parents[1]
SRC=DEST/'data/buyer-research-inputs/2026-10-29'
ASOF='2026-10-29'
def read(name): return json.loads((SRC/name).read_text())
def read_sites(group):
    extra=SRC/f'sites_{group}_extra.json'
    return read(f'sites_{group}.json')+(json.loads(extra.read_text()) if extra.exists() else [])
def urls(s): return list(dict.fromkeys(x['url'] for x in s.get('sources',[]) if x.get('url')))
def human(s):
    if not isinstance(s,str) or s.startswith(('http','/')): return s
    s=re.sub(r"(?<=[a-z'’])(?=[\d$])",' ',s)
    s=re.sub(r'(\d)\+(MW|GW|kW)\b',r'\1+ \2',s)
    s=re.sub(r'(?<=\d)(?=(?:MW|GW|kVA|kV|kW|acres\b|ac\b|months\b|miles\b|mi\b|ft\b|SF\b|sf\b|feet\b))',' ',s)
    s=re.sub(r'\b(about|approximately|roughly|within|least|for|and|of|than|from|around|over|under|in|to|at|minimum|maximum|updated|Lots|Lot|Site|Park)(?=\d)',r'\1 ',s)
    s=re.sub(r'(?<=\d)(?=(?:industrial|gross|usable|developable|acre|total|ultimate))',' ',s)
    s=re.sub(r'\b(MO|NC|OR)(?=\d{5})',r'\1 ',s)
    s=s.replace('Hinds is a conditional ERCOT candidate, subject to territory and layout proof.','Hinds is a conditional regional lead; the exact utility/ISO territory and offered tract remain unresolved.')
    s=s.replace("Asking price is within the user's low land-cost lane.","The $399,000 asking price exceeds founder fee-simple resources; affordable option terms are not established.")
    return s
def clean(obj,key=''):
    if isinstance(obj,dict):return {k:clean(v,k) for k,v in obj.items()}
    if isinstance(obj,list):return [clean(v,key) for v in obj]
    if key.lower().endswith(('url','id','ids','date','retrieved','apn')):return obj
    return human(obj)

buyers=[]
for name in ['major','emerging','regional','global','energy']:
    buyers+=read(f'buyers_{name}.json')
assert len(buyers)==100, f'Expected 100 profiles; got {len(buyers)}'
assert len({b['id'] for b in buyers})==100
bm={b['id']:b for b in buyers}
international=set('stt-gdc gds dayone airtrunk nextdc princeton-digital-group kao-data atlasedge atnorth'.split())
lane_members={
 'Mid-scale / urban AI':'metrobloks dataprana aib-data-centers edged colovore montera',
 'Industrial / facility reuse':'tecfusions patmos chirisa serverfarm 1547 data-journey',
 'Regional / interconnection':'equinix coresite cologix h5 365-data-centers tierpoint expedient lightedge us-signal bluebird-fiber ark-data-centers dastor lincoln-rackhouse scalematrix netrality dc-blox radiusdc element-critical dartpoints centersquare csquare flexential databank',
 'Energy-led AI':'crusoe lancium applied-digital terawulf iren core-scientific hut-8 cipher-digital riot-platforms mara soluna bitdeer whitefiber galaxy-digital nscale giga-energy takanock verrus',
 'Land / campus infrastructure':'tract catellus goodman powerhouse',
 'Owner-builders':'aws microsoft google meta apple xai'
}
priority_order='dataprana metrobloks aib-data-centers radiusdc dc-blox tecfusions patmos dartpoints colovore databank cyrusone edged powerhouse chirisa 365-data-centers'.split()
for b in buyers:
    b['lane']='International watch' if b['id'] in international else next((k for k,v in lane_members.items() if b['id'] in v.split()),'Hyperscale campuses')
    b['usRelevance']='low' if b['id'] in international else ('medium' if b['usRelevance']=='low' else b['usRelevance'])
    b['priority']='First requirement-validation calls' if b['id'] in priority_order else ('Sponsor / anchor customer required' if b['lane'] in ['Hyperscale campuses','Energy-led AI','Owner-builders','Land / campus infrastructure'] else 'Validate live acquisition mandate')
    b.pop('candidateSiteIds',None)
    b['noMatchReason']=''
    # Distinguish published product/strategy from an actual land intake criterion.
    strategy_only={'ark-data-centers','atlasedge','avaio','data-journey','dastor','hut-8','iren','lightedge','lincoln-rackhouse','scalematrix','verrus','tract','dc-blox'}
    for r in b['publishedRequirements']:
        if r['kind']=='published requirement' and (b['id'] in strategy_only or (b['id']=='aib-data-centers' and r['fact'].startswith('Current site')) or (b['id']=='giga-energy' and r['fact'].startswith('Company states'))):
            r['kind']='published strategy / product'
bm['radiusdc']['searchBrief']=bm['radiusdc']['searchBrief'].split('No specific currently offered')[0].strip()+' Prioritize a technically viable satellite linked to 1500 Champa; its Denver page says the hub is fully leased and expansion is being evaluated.'
bm['radiusdc']['acquisitionSignal']+=' Current Denver page explicitly states active evaluation of expansion opportunities, though no interest in the Thornton offering is established.'
bm['radiusdc']['publishedRequirements'].append({'fact':'The Denver hub at 1500 Champa is fully leased and RadiusDC says it is actively evaluating expansion opportunities in that market.','sourceUrl':'https://www.radius-dc.com/insights-resources/denver-colorado','kind':'project evidence'})
bm['radiusdc']['sources'].append({'title':'Denver hub and active expansion evaluation','url':'https://www.radius-dc.com/insights-resources/denver-colorado','publisher':'RadiusDC','date':None,'retrieved':ASOF})

sites=[]
def add(s):
    s.setdefault('matches',[])
    s.setdefault('sourceUrls',[s['listingUrl']])
    s['sourceUrls']=list(dict.fromkeys([s['listingUrl']]+s['sourceUrls']))
    s.setdefault('powerVerified',False)
    s['availableMw']=None
    s.setdefault('evidenceDate',ASOF)
    s.setdefault('rank',50+len(sites))
    s.setdefault('lane','Greenfield / phased campus')
    s.setdefault('capitalLane','Buyer-backed / institutional')
    s.setdefault('apnStatus','Reported in marketing only; exact offered boundary, title and ownership not independently reconciled.' if s.get('apn') else 'Exact offered parcel and legal description unresolved.')
    s.setdefault('scenarioHold','')
    s.setdefault('matchCandidates',[])
    existing=next((x for x in sites if x['listingUrl'].rstrip('/')==s['listingUrl'].rstrip('/')),None)
    if existing:
        existing['matchCandidates']+=s['matchCandidates']
        existing['sourceUrls']=list(dict.fromkeys(existing['sourceUrls']+s['sourceUrls']))
        existing['blockers']=list(dict.fromkeys(existing['blockers']+s['blockers']))
        return
    sites.append(s)

for s in read('parcel_candidates.json'):
    s['priceNote']=s.get('quotedPriceText') or s.get('priceNote') or ('Current marketed asking price; confirm with seller.' if s['askingPrice'] is not None else 'No settled total asking price. Obtain a current broker/owner quote; any per-acre arithmetic is not an option fee.')
    s['matchCandidates']=[{'name':n} for n in s.pop('fitBuyerNames')]
    s['availabilityNote']=s.get('availabilityNote','Current owner availability unconfirmed.')
    add(s)

for x in read_sites('major'):
    add(dict(id=x['id'],name=x['name'],location=x['address'],address=x['address'],state=x['state'],acreage=x['acresGross'],askingPrice=x['askingPriceUSD'],priceNote=x['askingPriceText'],apn=x['apn'],apnStatus=x['parcelStatus'],listingUrl=x['listingUrl'],sourceUrls=x.get('sourceUrls',[x['listingUrl']]),status='RESEARCH / broker-marketed offering',availabilityNote=x['availability'],powerClaim=' '.join(x['claims'])+' Available MW is not utility-verified.',fitRationale=' '.join(x['claims'][:1]),blockers=x['blockingQuestions'],controlFeasibility=x['capitalFit'],nextProof=x['nextAction'],matchCandidates=[{'id':m['buyerId'],'why':m['why'],'test':m['specificTest']} for m in x['buyerMatches']]))

for x in read_sites('emerging'):
    add(dict(id=x['id'],name=x['name'],location=x['market'],address=x['address'],state=x['state'],acreage=x['acres'],askingPrice=x['askingPriceUsd'],priceNote=x['priceDescription'],apn='; '.join(x['parcelIds']) or None,apnStatus=x['parcelStatus'],listingUrl=x['listingUrl'],sourceUrls=urls(x),status=x['status'],availabilityNote=x['availability'],powerClaim=x['power']['claim'],fitRationale=' '.join(x['advertisedFacts']),blockers=list(dict.fromkeys(c for m in x['buyerMatches'] for c in m['remainingConditions'])),controlFeasibility=x['capitalFit'],nextProof=x['nextAction'],lane='Existing facility / conversion' if x['buildingSf'] else 'Greenfield / phased campus',matchCandidates=[{'id':m['developerId'],'why':m['why'],'test':'; '.join(m['remainingConditions'])} for m in x['buyerMatches']]))

for x in read_sites('global'):
    add(dict(id=x['id'],name=x['name'],location=x['city']+', '+x['state'],address=x['address'],state=x['state'],acreage=x['acres'],askingPrice=x['price'],priceNote=x['priceBasis'],apn=x['apn'],apnStatus=x['apnStatus'],listingUrl=x['listingUrl'],sourceUrls=urls(x),status=x['status'],availabilityNote=x['availability'],powerClaim=x['powerStatus'],fitRationale=x['whyMatch'],blockers=x['blockingQuestions'],controlFeasibility='No assignable option, seller authority or compensation agreement has been verified. '+x['priceBasis'],nextProof=x['blockingQuestions'][0],matchCandidates=[{'id':i,'why':x['whyMatch']} for i in x['buyerIds']]))

for x in read('sites_regional.json'):
    if x['id']=='chester-ng-datacenter':
        s=next(s for s in sites if s['id']=='em-ng-chester')
        s['matchCandidates'] += [{'name':n,'why':' '.join(x['matchRationale'])} for n in x['buyerNames']]
        s['blockers']+=x['blockers'];continue
    add(dict(id=x['id'],name=x['name'],location=x['address'],address=x['address'],state=x['state'],acreage=x['acres'],askingPrice=x['price'],priceNote=x['priceText'],apn=x['apn'],listingUrl=x['listingUrl'],sourceUrls=urls(x),status='RESEARCH / broker-marketed offering',availabilityNote=x['availability'],powerClaim=x['powerClaim'],fitRationale=' '.join(x['matchRationale']),blockers=x['blockers'],controlFeasibility='No affordable assignable control is established; seller price, authority and contingency terms need confirmation.',nextProof='Obtain exact offered parcels, current offering package and buyer-specific phase/transaction requirements before paying for work.',lane='Existing facility / incremental expansion' if 'buildingSqFt' in x else 'Greenfield / phased campus',matchCandidates=[{'name':n} for n in x['buyerNames']]))

# Energy-specific records; deduplicate the same marketed offering across research lanes.
energy_path=SRC/'sites_energy.json'
if energy_path.exists():
    for x in json.loads(energy_path.read_text()):
        if x['id']=='hinds-110-buyer-screen':continue # only weak oversized/generator-dependent exceptions
        candidates=[{'id':m['buyerId'],'why':m['reason']} for m in x['matches']]
        if x['id']=='rural-hall-circle-143':
            s=next(s for s in sites if s['id']=='rural-hall-circle143')
            s['matchCandidates']+=candidates;continue
        add(dict(id=x['id'],name=x['name'],location=x['address'],address=x['address'],state=x['state'],acreage=x['acres'],askingPrice=x['askingPrice'],priceNote=x['priceLabel'],apn=x['apn'],listingUrl=x['listingUrl'],sourceUrls=[e['url'] for e in x['evidence']],status='RESEARCH / broker-marketed offering',availabilityNote=x['availability'],powerClaim=x['powerStatus'],fitRationale=' '.join(e['claim'] for e in x['evidence']),blockers=x['blockingQuestions'],controlFeasibility=x['founderFit'],nextProof=x['suggestedFirstAction'],lane='Existing facility / conversion' if x['id']=='mayodan-ayersville-plant' else 'Industrial brownfield / redevelopment' if x['id']=='killen-power-plant' else 'Greenfield / phased campus',matchCandidates=candidates))

sm={s['id']:s for s in sites}
name_alias={b['name'].lower():b['id'] for b in buyers}
name_alias.update({'lightedge':'lightedge','h5 data centers':'h5','netrality data centers':'netrality','edged us':'edged','skybox data centers':'skybox','skybox datacenters':'skybox','aib data centers':'aib-data-centers','novva data centers':'novva','dāstor':'dastor','prime data centers':'prime','compass datacenters':'compass','t5 data centers':'t5','stream data centers':'stream'})

def custom(sid,ids):
    s=sm[sid];existing={m.get('id') or name_alias.get(m.get('name','').lower()):m for m in s['matchCandidates']}
    s['matchCandidates']=[dict(existing.get(i,{}),id=i) for i in ids]

# Reject broad "power-seeking company" matches that ignore the actual product or scale.
custom('hinds-110',['dataprana','aib-data-centers'])
custom('benson-12002003a',['novva','tecfusions'])
custom('metamora-37',['us-signal','ark-data-centers','expedient'])
custom('cleveland-marginal-60',['tecfusions','patmos'])
custom('comanche-cr210-112',[]) # no specific buyer/location rationale beyond generic rural power
custom('rome-huffaker-192',['microsoft'])
custom('old-wire-51',[])
custom('em-council-bluffs-121',['edged']) # 121 acres is not a Tract master-park mandate
custom('em-ng-chester',['chirisa','tecfusions','tierpoint','365-data-centers','h5'])
custom('silver-spring-datacenter',['h5','netrality','tierpoint','lightedge'])
custom('forest-grove-kingwood715',['metrobloks']) # reject Crane scale exception unless confirmed
custom('marana-towne-center100',[]) # no proved Beale need beyond existing 600-acre campus
custom('kc-nw128-163',['google','meta','lincoln-rackhouse'])
custom('jerome-industrial-parkway-160',['cologix','365-data-centers','edgeconnex'])
custom('rocket-25',['databank','cyrusone','digital-realty','skybox'])
custom('venus-700',['vantage','qts','stack-infrastructure','skybox','databank','yondr'])
custom('doswell-508',['edgecore','qts','digital-realty','t5','ada-infrastructure'])

sm['hinds-110'].update(status='HOLD / availability and tract conflict',scenarioHold='No numerical scenario until current availability and the exact offered tract are reconciled.',rank=1,capitalLane='Low-cash discovery first',priceNote='Land.com and HAR displayed $385,000 on October 29. Other snapshots/archive pages show $319,000 or $352,000 and conflicting sold status. Treat price/status as unsettled until Davis Vernon confirms MLS 21317653.',availabilityNote='Current Land.com and HAR views say For Sale at $385,000; an archived MLS page says Sold at $352,000. No seller confirmation. Listing ID 27899900 is not an APN.',apnStatus='A prior watch identified parent account 100771, but it is not reconciled to this 110-acre offering. HAR legal description references ABST 2054 and ABST 165, BLK 12, SEC 30 & 31, H&TC.',fitRationale='Buyer-first hypothesis: Dataprana’s 10–50 MW grid strategy is closer to a possible phased 110-acre project than a generic gigawatt-campus buyer list. AIB is an exception test only if its current 40–90 MW product can be supported. Neither has reviewed Hinds.',powerClaim='Crossing 138 kV / 345 kV lines are marketing claims only. Exact distribution/transmission provider, AEP versus cooperative service path, ISO territory, load rights, tariff and schedule remain unresolved. No available MW is verified.')
sm['hinds-110']['sourceUrls']+=['https://www.har.com/homedetail/110-hinds-rd-vernon-tx-76384/17550489','https://steavycarter.com/mls/21317653']
# Only retain observed URLs supplied by the underlying research or root source register.
sm['hinds-110']['sourceUrls']=[u for u in sm['hinds-110']['sourceUrls'] if '17550489' not in u]
sm['old-wire-51'].update(status='ARCHIVE / off-market listing',scenarioHold='Direct listing is off market; no active opportunity or forecast.',capitalLane='Archive / rejected',rank=998)
sm['comanche-cr210-112'].update(status='RESERVE / no defensible buyer match',capitalLane='Reserve / mandate required',rank=990,fitRationale='A nearby substation and rural Texas acreage do not establish a buyer-specific advantage. Archived as a comparison lead until a named buyer supplies a regional need, customer case and usable first-phase layout.')
sm['marana-towne-center100'].update(status='RESERVE / scale and mandate mismatch',capitalLane='Reserve / mandate required',rank=991)
sm['em-tric-electric-75'].update(status='HOLD / direct listing unavailable',scenarioHold='Broker page returned 404; revalidate availability before assigning a scenario.',rank=980)
sm['rome-huffaker-192'].update(status='AUCTION / funded buyer required',capitalLane='Auction / sponsor only',rank=97,scenarioHold='No numerical scenario: auction timing, exact adjacency and a Microsoft requirement are unverified.',controlFeasibility='Auction advertises hard 10% deposit and closing deadline; no diligence contingencies verified. No bid is authorized. Consider only with a funded buyer and documented compensation/control route.',priceNote='Advertised $500,000 is an auction placeholder, not a negotiated asking price. Bidding November 12–19 and advertised December 18 closing need confirmation.')
sm['em-whiteoak-dsc-55'].update(status='PARTNERSHIP / sale not confirmed',capitalLane='Owner JV / no control verified',rank=20)
sm['kc-us40-1021'].update(listingUrl='https://www.showcase.com/8700-e-us-highway-40-kansas-city-mo-64129/39810814/',availabilityNote='Root researcher opened the Showcase offering showing 10.21 acres and $399,000 on October 29. Other retrieval attempts redirected. Live seller availability remains unconfirmed.',rank=4,capitalLane='Low-cash discovery first',nextProof='Obtain the broker survey/easement map and zoning boundaries; establish at least five truly developable acres and a qualifying IXP within the published distance before a utility study.')
sm['kc-congress-lots23'].update(rank=7,capitalLane='Owner JV / no control verified',nextProof='Confirm either individual 18.632/19.621-acre lot passes the IXP test and seller will discuss buyer-led JV/contingent control; reconcile price.')
sm['forest-grove-kingwood715']['fitRationale']='The 7.15-acre nominal size fits metrobloks’ published acreage band. The wetland study, net developable area, FAR, permitted height and qualifying IXP distance remain decisive. Crane’s much larger local campus is a regional precedent, not a defensible buyer match for this small tract.'
sm['rural-hall-circle143'].update(rank=6,capitalLane='Buyer-backed / institutional')
sm['rocket-25'].update(rank=3)
sm['venus-700'].update(rank=10)
sm['em-amgeneral-mishawaka'].update(rank=5)
sm['north-forsyth-313'].update(rank=9)
for i,sid in enumerate(['dickert-70','i26-publicworks-65','fish-hatchery-53','benson-12002003a']):
    sm[sid].update(rank=[2,2.1,12,15][i],capitalLane='Low-cash discovery first')
sm['dickert-70']['priceNote']='County quotes $12,000–$15,000/acre: $840,000–$1.05 million for 70 acres is arithmetic, not a confirmed total offer. Original availability field is 2018; refresh pricing.'
sm['i26-publicworks-65']['priceNote']='County quotes $15,000/acre with minimum 20-acre tract. A 20-acre phase implies $300,000 arithmetically; no subdivision, seller agreement or option fee established. Original availability field is 2015.'
sm['neely-119']['priceNote']='EDC quotes $22,500/acre; 119 acres implies $2,677,500 arithmetically, not a confirmed seller quote. Reconcile tract identity and current terms.'
sm['newberry-south-192']['priceNote']='County quotes $30,000/acre and a 10-acre minimum. Whole-tract arithmetic is $5,773,500; phase size, expansion control and price require seller confirmation.'
sm['henson-road-50']['priceNote']='Listing quotes $150,000/acre. Whole-tract arithmetic is $7,492,500 for 49.95 gross acres, of which roughly 30 are advertised usable. No option price or approved split.'
sm['maiden-enterprise-32']['priceNote']='Conflicting marketed totals around $2.075 million and $2.299 million; exact current offered tract and asking price require confirmation.'
sm['benson-12002003a']['priceNote']='Current broker quote $550,000; older syndication $432,000. Acreage differs (about 90, 103 or 106). Neither offered boundary nor current price is independently settled.'
sm['metamora-37']['fitRationale']='A roughly 34-net-acre industrial site is a regional/incremental-campus hypothesis for Midwest operators. US Signal, Ark and Expedient need a Toledo-area customer/network gap; their other Midwest projects do not establish one.'
if 'mayodan-ayersville-plant' in sm:
    sm['mayodan-ayersville-plant'].update(status='HOLD / current offering and leaseback unresolved',scenarioHold='Current broker availability, possession and price require refresh; historical leaseback changes the build event.',rank=94)
if 'killen-power-plant' in sm:
    sm['killen-power-plant'].update(status='SPECIALIST / remediation and infrastructure rebuild',rank=90,priceNote='No public price. Headline 336.38 acres conflicts with 345.79-acre prose and future remediation acreage. Obtain exact current offered perimeter.',capitalLane='Specialist sponsor / brownfield')
if 'hutto-limmer-94' in sm:sm['hutto-limmer-94']['rank']=14
if 'houston-fidelity-30' in sm:
    sm['houston-fidelity-30'].update(lane='Existing facility / conversion',rank=95,status='HOLD / availability conflict',scenarioHold='Primary broker page remains live, but an off-market syndication and reported Raeden acquisition negotiations conflict. Broker must confirm it is available before a numeric scenario.',availabilityNote='Marcus & Millichap still markets the offering, while Cityfeet marks it off-market and September 2026 reporting describes Raeden acquisition negotiations. Current offering status is unresolved.')
    sm['houston-fidelity-30']['sourceUrls']+=['https://www.cityfeet.com/cont/listing/4202-fidelity-st-houston-tx-77029/cs39695248','https://www.chron.com/news/article/jacinto-city-data-center-texas-22413299.php']
if 'hillsboro-jackson-south32' in sm:sm['hillsboro-jackson-south32']['rank']=24
if 'tonopah-339th-275' in sm:sm['tonopah-339th-275'].update(scenarioHold='No numerical scenario until current floodplain/remediation status and the buyer’s generation/land transaction model are established.',capitalLane='Specialist sponsor / brownfield',rank=93)
if 'em-grant-thornton-12' in sm:sm['em-grant-thornton-12'].update(rank=6.5,status='TARGETED RESEARCH / buyer network link identified')
if 'em-tract-adjacent-buckeye-18' in sm:sm['em-tract-adjacent-buckeye-18'].update(status='ADJACENCY / ancillary acquisition hypothesis',scenarioHold='Potential access, utility-corridor or ancillary purchase is different from the defined data-center construction event. No build scenario until Tract identifies an actual DC use.',rank=96)
if 'em-ovilla-waxahachie-600' in sm:
    sm['em-ovilla-waxahachie-600'].update(status='HOLD / offered perimeter and overlap unresolved',scenarioHold='Reconcile exact current parcels and potential overlap with Project Venus before treating this as independent site inventory.',rank=92)
    sm['venus-700']['blockers'].append('Reconcile parcel schedule with the older Ovilla Road / 600+ acre CBRE offering. The two marketing records may overlap; they are not established independent physical sites or independent buyer probabilities.')
if 'eagle-mountain-jll100' in sm:sm['eagle-mountain-jll100'].update(status='HOLD / offered tranche and acreage unresolved',scenarioHold='Confirm which exact current tranche remains available before modeling a construction event on it. The brochure’s 390/290/100-acre conflict is unresolved.',rank=94)

texas_url='https://gov.texas.gov/news/post/governor-abbott-directs-tceq-to-halt-data-center-permits'
for s in sites:
    if s['state']=='TX':
        s['blockers'].append('Texas Governor’s September 21, 2026 direction pauses affected TCEQ data-center permit reviews pending safeguards. Exact permit scope and current treatment must be established; no end date was verified in this run. Do not assume power confirmation resolves permitting.')
        s['sourceUrls'].append(texas_url)

overrides={
 ('hinds-110','dataprana'):('The 10–50 MW stated grid strategy supports a staged-load question on Hinds. The actual utility/ISO territory, first phase and current availability remain unresolved.','Confirm accepted utility territory and a 10–25 MW first facility phase with possible 50 MW expansion.'),
 ('hinds-110','aib-data-centers'):('AIB’s utility-rights acquisition model is relevant only if this tract can support its current 40–90 MW lane or a buyer-approved smaller first phase. No AIB interest in Hinds is known.','Confirm minimum phase and whether this Wilbarger location qualifies; require transferable rights and buyer-reviewed layout.'),
 ('benson-12002003a','novva'):('Novva’s western, low-water campus strategy provides a design analogy. Benson is a new-market exception; it is not Phoenix, and regional customer/network demand is unproved.','Obtain an explicit Tucson/Benson mandate, exact offered acreage and acceptable customer latency.'),
 ('benson-12002003a','tecfusions'):('TECfusions has a Tucson reuse precedent, making southern Arizona worth a direct requirement question. This is raw land rather than its demonstrated reuse product, a material disadvantage.','Confirm a greenfield exception and whether Benson meets tenant/network geography.'),
 ('venus-700','yondr'):('Yondr has a Dallas/Lancaster campus precedent. A 700-acre Southern Dallas offering could support phased customer capacity, but must beat its already controlled regional pipeline.','Confirm a current DFW acquisition need, first building IT load, diverse network routes and expansion service schedule.'),
 ('doswell-508','ada-infrastructure'):('Ada’s I-95 South Northern Virginia corridor program makes this a specific corridor/latency test. Doswell lies farther south and only 319 of 508 acres are marketed usable.','Obtain buyer acceptance of this corridor, network latency, contiguous net acreage and first-phase capacity.'),
 ('forest-grove-kingwood715','metrobloks'):('The 7.15-acre nominal size fits metrobloks’ published band, but wetland losses, FAR/height and the distance to a qualifying local IXP can defeat it even with suitable power.','Verify at least five developable acres and the actual qualifying IXP distance before buyer submission.'),
 ('rural-hall-circle143','aib-data-centers'):('AIB’s Carolinas pipeline and 40–90 MW development lane create a plausible first-buyer test. The seller’s funded load study and request for buyer input offer a way to shape diligence around that phase.','Confirm an active AIB Carolinas need, preferred 40–90 MW phase and whether study/control rights can transfer.'),
 ('rural-hall-circle143','montera'):('Montera’s large scalable campuses make this a secondary 100+ MW layout test. Neither a Rural Hall mandate nor enough net usable area for its product is established.','Confirm this metro and a 100+ MW initial/ultimate layout before treating Montera as a qualified buyer.'),
 ('rocket-25','skybox'):('Skybox has Houston experience, but the marketed 50 MW first block is below its documented 300+ MW PowerCampus lane. Consider only a smaller-product mandate or credible expansion beyond this first phase.','Ask whether a 50 MW initial / 250 MW possible campus fits any live Skybox customer requirement.'),
 ('em-whiteoak-dsc-55','powerhouse'):('Richmond and a powered-shell/landowner JV structure fit PowerHouse’s demonstrated model. This is a partnership inquiry, not an available assignment of an owned option.','Confirm owner seeks a development partner and PowerHouse has unmet Richmond demand outside existing joint projects.'),
 ('em-whiteoak-dsc-55','chirisa'):('Chirisa’s Richmond presence and acquisition/JV flexibility make an owner partnership plausible; existing regional inventory could eliminate incremental demand.','Verify owner cooperation, buyer customer requirement and a lawful documented compensation route.')
}

# Explicit assumption sets, not measured conversion rates. Products are a conditional chain.
assumption_sets={
 'specific': [[15,30,45],[50,65,80],[60,75,90]],
 'plausible': [[10,20,30],[40,60,75],[50,70,85]],
 'exception': [[5,10,20],[25,45,65],[40,60,80]],
 'reuse': [[15,25,40],[40,60,75],[55,75,90]],
 'entitlement': [[10,20,30],[25,45,65],[50,70,85]],
}
specific_pairs={('rocket-25','databank'),('rocket-25','cyrusone'),('rural-hall-circle143','aib-data-centers'),('venus-700','vantage'),('venus-700','qts'),('venus-700','stack-infrastructure'),('north-forsyth-313','dc-blox')}
exception_sites={'benson-12002003a','kc-us40-1021','forest-grove-kingwood715','tupelo-705','maiden-enterprise-32','fish-hatchery-53','metamora-37','kc-nw128-163'}
phase_by_site={
 'hinds-110':'10–25 MW first facility phase with a possible 50 MW expansion; AIB instead requires a confirmed 40–90 MW product or explicit exception.',
 'benson-12002003a':'20–50 MW first facility phase, subject to buyer confirmation of its product and this southern Arizona market.',
 'kc-us40-1021':'20+ MW facility-side procurement path, consistent with the published metrobloks criterion; the source does not label its MW as IT.',
 'kc-congress-lots23':'20+ MW facility-side capacity on one 18.632/19.621-acre lot, with buyer-approved ramp.',
 'forest-grove-kingwood715':'20+ MW facility-side capacity on the net buildable portion; this may fail layout even with power.',
 'rural-hall-circle143':'40–90 MW facility-side capacity for AIB; Montera requires a separately confirmed 100+ MW campus program.',
 'rocket-25':'50 MW facility-side first block; 250 MW expansion remains a separate unverified broker claim.',
 'venus-700':'150 MW facility-side first block; the advertised 2,400 MW future target is not assumed delivered or secured.',
 'em-amgeneral-mishawaka':'10–20 MW initial facility phase for conversion, expandable if layout/customer demand justifies it; broker’s 50 MW possibility is unverified.',
 'em-ng-chester':'10–30 MW of incremental facility-side retrofit capacity, subject to buyer engineering; existing acquisition alone is not the modeled event.',
 'silver-spring-datacenter':'Buyer-specified incremental 5–10 MW expansion/major conversion beyond current commitments; existing contracted IT load is not free expansion power.',
 'maiden-enterprise-32':'3–8 MW facility-side regional phase. Public marketing does not establish 10–50 MW; a larger product must be rejected or separately studied.',
 'i26-publicworks-65':'5–15 MW initial facility phase on an agreed subdivision, with buyer-approved expansion rights.',
 'dickert-70':'5–20 MW initial facility phase, not a claim that the marketed 12 kV distribution can deliver it.',
 'fish-hatchery-53':'5–20 MW initial regional facility phase, which must correspond to a real Columbia-area customer/network need.',
 'metamora-37':'5–20 MW facility-side Midwest phase, buyer-approved; existing Toledo Edison line data is not deliverability.',
 'cleveland-marginal-60':'20–50 MW first facility phase; generation-site history does not establish an import right.',
 'tupelo-705':'100–200 MW first facility phase with scalable service for a customer-led campus.',
 'abilene-eastlake-1450':'100–300 MW first facility phase with staged campus expansion, separate from existing controlled Abilene projects.',
 'doswell-508':'100–200 MW first facility phase across a verified contiguous buildable area.',
 'jerome-industrial-parkway-160':'50 MW facility-side first block as a hypothetical condition; broker capacity/zoning statements remain unverified.',
 'aurora-connect470-26':'20–40 MW first facility phase on the actual 26.8-acre Lot 1, subject to product and usable-area fit.'
}
phase_by_site.update({'hutto-limmer-94':'20–40 MW first facility phase for an Austin/Hutto metro product; Colovore’s actual rack-density, coolant and expansion requirements must define the plan.','killen-power-plant':'100–200 MW technically deliverable facility-side first phase after necessary infrastructure rebuild; neither the retired generation rating nor a third party’s 650 MW proposal is assumed available.','mayodan-ayersville-plant':'10–20 MW first facility-side conversion phase; advertised switchgear ratings are not service commitments.'})
phase_by_site.update({'em-grant-thornton-12':'Buyer-approved incremental deployment/major conversion within a hypothetical 7 MW facility-side service envelope. The broker’s 3.5 MW in-use / 7 MW equipment sizing is not vacant IT load or confirmed incremental service.','houston-fidelity-30':'40 MW facility-side first conversion phase, with a separately proven 79 MW expansion path; neither figure is utility-verified.','hillsboro-jackson-south32':'Buyer-approved 30–60 MW facility-side first phase with a verified campus layout and future expansion strategy; no acreage-to-MW yield is assumed.'})
phase_by_site.update({'mesa-eastmark-5289':'Buyer-approved first building around 36 MW critical IT, with separately sized facility service and cooling loads. This is an NTT project analogy, not a site commitment or universal requirement.','chicago-cermak-square':'16 MW initial and up to 40 MW later as the broker’s hypothetical phase concept; confirm whether those figures mean utility or critical IT load and what can actually be accommodated.'})
for s in sites:
    seen=set()
    for m in s.pop('matchCandidates'):
        bid=m.get('id') or name_alias.get(m.get('name','').lower())
        if not bid or bid not in bm:raise ValueError((s['id'],m))
        if bid in seen:continue
        seen.add(bid); b=bm[bid]
        why=m.get('why') or f"Buyer-specific test: {b['searchBrief']} Candidate evidence: {s['fitRationale']}"
        if not m.get('why') and bid=='dc-blox':
            why=f"DC BLOX's Southeast development model combines sites and power with its dark-fiber network. {s['name']} is a regional node or phased-campus hypothesis only if it fills an uncovered customer/network need; nearby generic telecom service is insufficient. Test the actual route to DC BLOX's backbone and compare against its owned capacity."
        elif not m.get('why') and bid=='dartpoints':
            why=f"DartPoints' regional enterprise/edge model calls for a smaller customer-backed phase rather than a remote hyperscale park. {s['name']} needs an identifiable regional latency/customer gap, diverse network access and a build-versus-existing-facility cost advantage. Its local footprint can also mean no additional site is needed."
        elif not m.get('why') and bid=='compass':
            why=f"Compass uses repeatable single-tenant campus phases and closed-loop/air cooling. The {s['acreage']}-acre gross offering warrants a modular-layout and expansion test, with contiguous buildable pads, chiller/generator yards and a confirmed customer region; acreage alone does not prove the product fits."
        elif not m.get('why') and bid=='prime':
            why=f"Prime's customer-led build-to-suit/powered-shell model makes the site's phase, utility delivery and transaction structure central. The {s['acreage']}-acre offering is a campus hypothesis only after a tenant geography, independent fiber entrances and expandable layout are established."
        elif not m.get('why') and bid=='t5':
            why=f"T5 expressly concentrates development on a short list of large campuses. {s['name']} must first make that location/product list; its service-business footprint is not evidence of land-buying demand. Test net contiguous area, phased expansion and customer delivery date."
        elif not m.get('why') and bid in {'applied-digital','hut-8','crusoe','lancium','vantage'}:
            why=f"{b['name']}'s specific search: {b['searchBrief']} The {s['acreage']}-acre offering can be tested for a staged customer-backed campus, but rural land plus transmission is insufficient. Fiber construction, actual first-phase size and an advantage over controlled inventory remain decisive."
        test=m.get('test') or b['buyerQuestions'][0]
        if (s['id'],bid) in overrides:why,test=overrides[(s['id'],bid)]
        strength='plausible'
        if (s['id'],bid) in specific_pairs:strength='specific'
        elif s['id'] in exception_sites or (s['id'],bid) in {('rural-hall-circle143','montera'),('rocket-25','skybox'),('em-125','edgecore'),('doswell-508','ada-infrastructure')}:strength='exception'
        elif s['id'] in ['holyfield-174','doswell-508','cleveland-marginal-60']:strength='entitlement'
        elif s['lane'].startswith('Existing'):strength='reuse'
        params=[p[:] for p in assumption_sets[strength]]
        if s['id']=='killen-power-plant':params=[[5,15,25],[15,30,50],[40,60,80]]
        if s['id']=='em-grant-thornton-12':params=[[20,35,50],[45,65,80],[60,75,90]]
        if bid=='data-journey':params[2]=[20,45,65] # private funding visibility / documented failed prior closing
        if s['id']=='rural-hall-circle143' and bid not in ['aib-data-centers','montera']:
            params=[[5,15,25],[30,50,70],[40,60,80]]
            if bid=='data-journey':params[2]=[20,45,65]
        vals=[math.floor(math.prod(p[i] for p in params)/10000+0.5) for i in range(3)]
        if s['scenarioHold']: vals=[None,None,None]
        power_scenario=phase_by_site.get(s['id'],'A buyer-confirmed 30–100 MW facility-side first phase with a suitable technical delivery path; this range is a search assumption, not an observed site capacity.')
        if s['id']=='rural-hall-circle143' and bid not in ['aib-data-centers','montera']:power_scenario='A buyer-approved 20–50 MW facility-side first phase with appropriate expansion; a greenfield product and this exact submarket must be explicitly accepted.'
        s['matches'].append(dict(buyerId=bid,low=vals[0],base=vals[1],high=vals[2],rationale=why,rejection=' '.join(s['blockers'][:2])+' Buyer-specific risk: '+b['rejectionTriggers'][0],raiseIf=test+' Also obtain a named decision-maker’s written requirement, exact offered boundary/control route and an anchor-customer/financing path.',powerScenario=power_scenario,scenarioHold=s['scenarioHold'],assumptionInputs=[] if s['scenarioHold'] else [dict(stage=label,low=p[0],base=p[1],high=p[2]) for label,p in zip(['Buyer selects this site, given suitable power','Non-power land, permits, network and economics clear, given selection','Funded physical construction starts by the horizon, given prior gates'],params)]))
    s['sourceUrls']=list(dict.fromkeys([s['listingUrl']]+s['sourceUrls']))

for b in buyers:
    ms=[s for s in sites if any(m['buyerId']==b['id'] for m in s['matches'])]
    b['matchStatus']=f'{len(ms)} researched site hypotheses; no expressed buyer interest verified.' if ms else 'No defensible marketed match established in this run.'
    if not ms:
        if b['id'] in international:b['noMatchReason']='International watch: no current U.S. acquisition mandate established. Preserve this market-specific search brief; do not force a U.S. parcel or invent a construction probability.'
        elif b['lane']=='Owner-builders':b['noMatchReason']='Owner-builder: public projects do not establish an open land acquisition intake. No specific marketed tract in this run has sufficient evidence of an unmet requirement; validate the internal site-selection mandate first.'
        else:b['noMatchReason']='No sufficiently specific marketed match found in this run. The search brief below remains actionable; buyer geography, product and unmet capacity need must be confirmed before attaching a parcel.'

buyers.sort(key=lambda b:(priority_order.index(b['id']) if b['id'] in priority_order else 100,b['name'].lower()))
sites.sort(key=lambda s:s['rank'])

method={
 'event':'The modeled event is that the named developer funds and begins physical construction of a first permanent data-center phase, or a major incremental conversion/expansion, on the identified offering by October 29, 2031. A purchase, announcement, land clearing or existing facility operation alone does not count. Actual buyer-specific construction probability is not yet estimable from public evidence.',
 'assumptions':[
  'User-specified condition: adequate technically deliverable power capacity for the buyer-approved first phase is demonstrated. None of these sites currently has utility-verified available MW in this research. Facility MW and critical IT MW are kept distinct; no fixed PUE conversion is assumed.',
  'Power suitability does not silently waive power price, upgrade allocation, collateral, tariff, redundancy, exact service date or transferability. Those commercial and scheduling issues remain in the execution gates unless the buyer separately accepts them.',
  'Each numerical scenario shows three subjective conditional inputs: buyer selection given power × non-power feasibility given selection × financed construction start given preceding gates. This is a conditional chain, not multiplication of independent marginal risks.',
  'Low/base/high outputs are products of the displayed assumption inputs, rounded to whole percentages. They are transparent planning cases, not measured rates, confidence intervals or statistically calibrated forecasts. You can change the base inputs in the site card to see sensitivity.',
  'The first-phase load in each card is a hypothesis to validate with the buyer. It is not an available-MW claim, engineering design or developer mandate. All other information is held at the public-evidence stage.',
  'Buyer identity, customers, competing owned inventory, customer latency, layout, permits, cooling/water, fiber construction, funding, seller cooperation and economics remain material. Existing facilities are modeled only for incremental build or major conversion.',
  'Hinds, the unavailable TRIC listing and the auction adjacency hypothesis receive no numerical scenario until their stated status/identity gates are resolved. Archived or rejected leads do not acquire a forecast merely because power is assumed.'
 ],
 'limitations':[
  '100 profiles are not 100 confirmed buyers. The directory includes operating developers, owner-builders, powered-land/master developers and nine international watch profiles. Roles and parent/JV links are disclosed.',
  'No developer has reviewed these site matches. Sources include published intake criteria, regulatory filings, project announcements, company pages and broker/EDC offerings. Project precedents are not universal purchasing requirements.',
  'No negative-project denominator, comparable conversion cohort or private buying mandate exists in this dataset. These subjective ranges can be substantially wrong; they must not be used as a land valuation or justification for spending.',
  'A buyer may build yet never buy a Syncranicity option. Sale price is not option cost. Assignment rights, seller authority, utility study reliance/transfer and compensation have not been established for any new lead.',
  'Matches share risks and some companies share parents or JVs. Do not add the percentages or calculate an at-least-one-buyer probability as if the opportunities were independent. Site counts are marketed offering records: the older Ovilla Road and Project Venus records may overlap and are flagged for parcel reconciliation.',
  'Availability, asking prices and published plans can change. A listing or EDC record is evidence of marketing, not seller confirmation. APNs shown are reported identifiers, not a title or boundary certification.',
  'The existing <$100,000 founder capital constraint, $5,000 learning cap and $10,000 soft-control cap remain unchanged. This research authorizes no payment, bid, reservation or outreach.'
 ]
}
actions=[
 dict(title='Validate three different buying briefs',contactUrl=bm['metrobloks']['sources'][0]['url'],contactLabel='metrobloks property intake',why='Start with metrobloks, Dataprana and AIB because their different published products can reject whole categories of land before spending.',script='I source conditional land and utility-rights opportunities. Before sending a parcel, I want to confirm the exact market, first-phase MW, latest service date and transaction you would consider. Your published criteria suggest a particular search lane; is it active today?',voicemail='I am validating your current land-acquisition brief before submitting sites. Could the person responsible for site selection confirm active metros, phase size and evidence needed for an initial review?',questions=['Which markets and first/ultimate MW are open now, and are those facility or critical IT MW?','metrobloks: qualifying IXP/distance method, net acres, FAR and height? Dataprana: accepted ISO/utility territories and 10–50 MW ramp? AIB: actual 40–90 MW minimum and any smaller-phase exception?','What customer commitment, power documents, fiber evidence and entitlement stage are required?','Would you take an assignable contract, direct purchase, landowner JV or staged closing, and who pays for studies/collateral?'],success='A named authorized reviewer, written brief, minimum submission package and next review date.',stop='No active geography/product mandate or no acceptable route for a small originator.'),
 dict(title='Reconcile Hinds before forecasting it',contactUrl=sm['hinds-110']['listingUrl'],contactLabel='Hinds listing / broker channel',why='Current pages conflict on status and price; the exact 110-acre carve-out and service territory remain unresolved.',script='Please confirm whether MLS 21317653 is available, the current price, exact county account and survey/legal description for the offered 110 acres. If it is available, would the owner authorize parcel-specific utility diligence and consider an assignable agreement with utility and buyer contingencies?',voicemail='I need to reconcile the current Hinds offering before any further diligence: availability, exact tract, asking price and whether conditional control is possible. Please send the current offering package.',questions=['Which current owner/entity has authority and what exact land is offered?','What explains the active/sold and $319k/$352k/$385k differences?','Which utility is authorized to respond for this tract, and can the existing AEP contact document the service path?','What diligence, assignment, deposit and extension terms would the seller actually consider?'],success='One reconciled current offering and a written utility-intake path; then validate Dataprana/AIB phase fit.',stop='Unavailable tract, unresolved owner authority or hard-money terms outside existing caps.'),
 dict(title='One Newberry buyer/EDC sprint',contactUrl=sm['dickert-70']['listingUrl'],contactLabel='Dickert / Newberry property record',why='Compare Dickert and I-26 Public Works only after DC BLOX or DartPoints identifies a real network/customer gap. Old per-acre marketing needs refresh.',script='We are checking whether a small phased data-center opportunity serves a specific regional buyer need. Could you confirm current availability, exact parcels, owners, per-acre pricing and whether a roughly 20-acre initial tract with expansion rights is possible?',voicemail='I am comparing two Newberry industrial offerings against a buyer-specific phased-load requirement. Please send current parcel, pricing, utility and carrier information and the right development contact.',questions=['Is there an unmet DC BLOX/DartPoints customer or network need here?','Are Dickert and I-26 still offered, and what subdivisions/expansion rights are permitted?','Who at the cooperative will provide a parcel/load/date-specific written response?','Can two physically diverse carrier routes be built and at what order-of-magnitude cost?'],success='A specific buyer reason to locate here plus refreshed owner/parcel and utility/carrier intake data.',stop='Existing regional capacity already serves demand, or network/buildable-area constraints defeat the phase.'),
 dict(title='Test Rocket’s advertised documents',contactUrl=sm['rocket-25']['listingUrl'],contactLabel='CBRE Project Rocket offering',why='Its advertised 50 MW path is a concrete document request. DataBank/CyrusOne should define the required Houston product before paid studies.',script='Your offering references a CenterPoint-studied 50 MW path and expansion. Please provide the exact parcels, current availability, executed or draft utility documents, conditions, service dates and reliance/transfer rights. We are checking a named metro-capacity buyer fit before committing capital.',voicemail='I would like the documents behind Project Rocket’s advertised power path, exact offered acreage and current pricing/contingency terms for a buyer-led review.',questions=['What is executed versus studied, and what expires or requires collateral?','Is the first 50 MW facility or IT capacity, and what is the actual deliverability date?','Can a new buyer rely on/assume the studies, service agreements and land rights?','What are the exact fiber routes, flood/drainage findings and current permit requirements?'],success='A reviewable utility/land package and a developer willing to compare it with owned Houston alternatives.',stop='No transferable advantage, unclear offering perimeter or unaffordable hard control.'),
 dict(title='Use Rural Hall to shape diligence with a buyer',contactUrl=sm['rural-hall-circle143']['listingUrl'],contactLabel='CBRE 8700 Circle Drive',why='Seller-funded study underway and a request for early buyer input make this a direct test of the buyer-first process.',script='The listing says the load study is funded and you welcome early buyer input. Could we align the study/site plan with a specific 40–90 MW developer brief, and clarify the rezoning process, exact parcels and control/assignment route?',voicemail='I am assessing whether a named developer’s phase requirements can inform the existing Rural Hall study. Please share study scope/timing, current entitlement docket and seller’s preferred transaction.',questions=['Which utility, applicant and phase are in the existing study?','What is the rezoning docket, current status and realistic decision path?','Can the eventual developer rely on or assume the study and service rights?','What asking price and conditional structure would the owner discuss?'],success='AIB or another suitable buyer confirms this market/phase and is willing to guide the next study step.',stop='Buyer needs a different market/product or study/land rights cannot be made usable.'),
 dict(title='Qualify a conversion rather than raw land',contactUrl=sm['em-amgeneral-mishawaka']['listingUrl'],contactLabel='Former AM General plant offering',why='TECfusions and Patmos have reuse precedents; the Mishawaka shell only helps if conversion beats new construction on cost and schedule.',script='Please provide vacant-possession status, current equipment schedule, environmental reports, structural loading and transferable utility agreements. We are checking phased data-center conversion with a specialist buyer.',voicemail='I am evaluating the former AM General property for a buyer-led technical conversion review. Please send the current sale/lease package, power-service documents and environmental/structural diligence.',questions=['What remains from the former electrical system and what is actually serviceable?','Are former peak demand and prospective 50 MW claims supported by current utility documents?','What contamination, roof/floor, cooling-yard, generator/noise and fire constraints exist?','Will the owner consider buyer-backed exclusivity while a specialist screens conversion economics?'],success='A specialist developer accepts the market and confirms a reusable technical/cost advantage.',stop='Retrofit scope removes the time/cost benefit or environmental liabilities cannot be allocated.'),
]
actions.insert(1,dict(title='Test RadiusDC’s Denver expansion gap',contactUrl='https://www.radius-dc.com/insights-resources/denver-colorado',contactLabel='RadiusDC Denver expansion statement',why='The Thornton offering advertises dark fiber to RadiusDC’s fully leased 1500 Champa hub. This connects a site feature to a disclosed expansion search, although no parcel interest is verified.',script='Your Denver page says you are evaluating expansion. Would an existing Thornton facility with verified diverse dark-fiber rights to 1500 Champa and a roughly 7 MW facility service envelope fit that requirement? We would first validate actual vacant capacity, rights and conversion economics.',voicemail='I am checking a Champa-connected Thornton facility against your published Denver expansion need. Could your acquisitions or development lead confirm whether this location, scale and acquisition/retrofit structure are relevant?',questions=['Is the current need another carrier hub, a connected satellite, or larger purpose-built capacity?','Does Thornton work for the actual customer latency and interconnection product?','What minimum incremental IT capacity, coolant density, vacant-possession and service date are required?','Will you review a broker-led acquisition packet before we pursue any control or paid studies?'],success='A named buyer reviewer accepts the specific product/location and states the minimum engineering and commercial evidence.',stop='Wrong scale/product, existing pipeline already covers demand, unusable fiber rights, or tenant encumbrances prevent meaningful expansion.'))
dataset=clean(dict(asOf=ASOF,buyers=buyers,sites=sites,summary='Reverse the sequence: obtain the developer’s current requirement, use the tailored search brief, validate one specific offering, then test affordable transferable control. This is a research and call-priority dataset; no new site has passed investment or control gates.',methodology=method,actions=actions))
out=DEST/'data/buyer-first-2026-10-29.json';out.write_text(json.dumps(dataset,ensure_ascii=False,indent=2)+'\n')
pub=DEST/'public/research/buyer-first-2026-10-29';pub.mkdir(parents=True,exist_ok=True)
(pub/'research.json').write_text(out.read_text())
with (pub/'buyers.csv').open('w',newline='') as f:
    fields=['id','name','role','parentGroup','usRelevance','lane','priority','regions','strategy','scale','publishedRequirements','inferredPreferences','differentiators','dealStructure','acquisitionSignal','searchBrief','rejectionTriggers','buyerQuestions','matchStatus','noMatchReason','sources']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for b in dataset['buyers']:w.writerow({k:json.dumps(b[k],ensure_ascii=False) if isinstance(b[k],list) else b[k] for k in fields})
with (pub/'site-matches.csv').open('w',newline='') as f:
    fields=['site_id','site_name','location','buyer_id','buyer_name','actual_probability','scenario_base_pct','scenario_low_pct','scenario_high_pct','scenario_inputs','forecast_hold','event_horizon','power_condition','rationale','rejection','raise_if','acreage','asking_price','price_note','status','capital_route','apn','apn_status','available_mw','listing_url','source_urls']
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
    for s in dataset['sites']:
        for m in s['matches']:
            w.writerow(dict(site_id=s['id'],site_name=s['name'],location=s['location'],buyer_id=m['buyerId'],buyer_name=bm[m['buyerId']]['name'],actual_probability='Not yet estimable',scenario_base_pct=m['base'],scenario_low_pct=m['low'],scenario_high_pct=m['high'],scenario_inputs=json.dumps(m['assumptionInputs']),forecast_hold=m['scenarioHold'],event_horizon='2031-10-29 physical first-phase or major incremental conversion start',power_condition=m['powerScenario'],rationale=m['rationale'],rejection=m['rejection'],raise_if=m['raiseIf'],acreage=s['acreage'],asking_price=s['askingPrice'],price_note=s['priceNote'],status=s['status'],capital_route=s['capitalLane'],apn=s['apn'],apn_status=s['apnStatus'],available_mw='Unknown',listing_url=s['listingUrl'],source_urls=' | '.join(s['sourceUrls'])))

lines=['# Buyer-first data-center research','',f'Research cutoff: {ASOF}','',dataset['summary'],'','## Scope and probability method','',method['event'],'']
for label in ['assumptions','limitations']:
    lines += ['### '+label.title(),'']+['- '+x for x in dataset['methodology'][label]]+['']
lines+=['## 100 developer profiles','']
for i,b in enumerate(dataset['buyers'],1):
    lines += [f"### {i}. {b['name']}",'',f"**Role:** {b['role']} · **Lane:** {b['lane']}",'',f"**Parent / shared interests:** {b['parentGroup']}",'',b['strategy'],'',f"**Geography:** {'; '.join(b['regions'])}",'',f"**Scale:** {b['scale']}",'','**Published evidence**','']
    lines += [f"- **{r['kind']}:** {r['fact']} [Source]({r['sourceUrl']})" for r in b['publishedRequirements']]+['']
    for label,key in [('What changes the search','differentiators'),('Analyst inference','inferredPreferences'),('Potential rejection risks','rejectionTriggers'),('Questions to validate','buyerQuestions')]:lines += [f'**{label}**','']+['- '+x for x in b[key]]+['']
    lines += [f"**Transaction route:** {b['dealStructure']}",'',f"**Acquisition signal:** {b['acquisitionSignal']}",'',f"**Search brief:** {b['searchBrief']}",'',b['matchStatus']+' '+b['noMatchReason'],'','**Sources**','']+[f"- [{x['title']}]({x['url']}) — {x['publisher']}; {x['date'] or 'undated'}; checked {x['retrieved']}" for x in b['sources']]+['']
lines += ['## Specific offerings and buyer-site scenarios','']
for s in dataset['sites']:
    lines += [f"### {s['name']}",'',s['status']+' · '+s['capitalLane'],'',s['address'],'',f"Advertised acres: {s['acreage'] if s['acreage'] is not None else 'unresolved'}. {s['priceNote']}",'',s['fitRationale'],'',f"**Availability:** {s['availabilityNote']}",'',f"**Parcel:** {s['apn'] or 'Unresolved'}. {s['apnStatus']}",'',f"**Power evidence:** {s['powerClaim']}",'',f"**Control:** {s['controlFeasibility']}",'','**Blockers**','']+['- '+x for x in s['blockers']]+['',f"**Next proof:** {s['nextProof']}",'']
    for m in s['matches']:
        forecast='NO NUMERICAL SCENARIO: '+m['scenarioHold'] if m['base'] is None else f"Uncalibrated planning base {m['base']}%, low–high {m['low']}–{m['high']}%. Actual probability not yet estimable."
        lines += [f"**{bm[m['buyerId']]['name']}** — {forecast}",'',m['rationale'],'',f"Power condition: {m['powerScenario']}",'',f"Could still reject: {m['rejection']}",'',f"Update trigger: {m['raiseIf']}",'']
        for a in m['assumptionInputs']:lines += [f"- {a['stage']}: low {a['low']}%, base {a['base']}%, high {a['high']}% (analyst assumption)."]
        lines+=['']
    lines += [f'- [Site source {i+1}]({u})' for i,u in enumerate(s['sourceUrls'])]+['']
lines+=['## Founder action scripts','']
for a in dataset['actions']:
    lines += [f"### {a['title']}",'',a['why'],'',f"[{a['contactLabel']}]({a['contactUrl']})",'',a['script'],'']+['- '+q for q in a['questions']]+['','**Voicemail:** '+a['voicemail'],'','**Success:** '+a['success'],'','**Stop:** '+a['stop'],'']
(pub/'report.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'buyers':len(buyers),'sites':len(sites),'pairs':sum(len(s['matches']) for s in sites),'numericScenarios':sum(m['base'] is not None for s in sites for m in s['matches']),'buyersMatched':len({m['buyerId'] for s in sites for m in s['matches']}),'uniqueSources':len({u for s in sites for u in s['sourceUrls']}|{u['url'] for b in buyers for u in b['sources']})}))
