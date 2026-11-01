import {withDatabase} from '@/lib/vercel-runtime';
import {importOrigination,queryOrigination} from '@/lib/origination-store';
export const dynamic='force-dynamic';
// Verified owner-only Site: dispatch authenticates visitors AND service callers.
// A service bearer supplies no visitor identity. Preserve owner-only hosting.
function boundary(req:Request){const origin=req.headers.get('origin');if(origin&&origin!==new URL(req.url).origin)return Response.json({error:'Origin not allowed'},{status:403});return null;}
async function GETHandler(req:Request){const denied=boundary(req);if(denied)return denied;try{return Response.json(await queryOrigination(new URL(req.url).searchParams),{headers:{'Cache-Control':'private, no-store'}})}catch(e){return Response.json({error:(e as Error).message},{status:503})}}
async function POSTHandler(req:Request){const denied=boundary(req);if(denied)return denied;if(!req.headers.get('content-type')?.includes('application/json'))return Response.json({error:'JSON required'},{status:415});try{const raw=await req.text();if(raw.length>2000000)return Response.json({error:'Batch exceeds 2 MB'},{status:413});return Response.json(await importOrigination(JSON.parse(raw)),{headers:{'Cache-Control':'private, no-store'}})}catch(e){return Response.json({error:(e as Error).message},{status:409})}}

export const GET=withDatabase(GETHandler);
export const POST=withDatabase(POSTHandler);
