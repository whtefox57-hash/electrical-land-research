'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="app-loading stack"><h1>This view could not load</h1><p>Saved research remains in the private database. Retry this view or return to Command.</p><button onClick={reset}>Retry</button><a className="source-link" href="/">Return to Command</a></main>}
