import test,{after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createServer} from 'vite';
const root=fileURLToPath(new URL('..',import.meta.url));
const vite=await createServer({appType:'custom',configFile:false,root,resolve:{alias:{'@':root}},server:{middlewareMode:true}});
after(()=>vite.close());
const {applySourceUpdates}=await vite.ssrLoadModule('/lib/source-updates.ts');
const {applyOct19}=await vite.ssrLoadModule('/lib/oct19-backfill.ts');
const {validateDesk}=await vite.ssrLoadModule('/lib/model.ts');
const base=JSON.parse(await readFile(new URL('../data/current-workspace.json',import.meta.url),'utf8'));

test('adds exactly 50 unique research records without changing founder controls',()=>{
 const s=structuredClone(base);s.appliedUpdates=[...(s.appliedUpdates||[]),'oct19-research-50-v1','oct19-four-site-screening-v1'];applySourceUpdates(s);
 const before=s.records.length,automations=JSON.stringify(s.automations),budget=JSON.stringify(s.budget);
 s.appliedUpdates=s.appliedUpdates.filter(x=>x!=='oct19-research-50-v1');applyOct19(s);validateDesk(s);
 const batch=s.records.filter(r=>r.researchOct19);
 assert.equal(batch.length,50);assert.equal(s.records.length,before+50);
 assert.equal(new Set(batch.map(r=>r.researchOct19.listingUrl)).size,50);
 assert.ok(batch.every(r=>r.priority_tier==='WATCH'&&r.capital_status==='HOLD'));
 assert.ok(batch.every(r=>r.intelligence.electricity.available_mw===null));
 assert.equal(s.founderFocusRecordId,'tx-vernon-27899900');
 assert.equal(JSON.stringify(s.automations),automations);assert.equal(JSON.stringify(s.budget),budget);
 const count=s.records.length,reports=s.reports.length;assert.equal(applyOct19(s),false);assert.equal(s.records.length,count);assert.equal(s.reports.length,reports);
});

test('renders all 50 sites and the explicit proof limits',async()=>{
 const {Research50Run,CurrentBatchLead}=await vite.ssrLoadModule('/components/oct19-research.tsx');
 const html=renderToStaticMarkup(React.createElement(Research50Run,{full:true}));
 assert.match(html,/50 sites ready for review/);assert.match(html,/New Castle/);assert.match(html,/Sergeant Bluff/);assert.match(html,/0.*paid-control-ready/s);assert.doesNotMatch(html,/NaN|undefined/);
 const s=structuredClone(base);applySourceUpdates(s);const card=renderToStaticMarkup(React.createElement(CurrentBatchLead,{record:s.records.find(r=>r.id==='oct19-27254380')}));
 assert.match(card,/available MW remains unknown/);assert.match(card,/Capital HOLD/);
});
