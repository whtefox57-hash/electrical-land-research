import test,{after} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {gzipSync} from 'node:zlib';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {createServer} from 'vite';
const root=fileURLToPath(new URL('..',import.meta.url));
const vite=await createServer({appType:'custom',configFile:false,root,resolve:{alias:{'@':root}},server:{middlewareMode:true}});
after(()=>vite.close());
const {applySourceUpdates}=await vite.ssrLoadModule('/lib/source-updates.ts');
const {applyOct22,OCT22_MARKER}=await vite.ssrLoadModule('/lib/oct22-backfill.ts');
const {validateDesk}=await vite.ssrLoadModule('/lib/model.ts');
const base=JSON.parse(await readFile(new URL('../data/current-workspace.json',import.meta.url),'utf8'));
const run=JSON.parse(await readFile(new URL('../data/research-oct22/run.json',import.meta.url),'utf8'));

test('research merges all twelve canonical offerings once without changing founder decisions',()=>{
 const s=structuredClone(base);s.appliedUpdates=[...(s.appliedUpdates||[]),OCT22_MARKER];applySourceUpdates(s);
 const beforeCount=s.records.length;
 const protectedIds=[run.focusId,'oct19-38995811'];
 for(const id of protectedIds){const r=s.records.find(r=>r.id===id);r.notes='Keep my note';r.summary='Keep my judgment';r.intelligence.electricity.available_mw=7;r.intelligence.portfolioStatus='BACKUP_2';r.history.push({action:'FOUNDER_CATEGORY_DECISION'});}
 const controls=JSON.stringify({budget:s.budget,automations:s.automations,focus:s.founderFocusRecordId,stopped:s.records.find(r=>r.id==='ga-gordon-048007'),tasks:s.tasks,expenses:s.expenses,decisions:s.decisions});
 s.appliedUpdates=s.appliedUpdates.filter(x=>x!==OCT22_MARKER);
 assert.equal(applyOct22(s),true);validateDesk(s);
 assert.equal(s.records.length,beforeCount+4);assert.equal(s.records.filter(r=>r.researchOct22).length,12);
 assert.equal(JSON.stringify({budget:s.budget,automations:s.automations,focus:s.founderFocusRecordId,stopped:s.records.find(r=>r.id==='ga-gordon-048007'),tasks:s.tasks,expenses:s.expenses,decisions:s.decisions}),controls);
 for(const id of protectedIds){const r=s.records.find(r=>r.id===id);assert.equal(r.notes,'Keep my note');assert.equal(r.summary,'Keep my judgment');assert.equal(r.intelligence.electricity.available_mw,7);assert.equal(r.intelligence.portfolioStatus,'BACKUP_2');}
 const after=JSON.stringify(s);assert.equal(applyOct22(s),false);assert.equal(JSON.stringify(s),after);
 assert.ok(gzipSync(JSON.stringify(s)).length*4/3<1_800_000,'merged workspace fits persistence ceiling');
 const c=s.records.find(r=>r.id===run.focusId);assert.equal(c.actions[0].id,run.actions[0].id);c.actions.find(a=>a.id===run.actions[0].id).done=true;
 s.appliedUpdates=s.appliedUpdates.filter(x=>x!==OCT22_MARKER);applyOct22(s);
 assert.equal(c.actions.find(a=>a.id===run.actions[0].id).done,true);
 assert.equal(s.reports.filter(p=>p.id===run.id).length,1);
});
test('new findings do not silently clear money or capacity gates; all source references resolve',()=>{
 const s=structuredClone(base);applySourceUpdates(s);
 for(const c of run.candidates){assert.equal(c.availableMW,null);assert.equal(c.assignmentProbability,null);assert.equal(c.paidControlReady,false);for(const id of c.sourceIds)assert.ok(run.sources.some(x=>x.id===id));}
 for(const r of s.records.filter(r=>r.origin==='October 22 research run')){assert.equal(r.priority_tier,'WATCH');assert.equal(r.capital_status,'HOLD');assert.equal(r.intelligence.electricity.available_mw,null);}
 assert.equal(s.latestOptionResearch.paidControlReady,false);assert.equal(s.latestOptionResearch.newSpend,0);
 assert.equal(s.records.find(r=>r.id==='ga-gordon-048007').screeningControl.status,'STOPPED');
});
test('decision memo renders twelve offerings, conditional choice, gates and real evidence links',async()=>{
 const {OptionResearch,OptionReviewLead}=await vite.ssrLoadModule('/components/oct22-research.tsx');
 const html=renderToStaticMarkup(React.createElement(OptionResearch,{full:true}));
 for(const text of ['October 30','Hinds','No reviewed site','TCEQ','Seller financing','G16','report.md','run.json'])assert.ok(html.includes(text),text);
 for(const c of run.candidates)assert.ok(html.includes('id="'+c.id+'"'));
 assert.doesNotMatch(html,/NaN|undefined/);
 const card=renderToStaticMarkup(React.createElement(OptionReviewLead,{candidate:run.candidates[0]}));
 assert.match(card,/Paid-control eligibility: HOLD/);assert.match(card,/issuer documents/);
});
