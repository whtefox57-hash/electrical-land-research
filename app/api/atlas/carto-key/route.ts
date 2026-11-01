import { env } from 'cloudflare:workers';
import { cartoCredential } from '@/lib/carto-credential.mjs';
export const dynamic = 'force-dynamic';
export const GET = (req: Request) => cartoCredential(req, env);
export const PUT = (req: Request) => cartoCredential(req, env);
export const DELETE = (req: Request) => cartoCredential(req, env);
