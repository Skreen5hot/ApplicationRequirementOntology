"""No test writes the runner's environment except through conftest's `bound_source` (IA Ops finding 2026-10-17, "the
fixed gates tear down the verifier's binding and assert the sibling override is absent", Shape B, bullet 6).

A verifier runs this suite with its own ARO_SOURCE_DOC_<8 hex> overrides. Three findings in a row were one class: the
gate's result was a function of whose account ran it. The last instance was a test that `pop`ped the verifier's
binding in its own `finally`, which reddened itself and every later test. Two mechanisms retire the class:

- this file refuses any direct write to `os.environ` (or monkeypatch's setenv/delenv) in a test module; and
- conftest's autouse guard turns any change to the source bindings that survives a test into an ERROR on THAT test.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TESTS = ROOT / "tests"

# `environ` under ANY spelling (os.environ, an aliased module, `from os import environ`) -- the mutation that first
# probed this gate wrote `_o.environ.pop(...)` and the os.-anchored pattern let it through.
WRITE = re.compile(r"\benviron\s*\[[^\]]*\]\s*=(?!=)"
                   r"|\benviron\s*\.\s*(?:pop|popitem|update|clear|setdefault)\s*\("
                   r"|\bdel\s+[\w.]*environ\b"
                   r"|\b(?:putenv|unsetenv)\s*\("
                   r"|\bmonkeypatch\.(?:setenv|delenv)\s*\(")


def env_writes(text: str) -> list[str]:
    """Every line of a test module that writes the process environment -> [line]."""
    return [l.strip() for l in text.splitlines() if WRITE.search(l)]


def test_no_test_module_writes_the_environment_outside_the_fixture():
    modules = sorted(p for p in TESTS.glob("*.py") if p.name != "conftest.py")
    offenders = {p.name: env_writes(p.read_text(encoding="utf-8")) for p in modules}
    offenders = {k: v for k, v in offenders.items() if v and k != Path(__file__).name}
    assert len(modules) >= 10, "examined %d modules" % len(modules)
    assert offenders == {}


@pytest.mark.parametrize("line", [
    'os.environ[key] = str(p)',
    'os.environ.pop(key, None)',
    'os.environ.update(env_before)',
    'os.environ.clear()',
    'os.environ.setdefault("ARO_SOURCE_DOC", "x")',
    'del os.environ["ARO_SOURCE_DOC"]',
    'os.putenv("ARO_SOURCE_DOC", "x")',
    'monkeypatch.setenv("ARO_SOURCE_DOC", "x")',
    'monkeypatch.delenv("ARO_SOURCE_DOC_109E1B50")',
    'import os as _o; _o.environ.pop(key, None)',
    'environ["ARO_SOURCE_DOC"] = "x"',
    'del _o.environ["ARO_SOURCE_DOC"]',
])
def test_each_form_of_write_is_caught(line):
    assert env_writes("    " + line + "\n") == [line]


@pytest.mark.parametrize("line", [
    'env = dict(os.environ)',
    'os.environ.get("ARO_SOURCE_DOC")',
    'assert os.environ["ARO_SOURCE_DOC"] == x',
    'env.pop("ARO_SOURCE_DOC", None)',
])
def test_reads_and_copies_are_not_writes(line):
    assert env_writes(line) == []


LEAK = '''
import os

def test_leaks(bound_source):
    os.environ.pop("ARO_SOURCE_DOC_109E1B50", None)     # the 51ec505 defect, re-introduced

def test_restores(bound_source):
    bound_source.unbind("sha256:109e1b50" + "0" * 56)
    bound_source.bind("sha256:2428b115" + "0" * 56, "elsewhere.md")
'''


OUTER_CONFTEST = '''
from pathlib import Path
import pytest

@pytest.fixture(autouse=True)
def _outer(monkeypatch):      # requests monkeypatch: set up BEFORE ARO's fixtures, so finalised AFTER them
    yield
    (Path(__file__).parent / "outer-fixture-ran").write_text("yes")
'''


@pytest.mark.parametrize("position", ["standalone", "nested"])
def test_the_conftest_guard_names_the_leaking_test_and_spares_the_restoring_one(tmp_path, position):
    """Falsified on demand: a test that pops the runner's binding errors BY NAME; one that changes bindings through
    the fixture passes. Run in a child pytest so the leak cannot reach this session -- and in BOTH positions Ops
    measured (finding 2026-10-17, "the leak guard asserts the environment at a point in the teardown chain it does not
    control"): standalone, and nested under a parent conftest whose autouse fixture requests monkeypatch. Before the
    guard moved into the setup/teardown hooks, the nested position inverted the verdict: the leaker passed and the
    honest binder errored."""
    top = tmp_path
    if position == "nested":
        (top / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
        (top / "conftest.py").write_text(OUTER_CONFTEST, encoding="utf-8")
        inner = top / "aro-checkout"
        inner.mkdir()
    else:
        inner = top
        (inner / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    shutil.copy(TESTS / "conftest.py", inner / "conftest.py")
    (inner / "test_leak.py").write_text(LEAK, encoding="utf-8")
    env = dict(os.environ)                  # a copy for the child
    env["ARO_SOURCE_DOC_109E1B50"] = "runner-binding.md"
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "no:randomly",
                        str(inner / "test_leak.py")], cwd=top, env=env, capture_output=True, text=True)
    if position == "nested":     # the precondition, verified: the outer monkeypatch-requesting fixture really ran
        assert (top / "outer-fixture-ran").is_file(), r.stdout
    out = r.stdout + r.stderr
    assert r.returncode != 0, out
    assert "ERROR at teardown of test_leaks" in out and "changed the runner's source bindings" in out, out
    assert "test_restores" not in out.split("short test summary")[-1], out
    assert re.search(r"\b2 passed, 1 error\b", out), out
