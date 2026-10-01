# SPDX-License-Identifier: Apache-2.0
"""The act tool -- the operator's one command for ratification sittings (Plan v1.1 Stage A, A5).

    python tools/act.py list   [--json]                      # pending items, oldest first (read-only)
    python tools/act.py show   ID [--json]                   # one item with its display duties (read-only)
    python tools/act.py act    ID VERB --actor NAME [--decision X] [--sitting-start ISO] [--note TEXT] [--json]

VERB is one of: accept | ratify | decide | amend | diagnostic.

What an act IS, and what this tool refuses (ARO 9; SPIKE.md 4; D23):

- an act is performed by a named human. An empty actor, or an actor naming an agent, is REFUSED; the
  measurement is void otherwise (the same list `spike/projections/project.py` and `rate.py` enforce);
- an act binds to a content address. The record's current digest is recomputed with the projector's
  own rule (`layout_rule.digest`, or the artifact file's SHA-256 for file-addressed items) and must equal
  the digest the item was queued at; a changed record is a new content address and needs a new item;
- an item already acted on, or superseded, cannot be acted on again;
- `decide` requires `--decision` and the letter must be one of the item's options when it lists them.

`accept`, `ratify` and `decide` are the ratifying verbs (the projector's RATIFYING_ACTS). `amend` records
that the operator changed a value -- the record must be re-queued at its new address, so an amend confers
nothing. `diagnostic` records that the operator opened a diagnostic instead of acting.

Each act writes `actedAt` (now, with offset), `act`, `actor`, `sittingStart` (if given), `decision`,
`actNote` and `actDigest` (the digest the act bound to) into its row. Every other line of the queue is
written back byte-for-byte.

Exit codes: 0 done; 1 refused (the act or query is not permitted -- the message says why); 2 usage or I/O.
`--json` prints one JSON object on stdout for any command, including refusals.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

ROOT_DEFAULT = Path(__file__).resolve().parents[1]
QUEUE_REL = Path("spike") / "measurements" / "ratification-queue.jsonl"
AGENT_ACTORS = {"agent", "dev-agent", "assistant", "claude", "model", "transformer",
                "aro-dev-agent", "ia-dev", "coord-j", "ops"}
VERBS = {"accept": "accepted", "ratify": "ratified", "decide": "decided",
         "amend": "amended", "diagnostic": "diagnostic-opened"}
RATIFYING = {"accepted", "ratified", "decided"}


class Refused(Exception):
    code = 1


class Usage(Exception):
    code = 2


def canonical(obj) -> bytes:
    """The projector's serialisation (spike/graph/rules/layout_rule.py), restated so this tool has no
    import-time dependency on the spike tree; a pin checks the two agree on every live queue row."""
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def digest(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def _find(obj, record_id):
    if isinstance(obj, dict):
        if obj.get("@id") == record_id:
            return obj
        for v in obj.values():
            hit = _find(v, record_id)
            if hit is not None:
                return hit
    elif isinstance(obj, list):
        for v in obj:
            hit = _find(v, record_id)
            if hit is not None:
                return hit
    return None


class Queue:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / QUEUE_REL
        if not self.path.is_file():
            raise Usage("no ratification queue at %s" % self.path)
        self.lines = self.path.read_text(encoding="utf-8").splitlines(keepends=True)
        self.rows = []
        for n, line in enumerate(self.lines):
            if line.strip():
                try:
                    self.rows.append((n, json.loads(line)))
                except ValueError as e:
                    raise Usage("%s line %d is not JSON: %s" % (self.path.name, n + 1, e))

    def superseded(self) -> set:
        s = {r.get("supersedes") for _, r in self.rows if r.get("supersedes")}
        return s | {r["id"] for _, r in self.rows if r.get("supersededBy")}

    def get(self, item_id):
        for n, r in self.rows:
            if r.get("id") == item_id:
                return n, r
        raise Refused("no queue item %r" % item_id)

    def pending(self):
        dead = self.superseded()
        rows = [r for _, r in self.rows if not r.get("actedAt") and r.get("id") not in dead]
        return sorted(rows, key=lambda r: (r.get("queuedAt") or "", r.get("id") or ""))

    def current_digest(self, row):
        """-> (kind, digest now) for the item's content address, or raise Refused if it cannot be read."""
        art = row.get("artifact")
        if not art:
            raise Refused("%s names no artifact; nothing to bind the act to" % row.get("id"))
        path = self.root / art
        if not path.is_file():
            raise Refused("%s: artifact %s is missing" % (row.get("id"), art))
        if row.get("recordDigest"):
            rec = _find(json.loads(path.read_text(encoding="utf-8")), row.get("record"))
            if rec is None:
                raise Refused("%s: record %s is not in %s" % (row.get("id"), row.get("record"), art))
            return "record", digest(rec)
        if row.get("artifactFileDigest"):
            return "file", "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        raise Refused("%s carries no content address (recordDigest / artifactFileDigest)" % row.get("id"))

    def write_row(self, line_no, row):
        self.lines[line_no] = json.dumps(row, ensure_ascii=False) + "\n"
        tmp = self.path.with_suffix(".jsonl.tmp")
        tmp.write_text("".join(self.lines), encoding="utf-8", newline="")
        tmp.replace(self.path)


