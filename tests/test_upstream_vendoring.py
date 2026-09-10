# SPDX-License-Identifier: Apache-2.0
"""The vendored BFO and CCO extracts, and whether they earn their place.

Two questions, and the second is the one worth asking.

  Is the vendoring correct?   Every upstream term this repository names is
                              described, nothing dangles, the digests match.

  Is it load-bearing?         Without these files 10 of 116 capability
                              classes reach the anchor the shapes walk to.
                              With them, 116. If that difference ever
                              collapses, the extracts are decoration and
                              the shape set they unblocked is back to
                              reporting the scope rather than the ontology.

None of these tests need the network. Rebuilding from upstream does, and
that is a separate mode of the tool -- see `--confirm`, which is what
shows these files are derived from the pins rather than hand-edited.
"""

from __future__ import annotations

import pytest

from conftest import load_tool

CAPABILITY_ANCHOR = "https://www.commoncoreontologies.org/ont00001379"
ROLE_ANCHOR = "http://purl.obolibrary.org/obo/BFO_0000023"


@pytest.fixture(scope="module")
def vendoring():
    return load_tool("aro_vendor", "tools/ontology/vendor_upstream.py")


@pytest.fixture(scope="module")
def report(vendoring):
    return vendoring.verify()


@pytest.fixture(scope="module")
def extracts(layout):
    """The vendored extracts as one graph."""
    import rdflib

    graph = rdflib.Graph()
    for path in layout.vendored_files():
        graph.parse(path, format="turtle")
    return graph


@pytest.fixture(scope="module")
def corpus(layout):
    import rdflib

    graph = rdflib.Graph()
    for path in layout.ontology_files():
        graph.parse(path, format="turtle")
    return graph


# ------------------------------------------------------------- pinning


def test_every_url_names_the_commit_it_pins(vendoring):
    """A tag can be moved to a different commit; a commit cannot.

    The pins declare both, and a url pinned to a tag while the file
    claims a commit would serve whatever the tag points at today.
    """
    for entry in vendoring.sources():
        assert entry["commit"] in entry["url"], entry["id"]


def test_the_recorded_digest_is_what_the_extract_digests_to(report):
    assert report["ok"], report["findings"]


def test_the_manifest_records_a_source_digest_for_every_extract(vendoring):
    import json

    root = vendoring.layout.repository_root()
    manifest = json.loads(
        (root / vendoring.MANIFEST).read_text(encoding="utf-8"))
    pinned = {entry["id"]: entry for entry in vendoring.sources()}
    assert set(manifest["extracts"]) == set(pinned)
    for key, record in manifest["extracts"].items():
        assert record["source_sha256"] == pinned[key]["sha256"], key
        assert record["commit"] == pinned[key]["commit"], key


# ------------------------------------------------------- completeness


def test_every_upstream_term_named_here_is_described(report):
    """The check that catches the corpus growing past the extract.

    A new cco: reference in a slice, or a new anchor in a constraint,
    lands as a term nothing describes -- and a shape walking through it
    silently answers "no" for every subject, which is what the 202
    violations were.
    """
    assert report["unresolved_seeds"] == [], report["unresolved_seeds"]


def test_the_extracts_reference_nothing_they_do_not_describe(report):
    """Closure. An extract that mentions an upstream term it does not
    carry has the same defect as the corpus did, one level down."""
    assert report["dangling_references"] == [], report["dangling_references"]


def test_a_term_that_is_not_vendored_is_reported_rather_than_ignored(
        vendoring, monkeypatch):
    """Falsifies the completeness check.

    Both assertions above pass when nothing is missing and would also
    pass if the check looked at the wrong thing. Adding one term nobody
    vendored has to produce a finding.
    """
    real = vendoring.seed_terms
    invented = "https://www.commoncoreontologies.org/ont00000000"

    monkeypatch.setattr(vendoring, "seed_terms",
                        lambda namespaces: real(namespaces) | {invented})
    record = vendoring.verify()
    assert invented in record["unresolved_seeds"], record
    assert not record["ok"]


