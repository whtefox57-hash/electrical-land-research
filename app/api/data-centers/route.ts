import {authorize} from '@/lib/auth';
import {dataset,evidenceData,dataCenterSummary,filterDataCenters,csvExport,relatedEvidence} from '@/lib/data-center-registry';
export const dynamic='force-dynamic';
export async function GET(req:Request){
 const denied=authorize(req);if(denied)return denied;
 const p=new URL(req.url).searchParams,headers={'Cache-Control':'private, max-age=300'};
 if(p.get('id')){const record=dataset.records.find(r=>r.id===p.get('id'));return record?Response.json({record,evidence:relatedEvidence(record),sources:{...dataset.sources,...evidenceData.sources}},{headers}):Response.json({error:'Data center not found'},{status:404})}
 const rows=filterDataCenters(p),format=p.get('format');
 if(format==='csv')return new Response(csvExport(rows),{headers:{...headers,'Content-Type':'text/csv;charset=utf-8','Content-Disposition':'attachment; filename="Syncranicity_US_Data_Centers.csv"'}});
 if(format==='geojson')return Response.json({type:'FeatureCollection',features:rows.filter(r=>r.latitude!=null&&r.longitude!=null).map(r=>({type:'Feature',id:r.id,geometry:{type:'Point',coordinates:[r.longitude,r.latitude]},properties:{id:r.id,name:r.name,operator:r.operator,state:r.state,status:r.status,segment:r.segment,capacity_mw:r.capacity_mw,capacity_basis:r.capacity_basis,land_acres:r.land_acres,location_precision:r.location_precision}}))},{headers:{...headers,'Content-Disposition':'attachment; filename="Syncranicity_US_Data_Centers.geojson"'}});
 if(format==='all')return Response.json({...dataset,summary:dataCenterSummary(),evidence:evidenceData},{headers});
 if(format==='summary')return Response.json({as_of:dataset.as_of,summary:dataCenterSummary(),methodology:dataset.methodology,audit:dataset.audit},{headers});
 const offset=Math.max(0,Math.floor(Number(p.get('offset'))||0)),limit=Math.min(200,Math.max(1,Math.floor(Number(p.get('limit'))||50)));
 return Response.json({total:rows.length,offset,limit,rows:rows.slice(offset,offset+limit)},{headers});
}
