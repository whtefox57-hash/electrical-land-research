import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeRun,registryKeyAliases} from '../lib/origination-validation.ts';
const listing={kind:'listing',id:'landsearch-1',data:{source_listing_id:'1',url:'https://example.com/1',state:'AL',disposition:'HOLD',decision_reason:'Missing power confirmation',next_action:'Read utility evidence',available_mw:null,residential_screen:{status:'UNKNOWN'},approval_history_status:'UNKNOWN',review_stage:'INDEX_ONLY'}};
test('unknown capacity and residential data can enter the hold queue',()=>assert.equal(normalizeRun({run_id:'one',records:[listing]}).records[0].data.available_mw,null));
test('seller power claim cannot create verified capacity',()=>assert.throws(()=>normalizeRun({run_id:'one',records:[{...listing,data:{...listing.data,available_mw:30}}]}),/utility evidence/));
test('index entries cannot be promoted without individual review',()=>assert.throws(()=>normalizeRun({run_id:'one',records:[{...listing,data:{...listing.data,disposition:'FURTHER_INVESTIGATION'}}]}),/index-only/));
test('county cannot be marked complete without source reconciliation',()=>assert.throws(()=>normalizeRun({run_id:'one',records:[{kind:'county',id:'01001',data:{state:'AL',complete:true}}]}),/completion requires/));
test('duplicate listing IDs are refused within a batch',()=>assert.throws(()=>normalizeRun({run_id:'one',records:[listing,listing]}),/Duplicate/));
test('updates preserve optimistic version guard',()=>assert.equal(normalizeRun({run_id:'one',records:[{...listing,expected_version:7}]}).records[0].expected_version,7));
test('qualified GET keys can be reused for POST without adding another prefix',()=>{
 const row=normalizeRun({run_id:'qualified',records:[{...listing,id:'listing:listing:landsearch-1',expected_version:3,data:{...listing.data,id:'landsearch-1'}}]}).records[0];
 assert.equal(row.id,'listing:landsearch-1');assert.equal(row.expected_version,3);
 assert.ok(registryKeyAliases('listing','landsearch-1').includes('listing:listing:landsearch-1'));
});
test('mixed bare and qualified copies cannot create two rows in one batch',()=>assert.throws(()=>normalizeRun({run_id:'duplicate-alias',records:[listing,{...listing,id:'listing:landsearch-1'}]}),/Duplicate/));
test('legacy normalization retains the old receipt identity for retries',()=>assert.equal(normalizeRun({run_id:'legacy',records:[{...listing,id:'listing:landsearch-1'}]},false).records[0].id,'listing:listing:landsearch-1'));
test('a conflicting data identity cannot overwrite another record',()=>assert.throws(()=>normalizeRun({run_id:'mismatch',records:[{...listing,data:{...listing.data,id:'landsearch-2'}}]}),/must match/));
