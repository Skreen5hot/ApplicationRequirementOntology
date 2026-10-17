// Called by .githooks/pre-commit. For every staged ledger/*.jsonl, compares the committed bytes (HEAD) with the staged
// bytes through the BUILT module's checkAppendOnly -- the hook holds no logic of its own (rq-035 = A).
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';

const top = execFileSync('git', ['rev-parse', '--show-toplevel'], { encoding: 'utf8' }).trim();
const { checkAppendOnly } = await import(pathToFileURL(join(top, 'src', 'ledger.ts')).href);
const git = (...args) => { try { return execFileSync('git', args, { encoding: 'utf8', cwd: top }); } catch { return ''; } };

const staged = git('diff', '--cached', '--name-only', '--diff-filter=ACMR').split('\n').filter((p) => /^ledger\/.*\.jsonl$/.test(p));
let refused = false;
for (const path of staged) {
  const before = git('show', 'HEAD:' + path);
  const after = git('show', ':' + path);
  const r = checkAppendOnly(before, after);
  if (!r.ok) {
    console.error('%s: %s -- an existing ledger line was rewritten (W-CS7-Δ1)', path, r.code);
    refused = true;
  }
}
process.exit(refused ? 1 : 0);
