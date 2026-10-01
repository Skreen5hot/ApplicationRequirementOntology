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


RATIFYING = {"accepted", "ratified", "decided"}
ADJ = {
    "adj:ledger-hooks-repo-home": {
        "title": "ledger repo home: the source says ledger/ + .githooks/; the factory builds one TypeScript module per unit",
        "beside": "the S5.ledger row displayed verbatim beside the toolchain fact", "facets": "L2 candidate vs. toolchain fact"},
    "adj:ledger-hash-kind": {
        "title": "the ledger hash leaves kind out (W-CS7-N) yet chain verification must catch any rewrite (W-CS7-Δ1): A, B or C",
        "beside": "W-CS7-N and W-CS7-Δ1 displayed verbatim, side by side", "facets": "two accepted L2 clauses in conflict"},
}


def _prior(existing, record_id):
    """The live row for a record (not superseded), or None."""
    dead = {r.get("supersedes") for r in existing if r.get("supersedes")}
    live = [r for r in existing if r.get("record") == record_id and r["id"] not in dead]
    return live[-1] if live else None


def rows_for(graph, existing, now):
    """New rows for records/adjudications not yet queued, and SUPERSEDING rows for ones whose bytes changed after
    an amend or a diagnostic (the designed path: an amend confers nothing and the record is re-queued at its new
    address). A record already accepted, ratified or decided whose bytes changed is REFUSED, never re-queued: that
    would silently replace a conferred value."""
    from build_l3 import L2, blocked_assertions
    blocked = blocked_assertions(json.loads(L2.read_text(encoding="utf-8")))
    n = max(int(r["id"].split("-")[1]) for r in existing) if existing else 0
    out = []

    def pending(item):
        prior = _prior(existing, item["@id"])
        if prior and prior.get("recordDigest") == digest(item):
            return None, False
        if prior and prior.get("act") in RATIFYING:
            raise SystemExit("%s changed after %s was %s -- refusing to re-queue a conferred item"
                             % (item["@id"], prior["id"], prior["act"]))
        return prior, True

    # adjudications first: an open adjudication is decided before the bundles that await it
    for adj in graph["adjudications"]:
        prior, due = pending(adj)
        if not due:
            continue
        n += 1
        meta = ADJ[adj["@id"]]
        row = {
            "id": "rq-%03d" % n, "batch": "WS3-3", "queuedAt": now,
            "kind": "Adjudication -- its own item, not a candidate (Amendment 2 ii)",
            "record": adj["@id"], "title": meta["title"], "artifact": ART, "recordDigest": digest(adj), "assertions": 0,
            "options": ["%s: %s" % (o["id"], o["label"]) for o in adj["options"]],
            "actRequested": "decide %s (record the decision letter on the act); read each option's consequence" % ", ".join(o["id"] for o in adj["options"]),
            "displayDuties": {"fragmentTextBesideAssertions": meta["beside"], "facetBreakdown": meta["facets"],
                              "standaloneFlag": "n/a", "expiryFlag": "n/a",
                              "vacuityClassFlags": ["no option is recommended by the dev agent"]},
            "queuedBy": "aro-dev-agent", "workstream": WORKSTREAM,
        }
        if prior:
            row["supersedes"] = prior["id"]
        out.append(row)
    for rec in graph["records"]:
        prior, due = pending(rec)
        if not due:
            continue
        n += 1
        labels = sorted({c.get("label", c["cite"]) for a in rec["assertions"] for c in a["rationaleSource"]})
        flags = ["depends on %s, which is %s -- confer this bundle only after that is settled" % (x, blocked[x])
                 for x in rec.get("blockedDependencies", [])]
        if rec.get("awaits"):
            flags.append("awaits " + rec["awaits"])
        flags += ["rebuilt from the architect's %s at %s: \"%s\"" % (a["act"], a["item"], a["note"])
                  for a in rec.get("amendmentNotes", [])]
        row = {
            "id": "rq-%03d" % n, "batch": "WS3-3", "queuedAt": now,
            "kind": "L3 Specification Record -- closure bundle (Amendment 2 ii: values conferred by the architect from labeled candidates)",
            "record": rec["@id"], "title": rec["title"], "artifact": ART, "recordDigest": digest(rec),
            "assertions": len(rec["assertions"]), "closes": rec["closes"], "dependsOn": rec["dependsOn"],
            "actRequested": "confirm each value matches what you conferred (each closure says how it was conferred), then ratify; or amend again",
            "displayDuties": {
                "fragmentTextBesideAssertions": "cited as rationale and displayed as such -- none grounds: " + ", ".join(labels),
                "facetBreakdown": "origin transformer(model-proposed, rebuilt from the architect's amend) / grounding absent / ratification unratified",
                "standaloneFlag": rec["standalone"],
                "expiryFlag": "n/a (dependent closure; lapses with its declared dependencies)",
                "vacuityClassFlags": flags,
                "whatRatifyingDoes": rec["displayDuties"]["whatRatifyingDoes"],
            },
            "queuedBy": "aro-dev-agent", "workstream": WORKSTREAM,
        }
        if prior:
            row["supersedes"] = prior["id"]
        out.append(row)
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
        sys.stdout.buffer.write(lines.encode("utf-8"))   # the rows carry non-cp1252 text
        return 0
    with QUEUE.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(lines)
    for r in new:
        print("%s  %-6s %s" % (r["id"], r["batch"], r["record"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
