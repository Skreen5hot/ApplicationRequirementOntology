"""Source Fragments as Text Spans -- the lightest viable implementation of ARO v0.5.2 section 5.1.

A fragment is the grounding unit. Its identity is content-derived, per the identity formula
(ARO 5.1, D23): source digest + fragment kind + canonical locator + normalization version +
normalized-content hash. Identical repeated text cannot collide because the locator (a code-point
range in the normalized text) disambiguates within one immutable digest.

    python spike/graph/fragments.py --spans spike/graph/spans.json -o spike/graph/fragments.json
    python spike/graph/fragments.py --verify spike/graph/fragments.json      # lapse check (ARO 5.2)

Spans are addressed by LINE in the normalized text and guarded by a `startsWith` prefix, so a
source edit that shifts lines fails loudly here rather than silently grounding an assertion in
the wrong sentence. `--verify` recomputes every fragment's text hash against the source as it is
now; a mismatch is a LapsedGroundingDiagnostic in the making, reported and never repaired here.

The fragment record carries the span text for the ratification queue's display duty (fragment
text beside the assertion, ARO 9). That copy is display metadata; identity is the hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import unicodedata
from pathlib import Path

# THE SOURCE PATH IS A PARAMETER; THE SOURCE DIGEST IS NOT.
#
# The registered `doc` is an absolute path under one account and is ACL-denied to the Ops account that
# measures all three spike arms -- so fragment verification and re-projection could only be run by the party
# that authored the package, leaving one half of Arm B's founding-input check self-attested. Arm A's inputs
# are in-tree and Ops verified them independently (twice catching a real defect); the arms were not equal on
# that axis.
#
# This overrides only WHERE the bytes are read from. The digest comparison in `verify` is untouched, so an
# override pointed at anything other than the pinned source returns the same total lapse it returns today --
# the pin remains the authority and this cannot weaken it. The registered `doc` and `digest` are left exactly
# as minted, and the path reaches no projected output (`project.py` embeds `source.digest`, never the path),
# so projected bytes are unaffected.
_SOURCE_ENV = "ARO_SOURCE_DOC"


def source_doc(registered: str) -> Path:
    """The path to read the source bytes from -> Path. `ARO_SOURCE_DOC` wins when set and non-empty."""
    return Path(os.environ.get(_SOURCE_ENV) or registered)


NORMALIZATION_VERSION = "norm-spike-1"      # NFC; CRLF and CR -> LF; nothing else
ANCHOR_CODEPOINTS = 64


class Refused(SystemExit):
    """A span that does not say what its author claimed it says."""


def normalize(text: str) -> str:
    return unicodedata.normalize("NFC", text.replace("\r\n", "\n").replace("\r", "\n"))


def sha_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def doc_digest(path: Path) -> str:
    """The registered source digest is over the bytes as delivered, not the normalized text."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def line_range(norm: str, first: int, last: int) -> tuple[int, int]:
    lines = norm.split("\n")
    if not (1 <= first <= last <= len(lines)):
        raise Refused("lines %d-%d are outside the document (%d lines)" % (first, last, len(lines)))
    start = sum(len(l) + 1 for l in lines[:first - 1])
    end = sum(len(l) + 1 for l in lines[:last]) - 1
    return start, end


def fragment(doc: Path, norm: str, digest: str, spec: dict) -> dict:
    first = spec.get("line") or spec["lines"][0]
    last = spec.get("line") or spec["lines"][1]
    start, end = line_range(norm, first, last)
    text = norm[start:end]
    prefix = spec["startsWith"]
    if not text.startswith(prefix):
        raise Refused("span %r at line %d does not start with %r; it starts with %r"
                      % (spec["label"], first, prefix, text[:len(prefix) + 12]))
    text_hash = sha_text(text)
    identity = "|".join([digest, "text-span", "%d-%d" % (start, end), NORMALIZATION_VERSION, text_hash])
    return {
        "fragmentId": "sf:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24],
        "label": spec["label"],
        "kind": "text-span",
        "source": {"doc": doc.name, "digest": digest},
        "locator": {"codepointRange": [start, end]},
        "normalizationVersion": NORMALIZATION_VERSION,
        "textHash": text_hash,
        "anchors": {"before": sha_text(norm[max(0, start - ANCHOR_CODEPOINTS):start]),
                    "after": sha_text(norm[end:end + ANCHOR_CODEPOINTS])},
        "display": {"lines": ("%d" % first) if first == last else "%d-%d" % (first, last),
                    "section": spec.get("section")},
        "text": text,
    }


