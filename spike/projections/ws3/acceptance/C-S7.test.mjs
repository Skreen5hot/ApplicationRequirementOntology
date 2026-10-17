// HUMAN-RATIFIED acceptance oracle for capability C-S7 register (path "register"), WS-3.
// The capability's end-to-end path from the source: J-S1 step 4 (append the registration) and J-S4 step 3 (append the
// ratification event), the full chain verifying from genesis (W-CS7-N, amended), and W-CS7-Δ1 through a REAL git
// commit with core.hooksPath set -- the architect's rq-035 condition 3: "a hook that never fires must not pass".
// PRECONDITION, PROVISIONED NOT DETECTED: git on PATH and the non-built .githooks/ (pre-commit + check-ledger.mjs) in
// the workspace. If either is missing this oracle FAILS -- it is never skipped (rq-035 condition 3).
// Source: src:srs-spec@2 (109e1b50...c614). Ratified: sr:L2:C-S7 (rq-047), sr:L3:ledger-interface (rq-064).

import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { appendEntry, verifyChain } from '../../src/ledger.ts';

const WORKSPACE = join(dirname(fileURLToPath(import.meta.url)), '..', '..');

test('J-S1 step 4 + J-S4 step 3: registration then ratification append; the chain verifies from genesis', () => {
  const dir = mkdtempSync(join(tmpdir(), 'c-s7-'));
  const path = join(dir, 'ledger.jsonl');
  writeFileSync(path, '');
  const reg = appendEntry(path, 'registration', { spec: 'specs/x', rev: 'abc123', vector: { P1: 2 } });
  const rat = appendEntry(path, 'ratification', { rev: 'abc123' });
  assert.equal(reg.seq, 1);
  assert.equal(rat.prev, reg.hash);
  const chain = readFileSync(path, 'utf8').trimEnd().split('\n').map((l) => JSON.parse(l));
  assert.deepEqual(verifyChain(chain), { ok: true });
});

test('W-CS7-Δ1 through a real commit: the hook refuses a rewritten ledger line (H-LEDGER-01), and admits an append', () => {
  const hooks = join(WORKSPACE, '.githooks');
  assert.ok(existsSync(join(hooks, 'pre-commit')) && existsSync(join(hooks, 'check-ledger.mjs')),
    'PRECONDITION: the non-built .githooks/ wrapper must be provisioned in the workspace (rq-035 condition 3)');
  assert.equal(spawnSync('git', ['--version']).status, 0, 'PRECONDITION: git must be provisioned (rq-035 condition 3)');

  const repo = mkdtempSync(join(tmpdir(), 'c-s7-repo-'));
  const git = (...a) => spawnSync('git', a, { cwd: repo, encoding: 'utf8' });
  git('init', '-q');
  git('config', 'user.email', 'oracle@example.invalid');
  git('config', 'user.name', 'C-S7 oracle');
  cpSync(join(WORKSPACE, 'src'), join(repo, 'src'), { recursive: true });
  cpSync(hooks, join(repo, '.githooks'), { recursive: true });
  git('config', 'core.hooksPath', '.githooks');
  mkdirSync(join(repo, 'ledger'));
  const path = join(repo, 'ledger', 'ledger.jsonl');
  writeFileSync(path, '');
  appendEntry(path, 'registration', { spec: 'specs/x', rev: 'abc123' });
  git('add', '-A');
  assert.equal(git('commit', '-q', '-m', 'registration').status, 0, 'a first append commits');

  writeFileSync(path, readFileSync(path, 'utf8').replace('"registration"', '"ratification"'));
  git('add', '-A');
  const refused = git('commit', '-q', '-m', 'rewrite');
  assert.notEqual(refused.status, 0, 'the hook must fire and refuse the rewrite');
  assert.match(refused.stderr + refused.stdout, /H-LEDGER-01/);

  git('reset', '-q');                                   // unstage the refused rewrite first...
  execFileSync('git', ['checkout', '--', 'ledger/ledger.jsonl'], { cwd: repo });   // ...then restore the committed bytes
  appendEntry(path, 'ratification', { rev: 'abc123' });
  git('add', '-A');
  assert.equal(git('commit', '-q', '-m', 'ratification').status, 0, 'an append still commits');
});
