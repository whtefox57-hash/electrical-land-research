import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applySourceUpdates} from '../lib/source-updates';
import {importBuyerWatch} from '../lib/buyer-watch-import';
import {validateDesk} from '../lib/model';
import payload from '../data/research-sept23/buyer-watch.json';
const s=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));
const decisions=structuredClone(s.records.map((r:any)=>({id:r.id,tier:r.priority_tier,capital:r.capital_status,notes:r.noteEntries})));
const budget=structuredClone(s.budget);
applySourceUpdates(s);validateDesk(s);
const report:any=s.reports.find((p:any)=>p.runId===payload.run_id);
assert.ok(report);assert.equal(report.original,payload.report);assert.equal(report.recordIds.length,33);
assert.equal(report.sourcePayload.buyer_events.length,3);
for(const id of report.recordIds){const r:any=s.records.find((r:any)=>r.id===id);assert.ok(r);assert.equal(r.intelligence.electricity.available_mw,null);}
for(const old of decisions){const r:any=s.records.find((r:any)=>r.id===old.id);assert.equal(r.priority_tier,old.tier);assert.equal(r.capital_status,old.capital);assert.deepEqual(r.noteEntries,old.notes);}
assert.deepEqual(s.budget,budget);
const before=JSON.stringify(s);assert.equal(applySourceUpdates(s),false);assert.equal(importBuyerWatch(s,payload).duplicate,true);assert.equal(JSON.stringify(s),before);
assert.throws(()=>importBuyerWatch(s,{...payload,report:payload.report+' correction'}),/CONFLICT/);
const protectedRecord:any=s.records.find((r:any)=>r.id===report.recordIds[0]);protectedRecord.priority_tier='REJECTED';protectedRecord.capital_status='HOLD';protectedRecord.categoryReason='Founder archive';
const renamed=structuredClone(payload);renamed.run_id+='-url-match';renamed.offerings=renamed.offerings.slice(0,1);renamed.offerings[0].id='different-upstream-id';renamed.buyer_events=[];
const count=s.records.length;const receipt=importBuyerWatch(s,renamed);assert.equal(s.records.length,count);assert.equal(receipt.recordIds[0],protectedRecord.id);assert.equal(protectedRecord.priority_tier,'REJECTED');assert.equal(protectedRecord.categoryReason,'Founder archive');
console.log('PASS: 33 offerings, complete original report, buyer events, URL matching, repeat imports, conflicting-run rejection, founder decisions and capital preservation.');
