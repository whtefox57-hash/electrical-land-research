import {authorize} from '@/lib/auth';import {db} from '@/lib/store';
export const dynamic='force-dynamic';
export async function GET(req:Request){const denied=authorize(req);if(denied)return denied;try{const row=await db().prepare('SELECT version FROM workspace WHERE id=?').bind('main').first();if(!row)return Response.json({error:'Workspace unavailable'},{status:503});return Response.json({version:row.version},{headers:{'Cache-Control':'private, no-store'}})}catch{return Response.json({error:'Delivery check unavailable'},{status:503})}}
