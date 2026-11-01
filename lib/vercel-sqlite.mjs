import { DatabaseSync } from 'node:sqlite';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

// One isolated SQLite copy per request. /tmp is never the durable authority.
// The caller must commit the complete image using the storage ETag it read.
export async function openSQLite(bytes) {
  const directory = await mkdtemp(join(tmpdir(), 'syncranicity-'));
  const filename = join(directory, 'request.sqlite');
  let sql;
  try {
    await writeFile(filename, bytes);
    sql = new DatabaseSync(filename, { enableForeignKeyConstraints: true, enableDoubleQuotedStringLiterals: true });
    sql.exec('PRAGMA journal_mode=DELETE; PRAGMA trusted_schema=OFF;');
  } catch (error) {
    sql?.close();
    await rm(directory, { recursive: true, force: true });
    throw error;
  }
  let dirty = false;
  const values = args => args.map(v => v === undefined ? null : typeof v === 'boolean' ? Number(v) : v);
  const execute = (text, args) => {
    const statement = sql.prepare(text);
    const before = sql.prepare('SELECT total_changes() AS n').get().n;
    const results = statement.all(...values(args));
    const changes = Number(sql.prepare('SELECT changes() AS n').get().n);
    if (sql.prepare('SELECT total_changes() AS n').get().n !== before) dirty = true;
    return { success: true, results, meta: { changes } };
  };
  const adapter = {
    prepare(text) {
      let args = [];
      const prepared = {
        bind(...input) { args = input; return prepared; },
        async all() { return execute(text, args); },
        async run() { return execute(text, args); },
        async first(column) { const row = execute(text, args).results[0] ?? null; return column && row ? row[column] : row; },
        _execute() { return execute(text, args); },
      };
      return prepared;
    },
    async batch(statements) {
      const priorDirty = dirty;
      sql.exec('BEGIN IMMEDIATE');
      try { const results = statements.map(s => s._execute()); sql.exec('COMMIT'); return results; }
      catch (error) { sql.exec('ROLLBACK'); dirty = priorDirty; throw error; }
    },
    async exec(text) { sql.exec(text); dirty = true; },
  };
  return {
    adapter,
    get dirty() { return dirty; },
    async bytes() { return readFile(filename); },
    integrity() { return sql.prepare('PRAGMA integrity_check').get().integrity_check === 'ok'; },
    async close() { sql.close(); await rm(directory, { recursive: true, force: true }); },
  };
}

export async function commitSQLite(session, expectedETag, storage) {
  if (!session.dirty) return;
  const bytes = await session.bytes();
  const receipt = await storage.put(bytes, expectedETag);
  const saved = await storage.get();
  if (!receipt.etag || saved?.etag !== receipt.etag || !Buffer.from(saved.bytes).equals(bytes)) {
    throw Error('Storage readback could not confirm this save. Refresh and inspect the saved state before retrying.');
  }
}
