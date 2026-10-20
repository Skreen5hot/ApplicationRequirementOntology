"""The FX-CAP executable checks (spike/projections/ws3/freeze2/fx_cap.py) on SEEDED inputs: each assertion holds on a
correct reading and is red, by its own message, on each way it can be false -- including the vacuous ones."""
import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ws3_fx_cap", ROOT / "spike" / "projections" / "ws3" / "freeze2" / "fx_cap.py")
FX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FX)
CONTROL = json.loads((ROOT / "spike" / "projections" / "ws3" / "freeze2" / "control-designation.json").read_text(encoding="utf-8"))

D_ADJ, D_LED = "sha256:" + "a" * 64, "sha256:" + "b" * 64
PLAN = {"capabilities": [{"capability": "C-S2", "path": "grade", "modules": ["grader-runner"]},
                         {"capability": "C-S3", "path": "adjudicate", "modules": ["adjudicator"]},
                         {"capability": "C-S7", "path": "register", "modules": ["ledger"]}]}
STANDARDS = {"standards": [
    {"module": "adjudicator", "provisional": False, "sha256": D_ADJ, "ratified_by": "Seeded via rq-901 (%s)" % D_ADJ, "actRef": {"queueRow": "rq-901"}},
    {"module": "ledger", "provisional": False, "sha256": D_LED, "ratified_by": "Seeded via rq-902 (%s)" % D_LED, "actRef": {"queueRow": "rq-902"}}]}
ROWS = [{"id": "rq-901", "act": "ratified", "artifactFileDigest": D_ADJ, "actDigest": D_ADJ},
        {"id": "rq-902", "act": "ratified", "artifactFileDigest": D_LED, "actDigest": D_LED}]
# the EMITTED shape of the OPS extension (ops-ledger-reader-1): status VERIFIED | BLOCKED, module states in `derived`
GOOD = {"reader": "ops-ledger-reader-1", "capabilities": {
    "C-S2": {"status": "BLOCKED", "derived": {"grader-runner": "built_unverified"},
             "reasons": ["grader-runner: oracle_gap (built_unverified)"],
             "barProvenance": [{"module": "grader-runner", "provisional": True, "ratified_by": None, "source": "model"}]},
    "C-S3": {"status": "VERIFIED", "derived": {"adjudicator": "verified"}, "reasons": [],
             "barProvenance": [{"module": "adjudicator", "provisional": False, "source": "spec", "ratified_by": STANDARDS["standards"][0]["ratified_by"]}]},
    "C-S7": {"status": "VERIFIED", "derived": {"ledger": "verified"}, "reasons": [],
             "barProvenance": [{"module": "ledger", "provisional": False, "source": "spec", "ratified_by": STANDARDS["standards"][1]["ratified_by"]}]}}}


def run(ext=GOOD, rows=ROWS, standards=STANDARDS):
    return FX.check(ext, PLAN, standards, rows, CONTROL)


def test_the_designation_names_c_s2_and_its_lifecycle():
    assert CONTROL["capability"] == "C-S2" and CONTROL["modules"] == ["grader-runner"]
    assert "ratified, or the capability is retired" in CONTROL["lifecycle"] and "before results" in CONTROL["what"].lower()


def test_both_assertions_hold_on_a_correct_reading():
    assert run() == []


def test_i_the_control_verifying_is_red():
    bad = copy.deepcopy(GOOD); bad["capabilities"]["C-S2"]["status"] = "VERIFIED"
    assert run(bad) == ["(i) the control C-S2 reads VERIFIED; a provisional-bar capability must never verify"]


def test_i_an_absent_control_is_red_not_vacuously_green():
    bad = copy.deepcopy(GOOD); del bad["capabilities"]["C-S2"]
    assert run(bad) == ["(i) the control C-S2 is absent from the extension's output -- an empty domain proves nothing"]


def test_ii_a_ratified_capability_not_verified_is_red():
    bad = copy.deepcopy(GOOD)
    bad["capabilities"]["C-S7"].update(status="BLOCKED", derived={"ledger": "stub"})
    assert run(bad) == ["(ii) C-S7 reads 'BLOCKED', not VERIFIED", "(ii) C-S7: module ledger derives 'stub', not verified"]


def test_i_a_control_blocked_for_the_wrong_reason_is_red():
    """BLOCKED is not enough: the control must be blocked BY its held bar (built_unverified), not by a stub,
    inherited debt, a provenance failure or absence -- each of those is a control that failed for another reason."""
    for wrong in ("stub", "inherited_debt", "authority_not_demonstrated", "absent", None):
        bad = copy.deepcopy(GOOD); bad["capabilities"]["C-S2"]["derived"] = {"grader-runner": wrong} if wrong else {}
        assert run(bad) == ["(i) the control C-S2: module grader-runner derives %r, not built_unverified (its held bar is "
                            "not what blocks it)" % wrong], wrong


def test_ii_a_broken_chain_is_red():
    rows = copy.deepcopy(ROWS); rows[0]["actDigest"] = "sha256:" + "c" * 64          # the act bound other bytes
    assert len(run(rows=rows)) == 1 and "chain is broken at queue row rq-901" in run(rows=rows)[0]
    amended = copy.deepcopy(ROWS); amended[1]["act"] = "amended"                       # an amend confers nothing
    assert "chain is broken at queue row rq-902" in run(rows=amended)[0]
    wrong = copy.deepcopy(GOOD); wrong["capabilities"]["C-S3"]["barProvenance"][0]["ratified_by"] = "someone else"
    assert "ratified_by 'someone else'" in run(wrong)[0]


def test_ii_with_no_ratified_bar_capability_is_red_not_vacuously_green():
    assert run(standards={"standards": []})[-1] == "(ii) no ratified-bar capability in the plan -- an empty domain proves nothing"


def test_i_the_control_must_read_exactly_blocked_not_merely_not_verified():
    """rq-088 (2026-10-20): the designation states the exact observable outcome; any status other than BLOCKED is red."""
    assert CONTROL["expectedObservation"]["capability"]["status"] == "BLOCKED"
    assert CONTROL["expectedObservation"]["modules"]["grader-runner"]["derived"] == "built_unverified"
    bad = copy.deepcopy(GOOD); bad["capabilities"]["C-S2"]["status"] = "PROVISIONAL"
    assert run(bad) == ["(i) the control C-S2 reads 'PROVISIONAL', not BLOCKED"]
