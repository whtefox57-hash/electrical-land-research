"""Private Site service caller. Credentials enter through hidden stdin only."""
import sys,json,urllib.request,urllib.error,pathlib
if sys.stdin.isatty():
 import termios
 old=termios.tcgetattr(sys.stdin.fileno());new=termios.tcgetattr(sys.stdin.fileno());new[3]&=~termios.ECHO;termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,new)
 print('Ready for private service input (hidden).',flush=True)
 try: config=json.loads(sys.stdin.readline())
 finally:termios.tcsetattr(sys.stdin.fileno(),termios.TCSANOW,old)
else:config=json.load(sys.stdin)
origin='https://syncranicity-deal-desk.whtefox57.chatgpt.site'
headers={'OAI-Sites-Authorization':'Bearer '+config['token'],'Content-Type':'application/json'}
def call(path,body=None):
 if not path.startswith('/api/origination'):raise ValueError('Only origination endpoints are supported')
 r=urllib.request.Request(origin+path,headers=headers,data=None if body is None else json.dumps(body).encode(),method='GET' if body is None else 'POST')
 try:
  with urllib.request.urlopen(r,timeout=60) as response:return json.load(response)
 except urllib.error.HTTPError as e:
  body=e.read().decode()[:800];raise RuntimeError(str(e.code)+' '+body) from None
if config.get('batch_files'):
 receipts=[]
 for f in config['batch_files']:
  payload=json.loads(pathlib.Path(f).read_text());receipt=call('/api/origination',payload)
  check=call('/api/origination?run_id='+payload['run_id'])
  if check.get('run',{}).get('hash')!=receipt.get('hash'):raise RuntimeError('Receipt hash mismatch')
  receipts.append(receipt);print(json.dumps({'run_id':receipt['run_id'],'records':receipt['record_count'],'verified':receipt['readback_verified'],'duplicate':receipt['duplicate']}),flush=True)
 if config.get('receipts_path'):pathlib.Path(config['receipts_path']).write_text(json.dumps(receipts,indent=2))
else:
 data=call(config.get('path','/api/origination?summary=1'),config.get('payload'))
 if config.get('save_path'):pathlib.Path(config['save_path']).write_text(json.dumps(data,indent=2));print(json.dumps({'saved':config['save_path'],'keys':list(data)}))
 else:print(json.dumps(data))
