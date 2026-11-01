import { authorize } from '@/lib/auth';
import { createBlobStorage } from '@/lib/vercel-blob.mjs';
import { openSQLite } from '@/lib/vercel-sqlite.mjs';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const tables = ['workspace','documents','snapshots','origination_records','origination_events','origination_runs','atlas_entities','atlas_events','atlas_jobs','atlas_outbox','atlas_parcels','atlas_results','atlas_runs'];
export async function POST(req: Request) {
  const denied = authorize(req, true); if (denied) return denied;
  if (!req.headers.get('content-type')?.startsWith('application/vnd.sqlite3')) return Response.json({error:'A complete SQLite database is required.'},{status:415});
  // Vercel request-body limits apply before this handler. Larger imports need a server-side transfer.
  const bytes = new Uint8Array(await req.arrayBuffer());
  if (bytes.length > 4 * 1024 * 1024 || Buffer.from(bytes.slice(0,16)).toString() !== 'SQLite format 3\0') return Response.json({error:'Invalid or oversized SQLite import. Use a server-side migration for databases over 4 MB.'},{status:413});
  let session;
  try {
    const storage = createBlobStorage();
    if (await storage.get()) return Response.json({error:'Destination already exists. Import will not overwrite it.'},{status:409});
    session = await openSQLite(bytes);
    if (!session.integrity()) throw Error('SQLite integrity check failed.');
    const present = (await session.adapter.prepare("SELECT name FROM sqlite_master WHERE type='table'").all()).results.map((r: any) => r.name);
    if (tables.some(t=>!present.includes(t))) throw Error('Incomplete database: one or more required tables are missing.');
    const row = await session.adapter.prepare("SELECT version FROM workspace WHERE id='main'").first();
    if (!row) throw Error('The main workspace is missing.');
    const result = await storage.put(bytes, null);
    const saved = await storage.get();
    if (saved?.etag !== result.etag || !Buffer.from(saved.bytes).equals(Buffer.from(bytes))) throw Error('Import readback was not confirmed. Inspect the destination before retrying.');
    return Response.json({imported:true,workspaceVersion:row.version,tables:tables.length},{headers:{'Cache-Control':'private, no-store'}});
  } catch(error) { return Response.json({error:(error as Error).message},{status:503}); }
  finally { await session?.close(); }
}
