import {createHash} from 'node:crypto';
import run from '@/data/research-oct22/run.json';
import prose from '@/data/research-oct22/prose.json';
import {blankIntelligence} from './intelligence';
import type {Desk,RecordFile} from './model';

export const OCT22_MARKER='oct22-option-comparison-v1';
const AT='2026-10-22T12:29:28Z';
function newRecord(c:typeof run.candidates[number]):RecordFile {
 const r:RecordFile={id:c.id,name:c.name,recordType:'UNRESOLVED_LEAD',apn:c.apns.join('; '),state:c.state,county:c.county,origin:'October 22 research run',updatedAt:AT,lifecycle:'ACTIVE',summary:c.signal,thesis:run.requirements.primary,moneyVerdict:'HOLD · No paid-control clearance',facts:[],sections:[],factors:[],checks:[],sources:[],actions:[],geometry:null,geometrySource:'',location:null,kill:null,history:[],notes:'',mapVisible:false,priority_tier:'WATCH',workflow_stage:'INITIAL_SCREEN',evidence_status:'V1 · MARKETING / PUBLIC-RECORD SCREEN',capital_status:'HOLD',opportunityId:c.id,categoryReason:c.risk,initialScreen:{traceableAsset:false,plausibleEconomics:false,powerSignal:false,buyerFit:false,noSupportedFatal:false,nextTest:true,alternateUse:false},alternateUse:'Not assessed',buyerFit:'Unvalidated buyer hypothesis',noteEntries:[],baseline:false};
 r.intelligence=blankIntelligence(r);return r;
}
export function applyOct22(s:Desk){
 if((s as any).appliedUpdates?.includes(OCT22_MARKER))return false;
 const recordIds:string[]=[];
 const findings:{recordId:string;text:string;sourceUrl:string;sourceDate:string}[]=[];
 for(const c of run.candidates){
  // Shared listing pages can contain distinct offerings (Dillon 53 / 48).
  // Refreshes must use their canonical IDs; new reviews may reuse an exact URL match.
  let r:any=s.records.find(x=>x.id===c.id);
  if(!r&&c.reviewKind==='REFRESH')throw new Error('Missing canonical October 22 record: '+c.id);
  if(!r)r=s.records.find(x=>x.sources.some(src=>src.url===c.listingUrl));
  if(!r){r=newRecord(c);s.records.push(r);}
  if(r.screeningControl?.status==='STOPPED')continue;
  recordIds.push(r.id);
  r.researchOct22={...c,id:r.id};r.updatedAt=AT;
  const sourceIds=c.sourceIds.map(id=>'OCT22-'+id);
  for(const sid of c.sourceIds){
   const src=run.sources.find(x=>x.id===sid);
   if(!src)throw new Error('Unknown October 22 source: '+sid);
   if(!r.sources.some((x:any)=>x.id==='OCT22-'+sid))r.sources.push({...src,id:'OCT22-'+sid});
  }
  if(!r.facts.some((x:any)=>x.label==='October 22 option comparison'))r.facts.push(
   {label:'October 22 option comparison',value:'#'+c.rank+' · '+c.disposition,status:'ANALYST COMPARISON · NOT FOUNDER TIER',sourceIds},
   {label:'October 22 advertised ask',value:c.price==null?'Unpublished':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(c.price),status:'MARKETING · '+c.priceNote,sourceIds},
   {label:'October 22 available MW / assignment probability',value:'Both unknown (null)',status:'NO ISSUER CAPACITY OR VALIDATED SUCCESS MODEL',sourceIds}
  );
  if(!r.sections.some((x:any)=>x.title==='October 22 option decision'))r.sections.unshift({title:'October 22 option decision',body:c.signal+' '+c.risk+' Next: '+c.nextTest,sourceIds});
  if(!r.checks.some((x:any)=>x.id==='oct22-payment-proof'))r.checks.push({id:'oct22-payment-proof',topic:'Paid option eligibility',status:'UNKNOWN',result:c.risk,scope:'October 30 hypothetical decision; no paid-control clearance',checkedAt:run.asOf,coverageNote:'Fresh public-source review; previous GIS work remains dated. Founder information is preserved separately.',sourceIds});
  const intel=r.intelligence||(r.intelligence=blankIntelligence(r));
  if(!intel.electricity.evidence.some((x:any)=>x.type==='OCT22_OPTION_COMPARISON'))intel.electricity.evidence.push({at:AT,type:'OCT22_OPTION_COMPARISON',availableMW:null,note:c.power,sourceIds});
  if(!intel.commercial.priceHistory.some((x:any)=>x.at===AT&&x.source===c.listingUrl))intel.commercial.priceHistory.push({at:AT,askingPrice:c.price,source:c.listingUrl,note:c.priceNote||'Observed marketing ask; no option agreement.'});
  // Keep founder values, classification, capacity, notes and completed actions intact.
  for(const a of run.actions.filter(a=>a.recordId===c.id).reverse())if(!r.actions.some((x:any)=>x.id===a.id))r.actions.unshift({...a,recordId:r.id});
  r.history.push({at:AT,action:'OCT22_OPTION_COMPARISON',note:c.disposition+'. Source snapshot added; founder decisions and capacity assertions preserved. No outreach or expenditure.',runId:run.id,sourceDate:run.asOf});
  findings.push({recordId:r.id,text:c.disposition+': '+c.risk,sourceUrl:c.listingUrl,sourceDate:run.asOf});
 }
 if(!s.reports.some(p=>p.id===run.id||p.runId===run.id))s.reports.push({id:run.id,runId:run.id,title:run.title,producerId:'founder-requested-research',producedAt:AT,retrievedAt:AT,original:prose.markdown,hash:createHash('sha256').update(prose.markdown).digest('hex'),recordIds:[...new Set(recordIds)],findings,status:'NEEDS_REVIEW',schemaVersion:2});
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),OCT22_MARKER];
 (s as any).latestOptionResearch={runId:run.id,asOf:run.asOf,deadline:run.deadline,conditionalChoiceId:run.focusId,paidControlReady:false,newSpend:0};
 s.history.push({at:AT,action:'OCT22_RESEARCH_PUBLISHED',note:'Twelve offering reviews, including four new review records. Hinds is the conditional target; none cleared for payment. No changes to budget, automations, founder priority or stopped Adairsville work.'});
 return true;
}
