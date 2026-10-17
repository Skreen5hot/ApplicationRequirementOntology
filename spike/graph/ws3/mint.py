"""Mint WS-3's fragments under the registered source and link each to its predecessor -- reproducibly.

    python spike/graph/ws3/mint.py            # writes spike/graph/ws3/fragments.json
    python spike/graph/ws3/mint.py --check    # exit 1 unless a re-mint reproduces the file byte for byte

The 2026-10-17 migration (src:srs-spec 2428b115 -> src:srs-spec@2 109e1b50) was first done by a one-off script. IA
Ops (finding 2026-10-17) asked for it to be reproducible, so that a verifier can re-mint the set and compare it byte for
byte rather than trusting the file. That is this tool: `fragments.extract` over ws3/spans.json, then one `migratedFrom`
per fragment, matched to the predecessor set (fragments-2428b115.json) by span label. The `text` flag is COMPUTED
from the two textHashes, never asserted. ARO 5.1/5.2, D23: migration is a relationship between distinct fragments,
never an identity.

The source is read through `fragments.source_doc`, so the per-source override (ARO_SOURCE_DOC_109E1B50) and the global
ARO_SOURCE_DOC both work from an account that cannot read the registered path.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import fragments as F  # noqa: E402

SPANS = HERE / "spans.json"
OUT = HERE / "fragments.json"
PREDECESSOR = HERE / "fragments-2428b115.json"


def mint():
    new = F.extract(SPANS)
    old = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    by_label = {f["label"]: f for f in old["fragments"]}
    missing = sorted(f["label"] for f in new["fragments"] if f["label"] not in by_label)
    if missing:
        raise SystemExit("no predecessor for span label(s) %s -- a migration link is never invented" % missing)
    changed = []
    for f in new["fragments"]:
        o = by_label[f["label"]]
        same = o["textHash"] == f["textHash"]
        f["migratedFrom"] = {"fragment": o["fragmentId"], "digest": o["source"]["digest"],
                             "text": "unchanged" if same else "CHANGED"}
        if not same:
            changed.append(f["label"])
    new["migration"] = {"from": "spike/graph/ws3/fragments-2428b115.json",
                        "rule": "ARO 5.1/5.2, D23: a migratedFrom relationship between distinct fragments, never identity; matched by span label",
                        "changed": changed}
    return new


def render(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    text = render(mint())
    if args.check:
        ok = OUT.read_text(encoding="utf-8") == text
        print("ws3/fragments.json %s a re-mint" % ("matches" if ok else "DIFFERS from"), file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 1
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print("minted %d fragment(s) with migratedFrom -> %s" % (text.count('"fragmentId"'), OUT.relative_to(HERE.parents[2])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
