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
GOOD = {"capabilities": {
    "C-S2": {"status": "built_unverified", "barProvenance": [{"module": "grader-runner", "provisional": True, "source": "model"}]},
    "C-S3": {"status": "VERIFIED", "barProvenance": [{"module": "adjudicator", "provisional": False, "ratified_by": STANDARDS["standards"][0]["ratified_by"]}]},
    "C-S7": {"status": "VERIFIED", "barProvenance": [{"module": "ledger", "provisional": False, "ratified_by": STANDARDS["standards"][1]["ratified_by"]}]}}}


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
    bad = copy.deepcopy(GOOD); bad["capabilities"]["C-S7"]["status"] = "built_unverified"
    assert run(bad) == ["(ii) C-S7 reads 'built_unverified', not VERIFIED"]


def test_ii_a_broken_chain_is_red():
    rows = copy.deepcopy(ROWS); rows[0]["actDigest"] = "sha256:" + "c" * 64          # the act bound other bytes
    assert len(run(rows=rows)) == 1 and "chain is broken at queue row rq-901" in run(rows=rows)[0]
    amended = copy.deepcopy(ROWS); amended[1]["act"] = "amended"                       # an amend confers nothing
    assert "chain is broken at queue row rq-902" in run(rows=amended)[0]
    wrong = copy.deepcopy(GOOD); wrong["capabilities"]["C-S3"]["barProvenance"][0]["ratified_by"] = "someone else"
    assert "ratified_by 'someone else'" in run(wrong)[0]


def test_ii_with_no_ratified_bar_capability_is_red_not_vacuously_green():
    assert run(standards={"standards": []})[-1] == "(ii) no ratified-bar capability in the plan -- an empty domain proves nothing"
