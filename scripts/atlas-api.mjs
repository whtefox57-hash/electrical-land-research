// Credentials arrive only on stdin. Usage: node scripts/atlas-api.mjs GET '/api/atlas?view=summary'
// or node scripts/atlas-api.mjs POST /api/atlas payload.json
import {readFile} from 'node:fs/promises';
const [method='GET',route='/api/atlas?view=summary',payloadPath]=process.argv.slice(2);
if(!['GET','POST'].includes(method)||!route.startsWith('/api/atlas')||route.includes('://'))throw Error('Only the atlas route is allowed');
let input='';for await(const chunk of process.stdin)input+=chunk;
const {token}=JSON.parse(input);if(typeof token!=='string'||!token)throw Error('Fresh Site service token required on stdin');
const response=await fetch('https://syncranicity-deal-desk.whtefox57.chatgpt.site'+route,{method,headers:{'OAI-Sites-Authorization':'Bearer '+token,...(method==='POST'?{'Content-Type':'application/json'}:{})},body:method==='POST'?await readFile(payloadPath,'utf8'):undefined,signal:AbortSignal.timeout(60000)});
const body=await response.text();if(!response.ok){process.stderr.write('Atlas HTTP '+response.status+'\n'+body);process.exitCode=1;}else process.stdout.write(body+'\n');
