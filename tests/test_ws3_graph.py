"""WS-3 (Plan v1.1 s5): the capability-grain L2 graph for the A9 target is reproducible, fully grounded, inside the
named region, and queued for 100% span review without disturbing the ratified slice."""
import json

import pytest
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS3 = ROOT / "spike" / "graph" / "ws3"
GRAPH = ROOT / "spike" / "graph" / "l2" / "srs-ws3.graph.jsonld"
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
REGISTER = ROOT / "spike" / "graph" / "source-register.json"
DIGEST = next(s["digest"] for s in json.loads(REGISTER.read_text(encoding="utf-8"))["registeredSources"]
              if s["id"] == "src:srs-spec@2")   # the source WS-3 now binds (2026-10-17 amendment)


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


def test_today_no_capability_span_lies_beyond_the_region_and_a_seeded_one_is_refused_or_disclosed(monkeypatch):
    """IA Ops finding 2026-10-17 (HIGH) bullet 5: say which case is measured. Today beyondRegion is EMPTY (the region
    was amended to 73-76). A seeded primary span outside the region is refused undisclosed and listed disclosed."""
    import copy
    assert _graph()["ws3"]["beyondRegion"] == []
    b2 = _load("build_l2")
    seeded = copy.deepcopy(b2.RECORDS)
    cap = next(r for r in seeded if r["@id"] == "sr:L2:C-S7")
    det = next(x for x in cap["assertions"] if x["@id"] == "a:C-S7:determinism")
    det["groundedBy"] = [b2.g("R-S1")]                                   # line 87: outside 43-53 / 73-76
    det.pop("diagnostic", None)
    monkeypatch.setattr(b2, "RECORDS", seeded)
    with pytest.raises(SystemExit, match="beyond the acted region with no diagnostic"):
        b2.build()
    det["diagnostic"] = "diag:seeded"
    beyond = b2.build()["ws3"]["beyondRegion"]
    assert [x["assertion"] for x in beyond] == ["a:C-S7:determinism"] and beyond[0]["line"] == 87


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


def _live_end(rows, item_id):
    """Follow `supersedes` forward from an item to the live end of its chain (rq-031 -> rq-039 -> rq-043)."""
    nxt = {r["supersedes"]: r["id"] for r in rows if r.get("supersedes")}
    while item_id in nxt:
        item_id = nxt[item_id]
    return item_id


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
    assert {r["batch"] for r in queued} <= {"WS3-2", "WS3-3", "WS3-4"}
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
    """Falsification (Ops finding 2026-10-01, bullet 2). Today nothing the bundles rest on is blocked (the C-S7
    conflict was resolved by the 2026-10-17 source amendment). Re-open a block on a copy of the L2 graph -> the
    ledger bundle is refused until it discloses it; disclose with no block -> refused as stale."""
    import copy
    l3 = _load("build_l3")
    g = _graph()
    assert l3.undisclosed_blocked_dependencies(l3.RECORDS, g) == []
    blocked = copy.deepcopy(g)
    for d in blocked["diagnostics"]:
        if d["@id"] == "diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash":
            d["status"], d["blocking"] = "open", True
    assert dict(l3.undisclosed_blocked_dependencies(l3.RECORDS, blocked)) == {
        "sr:L3:ledger-interface": ["a:C-S7:W-CS7-D1", "a:C-S7:W-CS7-N"]}
    stale = [dict(r, blockedDependencies=["a:C-S7:W-CS7-N"]) if r["@id"] == "sr:L3:ledger-interface" else r
             for r in l3.RECORDS]
    assert dict(l3.undisclosed_blocked_dependencies(stale, g)) == {"sr:L3:ledger-interface": []},         "a stale disclosure (no block) is refused too"


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
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    for amended in ("rq-031", "rq-032", "rq-033", "rq-034"):
        end = _live_end(rows, amended)
        assert end != amended and end in {r["id"] for r in live.values()}, (amended, end)
    mb = live["sr:L3:ws3-module-boundaries"]
    assert mb["supersedes"] == "rq-030" and "RE-RATIFICATION" in mb["displayDuties"]["vacuityClassFlags"][0],         "a conferred item is re-queued only by the source lapse"
    assert live["adj:ledger-hooks-repo-home"]["id"] == "rq-035" and live["adj:ledger-hash-kind"]["id"] == "rq-038",         "decided adjudications stay bound to the fragments they were decided on"


