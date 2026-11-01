import assert from "node:assert/strict";
import test from "node:test";
import {Miniflare,Log} from "miniflare";

const developmentPreviewMeta =
  /<meta(?=[^>]*\bname=["']codex-preview["'])(?=[^>]*\bcontent=["']development["'])[^>]*>/i;

test("production page omits development preview metadata", async () => {
  const mf=new Miniflare({modules:true,scriptPath:'dist/server/index.js',modulesRules:[{type:'ESModule',include:['**/*.js','**/*.mjs'],fallthrough:true}],compatibilityDate:'2026-05-15',compatibilityFlags:['nodejs_compat'],d1Databases:['DB'],r2Buckets:['BUCKET'],assets:{directory:'dist/client',binding:'ASSETS',routerConfig:{has_user_worker:true,invoke_user_worker_ahead_of_assets:true}},log:new Log(0)});
  try {
    const response=await mf.dispatchFetch('https://desk.example/research-oct22');
    assert.equal(response.status,200);
    assert.match(response.headers.get('content-type')??'',/^text\/html\b/i);
    const html=await response.text();
    assert.match(html,/Hinds, if the terms/);
    assert.match(html,/No reviewed site is currently cleared for payment/);
    assert.doesNotMatch(html,developmentPreviewMeta);
  } finally { await mf.dispose(); }
});
