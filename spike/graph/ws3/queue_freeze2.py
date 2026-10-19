"""Queue the freeze-2 architect act for ratification: the demonstration-control designation (Plan v1.1 s3, PF-OPS-2;
checklist 11.2), bound to its file's SHA-256, batch WS3-6.

    python spike/graph/ws3/queue_freeze2.py            # appends the row unless queued at the file's current bytes
    python spike/graph/ws3/queue_freeze2.py --dry-run

The FX-CAP assertions (spike/projections/ws3/freeze2/fx_cap.py) are Ops' freeze-2 instrument, stated as executable
checks; they are not queued here -- the designation is the act the plan assigns to the architect.
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
FILE = "spike/projections/ws3/freeze2/control-designation.json"
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
        "id": "rq-%03d" % n, "batch": "WS3-6", "queuedAt": now,
        "kind": "WS-3 freeze-2 act -- the demonstration-control designation, ratified at its content address",
        "title": "designate C-S2 (grade) the demonstration control: bar held provisional by design, expected built_unverified, "
                 "disposed by act after the demonstration (ratify its bar or retire the capability)",
        "artifact": FILE, "artifactFileDigest": d, "assertions": 0,
        "actRequested": "read the file (shown in full below); ratify to designate C-S2 the control at freeze 2, before results; "
                        "or amend (another capability, another rationale, another lifecycle)",
        "displayDuties": {
            "restsOn": "Plan v1.1 s3 'the demonstration control' (PF-OPS-2) and checklist 11.2; the accepted L2 "
                       "ws3.demonstrationControlCandidate; the A9 target act as restated 2026-10-17",
            "whatRatifyingDoes": "designates C-S2 as the demonstration CONTROL (disclosed, not debt) before the capability "
                                 "build; FX-CAP assertion (i) then requires it to read built_unverified, never VERIFIED",
            "lifecycle": "after the demonstration you dispose of it by a separate act (Plan v1.1 B6): ratify its bar, or retire the capability",
            "facetBreakdown": "origin transformer(model-drafted designation from the accepted L2 proposal) / ratification unratified",
        },
        "queuedBy": "aro-dev-agent", "sourceDigest": SOURCE,
        "workstream": "WS-3 (Plan v1.1 s5; Stage B freeze 2)",
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
        print("nothing to queue: the designation is queued at its current bytes")
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
