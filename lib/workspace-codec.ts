import {gzipSync,gunzipSync} from 'node:zlib';
import {Buffer} from 'node:buffer';
import type {Desk} from './model';

// Keep the logical workspace and snapshots complete while staying below D1's
// 2 MB cell/row limit. Legacy plain JSON remains readable without a migration.
const encoding='syncranicity-gzip-base64-v1';
export function encodeWorkspace(data:Desk):string{
 const json=JSON.stringify(data);
 const stored=Buffer.byteLength(json)<1000000?json:JSON.stringify({encoding,payload:gzipSync(json,{level:1}).toString('base64')});
 if(Buffer.byteLength(stored)>1900000)throw Error('Workspace exceeds the safe storage limit. Existing research is unchanged; export and split the workspace before adding more.');
 return stored;
}
export function decodeWorkspace(stored:string):Desk{
 const value=JSON.parse(stored);
 if(value?.encoding===encoding){
  if(typeof value.payload!=='string')throw Error('Invalid workspace storage envelope.');
  return JSON.parse(gunzipSync(Buffer.from(value.payload,'base64'),{maxOutputLength:32*1024*1024}).toString('utf8'));
 }
 if(value?.encoding)throw Error('Unsupported workspace storage encoding.');
 return value;
}
