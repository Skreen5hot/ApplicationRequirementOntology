"""WS-3 (Plan v1.1 s5): the capability-grain L2 graph for the A9 target is reproducible, fully grounded, inside the
named region, and queued for 100% span review without disturbing the ratified slice."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS3 = ROOT / "spike" / "graph" / "ws3"
GRAPH = ROOT / "spike" / "graph" / "l2" / "srs-ws3.graph.jsonld"
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
DIGEST = "sha256:2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450"


def _run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def _graph():
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _fragments():
    return json.loads((WS3 / "fragments.json").read_text(encoding="utf-8"))["fragments"]


def test_the_graph_on_disk_is_exactly_what_the_builder_produces():
    r = _run("spike/graph/ws3/build_l2.py", "--check")
    assert r.returncode == 0, r.stderr


def test_every_citation_resolves_to_a_fragment_minted_from_the_registered_digest():
    frags = {f["fragmentId"]: f for f in _fragments()}
    assert all(f["source"]["digest"] == DIGEST for f in frags.values())
    g = _graph()
    cited = [c["fragment"] for r in g["records"] for a in r["assertions"] for c in a["groundedBy"]]
    cited += [e for d in g["diagnostics"] for e in d["evidence"]]
    assert cited and all(c in frags for c in cited)


def test_every_assertion_is_grounded_by_a_primary_span():
    for r in _graph()["records"]:
        for a in r["assertions"]:
            assert any(c["role"] == "primary" for c in a["groundedBy"]), a["@id"]


def test_the_capabilities_are_exactly_the_A9_target():
    g = _graph()
    caps = sorted(a["target"]["name"] for r in g["records"] for a in r["assertions"]
                  if a.get("target", {}).get("kind") == "capability")
    assert caps == ["C-S2", "C-S3", "C-S7"] == g["ws3"]["target"]["capabilities"]
    assert g["ws3"]["demonstrationControlCandidate"]["capability"] == "C-S2"


def _acted_region():
    """The bound is the ACT's, read from the verbatim record by the builder's own parser -- never retyped here
    (Ops finding 2026-10-01: this test's constant once said 73-77 while its comment said 73-75)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ws3_build_l2", WS3 / "build_l2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.acted_region(), mod.in_region


def test_the_graph_carries_the_acts_region_and_not_another():
    region, _ = _acted_region()
    assert _graph()["ws3"]["target"]["regionLines"] == region


def test_every_capability_primary_span_lies_inside_the_acted_region_or_is_disclosed_beyond_it():
    """Inside the region, or listed in ws3.beyondRegion with an OPEN blocking diagnostic -- the gate never decides
    whether a span beyond the act is admissible; the architect does."""
    region, in_region = _acted_region()
    g = _graph()
    by_id = {f["fragmentId"]: f for f in _fragments()}
    diags = {d["@id"]: d for d in g["diagnostics"]}
    beyond = {b["assertion"] for b in g["ws3"]["beyondRegion"]}
    for r in g["records"]:
        if r["@id"] in ("sr:L2:C-S2", "sr:L2:C-S3", "sr:L2:C-S7"):
            for a in r["assertions"]:
                for c in a["groundedBy"]:
                    if c["role"] == "primary" and not in_region(int(by_id[c["fragment"]]["display"]["lines"]), region):
                        assert a["@id"] in beyond, (a["@id"], c["label"])
                        d = diags[a["diagnostic"]]
                        assert d["status"] == "open" and d["blocking"] is True, d["@id"]


def _live_rows(artifact):
    """Queue rows for one artifact, minus any row a later row supersedes (tools/act.py's own rule)."""
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    dead = {r.get("supersedes") for r in rows if r.get("supersedes")}
    return [r for r in rows if r.get("artifact") == artifact and r["id"] not in dead]


def test_a_span_beyond_the_region_is_flagged_on_its_queue_row_by_line():
    live = {r["record"]: r for r in _live_rows("spike/graph/l2/srs-ws3.graph.jsonld")}
    for b in _graph()["ws3"]["beyondRegion"]:
        row = live["sr:L2:" + b["assertion"].split(":")[1]]
        assert any("line %d" % b["line"] in f and "beyond" in f for f in row["displayDuties"]["vacuityClassFlags"]), row["id"]


def test_every_WS3_record_has_one_live_row_and_show_renders_it():
    # the digest property itself is pinned by test_act_tool's every-live-row check (Ops finding 2026-10-01, bullet 6)
    ws3 = _live_rows("spike/graph/l2/srs-ws3.graph.jsonld")
    recs = [r["@id"] for r in _graph()["records"]]
    assert sorted(r["record"] for r in ws3) == sorted(recs)
    for row in ws3:
        assert _run("tools/act.py", "show", row["id"]).returncode == 0, row["id"]


def test_the_ratified_slice_projection_is_untouched():
    r = _run("spike/projections/project.py", "--check")
    assert r.returncode == 0 and "byte-identical" in r.stdout, r.stdout + r.stderr


L3 = ROOT / "spike" / "graph" / "l3" / "srs-ws3.design.candidates.jsonld"


def test_the_L3_candidates_on_disk_are_exactly_what_the_builder_produces():
    r = _run("spike/graph/ws3/build_l3.py", "--check")
    assert r.returncode == 0, r.stderr


def test_L3_never_grounds_and_every_reference_lands_in_the_L2_graph():
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    assert '"groundedBy"' not in L3.read_text(encoding="utf-8"), "L3 forbids groundedBy (ARO D17)"
    g = _graph()
    known = ({r["@id"] for r in g["records"]} | {a["@id"] for r in g["records"] for a in r["assertions"]}
             | {d["@id"] for d in g["diagnostics"]})
    refs = [x for r in l3["records"] for x in r["dependsOn"] + r["closes"] + r["addresses"]]
    refs += [a["conflict"] for a in l3["adjudications"]]
    assert refs and [x for x in refs if x not in known] == []


def test_every_L3_record_and_adjudication_has_one_live_row():
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    ids = [r["@id"] for r in l3["records"]] + [a["@id"] for a in l3["adjudications"]]
    queued = _live_rows("spike/graph/l3/srs-ws3.design.candidates.jsonld")
    assert sorted(r["record"] for r in queued) == sorted(ids), "exactly one LIVE row per record"
    assert {r["batch"] for r in queued} <= {"WS3-2", "WS3-3"}
    for row in queued:
        assert _run("tools/act.py", "show", row["id"]).returncode == 0, row["id"]


def test_the_architects_amendment_is_what_moved_the_bound(tmp_path):
    """2026-10-01: 'amend A9's region to 73–76'. Without the amendment record the parser returns A9's own 73-75;
    with it, 73-76 -- the bound moves only by an act on the record, never by editing a number in code."""
    import shutil
    region, _ = _acted_region()
    assert region == [[43, 53], [73, 76]]
    d = tmp_path / "decisions"
    d.mkdir()
    shutil.copy(ROOT / "docs" / "decisions" / "2026-10-01-a9-ws3-target-naming-act.md", d)
    import importlib.util
    spec = importlib.util.spec_from_file_location("ws3_build_l2_b", WS3 / "build_l2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.acted_region(d / "2026-10-01-a9-ws3-target-naming-act.md") == [[43, 53], [73, 75]]
    assert _graph()["ws3"]["beyondRegion"] == []


def _load(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, WS3 / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_an_L3_bundle_resting_on_a_blocked_assertion_must_disclose_it():
    """Falsification (Ops finding 2026-10-01, bullet 2), on the state as it stands: the ledger bundle rests on the
    two C-S7 clauses the architect's rq-034 diagnostic blocks, and discloses them. Remove the disclosure -> refused;
    lift the block while the disclosure stays -> refused as stale."""
    import copy
    l3 = _load("build_l3")
    g = _graph()
    assert l3.undisclosed_blocked_dependencies(l3.RECORDS, g) == []
    undisclosed = [{k: v for k, v in r.items() if k != "blockedDependencies"} for r in l3.RECORDS]
    assert dict(l3.undisclosed_blocked_dependencies(undisclosed, g)) == {
        "sr:L3:ledger-interface": ["a:C-S7:W-CS7-D1", "a:C-S7:W-CS7-N"]}
    lifted = copy.deepcopy(g)
    for d in lifted["diagnostics"]:
        if d["@id"] == "diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash":
            d["status"] = "closed"
    assert dict(l3.undisclosed_blocked_dependencies(l3.RECORDS, lifted)) == {"sr:L3:ledger-interface": []},         "a stale disclosure (the block lifted) is refused too"


def test_section_3_coverage_is_derived_from_the_spans_and_lies_in_the_region():
    region, in_region = _acted_region()
    import re
    text = _graph()["coverage"]["covered"]["SRS §3"]
    ranges = [(int(a), int(b)) for a, b in re.findall(r"\((\d+)–(\d+)\)", text)]
    assert len(ranges) == 3 and all(in_region(a, region) and in_region(b, region) for a, b in ranges), text


def test_a_rebuilt_item_supersedes_the_amended_one_and_carries_the_architects_note_verbatim():
    """An amend confers nothing; the record is rebuilt and re-queued at its new address, superseding the amended
    row. The rebuilt record quotes the architect's note from the queue (read, not retyped), and a conferred item
    (ratified / decided) is never re-queued."""
    rows = {r["id"]: r for r in (json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip())}
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    for rec in l3["records"]:
        for note in rec.get("amendmentNotes", []):
            assert note["note"] == rows[note["item"]]["actNote"], (rec["@id"], note["item"])
    live = {r["record"]: r for r in _live_rows("spike/graph/l3/srs-ws3.design.candidates.jsonld")}
    for amended in ("rq-031", "rq-032", "rq-033", "rq-034"):
        assert any(r.get("supersedes") == amended for r in live.values()), amended
    assert live["sr:L3:ws3-module-boundaries"]["id"] == "rq-030"
    assert live["adj:ledger-hooks-repo-home"]["id"] == "rq-035"


def test_every_amended_row_has_a_successor_bound_to_the_records_current_address():
    """IA Ops finding 2026-10-01, bullet 2: an amend confers nothing, so it must be followed by a re-queue at the
    record's new address -- a queue holding an amended row with no live successor fails here."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("aro_act_t", ROOT / "tools" / "act.py")
    act = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(act)
    q = act.Queue(ROOT)
    rows = [r for _, r in q.rows]
    for amended in (r for r in rows if r.get("act") == "amended"):
        succ = [r for r in rows if r.get("supersedes") == amended["id"]]
        assert succ, "%s is amended with no successor" % amended["id"]
        live = [r for r in succ if r["id"] not in q.superseded()] or succ
        assert any(q.current_digest(r)[1] == r["recordDigest"] for r in live), amended["id"]


def test_the_architects_blocking_diagnostic_is_derived_from_the_act_row():
    """IA Ops finding 2026-10-01, bullet 1: status and blocking come from rq-034's act, never retyped. Falsified on a
    copy of the queue: drop BLOCKING from the note -> not blocking; confer a successor -> closed."""
    b2 = _load("build_l2")
    g = _graph()
    d = [x for x in g["diagnostics"] if x["@id"] == "diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash"][0]
    queue = {json.loads(l)["id"]: json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()}
    assert d["status"] == "open" and d["blocking"] is True and d["actRecord"]["note"] == queue["rq-034"]["actNote"]
    src = [x for x in b2.DIAGNOSTICS if x["@id"] == d["@id"]][0]
    soft = dict(queue, **{"rq-034": dict(queue["rq-034"], actNote="kind is outside the preimage")})
    assert b2.raised_by_act(src, soft)["blocking"] is False
    succ = [r for r in queue.values() if r.get("supersedes") == "rq-034"][0]
    done = dict(queue, **{succ["id"]: dict(succ, act="ratified", actor="Aaron")})
    assert b2.raised_by_act(src, done)["status"] == "closed"
