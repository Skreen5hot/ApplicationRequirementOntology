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
SOURCE = "sha256:109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614"

ITEMS = [
    {"file": BASE + "/bars/adjudicator.test.mjs", "kind": "module bar", "unit": "adjudicator", "capability": "C-S3",
     "title": "bar for src/adjudicator.ts (C-S3) -- witnesses W-CS3-N/Δ1/Δ2, variants, K, A-DIM-01, tie, order, causes",
     "rests": "sr:L2:C-S3 (rq-046), sr:L2:R-S4 (rq-049), sr:L2:R-S5 (rq-050), sr:L3:adjudicator-interface (rq-066), sr:L3:ws3-field-types (rq-061)",
     "fixtures": "the rater-C record and the C-S5 report (A9) are INLINE in this file, so this digest pins them"},
    {"file": BASE + "/bars/ledger.test.mjs", "kind": "module bar", "unit": "ledger", "capability": "C-S7",
     "title": "bar for src/ledger.ts (C-S7) -- four-field hash, genesis, verifyChain (kind included), checkAppendOnly, appendEntry",
     "rests": "sr:L2:C-S7 (rq-047), sr:L2:LedgerEntry (rq-053), sr:L3:ledger-interface (rq-064), sr:L3:ws3-field-types (rq-061), rq-038 = A",
     "fixtures": "none; expected hashes are computed in the file from the ratified encoding, never read from the module"},
    {"file": BASE + "/acceptance/C-S3.test.mjs", "kind": "capability oracle", "unit": None, "capability": "C-S3",
     "title": "acceptance oracle for C-S3 adjudicate -- J-S1 step 3 end to end, and V-S2 recomputability",
     "rests": "sr:L2:C-S3 (rq-046), sr:L3:adjudicator-interface (rq-066)",
     "fixtures": "the rater-C record, inline"},
    {"file": BASE + "/acceptance/C-S7.test.mjs", "kind": "capability oracle", "unit": None, "capability": "C-S7",
     "title": "acceptance oracle for C-S7 register -- J-S1 step 4 + J-S4 step 3, and W-CS7-Δ1 through a REAL git commit (rq-035 condition 3)",
     "rests": "sr:L2:C-S7 (rq-047), sr:L3:ledger-interface (rq-064), rq-035 = A with conditions",
     "fixtures": "none; PRECONDITION provisioned not detected: git and the non-built .githooks/ -- missing either FAILS, never skips"},
    {"file": BASE + "/nonbuilt/.githooks/pre-commit", "kind": "non-built deliverable", "unit": None, "capability": "C-S7",
     "title": "the ledger hook wrapper (.githooks/pre-commit) -- runs check-ledger.mjs; holds no logic (rq-035 = A, condition 2)",
     "rests": "sr:L2:ledger (rq-056), rq-035 = A with conditions", "fixtures": "n/a"},
    {"file": BASE + "/nonbuilt/.githooks/check-ledger.mjs", "kind": "non-built deliverable", "unit": None, "capability": "C-S7",
     "title": "the hook's script (.githooks/check-ledger.mjs) -- calls the BUILT checkAppendOnly on each staged ledger file",
     "rests": "sr:L3:ledger-interface (rq-064), rq-035 = A with conditions", "fixtures": "n/a"},
]


def file_digest(rel):
    return "sha256:" + hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def test_titles(rel):
    return re.findall(r"^test\('([^']+)'", (ROOT / rel).read_text(encoding="utf-8"), re.M)


def rows_for(existing, now):
    n = max(int(r["id"].split("-")[1]) for r in existing) if existing else 0
    dead = {r.get("supersedes") for r in existing if r.get("supersedes")}
    out = []
    for it in ITEMS:
        live = [r for r in existing if r.get("artifact") == it["file"] and r["id"] not in dead]
        prior = live[-1] if live else None
        d = file_digest(it["file"])
        if prior and prior.get("artifactFileDigest") == d:
            continue
        if prior and prior.get("actedAt"):
            raise SystemExit("%s changed after %s was acted on -- not re-queued here" % (it["file"], prior["id"]))
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
                                                               "pinned at this digest; it never enters plan.json files"}[it["kind"]],
                "devEvidence": "Dev ran every WS-3 bar and oracle against a PRIVATE reference implementation (never committed -- the "
                               "factory builds from the spec): 30 of 30 pass, and 6 named wrong implementations are each caught "
                               "(kind outside the hash, numeric ordering, unvalidated route, ties not knocked out, a partial line "
                               "admitted, the hook not provisioned). Dev's probe, not verification.",
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
