import test, {beforeEach,afterEach} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import ts from 'typescript';

// Isolated in-memory database and fabricated fixtures. Never write to the Site.
let database;
const realFetch=globalThis.fetch;
const wrap=(sql,args=[])=>({bind(...values){return wrap(sql,values)},async first(){return database.prepare(sql).get(...args)||null},async all(){return {results:database.prepare(sql).all(...args)}},async run(){const result=database.prepare(sql).run(...args);return {meta:{changes:Number(result.changes)}}}});
const adapter={prepare:sql=>wrap(sql),async batch(statements){database.exec('BEGIN');try{const result=[];for(const s of statements)result.push(await s.run());database.exec('COMMIT');return result}catch(e){database.exec('ROLLBACK');throw e}}};
globalThis.__atlasTestDb=adapter;
globalThis.__atlasTestDigest=async s=>createHash('sha256').update(s).digest('hex');
const source=(await readFile(new URL('../lib/atlas-store.ts',import.meta.url),'utf8')).replace("import {db,digest} from './store';","const db=()=>globalThis.__atlasTestDb; const digest=globalThis.__atlasTestDigest;").replace("'./atlas-rules.mjs'",JSON.stringify(new URL('../lib/atlas-rules.mjs',import.meta.url).href));
const compiled=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}}).outputText;
const {atlasImport,atlasQuery,atlasRefresh,atlasReconcile}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const geometry={type:'Polygon',coordinates:[[[-110,31],[-109.999,31],[-109.999,31.001],[-110,31.001],[-110,31]]]};
const parcel=(id='fixture')=>({id,apn:'000123',county_fips:'04003',county:'Fixture',state:'AZ',source_id:'test',source_url:'https://example.invalid/official',source_date:new Date().toISOString(),retrieved_at:new Date().toISOString(),geometry,expected_version:0});
beforeEach(async()=>{database=new DatabaseSync(':memory:');const dir=new URL('../drizzle/',import.meta.url);for(const name of (await readdir(dir)).filter(n=>n.endsWith('.sql')).sort())database.exec(await readFile(new URL(name,dir),'utf8'));});
afterEach(()=>{database.close();globalThis.fetch=realFetch;});

test('import retry is idempotent and stale batch rolls back every row',async()=>{
 const payload={run_id:'first',parcels:[parcel()]};await atlasImport(payload);assert.equal((await atlasImport(payload)).duplicate,true);
 await assert.rejects(atlasImport({...payload,parcels:[{...payload.parcels[0],apn:'changed'}]}),/Run ID conflict/);
 await assert.rejects(atlasImport({run_id:'stale',parcels:[parcel('would-be-new'),parcel()]}),/rolled back/);
 assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_parcels').get().n,1);assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_runs').get().n,1);
 const p=await atlasQuery(new URLSearchParams('view=parcel&id=fixture'));assert.equal(p.parcel.color,'GRAY');assert.equal(p.parcel.available_mw,null);
});

test('lost checkpoint lease rolls back data and cursor together',async()=>{
 await assert.rejects(atlasImport({run_id:'lost',parcels:[parcel()],job_checkpoint:{job_id:'missing',lease_token:'expired',state:'READY',data:{cursor:1}}}),/rolled back/);
 assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_parcels').get().n,0);
});

test('export with unknown source rights excludes geometry and attributes',async()=>{
 await atlasImport({run_id:'rights',parcels:[parcel(),{...parcel('allowed'),export_allowed:true}]});
 const result=await atlasQuery(new URLSearchParams('view=export'));assert.equal(result.features.length,1);assert.equal(result.features[0].id,'allowed');assert.equal(result.export_excluded,1);
});

