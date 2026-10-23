"""C1 self-test: a fixture dry run on synthetic prose (Plan v1.1 C1) -- the author's own planted cases, scored.

    python spike/transformer/selftest/dry_run.py -o <run-root> [--model sonnet]     # live: one claude -p per section
    python spike/transformer/selftest/dry_run.py --score <run-root>                  # re-score an existing run

A DRY RUN, NOT A MEASUREMENT. The cases are the transformer author's, in text the author wrote, so a pass says the
mechanism works end to end on prose built to exercise it -- nothing about real specifications. The real probe is C3-C6,
against OPS's sealed placements, which the author never sees.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import transform as t  # noqa: E402

ROOT = HERE.parents[2]
EXPECT = HERE / "expectations.json"


def _lines_of(fragment_ids, frags):
    return {int(frags[f]["display"]["lines"]) for f in fragment_ids if f in frags}


def score(run: Path) -> dict:
    exp = json.loads(EXPECT.read_text(encoding="utf-8"))
    graph = json.loads((run / "candidate.graph.jsonld").read_text(encoding="utf-8"))
    frags = {f["fragmentId"]: f for f in json.loads((run / "fragments.json").read_text(encoding="utf-8"))["fragments"]}
    assertions = [a for r in graph["records"] for a in r["assertions"]]
    by_line = {}
    for a in assertions:
        for line in _lines_of([g["fragment"] for g in a["groundedBy"] if g["role"] == "primary"], frags):
            by_line.setdefault(line, []).append(a)
    results = []
    for c in exp["cases"]:
        on = by_line.get(c["line"], [])
        if c["kind"] == "covered":
            ok, detail = bool(on), "%d assertion(s) grounded on line %d" % (len(on), c["line"])
        elif c["kind"] == "split":
            ok, detail = len(on) >= c["min"], "%d assertion(s) on line %d (need >= %d)" % (len(on), c["line"], c["min"])
        elif c["kind"] == "no-invention":
            hits = [a["statement"] for a in on if any(w in a["statement"].lower() for w in c["forbidden"])]
            ok, detail = not hits, "invented: %s" % hits if hits else "no forbidden term in %d assertion(s)" % len(on)
        elif c["kind"] == "not-normative":
            bad = [a["statement"] for a in on if a["role"] == "Normative" and a["force"] in ("obligation", "prohibition")]
            ok, detail = not bad, "normative from an example: %s" % bad if bad else "no obligation drawn from the example"
        else:
            ds = [d for d in graph["diagnostics"] if d["@type"] in c["types"] and c["line"] in _lines_of(d["evidence"], frags)]
            ok, detail = bool(ds), "%d matching diagnostic(s)" % len(ds)
        results.append({"id": c["id"], "kind": c["kind"], "ok": ok, "knownLimit": bool(c.get("knownLimit")),
                        "detail": detail})
    failed = [r for r in results if not r["ok"] and not r["knownLimit"]]
    return {"results": results, "failed": len(failed), "passed": sum(r["ok"] for r in results),
            "knownLimitsMissed": [r["id"] for r in results if not r["ok"] and r["knownLimit"]]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("-o", "--out")
    ap.add_argument("--score")
    ap.add_argument("--model", default="sonnet")
    args = ap.parse_args(argv)
    if args.out:
        src = ROOT / json.loads(EXPECT.read_text(encoding="utf-8"))["source"]
        digest = "sha256:" + hashlib.sha256(src.read_bytes()).hexdigest()
        result = t.transform(src, digest, "src:synthetic-c1-selftest", t.claude_cli(args.model), model_id=args.model)
        t.write_run(result, Path(args.out))
    run = Path(args.score or args.out)
    s = score(run)
    (run / "selftest-score.json").write_text(json.dumps(s, indent=2) + "\n", encoding="utf-8", newline="\n")
    for r in s["results"]:
        print("%-5s %-26s %s%s" % ("ok" if r["ok"] else "MISS", r["id"], r["detail"], "  (known limit)" if r["knownLimit"] else ""))
    print("passed %d of %d; failed %d (known limits missed: %s)"
          % (s["passed"], len(s["results"]), s["failed"], ", ".join(s["knownLimitsMissed"]) or "none"))
    return 1 if s["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
