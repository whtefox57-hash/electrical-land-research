export type DCSource = {id:string;title:string;url:string;license?:string;retrieved?:string;note?:string};
export type DCPower = {mw:number;basis:string;scope:string;status?:string;as_of?:string|null;source_ids:string[];note?:string};
export type DCRecord = {
 id:string;name:string;operator:string|null;developer:string|null;land_purchaser:string|null;
 address:string|null;city:string|null;county:string|null;state:string;country:string;
 latitude:number|null;longitude:number|null;location_precision:string;record_type:string;status:string;
 segment:string;segment_basis:string;size_band:string;capacity_mw:number|null;capacity_basis:string;
 power:DCPower[];actual_usage_mw:number|null;land_acres:number|null;acreage_basis:string|null;
 building_sqft:number|null;parent_id:string|null;source_ids:string[];source_record_ids:string[];
 evidence_ids:string[];notes:string[];review_status:string;updated_at:string|null;
 approval_context?:{status:string;text:string;source_ids:string[];review:string}|null;
 utility?:string|null;cooling?:string|null;water_notes?:string|null;status_history?:any[];
};
export type DCDataset = {schema_version:string;as_of:string;records:DCRecord[];sources:Record<string,DCSource>;methodology:Record<string,any>;audit:Record<string,any>};
export const segmentLabels:Record<string,string>={hyperscale:'Hyperscale / cloud',large:'Other large · ≥50 MW',smaller:'Smaller · <50 MW',unknown:'Size unknown',crypto:'Crypto / mining'};
export const segmentColors:Record<string,string>={hyperscale:'#6d54ce',large:'#156d83',smaller:'#bc8032',unknown:'#7f8b95',crypto:'#b04d67'};
export function displayCategory(r:Pick<DCRecord,'segment'|'size_band'>){return r.segment==='hyperscale'?'hyperscale':r.segment==='crypto'?'crypto':r.size_band==='large'?'large':r.size_band==='smaller'?'smaller':'unknown'}
export function numberOrUnknown(v:number|null|undefined,suffix=''){return v==null?'Not established':v.toLocaleString('en-US',{maximumFractionDigits:2})+suffix}
