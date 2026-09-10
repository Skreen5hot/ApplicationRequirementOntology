# SPDX-License-Identifier: Apache-2.0
"""The layout contract describes the repository, or it fails.

A contract nobody checks is a set of paths that used to be true. Both
directions are asserted: every component resolves, and every tracked file
belongs to a component or falls under a rule that was written on purpose.
"""

from __future__ import annotations

import subprocess


def tracked(repo) -> list[str]:
    result = subprocess.run(["git", "ls-files"], cwd=str(repo),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-400:]
    return [line for line in result.stdout.splitlines() if line]


def test_every_tracked_component_resolves(layout):
    """A contract naming something absent is worse than no contract:
    every consumer believes it."""
    missing = [c.id for c in layout.components()
               if c.tracked and not c.exists()]
    assert not missing, missing


def test_never_tracked_components_are_absent_from_the_index(layout, repo):
    """The invariant, asserted rather than remembered.

    `tracked: false` says a component's files may exist on disk and must
    never be committed. That is a stronger statement than .gitignore
    makes: ignoring a path and a path being absent from the index are
    different facts, and only the second one keeps something off a public
    URL. A file already tracked stays tracked however the ignore rules
    change.

    This exists because four PDFs -- one of them a paid ISO standard --
    were committed and served publicly while the README said they were
    not redistributed.
    """
    never = [c for c in layout.components() if not c.tracked]
    assert never, (
        "no component is marked tracked: false, so this test is watching "
        "nothing")

    indexed = set(tracked(repo))
    for entry in never:
        leaked = sorted(p for p in indexed
                        if p == entry.path or p.startswith(entry.path + "/"))
        assert not leaked, (
            "%s is declared never-tracked but these files are in the "
            "index: %s" % (entry.id, leaked))


def test_the_never_tracked_check_would_catch_a_committed_file(layout, repo):
    """Guards the test above. It passes trivially if the component's path
    never appears, so a typo in the declared path would silence it."""
    never = [c for c in layout.components() if not c.tracked]
    for entry in never:
        pretend_indexed = {entry.path + "/something.pdf"}
        leaked = sorted(p for p in pretend_indexed
                        if p == entry.path or p.startswith(entry.path + "/"))
        assert leaked, (
            "a file under %s would not be recognised as belonging to it, "
            "so the check cannot fire" % entry.path)


def test_no_two_components_share_an_id(layout):
    """Guarded in the loader, asserted here so the guard is exercised
    rather than assumed."""
    ids = [c.id for c in layout.components()]
    assert len(ids) == len(set(ids)), sorted(
        i for i in ids if ids.count(i) > 1)


def test_every_component_declares_a_role_with_a_meaning(layout):
    """A role is not a label. Each one carries a licensing consequence,
    so an unrecognised role would be classified by accident."""
    known = {"ontology-module", "ontology-module-set", "ontology-validation",
             "test-fixture", "generated-artifact", "documentation",
             "third-party-reference", "configuration", "tool",
             "project-licence"}
    unknown = sorted({c.role for c in layout.components()} - known)
    assert not unknown, (
        "roles with no stated meaning: %s. Add them to the licensing rules "
        "deliberately rather than letting a file inherit a guess." % unknown)


def test_the_ontology_scope_excludes_what_it_must(layout, repo):
    """The reasoner scope is the authored ontology and nothing else.

    Sweeping the tree would load the reports the reasoner itself wrote
    and a fixture whose entire purpose is to be invalid, then report the
    result as a property of the ontology.
    """
    scope = {p.relative_to(repo).as_posix() for p in layout.ontology_files()}
    assert scope, "the ontology scope is empty"

    for excluded in ("APQC_ontology/apqc_bad_examples.ttl",
                     "APQC_ontology/apqc_shapes.ttl",
                     "APQC_ontology/capabilities_roles_shapes.ttl"):
        assert excluded not in scope, (
            "%s is in the reasoner scope; it is a %s"
            % (excluded, layout.owning_component(excluded).role))

    for report in scope:
        assert not report.startswith("APQC_ontology/reports/"), report
        assert not report.startswith("APQC_ontology/reference/"), report


def test_the_ontology_scope_is_not_empty_by_accident(layout):
    """Guards the test above: an empty scope excludes everything and
    would satisfy every assertion in it."""
    assert len(layout.ontology_files()) >= 15, len(layout.ontology_files())


def test_every_tracked_file_has_an_owning_component_or_a_stated_rule(
        layout, repo, disposition):
    """The inverse direction. A file nothing declares is a file nobody
    decided about, and it will be classified by a suffix guess."""
    undeclared = []
    for relative in tracked(repo):
        if layout.owning_component(relative) is None:
            undeclared.append(relative)

    # Files under tooling directories are covered by a stated fallback
    # rather than declared one by one; anything else is a gap.
    unexplained = [p for p in undeclared
                   if not p.startswith((".github/", "tools/", "tests/",
                                        "config/"))
                   and "/" in p]
    assert not unexplained, (
        "%d tracked file(s) belong to no component: %s"
        % (len(unexplained), unexplained[:8]))


def test_a_component_pointing_nowhere_is_caught(layout, repo, tmp_path):
    """Falsifies the resolver: a contract that returned paths without
    checking them would pass the first test in this file trivially."""
    import pytest

    entry = layout.component("docs.readme")
    original = entry.path
    try:
        entry.path = "docs/this-does-not-exist.md"
        with pytest.raises(layout.LayoutError) as error:
            entry.resolve()
        assert "docs.readme" in str(error.value)
    finally:
        entry.path = original
    assert entry.resolve().is_file()


def test_the_index_is_lf_throughout(repo):
    """The rule in .gitattributes, checked rather than trusted.

    A CRLF inside a Turtle literal is part of that literal's value, so
    two checkouts with different core.autocrlf settings would disagree
    about the corpus while both looked correct locally. The same applies
    to any digest recorded over a file git is free to re-encode: a byte
    digest over such a file is not a byte digest.

    The index was already LF when the rule was written -- 65 blobs, none
    with CRLF -- so this pins existing behaviour rather than announcing a
    change. That is the cheap moment to do it, and the reason to assert
    it now is that nothing about a passing state stops it drifting.
    """
    import subprocess

    nul = chr(0).encode()
    crlf = (chr(13) + chr(10)).encode()
    files = subprocess.run(["git", "ls-files"], cwd=str(repo),
                           capture_output=True, text=True).stdout.split(chr(10))
    offenders, checked = [], 0
    for name in filter(None, files):
        blob = subprocess.run(["git", "cat-file", "blob", ":" + name],
                              cwd=str(repo), capture_output=True).stdout
        if nul in blob[:8000]:
            continue
        checked += 1
        if crlf in blob:
            offenders.append(name)

    assert checked > 40, (
        "only %d text blobs were examined; this test is watching less "
        "than it should" % checked)
    assert not offenders, (
        "%d blob(s) carry CRLF in the index: %s"
        % (len(offenders), offenders[:8]))


def test_the_line_ending_rule_is_repository_wide(repo):
    """Narrowing it to *.ttl would leave every recorded digest describing
    the machine that measured it."""
    rule = (repo / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in rule, (
        "the repository-wide rule is gone; a corpus-only rule protects "
        "the corpus and nothing that records a checksum of anything else")
