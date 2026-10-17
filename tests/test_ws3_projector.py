"""The WS-3 projector (IA plan D-8 part 2b). Every test SEEDS its queue -- a copy of the real rows with the WS3-5 acts
stripped or applied here -- and never takes the live queue's state as its expected value (Ops HIGH finding
2026-10-17, "the gates that hold the act read the queue's current state"). The acts applied below are SEEDED, by a
seeded actor; they are not the architect's and never reach the queue file."""
import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ws3_projector", ROOT / "spike" / "projections" / "ws3" / "project.py")
P = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

WS35 = [i["file"] for i in P.ITEMS]
SEEDED = "Seeded Architect"


def _strip(r):
    for k in ("actedAt", "act", "actor", "actDigest", "decision", "actNote", "sittingStart"):
        r.pop(k, None)
    return r


def seeded(homes=None, actor=SEEDED, files_override=None, act="ratified"):
    """(l2, l3, fragments, rows, files) with the WS3-5 rows UNACTED, then acted here if `homes` is given."""
    l2, l3, fragments, rows, files = P.load_real()
    files = dict(files, **(files_override or {}))
    dead = {r.get("supersedes") for r in rows if r.get("supersedes")}
    rows = copy.deepcopy(rows)
    targets = [r for r in rows if r["id"] not in dead and (r.get("record") == P.HOMES or r.get("artifact") in WS35)]
    assert len(targets) == 7, "seeded %d rows (WS3-5: rq-067..rq-072 and the module-homes adjudication)" % len(targets)
    for r in targets:
        _strip(r)
        if homes is None:
            continue
        if r.get("artifact") in WS35:
            r["artifactFileDigest"] = P.file_digest(files[r["artifact"]])    # an override is a NEW content address
        r.update(actedAt="2026-10-20T10:00:00-04:00", actor=actor,
                 act="decided" if r.get("record") == P.HOMES else act,
                 actDigest=r.get("recordDigest") or r.get("artifactFileDigest"))
        if r.get("record") == P.HOMES:
            r["decision"] = homes
    return l2, l3, fragments, rows, files


def run(*a, **k):
    l2, l3, fragments, rows, files = seeded(*a, **k)
    return P.project(l2, l3, fragments, rows, files)


def test_unacted_it_refuses_and_lists_exactly_the_ws3_5_items():
    with pytest.raises(P.Refused) as e:
        run()
    awaiting = e.value.awaiting
    assert len(awaiting) == 7, awaiting
    assert sum(P.HOMES in w for w in awaiting) == 1 and all(any(f in w for w in awaiting) for f in WS35)


def test_decided_A_it_projects_deterministically_with_capabilities_and_oracles():
    out, again = run("A"), run("A")
    assert out == again, "two projections of the same inputs differ"
    plan = json.loads(out["plan.json"])
    assert {u["id"]: u["files"] for u in plan["units"]} == {
        "adjudicator": ["src/adjudicator.ts"], "grader-runner": ["src/grader-runner.ts"],
        "grading-types": ["src/grading-types.ts"], "ledger": ["src/ledger.ts"]}
    assert {u["id"]: u["depends_on"] for u in plan["units"]}["adjudicator"] == ["grading-types"]
    assert [(c["capability"], c["path"], c["modules"]) for c in plan["capabilities"]] == [
        ("C-S2", "grade", ["grader-runner"]), ("C-S3", "adjudicate", ["adjudicator"]), ("C-S7", "register", ["ledger"])]
    assert [(o["capability"], o["acceptance_test"]) for o in plan["oracles"]] == [
        ("C-S3", "test/acceptance/C-S3.test.mjs"), ("C-S7", "test/acceptance/C-S7.test.mjs")]
    for o in plan["oracles"]:
        assert o["ratified_by"] == "%s via %s (%s)" % (SEEDED, o["actRef"]["queueRow"], o["actRef"]["actDigest"])
        assert o["actRef"]["bound"] == o["sha256"]
    assert plan["provisional"] and plan["provisional"][0].startswith("C-S2 (grade): no ratified bar or oracle")
    assert sorted(d["module"] for d in plan["departures"]) == ["adjudicator", "grader-runner", "ledger"]


def test_the_bundle_carries_the_ratified_bytes_and_the_act_beside_each():
    out = run("A")
    _, _, _, _, files = P.load_real()
    std_dir = next(k for k in out if k.endswith("/standards.json")).rsplit("/", 1)[0]
    assert std_dir == "oracles/109e1b502684"
    std = json.loads(out[std_dir + "/standards.json"])
    assert std["schema"] == "coord-standards/1"
    assert [(s["module"], s["provisional"], s["source"]) for s in std["standards"]] == [
        ("adjudicator", False, "spec"), ("ledger", False, "spec")]
    for s in std["standards"]:
        src = next(i["file"] for i in P.ITEMS if i.get("unit") == s["module"])
        assert out["%s/%s.test.mjs" % (std_dir, s["module"])] == files[src]
        assert s["sha256"] == P.file_digest(files[src]) == s["actRef"]["bound"]
    md = json.loads(out["plan.json"])["projectionInputManifestDigest"]
    assert md == std["projectionInputManifestDigest"] == json.loads(out["nonbuilt/manifest.json"])["projectionInputManifestDigest"]


