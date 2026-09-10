# SPDX-License-Identifier: Apache-2.0
"""The corpus measures, and the honesty of the validation ladder.

The SHACL tests here assert almost nothing about whether the ontology is
correct, because right now that cannot be determined: the shapes reason
over BFO and CCO, and neither is in the repository. What they assert is
that the tool says so, rather than reporting 213 violations that describe
a missing vocabulary and reading exactly like defects.
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


def test_the_ladder_reports_missing_vocabulary_rather_than_violations(
        validation):
    """The finding, and the distinction that makes it a finding.

    Shapes requiring a class to reach a CCO anchor via subClassOf+ have
    no chain to walk when CCO is absent. They report every subject as
    violating, and that report is indistinguishable from a real defect
    unless the tool separates the two.
    """
    record = validation
    assert record["unresolved"], (
        "no upstream vocabulary is reported missing; if BFO and CCO have "
        "been vendored, this test should be inverted rather than deleted")
    assert set(record["unresolved"]) == {"BFO/OBO", "CCO"}, record["unresolved"]

    for name, rung in record["rungs"].items():
        assert not rung["evaluable"], (
            "%s became evaluable; its violations are now findings about "
            "the ontology and should be asserted as such" % name)


def test_a_ladder_that_evaluated_nothing_does_not_pass(validation):
    """`all()` over an empty sequence is True, so the first version of
    this tool reported success having evaluated no rung at all."""
    record = validation
    if not record["evaluable_rungs"]:
        assert record["passed"] is False, (
            "every rung is blocked and the ladder still reports passed")


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
    assert unexercised == ["validation.capabilities-roles-shapes"], (
        "the set of shape sets with no negative fixture changed: %s"
        % unexercised)
