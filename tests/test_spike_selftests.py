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
