'use client';
import { useEffect, useState } from 'react';
import { KeyRound, ShieldCheck } from 'lucide-react';
type Status = {configured:boolean;updated_at:string|null};
export default function CartoKeySettings(){
 const [status,setStatus]=useState<Status|null>(null),[apiKey,setApiKey]=useState(''),[busy,setBusy]=useState(false),[testing,setTesting]=useState(false),[message,setMessage]=useState(''),[error,setError]=useState('');
 async function load(){try{const r=await fetch('/api/atlas/carto-key',{cache:'no-store',credentials:'same-origin'});const b=await r.json();if(!r.ok)throw Error(b.error||'Key status unavailable.');setStatus(b);setError('');}catch(e){setError((e as Error).message);}}
 useEffect(()=>{void load()},[]);
 async function change(method:'PUT'|'DELETE'){
  if(busy)return;const value=apiKey;setApiKey('');setBusy(true);setMessage('');setError('');
  try{const r=await fetch('/api/atlas/carto-key',{method,cache:'no-store',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify(method==='PUT'?{api_key:value}:{})});const b=await r.json();if(!r.ok)throw Error(b.error||'Could not update the key.');setStatus(b);window.dispatchEvent(new Event('atlas-carto-changed'));setMessage(method==='PUT'?'CARTO key saved securely.':'CARTO key removed.');}
  catch(e){await load();setError((e as Error).message);}finally{setBusy(false);}
 }
 async function testConnection(){setTesting(true);setError('');setMessage('');try{const r=await fetch('/api/atlas/basemap/0/0/0.png?v='+Date.now(),{cache:'no-store',credentials:'same-origin'});if(!r.ok){const b=await r.json();throw Error(b.error||'Map connection failed.')}await r.arrayBuffer();setMessage('CARTO connected: an authenticated map tile loaded successfully.');window.dispatchEvent(new Event('atlas-carto-changed'));}catch(e){setError((e as Error).message)}finally{setTesting(false)}}
 return <div className="pa-key-settings"><div className="pa-key-heading"><ShieldCheck size={24}/><div><h2>CARTO connection</h2><p>Manage the API key for your private Parcel Atlas.</p></div></div>
 <div className="pa-key-status"><KeyRound size={17}/><strong>{status?status.configured?'Key saved':'No key saved':'Checking saved status…'}</strong>{status?.updated_at&&<span>Updated {new Date(status.updated_at).toLocaleString('en-US',{timeZone:'America/Phoenix'})}</span>}</div>
 <p>Your key is encrypted on the server. The saved key is never shown or included in parcel exports and backups.</p>
 <form onSubmit={e=>{e.preventDefault();void change('PUT')}} autoComplete="off">
 <label className="pa-control" htmlFor="pa-carto-api-key">{status?.configured?'Replace CARTO API key':'CARTO API key'}<input id="pa-carto-api-key" name="carto-api-key" type="password" autoComplete="off" spellCheck={false} autoCapitalize="none" maxLength={8192} value={apiKey} onChange={e=>setApiKey(e.target.value)} placeholder="Paste your CARTO API key" required disabled={busy} aria-describedby="pa-carto-key-help"/></label>
 <p id="pa-carto-key-help" className="pa-small">Use a CARTO Basemaps API key. The map uses it through the server; it never appears in browser tile URLs. If website restrictions are enabled, allow syncranicity-deal-desk.whtefox57.chatgpt.site. This does not purchase or upgrade a CARTO plan.</p>
 <div className="pa-key-actions"><button type="submit" className="pa-button" disabled={busy||!apiKey.trim()}>{busy?'Updating…':status?.configured?'Replace key':'Save key securely'}</button><button type="button" className="pa-button" disabled={busy||!status?.configured} onClick={()=>void change('DELETE')}>Remove key</button></div>
 </form><button type="button" className="pa-button" disabled={busy||testing||!status?.configured} onClick={()=>void testConnection()}>{testing?'Testing map connection…':'Test map connection'}</button>{message&&<p role="status" className="pa-notice">{message}</p>}{error&&<div role="alert" className="pa-notice pa-error">{error}<button type="button" onClick={load} disabled={busy}>Check status</button></div>}</div>;
}