def act(q: Queue, item_id, verb, actor, decision=None, sitting_start=None, note=None, now=None):
    if verb not in VERBS:
        raise Usage("verb must be one of %s" % ", ".join(sorted(VERBS)))
    who = (actor or "").strip()
    if not who:
        raise Refused("an act needs a named human actor; an act nobody performed confers nothing")
    if who.lower() in AGENT_ACTORS:
        raise Refused("actor %r is an agent: an agent never performs, batches or simulates an act "
                      "(SPIKE.md 4; the measurement would be void)" % who)
    line_no, row = q.get(item_id)
    if item_id in q.superseded():
        raise Refused("%s is superseded; act on the item that replaced it" % item_id)
    if row.get("actedAt"):
        raise Refused("%s was already acted on (%s by %s at %s); a changed record is a new item"
                      % (item_id, row.get("act"), row.get("actor"), row.get("actedAt")))
    kind, now_digest = q.current_digest(row)
    queued_at = row.get("recordDigest") or row.get("artifactFileDigest")
    if now_digest != queued_at:
        raise Refused("%s: the %s changed since it was queued (queued %s, now %s); an act binds to a content "
                      "address -- re-queue the record at its new address" % (item_id, kind, queued_at, now_digest))
    mapped = VERBS[verb]
    if mapped == "decided":
        if not decision:
            raise Refused("decide needs --decision")
        opts = [str(o).split(":", 1)[0].strip() for o in row.get("options") or []]
        if opts and decision not in opts:
            raise Refused("decision %r is not one of this item's options %s" % (decision, opts))
    elif decision:
        raise Refused("--decision is only meaningful with decide")
    stamp = (now or dt.datetime.now().astimezone()).isoformat(timespec="seconds")
    row.update({"actedAt": stamp, "act": mapped, "actor": who, "actDigest": now_digest})
    if sitting_start:
        row["sittingStart"] = sitting_start
    if decision:
        row["decision"] = decision
    if note:
        row["actNote"] = note
    q.write_row(line_no, row)
    return {"id": item_id, "act": mapped, "actor": who, "actedAt": stamp, "actDigest": now_digest,
            "confers": mapped in RATIFYING, "decision": decision}


def _fragment_texts(q):
    """fragment id -> (line, text), from every item's display duties: L3 items cite the same source passages
    the L2 items display, so one index serves both."""
    out = {}
    for _, r in q.rows:
        for f in (r.get("displayDuties") or {}).get("fragmentTextBesideAssertions") or []:
            if isinstance(f, dict) and f.get("fragment"):
                out[f["fragment"]] = (f.get("line"), f.get("text") or "")
    return out


def _wrap(text, indent, width=100):
    import textwrap
    return textwrap.fill(" ".join(str(text).split()), width=width, initial_indent=indent,
                         subsequent_indent=" " * len(indent)) if text else indent + "(empty)"


