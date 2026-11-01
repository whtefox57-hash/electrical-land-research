// Minimal server-only Blob transport, following the official vercel/storage
// SDK API v13 wire contract. No tokens or storage URLs reach the browser.
// https://github.com/vercel/storage/tree/main/packages/blob/src
const pathname = 'deal-desk/workspace.sqlite';
const maxBytes = 96 * 1024 * 1024;
export function blobConfigured() {
  return Boolean(process.env.BLOB_READ_WRITE_TOKEN || (process.env.BLOB_STORE_ID && process.env.VERCEL_OIDC_TOKEN));
}
function auth() {
  const token = process.env.BLOB_READ_WRITE_TOKEN || process.env.VERCEL_OIDC_TOKEN;
  const id = process.env.BLOB_READ_WRITE_TOKEN?.split('_')[3] || process.env.BLOB_STORE_ID?.replace(/^store_/, '');
  if (!token || !id || !/^[a-zA-Z0-9]+$/.test(id)) throw Error('Connect a private Vercel Blob store before using the workspace.');
  return { token, id };
}
export function createBlobStorage(transport = fetch) {
  return {
    async get() {
      const { token, id } = auth();
      const response = await transport(`https://${id}.private.blob.vercel-storage.com/${pathname}?cache=0`, {
        headers: { Authorization: `Bearer ${token}` }, cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(45000),
      });
      if (response.status === 404) return null;
      if (!response.ok) throw Error(`Private storage read failed (${response.status}).`);
      if (Number(response.headers.get('content-length')) > maxBytes) throw Error('Workspace exceeds the verified snapshot size limit.');
      const bytes = Buffer.from(await response.arrayBuffer());
      if (bytes.length > maxBytes) throw Error('Workspace exceeds the verified snapshot size limit.');
      const etag = response.headers.get('etag');
      if (!etag) throw Error('Storage returned no version; refusing an unsafe save.');
      return { bytes, etag };
    },
    async put(bytes, expectedETag = null) {
      if (bytes.length > maxBytes) throw Error('Workspace exceeds the verified snapshot size limit.');
      const { token, id } = auth();
      const headers = {
        Authorization: `Bearer ${token}`, 'x-api-version': '13', 'x-vercel-blob-store-id': id,
        'x-vercel-blob-access': 'private', 'x-add-random-suffix': '0',
        'x-allow-overwrite': expectedETag ? '1' : '0', 'x-content-type': 'application/vnd.sqlite3',
        'x-cache-control-max-age': '60', ...(expectedETag ? { 'x-if-match': expectedETag } : {}),
      };
      const response = await transport(`https://blob.vercel-storage.com/?pathname=${encodeURIComponent(pathname)}`, {
        method: 'PUT', headers, body: bytes, cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(45000),
      });
      if ([409, 412].includes(response.status)) throw Error('CONFLICT: Another request saved first. Refresh before retrying; this request did not overwrite it.');
      if (!response.ok) throw Error(`Private storage save failed (${response.status}).`);
      return response.json();
    },
  };
}
