from pathlib import Path
import json,hashlib,shutil
root=Path(__file__).resolve().parents[1];p=Path('/workspace/scratch/e48b251efe6f/research-extract/benson-gis');d=json.loads((p/'ingestion-report.json').read_text())
original=(p/'REPORT.md').read_text().strip();report={'schemaVersion':1,'producerId':d['producerId'],'runId':d['runId'],'producedAt':d['producedAt'],'title':d['title'],'recordIds':d['recordIds'],'original':original,'findings':[{'recordId':f['recordId'],'text':f['title']+': '+f['claim']+' Limit: '+f['limitations'],'sourceUrl':f['sourceUrls'][0],'sourceDate':f['retrievedAt']} for f in d['findings']]}
(root/'data/current-report.json').write_text(json.dumps(report,indent=2))
# Preserve only primary evidence, manifests and findings; exclude research scripts from user document collection.
t=root/'data/current-benson';t.mkdir(exist_ok=True)
for f in p.iterdir():
 if f.is_file() and f.suffix in ['.json','.md','.geojson']:shutil.copy2(f,t/f.name)
print('Real research report normalized:',len(report['findings']),'findings. Original bytes:',len(original))