def extract(spans_path: Path) -> dict:
    spec = json.loads(spans_path.read_text(encoding="utf-8"))
    doc = Path(spec["doc"])
    if not doc.is_file():
        raise Refused("source %s is not a file; nothing can be registered" % doc)
    digest = doc_digest(doc)
    expected = spec.get("expectedDigest")
    if expected and expected != digest:
        raise Refused("source digest %s is not the registered %s; the source changed and every "
                      "fragment below would be minted against the wrong revision" % (digest, expected))
    norm = normalize(doc.read_text(encoding="utf-8"))
    fragments = [fragment(doc, norm, digest, s) for s in spec["spans"]]
    labels = [f["label"] for f in fragments]
    if len(set(labels)) != len(labels):
        raise Refused("duplicate span labels: %s" % sorted(l for l in labels if labels.count(l) > 1))
    return {"source": {"doc": str(doc), "digest": digest, "registeredAs": spec.get("registeredAs")},
            "normalizationVersion": NORMALIZATION_VERSION,
            "fragments": fragments}


def verify(fragments_path: Path) -> list[str]:
    """Every fragment's text hash, recomputed against the source now -> the lapsed ones."""
    data = json.loads(fragments_path.read_text(encoding="utf-8"))
    doc = source_doc(data["source"]["doc"])
    lapsed = []
    # UNREADABLE IS A LAPSE, NOT A CRASH (F5, Ops 2026-09-12). `is_file()` succeeds on an ACL-denied file --
    # stat is permitted, the read is not -- so `doc_digest` raised PermissionError instead of reporting the
    # total lapse this branch exists to report. With the path now parameterized, the unset case is exactly
    # the one an Ops account hits, so it must degrade legibly rather than traceback. A nonexistent path
    # already degraded (is_file() False); denied-but-present did not.
    #
    # I could not reproduce it from this account -- the coord paths read as absent here, not denied, so the
    # raising branch is unreachable for me. The guard is written to the mechanism Ops measured, and the
    # distinct wording is so the two causes are never confused in a log.
    try:
        if not doc.is_file():
            return ["source missing: every fragment lapses (ARO 5.2)"]
        current = doc_digest(doc)
    except OSError as exc:
        return ["source unreadable (%s): every fragment lapses (ARO 5.2)" % type(exc).__name__]
    if current != data["source"]["digest"]:
        return ["source digest changed: every fragment lapses (ARO 5.2)"]
    norm = normalize(doc.read_text(encoding="utf-8"))
    for f in data["fragments"]:
        start, end = f["locator"]["codepointRange"]
        if sha_text(norm[start:end]) != f["textHash"]:
            lapsed.append(f["fragmentId"] + " (" + f["label"] + ")")
    return lapsed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--spans")
    ap.add_argument("-o", "--out")
    ap.add_argument("--verify")
    args = ap.parse_args(argv)
    if args.verify:
        lapsed = verify(Path(args.verify))
        if lapsed:
            print("LAPSED: %d fragment(s) no longer match the source: %s" % (len(lapsed), lapsed))
            return 1
        print("every fragment still matches the source")
        return 0
    if not args.spans:
        ap.error("--spans or --verify is required")
    out = extract(Path(args.spans))
    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
        print("%d fragment(s) -> %s (source %s)" % (len(out["fragments"]), args.out, out["source"]["digest"][:23]))
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
