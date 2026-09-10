# SPDX-License-Identifier: Apache-2.0
"""The corpus measures, and the honesty of the validation ladder.

Until BFO and CCO were vendored these tests asserted almost nothing about
whether the ontology is correct, because that could not be determined:
the shapes reason over both, and neither was in the repository. What they
asserted instead was that the tool said so, rather than reporting 213
violations that described a missing vocabulary and read exactly like
defects.

Both rungs are evaluable now, so the assertions have been inverted rather
than deleted -- the old ones are still visible in the git history, and
what they were guarding against is still what the new ones guard.

The findings that remain are findings. Five process classes are missing
ex:pcfID and five are missing skos:example; those are recorded here as
the number they are, so that fixing them is a visible change and adding
new ones is a failure.
"""

from __future__ import annotations

import pytest

from conftest import load_tool


@pytest.fixture(scope="module")
def digest_tool():
    return load_tool("aro_digest", "tools/ontology/corpus_digest.py")


@pytest.fixture(scope="module")
def digest(digest_tool):
    return digest_tool.measure()


@pytest.fixture(scope="module")
def validator():
    return load_tool("aro_validate", "tools/ontology/validate.py")


@pytest.fixture(scope="module")
def validation(validator):
    """Measured once.

    Each call runs every shape set against the whole corpus and against
    the fixture -- four SHACL passes over 62,000 triples. Three tests
    asking for it separately turned a one-second suite into one that
    outran a ten-minute timeout.
    """
    return validator.measure()


# ------------------------------------------------------------- digests


def test_the_two_measures_cover_every_triple(digest):
    """Ground triples and blank-node-touching triples partition the
    graph. If they did not, a change could land in the gap between them
    and move neither number."""
    merged = digest["merged"]
    assert (merged["ground_triples"] + merged["blank_nodes"]["triples_touching"]
            == merged["triples"]), merged


def test_the_corpus_is_not_empty(digest):
    """Guards every digest below: a digest of nothing is stable, and
    means nothing."""
    assert digest["merged"]["triples"] > 50000, digest["merged"]["triples"]
    assert digest["scope"]["files"] >= 18, digest["scope"]


def test_the_scope_is_the_authored_ontology(digest):
    """Not a directory walk. A walk would include the reasoner's own
    output and the fixture built to be invalid."""
    paths = digest["scope"]["paths"]
    assert not [p for p in paths if "/reports/" in p], paths
    assert not [p for p in paths if "bad_examples" in p], paths
    assert not [p for p in paths if "shapes" in p], paths


def test_the_ground_digest_moves_when_a_named_term_changes(digest_tool):
    """Falsifies the measure: a digest that ignored content would be
    perfectly stable and perfectly useless."""
    import rdflib

    graph = rdflib.Graph()
    graph.parse(data='<https://ex.invalid/a> <https://ex.invalid/p> "one" .',
                format="turtle")
    before = digest_tool.digest_of(digest_tool.ground(graph))
    graph.add((rdflib.URIRef("https://ex.invalid/a"),
               rdflib.URIRef("https://ex.invalid/p"),
               rdflib.Literal("two")))
    assert digest_tool.digest_of(digest_tool.ground(graph)) != before


def test_the_blank_node_shape_survives_reparsing(digest_tool):
    """The reason blank nodes get a shape rather than a digest.

    rdflib renames them on every parse, so a naive comparison reports
    every restriction as both added and removed -- which is exactly what
    the first namespace check in this repository did.
    """
    import rdflib

    turtle = ("@prefix ex: <https://ex.invalid/> ." + chr(10)
              + "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> ."
              + chr(10)
              + "ex:A rdfs:subClassOf [ a ex:R ; ex:on ex:p ] ." + chr(10)
              + "ex:B rdfs:subClassOf [ a ex:R ; ex:on ex:q ] ." + chr(10))
    first, second = rdflib.Graph(), rdflib.Graph()
    first.parse(data=turtle, format="turtle")
    second.parse(data=turtle, format="turtle")

    raw_first = {(str(s), str(p), str(o)) for s, p, o in first}
    raw_second = {(str(s), str(p), str(o)) for s, p, o in second}
    assert raw_first != raw_second, (
        "blank node names were stable across parses, so the problem this "
        "measure exists for did not occur and it is not being tested")

    assert (digest_tool.bnode_shape(first)["shape_sha256"]
            == digest_tool.bnode_shape(second)["shape_sha256"])


# ------------------------------------------------------- the ladder


