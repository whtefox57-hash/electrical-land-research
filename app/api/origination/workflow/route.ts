import {withDatabase} from '@/lib/vercel-runtime';
import workflow from '@/docs/origination-workflow.json';
export const dynamic='force-dynamic';
async function GETHandler(){return Response.json(workflow,{headers:{'Cache-Control':'private, no-store'}})}

export const GET=withDatabase(GETHandler);
