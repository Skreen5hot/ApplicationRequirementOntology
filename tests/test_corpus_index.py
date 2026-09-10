# SPDX-License-Identifier: Apache-2.0
"""The corpus index, and whether it is derived or merely present.

The file this generator replaces had no generator. It could not be
rebuilt, could not be checked, and had been text-edited -- while its own
README told readers to grep it in preference to reading a slice, which is
the arrangement that turns a stale row into a fact.

So the tests here are not mainly about the columns. They are about the
three properties the previous file lacked: that a fresh build reproduces
what is committed, that the classification rests on the ontology rather
than on the spelling of a class name, and that the generator refuses
rather than degrades when the vocabulary it reasons over is absent.
"""

from __future__ import annotations

import pytest

from conftest import load_tool

EX = "https://fandaws.com/ontology/apqc#"


@pytest.fixture(scope="module")
def indexer():
    return load_tool("aro_build_index", "tools/ontology/build_index.py")


@pytest.fixture(scope="module")
def built(indexer):
    """Built once. Each build parses twenty files and walks the corpus."""
    rows, conflicts = indexer.build()
    return {"rows": rows, "conflicts": conflicts,
            "by_iri": {row[0]: row for row in rows}}


# ------------------------------------------------- derived, not present


def test_the_committed_index_is_what_the_generator_produces(indexer, built):
    """The property the previous index could not have had.

    An artifact nothing compares is a claim. This is the comparison, and
    it is the same code path `--check` runs in CI.
    """
    on_disk = indexer.target().read_text(
        encoding="utf-8-sig").replace("\r\n", "\n")
    assert on_disk == indexer.render(built["rows"]), (
        "APQC_ontology/index/corpus_index.tsv differs from a fresh build; "
        "run python tools/ontology/build_index.py")


def test_building_twice_gives_the_same_bytes(indexer, built):
    """Sorted, and independent of the order the files were parsed in."""
    again, _conflicts = indexer.build()
    assert indexer.render(again) == indexer.render(built["rows"])


def test_the_generator_refuses_without_the_vendored_upstream(indexer,
                                                             monkeypatch):
    """The failure this tool exists to not have.

    Every kind is decided by walking rdfs:subClassOf to a BFO or CCO
    anchor. With the upstream absent the walk stops at the first foreign
    parent, every class falls through to `other`, and the index looks
    complete. Degrading silently is the whole defect class; refusing is
    the fix.
    """
    monkeypatch.setattr(indexer.layout, "vendored_files", lambda: [])
    with pytest.raises(SystemExit) as raised:
        indexer.build()
    assert "vendored" in str(raised.value)


def test_a_missing_anchor_is_refused_rather_than_silently_empty(indexer,
                                                                monkeypatch):
    """An anchor that resolves to nothing has no descendants.

    Its kind then empties, the terms fall through to the next rule, and
    the result is a plausible index that is wrong in one whole category.
    """
    broken = tuple(
        (kind, tuple(a + "-does-not-exist" for a in anchors), name)
        for kind, anchors, name in indexer.KIND_ANCHORS)
    monkeypatch.setattr(indexer, "KIND_ANCHORS", broken)
    with pytest.raises(SystemExit) as raised:
        indexer.build()
    assert "anchor" in str(raised.value)


# --------------------------------------------- the rows are the corpus


def test_every_declared_term_appears_exactly_once(indexer, built, layout):
    """Both directions. A term missing from the index is invisible to
    anyone following the README; a row for a term nothing declares points
    at a file that says nothing about it."""
    import rdflib
    from rdflib.namespace import RDF

    graph = rdflib.Graph()
    for path in layout.ontology_files():
        graph.parse(path, format="turtle")
    declared = set()
    for declaration in indexer.DECLARATIONS:
        for subject in graph.subjects(RDF.type, rdflib.URIRef(declaration)):
            if isinstance(subject, rdflib.URIRef) and str(subject).startswith(EX):
                declared.add(indexer.short(str(subject)))

    indexed = [row[0] for row in built["rows"]]
    assert len(indexed) == len(set(indexed)), "a term is indexed twice"
    assert set(indexed) == declared, (
        "indexed but not declared: %s; declared but not indexed: %s"
        % (sorted(set(indexed) - declared)[:5],
           sorted(declared - set(indexed))[:5]))


def test_the_wiring_module_does_not_get_terms_of_its_own(built):
    """Declaration, not mention.

    capabilities_wiring.ttl names hundreds of classes and declares none.
    Indexing what a file mentions would file every one of them against a
    module that says nothing about what they are.
    """
    assert not [row for row in built["rows"] if row[2] == "wiring"], (
        "terms were filed under the wiring module, which declares none")


# ------------------------------------ classification rests on ancestry


