// HUMAN-RATIFIED acceptance oracle for capability C-S3 adjudicate (path "adjudicate"), WS-3.
// It imports the REAL module from its accepted L2 home (tools/adjudicator/, adj:ws3-module-homes = B at rq-074) and
// runs the capability's end-to-end path from the source's own journey: J-S1 step 3 -- "C-S3 adjudicates the pair ->
// adjudicated report" -- including the third-rater turn (W-CS3-N) on the replayed rater-C fixture A9 names.
// The inline A and B values are committed GradeRecord fixtures representing the two isolated grades; this oracle does
// not itself prove grader isolation (that is C-S2's). It does NOT exercise V-S2: V-S2 governs recomputing printed
// disposition and readiness lines per method s6.2, which rq-066 keeps absent until that method is registered -- V-S2
// stays pending under diag:external-method-artifacts.
// Source: src:srs-spec@2 (109e1b50...c614). Ratified records: sr:L2:C-S3 (rq-046), sr:L3:adjudicator-interface (rq-066).

import test from 'node:test';
import assert from 'node:assert/strict';
import { adjudicate, route } from '../../tools/adjudicator/adjudicator.ts';

const DIMS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11'];
const grade = (rater, p6) => ({ rater, model: 'm-1', manifest_hash: 'a'.repeat(64),
  vector: Object.fromEntries(DIMS.map((d) => [d, d === 'P6' ? p6 : 2])), evidence: { P6: 'spec.md:214' }, provisional: true });
const RATER_C = Object.freeze(grade('C', 2));
const clone = (x) => JSON.parse(JSON.stringify(x));

test('J-S1 step 3: two isolated grades route P6 to a third rater, and C settles it -> the complete PRINTED report', () => {
  const a = grade('A', 2), b = grade('B', 1);
  assert.deepEqual(route(a, b).route, { P6: 'third-rater' });
  const pending = adjudicate(a, b);
  assert.equal(pending.provisional, true, 'without rater C the report is provisional');
  const report = adjudicate(a, b, { c: RATER_C });
  // the complete PRINTED variant: every agreed dimension retained, P6 settled to 2, nothing else
  const vector = Object.fromEntries(DIMS.map((d) => [d, 2]));
  assert.deepEqual(report, { vector, contested_knockouts: [], provisional: false });
  for (const absent of ['route', 'disposition_line', 'queue', 'disposition', 'readiness'])
    assert.ok(!(absent in report), absent + ' is absent from a PRINTED report');
});

test('C-S3 determinism: the adjudicated report recomputes, by pure function, from the same committed GradeRecords', () => {
  const original = [grade('A', 2), grade('B', 1), clone(RATER_C)];
  const snapshot = clone(original);                       // taken BEFORE the first call
  const first = adjudicate(original[0], original[1], { c: original[2] });
  assert.deepEqual(original, snapshot, 'the first call left its inputs untouched');
  const fresh = clone(snapshot);
  const again = adjudicate(fresh[0], fresh[1], { c: fresh[2] });
  assert.deepEqual(fresh, snapshot, 'the second call left its inputs untouched');
  assert.deepEqual(again, first, 'the same records give the same complete report');
});
