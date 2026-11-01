import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {openSQLite,commitSQLite} from '../lib/vercel-sqlite.mjs';
import {createBlobStorage} from '../lib/vercel-blob.mjs';
import {authorize} from '../lib/auth.ts';

async function fixture() {
 const s=await openSQLite(new Uint8Array());
 await s.adapter.exec('CREATE TABLE records(id TEXT PRIMARY KEY,version INTEGER NOT NULL,data TEXT NOT NULL); CREATE TABLE events(id TEXT PRIMARY KEY,data TEXT NOT NULL);');
 await s.adapter.prepare('INSERT INTO records VALUES(?,1,?)').bind('a','original').run();
 return s;
}
test('atomic batch rolls back every statement when the last constraint fails',async()=>{
 const s=await fixture();try{
  await assert.rejects(s.adapter.batch([
   s.adapter.prepare('UPDATE records SET data=? WHERE id=?').bind('changed','a'),
   s.adapter.prepare('INSERT INTO events VALUES(?,?)').bind('event',null),
  ]));
  assert.equal((await s.adapter.prepare('SELECT data FROM records WHERE id=?').bind('a').first()).data,'original');
  assert.equal((await s.adapter.prepare('SELECT COUNT(*) n FROM events').first()).n,0);
 }finally{await s.close();}
});
test('stale compare-and-swap leaves saved data unchanged',async()=>{
 const s=await fixture();try{
  const result=await s.adapter.prepare('UPDATE records SET data=?,version=version+1 WHERE id=? AND version=?').bind('new','a',0).run();
  assert.equal(result.meta.changes,0);
  assert.equal((await s.adapter.prepare('SELECT data FROM records').first()).data,'original');
 }finally{await s.close();}
});
test('two isolated requests cannot overwrite a newer snapshot',async()=>{
 const initial=await fixture();let bytes;try{bytes=await initial.bytes();}finally{await initial.close();}
 let saved={bytes,etag:'v1'};
 const storage={get:async()=>saved,put:async(next,expected)=>{if(expected!==saved.etag)throw Error('CONFLICT');saved={bytes:next,etag:'v2'};return saved;}};
 const a=await openSQLite(bytes),b=await openSQLite(bytes);
 try{
  await a.adapter.prepare('UPDATE records SET data=?').bind('winner').run();
  await b.adapter.prepare('UPDATE records SET data=?').bind('loser').run();
  await commitSQLite(a,'v1',storage);
  await assert.rejects(commitSQLite(b,'v1',storage),/CONFLICT/);
  const check=await openSQLite(saved.bytes);try{assert.equal((await check.adapter.prepare('SELECT data FROM records').first()).data,'winner');}finally{await check.close();}
 }finally{await a.close();await b.close();}
});
test('commit rejects an unconfirmed storage readback',async()=>{
 const s=await fixture();try{
  await assert.rejects(commitSQLite(s,'old',{put:async()=>({etag:'new'}),get:async()=>({etag:'old',bytes:Buffer.from('bad')})}),/readback/);
 }finally{await s.close();}
});
test('Blob writes use private access and ETag conditions; errors do not leak credentials',async()=>{
 const old=process.env.BLOB_READ_WRITE_TOKEN;
 process.env.BLOB_READ_WRITE_TOKEN='vercel_blob_rw_teststore_testsecret';
 try{
  const storage=createBlobStorage(async(url,options)=>{
   assert.equal(options.headers['x-if-match'],'previous');
   assert.equal(options.headers['x-vercel-blob-access'],'private');
   assert.equal(options.headers['x-allow-overwrite'],'1');
   return new Response('',{status:412});
  });
  await assert.rejects(storage.put(Buffer.from('db'),'previous'),/CONFLICT/);
 }finally{if(old===undefined)delete process.env.BLOB_READ_WRITE_TOKEN;else process.env.BLOB_READ_WRITE_TOKEN=old;}
});
test('PWA caches only the public offline page and local icons',async()=>{
 const manifest=JSON.parse(await fs.readFile(new URL('../public/home-screen-v2.webmanifest',import.meta.url),'utf8'));
 assert.equal(manifest.display,'standalone');assert.equal(manifest.start_url,'/');
 for(const icon of manifest.icons){assert.ok(icon.src.startsWith('/'));await fs.access(new URL('../public'+icon.src,import.meta.url));}
 const sw=await fs.readFile(new URL('../public/sw.js',import.meta.url),'utf8');
 const files=sw.match(/const PUBLIC = (\[[^;]+\]);/)[1];
 assert.deepEqual(JSON.parse(files.replaceAll("'",'"')),['/offline','/home-icon-v2-192.png','/home-icon-v2-512.png']);
 assert.ok(!sw.includes('cache.put('));
});
test('forged Sites identity cannot enable an unconfigured runtime; protected writes require same-origin',()=>{
 const previous={VERCEL:process.env.VERCEL,DEPLOYMENT_AUTH_BOUNDARY:process.env.DEPLOYMENT_AUTH_BOUNDARY};
 try{
  delete process.env.VERCEL;delete process.env.DEPLOYMENT_AUTH_BOUNDARY;
  assert.equal(authorize(new Request('https://desk.test/api/desk',{headers:{'oai-authenticated-user-email':'whtefox57@gmail.com'}})).status,401);
  process.env.VERCEL='1';process.env.DEPLOYMENT_AUTH_BOUNDARY='vercel-sso';
  assert.equal(authorize(new Request('https://desk.test/api/mutate',{method:'POST',headers:{origin:'https://evil.test','content-type':'application/json'}}),true).status,403);
  assert.equal(authorize(new Request('https://desk.test/api/mutate',{method:'POST',headers:{origin:'https://desk.test','content-type':'application/json'}}),true),null);
 }finally{for(const [key,value]of Object.entries(previous)){if(value===undefined)delete process.env[key];else process.env[key]=value;}}
});