def test_the_upstream_vocabulary_the_shapes_walk_is_in_scope(validation):
    """The inverse of what this test used to assert.

    Shapes requiring a class to reach a CCO anchor via subClassOf+ have
    no chain to walk when CCO is absent. They report every subject as
    violating, and that report is indistinguishable from a real defect
    unless the tool separates the two. It did separate them, and then the
    vocabulary was vendored, so now every referenced term resolves.
    """
    record = validation
    assert record["unresolved"] == [], (
        "%s is referenced and not described, so any rung that walks "
        "through it is reporting the scope again" % record["unresolved"])
    for name, info in record["upstream_vocabularies"].items():
        assert info["resolvable"], (name, info)

    for name, rung in record["rungs"].items():
        assert rung["evaluable"], (
            "%s is blocked on %s" % (name,
                                     rung["blocked_by_missing_vocabulary"]))


def test_a_resolvable_vocabulary_is_not_a_complete_one(validation):
    """What "resolvable" does and does not mean.

    Every referenced term is described. That is true of a partial extract
    by construction -- the extract was built from the references -- and
    it is not the same claim as "BFO and CCO are present". The report has
    to carry the difference, or a reader takes the first for the second.
    """
    vendoring = validation["vendoring"]
    assert vendoring["available"], vendoring
    assert vendoring["partial_extracts"] is True
    assert vendoring["not_covered"]
    assert sum(entry["axioms_dropped"]
               for entry in vendoring["sources"].values()) > 0


def test_the_violations_are_attributed_to_whose_terms_they_are(validation):
    """Loading somebody else ontology into the data graph creates the
    mirror of the problem it solved: a defect in the extract reported as
    a defect here."""
    for name, rung in validation["rungs"].items():
        corpus = rung["corpus"]
        assert (corpus["against_authored_terms"]
                + corpus["against_vendored_terms"]
                == corpus["violations"]), (name, corpus)
        assert corpus["against_vendored_terms"] == 0, (
            "%d violation(s) are against vendored upstream terms, which "
            "are findings about the extract" % corpus["against_vendored_terms"])


def test_the_baseline_describes_reality(validation, validator):
    """The gate, run as a test.

    The count of open findings used to be written into this file as
    `== 10`. It now lives in config/validation-baseline.json, so the team
    inheriting this can see what is owed without reading test code, and
    so there is one source of truth rather than a number here and another
    in a report.
    """
    problems = validator.compare(validation, validator.baseline())
    assert problems == [], problems


def test_every_rung_is_recorded(validation, validator):
    """Both directions. A rung with no baseline entry would be adopted
    silently; an entry for a rung that no longer exists is coverage for
    nothing."""
    recorded = set((validator.baseline().get("rungs") or {}))
    assert recorded == set(validation["rungs"]), (
        "recorded but gone: %s; present but unrecorded: %s"
        % (sorted(recorded - set(validation["rungs"])),
           sorted(set(validation["rungs"]) - recorded)))


def test_the_apqc_findings_are_still_the_two_kinds_recorded(validation):
    """The baseline carries a count. This carries what the count is of,
    because ten findings of a different kind would satisfy a number."""
    rung = validation["rungs"]["validation.apqc-shapes"]
    messages = sorted({v["message"] for v in rung["corpus"]["detail"]})
    assert messages == [
        "Process has no skos:example (recommended for production).",
        "Process is missing ex:pcfID (stable APQC provenance anchor).",
    ], messages


# ------------------------------------------------------- the gate


def rung(findings=0, evaluable=True, exercised=True, vendored=0):
    return {"evaluable": evaluable, "can_still_fail": exercised,
            "blocked_by_missing_vocabulary": [] if evaluable else ["CCO"],
            "corpus": {"against_authored_terms": findings,
                       "against_vendored_terms": vendored}}


