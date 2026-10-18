"""Queue WS-3's bars, capability oracles and the non-built hook for ratification -- one row per FILE, bound to the
file's own SHA-256 (artifactFileDigest, as rq-012/rq-013), batch WS3-5.

    python spike/graph/ws3/queue_bars.py            # appends rows for files not yet queued at their current bytes
    python spike/graph/ws3/queue_bars.py --dry-run

What ratifying one means (Plan v1.1 s5; IA design note DEV-2026-10-01-d8-part2-design.md, as answered by Ops):
  - a module BAR becomes a ratified standard for that module (provisional: false); its `ratified_by` will carry the
    act (rq-id and act digest) so FX-CAP reads the chain from queue act to capability verdict;
  - a capability ORACLE becomes the human-ratified acceptance test for that capability (oracle.py: ratified_by required);
  - the HOOK is the non-built deliverable rq-035 condition 2 names, digest-pinned, placed by Ops before the bar runs.
C-S2 (grade) gets NO ratified bar or oracle: it is the proposed demonstration control (designated at freeze 2).
A changed file is a new content address: an unacted row is superseded; an acted one is never re-queued here.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
BASE = "spike/projections/ws3"
RATIFYING = {"accepted", "ratified", "decided"}
SOURCE = "sha256:109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614"

ITEMS = [
    {"file": BASE + "/bars/adjudicator.test.mjs", "kind": "module bar", "unit": "adjudicator", "capability": "C-S3",
     "title": "bar for tools/adjudicator/adjudicator.ts (C-S3; home per rq-074 = B) -- witnesses W-CS3-N/Δ1/Δ2, variants, K, A-DIM-01, tie, order, causes",
     "rests": "sr:L2:C-S3 (rq-046), sr:L2:R-S4 (rq-049), sr:L2:R-S5 (rq-050), sr:L3:adjudicator-interface (rq-066), sr:L3:ws3-field-types (rq-061), adj:ws3-module-homes = B (rq-074)",
     "fixtures": "the rater-C record and the C-S5 report (A9) are INLINE in this file, so this digest pins them",
     "amendedBy": "rq-075 (2026-10-18): import, header and title target tools/adjudicator/adjudicator.ts; V-S2 dropped from the determinism comment; the 18 assertions otherwise unchanged"},
    {"file": BASE + "/bars/ledger.test.mjs", "kind": "module bar", "unit": "ledger", "capability": "C-S7",
     "title": "bar for src/ledger.ts (C-S7) -- four-field hash, recursive canonical form, genesis, verifyChain (kind included), checkAppendOnly, appendEntry",
     "rests": "sr:L2:C-S7 (rq-047), sr:L2:LedgerEntry (rq-053), sr:L3:ledger-interface (rq-064), sr:L3:ws3-field-types (rq-061), rq-038 = A",
     "fixtures": "none; expected hashes and entries are computed in the file from the ratified encoding, never read from the module",
     "amendedBy": "rq-077 (2026-10-18), its intended note recorded verbatim in docs/decisions/2026-10-18-ws3-5-sitting-rq-077-note-and-duration.md (the act's own note is a copy of rq-075's): recursive canonicalization; appendEntry's entries built independently; whole JSONL lines"},
    {"file": BASE + "/acceptance/C-S3.test.mjs", "kind": "capability oracle", "unit": None, "capability": "C-S3",
     "title": "acceptance oracle for C-S3 adjudicate -- J-S1 step 3 end to end (the complete PRINTED report), and C-S3 determinism",
     "rests": "sr:L2:C-S3 (rq-046), sr:L3:adjudicator-interface (rq-066), adj:ws3-module-homes = B (rq-074)",
     "fixtures": "the rater-C record, inline; A and B are committed GradeRecord fixtures (this oracle does not prove grader isolation)",
     "amendedBy": "rq-069 (2026-10-18): V-S2 overclaim removed (V-S2 stays pending under diag:external-method-artifacts); purity snapshot before the first call, re-run from fresh clones; the complete PRINTED variant asserted; import from tools/adjudicator/"},
    {"file": BASE + "/acceptance/C-S7.test.mjs", "kind": "capability oracle", "unit": None, "capability": "C-S7",
     "title": "acceptance oracle for C-S7 register -- J-S1 step 4 + J-S4 step 3 (each event exact), and W-CS7-Δ1 through a REAL git commit: rewrite, deletion and read failures refused",
     "rests": "sr:L2:C-S7 (rq-047), sr:L2:LedgerEntry (rq-053), sr:L3:ledger-interface (rq-064), rq-035 = A with conditions",
     "fixtures": "none; PRECONDITION provisioned not detected: git, the non-built .githooks/ and (on POSIX) the wrapper's executable mode -- missing any FAILS, never skips",
     "amendedBy": "rq-070 (2026-10-18): seq/prev/kind/payload of both events, the persisted lines exactly, and the committed final entry; plus rq-072's coverage: a staged deletion and induced index and blob-read failures"},
    {"file": BASE + "/nonbuilt/.githooks/pre-commit", "kind": "non-built deliverable", "unit": None, "capability": "C-S7",
     "title": "the ledger hook wrapper (.githooks/pre-commit) -- runs check-ledger.mjs; holds no logic (rq-035 = A, condition 2); bytes unchanged, mode now 100755",
     "rests": "sr:L2:ledger (rq-056), rq-035 = A with conditions", "fixtures": "n/a",
     "amendedBy": "rq-071 (2026-10-18): the file accepted unchanged; its mode (100755), install path and core.hooksPath are bound by the delivery descriptor (nonbuilt/delivery.json), queued beside it"},
    {"file": BASE + "/nonbuilt/.githooks/check-ledger.mjs", "kind": "non-built deliverable", "unit": None, "capability": "C-S7",
     "title": "the hook's script (.githooks/check-ledger.mjs) -- Git/index plumbing only, fail-closed; the decision is the BUILT checkAppendOnly",
     "rests": "sr:L3:ledger-interface (rq-064), rq-035 = A with conditions", "fixtures": "n/a",
     "amendedBy": "rq-072 (2026-10-18): no catch-all (exit 2 on any git/index/blob failure); deletion and rename refused (H-LEDGER-01); -z parsing; staged blobs from the index; empty predecessor only for status A; malformed content fails closed"},
    {"file": BASE + "/nonbuilt/delivery.json", "kind": "non-built delivery descriptor", "unit": None, "capability": "C-S7",
     "title": "the non-built delivery record -- both hook files' digests, modes (pre-commit 100755), install paths, core.hooksPath, fail-not-skip",
     "rests": "rq-035 = A, condition 2; rq-071 (2026-10-18)", "fixtures": "n/a",
     "amendedBy": "new, per rq-071: 'the complete content-addressed deliverable record must change'"},
]


def file_digest(rel):
    return "sha256:" + hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


# A test title is a JavaScript STRING LITERAL, so it is parsed as one: either quote style, escapes resolved (IA Ops
# finding 2026-10-17, "the queue row publishes a truncated test title and would drop a double-quoted one" -- the old
# pattern `^test\('([^']+)'` stopped at an escaped apostrophe and matched no double-quoted title at all).
_TITLE = re.compile(r"""^test\(\s*(['"])((?:\\.|(?!\1)[^\\\n])*)\1""", re.M)
_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "v": "\v", "0": "\0"}


def _unescape(body):
    return re.sub(r"\\(.)", lambda m: _ESCAPES.get(m.group(1), m.group(1)), body)


def test_titles(rel, text=None):
    """Every top-level test(...) title, in order -> [str]. REFUSES when a declaration's title is not a plain string
    literal (e.g. a template literal), rather than silently publishing fewer duties than the file asserts."""
    text = (ROOT / rel).read_text(encoding="utf-8") if text is None else text
    titles = [_unescape(m.group(2)) for m in _TITLE.finditer(text)]
    declared = len(re.findall(r"^test\(", text, re.M))
    if declared != len(titles):
        raise SystemExit("%s declares %d test(...) but %d titles parse as string literals -- refusing to publish a short "
                         "list" % (rel, declared, len(titles)))
    return titles


def published_duties(rel):
    titles = test_titles(rel)
    return titles or "n/a (not a test file)", len(titles)


def rows_for(existing, now):
    n = max(int(r["id"].split("-")[1]) for r in existing) if existing else 0
    dead = {r.get("supersedes") for r in existing if r.get("supersedes")}
    out = []
    for it in ITEMS:
        live = [r for r in existing if r.get("artifact") == it["file"] and r["id"] not in dead]
        prior = live[-1] if live else None
        d = file_digest(it["file"])
        tests, count = published_duties(it["file"])
        # a row is current only if its BYTES and its PUBLISHED DUTIES both match: a corrected title list re-queues the
        # row at the same digest (the duty list is part of what ratification confers over)
        same_duties = prior and (prior.get("displayDuties") or {}).get("tests") == tests and prior.get("assertions") == count
        amended = prior and prior.get("actedAt") and prior.get("act") not in RATIFYING
        if prior and prior.get("artifactFileDigest") == d and same_duties and not amended:
            continue
        if prior and prior.get("actedAt") and not amended:
            raise SystemExit("%s (or its published duties) changed after %s was %s -- not re-queued here"
                             % (it["file"], prior["id"], prior.get("act")))
        # an AMEND confers nothing: the item is re-presented on a new row that supersedes it, even at unchanged bytes
        # (rq-071 accepted the wrapper's bytes unchanged and amended only its delivery record)
        n += 1
        titles = test_titles(it["file"])
        row = {
            "id": "rq-%03d" % n, "batch": "WS3-5", "queuedAt": now,
            "kind": "WS-3 %s -- ratification of a file at its content address" % it["kind"],
            "title": it["title"], "artifact": it["file"], "artifactFileDigest": d, "assertions": len(titles),
            "actRequested": "read the file (shown in full below); ratify if every test asserts only what the ratified records say, "
                            "or amend with what to change",
            "displayDuties": {
                "restsOn": it["rests"],
                "fixtures": it["fixtures"],
                "tests": titles or "n/a (not a test file)",
                "whatRatifyingDoes": {"module bar": "it becomes the ratified standard for unit %s (provisional: false); ratified_by "
                                                    "will carry this act so FX-CAP can read the chain from act to verdict" % it["unit"],
                                      "capability oracle": "it becomes the human-ratified acceptance test for %s" % it["capability"],
                                      "non-built deliverable": "it is placed by Ops in the build workspace before the bars run, "
                                                               "pinned at this digest; it never enters plan.json files",
                                      "non-built delivery descriptor": "it binds what a file digest cannot: each hook file's mode and "
                                                                       "install path, and core.hooksPath; Ops provisions exactly this, "
                                                                       "failing (never skipping) if any of it cannot be established"}[it["kind"]],
                "amendedBy": it["amendedBy"],
                "devEvidence": "Dev ran every WS-3 bar and oracle against a PRIVATE reference implementation (never committed -- the "
                               "factory builds from the spec), laid out per rq-074 = B: 35 of 35 pass; Ops' five survivors and the "
                               "six 2026-10-18 amendment targets (a mutating adjudicate, a PRINTED report with a stray key, kind "
                               "substituted on append, top-level-only canonical form, a missing final newline, the old catch-all "
                               "hook) each pass the previous file and fail this one by its named test. Dev's probe, not verification.",
                "facetBreakdown": "origin transformer(model-authored test) / grounding: the ratified records above / ratification unratified",
            },
            "queuedBy": "aro-dev-agent", "sourceDigest": SOURCE,
            "workstream": "WS-3 (Plan v1.1 s5; D-8 part 2b: bars and oracles)",
        }
        if prior:
            row["supersedes"] = prior["id"]
        out.append(row)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    text = QUEUE.read_text(encoding="utf-8")
    existing = [json.loads(l) for l in text.splitlines() if l.strip()]
    now = dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    new = rows_for(existing, now)
    if not new:
        print("nothing to queue: every WS-3 bar, oracle and hook file is queued at its current bytes")
        return 0
    lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new)
    if args.dry_run:
        sys.stdout.buffer.write(lines.encode("utf-8"))
        return 0
    with QUEUE.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(lines)
    for r in new:
        print("%s  %s  %s" % (r["id"], r["batch"], r["artifact"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
