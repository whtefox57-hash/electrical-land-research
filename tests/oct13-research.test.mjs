import test,{after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createServer} from 'vite';
const root=fileURLToPath(new URL('..',import.meta.url));
const vite=await createServer({appType:'custom',configFile:false,root,resolve:{alias:{'@':root}},server:{middlewareMode:true}});
after(()=>vite.close());
const {applySourceUpdates}=await vite.ssrLoadModule('/lib/source-updates.ts');
const {applyOct13}=await vite.ssrLoadModule('/lib/oct13-backfill.ts');
const {validateDesk}=await vite.ssrLoadModule('/lib/model.ts');
const base=JSON.parse(await readFile(new URL('../data/current-workspace.json',import.meta.url),'utf8'));
test('appends research once, keeps distinct shared-parent offers and preserves capital',()=>{
 const s=structuredClone(base);applySourceUpdates(s);validateDesk(s);
 const count=s.records.length,reports=s.reports.length;
 assert.equal(s.records.filter(r=>r.id==='tx-vernon-27899900').length,1);
 assert.equal(s.records.filter(r=>r.id==='fl-chiefland-fannin').length,1);
 assert.equal(s.records.filter(r=>r.id.startsWith('sc-dillon-')).length,6);
 assert.equal(s.records.find(r=>r.id==='sc-dillon-72').geometry,null);
 assert.equal(s.records.find(r=>r.id==='sc-dillon-721').geometry,null);
 assert.equal(s.records.find(r=>r.id==='sc-dillon-53').geometry.type,'Polygon');
 assert.ok(s.records.find(r=>r.id==='ga-gordon-048007').geometry);
 assert.equal(s.founderFocusRecordId,'tx-vernon-27899900');
 assert.equal(s.budget.learningCap,5000);assert.equal(s.budget.softControlCap,10000);
 assert.equal(applyOct13(s),false);assert.equal(s.records.length,count);assert.equal(s.reports.length,reports);
 for(const r of s.records.filter(r=>r.researchOct13))assert.equal(r.researchOct13.availableMW,null);
 for(const p of s.reports.filter(p=>p.id.startsWith('recovered-power-siting-')))assert.equal(p.hash,createHash('sha256').update(p.original).digest('hex'));
 assert.ok(gzipSync(JSON.stringify(s)).length*4/3<1_800_000,'compressed workspace fits existing persistence ceiling');
});
test('preserves founder notes, rejection, portfolio, capacity and completed actions',()=>{
 const s=structuredClone(base);applySourceUpdates(s);s.appliedUpdates=s.appliedUpdates.filter(x=>x!=='oct13-research-v1');
 const r=s.records.find(x=>x.id==='tx-vernon-27899900');r.notes='Founder private note';r.priority_tier='REJECTED';r.lifecycle='REJECTED';r.summary='Founder decision';r.intelligence.portfolioStatus='ARCHIVED';r.intelligence.electricity.available_mw=7;r.history.push({at:'2026-10-12',action:'FOUNDER_CATEGORY_DECISION',note:'Preserve this decision'});r.actions.find(a=>a.id==='oct13-hinds-documents').done=true;
 const automations=JSON.stringify(s.automations),budget=JSON.stringify(s.budget);
 applyOct13(s);
 assert.equal(r.notes,'Founder private note');assert.equal(r.priority_tier,'REJECTED');assert.equal(r.summary,'Founder decision');assert.equal(r.intelligence.portfolioStatus,'ARCHIVED');assert.equal(r.intelligence.electricity.available_mw,7);assert.equal(r.actions.find(a=>a.id==='oct13-hinds-documents').done,true);
 assert.equal(JSON.stringify(s.automations),automations);assert.equal(JSON.stringify(s.budget),budget);
});
test('renders research, all reviewed leads, evidence downloads and explicit proof limits',async()=>{
 const {LatestResearch,CurrentLead}=await vite.ssrLoadModule('/components/oct13-research.tsx');
 const html=renderToStaticMarkup(React.createElement(LatestResearch,{full:true}));
 assert.match(html,/Hinds first/);assert.match(html,/Dillon 53/);assert.match(html,/Pineville Road/);assert.match(html,/recovered-week.json/);assert.match(html,/cross-chat coverage is incomplete/);assert.doesNotMatch(html,/NaN|undefined/);
 const s=structuredClone(base);applySourceUpdates(s);
 for(const r of s.records.filter(r=>r.researchOct13)){
  const card=renderToStaticMarkup(React.createElement(CurrentLead,{record:r}));assert.match(card,/HOLD/);assert.doesNotMatch(card,/NaN|undefined/);
 }
});
