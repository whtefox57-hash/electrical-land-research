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
const {applyOct19Screening,SCREENING_MARKER}=await vite.ssrLoadModule('/lib/oct19-screening-backfill.ts');
const {validateDesk}=await vite.ssrLoadModule('/lib/model.ts');
const base=JSON.parse(await readFile(new URL('../data/current-workspace.json',import.meta.url),'utf8'));

test('follow-up is idempotent and preserves founder locks, capital, focus and capacity',()=>{
 const s=structuredClone(base);applySourceUpdates(s);validateDesk(s);
 const ids=['oct19-38995811','sc-dillon-53','oct19-27254380','oct19-3934635'];
 assert.equal(s.records.filter(r=>r.desktopScreeningOct19).length,4);
 const count=s.records.length,reports=s.reports.length,budget=JSON.stringify(s.budget),automations=JSON.stringify(s.automations);
 assert.equal(applyOct19Screening(s),false);assert.equal(s.records.length,count);assert.equal(s.reports.length,reports);
 assert.equal(s.founderFocusRecordId,'tx-vernon-27899900');
 assert.equal(JSON.stringify(s.budget),budget);assert.equal(JSON.stringify(s.automations),automations);
 assert.ok(ids.every(id=>s.records.find(r=>r.id===id).intelligence.electricity.available_mw===null));
 const r=s.records.find(r=>r.id===ids[0]);r.notes='Founder retained note';r.summary='Founder retained decision';r.history.push({action:'FOUNDER_CATEGORY_DECISION'});r.intelligence.electricity.available_mw=7;r.intelligence.portfolioStatus='BACKUP_2';
 s.appliedUpdates=s.appliedUpdates.filter(x=>x!==SCREENING_MARKER);applyOct19Screening(s);
 assert.equal(r.notes,'Founder retained note');assert.equal(r.summary,'Founder retained decision');assert.equal(r.intelligence.electricity.available_mw,7);assert.equal(r.intelligence.portfolioStatus,'BACKUP_2');
});
test('Adairsville pending work is cancelled, not marked completed or erased',()=>{
 const s=structuredClone(base);s.appliedUpdates=[...(s.appliedUpdates||[]),SCREENING_MARKER];applySourceUpdates(s);
 const r=s.records.find(r=>r.id==='ga-gordon-048007');r.notes='Keep this history';r.actions.push({id:'pending-test',done:false,title:'Pending research'});r.actions.push({id:'completed-test',done:true,title:'Completed research'});s.tasks.push({id:'global-pending-test',recordId:r.id,done:false,title:'Pending global research'});
 s.appliedUpdates=s.appliedUpdates.filter(x=>x!==SCREENING_MARKER);applyOct19Screening(s);
 assert.equal(r.workflow_stage,'SCREENING_STOPPED');assert.equal(r.screeningControl.status,'STOPPED');assert.equal(r.notes,'Keep this history');
 assert.ok(!r.actions.some(a=>!a.done));assert.ok(!s.tasks.some(a=>a.recordId===r.id&&!a.done));
 assert.ok(r.actions.some(a=>a.id==='completed-test'&&a.done));assert.ok(r.cancelledScreeningActions.some(a=>a.id==='pending-test'&&!a.done&&a.cancelledAt));assert.ok(r.cancelledScreeningActions.some(a=>a.id==='global-pending-test'));
});
test('public report view and dossier cards expose current priority and proof limits',async()=>{
 const {ScreeningReport,ScreeningLead}=await vite.ssrLoadModule('/components/oct19-screening.tsx');
 const html=renderToStaticMarkup(React.createElement(ScreeningReport));
 for(const text of ['Rooks','Adairsville screening is stopped','76-acre','available','report.pdf'])assert.ok(html.toLowerCase().includes(text.toLowerCase()));
 assert.doesNotMatch(html,/NaN|undefined/);
 const s=structuredClone(base);applySourceUpdates(s);const card=renderToStaticMarkup(React.createElement(ScreeningLead,{record:s.records.find(r=>r.id==='oct19-38995811')}));
 assert.match(card,/EQUAL PRIORITY/);assert.match(card,/Capital HOLD/);assert.match(card,/available MW remains unknown/);
 assert.equal(s.records.find(r=>r.id==='oct19-27254380').location,null);
});
