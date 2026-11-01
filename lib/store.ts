import { database } from './vercel-runtime';
import type { Desk } from './model';
import {applySourceUpdates} from './source-updates';
import {encodeWorkspace,decodeWorkspace} from './workspace-codec';
export function db(){return database();}
export async function readDesk():Promise<{data:Desk;version:number}>{
 for(let attempt=0;attempt<4;attempt++){
  const r=await db().prepare('SELECT data,version FROM workspace WHERE id=?').bind('main').first();if(!r)throw Error('Baseline migration has not completed.');const data=decodeWorkspace(r.data),version=r.version;
  if(!applySourceUpdates(data))return {data,version};
  try{return {data,version:await saveDesk(data,version)}}catch(e){if(!(e as Error).message.startsWith('CONFLICT')||attempt===3)throw e;}
 }
 throw Error('Workspace update conflict; retry');
}
export async function saveDesk(data:Desk,expected:number){
 const d=db();const at=new Date().toISOString();const stored=encodeWorkspace(data);
 const results=await d.batch([
  d.prepare('INSERT INTO snapshots (id,data,version,created_at) SELECT ?,data,version,? FROM workspace WHERE id=? AND version=?').bind(crypto.randomUUID(),at,'main',expected),
  d.prepare('UPDATE workspace SET data=?,version=version+1 WHERE id=? AND version=?').bind(stored,'main',expected)
 ]);
 if(results[1].meta.changes!==1)throw Error('CONFLICT: Another session saved first. Refresh before retrying; your changes were not saved.');
 return expected+1;
}
export async function digest(s:string){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s)))).map(x=>x.toString(16).padStart(2,'0')).join('');}
