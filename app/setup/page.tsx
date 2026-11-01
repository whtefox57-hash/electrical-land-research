import Link from 'next/link';
import { blobConfigured } from '@/lib/vercel-blob.mjs';
export const dynamic = 'force-dynamic';
export default function Setup() {
  return <main className="deployment-setup"><p className="eyebrow">SYNCRANICITY / VERCEL</p><h1>Deal Desk setup</h1>
    <p>The standalone application is deployed. {blobConfigured() ? 'Durable storage is configured; the current database still needs importing.' : 'Durable storage still needs connecting.'}</p>
    <ol><li>In the Vercel project, connect a <strong>private Blob store</strong> and its server-only storage credentials, then redeploy.</li><li>Export the complete live SQLite database, including workspace, documents, history, origination and atlas tables. A workspace JSON export alone is incomplete.</li><li>Upload that verified SQLite backup to <code>POST /api/migration</code> with <code>Content-Type: application/vnd.sqlite3</code>. This endpoint only creates an empty destination; it cannot overwrite an existing database.</li></ol>
    <p>The original private workspace remains available while migration is pending.</p><div className="setup-links"><a href="https://syncranicity-deal-desk.whtefox57.chatgpt.site">Open existing Deal Desk ↗</a><Link href="/">Check setup again</Link></div>
    <p className="muted">Scheduled research still delivers to the existing site. No schedules or keys have been transferred.</p></main>;
}
