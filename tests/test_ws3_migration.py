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


def test_minting_honours_the_per_source_override_and_an_unreadable_source_is_a_legible_lapse(tmp_path):
    sys.path.insert(0, str(ROOT / "spike" / "graph"))
    import fragments as F
    spans = _load(WS3 / "spans.json")
    copy_of_source = tmp_path / "amended.md"
    copy_of_source.write_bytes(Path(spans["doc"]).read_bytes())
    key = "ARO_SOURCE_DOC_" + spans["expectedDigest"].split(":")[-1][:8].upper()
    alt = tmp_path / "spans.json"
    alt.write_text(json.dumps(dict(spans, doc=str(tmp_path / "nowhere" / "SPEC.md"))), encoding="utf-8")
    env_before = dict(os.environ)
    try:
        os.environ.pop("ARO_SOURCE_DOC", None)
        with pytest.raises(F.Refused, match="every fragment lapses"):
            F.extract(alt)                                  # the registered path is unreadable -> legible, no traceback
        os.environ[key] = str(copy_of_source)
        minted = F.extract(alt)                             # the per-source override binds this generation only
        assert minted["source"]["digest"] == spans["expectedDigest"]
        assert F.source_doc("anything", "sha256:2428b115" + "0" * 56) == Path("anything"), "other generations unaffected"
    finally:
        os.environ.clear()
        os.environ.update(env_before)
