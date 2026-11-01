from pathlib import Path
import json,hashlib,mimetypes,base64
root=Path(__file__).resolve().parents[1]
s=json.loads((root/'data/seed-workspace.json').read_text());r=next(x for x in s['records'] if x['id']=='az-cochise-12002003a');p=json.loads((root/'data/current-benson/ingestion-report.json').read_text());report=json.loads((root/'data/current-report.json').read_text());at=p['producedAt']
report.update(id='benson-official-gis-20260905',hash=hashlib.sha256(report['original'].encode()).hexdigest(),retrievedAt=at,status='NEEDS_REVIEW')
s['reports'].append(report);
for x in s['records']:
 if x['id'] in ['ca-sanjoaquin-05926084','ca-sanjoaquin-05926086']:x['opportunityId']='eight-mile-road-pair'
 if x['id'] in ['ca-sanjoaquin-00517015','ca-sanjoaquin-00517016']:x['opportunityId']='peltier-road-pair'
 if x['id'] in ['ca-sanjoaquin-06308023','ca-sanjoaquin-06315041']:x['opportunityId']='harney-lane-pair'
r['geometry']=p['geometry'];r['geometrySource']=p['geometrySource'];r['evidence_status']='2026-09-05 GIS / OPEN CONFLICTS';r['updatedAt']='2026-09-05';r['workflow_stage']='GIS_IN_PROGRESS';r['summary']='Retain Priority for research; hold option money. Exact county polygon recovered and 26 whole-polygon layer checks completed. The county record itself contains the acreage conflict. Roads, an active electronic-range overlay, current use rules and legal offered boundaries still require resolution.'
r['categoryReason']='Initial screen passed under workflow v3. Source-linked GIS now supports targeted follow-up; current legal offering, road rights, military overlay applicability, use permission, utility MW and buildable area are not cleared.'
r['history'].append({'at':at,'action':'REPORT_RECEIVED','reportId':report['id'],'note':'Official Benson GIS report imported; 12 findings linked. Research status updated by build review; capital remains HOLD.'})
r['facts'].extend([{'label':'Current county acreage attributes','value':'115.45 parcel_size / 106.92 acres in the same official feature','status':'SOURCE CONFLICT · retrieved 2026-09-05','sourceIds':['BEN-GIS-PARCEL-20260905']},{'label':'Independent polygon calculation','value':'Approximately 106.80 acres in NAD83 / UTM Zone 12N. Net usable area UNKNOWN.','status':'GIS CALCULATION · not a deed or buildable acreage','sourceIds':['BEN-GIS-PARCEL-20260905']},{'label':'Electronic-range overlay','value':'Active Fort Huachuca Electronic Range feature intersects the parcel','status':'MAPPED FINDING · applicability requires interpretation','sourceIds':['BEN-GIS-MILITARY-20260905']}])
for old in r['checks']:old['historical']=True
for old in r['sections']:old['historical']=True
# IDs below are taken from the delivered findings, with field-level source links retained.
for f in p['findings']:
 sourceid=f['id'];r['sources'].append({'id':sourceid,'title':f['title'],'url':f['sourceUrls'][0],'publisher':'Official county-linked published GIS service','date':'See retained layer effective dates','retrievedAt':f['retrievedAt'],'kind':'FULL_POLYGON_QUERY','limitation':f['limitations']})
 r['checks'].append({'id':sourceid,'topic':f['title'],'status':f['resultStatus'],'result':f['claim'],'scope':f['scope'],'sourceIds':[sourceid],'checkedAt':f['retrievedAt'],'coverageNote':f['limitations']})
