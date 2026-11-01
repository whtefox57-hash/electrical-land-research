import raw from '@/data/data-center-registry.json';
import evidence from '@/data/data-center-evidence.json';
import type {DCDataset,DCRecord} from './data-center-types';
import {displayCategory} from './data-center-types';
export const dataset=raw as unknown as DCDataset;
export const evidenceData=evidence as any;
const evidenceMap=new Map<string,any>(evidenceData.records.map((r:any)=>[r.id,r]));
export function relatedEvidence(r:DCRecord){return r.evidence_ids.map(id=>evidenceMap.get(id)).filter(Boolean)}
export function filterDataCenters(p:URLSearchParams){
 const q=(p.get('q')||'').trim().toLowerCase();
 return dataset.records.filter(r=>(!q||[r.name,r.operator,r.address,r.city,r.county,r.state,r.land_purchaser].join(' ').toLowerCase().includes(q))&&(!p.get('state')||r.state===p.get('state'))&&(!p.get('status')||r.status===p.get('status'))&&(!p.get('category')||displayCategory(r)===p.get('category')));
}
export function dataCenterSummary(){const r=dataset.records;return {total:r.length,mapped:r.filter(x=>x.latitude!=null&&x.longitude!=null).length,power:r.filter(x=>x.capacity_mw!=null).length,acreage:r.filter(x=>x.land_acres!=null).length,operator:r.filter(x=>x.operator).length,purchaser:r.filter(x=>x.land_purchaser).length,transactions:r.filter(x=>relatedEvidence(x).some(e=>e.land_transactions.length)).length,approvals:r.filter(x=>relatedEvidence(x).some(e=>e.approvals.length)).length,evidence_cases:evidenceData.records.length,distinct_transactions:evidenceData.records.reduce((n:number,e:any)=>n+e.land_transactions.length,0),states:[...new Set(r.map(x=>x.state))].sort(),status:Object.fromEntries([...new Set(r.map(x=>x.status))].map(s=>[s,r.filter(x=>x.status===s).length])),categories:Object.fromEntries(['hyperscale','large','smaller','unknown','crypto'].map(s=>[s,r.filter(x=>displayCategory(x)===s).length]))}}
export function csvExport(rows:DCRecord[]){const keys=['id','name','operator','developer','land_purchaser','address','city','county','state','status','record_type','segment','size_band','capacity_mw','capacity_basis','actual_usage_mw','land_acres','acreage_basis','building_sqft','latitude','longitude','location_precision','parent_id','evidence_ids','source_ids','review_status'];const cell=(v:any)=>{let s=v==null?'':Array.isArray(v)?v.join(' | '):String(v);if(/^[=+@\-]/.test(s)&&typeof v!=='number')s="'"+s;return '"'+s.replaceAll('"','""')+'"'};return '\uFEFF'+keys.join(',')+'\r\n'+rows.map(r=>keys.map(k=>cell((r as any)[k])).join(',')).join('\r\n')}
