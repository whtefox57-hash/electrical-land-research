import {withDatabase} from '@/lib/vercel-runtime';
import {historyProgress,historyDetail,historyQueue,historyStages,queueRecords} from '@/lib/data-center-history';
import workflow from '@/data/data-center-history-workflow.json';
export const dynamic='force-dynamic';
// The existing owner-only Sites gateway authorizes both visitors and service callers.
// Service credentials deliberately carry no visitor email; keep the current audience private.
async function GETHandler(req:Request){
 const origin=req.headers.get('origin');if(origin&&origin!==new URL(req.url).origin)return Response.json({error:'Origin not allowed'},{status:403});
 const p=new URL(req.url).searchParams,headers={'Cache-Control':'private, no-store'};
 try{
  if(p.get('format')==='workflow')return Response.json(workflow,{headers});
  if(p.get('id')){const row=await historyDetail(p.get('id')!);return row?Response.json(row,{headers}):Response.json({error:'Inventory record not found'},{status:404,headers})}
  const progress=await historyProgress();
  if(p.get('format')==='progress'||p.get('summary')==='1')return Response.json({summary:progress.summary,rows:progress.rows,stages:historyStages},{headers});
  const offset=Math.max(0,Math.floor(Number(p.get('offset'))||0)),limit=Math.min(100,Math.max(1,Math.floor(Number(p.get('limit'))||20)));
  const ids=p.get('next')==='1'?historyQueue.record_ids.filter(progress.eligible):historyQueue.record_ids;
  return Response.json({total:ids.length,offset,limit,summary:progress.summary,rows:queueRecords(ids.slice(offset,offset+limit))},{headers});
 }catch(e){return Response.json({error:(e as Error).message},{status:503,headers})}
}

export const GET=withDatabase(GETHandler);
