export function GET() {
  return new Response('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#111827"><title>Deal Desk · Offline</title><body style="margin:0;background:#111827;color:#fff;font:18px system-ui;padding:12vh 8vw"><h1>You are offline</h1><p>Reconnect to open your private Deal Desk. Research and unsent changes are not cached on this device.</p><a href="/" style="color:#8ec5ff">Try again</a></body></html>', { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-cache' } });
}
