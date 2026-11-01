import {createHash} from 'node:crypto';
import report from '@/data/screening-oct19/report.json';
import prose from '@/data/screening-oct19/prose.json';
import parcels from '@/data/screening-oct19/parcels.json';
import discovery from '@/data/research-oct19/run.json';
import {blankIntelligence,founderProtected} from './intelligence';
import type {Desk} from './model';

export const SCREENING_MARKER='oct19-four-site-screening-v1';
const AT='2026-10-19T16:10:00Z';
export function applyOct19Screening(s:Desk){
 if((s as any).appliedUpdates?.includes(SCREENING_MARKER))return false;
 const ids:string[]=[];
 for(const c of report.sites){
  const r:any=s.records.find(r=>r.id===c.id);
  if(!r)throw new Error('Screening update requires its existing canonical record: '+c.id);
  ids.push(r.id);r.desktopScreeningOct19=c;r.updatedAt=AT;
  const latest=discovery.candidates.find(x=>x.id===c.id);if(latest)r.researchOct19={...latest};
  const protectedRecord=founderProtected(r);
  if(!protectedRecord){r.summary=c.summary;r.categoryReason=c.blocker;r.moneyVerdict='HOLD · $0 new spend. '+c.verdict;r.buyerFit=c.load+'; analyst hypothesis, no validated buyer.';r.thesis=c.summary;}
  if(!r.apn&&c.apns.length)r.apn=c.apns.join('; ');
  if(c.key==='NEWCASTLE'&&!protectedRecord)r.recordType='OFFERED_PORTION';
  if(c.key==='WILLISTON'&&!protectedRecord)r.recordType='ASSEMBLAGE';
  for(const sid of c.source_ids){const src=report.sources.find(x=>x.id===sid)!;const id='SCREEN19-'+sid;if(!r.sources.some((x:any)=>x.id===id))r.sources.push({...src,id,limitation:src.limitation+' Scope: '+src.scope});}
  const sourceIds=c.source_ids.map(x=>'SCREEN19-'+x);
  r.facts.push({label:'October 19 follow-up disposition',value:c.verdict,status:'DESKTOP FINDING',sourceIds},{label:'Founder research priority',value:c.research_priority,status:'RESEARCH ORDER ONLY',sourceIds},{label:'Available MW in follow-up evidence',value:'Unknown (null); no subject issuer allocation recovered',status:'NOT DOCUMENTED',sourceIds});
  r.sections.unshift({title:'October 19 follow-up screening',body:c.summary+' '+c.blocker+' Next: '+c.next_test,sourceIds});
  r.checks.push(...c.gates.map(g=>({id:'screen19-'+g.id,topic:g.name,status:g.status==='ADVERSE_HISTORY_HOLD'?'BLOCKED':'UNKNOWN',result:g.reason,scope:'Founder-requested offered land and load hypothesis; full proof incomplete',checkedAt:'2026-10-19',coverageNote:'See four-site PDF and source ledger. Public records do not substitute for exact-load, title, carrier or professional writing.',sourceIds})));
  const intel=r.intelligence||(r.intelligence=blankIntelligence(r));
  intel.electricity.evidence.push({at:AT,type:'OCT19_FOUR_SITE_SCREEN',availableMW:null,note:c.blocker,sourceIds});
  if(intel.electricity.available_mw==null)intel.electricity.verification='NOT DOCUMENTED · OCTOBER 19 FOLLOW-UP';
  intel.land.conflicts.push(c.blocker);
  if(!protectedRecord){
   intel.land.apns=c.offered_apns.length?c.offered_apns:c.apns;intel.land.advertisedAcreage=c.acres;
   intel.land.kind=c.key==='NEWCASTLE'?'OFFERED_PORTION':c.key==='WILLISTON'?'ASSEMBLAGE':'EXACT_APN';
  }
  // Matched tax geometry is not silently promoted to an offered-tract survey.
  const feature=parcels.features.find((f:any)=>f.properties.apn===c.geometry_apn);
  if(!r.geometry&&feature){r.geometry=feature.geometry;r.geometrySource='Published tax/GIS polygon · '+(feature.properties as any).geometry_as_of+' · offered boundary not surveyed';(r as any).geometryRetrievedAt='2026-10-19';}
  if(c.key==='NEWCASTLE'&&r.geometry){r.location=null;r.geometrySource='Indiana 2025 tax parcel layer, loaded August 14, 2025; offered 44.35-acre split unresolved';}
  if(!protectedRecord&&r.geometry)r.mapVisible=true;
  if(!protectedRecord)r.actions.unshift({id:'screen19-'+r.id,recordId:r.id,order:c.key==='ROOKS'?1:c.key==='NEWCASTLE'?2:c.key==='DILLON'?3:4,title:c.key==='WILLISTON'?'Check for a written cure before more pursuit':'Obtain the decisive existing documents',contact:c.contact,channel:'Prepared document request · no message sent',question:c.next_test,decision:c.blocker,costEstimate:'$0 request · no application, fee or contract authorized',approvalRequired:true,done:false});
  r.history.push({at:AT,action:'OCT19_FOLLOWUP_SCREENING',note:c.verdict+'. Founder category, notes, portfolio, capacity assertions and capital decisions preserved.',sourceDate:'2026-10-19',runId:report.id});
 }
 // Explicit founder stop: preserve the archive while removing pending screening work.
 const stopped:any=s.records.find(r=>r.id==='ga-gordon-048007');
 if(stopped){
  const cancelled=[...stopped.actions.filter((a:any)=>!a.done),...s.tasks.filter(a=>a.recordId===stopped.id&&!a.done)];
  stopped.cancelledScreeningActions=[...(stopped.cancelledScreeningActions||[]),...cancelled.map(a=>({...a,cancelledAt:AT,cancelledReason:'Founder stopped Adairsville screening on October 19, 2026'}))];
  stopped.actions=stopped.actions.filter((a:any)=>a.done);s.tasks=s.tasks.filter(a=>a.recordId!==stopped.id||a.done);
  stopped.screeningControl={status:'STOPPED',at:AT,reason:'Explicit founder instruction',resumeRequiresFounderInstruction:true};
  stopped.workflow_stage='SCREENING_STOPPED';
  stopped.sections.unshift({title:'Screening stopped · October 19',body:'Founder instructed: stop screening the Adairsville site. Pending screening actions were cancelled and retained in history; prior research and decisions are preserved. No new Adairsville research was conducted in this pass.',sourceIds:[]});
  stopped.history.push({at:AT,action:'FOUNDER_STOP_SCREENING',note:'Adairsville screening stopped. Historical dossier retained.',cancelledActionIds:cancelled.map(a=>a.id)});
 }
 if(!s.reports.some(r=>r.id===report.id))s.reports.push({id:report.id,runId:report.id,title:report.title,producerId:'founder-requested-research',producedAt:AT,retrievedAt:AT,original:prose.markdown,hash:createHash('sha256').update(prose.markdown).digest('hex'),recordIds:ids,findings:report.sites.map(c=>({recordId:c.id,text:c.verdict+': '+c.blocker,sourceUrl:c.listing_url,sourceDate:'2026-10-19'})),status:'NEEDS_REVIEW',schemaVersion:2});
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),SCREENING_MARKER];
 s.history.push({at:AT,action:'OCT19_FOLLOWUP_PUBLISHED',note:'Dillon continued; New Castle and Williston screened; Rooks added at equal founder-requested research priority; Adairsville screening stopped. No spending or outreach. Hinds focus, budgets, automations and founder categories preserved.'});
 return true;
}
