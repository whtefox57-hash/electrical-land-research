import {readCartoKey} from './carto-credential.mjs';
const headers={'Cache-Control':'private, no-store, max-age=0','Vary':'Cookie','X-Content-Type-Options':'nosniff'};
const fail=(error,status)=>Response.json({error},{status,headers});
// Fixed upstream and bounded integer coordinates: this is never an arbitrary proxy.
export async function atlasBasemap(request,env,fetchTile=fetch) {
 const owner=env.ATLAS_SETTINGS_OWNER_EMAIL;
 const email=request.headers.get('oai-authenticated-user-email');
 if(!owner||!email||email.toLowerCase()!==owner.toLowerCase())return fail('Owner sign-in required.',403);
 const origin=request.headers.get('origin');
 if((origin&&origin!==new URL(request.url).origin)||request.headers.get('sec-fetch-site')==='cross-site')return fail('Same-origin request required.',403);
 if(request.method!=='GET')return fail('Method not allowed.',405);
 const url=new URL(request.url);
 const match=/^\/api\/atlas\/basemap\/(\d{1,2})\/(\d{1,6})\/(\d{1,6})\.png$/.exec(url.pathname);
 if(!match||[...url.searchParams.keys()].some(k=>k!=='v'))return fail('Invalid tile.',400);
 const [z,x,y]=match.slice(1).map(Number);
 if(z>19||x>=2**z||y>=2**z)return fail('Invalid tile.',400);
 try {
  if(!env.BUCKET||!env.ATLAS_CREDENTIAL_ENCRYPTION_KEY)return fail('Secure map connection unavailable.',503);
  const key=await readCartoKey(env);
  if(!key)return fail('No CARTO basemap key saved. Open Atlas Settings.',409);
  const upstream=new URL(`https://basemaps.cartocdn.com/rastertiles/light_all/${z}/${x}/${y}.png`);
  upstream.searchParams.set('key',key);
  // Only the Site referer is sent for keys restricted to this website.
  // Never forward visitor cookies, identity, authorization or upstream error text.
  const result=await fetchTile(upstream.href,{headers:{Accept:'image/png',Referer:url.origin+'/'},redirect:'error',signal:AbortSignal.timeout(10000)});
  if(!result.ok)return fail(result.status===401||result.status===403?'CARTO rejected the saved basemap key. Check its validity and website restrictions.':'CARTO tiles are temporarily unavailable.',502);
  if(!result.headers.get('content-type')?.toLowerCase().startsWith('image/png'))return fail('CARTO returned an invalid tile.',502);
  const tile=new Uint8Array(await result.arrayBuffer());
  const signature=[137,80,78,71,13,10,26,10];
  if(tile.length>2000000||!signature.every((b,i)=>tile[i]===b))return fail('CARTO returned an invalid tile.',502);
  return new Response(tile,{headers:{...headers,'Content-Type':'image/png'}});
 } catch {return fail('Secure map connection unavailable. Check Atlas Settings.',503);}
}
