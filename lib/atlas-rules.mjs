// Pure, versioned desktop screening. It never authorizes paid control.
export const RULE_VERSION = 'ATLAS_DESKTOP_2026-10-31_v1';
const DAY = 86400000, SQM_PER_ACRE = 4046.8564224, RADIUS_M = 6371008.8;
const EVIDENCE_LEVELS = ['V0', 'V1', 'V2', 'V3', 'V4'];
const STATES = ['PASS', 'FAIL', 'CURABLE', 'UNKNOWN', 'NOT_APPLICABLE'];
function deepFreeze(object) { Object.freeze(object); for (const value of Object.values(object)) if (value && typeof value === 'object' && !Object.isFrozen(value)) deepFreeze(value); return object; }
export const profiles = deepFreeze([
  { id: 'inference', version: '1.0', name: '20–30 MW facility demand', description: 'Preliminary inference-scale hypothesis within a 10–50 MW research lane. Capacity and buyer acceptance are unconfirmed.', buyer_segment: 'inference', facility_mw: [20, 30], it_mw: null, required_acres: null, hypothesis_based: true },
  { id: 'hyperscale', version: '1.0', name: 'Hyperscale / training', description: 'Separate campus scenario; requires an attributable buyer brief, load, layout and delivery horizon.', buyer_segment: 'hyperscale', facility_mw: null, it_mw: null, required_acres: null, hypothesis_based: true },
  { id: 'urban-infill', version: '1.0', name: 'Urban infill', description: 'Metro and latency-specific scenario; no universal acreage threshold.', buyer_segment: 'urban-infill', facility_mw: null, it_mw: null, required_acres: null, hypothesis_based: true },
  { id: 'industrial-reuse', version: '1.0', name: 'Industrial reuse', description: 'Existing industrial land or facilities; existing service does not establish transferable load capacity.', buyer_segment: 'industrial-reuse', facility_mw: null, it_mw: null, required_acres: null, hypothesis_based: true },
]);

const rule = (id, name, fields, days, condition, next) => ({ id, name, applicable_profiles: profiles.map(p => p.id), mandatory: true, input_fields: fields, geographic_scope: 'Exact parcel and controlling authorities; all 50 states and DC', evidence_requirements: 'Attributable source, exact scope, effective/review date, retrieval date, explicit result; unknown or conflicting evidence cannot pass.', units: 'Rule-specific; distances in meters, area in acres, demand in facility MW', threshold: condition, threshold_authority: 'Syncranicity Parcel Atlas build prompt, 2026-10-30; freshness limits are provisional operational assumptions', freshness_days: days, reason_code: id, next_verification: next });
export const rulesConfig = deepFreeze({
  version: RULE_VERSION,
  precedence: ['RED: supported fatal scenario failure', 'GRAY: unknown or stale mandatory evidence', 'AMBER: supported curable condition', 'GREEN: every mandatory rule passes'],
  freshness_note: 'These maximum ages are operational review intervals, not a representation of legal or data validity. An earlier explicit expiry controls. Refreshing retrieval time alone cannot renew evidence.',
  residential_bands_m: [250, 500, 1000, 1609.344],
  required_physical_layers: ['flood', 'wetlands', 'terrain', 'protected_land', 'roads', 'buildings'],
  required_layout_systems: ['building', 'electrical', 'cooling', 'backup', 'stormwater', 'access', 'construction'],
  rules: [
    rule('IDENTITY', 'Parcel geometry and identity', ['geometry', 'apn', 'county_fips', 'source_url', 'source_date', 'retrieved_at', 'identity_conflict'], 365, 'Valid polygon, string APN, county identity and dated source; no unresolved identity conflict.', 'Reconcile the exact legal parcel against the current official GIS and title description.'),
    rule('JURISDICTION', 'Controlling authority', ['jurisdiction'], 180, 'Resolved controlling authorities and documented scope; county identity alone is insufficient.', 'Resolve municipal, county, ETJ, tribal and federal authority as applicable.'),
    rule('PHYSICAL', 'Physical layer coverage', ['coverage.physical'], 365, 'All declared physical layers covered, count/pagination reconciled and no service failure or truncation.', 'Complete current flood, wetland, terrain, protected-land, road and building coverage for the exact site.'),
    rule('RESIDENTIAL', 'Residential and sensitive-use review', ['coverage.residential', 'residential'], 180, 'Current classified measurements in all four research bands, explicit units and sensitive-use review.', 'Classify buildings, measure boundary-to-dwelling distances and review residential approvals and sensitive uses.'),
    rule('LAYOUT', 'Preliminary development envelope', ['layout', 'envelope', 'geometry_version'], 180, 'Versioned scenario requirement and preliminary fit, with validated union-based exclusions and contiguous area.', 'Prepare a sourced scenario layout covering buildings, electrical yard, cooling, backup, drainage, access and construction.'),
    rule('RESTRICTIONS', 'Applicable restrictions', ['restrictions'], 90, 'Sourced handling of known use restrictions with applicability and reopening criteria for failures.', 'Read current controlling use rules, overlays, moratoria and relevant decisions.'),
    rule('CONTEXT', 'Infrastructure or buyer context', ['context'], 180, 'Attributable, current, exact-scope infrastructure or buyer evidence; no capacity inference from proximity.', 'Identify the source-supported buyer need or infrastructure lead and its next verification.'),
  ],
});

