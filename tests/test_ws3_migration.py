"""The 2026-10-17 migration link is gated (IA Ops finding: "the migration link is ungated and the minting path is
closed to the verifier"). Every migratedFrom is checked against the predecessor set and the textHashes; the
re-acceptance flags are recomputed; the set re-mints byte for byte; minting honours the source override."""
import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WS3 = ROOT / "spike" / "graph" / "ws3"
NEW = WS3 / "fragments.json"
OLD = WS3 / "fragments-2428b115.json"
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
GRAPH_REL = "spike/graph/l2/srs-ws3.graph.jsonld"


def _load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def migration_problems(new, old):
    """Every way a migration set can be wrong -> [problem]. The single oracle the named tests below drive."""
    o_by_id = {f["fragmentId"]: f for f in old["fragments"]}
    out = []
    targets = []
    for f in new["fragments"]:
        m = f.get("migratedFrom")
        if not m:
            out.append("%s: no migratedFrom" % f["label"])
            continue
        o = o_by_id.get(m["fragment"])
        if o is None:
            out.append("%s: migratedFrom %s is not in the pre-amendment set" % (f["label"], m["fragment"]))
            continue
        targets.append(m["fragment"])
        if o["label"] != f["label"]:
            out.append("%s: migratedFrom points at span %s" % (f["label"], o["label"]))
        if m["digest"] != old["source"]["digest"]:
            out.append("%s: migratedFrom names digest %s, not the predecessor's" % (f["label"], m["digest"]))
        truth = "unchanged" if o["textHash"] == f["textHash"] else "CHANGED"
        if m["text"] != truth:
            out.append("%s: text flag says %s, the hashes say %s" % (f["label"], m["text"], truth))
    if len(set(targets)) != len(targets):
        out.append("two fragments migrate from the same predecessor")
    return out


def test_every_migration_link_holds_and_the_counts_are_exact():
    new, old = _load(NEW), _load(OLD)
    assert migration_problems(new, old) == []
    links = [f["migratedFrom"] for f in new["fragments"]]
    assert len(links) == len(new["fragments"]) == 34
    assert len({l["fragment"] for l in links}) == 34
    assert {l["digest"] for l in links} == {old["source"]["digest"]}
    changed = [f["label"] for f in new["fragments"] if f["migratedFrom"]["text"] == "CHANGED"]
    assert changed == ["C-S7.W-CS7-N"] == new["migration"]["changed"]


@pytest.mark.parametrize("mutation", ["delete", "foreign", "other-label", "flip-unchanged", "flip-changed"])
def test_each_way_of_breaking_a_link_is_caught(mutation):
    new, old = _load(NEW), _load(OLD)
    bad = copy.deepcopy(new)
    f = next(x for x in bad["fragments"] if x["label"] == ("C-S7.W-CS7-N" if mutation == "flip-changed" else "C-S2.header"))
    if mutation == "delete":
        del f["migratedFrom"]
    elif mutation == "foreign":
        f["migratedFrom"]["fragment"] = "sf:" + "0" * 24
    elif mutation == "other-label":
        f["migratedFrom"]["fragment"] = next(o["fragmentId"] for o in old["fragments"] if o["label"] == "C-S3.header")
    elif mutation == "flip-unchanged":
        f["migratedFrom"]["text"] = "CHANGED"
    else:
        f["migratedFrom"]["text"] = "unchanged"
    assert migration_problems(bad, old), mutation


def test_the_reacceptance_flags_are_recomputed_from_the_fragments_not_copied():
    """Bullet 5: each WS3-4 re-acceptance row's 'N of M unchanged ... CHANGED text at line(s) ...' must equal what
    the fragment texts say. Live cases rq-047 (7 of 8), rq-053 (3 of 4), rq-059 (1 of 2)."""
    new, old = _load(NEW), _load(OLD)
    by_id = {f["fragmentId"]: f for f in new["fragments"]}
    o_by_id = {f["fragmentId"]: f for f in old["fragments"]}
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    lapse = [r for r in rows if r.get("artifact") == GRAPH_REL and "RE-ACCEPTANCE" in r.get("kind", "")]
    assert len(lapse) == 15
    seen = {}
    for r in lapse:
        cited = r["displayDuties"]["fragmentTextBesideAssertions"]
        changed = [t["line"] for t in cited if o_by_id[by_id[t["fragment"]]["migratedFrom"]["fragment"]]["textHash"]
                   != by_id[t["fragment"]]["textHash"]]
        flag = r["displayDuties"]["vacuityClassFlags"][0]
        m = re.search(r"(\d+) of (\d+) cited spans are unchanged text", flag)
        assert m and (int(m.group(1)), int(m.group(2))) == (len(cited) - len(changed), len(cited)), (r["id"], flag)
        assert (("CHANGED text at line(s) " + ", ".join(changed)) in flag) == bool(changed), (r["id"], flag)
        seen[r["id"]] = (len(cited) - len(changed), len(cited))
    assert seen["rq-047"] == (7, 8) and seen["rq-053"] == (3, 4) and seen["rq-059"] == (1, 2)


