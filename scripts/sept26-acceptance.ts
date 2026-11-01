import assert from 'node:assert/strict';
import fs from 'node:fs';
import {applySourceUpdates} from '../lib/source-updates';
import {applySept26} from '../lib/sept26-backfill';
import {sept26Candidates} from '../lib/sept26-catalog';
import {validateDesk} from '../lib/model';
import {encodeWorkspace,decodeWorkspace} from '../lib/workspace-codec';
import {optionDraft} from '../lib/research-option';
const s=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));
applySourceUpdates(s);validateDesk(s);
assert.equal(sept26Candidates.length,50);
assert.equal(new Set(sept26Candidates.map(d=>d.listingUrl)).size,50);
const rows=s.records.filter((r:any)=>r.origin==='September 26 additional listing research');
assert.equal(rows.length,50);
for(const d of sept26Candidates){
 assert.ok(d.price>0);assert.ok(d.contacts[0].name);assert.ok(d.listingUrl.startsWith('https://'));
 assert.equal(d.assignmentAssessment.percent,null);assert.equal(d.score,undefined);
 assert.ok(optionDraft(d).includes(d.name));
 const r=rows.find((r:any)=>r.id===d.id);assert.ok(r);assert.equal(r.capital_status,'HOLD');assert.equal(r.priority_tier,'WATCH');
}
assert.equal(s.budget.learningCap,5000);assert.equal(s.budget.softControlCap,10000);
const before=JSON.stringify(s);assert.equal(applySept26(s),false);assert.equal(JSON.stringify(s),before);
rows[0].priority_tier='REJECTED';rows[0].notes='Founder decision preserved';
(s as any).appliedUpdates=(s as any).appliedUpdates.filter((x:string)=>x!=='sept26-listing-50-v1');
applySept26(s);assert.equal(rows[0].priority_tier,'REJECTED');assert.equal(rows[0].notes,'Founder decision preserved');
assert.equal(s.records.filter((r:any)=>r.id===rows[0].id).length,1);
assert.deepEqual(decodeWorkspace(encodeWorkspace(s)),s);
console.log('PASS: 50 unique listings, prices/links, withheld probabilities, repeat-safe import, founder decisions and budgets preserved, storage round trip.');
