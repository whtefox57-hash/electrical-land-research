// Server-only CARTO credential vault. Never import into client components.
const OBJECT = '_private-credentials/carto-v1.json';
const AAD = new TextEncoder().encode('appgprj_6a9c555e97f48191a1d45c2cb55d4779:carto:v1');
const headers = {'Cache-Control':'private, no-store, max-age=0','Pragma':'no-cache','Vary':'Cookie','X-Content-Type-Options':'nosniff'};
const reply=(data,status=200)=>Response.json(data,{status,headers});
const b64=bytes=>btoa(String.fromCharCode(...bytes));
async function encryptionKey(value) {
 if(typeof value!=='string')throw Error('Vault unavailable');
 const bytes=Uint8Array.from(atob(value),c=>c.charCodeAt(0));
 if(bytes.length!==32)throw Error('Vault unavailable');
 return crypto.subtle.importKey('raw',bytes,'AES-GCM',false,['encrypt','decrypt']);
}
// Only server tile requests may consume this value; never serialize it to a client.
export async function readCartoKey(env) {
 const object=await env.BUCKET.get(OBJECT);
 if(!object)return null;
 const item=await object.json();
 if(item.version!==1)throw Error('Vault unavailable');
 const bytes=value=>Uint8Array.from(atob(value),c=>c.charCodeAt(0));
 const key=await encryptionKey(env.ATLAS_CREDENTIAL_ENCRYPTION_KEY);
 const clear=await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes(item.iv),additionalData:AAD},key,bytes(item.ciphertext));
 return new TextDecoder().decode(clear);
}
async function limitedJson(req) {
 const reader=req.body?.getReader(); if(!reader)throw Error('Invalid input');
 const chunks=[];let size=0;
 try {while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>12288){await reader.cancel();throw Error('Invalid input');}chunks.push(value);}}
 finally {reader.releaseLock();}
 const bytes=new Uint8Array(size);let offset=0;for(const c of chunks){bytes.set(c,offset);offset+=c.length;}
 return JSON.parse(new TextDecoder().decode(bytes));
}
export async function cartoCredential(request,env) {
 // Sites sanitizes identity headers. A second owner check protects this route
 // if the Site audience is expanded later. Service access cannot change keys.
 const owner=env.ATLAS_SETTINGS_OWNER_EMAIL;
 const email=request.headers.get('oai-authenticated-user-email');
 if(!owner||!email||email.toLowerCase()!==owner.toLowerCase())return reply({error:'Sign in as the Deal Desk owner to manage this key.'},403);
 const origin=request.headers.get('origin');
 if((origin&&origin!==new URL(request.url).origin)||request.headers.get('sec-fetch-site')==='cross-site')return reply({error:'Same-origin request required.'},403);
 if(!['GET','PUT','DELETE'].includes(request.method))return reply({error:'Method not allowed.'},405);
 if(request.method!=='GET'&&(!origin||!request.headers.get('content-type')?.toLowerCase().startsWith('application/json')))return reply({error:'Same-origin JSON required.'},403);
 if(!env.BUCKET||!env.ATLAS_CREDENTIAL_ENCRYPTION_KEY)return reply({error:'Secure storage is unavailable. Your key has not been changed.'},503);
 try {
  if(request.method==='GET') {
   const object=await env.BUCKET.head(OBJECT);
   return reply({configured:!!object,updated_at:object?.uploaded?.toISOString()??null});
  }
  if(request.method==='DELETE') {await env.BUCKET.delete(OBJECT);return reply({configured:false,updated_at:null});}
  let input;try{input=await limitedJson(request);}catch{return reply({error:'Enter a valid CARTO API key (maximum 8,192 characters).'},400);}
  if(typeof input?.api_key!=='string'||!input.api_key.trim()||input.api_key.length>8192||/[\s\x00-\x1f\x7f]/.test(input.api_key.trim()))return reply({error:'Enter a valid CARTO API key (maximum 8,192 characters).'},400);
  const key=await encryptionKey(env.ATLAS_CREDENTIAL_ENCRYPTION_KEY);
  const iv=crypto.getRandomValues(new Uint8Array(12));
  const encrypted=await crypto.subtle.encrypt({name:'AES-GCM',iv,additionalData:AAD},key,new TextEncoder().encode(input.api_key.trim()));
  const at=new Date().toISOString();
  await env.BUCKET.put(OBJECT,JSON.stringify({version:1,iv:b64(iv),ciphertext:b64(new Uint8Array(encrypted)),updated_at:at}),{httpMetadata:{contentType:'application/json',cacheControl:'no-store'}});
  return reply({configured:true,updated_at:at});
 } catch {return reply({error:'Secure storage is unavailable. Check the saved status before retrying.'},503);}
}
