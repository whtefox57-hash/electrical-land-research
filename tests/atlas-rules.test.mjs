import test from 'node:test';
import assert from 'node:assert/strict';
import { profiles, rulesConfig, screenParcel, geometryMetrics, matchListing } from '../lib/atlas-rules.mjs';

// Deliberately synthetic fixtures; never imported into the production inventory.
const NOW = '2026-10-31T03:00:00Z';
const DATE = '2026-10-30T03:00:00Z';
const square = (x = -110, y = 31, size = 0.02) => ({ type: 'Polygon', coordinates: [[[x, y], [x + size, y], [x + size, y + size], [x, y + size], [x, y]]] });
const evidence = extra => ({ status: 'PASS', source_url: 'https://example.invalid/test-evidence', reason: 'Isolated test evidence; not an actual parcel assessment.', effective_date: DATE, retrieved_at: DATE, scope_match: true, evidence_level: 'V3', ...extra });
function candidate() {
  const geometry = square(), gross = geometryMetrics(geometry).computed_acres;
  return {
    id: 'test-parcel', apn: '000123', county_fips: '04003', geometry, geometry_version: 'fixture-geometry-1', snapshot_id: 'fixture-snapshot-1',
    source_url: 'https://example.invalid/test-official-gis', source_date: DATE, retrieved_at: DATE, evidence_level: 'V3', requested_facility_mw: 25,
    jurisdiction: evidence({ resolved: true, authorities: ['Test controlling authority'] }),
    coverage: {
      physical: evidence({ complete: true, layer_coverage: Object.fromEntries(rulesConfig.required_physical_layers.map(l => [l, 'COMPLETE'])) }),
      residential: evidence({ complete: true }),
    },
    residential: { nearest_confirmed_m: null, nearest_possible_m: null, counts: Object.fromEntries(rulesConfig.residential_bands_m.map(b => [String(b), { confirmed: 0, possible: 0 }])), measurement_reference: 'parcel_boundary', count_unit: 'buildings', sensitive_use_review_complete: true },
    layout: evidence({ version: 'test-layout-1', profile_id: 'inference', profile_version: '1.0', facility_mw: 25, fits: true, area_requirement_acres: 20, threshold_authority: 'Isolated test scenario assumption', systems_considered: [...rulesConfig.required_layout_systems] }),
    envelope: { version: 'test-envelope-1', validated: true, union_applied: true, geometry_version: 'fixture-geometry-1', profile_id: 'inference', profile_version: '1.0', method: 'Isolated fixture with no excluded area', source_url: 'https://example.invalid/test-envelope', computed_at: DATE, source_versions: { test: 'fixture-1' }, gross_acres: gross, excluded_union_acres: 0, usable_acres: gross, largest_block_acres: gross, components_acres: [gross] },
    restrictions: evidence({ status: 'PASS' }), context: evidence({ status: 'PASS' }),
  };
}
const failure = () => evidence({ status: 'FAIL', fatal: true, authority_type: 'adopted_rule', reason: 'Synthetic rule expressly excludes this use on this parcel.', reopening_criteria: 'The test rule is repealed or a lawful alternative is documented.' });
const offering = p => ({ id: 'test-listing', county_fips: p.county_fips, apn: p.apn, advertised_acres: geometryMetrics(p.geometry).computed_acres, offered_scope: 'whole_parcel', scope_verified: true, source_url: 'https://example.invalid/test-offering' });

test('rules and profiles are immutable; no universal acreage requirement is invented', () => {
  assert.equal(profiles.length, 4);
  assert.ok(profiles.every(p => p.required_acres === null));
  assert.throws(() => { profiles[0].required_acres = 50; }, TypeError);
  assert.throws(() => { rulesConfig.rules[0].mandatory = false; }, TypeError);
  assert.ok(rulesConfig.rules.every(r => r.threshold_authority && r.next_verification && r.freshness_days));
});

