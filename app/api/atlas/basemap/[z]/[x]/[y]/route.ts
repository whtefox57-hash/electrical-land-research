import {withDatabase} from '@/lib/vercel-runtime';
import {vaultEnvironment} from '@/lib/vercel-runtime';
import {atlasBasemap} from '@/lib/atlas-basemap.mjs';
export const dynamic='force-dynamic';
const GETHandler=(req:Request)=>{
 const headers=new Headers(req.headers);
 headers.set('oai-authenticated-user-email',process.env.ATLAS_SETTINGS_OWNER_EMAIL||'');
 return atlasBasemap(new Request(req,{headers}), vaultEnvironment());
};

export const GET=withDatabase(GETHandler);
