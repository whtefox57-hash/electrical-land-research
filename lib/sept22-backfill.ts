import {createHash} from 'node:crypto';
import catalog from '@/data/research-sept22/research.json';
import candidates from '@/data/research-sept22/new-candidates.json';
import {newResearchRecords} from './sept20-backfill';
import type {Desk} from './model';

export function additionalResearchRecords(){
 return newResearchRecords({asOf:catalog.asOf,candidates},'September 22 additional 50').map((r:any)=>{
  // The source catalog owns the detailed audit; keep canonical workspace rows compact.
  const {stateScreen,score,...card}=r.dealCard;
  const {factors,...scoreSummary}=score;
  r.dealCard={...card,score:scoreSummary};
  r.history[0].note='Additional priced research offering; no paid-control promotion. Conditional assignment judgment is not a measured probability.';
  return r;
 });
}

export function applySept22(s:Desk){
 const marker='sept22-additional-50-v1';
 if((s as any).appliedUpdates?.includes(marker))return false;
 const at=new Date().toISOString();
 for(const r of additionalResearchRecords())if(!s.records.some(old=>old.id===r.id))s.records.push(r);
 const run=catalog.runs[0];
 if(!s.reports.some(p=>p.runId===run.id)){
  const original=run.summary+'\n\n'+catalog.assignmentMethod+'\n\n'+candidates.map(d=>`${d.rank}. ${d.name} | ${d.state} | $${d.price.toLocaleString()} | ${d.listingUrl}\nWorking assignment estimate ${d.assignmentEstimate.percent}% (${d.assignmentEstimate.low}–${d.assignmentEstimate.high}%), conditional; very low confidence.\n${d.nextTest}`).join('\n\n');
  s.reports.push({id:run.id,runId:run.id,producerId:'6a9661495ebc8191841ea60a5fbfab06',producedAt:run.completedAt,retrievedAt:at,title:run.title,original,hash:createHash('sha256').update(original).digest('hex'),recordIds:run.newIds,findings:[],status:'NEEDS_REVIEW',schemaVersion:2,dailyDigest:run,delivery:'SOURCE_BACKFILL'} as any);
 }
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),marker];
 s.history.push({at,action:'SEPT22_ADDITIONAL_RESEARCH',note:'50 distinct priced offerings added with conditional assignment judgments, contacts and sample option terms. Original research, founder decisions and capital limits preserved.'});
 return true;
}