const finite = n => typeof n === 'number' && Number.isFinite(n);
const nonnegative = n => finite(n) && n >= 0;
const str = v => typeof v === 'string' && v.trim().length > 0;
const dayTime = v => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}(T|$)/.test(v) ? Date.parse(v) : NaN;
const sourceOK = v => typeof v === 'string' && /^(https?:\/\/|library-file:|source:)/i.test(v);
const level = v => EVIDENCE_LEVELS.includes(v) ? v : 'V0';
const toRad = n => n * Math.PI / 180;
const lonDelta = n => ((n + 540) % 360) - 180;
const round = n => finite(n) ? Math.round(n * 1e6) / 1e6 : null;

function unwrapRing(ring) {
  const out = [ring[0].slice(0, 2)];
  for (let i = 1; i < ring.length; i++) out.push([out[i - 1][0] + lonDelta(ring[i][0] - ring[i - 1][0]), ring[i][1]]);
  return out;
}
const orient = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
const nearZero = x => Math.abs(x) < 1e-12;
const onSegment = (a, b, p) => nearZero(orient(a, b, p)) && p[0] >= Math.min(a[0], b[0]) - 1e-12 && p[0] <= Math.max(a[0], b[0]) + 1e-12 && p[1] >= Math.min(a[1], b[1]) - 1e-12 && p[1] <= Math.max(a[1], b[1]) + 1e-12;
function intersects(a, b, c, d) {
  const x = orient(a, b, c), y = orient(a, b, d), z = orient(c, d, a), w = orient(c, d, b);
  return (x * y < 0 && z * w < 0) || (nearZero(x) && onSegment(a, b, c)) || (nearZero(y) && onSegment(a, b, d)) || (nearZero(z) && onSegment(c, d, a)) || (nearZero(w) && onSegment(c, d, b));
}
function pointInRing(p, ring) {
  let inside = false;
  for (let i = 0, j = ring.length - 2; i < ring.length - 1; j = i++) {
    const a = ring[j], b = ring[i];
    if (onSegment(a, b, p)) return 0;
    if (((a[1] > p[1]) !== (b[1] > p[1])) && p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside ? 1 : -1;
}
const shiftRing = (ring, reference) => { const shift = Math.round((reference - ring[0][0]) / 360) * 360; return ring.map(p => [p[0] + shift, p[1]]); };
function ringArea(ring) {
  let sum = 0;
  for (let i = 1; i < ring.length; i++) sum += toRad(lonDelta(ring[i][0] - ring[i - 1][0])) * (2 + Math.sin(toRad(ring[i - 1][1])) + Math.sin(toRad(ring[i][1])));
  return Math.abs(sum * RADIUS_M ** 2 / 2);
}
function distance(a, b) {
  const lat1 = toRad(a[1]), lat2 = toRad(b[1]), dLat = lat2 - lat1, dLon = toRad(lonDelta(b[0] - a[0]));
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return 2 * RADIUS_M * Math.asin(Math.sqrt(Math.min(1, Math.max(0, h))));
}

/** Preliminary spherical metrics. Invalid or unresolved topology yields null area, never a repaired parcel. */
export function geometryMetrics(input) {
  const geometry = input?.type === 'Feature' ? input.geometry : input;
  const output = { valid: false, geometry_type: geometry?.type || null, computed_acres: null, gross_acres: null, area_m2: null, largest_component_acres: null, component_acres: [], bbox: null, width_m: null, height_m: null, crosses_antimeridian: false, vertex_count: 0, issues: [], method: 'Spherical geodesic area (mean Earth radius 6371008.8 m); preliminary, not a boundary survey', repaired: false };
  const fail = reason => ({ ...output, issues: [...output.issues, reason] });
  if (!geometry || !['Polygon', 'MultiPolygon'].includes(geometry.type)) return fail('POLYGON_REQUIRED');
  const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
  if (!Array.isArray(polygons) || !polygons.length) return fail('EMPTY_GEOMETRY');
  const all = [], prepared = [];
  for (const polygon of polygons) {
    if (!Array.isArray(polygon) || !polygon.length) return fail('EMPTY_POLYGON');
    const rings = [];
    for (const ring of polygon) {
      if (!Array.isArray(ring) || ring.length < 4) return fail('RING_TOO_SHORT');
      if (!ring.every(p => Array.isArray(p) && finite(p[0]) && finite(p[1]) && Math.abs(p[0]) <= 180 && Math.abs(p[1]) < 90)) return fail('INVALID_COORDINATES_OR_POLAR_GEOMETRY');
      if (ring[0][0] !== ring.at(-1)[0] || ring[0][1] !== ring.at(-1)[1]) return fail('UNCLOSED_RING');
      for (let i = 1; i < ring.length; i++) if (ring[i][0] === ring[i - 1][0] && ring[i][1] === ring[i - 1][1]) return fail('DUPLICATE_CONSECUTIVE_VERTEX');
      output.vertex_count += ring.length;
      if (output.vertex_count > 20000) return fail('GEOMETRY_REQUIRES_OFFLINE_TOPOLOGY_VALIDATION');
      const r = unwrapRing(ring); rings.push(r); all.push(...ring.slice(0, -1));
    }
    for (let i = 1; i < rings.length; i++) rings[i] = shiftRing(rings[i], rings[0][0][0]);
    prepared.push(rings);
  }
  let checks = 0;
  const crossRings = (a, b, same = false) => {
    for (let i = 0; i < a.length - 1; i++) for (let j = same ? i + 1 : 0; j < b.length - 1; j++) {
      if (same && (Math.abs(i - j) <= 1 || (i === 0 && j === a.length - 2))) continue;
      if (++checks > 2000000) throw Error('GEOMETRY_REQUIRES_OFFLINE_TOPOLOGY_VALIDATION');
      if (intersects(a[i], a[i + 1], b[j], b[j + 1])) return true;
    }
    return false;
  };
  try {
    for (const rings of prepared) {
      for (const ring of rings) if (crossRings(ring, ring, true)) return fail('SELF_INTERSECTING_RING');
      for (let h = 1; h < rings.length; h++) {
        if (pointInRing(rings[h][0], rings[0]) !== 1 || crossRings(rings[0], rings[h])) return fail('HOLE_OUTSIDE_OR_TOUCHING_SHELL');
        for (let k = 1; k < h; k++) if (crossRings(rings[h], rings[k]) || pointInRing(rings[h][0], rings[k]) >= 0 || pointInRing(rings[k][0], rings[h]) >= 0) return fail('OVERLAPPING_HOLES');
      }
    }
    const inPolygon = (p, rings) => pointInRing(p, rings[0]) >= 0 && !rings.slice(1).some(r => pointInRing(p, r) >= 0);
    for (let i = 0; i < prepared.length; i++) for (let j = 0; j < i; j++) {
      const a = prepared[i], b = prepared[j].map(r => shiftRing(r, a[0][0][0]));
      if (a.some(ar => b.some(br => crossRings(ar, br))) || inPolygon(a[0][0], b) || inPolygon(b[0][0], a)) return fail('COMPONENTS_OVERLAP_OR_TOUCH_REQUIRES_REVIEW');
    }
  } catch (e) { return fail(e.message); }
  const areas = polygons.map(p => ringArea(p[0]) - p.slice(1).reduce((s, r) => s + ringArea(r), 0));
  if (areas.some(a => !finite(a) || a <= 0.01)) return fail('ZERO_OR_NEGATIVE_AREA');
  const lons = [...new Set(all.map(p => (p[0] + 360) % 360))].sort((a, b) => a - b);
  let gap = -1, gapAt = 0;
  for (let i = 0; i < lons.length; i++) { const d = (i === lons.length - 1 ? lons[0] + 360 : lons[i + 1]) - lons[i]; if (d > gap) { gap = d; gapAt = i; } }
  const westRaw = lons[(gapAt + 1) % lons.length], eastRaw = lons[gapAt], west = lonDelta(westRaw), east = lonDelta(eastRaw);
  const south = Math.min(...all.map(p => p[1])), north = Math.max(...all.map(p => p[1]));
  if (360 - gap >= 180) return fail('HEMISPHERE_SCALE_GEOMETRY_REQUIRES_REVIEW');
  const area = areas.reduce((a, b) => a + b, 0), acres = area / SQM_PER_ACRE;
  const middleLon = lonDelta(westRaw + (360 - gap) / 2);
  return { ...output, valid: true, computed_acres: round(acres), gross_acres: round(acres), area_m2: round(area), largest_component_acres: round(Math.max(...areas) / SQM_PER_ACRE), component_acres: areas.map(a => round(a / SQM_PER_ACRE)), bbox: [west, south, east, north], width_m: round(distance([west, (south + north) / 2], [east, (south + north) / 2])), height_m: round(distance([middleLon, south], [middleLon, north])), crosses_antimeridian: west > east };
}

function evidenceCheck(e, now, days, profileId, requireScope = true) {
  if (!e || !STATES.includes(e.status)) return 'MISSING_RESULT';
  if (!sourceOK(e.source_url) || !str(e.reason || e.summary)) return 'MISSING_ATTRIBUTION';
  if (requireScope && e.scope_match !== true) return 'UNVERIFIED_SCOPE';
  if (Array.isArray(e.profile_ids) && !e.profile_ids.includes(profileId)) return 'DIFFERENT_PROFILE';
  if (e.conflicting === true || e.truncated === true || e.error) return 'CONFLICTED_OR_INCOMPLETE_SOURCE';
  const date = dayTime(e.reviewed_at || e.effective_date), retrieved = dayTime(e.retrieved_at);
  if (!finite(date) || !finite(retrieved) || date > now || retrieved > now) return 'MISSING_OR_FUTURE_DATE';
  if (now - date > days * DAY) return 'STALE_EVIDENCE';
  if (e.expires_at != null && (!finite(dayTime(e.expires_at)) || dayTime(e.expires_at) <= now)) return 'EXPIRED_EVIDENCE';
  if (e.status === 'NOT_APPLICABLE' && !str(e.not_applicable_reason)) return 'UNJUSTIFIED_NOT_APPLICABLE';
  return null;
}
function resultFor(def, status, reason, e = null, overrides = {}) {
  return { id: def.id, name: def.name, mandatory: def.mandatory, status, reason, reason_code: `${def.id}_${status}`, next_verification: def.next_verification, source_url: e?.source_url || null, effective_date: e?.effective_date || null, reviewed_at: e?.reviewed_at || null, evidence_level: level(e?.evidence_level), fatal: false, ...overrides };
}
function envelopeCheck(p, profile, metrics, now) {
  const e = p.envelope;
  if (!e || e.validated !== true || e.union_applied !== true || !str(e.method) || !sourceOK(e.source_url) || !str(p.geometry_version) || e.geometry_version !== p.geometry_version || e.profile_id !== profile.id || e.profile_version !== profile.version || !e.source_versions || !Object.keys(e.source_versions).length) return { valid: false, reason: 'Envelope requires validated, version-matched union exclusions and input provenance.' };
  const t = dayTime(e.computed_at);
  if (!finite(t) || t > now || now - t > 180 * DAY) return { valid: false, reason: 'Envelope calculation is missing, future-dated or stale.' };
  const fields = ['gross_acres', 'excluded_union_acres', 'usable_acres', 'largest_block_acres'];
  if (fields.some(k => !nonnegative(e[k])) || !Array.isArray(e.components_acres) || e.components_acres.some(n => !nonnegative(n))) return { valid: false, reason: 'Envelope areas or component accounting are incomplete.' };
  const tolerance = Math.max(0.01, metrics.gross_acres * 0.01), sum = e.components_acres.reduce((a, b) => a + b, 0), largest = e.components_acres.length ? Math.max(...e.components_acres) : 0;
  if (Math.abs(e.gross_acres - metrics.gross_acres) > tolerance || Math.abs(e.excluded_union_acres + e.usable_acres - e.gross_acres) > tolerance || Math.abs(sum - e.usable_acres) > tolerance || Math.abs(largest - e.largest_block_acres) > tolerance || e.usable_acres > e.gross_acres + tolerance || e.largest_block_acres > e.usable_acres + tolerance) return { valid: false, reason: 'Envelope gross, union exclusions, usable area and contiguous components do not reconcile.' };
  return { valid: true, reason: 'Validated envelope accounting reconciles.', usable_acres: e.usable_acres, largest_block_acres: e.largest_block_acres, excluded_union_acres: e.excluded_union_acres };
}

/** Screen only the selected profile; later title/utility diligence does not masquerade as a desktop pass. */
export function screenParcel(input, profileId = 'inference', nowISO = new Date().toISOString()) {
  const p = input?.type === 'Feature' ? { ...input.properties, geometry: input.geometry } : (input || {});
  const profile = profiles.find(x => x.id === profileId);
  if (!profile) throw Error(`Unknown screening profile: ${profileId}`);
  const now = dayTime(nowISO); if (!finite(now)) throw Error('A valid evaluation date is required.');
  const metrics = geometryMetrics(p.geometry), envelope = metrics.valid ? envelopeCheck(p, profile, metrics, now) : { valid: false, reason: 'Resolve parcel geometry before calculating a development envelope.' };
  const requestedMW = p.requested_facility_mw ?? p.layout?.facility_mw;
  const results = [];
  for (const def of rulesConfig.rules) {
    if (def.id === 'IDENTITY') {
      const sourceDate = dayTime(p.source_date), retrieved = dayTime(p.retrieved_at);
      const valid = metrics.valid && str(p.apn) && /^\d{5}$/.test(p.county_fips || '') && sourceOK(p.source_url) && finite(sourceDate) && finite(retrieved) && sourceDate <= now && retrieved <= now && now - sourceDate <= def.freshness_days * DAY && p.identity_conflict !== true;
      results.push(resultFor(def, valid ? 'PASS' : 'UNKNOWN', valid ? 'Dated parcel polygon and raw APN are resolved within the county identity.' : `Exact parcel identity or current geometry remains unresolved${metrics.issues.length ? ': ' + metrics.issues.join(', ') : ''}.`, { source_url: p.source_url, effective_date: p.source_date, evidence_level: p.evidence_level }));
      continue;
    }
    const e = def.id === 'PHYSICAL' ? p.coverage?.physical : def.id === 'RESIDENTIAL' ? p.coverage?.residential : p[{ JURISDICTION: 'jurisdiction', LAYOUT: 'layout', RESTRICTIONS: 'restrictions', CONTEXT: 'context' }[def.id]];
    const problem = evidenceCheck(e, now, def.freshness_days, profile.id);
    if (problem) { results.push(resultFor(def, 'UNKNOWN', `${problem}: ${def.next_verification}`, e)); continue; }
    let status = e.status, reason = e.reason || e.summary, fatal = false;
    if (status === 'NOT_APPLICABLE' && ['JURISDICTION', 'PHYSICAL', 'RESIDENTIAL', 'LAYOUT', 'CONTEXT'].includes(def.id)) { status = 'UNKNOWN'; reason = 'This mandatory desktop category cannot be waived for an entire parcel.'; }
    if (['PASS', 'CURABLE'].includes(status) && def.id === 'JURISDICTION' && (e.resolved !== true || !Array.isArray(e.authorities) || !e.authorities.length || !e.authorities.every(str))) { status = 'UNKNOWN'; reason = 'County membership alone does not resolve the controlling authorities.'; }
    if (['PASS', 'CURABLE'].includes(status) && def.id === 'PHYSICAL' && (e.complete !== true || !finite(dayTime(e.effective_date)) || now - dayTime(e.effective_date) > def.freshness_days * DAY || !rulesConfig.required_physical_layers.every(id => e.layer_coverage?.[id] === 'COMPLETE' || (e.layer_coverage?.[id] === 'NOT_APPLICABLE' && str(e.layer_explanations?.[id]))))) { status = 'UNKNOWN'; reason = 'Physical coverage is missing, stale or incomplete for one or more required layers.'; }
    if (['PASS', 'CURABLE'].includes(status) && def.id === 'RESIDENTIAL') {
      const r = p.residential, rings = r?.counts;
      const measured = rulesConfig.residential_bands_m.every(band => nonnegative(rings?.[String(band)]?.confirmed) && Number.isInteger(rings[String(band)].confirmed) && nonnegative(rings?.[String(band)]?.possible) && Number.isInteger(rings[String(band)].possible));
      const monotone = measured && ['confirmed', 'possible'].every(kind => rulesConfig.residential_bands_m.every((band, i, a) => i === 0 || rings[String(band)][kind] >= rings[String(a[i - 1])][kind]));
      const distances = r && (r.nearest_confirmed_m === null || nonnegative(r.nearest_confirmed_m)) && (r.nearest_possible_m === null || nonnegative(r.nearest_possible_m));
      const noMissingNearest = measured && (rings['1609.344'].confirmed === 0 || nonnegative(r.nearest_confirmed_m)) && (rings['1609.344'].possible === 0 || nonnegative(r.nearest_possible_m));
      if (e.complete !== true || !finite(dayTime(e.effective_date)) || now - dayTime(e.effective_date) > def.freshness_days * DAY || !measured || !monotone || !distances || !noMissingNearest || r.measurement_reference !== 'parcel_boundary' || r.count_unit !== 'buildings' || r.sensitive_use_review_complete !== true) { status = 'UNKNOWN'; reason = 'Classified building counts, distances, measurement reference or sensitive-use coverage are incomplete or stale.'; }
      else if (r.dense_adjacency === true || r.mitigation_review_required === true) { status = 'CURABLE'; reason = 'Residential exposure requires a named layout and local approval review; distance bands are not legal setbacks.'; }
    }
    if (['PASS', 'CURABLE'].includes(status) && def.id === 'LAYOUT') {
      if (!envelope.valid || !str(e.version) || e.profile_id !== profile.id || e.profile_version !== profile.version || !str(e.threshold_authority) || !finite(e.area_requirement_acres) || e.area_requirement_acres <= 0 || !finite(requestedMW) || requestedMW <= 0 || e.facility_mw !== requestedMW || (profile.facility_mw && (requestedMW < profile.facility_mw[0] || requestedMW > profile.facility_mw[1])) || !rulesConfig.required_layout_systems.every(x => e.systems_considered?.includes(x)) || typeof e.fits !== 'boolean') { status = 'UNKNOWN'; reason = !envelope.valid ? envelope.reason : 'The scenario layout is missing versioned requirements, matching facility demand, authority or system allocations.'; }
      else if (!e.fits || envelope.largest_block_acres < e.area_requirement_acres) { status = 'CURABLE'; reason = 'The declared layout does not currently fit the validated contiguous envelope; evaluate a revised layout or assembly.'; }
    }
    if (status === 'FAIL') {
      fatal = e.fatal === true && str(e.reopening_criteria) && ['adopted_rule', 'documented_buyer_requirement', 'professional_assessment'].includes(e.authority_type);
      if (!fatal) { status = 'CURABLE'; reason = 'A sourced conflict is recorded, but its fatal applicability and reopening criteria are not established. ' + reason; }
    }
    results.push(resultFor(def, status, reason, e, { fatal, reopening_criteria: e.reopening_criteria || null }));
  }
  for (const [index, condition] of (Array.isArray(p.conditions) ? p.conditions : []).entries()) {
    const def = { id: `CONDITION_${index + 1}`, name: condition.name || 'Additional scenario condition', mandatory: true, next_verification: condition.next_verification || 'Resolve the recorded condition against its stated scope.' };
    const problem = evidenceCheck(condition, now, 90, profile.id);
    if (problem) { results.push(resultFor(def, 'UNKNOWN', problem, condition)); continue; }
    const fatal = condition.status === 'FAIL' && condition.fatal === true && str(condition.reopening_criteria) && ['adopted_rule', 'documented_buyer_requirement', 'professional_assessment'].includes(condition.authority_type);
    results.push(resultFor(def, condition.status === 'FAIL' && !fatal ? 'CURABLE' : condition.status, condition.reason || condition.summary, condition, { fatal, reopening_criteria: condition.reopening_criteria || null }));
  }
  const fatal = results.find(r => r.status === 'FAIL' && r.fatal), unknown = results.find(r => r.status === 'UNKNOWN'), curable = results.find(r => r.status === 'CURABLE');
  const color = fatal ? 'RED' : unknown ? 'GRAY' : curable ? 'AMBER' : 'GREEN';
  const powerCurrent = !evidenceCheck(p.power, now, 90, profile.id) && p.power.status === 'PASS' && finite(requestedMW) && requestedMW > 0 && p.power.load_facility_mw === requestedMW;
  const pathStages = ['UTILITY_PATH', 'FEASIBILITY', 'STUDY', 'CONTRACT', 'ENERGIZED'];
  const powerPath = powerCurrent && pathStages.includes(p.power.stage);
  const planningCurrent = !evidenceCheck(p.planning, now, 90, profile.id) && p.planning.status === 'PASS' && p.planning.use_path_reviewed === true;
  const availableMW = powerCurrent && p.power.capacity_confirmed === true && ['STUDY', 'CONTRACT', 'ENERGIZED'].includes(p.power.stage) && nonnegative(p.power.available_mw) ? p.power.available_mw : null;
  const labels = { GREEN: 'Desktop candidate – capacity unconfirmed', AMBER: 'Conditional candidate – review required', RED: 'Scenario conflict – reopening criteria apply', GRAY: 'Insufficient current desktop evidence' };
  const issues = results.filter(r => ['FAIL', 'UNKNOWN', 'CURABLE'].includes(r.status)).map(r => ({ rule_id: r.id, status: r.status, reason: r.reason, next_verification: r.next_verification }));
  const minimumLevel = Math.min(...results.filter(r => r.mandatory && r.status !== 'NOT_APPLICABLE').map(r => EVIDENCE_LEVELS.indexOf(r.evidence_level)));
  return { profile_id: profile.id, profile_version: profile.version, rules_version: RULE_VERSION, evaluated_at: new Date(now).toISOString(), hypothesis_based: profile.hypothesis_based, color, label: labels[color], dark_outline: color === 'GREEN' && !!powerPath && !!planningCurrent, evidence_level: EVIDENCE_LEVELS[Math.max(0, minimumLevel)], rules: results, issues, next_action: (fatal || unknown || curable)?.next_verification || 'Verify exact-load utility service, planning path, title, buyer requirements and affordable control before any paid option.', available_mw: availableMW, power_stage: powerCurrent ? p.power.stage || 'UNKNOWN' : p.power?.stage ? 'STALE_OR_UNVERIFIED' : 'UNKNOWN', requested_facility_mw: finite(requestedMW) ? requestedMW : null, computed_acres: metrics.computed_acres, gross_acres: metrics.gross_acres, usable_acres: envelope.valid ? envelope.usable_acres : null, largest_block_acres: envelope.valid ? envelope.largest_block_acres : null, excluded_union_acres: envelope.valid ? envelope.excluded_union_acres : null, geometry_metrics: metrics, input_versions: { snapshot_id: p.snapshot_id || null, geometry_version: p.geometry_version || null, envelope_version: p.envelope?.version || null }, paid_control_status: p.paid_control_status || 'NOT_AUTHORIZED_BY_ATLAS', approval_probability: null };
}

function canonicalGeometry(geometry) {
  const polygons = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
  const canonicalRing = ring => {
    const coordinates = ring.slice(0, -1).map(p => `${p[0].toFixed(7)},${p[1].toFixed(7)}`);
    const rotated = arr => { let best = 0; for (let i = 1; i < arr.length; i++) if (arr[i] < arr[best]) best = i; return [...arr.slice(best), ...arr.slice(0, best)].join(';'); };
    return [rotated(coordinates), rotated([...coordinates].reverse())].sort()[0];
  };
  return polygons.map(p => `${canonicalRing(p[0])}|${p.slice(1).map(canonicalRing).sort().join('|')}`).sort().join('||');
}

/** Identity reconciliation only. It does not prove current listing availability or qualify an alert. */
export function matchListing(parcelInput, listing) {
  const parcel = parcelInput?.type === 'Feature' ? { ...parcelInput.properties, geometry: parcelInput.geometry } : parcelInput || {};
  const pAPN = typeof parcel.apn === 'string' ? parcel.apn.trim() : null;
  const base = { parcel_id: parcel.id || null, listing_id: listing?.id || null, state: 'UNRESOLVED', confidence: 'UNRESOLVED', offered_scope: listing?.offered_scope || 'unknown', corroboration: [], reason: '', next_action: 'Resolve the offered APNs, legal description and exact portion using source records.' };
  const out = (state, reason, corroboration = []) => ({ ...base, state, confidence: state, reason, corroboration });
  if (!listing || !pAPN || !/^\d{5}$/.test(parcel.county_fips || '')) return out('UNRESOLVED', 'The parcel or offering lacks a raw string APN and county identity.');
  const parts = Array.isArray(listing.parcels) ? listing.parcels : [];
  const part = parts.find(p => p.county_fips === parcel.county_fips && typeof p.apn === 'string' && p.apn.trim() === pAPN);
  const candidate = part ? { ...listing, ...part } : listing;
  const apns = (Array.isArray(candidate.apns) ? candidate.apns : [candidate.apn]).filter(a => typeof a === 'string').map(a => a.trim());
  const providerMatch = str(parcel.provider_parcel_id) && parcel.provider_parcel_id === candidate.provider_parcel_id && str(parcel.provider) && parcel.provider === candidate.provider;
  if (candidate.county_fips && candidate.county_fips !== parcel.county_fips) return out('CONFLICTING', 'The offered county and the parcel county do not agree.');
  if (!apns.includes(pAPN) && !providerMatch) return out(apns.length ? 'CONFLICTING' : 'UNRESOLVED', apns.length ? 'Raw APNs do not agree; leading zeros and internal punctuation are preserved.' : 'A marketing pin or address alone cannot verify the legal parcel.');
  if (!candidate.county_fips) return out('PROBABLE', 'An APN/provider lead matches, but county identity is missing.');
  if (candidate.identity_conflict || parcel.identity_conflict) return out('CONFLICTING', 'An unresolved source identity conflict remains.');
  if (listing.offered_scope === 'portion' || candidate.offered_scope === 'portion') return out('PROBABLE', 'The parent parcel is identified; the actual offered portion still requires a verified polygon.');
  if ((apns.length > 1 || listing.offered_scope === 'assembly') && !part) return out('PROBABLE', 'The offering names this constituent parcel; total assembly acreage cannot corroborate an individual constituent.');
  const metrics = geometryMetrics(parcel.geometry), offered = candidate.geometry ? geometryMetrics(candidate.geometry) : null;
  if (!metrics.valid) return out('PROBABLE', 'The APN matches but the legal parcel geometry needs validation.');
  let geometryMatch = false;
  if (candidate.geometry) {
    if (!offered?.valid) return out('PROBABLE', 'Offered geometry is invalid or requires a full topology check.');
    geometryMatch = canonicalGeometry(parcel.geometry) === canonicalGeometry(candidate.geometry);
    if (!geometryMatch) return out('CONFLICTING', 'The offered polygon differs from the identified whole parcel; reconcile a split, assembly or misplaced geometry.');
  }
  const acres = candidate.advertised_acres ?? candidate.acreage;
  const acreageMatch = finite(acres) && acres > 0 && Math.abs(acres - metrics.computed_acres) / metrics.computed_acres <= 0.02;
  if (finite(acres) && !acreageMatch) return out('CONFLICTING', 'Advertised and computed whole-parcel acreage differ by more than the provisional 2% reconciliation tolerance.');
  if (!sourceOK(candidate.source_url || candidate.listing_url || candidate.url) || !sourceOK(parcel.source_url)) return out('PROBABLE', 'Identity aligns, but both offering and parcel source attribution are required.');
  if (!['whole_parcel', 'assembly'].includes(listing.offered_scope) || listing.scope_verified !== true) return out('PROBABLE', 'Identity aligns, but the source has not verified the complete offered scope.');
  if (geometryMatch || acreageMatch) return out('VERIFIED', 'County and raw APN/provider identity agree, with corroboration for the verified offered scope.', [providerMatch ? 'provider_parcel_id' : 'county_and_raw_apn', ...(geometryMatch ? ['exact_geometry'] : []), ...(acreageMatch ? ['acreage_within_provisional_2_percent'] : [])]);
  return out('PROBABLE', 'Identity agrees, but geometry or whole-parcel acreage corroboration is missing.');
}
