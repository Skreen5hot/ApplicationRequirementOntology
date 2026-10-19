// HUMAN-RATIFIED acceptance oracle for capability C-S7 register (path "register"), WS-3.
// The capability's end-to-end path from the source: J-S1 step 4 (append the registration) and J-S4 step 3 (append the
// ratification event), the full chain verifying from genesis (W-CS7-N, amended), and W-CS7-Δ1 through a REAL git
// commit with core.hooksPath set -- the architect's rq-035 condition 3: "a hook that never fires must not pass".
// PRECONDITION, PROVISIONED NOT DETECTED: git on PATH and the non-built .githooks/ (pre-commit + check-ledger.mjs) in
// the workspace, the wrapper executable where the platform represents POSIX mode (rq-071). If any is missing this
// oracle FAILS -- it is never skipped (rq-035 condition 3).
// Source: src:srs-spec@2 (109e1b50...c614). Ratified: sr:L2:C-S7 (rq-047), sr:L2:LedgerEntry (rq-053),
// sr:L3:ledger-interface (rq-064). Every value asserted below is already conferred there (rq-070, 2026-10-18).
// BOUND TO THE RATIFIED NON-BUILT DELIVERY SET (rq-081, 2026-10-19): the wrapper (rq-082), the hook script (rq-085) and
// the delivery descriptor (rq-086) at the digests pinned below; the provisioned hook files must be exactly those bytes,
// or this oracle FAILS. The descriptor binds their modes, install paths and core.hooksPath.

