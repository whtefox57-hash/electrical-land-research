import {createHash} from 'node:crypto';
import data from '@/data/research-oct29.json';
import {applyEntities} from './research-upsert';
import type {Desk} from './model';
export function applyOct29(s:Desk){
 const marker='oct29-shortlist-v1',at='2026-10-29T20:00:00Z';
 if((s as any).appliedUpdates?.includes(marker))return false;
 const canonical:Record<number,string>={0:'tx-vernon-27899900',1:'fl-chiefland-fannin',3:'oct19-27254380',4:'oct19-3934635'};
 const ids:string[]=[];
 data.rows.forEach((c,i)=>{
 let r=s.records.find(x=>x.id===canonical[i])||s.records.find(x=>x.sources.some(src=>c.links.some(l=>l.url===src.url)));
 if(!r&&i===2)r=s.records.find(x=>/saginaw|705.*graham/i.test(x.name));
 if(!r&&i===7)r=s.records.find(x=>x.apn.includes('120-02-003A'));
 if(!r&&i===8)r=s.records.find(x=>/union center/i.test(x.name));
 if((r as any)?.screeningControl?.status==='STOPPED')return;
 const id=r?.id||c.id;
 const sources=c.links.map((l,j)=>({id:`OCT29-${i}-${j}`,title:l.title,url:l.url,publisher:'Public listing / offering source',date:'2026-10-29 review',retrievedAt:at,kind:'LISTING_REVIEW',limitation:'Marketing or directory/status link; does not prove deliverable power or accepted option terms.'}));
 applyEntities(s,{producerId:'founder-requested-research',runId:'research-2026-10-29',title:'October 29 option shortlist',summary:'Dated review added; existing founder decisions preserved',opportunities:[{id,...(!r?{name:c.name,state:c.name.match(/\b(TX|FL|MI|IN|ND|OH|AZ|WY|SC|AL|AR|CA)\b/)?.[0]||'Unknown',summary:c.summary}:{}),sources,facts:[{label:'October 29 option review',value:(c.rank?'Rank '+c.rank+' · ':'Watch / hold · ')+c.summary,status:'ANALYST REVIEW · NOT PAYMENT CLEARANCE',sourceIds:sources.map(x=>x.id)}]}],companies:[]},at);
 r=s.records.find(x=>x.id===id)!;
 r.sections.unshift({title:'October 29 decision and listing links',body:c.price+'\n'+c.risk+'\nFull review: /research-oct29',sourceIds:sources.map(x=>x.id)});
 ids.push(id);
 });
 s.reports.push({id:'research-2026-10-29',runId:'research-2026-10-29',producerId:'founder-requested-research',title:'October 29 · month-end option shortlist and listing links',producedAt:at,retrievedAt:at,original:data.markdown,hash:createHash('sha256').update(data.markdown).digest('hex'),recordIds:ids,findings:[],status:'NEEDS_REVIEW',schemaVersion:2});
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),marker];
 (s as any).latestOptionResearch={runId:'research-2026-10-29',asOf:'2026-10-29',deadline:'2026-10-31',conditionalChoiceId:'tx-vernon-27899900',paidControlReady:false,newSpend:0};
 return true;
}
