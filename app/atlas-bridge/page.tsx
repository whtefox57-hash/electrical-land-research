'use client';
import {useEffect,useState} from 'react';
const ATLAS='https://syncranicity-atlas.whtefox57.chatgpt.site';
const fields=['id','name','recordType','apn','state','county','updatedAt','lifecycle','summary','thesis','moneyVerdict','facts','sections','checks','sources','actions','geometry','geometrySource','location','priority_tier','workflow_stage','evidence_status','capital_status','intelligence','kill','mapOverlays'];
// Read-only, same-user bridge. Authentication stays on the existing Deal Desk API.
export default function AtlasBridge(){
 const [status,setStatus]=useState('Waiting for Atlas');
 useEffect(()=>{
  let dead=false,busy=false,nonce='',revision:any=null;
  const send=(payload:any)=>{if(nonce&&!dead)window.parent.postMessage({type:'syncranicity:desk-data',nonce,...payload},ATLAS);};
  async function sync(){if(busy||!nonce)return;busy=true;try{
   const check=await fetch('/api/revision',{credentials:'same-origin',cache:'no-store'});if(!check.ok)throw new Error('Sign in to Deal Desk to connect current research.');const rev:any=await check.json();if(rev.version===revision)return;
   const r=await fetch('/api/desk',{credentials:'same-origin',cache:'no-store'});if(!r.ok)throw new Error('Current Deal Desk research is unavailable.');const d:any=await r.json();if(!Array.isArray(d.data?.records))throw new Error('Unexpected research format');
   revision=d.version;send({records:d.data.records.map((r:any)=>Object.fromEntries(fields.filter(k=>k in r).map(k=>[k,r[k]]))),revision,updatedAt:new Date().toISOString()});setStatus('Atlas connected · read only');
  }catch(e:any){send({error:e.message});setStatus(e.message);}finally{busy=false;}}
  function receive(e:MessageEvent){if(e.origin!==ATLAS||e.source!==window.parent||e.data?.type!=='syncranicity:desk-connect'||typeof e.data.nonce!=='string'||e.data.nonce.length>100)return;nonce=e.data.nonce;revision=null;void sync();}
  window.addEventListener('message',receive);window.parent.postMessage({type:'syncranicity:desk-ready'},ATLAS);const timer=setInterval(sync,90000);return()=>{dead=true;clearInterval(timer);window.removeEventListener('message',receive);};
 },[]);
 return <main style={{padding:24,fontFamily:'system-ui'}}><h1>Atlas research connection</h1><p>{status}</p><p>Existing sign-in is required. This connection shares site research with your Atlas and cannot edit Deal Desk.</p><a href="/">Open Deal Desk</a></main>;
}
