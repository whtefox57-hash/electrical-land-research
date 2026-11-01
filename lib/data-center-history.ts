import queue from '@/data/data-center-history-queue.json';
import {dataset} from './data-center-registry';
import {db} from './store';

export const historyQueue=queue;
const inventory=new Map(dataset.records.map(r=>[r.id,r]));
const positions=new Map(queue.record_ids.map((id,i)=>[id,i+1]));
export const historyStages={UNSTARTED:'Not started',IN_PROGRESS:'In progress',REVIEWED_PARTIAL:'Searched · gaps remain',HISTORY_ESTABLISHED:'History established',IDENTITY_UNRESOLVED:'Identity unresolved',DUPLICATE_LINKED:'Related inventory entry',NOT_A_DATA_CENTER:'Not a verified data center'};
export async function historyProgress(){
 const r=await db().prepare("SELECT id,version,updated_at,json_extract(data,'$.record_id') record_id,json_extract(data,'$.queue_position') queue_position,json_extract(data,'$.review_stage') review_stage,json_extract(data,'$.checked_at') checked_at,json_extract(data,'$.complete') complete,json_extract(data,'$.lease.expires_at') lease_expires_at,json_extract(data,'$.completion.parcel') parcel,json_extract(data,'$.completion.original_transaction') original_transaction,json_extract(data,'$.completion.original_listing') original_listing FROM origination_records WHERE kind='case' AND id LIKE 'case:dc-history-%' ORDER BY CAST(json_extract(data,'$.queue_position') AS INTEGER)").all();
 const rows=r.results.filter((x:any)=>inventory.has(x.record_id));
 const reviewed=rows.filter((x:any)=>x.checked_at&&x.review_stage!=='IN_PROGRESS'&&x.review_stage!=='UNSTARTED');
 const known=new Map(rows.map((x:any)=>[x.record_id,x]));
 const eligible=(id:string)=>{const p:any=known.get(id);return !p||p.review_stage==='UNSTARTED'||(p.review_stage==='IN_PROGRESS'&&p.lease_expires_at&&Date.parse(p.lease_expires_at)<Date.now())};
 const next=queue.record_ids.find(eligible);
 return {rows,summary:{inventory_records:queue.record_count,started:rows.length,reviewed:reviewed.length,complete:rows.filter((x:any)=>x.complete===1).length,in_progress:rows.filter((x:any)=>x.review_stage==='IN_PROGRESS').length,unstarted:queue.record_count-rows.length,with_parcel:reviewed.filter((x:any)=>x.parcel===1).length,with_original_transaction:reviewed.filter((x:any)=>x.original_transaction===1).length,with_original_listing:reviewed.filter((x:any)=>x.original_listing===1).length,identity_unresolved:rows.filter((x:any)=>x.review_stage==='IDENTITY_UNRESOLVED').length,duplicate_linked:rows.filter((x:any)=>x.review_stage==='DUPLICATE_LINKED').length,next_record_id:next||null,next_queue_position:next?positions.get(next):null,national_complete:false},eligible};
}
export async function historyDetail(recordId:string){
 if(!inventory.has(recordId))return null;
 const row=await db().prepare("SELECT id,version,updated_at,data FROM origination_records WHERE kind='case' AND id=?").bind('case:dc-history-'+recordId).first();
 return {record_id:recordId,queue_position:positions.get(recordId),registry_id:row?.id||null,version:row?.version||0,updated_at:row?.updated_at||null,research:row?JSON.parse(row.data):null};
}
export function queueRecords(ids:string[]){return ids.map(id=>{const r=inventory.get(id)!;return {queue_position:positions.get(id),...r,inventory_sources:r.source_ids.map(k=>dataset.sources[k]).filter(Boolean)}})}