test('source outage retains a frozen ID manifest and resumes without duplicate parcels',async()=>{
 const data={county_fips:'04003',county:'Fixture',state:'AZ',source_id:'test',adapter:{url:'https://example.gov/FeatureServer/0',access:'PUBLIC_NO_KEY',where:'OBJECTID <= 13',apn_field:'apn',oid_field:'OBJECTID',acres_field:'acres'}};
 await atlasImport({run_id:'partition',entities:[{kind:'partition',id:'test-partition',expected_version:0,data}]});
 let failPage=false;let countCalls=0;
 globalThis.fetch=async url=>{const p=new URL(url).searchParams;if(p.has('returnCountOnly')){countCalls++;return Response.json({count:13})}if(p.has('returnIdsOnly'))return Response.json({objectIds:Array.from({length:13},(_,i)=>i+1)});if(failPage)return new Response('Unavailable',{status:503});const ids=p.get('objectIds').split(',').map(Number);return Response.json({type:'FeatureCollection',features:ids.map(i=>({type:'Feature',geometry,properties:{OBJECTID:i,apn:'000'+i,acres:1}}))});};
 const first=await atlasRefresh({partition_id:'test-partition'});assert.equal(first.cursor,12);assert.equal(first.complete,false);
 failPage=true;await assert.rejects(atlasRefresh({partition_id:'test-partition'}),/503/);
 const failed=database.prepare('SELECT state,data FROM atlas_jobs').get();assert.equal(failed.state,'FAILED');assert.equal(JSON.parse(failed.data).cursor,12);
 failPage=false;const resumed=await atlasRefresh({partition_id:'test-partition'});assert.equal(resumed.cursor,13);assert.equal(resumed.complete,true);assert.equal(countCalls,1);assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_parcels').get().n,13);
});

test('active lease excludes a second ingest worker',async()=>{
 await atlasImport({run_id:'p',entities:[{kind:'partition',id:'p',expected_version:0,data:{adapter:{url:'https://example.gov/FeatureServer/0',access:'PUBLIC_NO_KEY'}}}]});
 database.prepare('INSERT INTO atlas_jobs(id,kind,state,data,lease_token,lease_until,updated_at) VALUES(?,?,?,?,?,?,?)').run('refresh:p','PARCEL_INGEST','RUNNING','{}','other',new Date(Date.now()+60000).toISOString(),new Date().toISOString());
 assert.equal((await atlasRefresh({partition_id:'p'})).status,'LEASED');
});

test('first observation of an active listing establishes baseline without a new-listing alert',async()=>{
 await atlasImport({run_id:'p',parcels:[parcel()]});
 const listing={county_fips:'04003',apn:'000123',listing_status:'ACTIVE',source_url:'https://example.invalid/listing',offered_scope:'whole_parcel',scope_verified:true,geometry};
 database.prepare('INSERT INTO origination_records(id,kind,data,version,updated_at) VALUES(?,?,?,?,?)').run('listing:fixture','listing',JSON.stringify(listing),1,new Date().toISOString());
 await atlasReconcile({});assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_outbox').get().n,0);
 const link=JSON.parse(database.prepare("SELECT data FROM atlas_entities WHERE kind='listing_link'").get().data);assert.equal(link.match_state,'VERIFIED');assert.equal(link.event,null);assert.equal(link.screen_color,'GRAY');
 await atlasReconcile({});assert.equal(database.prepare('SELECT COUNT(*) n FROM atlas_entities WHERE kind=?').get('listing_observation').n,1);
});

test('large match queues keep exact active counts while responses stay bounded and pageable',async()=>{
 const links=Array.from({length:112},(_,i)=>({kind:'listing_link',id:'link-'+String(i).padStart(3,'0'),expected_version:0,data:{listing_id:'listing-'+i,match_state:i<11?'VERIFIED':'UNRESOLVED',active:i!==0}}));
 await atlasImport({run_id:'links-a',entities:links.slice(0,100)});await atlasImport({run_id:'links-b',entities:links.slice(100)});
 const summary=await atlasQuery(new URLSearchParams('view=summary'));assert.equal(summary.counts.listings_matched,10);assert.equal(summary.counts.listings_review,101);assert.equal(summary.unmatched_listings.length,100);assert.equal(summary.listing_links_truncated,true);
 const first=await atlasQuery(new URLSearchParams('view=listing_links'));assert.equal(first.records.length,100);assert.ok(first.next_cursor);
 const next=await atlasQuery(new URLSearchParams({view:'listing_links',after:first.next_cursor}));assert.equal(next.records.length,11);assert.equal(next.next_cursor,null);
});
