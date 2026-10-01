"""Append the WS-3 L3 closure bundles and adjudications to the ratification queue, into batch WS3-2.

    python spike/graph/ws3/queue_l3.py            # appends rows for records not yet queued
    python spike/graph/ws3/queue_l3.py --dry-run

Same row shapes as rq-008 (closure bundle) and rq-011 (adjudication). Refuses to queue a record twice. The L3 rows
are queued AFTER the WS3-2 L2 rows, so the components and seams they close over are reviewed first in the sitting.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from queue_l2 import QUEUE, digest  # noqa: E402  -- one canonical digest for every WS-3 row

ROOT = HERE.parents[2]
ART = "spike/graph/l3/srs-ws3.design.candidates.jsonld"
WORKSTREAM = "WS-3 (Plan v1.1 s5; target: docs/decisions/2026-10-01-a9-ws3-target-naming-act.md)"


def rows_for(graph, existing, now):
    n = max(int(r["id"].split("-")[1]) for r in existing) if existing else 0
    queued = {r.get("record") for r in existing}
    out = []
    for rec in graph["records"]:
        if rec["@id"] in queued:
            continue
        n += 1
        labels = sorted({c.get("label", c["cite"]) for a in rec["assertions"] for c in a["rationaleSource"]})
        out.append({
            "id": "rq-%03d" % n, "batch": "WS3-2", "queuedAt": now,
            "kind": "L3 Specification Record -- closure bundle (Amendment 2 ii: values conferred by the architect from labeled candidates)",
            "record": rec["@id"], "title": rec["title"], "artifact": ART, "recordDigest": digest(rec),
            "assertions": len(rec["assertions"]), "closes": rec["closes"], "dependsOn": rec["dependsOn"],
            "actRequested": "confer or amend each proposed value, then ratify the record; an amended value is new content and a new content address",
            "displayDuties": {
                "fragmentTextBesideAssertions": "cited as rationale and displayed as such -- none grounds: " + ", ".join(labels),
                "facetBreakdown": "origin transformer(model-proposed) / grounding absent / ratification unratified",
                "standaloneFlag": rec["standalone"],
                "expiryFlag": "n/a (dependent closure; lapses with its declared dependencies)",
                "vacuityClassFlags": [],
                "whatRatifyingDoes": rec["displayDuties"]["whatRatifyingDoes"],
            },
            "queuedBy": "aro-dev-agent", "workstream": WORKSTREAM,
        })
    for adj in graph["adjudications"]:
        if adj["@id"] in queued:
            continue
        n += 1
        out.append({
            "id": "rq-%03d" % n, "batch": "WS3-2", "queuedAt": now,
            "kind": "Adjudication -- its own item, not a candidate (Amendment 2 ii)",
            "record": adj["@id"],
            "title": "ledger repo home: the source says ledger/ + .githooks/; the factory builds one TypeScript module per unit",
            "artifact": ART, "recordDigest": digest(adj), "assertions": 0,
            "options": ["%s: %s" % (o["id"], o["label"]) for o in adj["options"]],
            "actRequested": "decide A, B or C (record the decision letter on the act); see each option's consequence for C-S7's bar",
            "displayDuties": {
                "fragmentTextBesideAssertions": "the S5.ledger row displayed verbatim beside the toolchain fact",
                "facetBreakdown": "L2 candidate vs. toolchain fact",
                "standaloneFlag": "n/a", "expiryFlag": "n/a",
                "vacuityClassFlags": ["no option is recommended by the dev agent"],
            },
            "queuedBy": "aro-dev-agent", "workstream": WORKSTREAM,
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    graph = json.loads((ROOT / ART).read_text(encoding="utf-8"))
    text = QUEUE.read_text(encoding="utf-8")
    existing = [json.loads(l) for l in text.splitlines() if l.strip()]
    now = dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    new = rows_for(graph, existing, now)
    if not new:
        print("nothing to queue: every WS-3 L3 record and adjudication is already queued")
        return 0
    lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new)
    if args.dry_run:
        sys.stdout.write(lines)
        return 0
    with QUEUE.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(lines)
    for r in new:
        print("%s  %-6s %s" % (r["id"], r["batch"], r["record"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
