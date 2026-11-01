import fs from 'node:fs';
// Service access is session-only stdin. Source records are read from canonical files.
let raw='';for await(const chunk of process.stdin)raw+=chunk;const auth=raw.trim()?JSON.parse(raw):{};
const origin=process.argv[2]||'https://syncranicity-deal-desk.whtefox57.chatgpt.site';
if(!['https://syncranicity-deal-desk.whtefox57.chatgpt.site','http://127.0.0.1:8787'].includes(origin))throw Error('Unexpected destination');
const headers={'Content-Type':'application/json',...(auth.token?{'OAI-Sites-Authorization':'Bearer '+auth.token}:{})};
const api=async(path,body)=>{const r=await fetch(origin+path,{method:body?'POST':'GET',headers,...(body?{body:JSON.stringify(body)}:{}),signal:AbortSignal.timeout(60000)});const j=await r.json();if(!r.ok||j.error)throw Error('HTTP '+r.status+': '+JSON.stringify(j));return j;};
const seed=JSON.parse(fs.readFileSync('data/atlas/pilot-seed.json','utf8')),ledger=JSON.parse(fs.readFileSync('data/atlas/county-ledger.json','utf8'));
const coverage={kind:'coverage',id:ledger.metadata.id,expected_version:0,data:ledger.metadata};
const countyRows=ledger.counties.map(c=>({kind:'county',id:c.county_fips,expected_version:0,data:{...c,source_url:ledger.metadata.source,source_vintage:ledger.metadata.vintage,parcel_denominator:null,parcel_collection_complete:false,screening_complete:false}}));
const entities=[coverage,...seed.entities,...countyRows];let receipts=0;
async function commit(label,records,kind,size){for(let i=0;i<records.length;i+=size){const run_id='atlas-initial-20261031-v1:'+label+':'+i,payload={action:'import',run_id,[kind]:records.slice(i,i+size)};const result=await api('/api/atlas',payload);const verify=await api('/api/atlas?view=run&id='+encodeURIComponent(run_id));if(!result.readback_verified||verify.run?.hash!==result.hash)throw Error('Readback mismatch');console.log(JSON.stringify({run_id,records:records.slice(i,i+size).length,duplicate:!!result.duplicate,readback:true}));receipts++;}}
await commit('entities',entities,'entities',50);await commit('parcels',seed.parcels,'parcels',20);
const summary=await api('/api/atlas?view=summary');if(summary.counts.parcels<seed.parcels.length)throw Error('Stored count below imported data');const first=await api('/api/atlas?view=parcel&id='+encodeURIComponent(seed.parcels[0].id));if(JSON.stringify(first.geometry)!==JSON.stringify(seed.parcels[0].geometry))throw Error('Geometry readback differs');
console.log(JSON.stringify({status:'VERIFIED',receipts,counts:summary.counts,first_geometry_verified:true,national_complete:summary.national_complete}));
