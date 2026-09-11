"""FX-SEAM-A and FX-SEAM-B -- the Phase-1.5 spike fixtures, authored RED.

ARO v0.5.2 sections 13 and 16; SPIKE.md section 2. The fixture data lives under
examples/fx-seam-a and examples/fx-seam-b; the checks are test-assembled here, so
there is no production disable surface (ARO 13, the uniqueness rule).

RED is encoded as a STRICT expected failure. Each red test runs and must fail; the
moment one passes without its marker being removed deliberately, the suite goes red.
That is not a skip -- PROCESS.md 9: a skip is a pass in disguise -- and pytest
reports each as `x`, visibly. Leaving them plainly failing instead would keep CI red
until Phase 5 and teach everyone to stop reading it.

The guards beside them are GREEN on purpose. They prove the fixture data exhibits
the class it claims to (ARO 0: a check must verify its own precondition), so that
when the red tests turn green at Phase 5 it is because projection fixed the seam,
not because the fixture never had teeth.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from conftest import load_tool

ROOT = Path(__file__).resolve().parents[1]
FX_A = ROOT / "examples" / "fx-seam-a"
FX_B = ROOT / "examples" / "fx-seam-b"

RED_A = ("FX-SEAM-A is RED by design at Phase 1.5: no projection compiler "
         "(layout component tool.aro-project) exists; ARO v0.5.2 section 16 "
         "Phase 5 turns it green")
RED_B = ("FX-SEAM-B is RED by design and ARO alone cannot turn it green: it needs "
         "the loop's seam gate consuming the projected `declared` tier (INT-2; "
         "ARO v0.5.2 sections 11.3 and 13), declared as integration.loop-seam-gate")


def _load(path: Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


_STEP = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def resolve(doc, path: str):
    """`units[0].declarations[1].name` -> the value. Raises on a wrong path, so a
    seam index pointing at nothing fails loudly rather than reading as agreement."""
    cur = doc
    for key, idx in _STEP.findall(path):
        cur = cur[int(idx)] if idx else cur[key]
    return cur


def seam_names(documents: dict, index: dict) -> dict:
    """{seam id: {document name: the name that document uses}}."""
    out = {}
    for seam in index["seams"]:
        out[seam["id"]] = {doc: resolve(documents[doc], path)
                           for doc, path in seam["statedAt"].items()}
    return out


def divergent(names_by_seam: dict) -> dict:
    return {seam: sorted(set(names.values()))
            for seam, names in names_by_seam.items()
            if len(set(names.values())) > 1}


def _component_or_fail(layout, component_id: str, why: str):
    try:
        return layout.component(component_id)
    except layout.LayoutError:
        pytest.fail(why)


# ------------------------------------------------------------ FX-SEAM-A


def _fx_a():
    index = _load(FX_A / "seams.json")
    documents = {name: _load(FX_A / rel) for name, rel in index["documents"].items()}
    return index, documents


def test_fx_seam_a_exhibits_the_ia_names_class():
    """The precondition guard: the founding inputs really do carry divergent
    names for the same seams, and agree on the control seam."""
    index, documents = _fx_a()
    expected = _load(FX_A / "expected.json")["onTheseFoundingInputs"]
    names = seam_names(documents, index)

    assert len(names) >= 4, names
    for seam, by_doc in names.items():
        assert len(by_doc) == 4, (seam, by_doc)
        for doc, name in by_doc.items():
            assert isinstance(name, str) and name, (seam, doc, name)

    assert divergent(names) == expected["divergentSeams"]
    agreeing = sorted(s for s in names if s not in divergent(names))
    assert agreeing == expected["agreeingSeams"], agreeing

    assert expected["projectionInputManifestPresent"] is False
    for doc, body in documents.items():
        assert body.get("projectionInputManifest") is None, (
            "%s carries a Projection Input Manifest, so it was not independently "
            "derived and this fixture no longer reproduces the class" % doc)


def test_fx_seam_a_the_check_discriminates():
    """Falsifies the detector: reconcile the divergent names in memory and it
    must report nothing. A detector that flagged everything would pass the
    guard above for the wrong reason."""
    index, documents = _fx_a()
    names = seam_names(documents, index)
    before = divergent(names)
    assert before, "nothing diverged, so there is nothing to reconcile"

    reconciled = {seam: {doc: sorted(by_doc.values())[0] for doc in by_doc}
                  for seam, by_doc in names.items()}
    assert reconciled != names, "the mutation did not apply"
    assert divergent(reconciled) == {}


@pytest.mark.xfail(strict=True, reason=RED_A)
def test_fx_seam_a_single_graph_projection_makes_the_founding_inputs_agree(layout):
    """The red half. Green requires a projector that emits all four founding
    inputs from one graph via one Projection Input Manifest."""
    entry = _component_or_fail(layout, "tool.aro-project", RED_A)
    projector = load_tool("aro_project", entry.path)
    index, _ = _fx_a()

    outputs = projector.project_founding_inputs(ROOT / "spike" / "graph")
    assert set(outputs) == set(index["documents"]), set(outputs)
    assert divergent(seam_names(outputs, index)) == {}

    digests = {doc: body.get("projectionInputManifestDigest") for doc, body in outputs.items()}
    assert all(digests.values()), digests
    assert len(set(digests.values())) == 1, digests


@pytest.mark.xfail(strict=True, reason=RED_A)
def test_fx_seam_a_disabling_single_source_projection_reintroduces_the_divergence(layout):
    """The uniqueness rule (ARO 13): with single-source projection disabled --
    test-assembled independent derivation only -- the mismatch reappears."""
    entry = _component_or_fail(layout, "tool.aro-project", RED_A)
    projector = load_tool("aro_project", entry.path)
    index, _ = _fx_a()

    outputs = projector.project_founding_inputs(ROOT / "spike" / "graph",
                                                independent_derivation=True)
    assert divergent(seam_names(outputs, index)), (
        "independent derivation produced agreeing inputs, so this fixture is "
        "not exercising the mechanism it claims to guard")


# ------------------------------------------------------------ FX-SEAM-B


def built_vs_projected(projected: dict, built: dict):
    """Every symbol a built consumer imports from the projected module must be
    among the projected exports -> (violations, clean consumers)."""
    module = projected["module"]
    exports = sorted(e["name"] for e in projected["exports"])
    violations, clean = [], []
    for consumer, body in sorted(built["modules"].items()):
        imports = [i for i in body.get("imports", []) if i["module"] == module]
        bad = [i for i in imports if i["symbol"] not in exports]
        violations.extend({"consumer": consumer, "module": module,
                           "symbol": i["symbol"], "projectedExports": exports}
                          for i in bad)
        if imports and not bad:
            clean.append(consumer)
    return violations, clean


def test_fx_seam_b_exhibits_the_ia_cseam_class():
    """The precondition guard: the built manifest imports a member the projected
    contract does not export, and the control consumer is left alone."""
    projected = _load(FX_B / "projected" / "declared-contract.json")
    built = _load(FX_B / "built" / "manifest.json")
    expected = _load(FX_B / "expected.json")["onTheseInputs"]

    assert projected["tier"] == "declared"
    assert len(projected["exports"]) >= 3
    violations, clean = built_vs_projected(projected, built)
    assert violations == expected["violations"], violations
    assert clean == expected["cleanConsumers"], clean


def test_fx_seam_b_the_check_discriminates():
    """Falsifies the detector: rename the offending import to a projected export
    and the violation must vanish while the control stays clean."""
    projected = _load(FX_B / "projected" / "declared-contract.json")
    built = _load(FX_B / "built" / "manifest.json")
    offending = built["modules"]["author-agent"]["imports"][0]
    assert offending["symbol"] == "getFindings", offending
    offending["symbol"] = "listFindings"
    violations, clean = built_vs_projected(projected, built)
    assert violations == [], violations
    assert clean == ["author-agent"], clean


@pytest.mark.xfail(strict=True, reason=RED_B)
def test_fx_seam_b_the_loop_seam_gate_consumes_the_projected_declared_tier(layout):
    """The red half, and the joint one: the loop's own seam gate, fed the
    projected `declared` contract, must report exactly the expected violation.
    Nothing in this repository can supply that gate; INT-2 must land first."""
    entry = _component_or_fail(layout, "integration.loop-seam-gate", RED_B)
    gate = load_tool("aro_loop_seam_gate", entry.path)

    projected = _load(FX_B / "projected" / "declared-contract.json")
    assert projected["projectionInputManifestDigest"], (
        "the projected tier is still the hand-authored stand-in; nothing has "
        "been projected")
    built = _load(FX_B / "built" / "manifest.json")
    expected = _load(FX_B / "expected.json")["onTheseInputs"]
    assert gate.seam_failures(projected, built) == expected["violations"]
