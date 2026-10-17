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
EXCEPTIONS = {
    "adj:ledger-hash-kind": "rq-038, decided A 2026-10-17T03:25:58-04:00 on a paraphrase (one passage carries the dev "
                            "agent's gloss '-- kind is not in the preimage'; the other elides H-LEDGER-01 to '...'). "
                            "Its bound bytes are left as acted; act.py show prints both cited fragments' verbatim bytes "
                            "beneath each passage, flagged NOT VERBATIM. The architect AFFIRMED A on the verbatim text "
                            "('stands'): docs/decisions/2026-10-17-rq-038-affirmed-on-the-verbatim-source.md.",
}


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
