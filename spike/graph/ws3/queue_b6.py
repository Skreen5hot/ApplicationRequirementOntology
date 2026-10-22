"""Queue the B6 architect act for ratification: the disposition of the demonstration control C-S2 (Plan v1.1 s3,
PF-OPS-2; task table B6), bound to its file's SHA-256, batch WS3-7. It follows the passing freeze-2 demonstration
(IA a4fd46e) and the designation rq-089, which promised this separate act.

    python spike/graph/ws3/queue_b6.py            # appends the row unless queued at the file's current bytes
    python spike/graph/ws3/queue_b6.py --dry-run
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
FILE = "spike/projections/ws3/freeze2/control-disposition.json"
SOURCE = "sha256:109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614"
RATIFYING = {"accepted", "ratified", "decided"}


def row_for(existing, now):
    d = "sha256:" + hashlib.sha256((ROOT / FILE).read_bytes()).hexdigest()
    dead = {r.get("supersedes") for r in existing if r.get("supersedes")}
    live = [r for r in existing if r.get("artifact") == FILE and r["id"] not in dead]
    prior = live[-1] if live else None
    if prior and prior.get("artifactFileDigest") == d and not (prior.get("actedAt") and prior.get("act") not in RATIFYING):
        return None
    if prior and prior.get("act") in RATIFYING:
        raise SystemExit("%s changed after %s was %s -- not re-queued here" % (FILE, prior["id"], prior["act"]))
    n = max(int(r["id"].split("-")[1]) for r in existing) + 1
    row = {
        "id": "rq-%03d" % n, "batch": "WS3-7", "queuedAt": now,
        "kind": "WS-3 B6 act -- the demonstration control's disposition, ratified at its content address",
        "title": "dispose of the C-S2 demonstration control: RETIRE the capability from the WS-3 target (reported in "
                 "the closeout as the disclosed control; nothing deleted, no score claimed)",
        "artifact": FILE, "artifactFileDigest": d, "assertions": 0,
        "actRequested": "read the file (shown in full below); ratify to retire C-S2 as the disposed control; or amend "
                        "to choose the other disposition the plan allows -- ratify its bar (which needs a spec-authored "
                        "bar AND acceptance oracle, each reviewed on its own act, then a re-run)",
        "displayDuties": {
            "restsOn": "Plan v1.1 s3 'the demonstration control' (PF-OPS-2) and task table B6; rq-089 (the designation, "
                       "which promised this act); the passing demonstration OPS-2026-10-22-freeze2-demonstration-passes.md "
                       "(IA a4fd46e, fx_cap.check == [])",
            "whatRatifyingDoes": "retires C-S2 (grade) from the WS-3 capability target for this phase; the Stage D "
                                 "closeout cites this act and reports C-S2 as the disclosed control, retired -- not debt, "
                                 "not a failure; its code and its provisional model bar stay as unratified artifacts",
            "lifecycle": "terminal for this phase: the control is disposed and never becomes an immortal provisional; "
                         "grading may return later as a new capability under a new freeze",
            "facetBreakdown": "origin transformer(model-drafted disposition from the demonstration record) / ratification unratified",
        },
        "queuedBy": "aro-dev-agent", "sourceDigest": SOURCE,
        "workstream": "WS-3 (Plan v1.1 s5; Stage B, B6)",
    }
    if prior:
        row["supersedes"] = prior["id"]
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    existing = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    row = row_for(existing, dt.datetime.now().astimezone().replace(microsecond=0).isoformat())
    if not row:
        print("nothing to queue: the disposition is queued at its current bytes")
        return 0
    line = json.dumps(row, ensure_ascii=False) + "\n"
    if args.dry_run:
        sys.stdout.buffer.write(line.encode("utf-8"))
        return 0
    with QUEUE.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)
    print("%s  %s  %s" % (row["id"], row["batch"], FILE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
