import {applyOct29} from './oct29-backfill';
import {applySept23} from './sept23-backfill';
import {applyOct13} from './oct13-backfill';
import {applyOct19} from './oct19-backfill';
import {applyOct19Screening} from './oct19-screening-backfill';
import {applyOct22} from './oct22-backfill';
import {applySept26} from './sept26-backfill';
import {applySeptemberBackfill} from './september-backfill';
import {applySept20} from './sept20-backfill';
import {applySept22} from './sept22-backfill';
import {importBuyerWatch} from './buyer-watch-import';
import buyerWatch from '@/data/research-sept23/buyer-watch.json';
import buyerWatchSept28 from '@/data/research-sept28/buyer-watch.json';
import recovery from '@/data/map-recovery-v2/recovery.json';
import registry from '@/data/task-registry-v2.json';
import type {Desk} from './model';
export function applySourceUpdates(s:Desk){
 let changed=false;
 if(!(s as any).appliedUpdates?.includes('desk-v2')){
 const at=registry.observedAt;
 for(const f of recovery.geometry.features){const p=f.properties as any;const r=s.records.find(r=>r.id===p.recordId);if(!r)continue;
  if(!r.geometry){r.geometry=f.geometry;r.geometrySource=p.geometry_source||p.sourceUrl||'San Joaquin County Public Works parcel service';(r as any).geometryRetrievedAt=p.retrieved_at||at;
   r.sources.push({id:'SJC-PARCEL-20260905',title:'County-published parcel geometry · September 2026',url:'https://services2.arcgis.com/GQhSReJEO6f7tsvy/arcgis/rest/services/Parcels/FeatureServer/0',publisher:'San Joaquin County Public Works',date:'September 2026',retrievedAt:at,kind:'EXACT_APN_POLYGON',limitation:'Tax/GIS parcel boundary only. Does not establish title, offered tract, development permission or availability.'});
   r.history.push({at,action:'OFFICIAL_GEOMETRY_ADDED',note:'Exact-APN county boundary recovered. Category, capital status and previous rejection preserved.'});
  }
 }
 s.automations=registry.tasks;
 (s as any).automationObservedAt=registry.observedAt;
 s.integration={mode:'MCP_READY_CONNECTION_REQUIRED',note:'Authenticated direct report intake is deployed. Connection and first scheduled delivery must be verified; no automatic chat-history mirror is claimed.'};
 s.reports.push({id:'sjc-boundaries-20260905',producerId:'official-map-recovery',runId:'sjc-eight-polygons-20260905',producedAt:at,retrievedAt:at,title:'Eight San Joaquin parcel boundaries recovered',original:recovery.report,hash:recovery.reportHash,recordIds:recovery.geometry.features.map(f=>(f.properties as any).recordId),findings:[],status:'NEEDS_REVIEW',schemaVersion:1});
 (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),'desk-v2'];
 s.history.push({at,action:'DESK_V2_SOURCE_UPDATE',note:'Eight exact parcel polygons added without changing founder decisions. Automation settings refreshed; no missing chat messages fabricated.'});changed=true;
 }
 if(!(s as any).appliedUpdates?.includes('desk-v2-platform-status')){
  s.integration={mode:'BLOCKED_ACCOUNT_CAPABILITY',note:'Automatic delivery is blocked: Sites MCP is not enabled for this Site owner (verified September 5, 2026). Scheduled research is not being mirrored here. The intake is built, but account enablement, task connection and a verified scheduled receipt are still required.'};
  (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),'desk-v2-platform-status'];changed=true;
 }
 const september=applySeptemberBackfill(s);const intake=applySept20(s);const additional=applySept22(s);const inference=applySept23(s);
 const marker='sept23-buyer-watch-import-v1';
 if(!(s as any).appliedUpdates?.includes(marker)){
  importBuyerWatch(s,buyerWatch,'SOURCE_BACKFILL');
  (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),marker];
  s.integration={mode:'BLOCKED_ACCOUNT_CAPABILITY',note:'September 23 Buyer Watch has been imported through a site update. Future Buyer Watch JSON exports can be uploaded with Import report. Scheduled delivery is still unverified: the account’s Sites MCP connection remains unavailable.'};
  changed=true;
 }
 const latest=applySept26(s);
 const sept28Marker='sept28-buyer-watch-import-v1';
 let sept28=false;
 if(!(s as any).appliedUpdates?.includes(sept28Marker)){
  importBuyerWatch(s,buyerWatchSept28,'SOURCE_BACKFILL');
  (s as any).appliedUpdates=[...((s as any).appliedUpdates||[]),sept28Marker];
  s.integration={mode:'BLOCKED_ACCOUNT_CAPABILITY',note:'September 28 Buyer Watch has been imported through an authorized source update. Recurring direct intake remains unavailable because Sites MCP is not enabled for this owner; future task runs still require a receipt/readback or another source update.'};
  sept28=true;
 }
 const october=applyOct13(s);
 const october19=applyOct19(s);
 const screening=applyOct19Screening(s);
 const optionReview=applyOct22(s);
 const oct29=applyOct29(s);
 return oct29||optionReview||screening||october19||october||sept28||latest||inference||additional||intake||september||changed;
}
