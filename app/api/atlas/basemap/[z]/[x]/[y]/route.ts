import {env} from 'cloudflare:workers';
import {atlasBasemap} from '@/lib/atlas-basemap.mjs';
export const dynamic='force-dynamic';
export const GET=(req:Request)=>atlasBasemap(req,env);
