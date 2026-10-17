// Ratification-bound bar for src/adjudicator.ts -- capability C-S3 adjudicate (WS-3, Plan v1.1 s5).
// Source: SRS src:srs-spec@2, sha256 109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614.
// Written against the architect's ratified records only: L2 sr:L2:C-S3 (rq-046), sr:L2:R-S4 (rq-049),
// sr:L2:R-S5 (rq-050); L3 sr:L3:adjudicator-interface (rq-066), sr:L3:ws3-field-types (rq-061).
// The two replay fixtures A9 names (a rater-C record; a C-S5 report) are INLINE below, so this file's own digest
// pins them: a fixture cannot change under a passing bar.

import test from 'node:test';
import assert from 'node:assert/strict';
import * as adj from '../src/adjudicator.ts';

const DIMS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11'];
const sorted = (xs) => [...xs].sort();                          // ECMAScript default sort (rq-066 canonical order)
const vec = (over = {}) => Object.fromEntries(DIMS.map((d) => [d, over[d] ?? 2]));
const rec = (rater, over = {}, extra = {}) => ({
  rater, model: 'm-1', manifest_hash: 'a'.repeat(64), vector: vec(over),
  evidence: { P6: 'spec.md:214' }, provisional: true, ...extra,
});

// --- the replay fixtures (A9; recorded at freeze 2) ---
const RATER_C = Object.freeze({ rater: 'C', model: 'm-1', manifest_hash: 'a'.repeat(64),
  vector: vec({ P6: 2 }), evidence: { P6: 'spec.md:214' }, provisional: true });
const C_S5_REPORT = Object.freeze({ clause: 'CL-1', dimension: 'P6', replayed: true });

const codeOf = (fn) => { try { fn(); } catch (e) { return e && e.code; } return undefined; };

test('surface: route and adjudicate are exported functions', () => {
  assert.equal(typeof adj.route, 'function');
  assert.equal(typeof adj.adjudicate, 'function');
});

// --- W-CS3-N (nominal), first half: routing ---
test('W-CS3-N: A P6=2, B P6=1, no zeros -> {route:{P6:"third-rater"}, contested_knockouts:[]}', () => {
  assert.deepEqual(adj.route(rec('A', { P6: 2 }), rec('B', { P6: 1 })),
    { route: { P6: 'third-rater' }, contested_knockouts: [] });
});

// --- W-CS3-N, second half: after rater C (the replayed fixture) ---
test('W-CS3-N: after rater C, P6 takes the consensus value and the report is PRINTED, provisional:false', () => {
  const r = adj.adjudicate(rec('A', { P6: 2 }), rec('B', { P6: 1 }), { c: RATER_C });
  assert.deepEqual(r, { vector: vec({ P6: 2 }), contested_knockouts: [], provisional: false });
  assert.deepEqual(Object.keys(r.vector), sorted(DIMS), 'PRINTED vector keys in canonical order');
  assert.ok(!('disposition' in r) && !('readiness' in r), 'no disposition text until method s6.2 is registered');
});

test('PENDING: a routed dimension with no c -> {route, contested_knockouts:[], provisional:true}', () => {
  assert.deepEqual(adj.adjudicate(rec('A', { P6: 2 }), rec('B', { P6: 1 })),
    { route: { P6: 'third-rater' }, contested_knockouts: [], provisional: true });
});

// --- W-CS3-Δ1 (either-rater zero) and R-S4 ---
test('W-CS3-Δ1: B scores P3=0 -> WITHHELD, contested_knockouts ["P3"], queue human, no disposition', () => {
  const r = adj.adjudicate(rec('A'), rec('B', { P3: 0 }));
  assert.deepEqual(r, { disposition_line: 'WITHHELD', contested_knockouts: ['P3'], queue: 'human' });
});

test('R-S4: a zero is a contested knockout, not a routed dimension', () => {
  assert.deepEqual(adj.route(rec('A', { P3: 0 }), rec('B', { P3: 1 })), { route: {}, contested_knockouts: ['P3'] });
});

// --- W-CS3-Δ2 (verified vacuous-pass report present) and R-S5 ---
test('W-CS3-Δ2: zero-free vector + replayed C-S5 report -> SUSPENDED, cause vacuous-pass:<CL>, queue human', () => {
  const r = adj.adjudicate(rec('A'), rec('B'), { attacks: [C_S5_REPORT] });
  assert.deepEqual(r, { disposition_line: 'SUSPENDED', cause: 'vacuous-pass:CL-1', contested_knockouts: ['P6'], queue: 'human' });
});