import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { chmodSync, cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { appendEntry, verifyChain } from '../../src/ledger.ts';

const WORKSPACE = join(dirname(fileURLToPath(import.meta.url)), '..', '..');
const GENESIS = '0'.repeat(64);
const PINNED_WRAPPER = 'sha256:8a915d8f6e8a3abe9e2287c615eb86bb2c34db8614a5c62c3b9bd8f084720342';    // rq-082
const PINNED_SCRIPT = 'sha256:72527039ce71314fab43bf4c30a339809b61c3c5ac4c928fcde8e864ad3897f9';     // rq-085
const PINNED_DELIVERY = 'sha256:ac3fe658047509395f827b22253c2823e5a4932b1a4d687d30fd03e80a25e7a2';   // rq-086
const fileSha = (p) => 'sha256:' + createHash('sha256').update(readFileSync(p)).digest('hex');
const canon = (v) => Array.isArray(v) ? '[' + v.map(canon).join(',') + ']'
  : (v && typeof v === 'object') ? '{' + Object.keys(v).sort().map((k) => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}'
  : JSON.stringify(v);
const hashOf = (seq, prev, kind, payload) =>
  createHash('sha256').update(Buffer.from(canon([seq, prev, kind, payload]), 'utf8')).digest('hex');
const entry = (seq, prev, kind, payload) => ({ seq, prev, kind, payload, hash: hashOf(seq, prev, kind, payload) });
const lines = (text) => { assert.ok(text.endsWith('\n'), 'whole JSONL lines'); return text.slice(0, -1).split('\n').map((l) => JSON.parse(l)); };

const REG = { spec: 'specs/x', rev: 'abc123', vector: { P1: 2 } };
const RAT = { rev: 'abc123' };

test('J-S1 step 4 + J-S4 step 3: registration then ratification -- each event exactly as appended; the chain verifies from genesis', () => {
  const dir = mkdtempSync(join(tmpdir(), 'c-s7-'));
  const path = join(dir, 'ledger.jsonl');
  writeFileSync(path, '');
  const reg = appendEntry(path, 'registration', REG);
  const rat = appendEntry(path, 'ratification', RAT);
  const wantReg = entry(1, GENESIS, 'registration', REG);
  const wantRat = entry(2, wantReg.hash, 'ratification', RAT);
  assert.deepEqual(reg, wantReg, 'the registration: seq 1, genesis prev, kind registration, the exact payload');
  assert.deepEqual(rat, wantRat, 'the ratification: seq 2, prev = the registration hash, kind ratification, the exact payload');
  const chain = lines(readFileSync(path, 'utf8'));
  assert.deepEqual(chain, [wantReg, wantRat], 'the persisted ledger is exactly those two events, in order');
  assert.deepEqual(verifyChain(chain), { ok: true });
});

test('W-CS7-Δ1 through a real commit: the hook refuses a rewrite, a deletion, and the seeded corrupt-index and malformed-staged-blob failures; it admits the intended append', () => {
  const hooks = join(WORKSPACE, '.githooks');
  assert.ok(existsSync(join(hooks, 'pre-commit')) && existsSync(join(hooks, 'check-ledger.mjs')),
    'PRECONDITION: the non-built .githooks/ wrapper must be provisioned in the workspace (rq-035 condition 3)');
  assert.equal(fileSha(join(hooks, 'pre-commit')), PINNED_WRAPPER, 'PRECONDITION: the provisioned wrapper is the ratified rq-082 bytes');
  assert.equal(fileSha(join(hooks, 'check-ledger.mjs')), PINNED_SCRIPT, 'PRECONDITION: the provisioned hook script is the rq-085 bytes');
  assert.equal(spawnSync('git', ['--version']).status, 0, 'PRECONDITION: git must be provisioned (rq-035 condition 3)');
  if (process.platform !== 'win32')
    assert.ok(statSync(join(hooks, 'pre-commit')).mode & 0o111, 'PRECONDITION: the wrapper is provisioned executable (rq-071)');

  const repo = mkdtempSync(join(tmpdir(), 'c-s7-repo-'));
  const git = (...a) => spawnSync('git', a, { cwd: repo, encoding: 'utf8' });
  git('init', '-q');
  git('config', 'user.email', 'oracle@example.invalid');
  git('config', 'user.name', 'C-S7 oracle');
  cpSync(join(WORKSPACE, 'src'), join(repo, 'src'), { recursive: true });
  cpSync(hooks, join(repo, '.githooks'), { recursive: true });
  if (process.platform !== 'win32') chmodSync(join(repo, '.githooks', 'pre-commit'), 0o755);
  git('config', 'core.hooksPath', '.githooks');
  mkdirSync(join(repo, 'ledger'));
  const path = join(repo, 'ledger', 'ledger.jsonl');
  writeFileSync(path, '');
  appendEntry(path, 'registration', REG);
  git('add', '-A');
  assert.equal(git('commit', '-q', '-m', 'registration').status, 0, 'a first append commits');
  const restore = () => { git('reset', '-q'); execFileSync('git', ['checkout', '--', 'ledger/ledger.jsonl'], { cwd: repo }); };

  // a rewritten line
  writeFileSync(path, readFileSync(path, 'utf8').replace('"registration"', '"ratification"'));
  git('add', '-A');
  const refused = git('commit', '-q', '-m', 'rewrite');
  assert.notEqual(refused.status, 0, 'the hook must fire and refuse the rewrite');
  assert.match(refused.stderr + refused.stdout, /H-LEDGER-01/);
  restore();

  // a staged deletion of a tracked ledger file (rq-072 (3))
  assert.equal(git('rm', '-q', 'ledger/ledger.jsonl').status, 0);
  const deleted = git('commit', '-q', '-m', 'delete');
  assert.notEqual(deleted.status, 0, 'the hook must refuse the deletion');
  assert.match(deleted.stderr + deleted.stdout, /H-LEDGER-01/);
  git('reset', '-q', '--', 'ledger/ledger.jsonl');
  execFileSync('git', ['checkout', '--', 'ledger/ledger.jsonl'], { cwd: repo });

  // a seeded git/index failure fails CLOSED (rq-072 (1)): the hook script run against a corrupt index exits NONZERO
  // (rq-081: nonzero is what rq-072 confers; no particular status or message is asserted)
  const corrupt = join(repo, 'corrupt-index');
  writeFileSync(corrupt, 'not an index');
  const broken = spawnSync('node', [join('.githooks', 'check-ledger.mjs')], { cwd: repo, encoding: 'utf8',
    env: { ...process.env, GIT_INDEX_FILE: corrupt } });
  assert.notEqual(broken.status, 0, 'a corrupt index is a refusal, never a pass: ' + broken.stderr);

  // a seeded staged blob that cannot be read as the function's input (rq-072 (7)): an append of invalid UTF-8
  writeFileSync(path, Buffer.concat([readFileSync(path), Buffer.from([0xff, 0xfe, 0x0a])]));
  git('add', '-A');
  const malformed = git('commit', '-q', '-m', 'malformed');
  assert.notEqual(malformed.status, 0, 'malformed ledger content is refused');
  restore();

  // the intended append still commits -- and what was committed is that ratification event (rq-070 (4))
  appendEntry(path, 'ratification', RAT);
  git('add', '-A');
  assert.equal(git('commit', '-q', '-m', 'ratification').status, 0, 'an append still commits');
  const committed = lines(execFileSync('git', ['show', 'HEAD:ledger/ledger.jsonl'], { cwd: repo, encoding: 'utf8' }));
  const wantReg = entry(1, GENESIS, 'registration', REG);
  assert.deepEqual(committed[committed.length - 1], entry(2, wantReg.hash, 'ratification', RAT), 'the committed final entry is the intended ratification');
  assert.deepEqual(verifyChain(committed), { ok: true });
});
