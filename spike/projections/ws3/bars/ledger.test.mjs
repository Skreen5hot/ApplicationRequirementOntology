// Ratification-bound bar for src/ledger.ts -- capability C-S7 register (WS-3, Plan v1.1 s5).
// Source: SRS src:srs-spec@2, sha256 109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614 (W-CS7-N as
// amended 2026-10-17: hash = sha256(seq || prev || kind || payload)).
// Written against the architect's ratified records only: L2 sr:L2:C-S7 (rq-047), sr:L2:LedgerEntry (rq-053);
// L3 sr:L3:ledger-interface (rq-064), sr:L3:ws3-field-types (rq-061); adjudication rq-038 (A) and rq-035 (A).
// Expected hashes are computed HERE, independently, from the ratified encoding -- never read back from the module.

import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import * as ledger from '../src/ledger.ts';

const GENESIS = '0'.repeat(64);
// rq-064: canonical JSON -- keys sorted, compact separators, UTF-8
const canon = (v) => Array.isArray(v) ? '[' + v.map(canon).join(',') + ']'
  : (v && typeof v === 'object') ? '{' + Object.keys(v).sort().map((k) => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}'
  : JSON.stringify(v);
const expectHash = (seq, prev, kind, payload) =>
  createHash('sha256').update(Buffer.from(canon([seq, prev, kind, payload]), 'utf8')).digest('hex');
const PAYLOAD = { spec: 'specs/x', rev: 'abc123', vector: { P1: 2, P6: 1 } };

const build = (n) => {
  let chain = [];
  for (let i = 0; i < n; i++) chain = [...chain, ledger.nextEntry(chain, i % 2 ? 'ratification' : 'registration', { ...PAYLOAD, i })];
  return chain;
};

test('surface: the five ratified functions are exported', () => {
  for (const f of ['entryHash', 'nextEntry', 'verifyChain', 'checkAppendOnly', 'appendEntry'])
    assert.equal(typeof ledger[f], 'function', f);
});

test('W-CS7-N (amended): hash = sha256 hex of canonical JSON of [seq, prev, kind, payload]', () => {
  assert.equal(ledger.entryHash(7, 'f'.repeat(64), 'registration', PAYLOAD), expectHash(7, 'f'.repeat(64), 'registration', PAYLOAD));
  assert.match(ledger.entryHash(1, GENESIS, 'registration', {}), /^[0-9a-f]{64}$/);
});

test('rq-038 = A: kind is IN the preimage -- changing kind alone changes the hash', () => {
  assert.notEqual(ledger.entryHash(7, GENESIS, 'registration', PAYLOAD), ledger.entryHash(7, GENESIS, 'ratification', PAYLOAD));
});

test('canonical: payload key order does not change the hash -- at every depth, not only the outermost', () => {
  assert.equal(ledger.entryHash(2, GENESIS, 'registration', { b: 1, a: 2 }), ledger.entryHash(2, GENESIS, 'registration', { a: 2, b: 1 }));
  // rq-077 (1): the ratified encoding sorts keys throughout the canonical JSON value
  const nestedAB = { spec: 'specs/x', vector: { P6: 1, P1: 2, sub: { z: [{ y: 1, x: 2 }], a: 0 } } };
  const nestedBA = { vector: { sub: { a: 0, z: [{ x: 2, y: 1 }] }, P1: 2, P6: 1 }, spec: 'specs/x' };
  assert.equal(ledger.entryHash(3, GENESIS, 'registration', nestedAB), ledger.entryHash(3, GENESIS, 'registration', nestedBA));
  assert.equal(ledger.entryHash(3, GENESIS, 'registration', nestedAB), expectHash(3, GENESIS, 'registration', nestedBA));
});

test('genesis: the first entry has seq 1 and prev = 64 zeros', () => {
  const e = ledger.nextEntry([], 'registration', PAYLOAD);
  assert.deepEqual(e, { seq: 1, prev: GENESIS, kind: 'registration', payload: PAYLOAD, hash: expectHash(1, GENESIS, 'registration', PAYLOAD) });
});

test('nextEntry is pure: seq = last + 1, prev = last hash, the chain is not mutated', () => {
  const chain = build(3);
  const before = JSON.stringify(chain);
  const e = ledger.nextEntry(chain, 'registration', PAYLOAD);
  assert.equal(e.seq, 4);
  assert.equal(e.prev, chain[2].hash);
  assert.equal(JSON.stringify(chain), before);
  assert.deepEqual(ledger.nextEntry(chain, 'registration', PAYLOAD), e);
});

test('nextEntry: seq = the LAST entry\'s seq + 1, not the chain length + 1', () => {
  // build() always yields seq == position, so it cannot tell the two readings apart; this entry is placed by hand
  const last = { seq: 7, prev: 'f'.repeat(64), kind: 'registration', payload: PAYLOAD,
                 hash: expectHash(7, 'f'.repeat(64), 'registration', PAYLOAD) };
  const e = ledger.nextEntry([last], 'ratification', { rev: 'abc123' });
  assert.equal(e.seq, 8);
  assert.equal(e.prev, last.hash);
  assert.equal(e.hash, expectHash(8, last.hash, 'ratification', { rev: 'abc123' }));
});

