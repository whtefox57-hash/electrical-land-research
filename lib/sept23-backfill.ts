import {createHash} from 'node:crypto';
import catalog from '@/data/research-sept23/research.json';
import candidates from '@/data/research-sept23/new-candidates.json';
import {newResearchRecords} from './sept20-backfill';
import type {Desk} from './model';

export function inferenceResearchRecords(){
 return newResearchRecords({asOf:catalog.asOf,candidates},'September 23 smaller inference research').map((r:any)=>{
  // Catalog owns immutable research details; workspace owns mutable founder work.
  r.recordType='UNRESOLVED_LEAD';
  r.dealCard={id:r.id,batch:'inference-50'};
  r.sources=r.sources.slice(0,1);
  r.actions=r.actions.slice(0,1).map((a:any)=>({...a,question:a.order===1?'Confirm active listing, price, exact offered APNs and assignable-option willingness.':a.order===2?'Confirm exact jurisdiction and current DC/generator use path.':'Confirm exact utility territory and a written 20–30 MW large-load screening path.',channel:a.channel,decision:'Written proof before paid control.'}));
  r.sections=[];
  r.alternateUse='Not verified';
  r.sources[0].limitation='Listing only; seller, title, MW and fiber unverified.';
  r.history[0].note='Unqualified inference lead; no paid control.';
  r.thesis='20–30 MW facility inference hypothesis; buyer not engaged.';
  r.buyerFit=r.thesis;
  r.initialScreen={traceableAsset:false,plausibleEconomics:false,powerSignal:false,buyerFit:false,noSupportedFatal:false,nextTest:true,alternateUse:false};
  r.moneyVerdict='HOLD — assignment probability not estimable; no paid control authorized.';
  r.intelligence.buyer={initialInterest:'No buyer engagement',killHold:'See research card',deeperDiligence:'Resolve decisive issue in card',buildInvestment:'Not established',objection:'Power, fiber, use, funding and transfer rights unknown',substitutes:'Not researched',whyPay:'Not buyer validated',nextProof:'Document calls'};
  return r;
 });
}
export function applySept23(s:Desk){
 const marker='sept23-inference-50-v1';
 if((s as any).appliedUpdates?.includes(marker))return false;
 const at=new Date().toISOString();
 for(const r of inferenceResearchRecords())if(!s.records.some(old=>old.id===r.id))s.records.push(r);
 const run=catalog.runs[0];
 if(!s.reports.some(p=>p.runId===run.id)){
  const original=run.summary+'\n\n'+catalog.assignmentMethod+'\n\n'+candidates.map(d=>`${d.rank}. ${d.name} | $${d.price.toLocaleString()} | ${d.listingUrl} | Assignment: NOT ESTIMABLE`).join('\n');
  s.reports.push({id:run.id,runId:run.id,producerId:'founder-requested-research',producedAt:run.completedAt,retrievedAt:at,title:run.title,original,hash:createHash('sha256').update(original).digest('hex'),recordIds:run.newIds,findings:[],status:'NEEDS_REVIEW',schemaVersion:2,dailyDigest:run,delivery:'SOURCE_BACKFILL'} as any);
 }
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),marker];
 s.history.push({at,action:'SEPT23_INFERENCE_RESEARCH',note:'50 smaller listings added. Assignment probabilities withheld. Existing founder decisions, notes and capital caps preserved; no paid promotion.'});
 return true;
}