def test_the_extracts_carry_no_blank_nodes(extracts):
    """By construction, and the reason the digest means anything.

    rdflib renames blank nodes on every parse. An extract containing one
    would digest differently every time it was rebuilt from identical
    upstream bytes, and `--confirm` would report a difference that is not
    there.
    """
    import rdflib

    blank = [t for triple in extracts for t in triple
             if isinstance(t, rdflib.BNode)]
    assert not blank, "%d blank node(s) in the extracts" % len(blank)


# ------------------------------------------------------- load-bearing


def reaches(graph, anchor: str, suffix: str) -> tuple:
    """How many ex: classes whose name ends in `suffix` reach `anchor`."""
    import rdflib

    query = """
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT (COUNT(DISTINCT ?c) AS ?n) WHERE {
          ?c a owl:Class .
          FILTER(STRSTARTS(STR(?c), "https://fandaws.com/ontology/"))
          FILTER(STRENDS(STR(?c), "%s"))
          %s
        }"""
    total = int(list(graph.query(query % (suffix, "")))[0][0])
    hit = int(list(graph.query(
        query % (suffix, "?c rdfs:subClassOf* <%s> ." % anchor)))[0][0])
    return hit, total


def test_the_cco_extract_is_what_makes_the_capability_shape_answerable(
        corpus, extracts):
    """The measurement this vendoring exists for.

    Without CCO the chain from a capability class stops at its first
    upstream parent, so the constraint reports every capability as
    failing to reach the anchor. That report reads exactly like a defect
    in the ontology, and it was one of 202.
    """
    before_hit, total = reaches(corpus, CAPABILITY_ANCHOR, "Capability")
    assert total > 100, total

    merged = corpus + extracts
    after_hit, after_total = reaches(merged, CAPABILITY_ANCHOR, "Capability")
    assert after_total == total, (
        "the extracts added classes in this repository's own namespace, "
        "which they must not")

    assert before_hit < total, (
        "every capability already reached the anchor without the extract, "
        "so this vendoring is not what unblocked the shape and this test "
        "is measuring nothing")
    assert after_hit == total, (
        "%d of %d capability classes still do not reach %s"
        % (total - after_hit, total, CAPABILITY_ANCHOR))


def test_the_role_shape_was_already_answerable(corpus):
    """Recorded because it is the honest half of the same measurement.

    The role constraint walks to a BFO anchor the corpus asserts
    directly, so it was never blocked. Vendoring BFO did not fix it and
    saying otherwise would credit this work with a result it did not
    produce.
    """
    hit, total = reaches(corpus, ROLE_ANCHOR, "Role")
    assert hit == total > 50, (hit, total)


# ---------------------------------------------------------- licensing


def test_the_extracts_are_third_party_and_redistributable(disposition):
    rows = {row.path: row for row in disposition.classify()}
    vendored = [row for row in rows.values()
                if row.disposition == disposition.VENDORED]
    assert len(vendored) == 2, [row.path for row in vendored]
    assert {row.licence for row in vendored} == {"CC-BY-4.0", "BSD-3-Clause"}
    for row in vendored:
        assert row.redistributable, row.path


def test_the_licence_comes_from_the_pins_not_from_this_repository(
        disposition):
    """A vendored file does not carry this repository's licence.

    The classifier answers `project_licence()` for everything it
    considers project content, and a vendored extract falling through to
    that would have this repository asserting MIT over somebody else
    ontology.
    """
    project = disposition.project_licence()
    rows = [row for row in disposition.classify()
            if row.disposition == disposition.VENDORED]
    assert rows
    for row in rows:
        assert row.licence != project, row.path


def test_attribution_is_checked_rather_than_assumed(disposition,
                                                    monkeypatch):
    """Falsifies the attribution check.

    Both licences permit redistribution on condition of attribution.
    Pointing the check at a file that does not contain the attribution
    has to produce a finding, or the condition is being reported as met
    by a check that never looks.
    """
    rows = disposition.classify()
    assert disposition.attribution_findings(rows) == []

    monkeypatch.setattr(disposition, "NOTICE", "LICENSE")
    problems = disposition.attribution_findings(rows)
    assert problems, (
        "the attribution check passed against a file containing no "
        "attribution")
    assert "vendor/cco/cco-aro-extract.ttl" in problems[0]


# -------------------------------------------------- what was not done


