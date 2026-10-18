// Called by .githooks/pre-commit. Git/index PLUMBING ONLY: it enumerates the staged ledger/**/*.jsonl changes and hands
// each file's committed and staged bytes to the BUILT module's checkAppendOnly, which alone decides (rq-035 = A).
// Fail-closed throughout (rq-072, the architect's amendment of 2026-10-18):
//   exit 1 -- H-LEDGER-01: a rewritten line, a deleted ledger file, or a rename/move away from a ledger path;
//   exit 2 -- operational failure: any git, index or blob-read error, or content that is not valid UTF-8.
// Nothing is ever converted to "" or to an empty file list; an empty predecessor is used ONLY for a file git itself
// reports as added (status A), which is also how every file of an initial commit is reported.
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';

const LEDGER = /^ledger\/.*\.jsonl$/;
const utf8 = new TextDecoder('utf-8', { fatal: true });   // malformed bytes THROW, never decode to replacement chars

function git(args, cwd) {                                 // raises on any failure -- no catch-all
  return execFileSync('git', args, { cwd, maxBuffer: 1 << 30, stdio: ['ignore', 'pipe', 'pipe'] });
}

function blob(spec, top) {
  return utf8.decode(git(['cat-file', 'blob', spec], top));
}

function stagedLedgerChanges(top) {
  // NUL-delimited: status \0 path \0 ... ; --no-renames reports a rename as D(old) + A(new), so the move away from a
  // ledger path is refused as a deletion
  const out = git(['diff', '--cached', '--name-status', '--no-renames', '-z'], top).toString('utf8');
  const parts = out.split('\0');
  if (parts[parts.length - 1] === '') parts.pop();
  if (parts.length % 2 !== 0) throw new Error('unparseable staged status from git diff -z');
  const changes = [];
  for (let i = 0; i < parts.length; i += 2) {
    const [status, path] = [parts[i], parts[i + 1]];
    if (LEDGER.test(path)) changes.push({ status, path });
  }
  return changes;
}

async function main() {
  const top = git(['rev-parse', '--show-toplevel']).toString('utf8').trim();
  if (!top) throw new Error('git rev-parse --show-toplevel returned nothing');
  const { checkAppendOnly } = await import(pathToFileURL(join(top, 'src', 'ledger.ts')).href);
  let refused = false;
  for (const { status, path } of stagedLedgerChanges(top)) {
    if (status === 'D') {
      console.error('%s: H-LEDGER-01 -- a tracked ledger file was deleted or moved away (W-CS7-Δ1)', path);
      refused = true;
      continue;
    }
    if (status !== 'A' && status !== 'M') {
      console.error('%s: H-LEDGER-01 -- staged status %s is not an append (W-CS7-Δ1)', path, status);
      refused = true;
      continue;
    }
    const before = status === 'A' ? '' : blob('HEAD:' + path, top);
    const after = blob(':' + path, top);                  // the STAGED blob, from the index -- never the working tree
    const r = checkAppendOnly(before, after);
    if (!r.ok) {
      console.error('%s: %s -- an existing ledger line was rewritten (W-CS7-Δ1)', path, r.code);
      refused = true;
    }
  }
  return refused ? 1 : 0;
}

try {
  process.exit(await main());
} catch (e) {
  console.error('check-ledger: operational failure, refusing the commit: %s', (e && (e.stderr || e.message)) || e);
  process.exit(2);
}
