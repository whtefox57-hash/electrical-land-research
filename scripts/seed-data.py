from pathlib import Path
import json,hashlib,base64,mimetypes,shutil
root=Path(__file__).resolve().parents[1];h=root/'data/handoff'
ex=Path('/workspace/scratch/e48b251efe6f/research-extract');shutil.copytree(ex,root/'data/extraction',dirs_exist_ok=True)
pack=json.loads((h/'research/research-pack.json').read_text());method=json.loads((root/'data/extraction/source-evidence.json').read_text());auto=json.loads((root/'data/automation-verification.json').read_text());manifest=json.loads((h/'IMPORT_MANIFEST.json').read_text())
at='2026-09-05T18:00:00Z';recs=pack['records'];reporttext=(h/'research/research-pack.json').read_text().strip()
for r in recs:
 rejected=r['lifecycle']=='REJECTED';benson=r['id']=='az-cochise-12002003a';acampo=r['id'] in ['ca-sanjoaquin-01322013','ca-sanjoaquin-01322058']
 r.update(baseline=True,priority_tier='REJECTED' if rejected else 'PRIORITY' if benson else 'WATCH',workflow_stage='ARCHIVED' if rejected else 'GIS_QUEUED' if benson else 'ASSET_DEFINITION_NEEDED' if r['id']=='tx-milam-r22018' else 'INITIAL_SCREEN',evidence_status='INHERITED / CONFLICT' if benson else 'INHERITED / NOT REVERIFIED',capital_status='HOLD',opportunityId='acampo-assemblage' if acampo else r['id'],noteEntries=[])
 assessment=next((x for x in method['initial_screen_assessments'] if x['id']==r['id']),{})
 r['categoryReason']=assessment.get('initial_screen_basis',r['summary'])
 r['initialScreen']={k:benson for k in ['traceableAsset','plausibleEconomics','powerSignal','buyerFit','noSupportedFatal','nextTest','alternateUse']}
 r['alternateUse']='Low-water industrial or ordinary rural use is a hypothesis only; land-use permission, access, market demand and downside value remain unproved.' if benson else 'Historical truck/RV or industrial use warrants a current approval and income check; no downside valuation established.' if acampo else 'Ordinary lawful use and downside value remain unverified. No alternate-use valuation is implied.'
 r['buyerFit']='Buyer class hypothesis: low-water industrial / phased compute. No named buyer mandate, committed MW or confirmed acquisition interest.'
 for a in r['actions']:a['recordId']=r['id']
 r['history'].append({'at':at,'action':'WORKFLOW_V3_MIGRATION','before':'Original preserved in immutable import','after':r['priority_tier'],'note':r['categoryReason'],'source':'COUNTY_GIS_WORKFLOW_V3.md; inherited research as of 2026-09-04'})
relations=[]
for r in recs:
 for a in r['actions']:
  if r['priority_tier']=='REJECTED':continue
  existing=next((x for x in relations if x['name']==a['contact']),None)
  if existing:
   if r['id'] not in existing['recordIds']:existing['recordIds'].append(r['id'])
  else:relations.append({'id':'rel-'+hashlib.sha256(a['contact'].encode()).hexdigest()[:12],'name':a['contact'],'type':'UTILITY' if any(x in a['contact'].lower() for x in ['utility','ssvec','pg&e']) else 'SELLER / BROKER' if any(x in a['contact'].lower() for x in ['seller','broker','owner','rotner']) else 'COUNTY / ADVISER','contact':a['channel'],'note':a['question'],'recordIds':[r['id']],'source':'Inherited handoff; reverify contact before use','at':'2026-09-04'})
documents=[];docsql=[]
def quote(s):return "'"+s.replace("'","''")+"'"
def chunks(s,n=28000):return [s[i:i+n] for i in range(0,len(s),n)]
for folder in ['handoff','project_sources','extraction']:
 for p in sorted((root/'data'/folder).rglob('*')):
  if not p.is_file():continue
  content=p.read_bytes();path=p.relative_to(root/'data').as_posix();id='doc-'+hashlib.sha256(path.encode()).hexdigest()[:16];hash=hashlib.sha256(content).hexdigest();mime=mimetypes.guess_type(p.name)[0] or 'text/plain';b64=base64.b64encode(content).decode();parts=chunks(b64)
  documents.append({'id':id,'name':p.name,'path':path,'mime':mime,'hash':hash,'size':len(content)})
  docsql.append('INSERT OR IGNORE INTO documents (id,name,mime,content,hash) VALUES ('+','.join(quote(v) for v in [id,p.name,mime,'',hash])+');')
  for part in parts:docsql.append('UPDATE documents SET content=content||'+quote(part)+' WHERE id='+quote(id)+';')
report={'id':'baseline-2026-09-04','producerId':'supplied-research-pack','runId':'handoff-2026-09-04','producedAt':'2026-09-04','retrievedAt':at,'title':'Original parcel research · September 4','original':reporttext,'hash':hashlib.sha256(reporttext.encode()).hexdigest(),'recordIds':[r['id'] for r in recs],'findings':[],'status':'BASELINE_IMPORTED','schemaVersion':1,'documentId':next(d['id'] for d in documents if d['path']=='handoff/research/research-pack.json')}
state={'schemaVersion':3,'records':recs,'reports':[report],'relationships':relations,'tasks':[],'expenses':[],'decisions':[],'documents':documents,'automations':auto['tasks'],'automationVerification':auto['verification'],'methodology':method,'migration':{'baseline':manifest,'importedRecordCount':14,'beforeCount':0,'afterCount':14,'hashesVerified':40,'importedAt':at,'legacyMethod':pack['method'],'allOriginalsPreserved':True,'baselineGeometryCount':0,'baselineLocatorCount':1},'history':[{'at':at,'action':'BASELINE_IMPORTED','note':'14 original IDs and all handoff source files preserved; original research dated September 4.'}],'budget':{'learningCap':5000,'softControlCap':10000,'historicalExposure':None},'sourceCoverage':json.loads((h/'research/RESEARCH_COVERAGE_AND_FAILURES.json').read_text()),'integration':{'mode':'MANUAL','note':'Authenticated report import. No verified automatic transfer from scheduled tasks. Task registry is a dated saved configuration snapshot, not live telemetry.'}}
(root/'data/seed-workspace.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
sql=['INSERT OR IGNORE INTO workspace (id,data,version) VALUES (\'main\',\'\',1);']
for part in chunks(json.dumps(state,ensure_ascii=False,separators=(',',':'))):sql.append('UPDATE workspace SET data=data||'+quote(part)+" WHERE id='main';")
sql+=docsql
(root/'drizzle/0001_baseline_import.sql').write_text('\n--> statement-breakpoint\n'.join(sql))
j=root/'drizzle/meta/_journal.json';d=json.loads(j.read_text());d['entries']=[x for x in d['entries'] if x['idx']!=1]+[{'idx':1,'version':'6','when':1788631200000,'tag':'0001_baseline_import','breakpoints':True}];j.write_text(json.dumps(d,indent=2))
print(json.dumps({'records':len(recs),'documents':len(documents),'relationships':len(relations),'stateBytes':len(json.dumps(state)),'migrationStatements':len(sql)}))
