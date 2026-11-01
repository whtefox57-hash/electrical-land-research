import {withDatabase} from '@/lib/vercel-runtime';
import {authorize} from '@/lib/auth';import {readDesk} from '@/lib/store';
export const dynamic='force-dynamic';
async function GETHandler(req:Request){const denied=authorize(req);if(denied)return denied;try{return Response.json(await readDesk(),{headers:{'Cache-Control':'private, no-store'}})}catch(e){return Response.json({error:(e as Error).message},{status:503})}}

export const GET=withDatabase(GETHandler);
