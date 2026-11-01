// Vercel Authentication protects ALL deployment URLs, functions and assets.
// Caller-supplied Sites identity headers are deliberately ignored.
export function authorize(request: Request, write = false) {
 if(process.env.VERCEL !== '1' || process.env.DEPLOYMENT_AUTH_BOUNDARY !== 'vercel-sso') return Response.json({error:'This deployment requires Vercel Authentication.'},{status:401,headers:{'Cache-Control':'no-store'}});
 if(write){
  const origin=request.headers.get('origin');
  if(!origin || origin!==new URL(request.url).origin) return Response.json({error:'Same-origin request required.'},{status:403});
  const contentType=request.headers.get('content-type')||'';
  if(!contentType.includes('application/json') && !(new URL(request.url).pathname==='/api/migration' && contentType.startsWith('application/vnd.sqlite3'))) return Response.json({error:'Unsupported content type.'},{status:415});
 }
 return null;
}
