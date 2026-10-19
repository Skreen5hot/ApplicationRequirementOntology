// Called by .githooks/pre-commit. Git/index PLUMBING ONLY: it enumerates the staged ledger/**/*.jsonl changes and hands
// each file's committed and staged bytes to the BUILT module's checkAppendOnly, which alone decides (rq-035 = A).
// Fail-closed throughout (rq-072, the architect's amendment of 2026-10-18):
//   exit 1 -- H-LEDGER-01: a rewritten line, a deleted ledger file, or a rename/move away from a ledger path;
//   exit 2 -- operational failure: any git, index or blob-read error, or content that is not valid UTF-8.
// Nothing is ever converted to "" or to an empty file list; an empty predecessor is used ONLY for a file git itself
// reports as added (status A), which is also how every file of an initial commit is reported.
// The selection and decision steps are exported pure functions (rq-083, 2026-10-19), so a pathname no filesystem here
// can hold -- one containing a line terminator -- can still be proved selected and refused. Run as a script, main() runs.
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { join, resolve } from 'node:path';

// rq-083: every character between the fixed prefix and suffix counts, line terminators included. A regex `.*` does not
// match \n, so `/^ledger\/.*\.jsonl$/` silently skipped a ledger pathname containing one.
export const isLedgerPath = (path) => path.startsWith('ledger/') && path.endsWith('.jsonl');

const utf8 = new TextDecoder('utf-8', { fatal: true });   // malformed bytes THROW, never decode to replacement chars

function git(args, cwd) {                                 // raises on any failure -- no catch-all
  return execFileSync('git', args, { cwd, maxBuffer: 1 << 30, stdio: ['ignore', 'pipe', 'pipe'] });
}

// NUL-delimited `git diff --cached --name-status --no-renames -z` output -> [{status, path}] for the LEDGER paths.
// --no-renames reports a rename as D(old) + A(new), so a move away from a ledger path is refused as a deletion.
export function ledgerChanges(zOutput) {
  const parts = zOutput.split('\0');
  if (parts[parts.length - 1] === '') parts.pop();
  if (parts.length % 2 !== 0) throw new Error('unparseable staged status from git diff -z');
  const changes = [];
  for (let i = 0; i < parts.length; i += 2) {
    const [status, path] = [parts[i], parts[i + 1]];
    if (isLedgerPath(path)) changes.push({ status, path });
  }
  return changes;
}

// The refusals for a set of ledger changes -> [{path, code, why}]. readBlob(spec) returns a string or THROWS; the
// append-only decision is the built checkAppendOnly's alone.
export function refusals(changes, readBlob, checkAppendOnly) {
  const out = [];
  for (const { status, path } of changes) {
    if (status === 'D') { out.push({ path, code: 'H-LEDGER-01', why: 'a tracked ledger file was deleted or moved away' }); continue; }
    if (status !== 'A' && status !== 'M') { out.push({ path, code: 'H-LEDGER-01', why: 'staged status ' + status + ' is not an append' }); continue; }
    const before = status === 'A' ? '' : readBlob('HEAD:' + path);
    const after = readBlob(':' + path);                   // the STAGED blob, from the index -- never the working tree
    const r = checkAppendOnly(before, after);
    if (!r.ok) out.push({ path, code: r.code, why: 'an existing ledger line was rewritten' });
  }
  return out;
}

async function main() {
  const top = git(['rev-parse', '--show-toplevel']).toString('utf8').trim();
  if (!top) throw new Error('git rev-parse --show-toplevel returned nothing');
  const { checkAppendOnly } = await import(pathToFileURL(join(top, 'src', 'ledger.ts')).href);
  const changes = ledgerChanges(git(['diff', '--cached', '--name-status', '--no-renames', '-z'], top).toString('utf8'));
  const refused = refusals(changes, (spec) => utf8.decode(git(['cat-file', 'blob', spec], top)), checkAppendOnly);
  for (const r of refused) console.error('%s: %s -- %s (W-CS7-Δ1)', JSON.stringify(r.path), r.code, r.why);
  return refused.length ? 1 : 0;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  try {
    process.exit(await main());
  } catch (e) {
    console.error('check-ledger: operational failure, refusing the commit: %s', (e && (e.stderr || e.message)) || e);
    process.exit(2);
  }
}
