import {importOrigination,queryOrigination} from '@/lib/origination-store';
export const dynamic='force-dynamic';
// Verified owner-only Site: dispatch authenticates visitors AND service callers.
// A service bearer supplies no visitor identity. Preserve owner-only hosting.
function boundary(req:Request){const origin=req.headers.get('origin');if(origin&&origin!==new URL(req.url).origin)return Response.json({error:'Origin not allowed'},{status:403});return null;}
export async function GET(req:Request){const denied=boundary(req);if(denied)return denied;try{return Response.json(await queryOrigination(new URL(req.url).searchParams),{headers:{'Cache-Control':'private, no-store'}})}catch(e){return Response.json({error:(e as Error).message},{status:503})}}
export async function POST(req:Request){const denied=boundary(req);if(denied)return denied;if(!req.headers.get('content-type')?.includes('application/json'))return Response.json({error:'JSON required'},{status:415});try{const raw=await req.text();if(raw.length>2000000)return Response.json({error:'Batch exceeds 2 MB'},{status:413});return Response.json(await importOrigination(JSON.parse(raw)),{headers:{'Cache-Control':'private, no-store'}})}catch(e){return Response.json({error:(e as Error).message},{status:409})}}
