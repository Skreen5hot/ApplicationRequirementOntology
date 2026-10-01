"""Append the WS-3 L2 records to the ratification queue -- one row per Specification Record (Amendment 2 i: the
architect reviews 100% of spans, beside the assertions they ground).

    python spike/graph/ws3/queue_l2.py            # appends rows for records not yet queued; prints what it did
    python spike/graph/ws3/queue_l2.py --dry-run  # prints the rows without writing

Rows carry the same shape as rq-003..rq-007 and the content address tools/act.py recomputes (`recordDigest`, the
canonical serialisation of the record). The script refuses to queue a record twice, so re-running it is a no-op.
Batches are sized to GP-E (Plan v1.1 s7: sittings of at most 2 h, ~11 acts): WS3-1 holds the capabilities, rules and
records; WS3-2 the components and seams (the L3 closures join WS3-2 when they are authored).
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
GRAPH_REL = "spike/graph/l2/srs-ws3.graph.jsonld"

BATCH = {
    "sr:L2:C-S2": "WS3-1", "sr:L2:C-S3": "WS3-1", "sr:L2:C-S7": "WS3-1",
    "sr:L2:R-S1": "WS3-1", "sr:L2:R-S4": "WS3-1", "sr:L2:R-S5": "WS3-1", "sr:L2:R-S6": "WS3-1",
    "sr:L2:GradeRecord": "WS3-1", "sr:L2:LedgerEntry": "WS3-1",
    "sr:L2:grader-runner": "WS3-2", "sr:L2:adjudicator": "WS3-2", "sr:L2:ledger": "WS3-2",
    "sr:L2:S-S2": "WS3-2", "sr:L2:S-S3": "WS3-2", "sr:L2:S-S6": "WS3-2",
}


def digest(obj) -> str:
    """tools/act.py's canonical(): sorted keys, compact separators, UTF-8, trailing newline."""
    return "sha256:" + hashlib.sha256(
        (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")).hexdigest()


def rows_for(graph, fragments, existing, now):
    by_id = {f["fragmentId"]: f for f in fragments}
    diag_ids = {d["@id"] for d in graph["diagnostics"]}
    n = max(int(r["id"].split("-")[1]) for r in existing) if existing else 0
    dead = {r.get("supersedes") for r in existing if r.get("supersedes")}
    live = {r.get("record"): r for r in existing if r.get("id") not in dead}
    region = graph["ws3"]["target"]["regionLines"]
    beyond = {b["assertion"]: b for b in graph["ws3"].get("beyondRegion", [])}
    out = []
    for rec in graph["records"]:
        prior = live.get(rec["@id"])
        if prior and prior.get("recordDigest") == digest(rec):
            continue
        if prior and prior.get("actedAt"):
            raise SystemExit("%s changed after %s was acted on -- an acted record is not re-queued by this script"
                             % (rec["@id"], prior["id"]))
        n += 1
        seen, texts = set(), []
        for a in rec["assertions"]:
            for c in a["groundedBy"]:
                if c["fragment"] not in seen:
                    seen.add(c["fragment"])
                    f = by_id[c["fragment"]]
                    texts.append({"fragment": c["fragment"], "line": f["display"]["lines"], "text": f["text"]})
        flags = [a[k] for a in rec["assertions"] for k in ("classificationNote", "scopeNote", "absence") if a.get(k)]
        flags += ["see %s" % a["diagnostic"] for a in rec["assertions"] if a.get("diagnostic") in diag_ids]
        flags += ["%s's primary span is line %d, beyond the A9 act's region (%s) -- accepting it needs the act's region "
                  "amended, or drop the clause" % (a["@id"], beyond[a["@id"]]["line"],
                                                   ", ".join("%d–%d" % tuple(x) for x in region))
                  for a in rec["assertions"] if a["@id"] in beyond]
        row_extra = {"supersedes": prior["id"]} if prior else {}
        out.append({
            "id": "rq-%03d" % n,
            "batch": BATCH[rec["@id"]],
            "queuedAt": now,
            "kind": "L2 Specification Record -- acceptance (Amendment 2 i: 100% span review)",
            "record": rec["@id"],
            "title": rec["title"],
            "artifact": GRAPH_REL,
            "recordDigest": digest(rec),
            "assertions": len(rec["assertions"]),
            "actRequested": "review every cited span beside its assertion; accept, amend, or open a diagnostic",
            "displayDuties": {
                "fragmentTextBesideAssertions": texts,
                "facetBreakdown": "origin transformer(hand-authored) / grounding present (%d fragment(s)) / ratification unratified -> not AUTHORITATIVE" % len(texts),
                "standaloneFlag": False,
                "expiryFlag": "n/a (L2)",
                "vacuityClassFlags": flags,
            },
            "queuedBy": "aro-dev-agent",
            "workstream": "WS-3 (Plan v1.1 s5; target: docs/decisions/2026-10-01-a9-ws3-target-naming-act.md)",
            **row_extra,
        })
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    graph = json.loads((ROOT / GRAPH_REL).read_text(encoding="utf-8"))
    fragments = json.loads((HERE / "fragments.json").read_text(encoding="utf-8"))["fragments"]
    text = QUEUE.read_text(encoding="utf-8")
    existing = [json.loads(l) for l in text.splitlines() if l.strip()]
    now = dt.datetime.now().astimezone().replace(microsecond=0).isoformat()
    new = rows_for(graph, fragments, existing, now)
    if not new:
        print("nothing to queue: every WS-3 L2 record is already queued")
        return 0
    lines = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in new)
    if args.dry_run:
        sys.stdout.write(lines)
        return 0
    with QUEUE.open("a", encoding="utf-8", newline="\n") as fh:
        if text and not text.endswith("\n"):
            fh.write("\n")
        fh.write(lines)
    for r in new:
        print("%s  %-6s %-24s %d assertion(s), %d span(s)" % (r["id"], r["batch"], r["record"], r["assertions"],
                                                             len(r["displayDuties"]["fragmentTextBesideAssertions"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
