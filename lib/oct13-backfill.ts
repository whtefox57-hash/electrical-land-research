import {createHash} from 'node:crypto';
import run from '@/data/research-oct13/run.json';
import prose from '@/data/research-oct13/report.json';
import recovered from '@/data/research-oct13/recovered-week.json';
import polygons from '@/data/research-oct13/geometry.json';
import {blankIntelligence,founderProtected} from './intelligence';
import type {Desk,RecordFile} from './model';

const MARKER='oct13-research-v1';
const AT='2026-10-13T00:00:00Z';
const digest=(value:string)=>createHash('sha256').update(value).digest('hex');
function blankRecord(c:any):RecordFile {
 const r:any={id:c.id,name:c.name,recordType:c.landKind==='OFFERED_PORTION'?'OFFERED_PORTION':c.apns.length?'PARCEL':'UNRESOLVED_LEAD',apn:c.apns.join('; '),state:c.state,county:c.county,origin:'October 13 research / recovered prior week',updatedAt:AT,lifecycle:'ACTIVE',summary:c.why,thesis:c.buyerFit,moneyVerdict:c.capitalDecision,facts:[],sections:[],factors:[],checks:[],sources:[],actions:[],geometry:null,geometrySource:'',location:null,kill:null,history:[],notes:'',mapVisible:false,priority_tier:'WATCH',workflow_stage:'INITIAL_SCREEN',evidence_status:'Incomplete desktop review; see October 13 evidence',capital_status:'HOLD',opportunityId:c.id,categoryReason:c.risk,initialScreen:{traceableAsset:false,plausibleEconomics:false,powerSignal:false,buyerFit:false,noSupportedFatal:false,nextTest:true,alternateUse:false},alternateUse:c.alternateUse,buyerFit:c.buyerFit,noteEntries:[],baseline:false};
 r.intelligence=blankIntelligence(r);return r;
}
export function applyOct13(s:Desk){
 if((s as any).appliedUpdates?.includes(MARKER))return false;
 const ids=new Map<string,string>();
 for(const c of run.candidates){
  // A shared broker page or shared parent APN can describe distinct offered tracts.
  // Only collapse by canonical ID or by a matching offering name and listing URL.
  let r=s.records.find(x=>x.id===c.id)||s.records.find(x=>x.name.toLowerCase()===c.name.toLowerCase()&&x.sources.some(src=>src.url===c.listingUrl));
  if(!r){r=blankRecord(c);s.records.push(r);}
  ids.set(c.id,r.id);
  const prior={summary:r.summary,moneyVerdict:r.moneyVerdict,apn:r.apn,askingPrice:r.intelligence?.commercial.askingPrice,portfolioStatus:r.intelligence?.portfolioStatus};
  (r as any).researchOct13={...c,id:r.id};
  if(!r.apn&&c.apns.length)r.apn=c.apns.join('; ');
  if(!founderProtected(r)){
   r.summary=c.why;r.thesis=c.buyerFit;r.moneyVerdict=c.capitalDecision;r.categoryReason=c.risk;r.buyerFit=c.buyerFit;r.alternateUse=c.alternateUse;
  }
  r.updatedAt=AT;
  for(const sid of c.sourceIds){const src=run.sources.find(x=>x.id===sid)!;const id='OCT13-'+sid;if(!r.sources.some(x=>x.id===id))r.sources.push({...src,id});}
  r.facts.push({label:'October 13 research disposition',value:c.priority+' · '+c.novelty,status:'RESEARCH ORDER ONLY',sourceIds:c.sourceIds.map(x=>'OCT13-'+x)},...c.facts.map(([label,value,status])=>({label,value,status,sourceIds:c.sourceIds.map(x=>'OCT13-'+x)})));
  r.sections.unshift({title:'October 13 update',body:c.power+' '+c.risk+' Next: '+c.nextTest,sourceIds:c.sourceIds.map(x=>'OCT13-'+x)});
  r.checks.push({id:'oct13-open-proof',topic:'Current power, use and control proof',status:'UNKNOWN',result:c.risk,scope:'Exact offered land; no paid-control clearance',checkedAt:'2026-10-13',coverageNote:'Listing/current policy checks plus dated prior county research; see source limitations.',sourceIds:c.sourceIds.map(x=>'OCT13-'+x)});
  const intel=r.intelligence||(r.intelligence=blankIntelligence(r));
  intel.land.kind=c.landKind as any;intel.land.apns=c.apns;intel.land.advertisedAcreage=c.acres;
  if('parentAcres' in c){intel.land.assessorAcreage=c.parentAcres as number;intel.land.parentApn=c.apns[0];}
  if('gisAcres' in c&&typeof c.gisAcres==='number')intel.land.gisAcreage=c.gisAcres;
  intel.commercial.priceHistory.push({at:AT,askingPrice:c.price,source:c.listingUrl,note:c.priceNote});
  intel.commercial.askingPrice=c.price;
  // Preserve any founder-entered capacity; never infer or replace it with a marketing number.
  intel.electricity.evidence.push({at:AT,type:'OCT13_RESEARCH',availableMW:null,note:c.power,sourceIds:c.sourceIds});
  if(intel.electricity.available_mw==null)intel.electricity.verification='NOT DOCUMENTED IN OCTOBER 13 REVIEW';
  const feature=polygons.features.find((f:any)=>f.properties?.apn===c.apns[0]||(c.id==='ga-gordon-048007'&&f.properties?.PIN?.replace(/\s+/g,' ')==='048 007'));
  if(!r.geometry&&feature&&c.landKind==='EXACT_APN'){r.geometry=feature.geometry;r.geometrySource='October 8 county-derived tax polygon; see Dillon/Adairsville source audit';(r as any).geometryRetrievedAt='2026-10-08';}
  if(!r.location&&'location' in c&&c.location)r.location={lon:c.location[0],lat:c.location[1],precision:'APPROXIMATE LISTING / PRIOR RESEARCH LOCATOR — NOT OFFERED SURVEY'};
  if(!founderProtected(r)&&(r.geometry||r.location))r.mapVisible=true;
  const prepared=run.actions.filter(a=>a.recordId===c.id).map(a=>({...a,id:'oct13-'+a.id,recordId:r!.id}));
  if(!prepared.length)prepared.push({id:'oct13-'+c.id+'-documents',recordId:r.id,order:1,title:'Resolve the next documented test',contact:c.contact,channel:c.channel,question:c.nextTest,decision:c.risk,costEstimate:'$0 document request; no fees authorized',approvalRequired:true,done:false});
  r.actions.unshift(...prepared.filter(a=>!r!.actions.some(x=>x.id===a.id)));
  r.history.push({at:AT,action:'OCT13_RESEARCH_UPDATE',note:c.priority+'. Evidence update; founder notes, decisions and formal category preserved.',before:prior,runId:run.id,sourceDate:'2026-10-13'});
 }
 const recordIds=[...new Set(ids.values())];
 for(const [id,title,original] of [[run.id,run.title,prose.current],['research-week-2026-10-06','October 6–12 recovered research review',prose.weekly]]){
  if(!s.reports.some(p=>p.id===id||p.runId===id))s.reports.push({id,runId:id,title,original,hash:digest(original),producerId:'founder-requested-research',producedAt:AT,retrievedAt:AT,recordIds,findings:run.candidates.map(c=>({recordId:ids.get(c.id)!,text:c.priority+': '+c.risk,sourceUrl:c.listingUrl,sourceDate:'2026-10-13'})),status:'NEEDS_REVIEW',schemaVersion:2});
 }
 for(const file of recovered.reports){
  const raw=JSON.parse(file.body);const day=raw.run_date;const id='recovered-power-siting-'+day;
  const original='Original recovered report; historical as of '+day+'. Full source metadata retained below.\n\n```json\n'+file.body+'\n```';
  if(s.reports.some(p=>p.id===id||p.hash===digest(original)))continue;
  s.reports.push({id,runId:id,producerId:'recovered-power-siting-watch',title:'Power / Siting Watch · '+day+' · recovered original',producedAt:day+'T00:00:00Z',retrievedAt:AT,original,hash:digest(original),recordIds:[ids.get(run.focusId)!],findings:[],status:'NEEDS_REVIEW',schemaVersion:2});
 }
 (s as any).founderFocusRecordId=ids.get(run.focusId);
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),MARKER];
 s.history.push({at:AT,action:'OCT13_RESEARCH_PUBLISHED',note:'Hinds pinned as active focus at founder request. Fourteen reviewed offering records, ten triage entries, current report, prior-week review and seven original watch reports added. Existing notes, founder decisions, portfolio designations, automation settings and capital caps preserved.'});
 return true;
}