test('R-S5 + precedence: an attack outranks a zero; SUSPENDED carries the COMPLETE K, canonically ordered', () => {
  const r = adj.adjudicate(rec('A', { P2: 0 }), rec('B'), { attacks: [C_S5_REPORT] });
  assert.equal(r.disposition_line, 'SUSPENDED');
  assert.deepEqual(r.contested_knockouts, sorted(['P2', 'P6']));
});

// --- the third-rater tie (c:adjudicator:tie) ---
test('tie: A, B and C pairwise different on a routed dimension -> WITHHELD with that dimension in K', () => {
  const r = adj.adjudicate(rec('A', { P6: 2 }), rec('B', { P6: 1 }), { c: rec('C', { P6: 0 }) });
  assert.deepEqual(r, { disposition_line: 'WITHHELD', contested_knockouts: ['P6'], queue: 'human' });
});

test('K is the deduplicated union of zeros, ties and attacks, in canonical order (P10 before P2)', () => {
  const r = adj.adjudicate(rec('A', { P2: 0, P6: 2 }), rec('B', { P10: 0, P6: 1 }),
    { c: rec('C', { P2: 0, P10: 0, P6: 0 }), attacks: [{ clause: 'CL-9', dimension: 'P2', replayed: true }] });
  assert.equal(r.disposition_line, 'SUSPENDED');
  assert.deepEqual(r.contested_knockouts, ['P10', 'P2', 'P6']);
});

// --- several attacks (c:adjudicator:attack-cause) ---
test('several attacks: cause names the clause that sorts first; every attacked dimension enters K; duplicates once', () => {
  const r = adj.adjudicate(rec('A'), rec('B'), { attacks: [
    { clause: 'CL-B', dimension: 'P2', replayed: true },
    { clause: 'CL-A', dimension: 'P5', replayed: true },
    { clause: 'CL-A', dimension: 'P5', replayed: true },
  ] });
  assert.equal(r.cause, 'vacuous-pass:CL-A');
  assert.deepEqual(r.contested_knockouts, ['P2', 'P5']);
});

// --- agreed dimensions (c:adjudicator:agreed-dimensions) ---
test('agreed dimensions are copied unchanged; C decides only the routed ones', () => {
  const r = adj.adjudicate(rec('A', { P1: 1, P6: 2 }), rec('B', { P1: 1, P6: 1 }), { c: rec('C', { P1: 2, P6: 1 }) });
  assert.equal(r.provisional, false);
  assert.equal(r.vector.P1, 1, "C's score on an agreed dimension is ignored");
  assert.equal(r.vector.P6, 1, 'the routed dimension takes the value two of A, B, C share');
});

// --- the input domain (c:adjudicator:input-domain, rq-063 item 5) ---
test('A-DIM-01: route refuses mismatched key sets and produces no result', () => {
  const short = rec('B'); delete short.vector.P11;
  assert.equal(codeOf(() => adj.route(rec('A'), short)), 'A-DIM-01');
});

test('A-DIM-01: adjudicate refuses a c with a different key set, and an attack on an unknown dimension', () => {
  const c = rec('C', { P6: 2 }); c.vector.P12 = 2;
  assert.equal(codeOf(() => adj.adjudicate(rec('A', { P6: 2 }), rec('B', { P6: 1 }), { c })), 'A-DIM-01');
  assert.equal(codeOf(() => adj.adjudicate(rec('A'), rec('B'),
    { attacks: [{ clause: 'CL-1', dimension: 'P99', replayed: true }] })), 'A-DIM-01');
});

// --- determinism (C-S3 determinism note; V-S2) ---
test('route and adjudicate are pure: same inputs, same output, inputs untouched', () => {
  const a = rec('A', { P6: 2 }), b = rec('B', { P6: 1 });
  const before = JSON.stringify([a, b, RATER_C]);
  const r1 = adj.adjudicate(a, b, { c: RATER_C }), r2 = adj.adjudicate(a, b, { c: RATER_C });
  assert.deepEqual(r1, r2);
  assert.deepEqual(adj.route(a, b), adj.route(a, b));
  assert.equal(JSON.stringify([a, b, RATER_C]), before);
});
