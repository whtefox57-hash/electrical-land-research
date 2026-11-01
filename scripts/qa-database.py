from pathlib import Path
import sqlite3,json
p=next(p for p in Path('.wrangler/state/v3/d1').rglob('*.sqlite') if p.name!='metadata.sqlite');c=sqlite3.connect(p);r=c.execute("SELECT data,version FROM workspace WHERE id='main'").fetchone();s=json.loads(r[0]);print(json.dumps({'version':r[1],'records':len(s['records']),'reports':[{'id':x['id'],'runId':x['runId']} for x in s['reports']],'notes':sum(len(x['noteEntries']) for x in s['records']),'tasks':len(s['tasks'])}))
