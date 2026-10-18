"""A file row's published duties describe the file (IA Ops finding 2026-10-17, "the queue row publishes a truncated test
title and would drop a double-quoted one"). `displayDuties.tests` is what ratification confers over, so for every LIVE
file row that carries one, it must equal -- byte for byte, in order -- the titles the artifact declares, and
`assertions` must equal the number of test(...) declarations. The expected titles come from an INDEPENDENT reader
(Python's own tokenizer over each JS string literal), never from queue_bars' extractor, which is what is under test."""
import ast
import importlib.util
import io
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
spec = importlib.util.spec_from_file_location("ws3_queue_bars", ROOT / "spike" / "graph" / "ws3" / "queue_bars.py")
QB = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(ROOT / "spike" / "graph" / "ws3"))
spec.loader.exec_module(QB)


def declared_titles(text):
    """Titles as the file declares them: each `test(` line's first token, read as a string literal by Python's own
    tokenizer (JS and Python agree on '...'/"..." with \\' \\" \\\\ escapes, which is every title in these files)."""
    out = []
    for line in text.splitlines():
        if not line.startswith("test("):
            continue
        tok = next(t for t in tokenize.generate_tokens(io.StringIO(line[len("test("):].lstrip()).readline))
        assert tok.type == tokenize.STRING, "a test title that is not a plain string literal: %r" % line
        out.append(ast.literal_eval(tok.string))
    return out


def _live_file_rows_with_tests():
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    dead = {r.get("supersedes") for r in rows if r.get("supersedes")}
    return [r for r in rows if r.get("artifactFileDigest") and r["id"] not in dead
            and isinstance((r.get("displayDuties") or {}).get("tests"), list)]


def test_every_live_rows_published_titles_are_the_files_own():
    rows = _live_file_rows_with_tests()
    assert len(rows) >= 4, "examined %d live file rows with a tests list (two bars, two oracles)" % len(rows)
    for r in rows:
        want = declared_titles((ROOT / r["artifact"]).read_text(encoding="utf-8"))
        got = r["displayDuties"]["tests"]
        wrong = [(i + 1, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w]
        assert len(got) == len(want) and not wrong, "%s: published %d titles, the file declares %d; mismatches %s" % (
            r["id"], len(got), len(want), wrong)
        assert r["assertions"] == len(want), "%s: assertions %s, the file declares %d" % (r["id"], r["assertions"], len(want))


SYNTHETIC = """import test from 'node:test';
test('a title with an escaped \\'apostrophe\\' in it', () => {});
test("a title with an escaped \\"double quote\\" in it", () => {});
test("the last entry's seq, double-quoted, no escape needed", () => {});
"""


def test_the_extractor_reads_both_quote_styles_and_escapes_and_matches_node(tmp_path):
    want = ["a title with an escaped 'apostrophe' in it", 'a title with an escaped "double quote" in it',
            "the last entry's seq, double-quoted, no escape needed"]
    assert QB.test_titles("synthetic", SYNTHETIC) == want == declared_titles(SYNTHETIC)
    f = tmp_path / "synthetic.test.mjs"
    f.write_text(SYNTHETIC, encoding="utf-8")
    r = subprocess.run(["node", "--test", "--test-reporter=tap", str(f)], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    assert re.search(r"^# tests 3$", r.stdout, re.M), r.stdout
    ran = [m.group(1) for m in re.finditer(r"^ok \d+ - (.*)$", r.stdout, re.M)]
    assert ran == want, ran


def test_a_title_that_is_not_a_string_literal_refuses_rather_than_shortening_the_list():
    with pytest.raises(SystemExit, match="declares 2 test"):
        QB.test_titles("synthetic", "test('one', () => {});\ntest(`two`, () => {});\n")