def test_the_manifest_states_what_the_extracts_leave_out(vendoring):
    """A partial extract that does not say it is partial is the defect
    this whole method is about."""
    import json

    root = vendoring.layout.repository_root()
    manifest = json.loads(
        (root / vendoring.MANIFEST).read_text(encoding="utf-8"))

    assert manifest["not_covered"], manifest.keys()
    assert any("anonymous class expression" in line
               for line in manifest["not_covered"])
    assert any("consistent" in line for line in manifest["not_covered"])

    dropped = sum(entry["axioms_dropped_anonymous_object"]
                  for entry in manifest["extracts"].values())
    assert dropped > 0, (
        "no axioms were dropped, so either the upstream has no anonymous "
        "class expressions -- it does -- or the count is not being taken")


def test_each_extract_says_in_its_own_header_that_it_is_partial(layout):
    """The manifest is a file somebody has to go and read. The extract is
    the file they already have open."""
    for path in layout.vendored_files():
        head = path.read_text(encoding="utf-8")[:3000]
        assert "partial extract" in head.lower(), path.name
        assert "cannot be" in head and "consistency" in head, path.name
        assert "axioms about the selected terms were dropped" in head, \
            path.name


# --------------------------------------------------------- serialising


def test_the_serialiser_round_trips_awkward_literals(vendoring):
    """Falsifies the escaping.

    Definitions in CCO run to several lines and contain quotation marks.
    A serialiser that got either wrong would emit a file that parses to a
    different graph, and the digest recorded for it would be a digest of
    the damage.
    """
    import rdflib

    subject = rdflib.URIRef("https://ex.invalid/a")
    awkward = ('line one' + chr(10) + 'line "two"' + chr(9) + 'tabbed'
               + chr(92) + ' backslash')
    triples = [
        (subject, rdflib.URIRef("https://ex.invalid/p"),
         rdflib.Literal(awkward, lang="en")),
        (subject, rdflib.URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
         rdflib.Literal("plain")),
        (subject, rdflib.URIRef("https://ex.invalid/n"),
         rdflib.Literal("3", datatype=rdflib.URIRef(
             "http://www.w3.org/2001/XMLSchema#integer"))),
    ]
    text = vendoring.serialise(triples, ["a test"])
    assert chr(10) not in text.split('"')[1], (
        "the literal was emitted across lines, so a newline inside it is "
        "no longer distinguishable from formatting")

    back = rdflib.Graph()
    back.parse(data=text, format="turtle")
    assert set(back) == set(triples)


def test_the_same_inputs_serialise_to_the_same_bytes(vendoring):
    """Sorted, deduplicated, and independent of the order given."""
    import rdflib

    triples = [
        (rdflib.URIRef("https://ex.invalid/b"),
         rdflib.URIRef("https://ex.invalid/p"), rdflib.Literal("two")),
        (rdflib.URIRef("https://ex.invalid/a"),
         rdflib.URIRef("https://ex.invalid/p"), rdflib.Literal("one")),
    ]
    first = vendoring.serialise(triples, ["h"])
    second = vendoring.serialise(list(reversed(triples)) + triples, ["h"])
    assert first == second


def test_a_blank_node_reaching_the_serialiser_is_refused(vendoring):
    """It cannot happen by construction, which is exactly why the guard
    is here: the construction is what would change."""
    import rdflib

    with pytest.raises(SystemExit):
        vendoring.serialise(
            [(rdflib.URIRef("https://ex.invalid/a"),
              rdflib.URIRef("https://ex.invalid/p"), rdflib.BNode())], ["h"])


# ------------------------------------------------------------- scope


def test_the_extracts_are_not_counted_as_this_repository_ontology(layout):
    """A vendored file in `ontology_files()` would put 660 third-party
    triples into the corpus digest, and the digest would then move
    whenever an upstream pin changed."""
    authored = {p.as_posix() for p in layout.ontology_files()}
    vendored = {p.as_posix() for p in layout.vendored_files()}
    assert vendored
    assert not (authored & vendored)


def test_the_corpus_digest_does_not_measure_the_vendored_extracts():
    digest = load_tool("aro_digest_scope",
                       "tools/ontology/corpus_digest.py").measure()
    assert not [p for p in digest["scope"]["paths"] if p.startswith("vendor/")]
