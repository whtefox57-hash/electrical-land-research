import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync(new URL('../data/data-center-registry.json',import.meta.url),'utf8'));
const evidence=JSON.parse(fs.readFileSync(new URL('../data/data-center-evidence.json',import.meta.url),'utf8'));
const records=data.records;
test('national inventory consists of 3000+ distinct sourced named records',()=>{
 assert.ok(records.length>=3000);
 assert.equal(new Set(records.map(r=>r.id)).size,records.length);
 assert.equal(records.filter(r=>/^Unnamed\b/i.test(r.name)).length,0);
 assert.equal(data.audit.retained_named_records,records.length);
 for(const r of records){assert.equal(r.country,'US');assert.match(r.state,/^[A-Z]{2}$/);assert.ok(r.source_record_ids.length);assert.ok(r.source_ids.length);assert.ok(r.name.trim());}
});
test('source references, acquisition joins and aliases resolve without duplicate ownership',()=>{
 const aliases=new Set();const cases=new Set(evidence.records.map(e=>e.id));
 for(const r of records){for(const s of r.source_ids)assert.ok(data.sources[s],r.id+': missing source '+s);for(const e of r.evidence_ids)assert.ok(cases.has(e));for(const id of r.source_record_ids){assert.ok(!aliases.has(id),'alias belongs to two records: '+id);aliases.add(id);}}
});
test('reported capacity and acreage never substitute for measured usage',()=>{
 for(const r of records){assert.equal(r.actual_usage_mw,null);assert.ok(r.land_acres===null||Number.isFinite(r.land_acres)&&r.land_acres>0);if(r.capacity_mw!==null){assert.ok(Number.isFinite(r.capacity_mw)&&r.capacity_mw>0);assert.ok(r.power.some(p=>p.mw===r.capacity_mw));assert.notEqual(r.capacity_basis,'not_established');}else assert.equal(r.size_band,'unknown');assert.notEqual(r.source_facility_type,'power_generation');assert.notEqual(r.source_facility_type,'crypto_mining');}
});
test('mapped coordinates are valid and no exact name-location duplicate survives',()=>{
 const seen=new Set();for(const r of records){assert.ok(r.latitude===null||r.latitude>=18&&r.latitude<=72);assert.ok(r.longitude===null||r.longitude>=-180&&r.longitude<=-66);const key=[r.name.toLowerCase(),r.state,r.latitude,r.longitude].join('|');assert.ok(!seen.has(key),key);seen.add(key)}
 assert.equal(data.audit.mapped_records,records.filter(r=>r.latitude!==null&&r.longitude!==null).length);
});
test('coverage claims disclose incomplete national and historical research',()=>{
 assert.equal(data.audit.complete_national_census,false);assert.equal(data.audit.actual_metered_mw_available,0);
 assert.equal(data.audit.with_land_acres,records.filter(r=>r.land_acres!==null).length);
 assert.equal(data.audit.with_reported_mw,records.filter(r=>r.capacity_mw!==null).length);
 assert.match(data.methodology.limitations,/not a complete U.S. census/);
});
