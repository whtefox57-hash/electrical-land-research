// Convert the official, generalized Census ZIP to county context and a dated ledger.
// This is cartographic context, never a parcel or jurisdiction suitability layer.
import fs from 'node:fs';
import {inflateRawSync} from 'node:zlib';
import {createHash} from 'node:crypto';
const input=process.argv[2];if(!input)throw Error('Supply the downloaded Census county ZIP');
const zip=fs.readFileSync(input),files=new Map();let end=zip.length-22;
while(end>=0&&zip.readUInt32LE(end)!==0x06054b50)end--;
if(end<0)throw Error('ZIP directory missing');
let offset=zip.readUInt32LE(end+16);const entries=zip.readUInt16LE(end+10);
for(let n=0;n<entries;n++){if(zip.readUInt32LE(offset)!==0x02014b50)throw Error('Invalid ZIP directory');const method=zip.readUInt16LE(offset+10),size=zip.readUInt32LE(offset+20),len=zip.readUInt16LE(offset+28),extra=zip.readUInt16LE(offset+30),comment=zip.readUInt16LE(offset+32),local=zip.readUInt32LE(offset+42),name=zip.subarray(offset+46,offset+46+len).toString();const start=local+30+zip.readUInt16LE(local+26)+zip.readUInt16LE(local+28),compressed=zip.subarray(start,start+size);files.set(name,method===0?compressed:method===8?inflateRawSync(compressed):null);offset+=46+len+extra+comment;}
const file=ext=>{const value=[...files].find(([n])=>n.endsWith(ext))?.[1];if(!value)throw Error('Missing '+ext);return value};
const dbf=file('.dbf'),shp=file('.shp'),num=dbf.readUInt32LE(4),header=dbf.readUInt16LE(8),recordSize=dbf.readUInt16LE(10),fields=[];let fieldOffset=1;
for(let i=32;dbf[i]!==13;i+=32){const name=dbf.subarray(i,i+11).toString().replace(/\0.*$/,'');const length=dbf[i+16];fields.push({name,offset:fieldOffset,length});fieldOffset+=length;}
const records=Array.from({length:num},(_,i)=>Object.fromEntries(fields.map(f=>[f.name,dbf.subarray(header+i*recordSize+f.offset,header+i*recordSize+f.offset+f.length).toString('utf8').trim()])));
const signed=ring=>ring.slice(1).reduce((a,p,i)=>a+ring[i][0]*p[1]-p[0]*ring[i][1],0);
const contains=(ring,p)=>{let yes=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes};
const geometries=[];for(let i=100;i<shp.length;){const size=shp.readInt32BE(i+4)*2,start=i+8,type=shp.readInt32LE(start);if(type!==5)throw Error('Only polygon county shapes supported');const parts=shp.readInt32LE(start+36),points=shp.readInt32LE(start+40),starts=Array.from({length:parts},(_,j)=>shp.readInt32LE(start+44+j*4)),base=start+44+parts*4;starts.push(points);const rings=starts.slice(0,-1).map((a,j)=>Array.from({length:starts[j+1]-a},(_,k)=>[shp.readDoubleLE(base+(a+k)*16),shp.readDoubleLE(base+(a+k)*16+8)]));const polys=rings.filter(r=>signed(r)<0).map(r=>[r]);for(const hole of rings.filter(r=>signed(r)>=0)){const parent=polys.find(p=>contains(p[0],hole[0]));if(!parent)throw Error('Orphan county hole');parent.push(hole);}geometries.push(polys.length===1?{type:'Polygon',coordinates:polys[0]}:{type:'MultiPolygon',coordinates:polys});i=start+size;}
if(records.length!==geometries.length)throw Error('DBF/geometry record mismatch');
const states=Object.fromEntries('01 AL,02 AK,04 AZ,05 AR,06 CA,08 CO,09 CT,10 DE,11 DC,12 FL,13 GA,15 HI,16 ID,17 IL,18 IN,19 IA,20 KS,21 KY,22 LA,23 ME,24 MD,25 MA,26 MI,27 MN,28 MS,29 MO,30 MT,31 NE,32 NV,33 NH,34 NJ,35 NM,36 NY,37 NC,38 ND,39 OH,40 OK,41 OR,42 PA,44 RI,45 SC,46 SD,47 TN,48 TX,49 UT,50 VT,51 VA,53 WA,54 WV,55 WI,56 WY'.split(',').map(s=>s.trim().split(' ')));
const source='https://www2.census.gov/geo/tiger/GENZ2025/shp/cb_2025_us_county_20m.zip',retrieved=new Date().toISOString();
const rows=records.map((r,i)=>({type:'Feature',id:r.GEOID,properties:{county_fips:r.GEOID,GEOID:r.GEOID,NAME:r.NAME,county:r.NAME,state:states[r.STATEFP]||r.STATEFP,state_fips:r.STATEFP,status:'NOT_COLLECTED',parcel_count:null,complete:false},geometry:geometries[i]}));
const features=rows.filter(f=>states[f.properties.state_fips]),territories=rows.filter(f=>!states[f.properties.state_fips]);if(new Set(features.map(f=>f.id)).size!==features.length||new Set(features.map(f=>f.properties.state)).size!==51)throw Error('County identity or state coverage mismatch');
const metadata={id:'census-2025-counties',total:features.length,vintage:'2025 Census cartographic boundaries (1:20 million)',source,retrieved_at:retrieved,sha256:createHash('sha256').update(zip).digest('hex'),state_count:51,scope:'50 states and District of Columbia; territories tracked separately',territory_count:territories.length,geometry_crs:'NAD83 geographic; generalized context only',national_complete:false,county_parcel_complete:0,parcel_denominator:null,limitations:'Census 2026 REST access was rejected; 2025 dated geography is used explicitly. Generalized boundaries are not legal boundary evidence.'};
fs.mkdirSync('public/atlas',{recursive:true});fs.mkdirSync('data/atlas',{recursive:true});
fs.writeFileSync('public/atlas/counties.geojson',JSON.stringify({type:'FeatureCollection',metadata,features}));
fs.writeFileSync('data/atlas/county-ledger.json',JSON.stringify({metadata,counties:features.map(f=>f.properties),territories:territories.map(f=>f.properties)},null,2));
console.log(JSON.stringify({...metadata,geometry_records:features.length}));