r['sections'].insert(0,{'title':'Fresh county GIS review · September 5','body':'Exact county polygon recovered; 69 published layers inventoried and 26 whole-polygon queries checked against independent result counts. Material findings include the acreage conflict, mapped roads, the active electronic-range overlay, two well-registry points and a utility-territory signal. Review the current findings below and the complete original report in Research Inbox; no legal access, available MW or buildable envelope is established.','sourceIds':[f['id'] for f in p['findings']]})
# Fix illustrative fact references to actual returned finding identifiers.
for f in r['facts'][-3:]:f['sourceIds']=[p['findings'][0]['id'] if 'acre' in f['label'].lower() or 'calculation' in f['label'].lower() else next(x['id'] for x in p['findings'] if 'military' in x['title'].lower() or 'electronic' in x['title'].lower())]
newaction={'id':'benson-gis-followup-20260905','recordId':r['id'],'order':1,'title':'Interpret the road rights and electronic-range overlay','contact':'Cochise County Planning / Recorder','channel':'Inherited Planning route: 520-432-9300; planning@cochise.az.gov — reverify before use','question':'For APN 120-02-003A, please identify the recorded N Aacco Trail corridor instrument and the applicable provisions for the active Fort Huachuca Electronic Range overlay. Which adopted use rules, including Ordinance 26-09 if applicable, govern this specific parcel and contemplated low-water industrial use?','decision':'Determine whether the mapped road and military overlay materially constrain the use/layout thesis before paying for control.','costEstimate':'$0 public-record follow-up; fees require approval','approvalRequired':True,'done':False}
r['actions'].insert(0,newaction)
for i,a in enumerate(r['actions']):a['order']=i+1
r['checks']=r['checks'][-len(p['findings']):]+r['checks'][:-len(p['findings'])]
overlays=[]
for lid,key,label,color in [(50,'roads','Mapped roads','#ce741f'),(1,'wells','Registry well points','#077c81'),(23,'military','Active electronic range','#8063b1')]:
 d=json.loads((root/f'data/current-benson/layer-{lid}-intersection.json').read_text());features=[]
 for f in d['features']:
  a=f['attributes'];g=f['geometry']
  if key=='military' and a.get('Active')!='Yes':continue
  if 'paths' in g:geo={'type':'MultiLineString','coordinates':g['paths']}
  elif 'x' in g:geo={'type':'Point','coordinates':[g['x'],g['y']]}
  elif 'rings' in g:geo={'type':'Polygon','coordinates':g['rings']}
  else:continue
  features.append({'type':'Feature','geometry':geo,'properties':{'name':a.get('fullrdname') or ('55-'+a['REGISTRY_ID'] if a.get('REGISTRY_ID') else label),'recordId':r['id']}})
 overlays.append({'id':key,'label':label,'color':color,'type':'line' if key=='roads' else 'circle' if key=='wells' else 'fill','data':{'type':'FeatureCollection','features':features},'retrievedAt':at,'limitation':'Published mapping only; no legal rights, usable water yield or development permission established.'})
r['mapOverlays']=overlays
s['history'].append({'at':at,'action':'OFFICIAL_GIS_REPORT_IMPORTED' ,'note':'Real report normalized, linked and retained. No automatic scheduled-task bridge is asserted.'})
sql=[]
def quote(v):return "'"+v.replace("'","''")+"'"
def chunks(v):return [v[i:i+28000] for i in range(0,len(v),28000)]
# Consolidated source bundle avoids flooding document navigation; all raw evidence stays in a single downloadable ZIP.
import zipfile
bundle=root/'data/Benson_GIS_Evidence_2026-09-05.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted((root/'data/current-benson').iterdir()):z.write(f,f.name)
files=[bundle,root/'data/current-benson/REPORT.md',root/'data/current-benson/benson-parcel.geojson',root/'data/current-benson/ingestion-report.json']
for f in files:
 path=f.relative_to(root/'data').as_posix();id='doc-'+hashlib.sha256(path.encode()).hexdigest()[:16];content=f.read_bytes();hash=hashlib.sha256(content).hexdigest();mime=mimetypes.guess_type(f.name)[0] or 'application/octet-stream';s['documents'].append({'id':id,'name':('Benson_GIS_Report_2026-09-05.md' if f.name=='REPORT.md' else f.name),'path':path,'mime':mime,'hash':hash,'size':len(content),'recordId':r['id']});sql.append('INSERT OR IGNORE INTO documents (id,name,mime,content,hash) VALUES ('+','.join(quote(v) for v in [id,f.name,mime,'',hash])+');')
 for part in chunks(base64.b64encode(content).decode()):sql.append('UPDATE documents SET content=content||'+quote(part)+' WHERE id='+quote(id)+';')
sql.append("UPDATE workspace SET data='',version=2 WHERE id='main';")
for part in chunks(json.dumps(s,ensure_ascii=False,separators=(',',':'))):sql.append('UPDATE workspace SET data=data||'+quote(part)+" WHERE id='main';")
(root/'data/current-workspace.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));(root/'drizzle/0002_benson_official_review.sql').write_text('\n--> statement-breakpoint\n'.join(sql));j=root/'drizzle/meta/_journal.json';d=json.loads(j.read_text());d['entries']=[x for x in d['entries'] if x['idx']!=2]+[{'idx':2,'version':'6','when':1788631500000,'tag':'0002_benson_official_review','breakpoints':True}];j.write_text(json.dumps(d,indent=2));print('Current migration prepared;',len(sql),'statements;',len(s['documents']),'documents;',len(s['reports']),'real reports')
