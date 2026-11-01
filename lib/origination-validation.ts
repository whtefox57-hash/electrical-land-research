export const kinds = ['listing','county','case','source'] as const;
export function canonicalRecordKey(kind:string,id:string){
 const prefix=kind+':';let bare=id;
 while(bare.startsWith(prefix))bare=bare.slice(prefix.length);
 if(!bare||bare.length>180)throw Error('A record needs a nonempty stable ID of at most 180 characters.');
 return prefix+bare;
}
// Older callers supplied the qualified registry key as the POST id. Preserve
// those stored rows and history while accepting either format from now on.
export function registryKeyAliases(kind:string,id:string){
 const prefix=kind+':',aliases:string[]=[];let key=canonicalRecordKey(kind,id);
 while(key.length<=180+prefix.length){aliases.push(key);key=prefix+key;}
 return aliases;
}
export function normalizeRecord(input:any,canonicalKeys=true){
 if(!input||!kinds.includes(input.kind)||typeof input.id!=='string'||!/^[A-Za-z0-9_.:-]{1,180}$/.test(input.id))throw Error('Each record needs a supported kind and stable id.');
 const data=input.data;
 if(!data||typeof data!=='object'||Array.isArray(data))throw Error('Record data must be an object.');
 if(JSON.stringify(data).length>50000)throw Error('Record exceeds 50 KB.');
 if(data.state&&!/^[A-Z]{2}$/.test(data.state))throw Error('Use a two-letter state code.');
 if(input.kind==='listing'){
  if(!['REJECT','HOLD','FURTHER_INVESTIGATION'].includes(data.disposition)||!data.decision_reason||!data.next_action)throw Error('Every listing needs a disposition, reason and next action.');
  if(!data.source_listing_id||!data.url||!/^https?:\/\//.test(data.url))throw Error('Every listing needs its source ID and canonical URL.');
  if(data.available_mw!=null&&!(data.power_confirmation?.evidence_level==='V4'&&data.power_confirmation?.document_url&&data.power_confirmation?.exact_parcel&&data.power_confirmation?.load_scope))throw Error('Non-null available MW requires current exact-parcel and load-scoped utility evidence.');
  if(data.review_stage==='INDEX_ONLY'&&data.disposition!=='HOLD')throw Error('An index-only record must remain HOLD pending detail review.');
  if(!data.residential_screen||!data.approval_history_status)throw Error('Residential and approval-history status are mandatory; UNKNOWN is valid.');
 }
 if(input.kind==='county'&&data.complete===true&&!(data.declared_source_universe?.length&&data.counts_reconciled===true&&data.individual_review_complete===true&&data.snapshot_at&&data.source_evidence?.length))throw Error('County completion requires a declared source universe, snapshot, reconciliation and individual review evidence.');
 const version=input.expected_version??0;
 if(!Number.isInteger(version)||version<0)throw Error('expected_version must be a nonnegative integer.');
 const id=canonicalKeys?canonicalRecordKey(input.kind,input.id):input.kind+':'+input.id;
 if(canonicalKeys&&data.id!=null&&canonicalRecordKey(input.kind,String(data.id))!==id)throw Error('Record id must match data.id.');
 return {id,kind:input.kind,state:data.state||data.USPS||null,county:data.county_fips||data.GEOID||data.county||null,disposition:data.disposition||null,stage:data.review_stage||data.inventory_status||null,data,expected_version:version};
}
export function normalizeRun(input:any,canonicalKeys=true){
 if(typeof input?.run_id!=='string'||!/^[A-Za-z0-9_.:-]{1,180}$/.test(input.run_id))throw Error('Stable run_id required; reuse unchanged payload for retries.');
 if(!Array.isArray(input.records)||input.records.length>100)throw Error('Submit at most 100 records per batch.');
 const records=input.records.map((r:any)=>normalizeRecord(r,canonicalKeys));
 if(new Set(records.map((x:any)=>x.id)).size!==records.length)throw Error('Duplicate record IDs in batch.');
 return {run_id:input.run_id,summary:input.summary||'',producer_id:input.producer_id||'manual-authorized',coverage:input.coverage||{},records};
}
