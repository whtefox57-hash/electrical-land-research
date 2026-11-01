import {withDatabase} from '@/lib/vercel-runtime';
import {vaultEnvironment} from '@/lib/vercel-runtime';
import { cartoCredential } from '@/lib/carto-credential.mjs';
export const dynamic = 'force-dynamic';
const GETHandler = (req: Request) => cartoCredential(ownerRequest(req), vaultEnvironment());
const PUTHandler = (req: Request) => cartoCredential(ownerRequest(req), vaultEnvironment());
const DELETEHandler = (req: Request) => cartoCredential(ownerRequest(req), vaultEnvironment());

function ownerRequest(req:Request){const h=new Headers(req.headers);h.set('oai-authenticated-user-email',process.env.ATLAS_SETTINGS_OWNER_EMAIL||'');return new Request(req,{headers:h});}

export const GET=withDatabase(GETHandler);
export const PUT=withDatabase(PUTHandler);
export const DELETE=withDatabase(DELETEHandler);