def test_the_gate_accepts_only_a_baseline_that_matches(validator):
    """Falsifies the gate, one disagreement at a time.

    Run against constructed records rather than the live ladder, because
    each live run is five minutes and because several of these states --
    a rung that has vanished, a vocabulary that has gone missing -- can
    no longer be reached from this repository at all. A branch that
    cannot be reached is a branch nobody has executed.
    """
    baseline = {"rungs": {"a": {"authored_findings": 10}}}

    assert validator.compare({"rungs": {"a": rung(10)}}, baseline) == []

    got = validator.compare({"rungs": {"a": rung(11)}}, baseline)
    assert got and "1 new finding." in got[0], got

    got = validator.compare({"rungs": {"a": rung(13)}}, baseline)
    assert got and "3 new findings." in got[0], got

    got = validator.compare({"rungs": {"a": rung(9)}}, baseline)
    assert got and "re-record" in got[0], got

    got = validator.compare({"rungs": {"a": rung(10), "b": rung(0)}}, baseline)
    assert got and "no entry" in got[0], got

    got = validator.compare({"rungs": {}}, baseline)
    assert got and "no longer exists" in got[0], got

    got = validator.compare({"rungs": {"a": rung(10, evaluable=False)}},
                            baseline)
    assert got and "cannot be evaluated" in got[0], got

    got = validator.compare({"rungs": {"a": rung(10, exercised=False)}},
                            baseline)
    assert got and "did not fire on the fixture" in got[0], got

    got = validator.compare({"rungs": {"a": rung(10, vendored=3)}}, baseline)
    assert got and "vendored upstream terms" in got[0], got


def test_recording_refuses_to_raise_a_count_without_a_reason(validator,
                                                             tmp_path,
                                                             monkeypatch):
    """Without this, a regression certifies itself on the one run that
    introduces it and the baseline becomes a transcript of whatever
    happened rather than a commitment."""
    import json

    monkeypatch.setattr(validator.layout, "repository_root",
                        lambda: tmp_path)
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "validation-baseline.json").write_text(
        json.dumps({"rungs": {"a": {"authored_findings": 10}}}),
        encoding="utf-8")

    raised = {"rungs": {"a": rung(11)}}
    assert validator.record_baseline(raised, None) == 1, (
        "recording accepted a raised count with no reason given")

    assert validator.record_baseline(raised, "deliberate, see ADR-9") == 0
    after = json.loads(
        (tmp_path / "config" / "validation-baseline.json").read_text(
            encoding="utf-8"))
    assert after["rungs"]["a"]["authored_findings"] == 11
    assert after["rungs"]["a"]["why"] == "deliberate, see ADR-9", (
        "the reason was not recorded beside the number it excuses")

    # Lowering never needs a reason.
    assert validator.record_baseline({"rungs": {"a": rung(4)}}, None) == 0


# --------------------------------------------- the wellformedness set


WELLFORMEDNESS_CONSTRAINTS = [
    "Class has no rdfs:label.",
    "Class has no skos:definition.",
    "Concept has no skos:prefLabel.",
]


def test_every_wellformedness_constraint_is_exercised(validation):
    """Named, not counted.

    Two of these find nothing in the corpus today -- every authored class
    already carries a label and a definition. A constraint that finds
    nothing and is never exercised is indistinguishable from one that
    selects nothing, and these exist for modules that do not yet exist,
    so the fixture is the only evidence they work at all.
    """
    rung = validation["rungs"]["validation.wellformedness"]
    fired = sorted({v["message"] for v in rung["fixture"]["detail"]})
    missing = [m for m in WELLFORMEDNESS_CONSTRAINTS if m not in fired]
    assert not missing, (
        "%d presence constraint(s) did not fire against the fixture: %s"
        % (len(missing), missing))

    drift = [m for m in fired if "in the same language" in m]
    assert drift, (
        "no drift constraint fired against the fixture, so the 57 findings "
        "it reports against the corpus rest on nothing")


def test_the_wellformedness_fixture_does_not_flag_what_is_legitimate(
        validation):
    """The false positives sh:maxCount 1 would have produced.

    A multilingual label pair is correct and must not be reported, and a
    catalog concept carrying no rdfs:label is correct because a concept
    is labelled with skos:prefLabel. The second of those was the first
    draft of this shape set, and it reported 3,842 findings that were the
    catalog being told to look like a class.
    """
    rung = validation["rungs"]["validation.wellformedness"]
    flagged = {v["focus"] for v in rung["fixture"]["detail"]}
    for good in ("FixtureMultilingual", "FixtureWellFormed",
                 "FixtureRepeatedValue", "FixtureConceptWellFormed"):
        assert not [f for f in flagged if f and f.endswith("#" + good)], (
            "%s was built to conform and did not" % good)


def test_the_fixtures_come_from_the_contract(validator, layout):
    """`measure` named one fixture component. A second shape set then had
    nowhere to put its cases except a file named for a corpus they have
    nothing to do with."""
    declared = {c.path for c in layout.components("test-fixture")}
    found = {p.relative_to(layout.repository_root()).as_posix()
             for p in validator.fixtures()}
    assert found == declared, (declared, found)
    assert len(found) > 1, (
        "there is still only one fixture, so this does not demonstrate "
        "that more than one is loaded")