test('complete desktop evidence produces GREEN but no MW, probability or paid authorization', () => {
  const p = candidate(), r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'GREEN'); assert.equal(r.available_mw, null); assert.equal(r.dark_outline, false);
  assert.match(r.label, /capacity unconfirmed/); assert.equal(r.approval_probability, null);
  assert.equal(r.paid_control_status, 'NOT_AUTHORIZED_BY_ATLAS');
  assert.ok(r.rules.every(x => x.status === 'PASS')); assert.equal(r.rules_version, rulesConfig.version);
  assert.equal(r.geometry_metrics.repaired, false);
});

test('ordinary ingested public geometry is GRAY and does not turn missing measurements into zero', () => {
  const complete = candidate();
  const p = { id: complete.id, apn: complete.apn, county_fips: complete.county_fips, geometry: complete.geometry, source_url: complete.source_url, source_date: DATE, retrieved_at: DATE };
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'GRAY'); assert.equal(r.available_mw, null); assert.equal(r.usable_acres, null); assert.equal(r.largest_block_acres, null);
  assert.equal(r.rules.find(x => x.id === 'RESIDENTIAL').status, 'UNKNOWN');
});

test('source-supported fatal restriction is RED even while other mandatory inputs are unknown', () => {
  const p = candidate(); p.restrictions = failure(); delete p.coverage;
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'RED'); assert.ok(r.issues.some(x => x.status === 'UNKNOWN'));
  assert.ok(r.rules.find(x => x.id === 'RESTRICTIONS').reopening_criteria);
});

