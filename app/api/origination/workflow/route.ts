import workflow from '@/docs/origination-workflow.json';
export const dynamic='force-dynamic';
export async function GET(){return Response.json(workflow,{headers:{'Cache-Control':'private, no-store'}})}
