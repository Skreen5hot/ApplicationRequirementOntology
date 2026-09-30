# SPDX-License-Identifier: Apache-2.0
"""The projector's and the layout rule's self-tests, run by the suite (IA OPS finding 2026-09-30).

Both self-tests are real, falsified checks -- including A4's "plan files are deliverables only; test paths
travel in the Tester Contract" -- but nothing in CI executed them, so reverting the rule landed green. They run
here as subprocesses, exactly as a person runs them, so the pin is the shipped command and nothing else.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("script", ["spike/graph/rules/layout_rule.py", "spike/projections/project.py"])
def test_selftest_passes(script):
    run = subprocess.run([sys.executable, str(ROOT / script), "--selftest"], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    assert run.returncode == 0 and "all checks passed" in run.stdout, run.stdout[-2000:] + run.stderr[-2000:]


def test_ratifying_the_finding_field_types_projects_typed_fields():
    """A6 (F6 remedy a): once rq-014 is acted on, `Finding` is projected with {name, type} fields carrying the L3
    ratification reference -- the shape the factory's F6 rule reads as ENFORCEABLE. Before the act, refused."""
    import importlib.util, json
    spec = importlib.util.spec_from_file_location("spike_projector_a6", ROOT / "spike/projections/project.py")
    project = importlib.util.module_from_spec(spec); spec.loader.exec_module(project)
    l2, l3, convention, fragments, queue = project.load_real()
    if not any(r.get("record") == "sr:L3:Finding-field-types" for r in queue):
        pytest.skip("rq-014 not queued in this tree")
    kw = dict(verify_fragments=None, convention_artifact="spike/graph/l3/convention-closure.candidate.json",
              rule_artifact="spike/graph/rules/layout_rule.py",
              rule_digest=project.file_digest(ROOT / "spike/graph/rules/layout_rule.py"))
    unacted = [r for r in queue if r.get("record") == "sr:L3:Finding-field-types" and not r.get("actedAt")]
    if unacted:
        with pytest.raises(project.Refused):
            project.project(l2, l3, convention, fragments, queue, **kw)
    acted = [dict(r, actedAt="2026-09-30T12:00:00-04:00", act="ratified", actor="Aaron")
             if r.get("record") == "sr:L3:Finding-field-types" else r for r in queue]
    out = project.project(l2, l3, convention, fragments, acted, **kw)
    finding = [e for e in out["declared"]["contract"]["exports"] if e["name"] == "Finding"][0]
    assert finding["record"] == "sr:L3:Finding-field-types" and finding["layer"] == "L3"
    types = {f["name"]: f["type"] for f in finding["shape"]["fields"]}
    assert set(types) == {"id", "source", "severity", "clause", "text", "replay"} and all(types.values()), types
