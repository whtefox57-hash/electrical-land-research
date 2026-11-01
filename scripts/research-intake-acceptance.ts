import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applySourceUpdates} from '../lib/source-updates';
import {applySept20,newResearchRecords} from '../lib/sept20-backfill';
import {validateDesk} from '../lib/model';
import {optionDraft} from '../lib/research-option';
import {parseDailyDigest} from '../lib/daily-digest';
import research from '../data/research-sept20/research.json';

const s:any=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));applySourceUpdates(s);validateDesk(s);
assert.equal(newResearchRecords().length,20);assert.equal(s.records.filter((r:any)=>r.origin==='September 20 listing research').length,20);
const before=JSON.stringify(s);assert.equal(applySept20(s),false);assert.equal(JSON.stringify(s),before,'repeated read must not duplicate or overwrite');
const existing=s.records.filter((r:any)=>!r.dealCard);assert.ok(existing.some((r:any)=>r.priority_tier==='REJECTED'));assert.equal(s.budget.learningCap,5000);assert.equal(s.budget.softControlCap,10000);
for(const d of research.candidates){
 assert.equal(d.score.factors.length,52);assert.equal(d.score.factors.reduce((n,f)=>n+f.weight,0),100);
 const lower=d.score.factors.reduce((n,f)=>n+f.weight*f.q*(f.rating??0)/5,0);assert.ok(Math.abs(lower-d.score.conservative)<.006);
 assert.ok(d.score.conservative<=d.score.base&&d.score.base<=d.score.upper);assert.equal(d.availableMW,null);assert.equal(d.carrierCapacity,null);
 assert.ok(d.contacts.find(c=>c.role==='Government')?.phone);assert.ok(/^https:\/\//.test(d.listingUrl));
 const contract=optionDraft(d);assert.ok(contract.includes(d.name));assert.ok(contract.includes(d.listingUrl));assert.ok(contract.includes('No payment has been authorized'));assert.ok(contract.includes(d.risk));
 const rec:any=s.records.find((r:any)=>r.id===d.id);assert.equal(rec.capital_status,'HOLD');assert.equal(rec.priority_tier,'WATCH');assert.equal(rec.intelligence.portfolioStatus,'OTHER');
}
assert.equal(new Set(research.states.map(s=>s.code)).size,50);
assert.equal(new Set(research.candidates.map(d=>d.listingUrl)).size,20);
assert.equal(research.candidates.filter(d=>d.price==null).length,2);
assert.throws(()=>parseDailyDigest({summary:'x',statesReviewed:['not-a-state']}));
assert.equal(parseDailyDigest({summary:'0 new',newIds:[],statesReviewed:['AZ']})?.newIds.length,0);
// Simulate a newer founder decision then reapply the additive release to prove it remains authoritative.
const locked:any=s.records.find((r:any)=>r.id===research.candidates[0].id);locked.priority_tier='REJECTED';locked.categoryReason='QA founder decision';locked.noteEntries.push({id:'qa-note',at:'2026-09-20',text:'QA preserved'});(s as any).appliedUpdates=(s as any).appliedUpdates.filter((x:string)=>x!=='sept20-research-intake-v1');applySept20(s);assert.equal(locked.categoryReason,'QA founder decision');assert.equal(locked.priority_tier,'REJECTED');assert.equal(locked.noteEntries.at(-1).text,'QA preserved');assert.equal(s.records.filter((r:any)=>r.id===locked.id).length,1);
console.log('PASS: 20 distinct records; 52-factor math; 50 states; option drafts; null capacities; budget/decision preservation; idempotence; daily schema.');
