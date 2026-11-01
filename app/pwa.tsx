'use client';
import { useEffect, useState } from 'react';
export default function PWA() {
  const [install, setInstall] = useState<any>(null);
  const [help, setHelp] = useState(false);
  useEffect(() => {
    if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {});
    const ready = (event: Event) => { event.preventDefault(); setInstall(event); };
    const installed = () => { setInstall(null); setHelp(false); };
    window.addEventListener('beforeinstallprompt', ready);
    window.addEventListener('appinstalled', installed);
    return () => { window.removeEventListener('beforeinstallprompt', ready); window.removeEventListener('appinstalled', installed); };
  }, []);
  return <aside className="pwa-actions" aria-label="App and source links">
    <a href="https://github.com/whtefox57-hash/electrical-land-research" target="_blank" rel="noreferrer">GitHub ↗</a>
    <button onClick={async () => { if (install) { await install.prompt(); await install.userChoice; setInstall(null); } else setHelp(!help); }}>Install app</button>
    {help && <span role="status">Chrome / Edge: use the address-bar install icon. iPhone: Safari → Share → Add to Home Screen.</span>}
  </aside>;
}
