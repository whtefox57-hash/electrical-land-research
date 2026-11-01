import fs from 'node:fs';
import path from 'node:path';
import {applySourceUpdates} from '../lib/source-updates';
import {optionDraft} from '../lib/research-option';
import research from '../data/research-sept22/research.json';
const atlas=path.resolve(process.argv[2]||'../atlas-sept22');
const state=JSON.parse(fs.readFileSync('data/current-workspace.json','utf8'));
applySourceUpdates(state);
for(const d of research.candidates.filter(d=>d.batch==='additional-50')){
 const body=optionDraft(d);
 fs.writeFileSync(`public/research-options/${d.id}.txt`,body);
 fs.writeFileSync(path.join(atlas,`public/research-options/${d.id}.txt`),body);
}
fs.writeFileSync(path.join(atlas,'public/data/deal-desk-snapshot.json'),JSON.stringify({source:'Published Deal Desk source snapshot; live authenticated bridge takes precedence',snapshotDate:research.asOf,recordCount:state.records.length,records:state.records},null,2)+'\n');
console.log(JSON.stringify({records:state.records.length,workspaceBytes:Buffer.byteLength(JSON.stringify(state)),newOptions:50,atlasSnapshot:atlas}));
