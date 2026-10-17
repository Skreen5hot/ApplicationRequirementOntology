// HUMAN-RATIFIED acceptance oracle for capability C-S3 adjudicate (path "adjudicate"), WS-3.
// It imports the REAL module and runs the capability's end-to-end path from the source's own journey:
// J-S1 step 3 -- "C-S3 adjudicates the pair -> adjudicated report" -- including the third-rater turn (W-CS3-N) on the
// replayed rater-C fixture A9 names, and V-S2: anyone, later, reaches the same verdict from the same records.
// Source: src:srs-spec@2 (109e1b50...c614). Ratified records: sr:L2:C-S3 (rq-046), sr:L3:adjudicator-interface (rq-066).

import test from 'node:test';
import assert from 'node:assert/strict';
import { adjudicate, route } from '../../src/adjudicator.ts';

const DIMS = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'P11'];
const grade = (rater, p6) => ({ rater, model: 'm-1', manifest_hash: 'a'.repeat(64),
  vector: Object.fromEntries(DIMS.map((d) => [d, d === 'P6' ? p6 : 2])), evidence: { P6: 'spec.md:214' }, provisional: true });
const RATER_C = Object.freeze(grade('C', 2));

test('J-S1 step 3: two isolated grades route P6 to a third rater, and C settles it -> a printed, non-provisional report', () => {
  const a = grade('A', 2), b = grade('B', 1);
  assert.deepEqual(route(a, b).route, { P6: 'third-rater' });
  const pending = adjudicate(a, b);
  assert.equal(pending.provisional, true, 'without rater C the report is provisional');
  const report = adjudicate(a, b, { c: RATER_C });
  assert.equal(report.provisional, false);
  assert.deepEqual(report.contested_knockouts, []);
  assert.equal(report.vector.P6, 2);
});

test('V-S2: the verdict recomputes, by pure function, from the same committed records', () => {
  const recs = JSON.parse(JSON.stringify([grade('A', 2), grade('B', 1), RATER_C]));
  const first = adjudicate(recs[0], recs[1], { c: recs[2] });
  const again = adjudicate(JSON.parse(JSON.stringify(recs[0])), JSON.parse(JSON.stringify(recs[1])), { c: JSON.parse(JSON.stringify(recs[2])) });
  assert.deepEqual(again, first);
});
