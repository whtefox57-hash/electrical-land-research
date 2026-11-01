import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applySourceUpdates} from '../lib/source-updates';
import {applySept23} from '../lib/sept23-backfill';
import {validateDesk} from '../lib/model';
import {optionDraft} from '../lib/research-option';
import {encodeWorkspace,decodeWorkspace} from '../lib/workspace-codec';
import catalog from '../data/research-sept23/research.json';
import previous from '../data/research-sept22/research.json';
const fresh:any[]=catalog.candidates.filter(d=>d.batch==='inference-50');
assert.equal(fresh.length,50);assert.equal(catalog.candidates.length,120);
assert.equal(new Set(catalog.candidates.map(d=>d.id)).size,120);
assert.equal(new Set(catalog.candidates.map(d=>d.listingUrl)).size,120);
for(const d of fresh){
 assert.ok(d.price>0&&d.acres>=5&&d.acres<30);
 assert.equal(d.assignmentAssessment.percent,null);assert.equal(d.assignmentAssessment.status,'NOT ESTIMABLE');assert.equal(d.assignmentEstimate,undefined);
 assert.equal(d.availableMW,null);assert.equal(d.carrierCapacity,null);assert.equal(d.location,null);
 assert.ok(d.contacts[0].url&&d.contacts[1].url&&d.contacts[2].url);
 assert.equal(d.score.factors.length,52);
 assert.ok(Math.abs(d.score.factors.reduce((s:number,f:any)=>s+f.weight,0)-100)<.00001);
 assert.ok(Math.abs(d.score.factors.reduce((s:number,f:any)=>s+f.weight*f.q*(f.rating??0)/5,0)-d.score.conservative)<.0006);
 assert.equal(d.score.factors.find((f:any)=>f.id==='P02').rating,null);
 assert.equal(d.option.controlExposure,1500);assert.equal(d.option.initialDays+d.option.extensionDays,360);
 const draft=optionDraft(d);assert.ok(draft.includes(d.name)&&draft.includes(d.risk)&&draft.includes(d.listingUrl));assert.ok(draft.includes('No payment has been authorized'));
 assert.equal(fs.readFileSync(`public/research-options/${d.id}.txt`,'utf8'),draft);
}
for(const d of previous.candidates)assert.deepEqual(catalog.candidates.find(x=>x.id===d.id),d,'Existing research preserved '+d.id);
const s:any=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));const prior=JSON.parse(JSON.stringify(s));applySourceUpdates(s);validateDesk(s);
assert.equal(s.records.length,179);assert.equal(s.records.filter((r:any)=>r.dealCard?.batch==='inference-50').length,50);
for(const r of s.records.filter((r:any)=>r.dealCard?.batch==='inference-50')){assert.equal(r.priority_tier,'WATCH');assert.equal(r.recordType,'UNRESOLVED_LEAD');assert.equal(r.initialScreen.powerSignal,false);}
const bytes=Buffer.byteLength(encodeWorkspace(s));assert.ok(bytes<1900000,`D1 workspace payload too large: ${bytes}`);
assert.deepEqual(decodeWorkspace(JSON.stringify(prior)),prior,'Legacy JSON must remain readable');
assert.deepEqual(decodeWorkspace(encodeWorkspace(s)),s,'All research and original report payloads survive compression');
assert.throws(()=>decodeWorkspace(JSON.stringify({encoding:'syncranicity-gzip-base64-v1',payload:'broken'})));
const before=JSON.stringify(s);assert.equal(applySept23(s),false);assert.equal(JSON.stringify(s),before);
const founder=s.records.find((r:any)=>r.id===fresh[0].id)!;founder.notes='Founder decision';founder.priority_tier='REJECTED';
(s as any).appliedUpdates=(s as any).appliedUpdates.filter((m:string)=>m!=='sept23-inference-50-v1');applySept23(s);assert.equal(founder.notes,'Founder decision');assert.equal(founder.priority_tier,'REJECTED');assert.equal(s.records.length,179);
assert.deepEqual(s.budget,prior.budget);assert.equal(catalog.runs[0].newIds.length,50);assert.equal(new Set(catalog.states.map(x=>x.code)).size,50);
console.log(`PASS: 50 distinct new / 120 catalog / 179 workspace including concurrent Buyer Watch; null probability/capacity, 52-factor math, contract parity, prior records and founder decisions preserved; ${bytes} stored bytes.`);