test('a claimed fatal failure without attributable current evidence cannot turn a parcel red', () => {
  const p = candidate(); p.restrictions = { ...failure(), source_url: null };
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
  p.restrictions = { ...failure(), effective_date: '2025-01-01' };
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('supported curable condition produces AMBER; mandatory missing coverage takes precedence', () => {
  const p = candidate(); p.restrictions = evidence({ status: 'CURABLE', reason: 'A synthetic conditional use review remains.' });
  assert.equal(screenParcel(p, 'inference', NOW).color, 'AMBER');
  p.coverage.physical.complete = false;
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
  p.coverage.physical.status = 'CURABLE';
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('a source failure is UNKNOWN, not an empty and clear overlay', () => {
  const p = candidate(); p.coverage.physical.error = 'HTTP 503';
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'GRAY'); assert.match(r.rules.find(x => x.id === 'PHYSICAL').reason, /INCOMPLETE_SOURCE/);
  delete p.coverage.physical.error; p.coverage.physical.truncated = true;
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('stale residential vintage stays GRAY despite a fresh retrieval or review timestamp', () => {
  const p = candidate(); p.coverage.residential.effective_date = '2025-01-01'; p.coverage.residential.reviewed_at = DATE;
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('expired and future-dated evidence cannot pass', () => {
  const p = candidate(); p.context.expires_at = '2026-10-30';
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
  p.context = evidence({ effective_date: '2026-11-01' });
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('classified counts require all bands, monotonic counts and matching distance units', () => {
  const p = candidate(); delete p.residential.counts['500'];
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
  const q = candidate(); q.residential.counts['250'].confirmed = 1; q.residential.nearest_confirmed_m = 100;
  assert.equal(screenParcel(q, 'inference', NOW).color, 'GRAY');
  const z = candidate(); z.residential.count_unit = 'dwelling_units';
  assert.equal(screenParcel(z, 'inference', NOW).color, 'GRAY');
});

test('residential proximity creates a review condition, not a fabricated legal rejection or probability', () => {
  const p = candidate(); p.residential.dense_adjacency = true;
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'AMBER'); assert.equal(r.approval_probability, null);
  assert.match(r.rules.find(x => x.id === 'RESIDENTIAL').reason, /not legal setbacks/);
});

test('overlapping exclusions require reconciled union accounting, not the sum of layer areas', () => {
  const p = candidate(), gross = p.envelope.gross_acres;
  p.envelope.excluded_union_acres = gross * 0.4; p.envelope.usable_acres = gross * 0.7;
  p.envelope.components_acres = [gross * 0.7]; p.envelope.largest_block_acres = gross * 0.7;
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'GRAY'); assert.equal(r.usable_acres, null); assert.match(r.rules.find(x => x.id === 'LAYOUT').reason, /do not reconcile/);
});

test('fragmented usable area does not masquerade as one contiguous development block', () => {
  const p = candidate(), gross = p.envelope.gross_acres;
  p.envelope.excluded_union_acres = gross * 0.2; p.envelope.usable_acres = gross * 0.8;
  p.envelope.components_acres = [gross * 0.4, gross * 0.4]; p.envelope.largest_block_acres = gross * 0.4;
  p.layout.area_requirement_acres = gross * 0.5;
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'AMBER'); assert.equal(r.largest_block_acres, gross * 0.4);
});

test('a geometry/profile change invalidates an old envelope and cannot silently reuse the result', () => {
  const p = candidate(); p.geometry_version = 'changed-geometry';
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
  assert.equal(screenParcel(candidate(), 'hyperscale', NOW).color, 'GRAY');
  assert.throws(() => screenParcel(candidate(), 'invented', NOW), /Unknown screening profile/);
});

test('the 20–30 facility MW profile cannot be silently applied to a 1,000 MW load', () => {
  const p = candidate(); p.requested_facility_mw = 1000; p.layout.facility_mw = 1000;
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('green plus current exact-load utility and reviewed use path permits dark outline only', () => {
  const p = candidate(); p.power = evidence({ stage: 'UTILITY_PATH', load_facility_mw: 25, available_mw: 1000 }); p.planning = evidence({ use_path_reviewed: true });
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.dark_outline, true); assert.equal(r.available_mw, null);
  p.power = evidence({ stage: 'STUDY', load_facility_mw: 25, available_mw: 30, capacity_confirmed: true });
  assert.equal(screenParcel(p, 'inference', NOW).available_mw, 30);
  p.power.load_facility_mw = 50;
  assert.equal(screenParcel(p, 'inference', NOW).available_mw, null); assert.equal(screenParcel(p, 'inference', NOW).dark_outline, false);
});

test('expired utility evidence downgrades utility badge without pretending desktop inputs disappeared', () => {
  const p = candidate(); p.power = evidence({ stage: 'CONTRACT', load_facility_mw: 25, capacity_confirmed: true, available_mw: 30, expires_at: '2026-10-30' }); p.planning = evidence({ use_path_reviewed: true });
  const r = screenParcel(p, 'inference', NOW);
  assert.equal(r.color, 'GREEN'); assert.equal(r.dark_outline, false); assert.equal(r.available_mw, null); assert.equal(r.power_stage, 'STALE_OR_UNVERIFIED');
});

test('unsupported mandatory category waivers do not manufacture green', () => {
  const p = candidate(); p.coverage.residential = evidence({ status: 'NOT_APPLICABLE', not_applicable_reason: 'Unclassified buildings were assumed nonresidential.' });
  assert.equal(screenParcel(p, 'inference', NOW).color, 'GRAY');
});

test('spherical area uses geodesic units, handles holes and records preliminary dimensions', () => {
  const m = geometryMetrics(square(0, 0, 0.001));
  assert.equal(m.valid, true); assert.ok(m.area_m2 > 12360 && m.area_m2 < 12370); assert.ok(m.computed_acres > 3.05 && m.computed_acres < 3.06);
  assert.ok(m.width_m > 111 && m.width_m < 112); assert.ok(m.height_m > 111 && m.height_m < 112);
  const outer = square(0, 0, 0.01), hole = square(0.002, 0.002, 0.004);
  const holed = geometryMetrics({ type: 'Polygon', coordinates: [...outer.coordinates, ...hole.coordinates] });
  assert.equal(holed.valid, true);
  assert.ok(Math.abs(holed.area_m2 - (geometryMetrics(outer).area_m2 - geometryMetrics(hole).area_m2)) < 0.01);
});

test('multipart geometry preserves separate component sizes and rejects overlaps', () => {
  const a = square(0, 0, 0.01), b = square(0.03, 0, 0.01);
  const m = geometryMetrics({ type: 'MultiPolygon', coordinates: [a.coordinates, b.coordinates] });
  assert.equal(m.valid, true); assert.equal(m.component_acres.length, 2); assert.ok(m.largest_component_acres < m.computed_acres);
  const overlap = geometryMetrics({ type: 'MultiPolygon', coordinates: [a.coordinates, square(0.005, 0, 0.01).coordinates] });
  assert.equal(overlap.valid, false); assert.equal(overlap.computed_acres, null);
});

test('an Alaska-style antimeridian parcel has a small width instead of spanning the world', () => {
  const m = geometryMetrics({ type: 'Polygon', coordinates: [[[179.99, 52], [-179.99, 52], [-179.99, 52.01], [179.99, 52.01], [179.99, 52]]] });
  assert.equal(m.valid, true); assert.equal(m.crosses_antimeridian, true); assert.ok(m.width_m < 1500); assert.ok(m.width_m > 1000);
});

test('self crossing, empty, unclosed, duplicate and invalid hole geometry do not yield clean metrics', () => {
  const bad = [
    null,
    { type: 'Polygon', coordinates: [] },
    { type: 'Polygon', coordinates: [[[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]]] },
    { type: 'Polygon', coordinates: [[[0, 0], [1, 0], [1, 1], [0, 1]]] },
    { type: 'Polygon', coordinates: [[[0, 0], [0, 0], [1, 0], [0, 1], [0, 0]]] },
    { type: 'Polygon', coordinates: [...square(0, 0, 0.01).coordinates, ...square(0.02, 0.02, 0.001).coordinates] },
  ];
  for (const g of bad) { const m = geometryMetrics(g); assert.equal(m.valid, false); assert.equal(m.computed_acres, null); assert.ok(m.issues.length); }
});

test('APN identity retains leading zeros and requires source corroboration', () => {
  const p = candidate(); assert.equal(matchListing(p, offering(p)).state, 'VERIFIED');
  assert.equal(matchListing(p, { ...offering(p), apn: '123' }).state, 'CONFLICTING');
  assert.equal(matchListing(p, { ...offering(p), apn: 123 }).state, 'UNRESOLVED');
  assert.equal(matchListing(p, { ...offering(p), advertised_acres: null }).state, 'PROBABLE');
  assert.equal(matchListing(p, { ...offering(p), county_fips: '04019' }).state, 'CONFLICTING');
});

test('marketing pins and proposed splits stay in review', () => {
  const p = candidate();
  assert.equal(matchListing(p, { id: 'pin-only', coordinates: [-110, 31], url: 'https://example.invalid/listing' }).state, 'UNRESOLVED');
  assert.equal(matchListing(p, { ...offering(p), offered_scope: 'portion' }).state, 'PROBABLE');
  assert.equal(matchListing(p, { ...offering(p), scope_verified: false }).state, 'PROBABLE');
});

test('multi-parcel assembly acreage cannot validate one constituent', () => {
  const p = candidate(), l = { ...offering(p), offered_scope: 'assembly', apns: [p.apn, '000456'], advertised_acres: geometryMetrics(p.geometry).computed_acres * 2 };
  assert.equal(matchListing(p, l).state, 'PROBABLE');
  l.parcels = [{ apn: p.apn, county_fips: p.county_fips, advertised_acres: geometryMetrics(p.geometry).computed_acres }];
  assert.equal(matchListing(p, l).state, 'VERIFIED');
});

test('exact geometry can corroborate a match despite reversed ring orientation; shifted polygon conflicts', () => {
  const p = candidate(), l = { ...offering(p), advertised_acres: null, geometry: { ...p.geometry, coordinates: [p.geometry.coordinates[0].slice().reverse()] } };
  assert.equal(matchListing(p, l).state, 'VERIFIED');
  l.geometry = square(-109, 31);
  assert.equal(matchListing(p, l).state, 'CONFLICTING');
});

test('screening is deterministic and leaves raw input unchanged', () => {
  const p = candidate(), before = JSON.stringify(p), a = screenParcel(p, 'inference', NOW), b = screenParcel(p, 'inference', NOW);
  assert.deepEqual(a, b); assert.equal(JSON.stringify(p), before);
  assert.equal(screenParcel({ type: 'Feature', properties: { ...p, geometry: undefined }, geometry: p.geometry }, 'inference', NOW).color, a.color);
  assert.throws(() => screenParcel(p, 'inference', 'not-a-date'), /evaluation date/);
});