def test_the_hook_travels_only_in_the_non_built_channel():
    out = run("A")
    nb = json.loads(out["nonbuilt/manifest.json"])["deliverables"]
    assert sorted(d["path"] for d in nb) == [".githooks/check-ledger.mjs", ".githooks/pre-commit"]
    planned = {f for u in json.loads(out["plan.json"])["units"] for f in u["files"]}
    assert not any(".githooks" in f for f in planned)
    assert all(("nonbuilt/" + d["path"]) in out for d in nb)


def test_decided_B_refuses_until_the_bar_and_oracle_import_the_decided_homes():
    with pytest.raises(P.Refused) as e:
        run("B")
    assert len(e.value.awaiting) == 2, e.value.awaiting
    assert any("bars/adjudicator.test.mjs" in w for w in e.value.awaiting)
    assert any("acceptance/C-S3.test.mjs" in w for w in e.value.awaiting)


def test_decided_B_with_rewritten_tests_projects_and_only_the_ledger_departs():
    _, _, _, _, files = P.load_real()
    bar, oracle = "spike/projections/ws3/bars/adjudicator.test.mjs", "spike/projections/ws3/acceptance/C-S3.test.mjs"
    rewritten = {bar: files[bar].replace(b"'../src/adjudicator.ts'", b"'../tools/adjudicator/adjudicator.ts'"),
                 oracle: files[oracle].replace(b"'../../src/adjudicator.ts'", b"'../../tools/adjudicator/adjudicator.ts'")}
    assert all(rewritten[k] != files[k] for k in rewritten)
    plan = json.loads(run("B", files_override=rewritten)["plan.json"])
    assert {u["id"]: u["files"] for u in plan["units"]}["adjudicator"] == ["tools/adjudicator/adjudicator.ts"]
    assert [d["module"] for d in plan["departures"]] == ["ledger"]


def test_a_hook_script_loading_an_unbuilt_module_refuses():
    _, _, _, _, files = P.load_real()
    hook = "spike/projections/ws3/nonbuilt/.githooks/check-ledger.mjs"
    moved = {hook: files[hook].replace(b"'src', 'ledger.ts'", b"'src', 'ledger-v2.ts'")}
    assert moved[hook] != files[hook]
    with pytest.raises(P.Refused) as e:
        run("A", files_override=moved)
    assert e.value.awaiting == ["%s imports ['src/ledger-v2.ts']; the plan builds []" % hook]


def test_a_decision_placing_a_hook_among_the_built_files_refuses():
    """rq-035 condition 2: the wrapper is NEVER in plan.json files. Seeded: option A's files put grading-types at the
    hook's path, and the seeded act is re-bound to that changed record (else the act check would refuse first)."""
    l2, l3, fragments, rows, files = seeded("A")
    l3 = copy.deepcopy(l3)
    adj = next(a for a in l3["adjudications"] if a["@id"] == P.HOMES)
    next(o for o in adj["options"] if o["id"] == "A")["files"]["grading-types"] = ".githooks/check-ledger.mjs"
    row = next(r for r in rows if r.get("record") == P.HOMES and r.get("actedAt"))
    row["recordDigest"] = row["actDigest"] = P.digest(adj)
    with pytest.raises(P.Refused, match="non-built deliverable is in plan.json files"):
        P.project(l2, l3, fragments, rows, files)


def test_decided_C_refuses_awaiting_the_source_amendment():
    with pytest.raises(P.Refused, match="awaiting the source amendment"):
        run("C")


def test_an_agent_act_voids_rather_than_projects():
    with pytest.raises(P.Refused, match="simulated a ratification act"):
        run("A", actor="claude")


def test_an_amend_is_not_a_ratification():
    with pytest.raises(P.Refused) as e:
        run("A", act="amended")
    assert len([w for w in e.value.awaiting if "no act yet" in w]) == 6, e.value.awaiting


def test_bytes_changed_after_the_act_need_a_new_act():
    l2, l3, fragments, rows, files = seeded("A")
    bar = "spike/projections/ws3/bars/ledger.test.mjs"
    files = dict(files, **{bar: files[bar] + b"\n// edited after the act\n"})
    with pytest.raises(P.Refused) as e:
        P.project(l2, l3, fragments, rows, files)
    assert [w for w in e.value.awaiting if "different content address" in w] and len(e.value.awaiting) == 1


def test_an_open_blocking_diagnostic_refuses(monkeypatch):
    diags = copy.deepcopy(P.build_l2.DIAGNOSTICS)
    d = next(x for x in diags if x["@id"] == "diag:external-method-artifacts")
    d["blocking"] = True
    monkeypatch.setattr(P.build_l2, "DIAGNOSTICS", diags)
    with pytest.raises(P.Refused) as e:
        run("A")
    assert e.value.awaiting == ["diag:external-method-artifacts is OPEN and BLOCKING"]


def test_the_control_may_not_carry_a_ratified_bar():
    l2, l3, fragments, rows, files = seeded("A")
    l2 = copy.deepcopy(l2)
    l2["ws3"]["demonstrationControlCandidate"]["capability"] = "C-S3"
    with pytest.raises(P.Refused, match="demonstration control C-S3 has a ratified bar"):
        P.project(l2, l3, fragments, rows, files)


def test_the_live_check_refuses_legibly_or_projects_never_crashes():
    """Whatever the live queue holds, --check exits 0 (projected, deterministic) or 3 (refused, with what it awaits)."""
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "spike/projections/ws3/project.py", "--check"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode in (0, 3), r.stdout + r.stderr
    assert ("REFUSED" in r.stdout and "awaiting:" in r.stdout) if r.returncode == 3 else "plan.json" in r.stdout
