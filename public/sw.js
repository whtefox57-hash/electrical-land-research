const CACHE = 'syncranicity-public-shell-v1';
const PUBLIC = ['/offline', '/home-icon-v2-192.png', '/home-icon-v2-512.png'];
self.addEventListener('install', event => { event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PUBLIC))); self.skipWaiting(); });
self.addEventListener('activate', event => { event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('syncranicity-public-shell-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin || event.request.method !== 'GET') return;
  // Never put workspace pages, APIs, downloads, credentials or auth into CacheStorage.
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(async () => (await caches.open(CACHE)).match('/offline')));
  } else if (PUBLIC.includes(url.pathname)) {
    event.respondWith(fetch(event.request).catch(async () => (await caches.open(CACHE)).match(url.pathname)));
  }
});
