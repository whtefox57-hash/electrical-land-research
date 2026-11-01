import {db,digest} from './store';
import {normalizeRun,registryKeyAliases} from './origination-validation';
export async function importOrigination(input:any){
 const normalized=normalizeRun(input),hash=await digest(JSON.stringify(normalized)),d=db();
 const old=await d.prepare('SELECT hash,data FROM origination_runs WHERE id=?').bind(normalized.run_id).first();
 if(old){
  // Keep unchanged retries of pre-normalization runs valid, including their
  // original receipt hashes and qualified IDs.
  if(old.hash!==hash&&old.hash!==await digest(JSON.stringify(normalizeRun(input,false))))throw Error('CONFLICT: run_id already contains different data. Use a correction run ID.');
  return {...JSON.parse(old.data),duplicate:true,readback_verified:true};
 }
 const lookups=normalized.records.map((row:any)=>{const aliases=registryKeyAliases(row.kind,row.id);return d.prepare('SELECT id FROM origination_records WHERE id IN ('+aliases.map(()=>'?').join(',')+')').bind(...aliases)});
 const found=lookups.length?await d.batch(lookups):[];
 const resolved=normalized.records.map((row:any,i:number)=>{
  const matches=found[i].results||[];
  if(matches.length>1)throw Error('CONFLICT: Multiple stored keys identify '+row.id+'. Reconcile them before writing.');
  return {...row,id:matches[0]?.id||row.id};
 });
 const at=new Date().toISOString();
 const receipt={run_id:normalized.run_id,hash,record_count:resolved.length,record_ids:resolved.map((r:any)=>r.id),summary:normalized.summary,producer_id:normalized.producer_id,coverage:normalized.coverage,committed_at:at};
 const statements=[];
 for(const row of resolved){
  // Stale versions fail the NOT NULL constraint and roll back the entire batch.
  statements.push(d.prepare('INSERT INTO origination_events(id,run_id,record_id,previous_data,data,created_at) VALUES (?,?,?,(SELECT data FROM origination_records WHERE id=?),CASE WHEN COALESCE((SELECT version FROM origination_records WHERE id=?),0)=? THEN ? ELSE NULL END,?)').bind(normalized.run_id+':'+row.id,normalized.run_id,row.id,row.id,row.id,row.expected_version,JSON.stringify(row.data),at));
  statements.push(d.prepare('INSERT INTO origination_records(id,kind,state,county,disposition,stage,data,version,updated_at) VALUES (?,?,?,?,?,?,?,1,?) ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,state=excluded.state,county=excluded.county,disposition=excluded.disposition,stage=excluded.stage,data=excluded.data,version=origination_records.version+1,updated_at=excluded.updated_at').bind(row.id,row.kind,row.state,row.county,row.disposition,row.stage,JSON.stringify(row.data),at));
 }
 statements.push(d.prepare('INSERT INTO origination_runs(id,hash,data,created_at) VALUES (?,?,?,?)').bind(normalized.run_id,hash,JSON.stringify(receipt),at));
 try{await d.batch(statements)}catch(e){
  const retry=await d.prepare('SELECT hash,data FROM origination_runs WHERE id=?').bind(normalized.run_id).first();
  if(retry?.hash===hash)return {...JSON.parse(retry.data),duplicate:true,readback_verified:true};
  throw Error('Import rolled back. Reload record versions before retrying. '+(e as Error).message);
 }
 const saved=await d.prepare('SELECT hash FROM origination_runs WHERE id=?').bind(normalized.run_id).first();
 if(saved?.hash!==hash)throw Error('Delivery readback failed. Do not advance the source cursor.');
 return {...receipt,duplicate:false,readback_verified:true};
}
export async function queryOrigination(params:URLSearchParams){
 const d=db();
 if(params.get('run_id')){const r=await d.prepare('SELECT data FROM origination_runs WHERE id=?').bind(params.get('run_id')).first();return {run:r?JSON.parse(r.data):null};}
 if(params.get('summary')==='1'){
  const [counts,states,runs,residence,reviews,completed]=await Promise.all([
   d.prepare('SELECT kind,disposition,COUNT(*) AS count FROM origination_records GROUP BY kind,disposition').all(),
   d.prepare("SELECT state,COUNT(*) AS count FROM origination_records WHERE kind='listing' GROUP BY state ORDER BY state").all(),
   d.prepare('SELECT data FROM origination_runs ORDER BY created_at DESC LIMIT 12').all(),
   d.prepare("SELECT COUNT(*) AS count FROM origination_records WHERE kind='listing' AND json_extract(data,'$.residential_screen.nearest_residence_m') IS NOT NULL").first(),
   d.prepare("SELECT stage,COUNT(*) AS count FROM origination_records WHERE kind='listing' GROUP BY stage").all(),
   d.prepare("SELECT COUNT(*) AS count FROM origination_records WHERE kind='county' AND json_extract(data,'$.complete')=1").first(),
  ]);
  return {counts:counts.results,states:states.results,runs:runs.results.map((r:any)=>JSON.parse(r.data)),residence_measured:residence?.count||0,completed_counties:completed?.count||0,review_stages:reviews.results,national_listing_denominator:null,national_complete:false};
 }
 const clauses=['kind=?'];const args:any[]=[params.get('kind')||'listing'];
 for(const field of ['state','disposition'])if(params.get(field)){clauses.push(field+'=?');args.push(params.get(field));}
 if(params.get('id')){const aliases=registryKeyAliases(params.get('kind')||'listing',params.get('id')!);clauses.push('id IN ('+aliases.map(()=>'?').join(',')+')');args.push(...aliases);}
 if(params.get('q')){clauses.push('data LIKE ?');args.push('%'+params.get('q')?.slice(0,200)+'%');}
 const limit=Math.min(200,Math.max(1,Math.floor(Number(params.get('limit'))||50))),offset=Math.max(0,Math.floor(Number(params.get('offset'))||0));
 const where=clauses.join(' AND ');
 const [n,rows]=await Promise.all([d.prepare('SELECT COUNT(*) AS count FROM origination_records WHERE '+where).bind(...args).first(),d.prepare('SELECT id,version,data,updated_at FROM origination_records WHERE '+where+" ORDER BY CASE disposition WHEN 'FURTHER_INVESTIGATION' THEN 0 WHEN 'HOLD' THEN 1 ELSE 2 END,state,id LIMIT ? OFFSET ?").bind(...args,limit,offset).all()]);
 return {total:n?.count||0,offset,limit,rows:rows.results.map((r:any)=>({registry_id:r.id,version:r.version,updated_at:r.updated_at,...JSON.parse(r.data)}))};
}
