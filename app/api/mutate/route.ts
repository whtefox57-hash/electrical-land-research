import {parseDailyDigest} from '@/lib/daily-digest';
import {importBuyerWatch} from '@/lib/buyer-watch-import';
import {authorize} from '@/lib/auth';import {readDesk,saveDesk,digest} from '@/lib/store';import {changeTier,validateDesk} from '@/lib/model';
export const dynamic='force-dynamic';
export async function POST(req:Request){const denied=authorize(req,true);if(denied)return denied;
 try{
  const raw=await req.text();if(raw.length>4000000)return Response.json({error:'Import exceeds 4 MB.'},{status:413});
  const b=JSON.parse(raw);const {data:s,version}=await readDesk();if(b.expectedVersion!==version)return Response.json({error:'Another session saved first. Refresh before retrying; your draft is still on screen.'},{status:409});
  const at=new Date().toISOString();const r=s.records.find(x=>x.id===b.recordId);let result='Saved';
  const text=(x:any,max=20000)=>{if(typeof x!=='string'||!x.trim()||x.length>max)throw Error('Enter valid text within the length limit.');return x.trim()};
  switch(b.action){
   case 'note':if(!r)throw Error('Record not found');r.noteEntries.push({id:crypto.randomUUID(),at,text:text(b.text)});r.history.push({at,action:'NOTE_ADDED',note:'Private founder note added.'});break;
   case 'task':{const t=[...s.tasks,...s.records.flatMap(x=>x.actions)].find(t=>t.id===b.id);if(!t)throw Error('Task not found');t.done=!!b.done;break;}
   case 'addTask':if(b.recordId&&!r)throw Error('Record not found');s.tasks.push({id:crypto.randomUUID(),recordId:r?.id,order:s.tasks.length+1,title:text(b.title,300),contact:'Founder',channel:'Internal task',question:text(b.title,300),decision:b.decision||'Founder task',costEstimate:'No spend authorized',approvalRequired:false,done:false,dueDate:b.dueDate||''});break;
   case 'triage':if(!r)throw Error('Record not found');if(!['PRIORITY','WATCH','REJECTED'].includes(b.tier))throw Error('Invalid category');if(b.screen&&b.tier==='PRIORITY'){for(const k of ['traceableAsset','plausibleEconomics','powerSignal','buyerFit','noSupportedFatal','nextTest','alternateUse'])if(typeof b.screen[k]!=='boolean')throw Error('Incomplete initial screen');r.initialScreen=b.screen;}changeTier(r,b.tier,text(b.reason),b.evidence||'',at);s.decisions.push({id:crypto.randomUUID(),recordId:r.id,at,type:'CATEGORY',reason:b.reason,evidence:b.evidence||'',tier:b.tier});break;
   case 'stage':if(!r||r.priority_tier!=='PRIORITY')throw Error('Deep GIS workflow applies to Priority records only.');if(!['GIS_QUEUED','GIS_IN_PROGRESS','GIS_REVIEWED','GIS_BLOCKED','HUMAN_VERIFICATION_NEEDED'].includes(b.stage))throw Error('Invalid stage');r.workflow_stage=b.stage;r.history.push({at,action:'GIS_STAGE',note:text(b.reason),stage:b.stage});break;
   case 'relationship':s.relationships.push({id:crypto.randomUUID(),name:text(b.name,200),type:text(b.type,100),contact:b.contact||'Unknown',note:b.note||'',recordIds:r?[r.id]:[],source:'Founder entry',at});break;
   case 'expense':{const amount=Number(b.amount);if(!Number.isFinite(amount)||amount<=0||amount>1000000)throw Error('Enter a positive amount');if(b.recordId&&!r)throw Error('Record not found');if(!['LEARNING','SOFT_CONTROL'].includes(b.kind))throw Error('Invalid expense type');s.expenses.push({id:crypto.randomUUID(),at,amount,kind:b.kind,recordId:r?.id||null,description:text(b.description,500),authorization:'Founder recorded historical expense; no payment initiated'});break;}
   case 'report':{
    if(b.report?.schema_version==='LBW.manual-intake.v1'){
     const receipt=importBuyerWatch(s,b.report);
     const next=receipt.changed?await saveDesk(s,version):version;
     const readback=await readDesk();
     if(!readback.data.reports.some(p=>p.id===receipt.reportId))throw Error('Import readback failed. Refresh and retry with the same file.');
     return Response.json({version:next,result:receipt.duplicate?'Already imported. No duplicates created.':'Buyer Watch saved and verified: '+receipt.recordIds.length+' linked offerings.',...receipt,readbackVerified:true});
    }
    const p=b.report;if(!p||p.schemaVersion!==1||!Array.isArray(p.recordIds)||!Array.isArray(p.findings)||p.recordIds.some((id:string)=>!s.records.some(x=>x.id===id)))throw Error('Report requires schemaVersion 1, known recordIds, and findings.');
    for(const f of p.findings)if(!p.recordIds.includes(f.recordId)||typeof f.text!=='string')throw Error('Finding must reference a linked record.');
    const original=text(p.original,250000),producerId=text(p.producerId,200),runId=text(p.runId,200);const hash=await digest(original);
    const existing=s.reports.find(x=>x.producerId===producerId&&x.runId===runId);
    if(existing){if(existing.hash!==hash)throw Error('CONFLICT: This run ID already has a different original report. Supply a new run ID for a correction.');return Response.json({version,result:'Already imported. No duplicates created.',duplicate:true});}
    const dailyDigest=parseDailyDigest(p.dailyDigest);if(dailyDigest&&[...dailyDigest.newIds,...dailyDigest.updatedIds].some(id=>!s.records.some(r=>r.id===id)))throw Error('Daily digest references unknown record');
    const report={dailyDigest,id:crypto.randomUUID(),producerId,runId,producedAt:text(p.producedAt,100),retrievedAt:at,title:text(p.title,300),original,hash,recordIds:p.recordIds,findings:p.findings,status:'NEEDS_REVIEW',schemaVersion:1};s.reports.push(report);
    for(const id of p.recordIds){const target=s.records.find(x=>x.id===id)!;target.history.push({at,action:'REPORT_RECEIVED',reportId:report.id,note:report.title+' — pending founder review; category and capital decisions preserved.'});}result='Report saved for review';break;
   }
   case 'reviewReport':{const p=s.reports.find(x=>x.id===b.id);if(!p)throw Error('Report not found');p.status='REVIEWED';s.history.push({at,action:'REPORT_REVIEWED',reportId:p.id,note:text(b.reason)});break;}
   case 'restore':{
    const next=b.workspace;validateDesk(next);if(s.records.some(x=>!next.records.some((y:any)=>y.id===x.id)))throw Error('Restore cannot remove existing records. Archive records instead.');
    for(const old of s.records){const n=next.records.find((x:any)=>x.id===old.id);if(old.priority_tier==='REJECTED'&&n?.priority_tier!=='REJECTED')throw Error('Restore cannot reopen archived records. Use the evidence-backed triage action.');}
    if(s.reports.some(p=>!next.reports.some((q:any)=>q.id===p.id)))throw Error('Restore cannot discard original reports.');
    if(s.documents.some(d=>!next.documents.some((n:any)=>n.id===d.id)))throw Error('Restore cannot remove source documents.');
    next.documents=s.documents;next.automations=s.automations;next.automationVerification=s.automationVerification;next.methodology=s.methodology;next.migration=s.migration;
    next.history.push({at,action:'WORKSPACE_RESTORE',note:text(b.reason),previousVersion:version});const v=await saveDesk(next,version);return Response.json({version:v,result:'Workspace restored; previous version retained as backup'});
   }
   default:throw Error('Unsupported action');
  }
  s.history.push({at,action:b.action,recordId:b.recordId||null});validateDesk(s);const v=await saveDesk(s,version);return Response.json({version:v,result});
 }catch(e){const message=(e as Error).message;return Response.json({error:message},{status:message.startsWith('CONFLICT')?409:400});}
}
