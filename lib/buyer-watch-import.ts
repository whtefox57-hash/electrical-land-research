import {createHash} from 'node:crypto';
import {parseEntities,applyEntities} from './research-upsert';
import {validateDesk, type Desk} from './model';

const producerId='6a8df51b19e481918002b72381a96d67';
const hash=(value:string)=>createHash('sha256').update(value).digest('hex');
const linkKey=(value:string)=>{try{const u=new URL(value);return u.hostname.replace(/^www\./,'')+u.pathname.replace(/\/$/,'')}catch{return value}};

/** Accept the original Buyer Watch export without relaxing decision or power gates. */
export function importBuyerWatch(s:Desk,input:any,delivery='MANUAL_IMPORT'){
 if(input?.schema_version!=='LBW.manual-intake.v1'||typeof input.run_id!=='string'||!input.run_id||input.run_id.length>200||typeof input.report!=='string'||!input.report.trim()||input.report.length>250000||!Number.isFinite(Date.parse(input.as_of))||!Array.isArray(input.offerings)||input.offerings.length>100||!Array.isArray(input.buyer_events)||input.buyer_events.length>100)throw Error('Invalid Buyer Watch export. Use the complete LBW.manual-intake.v1 JSON file.');
 const payloadHash=hash(JSON.stringify(input));
 const old=s.reports.find(p=>p.producerId===producerId&&p.runId===input.run_id) as any;
 if(old){if(old.sourcePayloadHash!==payloadHash)throw Error('CONFLICT: This Buyer Watch run already contains different data. Use a new correction run ID.');return {changed:false,reportId:old.id,recordIds:old.recordIds,duplicate:true};}
 const at=new Date().toISOString();
 const opportunities=input.offerings.map((o:any)=>{
  if(typeof o.url!=='string'||!/^https?:\/\//.test(o.url))throw Error('Offering requires a listing URL');
  const matching=s.records.filter(r=>r.id===o.id||r.sources.some(src=>linkKey(src.url)===linkKey(o.url)));
  if(matching.length>1)throw Error('Multiple existing records match '+o.name+'; reconcile before import.');
  const existing=matching[0],id=existing?.id||o.id;
  const sourceId='LBW-'+input.as_of;
  return {id,...(!existing?{name:o.name,state:o.state,county:o.county||'',summary:o.why||o.risk||'Unqualified advertised offering',recordType:'UNRESOLVED_LEAD'}:{}),sources:[{id:sourceId,title:'Buyer Watch listing observation',url:o.url,publisher:new URL(o.url).hostname,date:o.baseline||input.as_of,retrievedAt:input.as_of,kind:'LISTING_CLAIM',limitation:'Freshness: '+(o.recheck||'Not refreshed')+'. Marketing evidence only; no utility capacity, title or buyer acceptance verified.'}],facts:[{label:'Advertised asking price · '+input.as_of,value:o.ask_text||'UNKNOWN',status:'LISTING CLAIM; see freshness',sourceIds:[sourceId]},{label:'Advertised acreage · '+input.as_of,value:o.acres_text||'UNKNOWN',status:'LISTING CLAIM',sourceIds:[sourceId]},{label:'Next unresolved test · '+input.as_of,value:o.first||o.risk||'UNKNOWN',status:'RESEARCH HOLD',sourceIds:[sourceId]}]};
 });
 const p={...parseEntities({opportunities}),producerId,runId:input.run_id,producedAt:input.as_of,title:'Buyer Watch · '+input.as_of,summary:'Saved dated research; no capital, portfolio or founder-decision changes.',findings:[]};
 const recordIds=applyEntities(s,p,at);
 s.companies??=[];s.events??=[];
 for(const e of input.buyer_events){
  if(typeof e.id!=='string'||!Array.isArray(e.buyer_ids)||typeof e.url!=='string'||!/^https?:\/\//.test(e.url))throw Error('Invalid buyer event');
  for(const buyerId of e.buyer_ids){
   const name=String(buyerId).replace(/^BUYER-/,'').replaceAll('-',' ');
   const normalize=(v:string)=>v.toLowerCase().replace(/[^a-z0-9]/g,'').replace(/datacenters$/,'');
   let company=s.companies.find(c=>c.id===buyerId||normalize(c.name)===normalize(name));
   if(!company){company={id:buyerId,name,segment:'Buyer Watch — requirements unconfirmed',role:'PARTNER',stated:[],revealed:[],inferred:[],serviceOpportunity:'Third-party option acceptance UNKNOWN',unknowns:['Exact markets, facility and IT MW, land-rights acceptance and compensation remain unverified.'],recordIds:[],location:null,projects:[],evidenceGrade:e.evidence||'RESEARCH',sources:[],updatedAt:input.as_of};s.companies.push(company);}
   const statement=input.as_of+': '+e.role+' · '+e.status+' · '+e.product+' · '+e.external_origination;
   if(!company.stated.includes(statement))company.stated.push(statement);
   if(!company.sources.some((x:any)=>x.url===e.url))company.sources.push({title:e.id,url:e.url,date:e.source_date,limitation:e.evidence});
   company.updatedAt=input.as_of;
   s.events.push({id:producerId+'/'+input.run_id+'/'+e.id+'/'+company.id,companyId:company.id,producerId,runId:input.run_id,at,field:'Buyer Watch observation',before:null,after:e,topic:'BUYER',why:p.title,evidenceGrade:e.evidence,source:e.url});
  }
 }
 const reportId='buyer-watch/'+input.run_id;
 s.reports.push({id:reportId,producerId,runId:input.run_id,producedAt:input.as_of,retrievedAt:at,title:p.title,original:input.report,hash:hash(input.report),recordIds,findings:[],status:'NEEDS_REVIEW',schemaVersion:2,delivery,sourcePayload:input,sourcePayloadHash:payloadHash} as any);
 s.history.push({at,action:'BUYER_WATCH_IMPORTED',runId:input.run_id,reportId,delivery,note:'Original export preserved. Listings matched by ID or exact source URL. Founder decisions, notes, expenses and budgets retained.'});
 validateDesk(s);
 return {changed:true,reportId,recordIds,duplicate:false};
}
