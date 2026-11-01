import React from 'react';
import assert from 'node:assert/strict';
import {renderToStaticMarkup} from 'react-dom/server';
import {ResearchHub,ParcelDecision} from '../components/research-hub';
import {sept26Candidates} from '../lib/sept26-catalog';
(globalThis as any).React=React;
const html=renderToStaticMarkup(<ResearchHub/>);
assert.ok(html.includes('Foreman Bundy'));assert.ok(html.includes('September 26'));
assert.equal((html.match(/Review deal →/g)||[]).length,50);
for(const d of sept26Candidates){
 const card=renderToStaticMarkup(<ParcelDecision candidate={d}/>);
 assert.ok(card.includes('NOT ESTIMABLE'));assert.ok(card.includes(d.listingUrl.replaceAll('&','&amp;')));
 assert.ok(!card.includes('undefined/100'));assert.ok(card.includes(d.marketingDate));
}
assert.ok(renderToStaticMarkup(<ResearchHub mode="states"/>).includes('Explore all 50 states'));
assert.ok(renderToStaticMarkup(<ResearchHub mode="daily"/>).includes('50 additional listing leads'));
console.log('PASS: default 50-row queue, all 50 detail cards, state view and daily run render.');
