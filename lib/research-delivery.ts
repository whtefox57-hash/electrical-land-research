import {parseDailyDigest} from './daily-digest';
import {parseEntities,applyEntities} from './research-upsert';
import {readDesk,saveDesk,digest} from './store';
import {validateDesk} from './model';
async function commitReport(input:any){
 const entities=parseEntities(input);
 const str=(v:any,name:string,max=250000)=>{if(typeof v!=='string'||!v.trim()||v.length>max)throw Error('Invalid '+name);return v.trim()};
 const p={...entities,dailyDigest:parseDailyDigest(input.dailyDigest),schemaVersion:2,producerId:str(input.producerId,'producerId',200),runId:str(input.runId,'runId',200),producedAt:str(input.producedAt,'producedAt',100),title:str(input.title,'title',300),original:str(input.original,'original'),summary:typeof input.summary==='string'?input.summary.slice(0,4000):'',recordIds:input.recordIds??[],findings:input.findings??[],sourceCoverage:input.sourceCoverage??[],sourceErrors:input.sourceErrors??[]};
 if(!Number.isFinite(Date.parse(p.producedAt)))throw Error('producedAt must be an ISO date');
 if(!Array.isArray(p.recordIds)||p.recordIds.some((id:any)=>typeof id!=='string')||!Array.isArray(p.findings)||!Array.isArray(p.sourceCoverage)||!Array.isArray(p.sourceErrors))throw Error('Invalid report arrays');
 if(p.findings.length>300||p.recordIds.length>200)throw Error('Report exceeds item limit');
 const hash=await digest(p.original);const payloadHash=await digest(JSON.stringify(p));
 for(let attempt=0;attempt<4;attempt++){
  const {data:s,version}=await readDesk();
  if(!s.automations.some(a=>a.id===p.producerId))throw Error('Unknown project producer ID');

  for(const f of p.findings)if(typeof f.text!=='string'||f.text.length>20000||(f.recordId&&!p.recordIds.includes(f.recordId)))throw Error('Invalid finding or record link');
  const old=s.reports.find(r=>r.producerId===p.producerId&&r.runId===p.runId);
  if(old){if((old as any).payloadHash?(old as any).payloadHash!==payloadHash:old.hash!==hash)throw Error('CONFLICT: Same run ID already has different content. Use a new correction run ID.');return {received:true,duplicate:true,reportId:old.id,runId:old.runId,hash:old.hash,receivedAt:old.retrievedAt,version,url:'/?view=inbox&report='+old.id};}
  const at=new Date().toISOString(),id=crypto.randomUUID();
  const touched=applyEntities(s,p,at);
  p.recordIds=Array.from(new Set([...p.recordIds,...touched]));
  if(p.dailyDigest&&[...p.dailyDigest.newIds,...p.dailyDigest.updatedIds].some(id=>!s.records.some(r=>r.id===id)))throw Error('Daily digest references unknown record');
  if(p.recordIds.some((id:string)=>!s.records.some(r=>r.id===id)))throw Error("Unknown record ID");
  s.reports.push({...p,id,hash,payloadHash,retrievedAt:at,status:'NEEDS_REVIEW',delivery:'MCP_AUTHENTICATED'} as any);
  for(const recordId of p.recordIds)s.records.find(r=>r.id===recordId)!.history.push({at,action:'REPORT_RECEIVED',reportId:id,note:p.title+' — received directly; founder decisions retained.'});
  s.history.push({at,action:'AUTOMATION_REPORT_RECEIVED',reportId:id,producerId:p.producerId,runId:p.runId});
  validateDesk(s);
  try{const next=await saveDesk(s,version);return {received:true,duplicate:false,reportId:id,runId:p.runId,hash,receivedAt:at,version:next,url:'/?view=inbox&report='+id}}catch(e){if(!(e as Error).message.startsWith('CONFLICT')||attempt===3)throw e;}
 }
 throw Error('Delivery could not be committed');
}
export async function deliveryStatus(producerId?:string,runId?:string){const {data:s,version}=await readDesk();const reports=s.reports.filter(p=>(!producerId||p.producerId===producerId)&&(!runId||p.runId===runId));return {version,receivedReports:reports.length,reports:reports.slice().sort((a,b)=>b.retrievedAt.localeCompare(a.retrievedAt)).slice(0,20).map(p=>({id:p.id,producerId:p.producerId,runId:p.runId,title:p.title,producedAt:p.producedAt,receivedAt:p.retrievedAt,hash:p.hash,url:'/?view=inbox&report='+p.id}))}}

export async function deliverReport(input:any){
 try{const receipt=await commitReport(input);const {data:s}=await readDesk();const stored=s.reports.find(p=>p.id===receipt.reportId&&p.producerId===input.producerId&&p.runId===input.runId&&p.hash===receipt.hash);if(!stored)throw Error('Readback verification failed');return {...receipt,syncStatus:'SYNCED',readbackVerified:true,verifiedAt:new Date().toISOString()};}
 catch(e){const message=(e as Error).message;let preserved=false;for(let attempt=0;attempt<3;attempt++){try{const {data:s,version}=await readDesk();if(!s.automations.some(a=>a.id===input?.producerId))break;const key=await digest(JSON.stringify(input));s.syncFailures??=[];if(!s.syncFailures.some(f=>f.id===key)){s.syncFailures.push({id:key,status:'SYNC_FAILED',at:new Date().toISOString(),producerId:input.producerId,runId:input.runId||'UNKNOWN',error:message,payload:input});await saveDesk(s,version);}preserved=true;break;}catch{}}
 throw Error('SYNC_FAILED: '+message+(preserved?' · Original payload retained in private failure history.':' · Storage retention could not be verified; producer must retain original report.'));}
}