def test_a_ladder_that_evaluated_nothing_does_not_pass(validator):
    """`all()` over an empty sequence is True, so the first version of
    this tool reported success having evaluated no rung at all.

    That state cannot be reached from this repository any more, which is
    exactly why the guard is tested against a constructed record rather
    than against the live one -- otherwise it would be a branch nobody
    executes, sitting in a tool whose whole subject is checks that do not
    fire.
    """
    assert validator.passed_of({}) is False

    blocked = {"one": {"evaluable": False,
                       "corpus": {"conforms": True}, "can_still_fail": True}}
    assert validator.passed_of(blocked) is False

    evaluated = {"one": {"evaluable": True,
                         "corpus": {"conforms": True},
                         "can_still_fail": True}}
    assert validator.passed_of(evaluated) is True


def test_the_shapes_are_still_wired_to_a_fixture(validation):
    """The bad-examples fixture must break at least one shape set.

    A fixture that breaks nothing is not a falsification, and a shape set
    with no fixture behind it has a green result that cannot be
    distinguished from a constraint selecting nothing.
    """
    record = validation
    exercised = [name for name, rung in record["rungs"].items()
                 if rung["fixture_exercises_these_shapes"]]
    assert exercised, (
        "the bad-examples fixture produced no violations against any shape "
        "set, so nothing is falsifying the shapes")

    unexercised = sorted(set(record["rungs"]) - set(exercised))
    assert unexercised == [], (
        "%s has no negative fixture behind it, so its result cannot be "
        "distinguished from a constraint that selects nothing" % unexercised)


CAPABILITY_ROLE_CONSTRAINTS = [
    "A class must not be both a Capability and a Role.",
    "Capability must have rdfs:label and skos:definition.",
    "Capability must reach cco:Agent Capability (ont00001379) via "
    "subClassOf+.",
    "Role must have rdfs:label and skos:definition.",
    "Role must reach bfo:Role (BFO_0000023) via subClassOf+.",
    "ex:bearsPermission must target a class reaching cco:Action Permission "
    "(ont00000751).",
    "ex:requiresCapability must target a class reaching cco:Agent Capability "
    "(ont00001379).",
    "ex:requiresPermission must target a class reaching cco:Action Permission "
    "(ont00000751).",
    "ex:requiresRole must target a class reaching bfo:Role (BFO_0000023).",
]


def test_every_capability_and_role_constraint_is_exercised(validation):
    """Named one by one, not counted.

    This shape set reported 202 violations while CCO was absent and zero
    the moment it arrived. A count would have been satisfied by any nine
    violations; what makes the zero against the corpus mean something is
    that each specific constraint is known to fire on data built to break
    it.
    """
    rung = validation["rungs"]["validation.capabilities-roles-shapes"]
    fired = sorted({v["message"] for v in rung["fixture"]["detail"]})
    missing = [m for m in CAPABILITY_ROLE_CONSTRAINTS if m not in fired]
    assert not missing, (
        "%d constraint(s) did not fire against the fixture: %s"
        % (len(missing), missing))


def test_the_fixture_does_not_simply_violate_everything(validation):
    """A fixture where every case fails cannot show a constraint
    discriminates. The positive controls have to survive it."""
    rung = validation["rungs"]["validation.capabilities-roles-shapes"]
    focus = {v["focus"] for v in rung["fixture"]["detail"]}
    for good in ("GoodCapability", "GoodRole", "GoodPermission"):
        assert not [f for f in focus if f and f.endswith("#" + good)], (
            "%s was built to conform and did not" % good)


# ------------------------------------------- the committed measurement


def test_the_committed_digest_is_the_one_the_tool_produces(digest, repo):
    """An artifact in the tree that nothing compares is a claim, not a
    measurement. This is the comparison."""
    import json

    recorded = json.loads(
        (repo / "config/corpus-digest.json").read_text(encoding="utf-8"))
    assert (recorded["merged"]["ground_sha256"]
            == digest["merged"]["ground_sha256"]), (
        "config/corpus-digest.json describes a different corpus; "
        "regenerate it in the commit that changed the ontology")
    assert (recorded["merged"]["blank_nodes"]["shape_sha256"]
            == digest["merged"]["blank_nodes"]["shape_sha256"])
    assert recorded["scope"]["paths"] == digest["scope"]["paths"]
