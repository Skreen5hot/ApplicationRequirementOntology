# SPDX-License-Identifier: Apache-2.0
"""The ontology's namespace, and the trap inside the shapes.

`example.org` is IANA-reserved for documentation. An ontology published
under it has IRIs that can never be dereferenced and must never be cited,
and moving off it later costs more the longer it is left.

The interesting test is the last one. Two SHACL files carry SPARQL in
`sh:select` literals, and one of them tests a namespace by string prefix:

    FILTER( STRSTARTS(STR(?super), "https://fandaws.com/ontology/apqc#") )

Text inside a literal is not an IRI, so a rename that walked the graph
would leave it behind -- and the constraint would then match nothing,
report no violations, and look exactly like a passing shape.
"""

from __future__ import annotations

import pytest

RESERVED = "example.org"
NAMESPACE = "https://fandaws.com/ontology/"


@pytest.fixture(scope="module")
def turtle(repo):
    return sorted((repo / "APQC_ontology").rglob("*.ttl"))


def test_the_corpus_was_measured_not_assumed(turtle):
    """Guards every test below: an empty file list passes all of them."""
    assert len(turtle) >= 30, len(turtle)


def test_no_term_cites_the_reserved_domain(turtle):
    """Terms, not text.

    The first version scanned the file as a string and failed on a Turtle
    comment describing a commented-out import -- prose about the code
    rather than the code, which is the defect this project keeps finding.
    A comment is dropped by the parser, which is exactly the right
    treatment: it cannot be dereferenced by anything.

    Literals are checked as well as IRIs, because the SHACL constraints
    carry SPARQL that names the namespace as a string.
    """
    import rdflib

    offenders = []
    for path in turtle:
        graph = rdflib.Graph()
        graph.parse(path, format="turtle")
        for triple in graph:
            for term in triple:
                if isinstance(term, rdflib.URIRef) and RESERVED in str(term):
                    offenders.append((path.name, "IRI", str(term)[:70]))
                elif isinstance(term, rdflib.Literal) and RESERVED in str(term):
                    offenders.append((path.name, "literal", str(term)[:70]))
    assert not offenders, (
        "%d term(s) still cite %s, which is reserved for documentation and "
        "cannot be dereferenced: %s"
        % (len(offenders), RESERVED, offenders[:5]))


def test_no_comment_still_describes_the_old_namespace(turtle):
    """Separate, and weaker on purpose.

    A stale comment breaks nothing, so this is not folded into the test
    above -- conflating them would make a prose fix look like a
    correctness fix. It is still worth failing on: a comment naming a
    namespace that no longer exists sends the next reader somewhere that
    is not there.
    """
    offenders = []
    for path in turtle:
        for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.lstrip()
            if stripped.startswith("#") and RESERVED in stripped:
                offenders.append("%s:%d" % (path.name, number))
    assert not offenders, offenders[:8]


def test_every_declared_prefix_is_under_the_project_namespace(turtle):
    """A prefix pointing somewhere else is either an upstream vocabulary
    or a mistake, and the two look identical in a diff."""
    import re

    upstream = ("http://www.w3.org/", "http://purl.obolibrary.org/",
                "https://www.commoncoreontologies.org/",
                "http://purl.org/dc/", "http://www.w3.org/ns/")
    stray = []
    for path in turtle:
        for match in re.finditer(r"@prefix\s+\S*:\s+<([^>]+)>",
                                 path.read_text(encoding="utf-8")):
            iri = match.group(1)
            if iri.startswith(NAMESPACE) or iri.startswith(upstream):
                continue
            stray.append((path.name, iri))
    assert not stray, stray[:8]


def test_the_sparql_inside_the_shapes_targets_the_current_namespace(repo):
    """The vacuous-pass trap.

    A constraint that filters on a namespace prefix string still runs
    when the string is stale. It simply selects nothing, reports no
    violation, and is indistinguishable from a shape that holds.
    """
    import rdflib

    shapes = [repo / "APQC_ontology/apqc_shapes.ttl",
              repo / "APQC_ontology/capabilities_roles_shapes.ttl"]
    citing = []
    for path in shapes:
        graph = rdflib.Graph()
        graph.parse(path, format="turtle")
        for _s, _p, obj in graph:
            if isinstance(obj, rdflib.Literal) and NAMESPACE in str(obj):
                citing.append((path.name, str(obj)))
            if isinstance(obj, rdflib.Literal) and RESERVED in str(obj):
                pytest.fail(
                    "%s carries SPARQL still naming %s; it would run, match "
                    "nothing, and report no violations" % (path.name, RESERVED))

    assert len(citing) >= 6, (
        "expected the shapes to name the namespace in their SPARQL; found "
        "%d such literals, so either the constraints changed or this test "
        "is no longer watching them" % len(citing))
