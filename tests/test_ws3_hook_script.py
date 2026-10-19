"""The hook script cannot be bypassed by a pathname containing a line terminator (rq-083, the architect's amendment of
2026-10-19). Such a path cannot be created on every filesystem the suite runs on, so the counterexample drives the
script's own exported selection and decision functions directly, in node, with a seeded staged-status stream -- and the
same stream is shown to slip past the previous `/^ledger\\/.*\\.jsonl$/` predicate."""
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "spike" / "projections" / "ws3" / "nonbuilt" / ".githooks" / "check-ledger.mjs"

PROBE = r"""
import { pathToFileURL } from 'node:url';
const hook = await import(pathToFileURL(process.argv[2]).href);
const nl = 'ledger/a\nb.jsonl', cr = 'ledger/a\rb.jsonl', ls = 'ledger/a\u2028b.jsonl';
const z = (...pairs) => pairs.map(([s, p]) => s + '\0' + p + '\0').join('');
const appendOnly = (before, after) => after.startsWith(before) && after.slice(before.length).endsWith('\n')
  ? { ok: true } : { ok: false, code: 'H-LEDGER-01' };                 // a stand-in with the ratified contract's shape
const blobs = { ['HEAD:' + nl]: '{"seq":1}\n', [':' + nl]: '{"seq":9}\n' };   // a rewrite of the first line
const read = (spec) => { if (!(spec in blobs)) throw new Error('no blob ' + JSON.stringify(spec)); return blobs[spec]; };
const out = {
  selected: [nl, cr, ls].map((p) => hook.isLedgerPath(p)),
  oldPredicate: [nl, cr, ls].map((p) => /^ledger\/.*\.jsonl$/.test(p)),
  changes: hook.ledgerChanges(z(['M', nl], ['M', 'src/ledger.ts'], ['D', cr])),
  rewrite: hook.refusals(hook.ledgerChanges(z(['M', nl])), read, appendOnly),
  deletion: hook.refusals(hook.ledgerChanges(z(['D', nl])), read, appendOnly),
  notLedger: ['ledger.jsonl', 'ledger/x.json', 'xledger/a.jsonl'].map((p) => hook.isLedgerPath(p)),
};
console.log(JSON.stringify(out));
"""


@pytest.fixture(scope="module")
def probe(tmp_path_factory):
    f = tmp_path_factory.mktemp("hook") / "probe.mjs"
    f.write_text(PROBE, encoding="utf-8")
    r = subprocess.run(["node", str(f), str(HOOK)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    return json.loads(r.stdout)


def test_a_ledger_path_with_a_line_terminator_is_selected_and_the_old_predicate_would_skip_it(probe):
    assert probe["selected"] == [True, True, True]
    assert probe["oldPredicate"] == [False, False, False], "the counterexample fails against the previous .* predicate"
    assert [c["path"] for c in probe["changes"]] == ["ledger/a\nb.jsonl", "ledger/a\rb.jsonl"]


def test_rewriting_or_deleting_that_path_is_refused(probe):
    assert probe["rewrite"] == [{"path": "ledger/a\nb.jsonl", "code": "H-LEDGER-01", "why": "an existing ledger line was rewritten"}]
    assert probe["deletion"] == [{"path": "ledger/a\nb.jsonl", "code": "H-LEDGER-01", "why": "a tracked ledger file was deleted or moved away"}]


def test_only_ledger_paths_are_selected(probe):
    assert probe["notLedger"] == [False, False, False]
