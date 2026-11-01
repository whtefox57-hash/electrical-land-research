import {Miniflare,Log} from 'miniflare';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const mf=new Miniflare({modules:true,scriptPath:'dist/server/index.js',modulesRules:[{type:'ESModule',include:['**/*.js','**/*.mjs'],fallthrough:true}],compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB'],r2Buckets:['BUCKET'],assets:{directory:'dist/client',binding:'ASSETS',routerConfig:{has_user_worker:true,invoke_user_worker_ahead_of_assets:true}},log:new Log(0)});
const checks=[];
const request=(path,body)=>mf.dispatchFetch('https://desk.example'+path,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined});
try{
 const db=await mf.getD1Database('DB');
 for(const s of (await fs.readFile('drizzle/0003_smart_secret_warriors.sql','utf8')).split('--> statement-breakpoint').map(x=>x.trim()).filter(Boolean))await db.prepare(s).run();
 const workflow=await (await request('/api/data-centers/history?format=workflow')).json();assert.equal(workflow.inventory_count,4257);checks.push('Saved research workflow available to owner-authorized service calls');
 const initial=await (await request('/api/data-centers/history?format=progress')).json();assert.equal(initial.summary.reviewed,0);assert.equal(initial.summary.unstarted,4257);checks.push('Unresearched entries are not counted as reviewed');
 const queue=await (await request('/api/data-centers/history?next=1&limit=2')).json();assert.equal(queue.rows.length,2);const r=queue.rows[0];
 const body={run_id:'qa-dc-history-reserve',records:[{kind:'case',id:'dc-history-'+r.id,expected_version:0,data:{id:'dc-history-'+r.id,record_id:r.id,queue_position:1,facility_name:r.name,state:r.state,review_stage:'IN_PROGRESS',lease:{owner:'qa',expires_at:'2099-01-01T00:00:00Z'},checked_at:null,complete:false}}]};
 const receipt=await (await request('/api/origination',body)).json();assert.equal(receipt.readback_verified,true);
 const next=await (await request('/api/data-centers/history?next=1&limit=1')).json();assert.notEqual(next.rows[0].id,r.id);checks.push('Active reservations prevent duplicate investigations');
 const detail=await (await request('/api/data-centers/history?id='+encodeURIComponent(r.id))).json();assert.equal(detail.version,1);assert.equal(detail.research.review_stage,'IN_PROGRESS');
 const update={run_id:'qa-dc-history-review',records:[{...body.records[0],expected_version:1,data:{...body.records[0].data,review_stage:'REVIEWED_PARTIAL',checked_at:'2026-10-31T03:00:00Z',completion:{identity:true,parcel:false,original_transaction:false,original_listing:false,approval_path:false},summary:'QA isolated example; gaps remain',search_log:[{query_or_locator:'QA',result:'no_relevant_result'}]}}]};
 assert.equal((await (await request('/api/origination',update)).json()).readback_verified,true);
 const progress=await (await request('/api/data-centers/history?format=progress')).json();assert.equal(progress.summary.reviewed,1);assert.equal(progress.summary.complete,0);checks.push('Partial research remains incomplete and reads back from durable storage');
 assert.equal((await request('/api/origination',{...body,run_id:'qa-stale'})).status,409);checks.push('Stale writes cannot replace saved research');
 const missing=await request('/api/data-centers/history?id=no-such-id');assert.equal(missing.status,404);checks.push('Unknown inventory IDs are rejected');
 const cross=await mf.dispatchFetch('https://desk.example/api/data-centers/history',{headers:{Origin:'https://evil.example'}});assert.equal(cross.status,403);checks.push('Cross-origin browser requests rejected');
 const result={passed:true,scope:'Isolated production Worker; Sites owner-only gateway remains the authorization boundary',checks};await fs.writeFile('qa/data-center-history-acceptance.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}finally{await mf.dispose()}