test('W-CS7-N: the full chain verifies from genesis', () => {
  assert.deepEqual(ledger.verifyChain(build(5)), { ok: true });
});

test('W-CS7-N: a chain NOT rooted at genesis fails, even when every hash is internally consistent', () => {
  // "verifies from genesis" (W-CS7-N) + genesis "seq 1 and prev = 64 zeros" (rq-064): a re-rooted or truncated chain,
  // re-hashed over its own fields, must not verify
  const rooted = (seq, prev) => [{ seq, prev, kind: 'registration', payload: PAYLOAD, hash: expectHash(seq, prev, 'registration', PAYLOAD) }];
  const reRooted = ledger.verifyChain(rooted(1, 'f'.repeat(64)));
  assert.equal(reRooted.ok, false, 'prev of the first entry is not the 64 zeros');
  assert.equal(reRooted.seq, 1);
  assert.equal(ledger.verifyChain(rooted(5, GENESIS)).ok, false, 'the first entry does not carry seq 1');
  const truncated = build(4).slice(2);
  assert.equal(ledger.verifyChain(truncated).ok, false, 'a chain with its first entries cut off');
});

test('W-CS7-Δ1: a rewrite of any hashed field fails verification at that entry -- kind alone included', () => {
  for (const [field, value] of [['payload', { tampered: true }], ['kind', 'ratification'], ['seq', 99], ['prev', 'e'.repeat(64)]]) {
    const chain = build(4).map((x) => ({ ...x }));
    chain[2] = { ...chain[2], [field]: field === 'kind' && chain[2].kind === 'ratification' ? 'registration' : value };
    const r = ledger.verifyChain(chain);
    assert.equal(r.ok, false, field);
    // the ratified signature returns { ok: false; seq } without saying whether seq is the entry's POSITION or its
    // stated seq; they coincide except when seq itself is tampered, so only that case leaves seq unasserted
    if (field !== 'seq') assert.equal(r.seq, 3, field);
  }
});

test('checkAppendOnly: appending whole JSONL lines is ok', () => {
  const before = '{"seq":1}\n';
  assert.deepEqual(ledger.checkAppendOnly(before, before + '{"seq":2}\n'), { ok: true });
  assert.deepEqual(ledger.checkAppendOnly('', '{"seq":1}\n'), { ok: true });
});

test('W-CS7-Δ1: any rewrite of an existing line -> H-LEDGER-01', () => {
  const before = '{"seq":1,"kind":"registration"}\n{"seq":2}\n';
  assert.deepEqual(ledger.checkAppendOnly(before, before.replace('registration', 'ratification')), { ok: false, code: 'H-LEDGER-01' });
  assert.deepEqual(ledger.checkAppendOnly(before, '{"seq":2}\n'), { ok: false, code: 'H-LEDGER-01' });
  assert.deepEqual(ledger.checkAppendOnly(before, before + '{"seq":3}'), { ok: false, code: 'H-LEDGER-01' }, 'a partial line is not whole');
});

test('appendEntry: appends exactly the requested next entry, one complete line per call, and never rewrites', () => {
  const dir = mkdtempSync(join(tmpdir(), 'ledger-bar-'));
  const path = join(dir, 'ledger.jsonl');
  writeFileSync(path, '');
  // rq-077 (2): the expected entries are built HERE from the ratified encoding -- never by calling nextEntry, so two
  // cooperating defects (in nextEntry and appendEntry) cannot pass together
  const RAT = { rev: 'abc123' };
  const want1 = { seq: 1, prev: GENESIS, kind: 'registration', payload: PAYLOAD, hash: expectHash(1, GENESIS, 'registration', PAYLOAD) };
  const want2 = { seq: 2, prev: want1.hash, kind: 'ratification', payload: RAT, hash: expectHash(2, want1.hash, 'ratification', RAT) };
  // rq-077 (3): after each call the file ends with \n and holds exactly one more complete JSONL line
  const completeLines = (text) => {
    assert.ok(text.endsWith('\n'), 'the file ends with a newline: the appended line is whole');
    return text.slice(0, -1).split('\n');
  };
  const e1 = ledger.appendEntry(path, 'registration', PAYLOAD);
  const first = readFileSync(path, 'utf8');
  assert.equal(completeLines(first).length, 1);
  const e2 = ledger.appendEntry(path, 'ratification', RAT);
  const text = readFileSync(path, 'utf8');
  assert.ok(text.startsWith(first), 'the first line is untouched');
  const raw = completeLines(text);
  assert.equal(raw.length, 2, 'exactly one additional line');
  assert.deepEqual(e1, want1, 'the returned registration entry');
  assert.deepEqual(e2, want2, 'the returned ratification entry');
  assert.deepEqual(raw.map((l) => JSON.parse(l)), [want1, want2], 'the persisted entries');
  assert.deepEqual(ledger.verifyChain([want1, want2]), { ok: true });
});
