# SPDX-License-Identifier: Apache-2.0
"""What this repository may publish, decided before it publishes.

The load-bearing test here is the last one, and it currently fails. That
is not a broken check: the repository redistributes a paid ISO standard
from a public URL while its README says it does not. The test is how that
stops being something somebody has to remember.
"""

from __future__ import annotations

import subprocess


def test_every_tracked_file_has_exactly_one_disposition(disposition):
    """`classify` refuses rather than guessing, so reaching this point at
    all is most of the assertion."""
    rows = disposition.classify()
    assert rows, "nothing was classified"
    paths = [row.path for row in rows]
    assert len(paths) == len(set(paths)), "a file was classified twice"

    tracked = subprocess.run(
        ["git", "ls-files"], cwd=str(disposition.layout.repository_root()),
        capture_output=True, text=True).stdout.splitlines()
    assert set(paths) == {p for p in tracked if p}, (
        "classified set and tracked set differ: "
        + str(sorted(set(paths) ^ {p for p in tracked if p})[:8]))


def test_the_project_licence_is_read_not_assumed(disposition):
    """A hardcoded licence map would assert terms the repository does not
    declare -- the same error as a README describing a policy its own
    contents contradict."""
    assert disposition.project_licence() == "MIT", (
        "LICENSE no longer says MIT; every project-authored file is "
        "reported as carrying whatever it says, so this is a deliberate "
        "change rather than a passing detail")


def test_an_ambiguous_licence_file_is_refused(disposition, monkeypatch):
    """Falsifies the reader: naming two licences must refuse, not pick."""
    import pytest

    class Fake:
        @staticmethod
        def read_text(encoding=None):
            return "MIT License ... Apache License ..."

    class FakeComponent:
        @staticmethod
        def resolve():
            return Fake()

    monkeypatch.setattr(disposition.layout, "component",
                        lambda _id: FakeComponent())
    disposition.project_licence.__wrapped__ if hasattr(
        disposition.project_licence, "__wrapped__") else None
    with pytest.raises(SystemExit) as error:
        disposition.project_licence()
    assert "Exactly one is required" in str(error.value)


def test_an_adjudication_matching_no_file_is_refused(disposition,
                                                     monkeypatch):
    """An exception granted for nothing reads as coverage."""
    import pytest

    monkeypatch.setattr(disposition, "adjudications", lambda: {
        "docs/no-such-file.md": {
            "path": "docs/no-such-file.md",
            "disposition": disposition.CONTENT,
            "why": "invented for this test",
            "decided": "2026-09-10",
            "decided_by": "test",
        }})
    with pytest.raises(SystemExit) as error:
        disposition.classify()
    assert "naming no tracked file" in str(error.value)


def test_reference_material_is_classified_as_not_redistributable(
        disposition):
    """The role exists so this is derived rather than remembered."""
    rows = {row.path: row for row in disposition.classify()}
    references = [row for row in rows.values()
                  if row.disposition == disposition.CITED]
    assert references, (
        "nothing is classified as third-party-cited, so either the "
        "reference material left the repository or the role stopped "
        "carrying its consequence")
    for row in references:
        assert row.redistributable is False, row
        assert row.licence is None, (
            "%s reports a licence; this repository grants no rights over "
            "it" % row.path)


def test_nothing_unpublishable_is_tracked(disposition):
    """The finding this repository currently has.

    ISO/IEC/IEEE 29148:2018 is a paid standard. It is committed here and
    served from a public GitHub URL, while README.md states that this
    repository does not redistribute it. One of those has to change, and
    it is not the standard's licence.

    Removing the files from the working tree is not enough on its own:
    they remain fetchable from the commit that added them, so the fix
    also has to rewrite that commit and force-push. That is the owner's
    call, which is why this is a failing test rather than an edit
    somebody made unilaterally.
    """
    rows = disposition.classify()
    unpublishable = [row.path for row in rows if not row.redistributable]
    assert not unpublishable, (
        "%d file(s) this repository may not redistribute are committed, "
        "and are therefore published wherever it is:\n    %s\n\n"
        "Cite them in README.md instead. Removing them needs a history "
        "rewrite, because they stay fetchable from the commit that added "
        "them."
        % (len(unpublishable), "\n    ".join(unpublishable)))
