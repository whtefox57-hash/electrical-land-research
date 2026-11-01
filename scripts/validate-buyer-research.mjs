import assert from 'node:assert/strict';
import {readFileSync,statSync} from 'node:fs';

const source='data/buyer-first-2026-10-29.json';
const data=JSON.parse(readFileSync(source,'utf8'));
const ids=new Set(data.buyers.map(b=>b.id));
assert.equal(data.buyers.length,100,'Exactly 100 reviewed profiles');
assert.equal(ids.size,100,'No duplicate platform IDs');
assert.equal(new Set(data.sites.map(s=>s.id)).size,data.sites.length,'Unique site records');
const checkUrl=u=>{assert.equal(typeof u,'string');assert.ok(['http:','https:'].includes(new URL(u).protocol));};
for(const b of data.buyers){
  for(const field of ['name','role','strategy','scale','dealStructure','acquisitionSignal','searchBrief','lane','matchStatus'])assert.ok(b[field]?.trim(),`${b.id}: ${field}`);
  for(const field of ['regions','publishedRequirements','inferredPreferences','differentiators','rejectionTriggers','buyerQuestions','sources'])assert.ok(b[field]?.length,`${b.id}: ${field}`);
  for(const r of b.publishedRequirements){assert.ok(r.fact);checkUrl(r.sourceUrl);assert.ok(['published requirement','published strategy / product','project evidence'].includes(r.kind));}
  for(const s of b.sources){checkUrl(s.url);assert.equal(s.retrieved,data.asOf);}
  const matches=data.sites.filter(s=>s.matches.some(m=>m.buyerId===b.id));
  if(!matches.length)assert.ok(b.noMatchReason,`${b.id}: unmatched explanation`);
}
let pairs=0,numeric=0,held=0;
for(const s of data.sites){
  checkUrl(s.listingUrl);s.sourceUrls.forEach(checkUrl);
  assert.equal(s.powerVerified,false,`${s.id}: no unverified utility claim promoted`);
  assert.equal(s.availableMw,null,`${s.id}: unknown MW remains null`);
  assert.ok(s.blockers.length && s.apnStatus && s.availabilityNote && s.nextProof);
  assert.equal(new Set(s.matches.map(m=>m.buyerId)).size,s.matches.length,`${s.id}: duplicate pair`);
  for(const m of s.matches){
    pairs++;assert.ok(ids.has(m.buyerId),`${s.id}: orphan buyer`);
    assert.ok(m.powerScenario && m.rationale && m.rejection && m.raiseIf);
    if(m.base===null){held++;assert.equal(m.low,null);assert.equal(m.high,null);assert.ok(m.scenarioHold);continue;}
    numeric++;assert.ok(!m.scenarioHold);assert.equal(m.assumptionInputs.length,3);
    assert.ok(0<=m.low && m.low<=m.base && m.base<=m.high && m.high<=100);
    for(const key of ['low','base','high']){
      const output=Math.round(m.assumptionInputs.reduce((p,a)=>p*a[key],1)/10000);
      assert.equal(m[key],output,`${s.id}/${m.buyerId}: scenario calculation ${key}`);
    }
  }
}
assert.equal(data.sites.find(s=>s.id==='old-wire-51').matches.length,0,'Off-market listing is not an active pair');
assert.ok(data.sites.find(s=>s.id==='hinds-110').matches.every(m=>m.base===null),'Hinds status hold retained');
const directory='public/research/buyer-first-2026-10-29/';
assert.deepEqual(JSON.parse(readFileSync(directory+'research.json','utf8')),data,'Download matches app dataset');
for(const name of ['buyers.csv','site-matches.csv','report.md'])assert.ok(statSync(directory+name).size>10000);
const report=readFileSync(directory+'report.md','utf8');
for(const b of data.buyers)assert.ok(report.includes(b.name),`${b.id}: full report coverage`);
console.log(JSON.stringify({ok:true,buyers:ids.size,sites:data.sites.length,pairs,numericScenarios:numeric,heldPairs:held,matchedBuyers:new Set(data.sites.flatMap(s=>s.matches.map(m=>m.buyerId))).size}));
