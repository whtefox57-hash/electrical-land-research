import { AsyncLocalStorage } from 'node:async_hooks';
import { openSQLite, commitSQLite } from './vercel-sqlite.mjs';
import { createBlobStorage, blobConfigured } from './vercel-blob.mjs';
import { authorize } from './auth';

const context = new AsyncLocalStorage<any>();
export function database() {
  const value = context.getStore();
  if (!value) throw Error('Database operations require an isolated request context.');
  return value.adapter;
}
export function withDatabase<T extends any[]>(handler: (...args: T) => Promise<Response> | Response) {
  return async (...args: T): Promise<Response> => {
    const denied = authorize(args[0]);
    if (denied) return denied;
    let session;
    try {
      if (!blobConfigured()) throw Error('Connect a private Vercel Blob store to complete setup.');
      const storage = createBlobStorage();
      const current = await storage.get();
      if (!current) throw Error('Import the current database at /setup. Historical source snapshots are not live data.');
      session = await openSQLite(current.bytes);
      const response = await context.run({ adapter: session.adapter }, () => handler(...args));
      if (response.status < 400) await commitSQLite(session, current.etag, storage);
      response.headers.set('Cache-Control', 'private, no-store');
      return response;
    } catch (error) {
      const message = (error as Error).message;
      return Response.json({ error: message }, { status: message.startsWith('CONFLICT') ? 409 : 503, headers: { 'Cache-Control': 'private, no-store' } });
    } finally { await session?.close(); }
  };
}

// Preserve the encrypted CARTO vault interface using private SQLite storage.
const object = async (key: string) => {
  const d = database();
  if (!await d.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='private_objects'").first()) await d.exec('CREATE TABLE private_objects (id TEXT PRIMARY KEY, value TEXT NOT NULL, uploaded TEXT NOT NULL)');
  return d.prepare('SELECT value,uploaded FROM private_objects WHERE id=?').bind(key).first();
};
export function vaultEnvironment() {
  return {
    ATLAS_CREDENTIAL_ENCRYPTION_KEY: process.env.ATLAS_CREDENTIAL_ENCRYPTION_KEY,
    ATLAS_SETTINGS_OWNER_EMAIL: process.env.ATLAS_SETTINGS_OWNER_EMAIL,
    CARTO_API_KEY: process.env.CARTO_API_KEY,
    BUCKET: {
      async get(key: string) { const row = await object(key); return row ? { json: async () => JSON.parse(row.value) } : null; },
      async head(key: string) { const row = await object(key); return row ? { uploaded: new Date(row.uploaded) } : null; },
      async put(key: string, value: string) { await object(key); return database().prepare('INSERT INTO private_objects(id,value,uploaded) VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET value=excluded.value,uploaded=excluded.uploaded').bind(key,value,new Date().toISOString()).run(); },
      async delete(key: string) { await object(key); return database().prepare('DELETE FROM private_objects WHERE id=?').bind(key).run(); },
    },
  };
}
