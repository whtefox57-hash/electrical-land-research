import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applySourceUpdates} from '../lib/source-updates';
import {applySept22} from '../lib/sept22-backfill';
import {validateDesk} from '../lib/model';
import {optionDraft} from '../lib/research-option';
import research from '../data/research-sept22/research.json';
import original from '../data/research-sept20/research.json';
const fresh=research.candidates.filter(d=>d.batch==='additional-50');
assert.equal(fresh.length,50);assert.equal(research.candidates.length,70);
assert.equal(new Set(research.candidates.map(d=>d.id)).size,70);
assert.equal(new Set(research.candidates.map(d=>d.listingUrl)).size,70);
for(const d of fresh){
 const x:any=d;
 assert.ok(d.price!=null&&d.price>0);assert.equal(d.score.factors.length,52);
 assert.equal(d.score.factors.reduce((n,f)=>n+f.weight,0),100);
 assert.ok(Math.abs(d.score.factors.reduce((n,f)=>n+f.weight*f.q*(f.rating??0)/5,0)-d.score.conservative)<.006);
 assert.equal(d.availableMW,null);assert.equal(d.carrierCapacity,null);
 assert.ok(d.contacts[0].phone,'broker phone: '+d.id);assert.ok(d.contacts[1].url);assert.ok(d.contacts[2].phone);
 assert.ok(x.assignmentEstimate.low<=x.assignmentEstimate.percent&&x.assignmentEstimate.percent<=x.assignmentEstimate.high);
 assert.equal(x.option.initialDays+x.option.extensionDays,730);
 const draft=optionDraft(d);assert.ok(draft.includes(d.name)&&draft.includes(d.listingUrl)&&draft.includes(d.risk));assert.ok(draft.includes('365-day extension'));
 assert.ok(draft.includes('No payment has been authorized'));
 assert.equal(fs.readFileSync(`public/research-options/${d.id}.txt`,'utf8'),draft);
}
for(const d of original.candidates){
 const newer:any=research.candidates.find(x=>x.id===d.id);
 for(const field of ['price','apns','checkedAt','score','option'])assert.deepEqual(newer[field],(d as any)[field],`Original field retained: ${d.id} ${field}`);
}
const s:any=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));applySourceUpdates(s);validateDesk(s);assert.equal(s.records.length,96);
assert.ok(Buffer.byteLength(JSON.stringify(s))<1900000,'Canonical workspace must retain room under the D1 row limit');
const before=JSON.stringify(s);assert.equal(applySept22(s),false);assert.equal(JSON.stringify(s),before);
const first:any=s.records.find((r:any)=>r.id===fresh[0].id);first.priority_tier='REJECTED';first.categoryReason='Founder decision must survive';first.notes='Founder note';
(s as any).appliedUpdates=(s as any).appliedUpdates.filter((x:string)=>x!=='sept22-additional-50-v1');applySept22(s);assert.equal(first.priority_tier,'REJECTED');assert.equal(first.notes,'Founder note');assert.equal(first.categoryReason,'Founder decision must survive');assert.equal(s.records.length,96);
assert.equal(s.budget.learningCap,5000);assert.equal(s.budget.softControlCap,10000);
assert.equal(research.runs[0].newIds.length,50);assert.equal(research.runs[0].rejected.length+research.runs[0].holds.length,25);
assert.equal(new Set(research.states.map(s=>s.code)).size,50);
console.log('PASS: 50 new / 70 total, distinct listings and IDs, 52-factor math, conditional estimates, 50 option documents, original 20 unchanged, 96 canonical records, idempotence and founder/capital preservation.');
