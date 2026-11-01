import {withDatabase} from '@/lib/vercel-runtime';
import {vaultEnvironment} from '@/lib/vercel-runtime';
import {atlasBasemap} from '@/lib/atlas-basemap.mjs';
export const dynamic='force-dynamic';
const GETHandler=(req:Request)=>atlasBasemap(req, vaultEnvironment());

export const GET=withDatabase(GETHandler);