def test_every_amended_row_has_a_successor_bound_to_the_records_current_address():
    """IA Ops finding 2026-10-01, bullet 2: an amend confers nothing, so it must be followed by a re-queue at the
    record's new address -- a queue holding an amended row with no live successor fails here."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("aro_act_t", ROOT / "tools" / "act.py")
    act = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(act)
    q = act.Queue(ROOT)
    rows = [r for _, r in q.rows]
    by_id = {r["id"]: r for r in rows}
    amended_rows = [r for r in rows if r.get("act") == "amended"]
    assert len(amended_rows) >= 6, "examined %d amended rows" % len(amended_rows)   # rq-031..034, rq-040, rq-042, rq-063
    for amended in amended_rows:
        end = _live_end(rows, amended["id"])
        assert end != amended["id"], "%s is amended with no successor" % amended["id"]
        assert q.current_digest(by_id[end])[1] == by_id[end]["recordDigest"], (amended["id"], end)


def _unsettled_rq044_chain():
    """A copy of the queue in which rq-044's chain ends at an AMENDED row (rq-063), as it stood before rq-066:
    every row past rq-063 on that chain is dropped. Built here so the arms below never ride on the live state."""
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    queue = {r["id"]: r for r in rows}
    at, drop = "rq-063", set()
    nxt = {r["supersedes"]: r["id"] for r in rows if r.get("supersedes")}
    while at in nxt:
        at = nxt[at]
        drop.add(at)
    q = {k: v for k, v in queue.items() if k not in drop}
    assert q["rq-063"]["act"] == "amended" and q["rq-044"]["act"] == "diagnostic-opened"
    return q


def test_the_architects_blocking_diagnostic_is_derived_from_the_act_row():
    """IA Ops findings 2026-10-01 bullet 1 and 2026-10-17 (HIGH) bullet 2. The live subject is taken from the rule;
    every falsification arm runs on an UNSETTLED chain, so none is vacuous whatever the live queue holds."""
    b2 = _load("build_l2")
    src = [x for x in b2.DIAGNOSTICS if x["@id"] == "diag:adjudicator-not-total-over-declared-inputs"][0]
    live = {d["@id"]: d for d in _graph()["diagnostics"]}[src["@id"]]
    rows_live = {json.loads(l)["id"]: json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()}
    assert live["status"] == b2.raised_by_act(src, rows_live)["status"]          # the subject, from the rule
    unsettled = _unsettled_rq044_chain()
    a_ = b2.raised_by_act(src, unsettled)                                        # (a) only an amended successor
    assert a_["status"] == "open"
    settled = dict(unsettled, **{"rq-063": dict(unsettled["rq-063"], act="ratified")})
    b_ = b2.raised_by_act(src, settled)                                          # (b) that successor ratified
    assert b_["status"] == "closed" and "rq-063" in b_["closedBy"]
    soft = dict(unsettled, **{"rq-044": dict(unsettled["rq-044"], actNote="adjudicate is not total")})
    assert b2.raised_by_act(src, soft)["blocking"] is False                      # (c) no BLOCKING, unsettled
    hard = dict(unsettled, **{"rq-044": dict(unsettled["rq-044"], actNote="BLOCKING: adjudicate is not total")})
    assert b2.raised_by_act(src, hard)["blocking"] is True                       # (d) BLOCKING, unsettled
    hop2 = dict(unsettled, **{"rq-999": dict(unsettled["rq-063"], id="rq-999", supersedes="rq-063", act="ratified")})
    assert b2.raised_by_act(src, hop2)["status"] == "closed"                     # two hops
    k = {d["@id"]: d for d in _graph()["diagnostics"]}["diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash"]
    assert k["status"] == "closed" and k["closedBy"].endswith("2026-10-17-srs-source-amendment-and-registration.md")


def _record_as_acted(row):
    """The record bytes an act was bound to: the version of its artifact, in git history, whose record digest equals
    the row's recordDigest. Never reconstructed -- found."""
    import hashlib
    import subprocess
    shas = subprocess.run(["git", "log", "--format=%H", "--", row["artifact"]], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    for sha in shas:
        text = subprocess.run(["git", "show", "%s:%s" % (sha, row["artifact"])], cwd=ROOT,
                              capture_output=True, encoding="utf-8").stdout
        try:
            g = json.loads(text)
        except ValueError:
            continue
        for rec in g.get("records", []) + g.get("adjudications", []):
            if rec["@id"] == row["record"]:
                canon = json.dumps(rec, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
                if "sha256:" + hashlib.sha256(canon.encode("utf-8")).hexdigest() == row["recordDigest"]:
                    return rec
    raise AssertionError("no version of %s in history matches %s" % (row["artifact"], row["id"]))


def test_a_closure_declared_as_proposed_is_byte_identical_to_the_proposal_the_act_bound():
    """Ops finding 2026-10-01 (c:ws3:VacuousPassReport): a closure whose `conferred` says 'as proposed' carried a
    rewritten note. For every rebuilt record, each closure declared 'as proposed' must equal, byte for byte, the
    closure in the record the architect's amend was bound to."""
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_id = {r["id"]: r for r in rows}
    l3 = json.loads(L3.read_text(encoding="utf-8"))
    checked = 0
    for rec in l3["records"]:
        for item in rec.get("amendmentOf", []):
            before = {a["@id"]: a for a in _record_as_acted(by_id[item])["assertions"]}
            for a in rec["assertions"]:
                if str(a.get("conferred", "")).startswith("as proposed") and a["@id"] in before:
                    assert a["proposed"] == before[a["@id"]]["proposed"], (rec["@id"], a["@id"], item)
                    checked += 1
    assert checked >= 7, checked


def test_the_queue_never_forks_and_a_fork_is_refused_not_guessed():
    """Ops residual 333b392: with two successors of one row, which branch settles a block depended on file order.
    One successor per row, in the live queue; and the derivation refuses a fork rather than picking a branch."""
    import pytest
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    sup = [r["supersedes"] for r in rows if r.get("supersedes")]
    assert len(sup) == len(set(sup)), "a row is superseded twice"
    b2 = _load("build_l2")
    queue = {r["id"]: r for r in rows}
    src = [x for x in b2.DIAGNOSTICS if x.get("raisedByAct") == "rq-044"][0]
    end = _live_end(rows, "rq-044")
    forked = dict(queue, **{"rq-998": dict(queue[end], id="rq-998", supersedes=queue[end].get("supersedes"))})
    with pytest.raises(SystemExit, match="forks"):
        b2.raised_by_act(src, forked)


def test_the_A9_restatement_names_the_region_and_digest_the_graph_uses():
    """2026-10-17: the architect re-anchored A9 to src:srs-spec@2. The restatement's quoted region and digest must be
    the ones the graph carries -- read from the record, never retyped."""
    import re
    g = _graph()
    rec = ROOT / g["ws3"]["target"]["restatedBy"]
    quoted = " ".join(l[1:].strip() for l in rec.read_text(encoding="utf-8").splitlines() if l.startswith(">"))
    m = re.search(r"lines (\d+)[–-](\d+) and (\d+)[–-](\d+)", quoted)
    a, b, c, d = map(int, m.groups())
    assert [[a, b], [c, d]] == g["ws3"]["target"]["regionLines"]
    assert ("sha256:" + re.search(r"sha256 ([0-9a-f]{64})", quoted).group(1)) == g["source"]["digest"] == DIGEST
