import {Miniflare,Log} from 'miniflare';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const mf=new Miniflare({modules:true,scriptPath:'dist/server/index.js',modulesRules:[{type:'ESModule',include:['**/*.js','**/*.mjs'],fallthrough:true}],compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB'],r2Buckets:['BUCKET'],assets:{directory:'dist/client',binding:'ASSETS',routerConfig:{has_user_worker:true,invoke_user_worker_ahead_of_assets:true}},log:new Log(0)});
const checks=[];
const request=(p,auth=true)=>mf.dispatchFetch('https://desk.example'+p,{headers:auth?{'oai-authenticated-user-email':'qa-owner@example.invalid'}:{}});
try{
 assert.equal((await request('/api/data-centers',false)).status,401);checks.push('Anonymous API requests rejected');
 const s=await (await request('/api/data-centers?format=summary')).json();assert.ok(s.summary.total>=3000);assert.equal(s.summary.total,JSON.parse(fs.readFileSync('data/data-center-registry.json','utf8')).records.length);checks.push('Production inventory matches the complete current 3000+ record register');
 const all=await (await request('/api/data-centers?format=all')).json();assert.equal(all.records.length,s.summary.total);assert.equal(all.evidence.records.length,21);assert.ok(Object.keys(all.sources).length>0);checks.push('Full directory payload includes records, sources and acquisition evidence');
 const directory=await request('/data-centers');assert.equal(directory.status,200);assert.match(directory.headers.get('content-type'),/text\/html/);assert.ok((await directory.text()).includes('Loading the national register'));checks.push('Directory page renders through the production Worker');
 const page=await (await request('/api/data-centers?state=AZ&limit=10')).json();assert.ok(page.rows.length<=10);assert.ok(page.rows.every(r=>r.state==='AZ'));checks.push('State filter and pagination');
 const detail=await (await request('/api/data-centers?id='+encodeURIComponent(page.rows[0].id))).json();assert.equal(detail.record.id,page.rows[0].id);assert.ok(detail.sources);checks.push('Record specifications and provenance');
 const missing=await request('/api/data-centers?id=does-not-exist');assert.equal(missing.status,404);checks.push('Unknown record returns404');
 const geo=await (await request('/api/data-centers?format=geojson&state=AZ')).json();assert.equal(geo.type,'FeatureCollection');assert.ok(geo.features.every(f=>f.properties.state==='AZ'));checks.push('Filtered geographic export');
 const csv=await request('/api/data-centers?format=csv&state=AZ');assert.match(csv.headers.get('content-type'),/text\/csv/);assert.ok((await csv.text()).includes('capacity_basis'));checks.push('CSV export retains measurement basis');
 fs.writeFileSync('qa/data-center-api-acceptance.json',JSON.stringify({passed:true,checks},null,2));console.log(JSON.stringify({passed:true,checks},null,2));
}finally{await mf.dispose()}
