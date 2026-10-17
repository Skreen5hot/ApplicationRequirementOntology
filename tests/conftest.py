# SPDX-License-Identifier: Apache-2.0
"""Shared fixtures, and the import path for the tools.

`tools/` is not an installed package on purpose. It is a directory of
scripts that the tests import directly, so there is no build step between
writing a tool and testing the tool that ships.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def load_tool(name: str, relative: str):
    """Import a tool by path, so tests exercise the file that ships."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def repo() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def layout():
    import layout as module

    return module


@pytest.fixture(scope="session")
def disposition():
    return load_tool("aro_disposition", "tools/licensing/disposition.py")


# SOURCE BINDINGS -- one owner for the whole suite (IA Ops finding 2026-10-17, "the fixed gates tear down the
# verifier's binding and assert the sibling override is absent", Shape B). A verifier runs this suite with its own
# ARO_SOURCE_DOC_<8 hex> overrides set; a gate may READ them, must never ASSERT them, and must leave them as it found
# them. Tests change a binding only through `bound_source` (monkeypatch underneath, so every change is undone at
# teardown), and test_env_bindings.py refuses any other write to os.environ in a test module.
SOURCE_ENV = "ARO_SOURCE_DOC"


def _source_bindings():
    return {k: v for k, v in os.environ.items() if k == SOURCE_ENV or k.startswith(SOURCE_ENV + "_")}


class SourceBinder:
    def __init__(self, mp):
        self._mp = mp

    @staticmethod
    def key(digest: str) -> str:
        return "%s_%s" % (SOURCE_ENV, digest.split(":")[-1][:8].upper())

    def bind(self, digest: str, path) -> None:
        self._mp.setenv(self.key(digest), str(path))

    def unbind(self, digest: str) -> None:
        self._mp.delenv(self.key(digest), raising=False)

    def unbind_global(self) -> None:
        self._mp.delenv(SOURCE_ENV, raising=False)


@pytest.fixture
def bound_source(monkeypatch) -> SourceBinder:
    return SourceBinder(monkeypatch)


# THE LEAK GUARD OWNS THE MOMENT IT LOOKS (IA Ops finding 2026-10-17, "the leak guard asserts the environment at a
# point in the teardown chain it does not control"). It was an autouse FIXTURE, so its check ran wherever pytest's
# reverse-setup order put it: under a parent conftest whose autouse fixture requests monkeypatch, monkeypatch was set
# up first and finalised LAST, so the guard looked before bound_source's restore and indicted the honest binder (and
# missed a raw pop, which monkeypatch then repaired). Now the snapshot is taken before ANY fixture is set up and
# compared after EVERY finaliser has run, by wrapping the setup and teardown hooks themselves. An exception raised
# after the teardown hook is reported by pytest as that test's teardown ERROR -- by name, as before.
_BEFORE = pytest.StashKey[dict]()


@pytest.hookimpl(wrapper=True)
def pytest_runtest_setup(item):
    item.stash[_BEFORE] = _source_bindings()
    return (yield)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_teardown(item, nextitem):
    result = yield
    before, after = item.stash.get(_BEFORE, None), _source_bindings()
    if before is not None and after != before:
        raise AssertionError("this test changed the runner's source bindings: before %r, after %r" % (before, after))
    return result