@pytest.mark.parametrize("term,kind,why", [
    ("ex:AccountingCapability", "capability", "reaches cco:ont00001379"),
    ("ex:AccountantRole", "role", "reaches obo:BFO_0000023"),
    ("ex:BaselineDemandForecast", "ice",
     "a CCO Predictive Information Content Entity; the previous index "
     "said other"),
    ("ex:FinancialInstrument", "other",
     "a CCO Material Artifact, an independent continuant -- it cannot be "
     "an information content entity, and the previous index said ice"),
    ("ex:RegulatoryBody", "agent",
     "a CCO Government Organization; the previous index said other"),
    ("ex:ApproveImplementationPlan", "process",
     "a CCO Planned Act; the previous index said other"),
])
def test_kind_follows_the_ontology_not_the_name(built, term, kind, why):
    """Each of these was decided by walking subClassOf.

    The last four are the cases where this generator and the file it
    replaced disagree, and they are here individually so that a change of
    mind about any one of them has to be deliberate.
    """
    row = built["by_iri"].get(term)
    assert row is not None, "%s is not indexed" % term
    assert row[1] == kind, "%s: %s -- %s" % (term, row[1], why)


def test_a_name_ending_in_capability_is_not_what_makes_it_one(built):
    """Falsifies the classification.

    If `kind` were derived from the spelling of the IRI, every capability
    row would end in "Capability" and nothing else would. It does not
    hold in either direction, which is the evidence that ancestry is what
    is being read.
    """
    capabilities = [row[0] for row in built["rows"] if row[1] == "capability"]
    assert capabilities
    not_named_so = [c for c in capabilities if not c.endswith("Capability")]
    assert not_named_so, (
        "every capability is spelled '...Capability', so this test cannot "
        "distinguish an ancestry rule from a suffix match")


# -------------------------------------------------- the file is a TSV


def test_no_field_can_break_a_row(built):
    """The corpus has multi-line definitions throughout.

    One unescaped newline ends a row early and every column after it is
    attributed to a term that does not exist.
    """
    for row in built["rows"]:
        assert len(row) == 9, row[0]
        for i, field in enumerate(row):
            assert "\t" not in field, (row[0], i)
            assert "\n" not in field and "\r" not in field, (row[0], i)


def test_the_definition_column_is_bounded(built, indexer):
    lengths = [len(row[8]) for row in built["rows"]]
    assert max(lengths) <= indexer.DEFINITION_LIMIT, max(lengths)


# ------------------------------------- what building it found, recorded


#: Terms whose inlined copies disagree. Pinned so the number can go down
#: visibly and cannot go up quietly. These are defects in the corpus, not
#: in the generator: the slices inline the shared genera rather than
#: importing them, and the copies have drifted.
CONFLICTING_LABELS = 6
CONFLICTING_DEFINITIONS = 51


def test_the_drift_between_inlined_copies_is_recorded(built):
    assert len(built["conflicts"]["label"]) == CONFLICTING_LABELS, (
        "%d term(s) now carry more than one distinct rdfs:label (was %d). "
        "If that is a fix, lower the number here in the same commit."
        % (len(built["conflicts"]["label"]), CONFLICTING_LABELS))
    assert (len(built["conflicts"]["definition"])
            == CONFLICTING_DEFINITIONS), (
        "%d term(s) now carry more than one distinct skos:definition "
        "(was %d)." % (len(built["conflicts"]["definition"]),
                       CONFLICTING_DEFINITIONS))


def test_a_conflict_resolves_to_the_canonical_home(indexer):
    """The rule, exercised directly.

    A shared module owns the term; a slice that inlined it does not get
    to redefine it. Picking silently is what made this invisible before,
    so the choice is a stated rule with a test rather than whichever
    value the parser reached last.
    """
    ext = "APQC_ontology/apqc-ext.ttl"
    slice_9 = "APQC_ontology/slices/apqc_9_0.ttl"

    value, conflicted = indexer.pick({ext: "owned", slice_9: "inlined"})
    assert (value, conflicted) == ("owned", True)

    value, conflicted = indexer.pick({slice_9: "same", ext: "same"})
    assert (value, conflicted) == ("same", False)

    # Two slices disagreeing and no shared module: lexicographic, so the
    # output does not depend on the order the files were parsed in.
    other = "APQC_ontology/slices/apqc_1_0.ttl"
    assert indexer.pick({slice_9: "b", other: "a"}) == ("a", True)
    assert indexer.pick({other: "a", slice_9: "b"}) == ("a", True)


def test_the_shared_genera_are_filed_under_ext_not_a_slice(built):
    """The previous index filed them by the first filename in string
    order, which put them in section "10" because `apqc_10_0.ttl` sorts
    ahead of `apqc_1_0.ttl`. That is a fact about sorting."""
    row = built["by_iri"]["ex:ActOfAccounting"]
    assert row[2] == "ext", row
    assert row[1] == "act-genus", row
