"""What an L3 closure says about how it was conferred, and what a diagnostic says about its status, are checked
against the acts -- never held by one literal path (IA Ops finding 2026-10-17, "the conferred label and the diagnostic
status are each held by one literal path").

Conferral: every claim a `conferred` label makes about an act is checked against THAT act's bound version of the
same record, found in git history by its recordDigest (never reconstructed, never the queue row's current bind):
  - "as proposed (rq-N" / "accepted as presented at rq-N" / "(rq-N: item k accepted as presented"  ->  byte-equal
  - "amended at rq-N [... and rq-M]"                                                              ->  different
Diagnostics: every status is derived at build; a flipped status, or a flipped `blocking`, goes red here."""
import copy
import hashlib
import json
import re
import subprocess
from functools import lru_cache
from pathlib import Path

import pytest

from conftest import load_tool

ROOT = Path(__file__).resolve().parents[1]
L2 = ROOT / "spike" / "graph" / "l2" / "srs-ws3.graph.jsonld"
L3 = ROOT / "spike" / "graph" / "l3" / "srs-ws3.design.candidates.jsonld"
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
b2 = load_tool("ws3_build_l2_conferral", "spike/graph/ws3/build_l2.py")

PRESENTED = [re.compile(r"^as proposed \((rq-\d+)"), re.compile(r"accepted as presented at (rq-\d+)"),
             re.compile(r"\((rq-\d+): item \d+ accepted as presented")]
AMENDED_CLAUSE = re.compile(r"amended at (rq-\d+[^;:]*)")


def claims(label):
    """-> [(act, 'presented' | 'amended')] that a conferred label makes. Partial phrases ('the routing rule itself as
    proposed at ...', 'checkAppendOnly ... as proposed') make no whole-closure claim and are not read as one."""
    out = []
    for rx in PRESENTED:
        out += [(m, "presented") for m in rx.findall(label or "")]
    for clause in AMENDED_CLAUSE.findall(label or ""):
        head = re.split(r"\bon the source\b|,? on\b", clause)[0]
        out += [(m, "amended") for m in re.findall(r"rq-\d+", head)]
    return sorted(set(out))   # one label may phrase the same claim twice ("as proposed (rq-063: item 6 accepted as presented")


def _rows():
    return {json.loads(l)["id"]: json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()}


def _digest(rec):
    return "sha256:" + hashlib.sha256((json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                                       + "\n").encode("utf-8")).hexdigest()


@lru_cache(maxsize=None)
def _history(artifact):
    shas = subprocess.run(["git", "log", "--format=%H", "--", artifact], cwd=ROOT, capture_output=True, text=True).stdout.split()
    versions = []
    for sha in shas:
        text = subprocess.run(["git", "show", "%s:%s" % (sha, artifact)], cwd=ROOT, capture_output=True,
                              encoding="utf-8").stdout
        try:
            versions.append(json.loads(text))
        except ValueError:
            pass
    return versions


def bound_record(row):
    for g in _history(row["artifact"]):
        for rec in g.get("records", []) + g.get("adjudications", []):
            if rec["@id"] == row["record"] and _digest(rec) == row["recordDigest"]:
                return rec
    return None


def conferral_problems(l3, rows):
    """-> ([problem], {(record, act): {'presented': n, 'amended': n}})"""
    problems, counts = [], {}
    for rec in l3["records"]:
        for a in rec["assertions"]:
            for act, kind in claims(a.get("conferred")):
                row = rows.get(act)
                if not row or row.get("record") != rec["@id"]:
                    continue                            # an act on another record (e.g. rq-033 on field-types): not this bind
                before = bound_record(row)
                assert before is not None, "%s's bound bytes are not in history" % act
                prior = {x["@id"]: x for x in before["assertions"]}.get(a["@id"])
                c = counts.setdefault((rec["@id"], act), {"presented": 0, "amended": 0})
                c[kind] += 1
                if kind == "presented" and (prior is None or prior["proposed"] != a["proposed"]):
                    problems.append("%s claims %s presented it, but it differs from %s's bound record" % (a["@id"], act, act))
                if kind == "amended" and prior is not None and prior["proposed"] == a["proposed"]:
                    problems.append("%s claims %s amended it, but it equals %s's bound record" % (a["@id"], act, act))
    return problems, counts


def test_every_conferral_claim_holds_against_the_acts_bound_record():
    problems, _ = conferral_problems(json.loads(L3.read_text(encoding="utf-8")), _rows())
    assert problems == []


def test_the_gate_counts_exactly_what_rq_063_conferred():
    """Bullet 3: 5 accepted as presented (items 3, 4, 6, 7, 8) and 3 amended (route, adjudicate, input-domain)."""
    _, counts = conferral_problems(json.loads(L3.read_text(encoding="utf-8")), _rows())
    assert counts[("sr:L3:adjudicator-interface", "rq-063")] == {"presented": 5, "amended": 3}


@pytest.mark.parametrize("closure,label", [
    ("c:adjudicator:tie", None),                      # 'item 3 accepted as presented at rq-063' phrasing
    ("c:adjudicator:agreed-dimensions", None),        # '(rq-063: item 6 accepted as presented' phrasing
    ("c:ws3:VacuousPassReport", None),                # 'as proposed (rq-031)' phrasing
])
def test_changing_a_presented_closure_goes_red_whatever_the_phrasing(closure, label):
    """Bullet 1, the mutation-D shape: the record changes and the row is re-bound -- the gate still compares to the
    act's historical bind, so it goes red."""
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    bad = copy.deepcopy(l3)
    for rec in bad["records"]:
        for a in rec["assertions"]:
            if a["@id"] == closure:
                a["proposed"] = dict(a["proposed"], note=(a["proposed"].get("note") or "") + " (edited)")
    problems, _ = conferral_problems(bad, _rows())
    assert any(closure in p for p in problems), problems


