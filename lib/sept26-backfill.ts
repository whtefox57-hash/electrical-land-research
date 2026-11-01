import {createHash} from 'node:crypto';
import {sept26Candidates,sept26Run} from './sept26-catalog';
import {newResearchRecords} from './sept20-backfill';
import type {Desk} from './model';

export function applySept26(s:Desk){
 const marker='sept26-listing-50-v1';
 if((s as any).appliedUpdates?.includes(marker))return false;
 const at=new Date().toISOString();
 const ids:string[]=[];
 for(const r of newResearchRecords({asOf:'2026-09-26',candidates:sept26Candidates},'September 26 additional listing research')){
  const existing=s.records.find(old=>old.id===r.id||old.sources.some(src=>src.url===r.sources[0].url));
  if(existing){ids.push(existing.id);continue;}
  r.recordType='UNRESOLVED_LEAD';r.mapVisible=false;
  r.initialScreen={traceableAsset:false,plausibleEconomics:false,powerSignal:false,buyerFit:false,noSupportedFatal:false,nextTest:true,alternateUse:false};
  r.moneyVerdict='HOLD — assignment probability and profit not estimable; no paid control authorized.';
  (r as any).dealCard={id:r.id,batch:'listing-50-sept26'};
  s.records.push(r);ids.push(r.id);
 }
 const original=sept26Run.summary+'\n\n'+sept26Candidates.map(d=>`## ${d.rank}. ${d.name}\n${d.state} · $${d.price.toLocaleString()} · ${d.acres} gross acres\n\n[Listing](${d.listingUrl})\n\nMarketing evidence: ${d.marketingDate} — ${d.marketingDateNote}\n\n${d.why}\n\nFirst test: ${d.nextTest}\n\nAssignment probability: NOT ESTIMABLE.`).join('\n\n')+'\n\n## Exclusions\n'+sept26Run.rejected.map(d=>`${d.name}: ${d.reason}`).join('\n\n');
 if(!s.reports.some(p=>p.runId===sept26Run.id))s.reports.push({id:sept26Run.id,runId:sept26Run.id,producerId:'founder-requested-research',producedAt:sept26Run.completedAt,retrievedAt:at,title:sept26Run.title,original,hash:createHash('sha256').update(original).digest('hex'),recordIds:ids,findings:[],status:'NEEDS_REVIEW',schemaVersion:2,dailyDigest:{...sept26Run,newIds:ids},delivery:'SOURCE_BACKFILL'} as any);
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),marker];
 s.history.push({at,action:'SEPT26_LISTING_RESEARCH',note:'50 listing-screened leads published, deduplicated by ID and listing URL. Existing decisions, notes and capital limits preserved. No probability, paid-control clearance or broker-confirmed availability implied.'});
 return true;
}