def _value(v):
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def render_show(q, row):
    """The item as the operator must see it: what is being asked, then each STATEMENT with the source passages
    it cites directly beneath it (the display duty 'review every cited span beside its assertion'), then the
    flags. `--json` keeps the raw row."""
    frags = _fragment_texts(q)
    L = ["%s  [%s]  %s" % (row.get("id"), row.get("batch") or "", row.get("title") or row.get("kind") or ""),
         _wrap(row.get("kind"), "  kind:   "),
         _wrap(row.get("actRequested"), "  asked:  "), ""]
    rec = None
    if row.get("record") and row.get("artifact") and (q.root / row["artifact"]).is_file():
        rec = _find(json.loads((q.root / row["artifact"]).read_text(encoding="utf-8")), row["record"])
    for n, a in enumerate((rec or {}).get("assertions") or [], 1):
        if a.get("statement"):
            L.append(_wrap(a["statement"], "  %d. " % n))
            for fld in a.get("fields") or []:
                L.append(_wrap("%s%s%s" % (fld.get("name"), "  e.g. " + ", ".join(_value(x) for x in fld.get("examples") or []) if fld.get("examples") else "",
                                           "  (" + fld["presence"] + ")" if fld.get("presence") else ""), "       - field "))
            cites = [(g.get("fragment"), g.get("role"), g.get("why")) for g in a.get("groundedBy") or []]
            head = "     cites:"
        else:
            proposed = a.get("proposed") or {}
            listed = {k: v for k, v in proposed.items()
                      if isinstance(v, list) and v and all(isinstance(x, dict) and x.get("name") for x in v)}
            flat = {k: v for k, v in proposed.items() if k not in listed}
            L.append(_wrap("; ".join("%s = %s" % (k, _value(v)) for k, v in flat.items()) or "(values below)",
                           "  %d. %s: " % (n, a.get("@id"))))
            for key, items in listed.items():      # e.g. field lists: one line each, so each value can be reviewed
                L.append("       %s:" % key)
                for x in items:
                    extra = ", ".join("%s %s" % (k, _value(v)) for k, v in x.items() if k not in ("name", "type", "note"))
                    L.append(_wrap("%s: %s%s%s" % (x["name"], x.get("type") or "(untyped)", "  [" + extra + "]" if extra else "",
                                                   "  -- " + x["note"] if x.get("note") else ""), "         - "))
            cites = [(c.get("cite"), "rationale", c.get("why") or c.get("note")) for c in a.get("rationaleSource") or []]
            head = "     rationale (not grounding):"
        L.append(head)
        for ref, role, why in cites:
            if ref in frags:
                line, text = frags[ref]
                L.append(_wrap(text, "       [line %s, %s] " % (line, role)))
            else:
                L.append("       [%s] %s" % (role, ref))
            if why:
                L.append(_wrap(why, "         why: "))
        L.append("")
    if rec is not None and rec.get("options"):
        for key in ("conflict", "theSourceSays", "thePlanSays"):
            if rec.get(key):
                L.append(_wrap(_value(rec[key]), "  %s: " % key))
        L.append("  options:")
        for o in rec["options"]:
            L.append(_wrap(o.get("label"), "    %s  " % o.get("id")))
            if o.get("content"):
                L.append(_wrap(o["content"], "        does: "))
            if o.get("consequenceForTheSpike"):
                L.append(_wrap(o["consequenceForTheSpike"], "        consequence: "))
        L.append("")
    if rec is None and row.get("record"):
        L.append("  (record %s not found in %s)" % (row["record"], row.get("artifact")))
    dd = row.get("displayDuties") or {}
    for key, val in dd.items():
        if key != "fragmentTextBesideAssertions" or isinstance(val, str):
            L.append(_wrap(_value(val), "  %s: " % key))
    L.append(_wrap(row.get("recordDigest") or row.get("artifactFileDigest"), "  bound to: "))
    if row.get("actedAt"):
        L.append("  ACTED: %s by %s at %s" % (row.get("act"), row.get("actor"), row.get("actedAt")))
    return "\n".join(L)


def _summary(row):
    return {k: row.get(k) for k in ("id", "batch", "kind", "record", "title", "queuedAt", "assertions",
                                    "options", "actRequested")}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="act.py", description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(ROOT_DEFAULT), help="repository root (default: this repository)")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("id")
    a = sub.add_parser("act"); a.add_argument("id"); a.add_argument("verb")
    a.add_argument("--actor", required=True); a.add_argument("--decision")
    a.add_argument("--sitting-start", dest="sitting_start"); a.add_argument("--note")
    for p in sub.choices.values():
        p.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    for stream in (sys.stdout, sys.stderr):      # a Windows console is cp1252; titles carry arrows and dashes
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    try:
        args = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    try:
        q = Queue(Path(args.root))
        if args.cmd == "list":
            out = {"pending": [_summary(r) for r in q.pending()]}
            text = "\n".join("%-7s %-4s %s  %s" % (r["id"], r.get("batch") or "", r.get("queuedAt") or "",
                                                    r.get("title") or r.get("kind") or "")
                             for r in q.pending()) or "(no pending items)"
        elif args.cmd == "show":
            _, row = q.get(args.id)
            out = {"item": row}
            text = render_show(q, row)
        else:
            out = act(q, args.id, args.verb, args.actor, args.decision, args.sitting_start, args.note)
            text = "%s %s by %s at %s (bound to %s)%s" % (out["id"], out["act"], out["actor"], out["actedAt"],
                                                         out["actDigest"], "" if out["confers"] else " -- confers nothing")
        print(json.dumps(out) if args.json else text)   # --json is ASCII-safe on any console
        return 0
    except (Refused, Usage) as e:
        if getattr(args, "json", False):
            print(json.dumps({"refused" if e.code == 1 else "error": str(e)}))
        else:
            print(("REFUSED: " if e.code == 1 else "ERROR: ") + str(e), file=sys.stderr)
        return e.code


if __name__ == "__main__":
    raise SystemExit(main())