def test_an_amended_claim_that_equals_its_bind_goes_red():
    """Bullet 2, the complement: a closure claiming an amendment must differ from that act's bound record."""
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    bad = copy.deepcopy(l3)
    rows = _rows()
    before = {x["@id"]: x for x in bound_record(rows["rq-063"])["assertions"]}
    for rec in bad["records"]:
        for a in rec["assertions"]:
            if a["@id"] == "c:adjudicator:route":
                a["proposed"] = before["c:adjudicator:route"]["proposed"]
    problems, _ = conferral_problems(bad, rows)
    assert any("c:adjudicator:route" in p and "amended" in p for p in problems), problems


# ------------------------------------------------------------------------------------------------- diagnostics

BLOCKING = {   # the author's declaration for diagnostics not raised by an act -- a flip must be a reviewed edit here
    "diag:W-CS3-N-third-rater-is-agentic": False, "diag:W-CS3-D2-needs-a-C-S5-report": False,
    "diag:hash-preimage-encoding-unstated": False, "diag:third-rater-tie-unwitnessed": False,
    "diag:GradeRecord-fields-by-example": False, "diag:out-of-region-endpoints": False,
    "diag:external-method-artifacts": False, "diag:ledger-hooks-repo-home": False, "diag:ws3-module-homes": False,
    "diag:C-S7-determinism-beyond-the-acted-region": False,
}


def test_no_diagnostic_status_is_a_literal_in_the_builder():
    assert all(d.get("status") is None for d in b2.DIAGNOSTICS), [d["@id"] for d in b2.DIAGNOSTICS if d.get("status")]


def test_every_built_status_is_the_derived_one_and_a_closure_names_its_act():
    """Bullet 4: flipping a status in the graph, with no act, disagrees with the derivation here."""
    g = json.loads(L2.read_text(encoding="utf-8"))
    rows = _rows()
    src = {d["@id"]: d for d in b2.DIAGNOSTICS}
    for d in g["diagnostics"]:
        derived = b2.derive_status(src[d["@id"]], rows)
        assert d["status"] == derived["status"], d["@id"]
        if d["status"] == "closed":
            by = d["closedBy"]
            assert (ROOT / by).is_file() or by.split()[0] in rows, (d["@id"], by)


def test_a_flipped_status_or_blocking_goes_red():
    g = json.loads(L2.read_text(encoding="utf-8"))
    rows = _rows()
    src = {d["@id"]: d for d in b2.DIAGNOSTICS}
    flipped = copy.deepcopy(g)
    d = next(x for x in flipped["diagnostics"] if x["@id"] == "diag:external-method-artifacts")
    d["status"] = "closed"
    assert d["status"] != b2.derive_status(src[d["@id"]], rows)["status"]
    for d in g["diagnostics"]:
        if not src[d["@id"]].get("raisedByAct"):
            assert d["blocking"] is BLOCKING[d["@id"]], d["@id"]       # bullet 5


def test_a_ratified_closure_closes_what_it_declares():
    """Bullet 6: rq-061, rq-064 and rq-066 are ratified; what their bundles `close` is closed in the graph."""
    g = {d["@id"]: d for d in json.loads(L2.read_text(encoding="utf-8"))["diagnostics"]}
    assert g["diag:GradeRecord-fields-by-example"]["closedBy"].startswith("rq-061")
    assert g["diag:hash-preimage-encoding-unstated"]["closedBy"].startswith("rq-064")
    assert g["diag:third-rater-tie-unwitnessed"]["closedBy"].startswith("rq-066")
    assert g["diag:adjudicator-not-total-over-declared-inputs"]["status"] == "closed"


UNRETRIEVABLE = {"rq-065": "queued against bytes rebuilt before they were committed (a mislabelled route closure), never "
                           "acted on, superseded by rq-066 -- Ops finding 2026-10-17 bullet 7"}


def test_every_ws3_rows_bind_is_retrievable_from_history():
    """Bullet 7 (offered): a queued row whose bound bytes no party can retrieve is a defect. The one known case is
    named here with its reason; any new one goes red."""
    rows = _rows()
    examined = [r for r in rows.values() if "srs-ws3" in r.get("artifact", "") and r.get("recordDigest")]
    assert len(examined) >= 50, "examined %d rows" % len(examined)
    missing = sorted(r["id"] for r in examined if bound_record(r) is None)
    assert missing == sorted(UNRETRIEVABLE), missing


def test_a_decided_adjudication_closes_the_conflict_it_resolves_and_only_a_live_decided_row_does():
    """2026-10-18, rq-074: "This closes diag:ws3-module-homes". Seeded rows, never the live queue."""
    d = next(x for x in b2.DIAGNOSTICS if x["@id"] == "diag:ws3-module-homes")
    assert d["resolvedByDecision"] == "adj:ws3-module-homes"
    row = {"id": "rq-900", "record": "adj:ws3-module-homes", "act": "decided", "decision": "B", "actor": "Seeded"}
    assert b2.derive_status(d, {"rq-900": row})["status"] == "closed"
    assert b2.derive_status(d, {})["status"] == "open", "no decision, still open"
    amended = dict(row, act="amended", decision=None)
    assert b2.derive_status(d, {"rq-900": amended})["status"] == "open", "an amend confers nothing"
    dead = {"rq-900": row, "rq-901": {"id": "rq-901", "record": "adj:ws3-module-homes", "supersedes": "rq-900"}}
    assert b2.derive_status(d, dead)["status"] == "open", "a superseded decision does not close it"
