"""Every source passage an adjudication shows under `theSourceSays` is the cited fragment's own bytes -- or a contiguous
excerpt of them with nothing added (IA Ops finding 2026-10-17, HIGH: "the source passages a decided adjudication
shows are a paraphrase, and the copy rule is opt-in"). Shape A: the class is fenced by this gate for EVERY
adjudication; the one decided record standing on a paraphrase is carried as a named, dated exception, and its bound
bytes do not move (rq-038's act stays intact)."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
L3 = ROOT / "spike" / "graph" / "l3" / "srs-ws3.design.candidates.jsonld"
FRAGMENT_SETS = [ROOT / "spike" / "graph" / "ws3" / "fragments.json", ROOT / "spike" / "graph" / "ws3" / "fragments-2428b115.json"]

spec = importlib.util.spec_from_file_location("aro_act", ROOT / "tools" / "act.py")
act = importlib.util.module_from_spec(spec)
spec.loader.exec_module(act)

# Named, dated, and checked to still be TRUE: an exception that no longer fails the rule is itself red (stale).
# The warrant is STRUCTURED and RESOLVED, never prose (IA Ops finding 2026-10-17, "the exception that carries the
# affirmation cites a record no gate resolves"): test_the_exception_warrant_resolves checks every field against the
# queue row and the affirmation record, so deleting the record or drifting a digest is red by name.
EXCEPTIONS = {
    "adj:ledger-hash-kind": {
        "row": "rq-038", "act": "decided", "decision": "A", "actedAt": "2026-10-17T03:25:58-04:00",
        "digest": "sha256:86cb35d5730a94fb0ca2ffc0c0b7003a4cd661f1e84932995e36d93b2e68b9ff",
        "affirmedBy": "docs/decisions/2026-10-17-rq-038-affirmed-on-the-verbatim-source.md",
        "why": "decided on a paraphrase (the gloss '-- kind is not in the preimage'; H-LEDGER-01 elided to '...'); "
               "bound bytes left as acted; show prints the verbatim fragments beneath; the architect affirmed A ('stands')",
    },
}
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"


def warrant_problems(exceptions, rows, root):
    """[why] for every exception whose structured warrant does not resolve -> []. One line per broken field."""
    by_id = {r["id"]: r for r in rows}
    out = []
    for adj, w in exceptions.items():
        r = by_id.get(w["row"])
        if r is None:
            out.append("%s: row %s is not in the queue" % (adj, w["row"]))
            continue
        for k in ("act", "decision", "actedAt"):
            if r.get(k) != w[k]:
                out.append("%s: %s.%s is %r, the warrant says %r" % (adj, w["row"], k, r.get(k), w[k]))
        if r.get("record") != adj:
            out.append("%s: %s binds %s" % (adj, w["row"], r.get("record")))
        for k in ("recordDigest", "actDigest"):
            if r.get(k) != w["digest"]:
                out.append("%s: %s.%s is %s, the warrant says %s" % (adj, w["row"], k, r.get(k), w["digest"]))
        doc = root / w["affirmedBy"]
        if not doc.is_file():
            out.append("%s: affirmedBy %s does not exist" % (adj, w["affirmedBy"]))
            continue
        text = doc.read_text(encoding="utf-8")
        for needle in (w["digest"], w["row"], adj):
            if needle not in text:
                out.append("%s: %s does not name %s" % (adj, w["affirmedBy"], needle))
    return out


def _fragments():
    out = {}
    for p in FRAGMENT_SETS:
        for f in json.loads(p.read_text(encoding="utf-8"))["fragments"]:
            out[f["fragmentId"]] = f["text"]
    return out


def passage_problems(adjudications, frags):
    """[(adjudication, label, why)] for every theSourceSays passage that is not a verbatim excerpt of its fragment."""
    out = []
    for adj in adjudications:
        val = adj.get("theSourceSays")
        for p in (val if isinstance(val, list) else [val] if val else []):
            text = frags.get(p.get("fragment"))
            if text is None:
                out.append((adj["@id"], p.get("label"), "cites %s, which no minted fragment set holds" % p.get("fragment")))
            elif not act.is_verbatim_excerpt(p.get("text") or "", text):
                out.append((adj["@id"], p.get("label"), "not a verbatim excerpt of %s" % p["fragment"]))
    return out


def _population():
    adjs = json.loads(L3.read_text(encoding="utf-8"))["adjudications"]
    n = sum(len(a["theSourceSays"]) if isinstance(a.get("theSourceSays"), list) else 1 for a in adjs if a.get("theSourceSays"))
    return adjs, n


def test_every_shown_source_passage_is_its_fragments_own_bytes_save_the_named_exception():
    adjs, n = _population()
    assert len(adjs) >= 3 and n >= 5, "examined %d adjudications and %d passages" % (len(adjs), n)
    problems = passage_problems(adjs, _fragments())
    assert sorted({a for a, _, _ in problems}) == sorted(EXCEPTIONS), problems
    assert sorted(l for a, l, _ in problems) == ["C-S7.W-CS7-D1", "C-S7.W-CS7-N"], "the exception is exactly rq-038's two"


def _rows():
    return [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_the_exception_warrant_resolves():
    """Bullets 1-4: every field of each exception's warrant is checked against the queue row and the affirmation
    record. Counted: 1 exception resolved today."""
    assert len(EXCEPTIONS) == 1, "resolved %d exception(s)" % len(EXCEPTIONS)
    assert warrant_problems(EXCEPTIONS, _rows(), ROOT) == []


@pytest.mark.parametrize("break_it", ["record-renamed", "warrant-digest", "row-digest", "record-digest", "actedAt"])
def test_a_broken_warrant_is_red_by_name(break_it, tmp_path):
    w = copy.deepcopy(EXCEPTIONS)
    rows = copy.deepcopy(_rows())
    root = ROOT
    if break_it == "record-renamed":
        w["adj:ledger-hash-kind"]["affirmedBy"] = "docs/decisions/renamed.md"
    elif break_it == "warrant-digest":
        w["adj:ledger-hash-kind"]["digest"] = w["adj:ledger-hash-kind"]["digest"][:-1] + "0"
    elif break_it == "row-digest":
        r = next(x for x in rows if x["id"] == "rq-038")
        r["actDigest"] = r["actDigest"][:-1] + "0"
    elif break_it == "record-digest":   # the affirmation record itself names another digest
        root = tmp_path
        doc = root / w["adj:ledger-hash-kind"]["affirmedBy"]
        doc.parent.mkdir(parents=True)
        src = (ROOT / w["adj:ledger-hash-kind"]["affirmedBy"]).read_text(encoding="utf-8")
        doc.write_text(src.replace(w["adj:ledger-hash-kind"]["digest"], w["adj:ledger-hash-kind"]["digest"][:-1] + "0"), encoding="utf-8")
    else:
        w["adj:ledger-hash-kind"]["actedAt"] = "2026-10-17T03:25:59-04:00"
    problems = warrant_problems(w, rows, root)
    assert problems and all(p.startswith("adj:ledger-hash-kind: ") for p in problems), problems


@pytest.mark.parametrize("target", ["adj:ledger-hooks-repo-home", "adj:ws3-module-homes"])
def test_one_inserted_word_turns_a_clean_passage_red_by_name(target):
    adjs, _ = _population()
    bad = copy.deepcopy(adjs)
    a = next(x for x in bad if x["@id"] == target)
    p = a["theSourceSays"][0] if isinstance(a["theSourceSays"], list) else a["theSourceSays"]
    words = p["text"].split(" ")
    p["text"] = " ".join(words[:2] + ["clearly"] + words[2:])
    assert [x for x in passage_problems(bad, _fragments()) if x[0] == target] == [(target, p["label"], "not a verbatim excerpt of %s" % p["fragment"])]


def test_a_bare_elision_is_red_and_the_sources_own_ellipsis_is_not():
    frag = 'append `{"vector": …}`; any rewrite → hook exit 1, `{"code": "H-LEDGER-01"}`; chain fails'
    assert act.is_verbatim_excerpt('append `{"vector": …}`;', frag)
    assert not act.is_verbatim_excerpt("any rewrite → hook exit 1 ...; chain fails", frag)
    assert not act.is_verbatim_excerpt("", frag)


def test_show_prints_the_fragments_own_bytes_beneath_a_paraphrase(capsys):
    q = act.Queue(ROOT)
    row = next(r for _, r in q.rows if r.get("record") == "adj:ledger-hash-kind" and r.get("actedAt"))
    out = act.render_show(q, row)
    assert out.count("NOT VERBATIM. The cited fragment") == 2
    assert '"H-LEDGER-01"' in out, "the elided error code is shown from the fragment"
    clean = next(r for _, r in q.rows if r.get("record") == "adj:ledger-hooks-repo-home" and r.get("actedAt"))
    shown = act.render_show(q, clean)
    assert "NOT VERBATIM" not in shown and "(verbatim from " in shown