def test_the_set_re_mints_byte_for_byte():
    r = subprocess.run([sys.executable, "spike/graph/ws3/mint.py", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr + r.stdout


def test_minting_honours_the_per_source_override_and_an_unreadable_source_is_a_legible_lapse(tmp_path, bound_source):
    sys.path.insert(0, str(ROOT / "spike" / "graph"))
    import fragments as F
    spans = _load(WS3 / "spans.json")
    digest = spans["expectedDigest"]
    copy_of_source = tmp_path / "amended.md"
    # seeded THROUGH source_doc (the verifier's binding), never by reading the registered path itself
    copy_of_source.write_bytes(F.source_doc(spans["doc"], digest).read_bytes())
    alt = tmp_path / "spans.json"
    alt.write_text(json.dumps(dict(spans, doc=str(tmp_path / "nowhere" / "SPEC.md"))), encoding="utf-8")
    bound_source.unbind_global()
    bound_source.unbind(digest)                             # neither override: the registered path alone is read
    with pytest.raises(F.Refused, match="every fragment lapses"):
        F.extract(alt)                                      # the registered path is unreadable -> legible, no traceback
    bound_source.bind(digest, copy_of_source)
    minted = F.extract(alt)                                 # the per-source override binds this generation only
    assert minted["source"]["digest"] == digest
    # isolation, asserted against a digest NO runner binds -- never against the absence of a sibling override the
    # runner may legitimately hold (ARO_SOURCE_DOC_2428B115 binds the slice; IA Ops finding 2026-10-17, bullet 4)
    assert F.source_doc("anything", "sha256:" + "0" * 64) == Path("anything"), "other generations unaffected"


def _bound_copy(tmp_path, name):
    """A copy of the amended source under an arbitrary file name, made through the verifier's own binding."""
    sys.path.insert(0, str(ROOT / "spike" / "graph"))
    import fragments as F
    spans = _load(WS3 / "spans.json")
    p = tmp_path / name
    p.write_bytes(F.source_doc(spans["doc"], spans["expectedDigest"]).read_bytes())
    return p, spans["expectedDigest"]


def test_mint_check_passes_under_any_override_file_name(tmp_path, bound_source):
    """IA Ops finding 2026-10-17 bullets 1-2: the re-mint reproduces the committed file byte for byte whatever the
    override copy is called -- minted twice under two different names, and the outputs compared. Every binding change
    goes through `bound_source`, so the runner's own binding is restored, not deleted (successor finding, bullet 3)."""
    copies = [_bound_copy(tmp_path, name) for name in ("SRS-SPEC-109e1b50.md", "a different name.txt")]
    sys.path.insert(0, str(WS3))
    import mint
    outs = []
    for p, digest in copies:
        bound_source.unbind_global()
        bound_source.bind(digest, p)
        env = dict(os.environ)                              # a copy for the child; the runner's env is not written
        r = subprocess.run([sys.executable, "spike/graph/ws3/mint.py", "--check"], cwd=ROOT, env=env,
                           capture_output=True, text=True)
        assert r.returncode == 0, (p.name, r.stderr + r.stdout)
        outs.append(mint.render(mint.mint()))
    assert len(outs) == 2 and outs[0] == outs[1]


def test_no_minted_field_derives_from_the_resolved_source_path(tmp_path, bound_source):
    """Bullet 6, the rule stated once: nothing written into fragments.json comes from the path actually READ."""
    p, digest = _bound_copy(tmp_path, "ZZQ-resolved-marker-copy.md")
    sys.path.insert(0, str(WS3))
    import mint
    bound_source.unbind_global()
    bound_source.bind(digest, p)
    text = mint.render(mint.mint())
    assert "ZZQ-resolved-marker-copy" not in text and str(tmp_path) not in text


def test_the_reshape_moved_path_fields_only():
    """Bullet 5: against the pre-reshape bytes (ARO 1070bdb), only the top-level source.doc moved; all 34 textHash
    values, all 34 migratedFrom blocks and every per-fragment field are unchanged."""
    before = json.loads(subprocess.run(["git", "show", "1070bdb:spike/graph/ws3/fragments.json"], cwd=ROOT,
                                       capture_output=True, encoding="utf-8").stdout)
    now = _load(NEW)
    assert before["fragments"] == now["fragments"] and before["migration"] == now["migration"]
    assert {k: v for k, v in before["source"].items() if k != "doc"} == {k: v for k, v in now["source"].items() if k != "doc"}
