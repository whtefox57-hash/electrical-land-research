export function authorize(request:Request,write=false){
 // Sites dispatch enforces the owner-only audience before invoking the Worker.
 // It supplies and sanitizes the identity header. The development branch uses isolated local D1.
 const localPreview=import.meta.env.DEV;
 if(!localPreview&&!request.headers.get('oai-authenticated-user-email'))return Response.json({error:'Sign in through this private Site to continue.'},{status:401,headers:{'Cache-Control':'no-store'}});
 if(write){const origin=request.headers.get('origin');if(!origin||origin!==new URL(request.url).origin)return Response.json({error:'Same-origin request required.'},{status:403});if(!request.headers.get('content-type')?.includes('application/json'))return Response.json({error:'JSON required.'},{status:415});}
 return null;
}
