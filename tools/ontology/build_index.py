# SPDX-License-Identifier: Apache-2.0
"""Build the greppable corpus index.

    python tools/ontology/build_index.py            # rewrite the index
    python tools/ontology/build_index.py --check    # compare, do not write

WHY THIS EXISTS

`APQC_ontology/index/corpus_index.tsv` was committed without a generator.
Its own README documented `python scripts/build_index.py`; there was no
`scripts/` directory. So the file could not be rebuilt, could not be
checked, and had been text-edited during the namespace migration -- while
the README told readers to grep it *in preference to reading a slice*,
which makes a stale row indistinguishable from a fact.

This is that generator. The contract records the debt it discharges.

WHAT DECIDES EACH COLUMN

  iri         every term in the project namespace that some module
              *declares* -- owl:Class, skos:Concept, an owl property, or
              owl:NamedIndividual. Declaration, not mention: the wiring
              module names hundreds of classes it does not define, and
              indexing those would list a term against a file that says
              nothing about it.

  kind        by walking rdfs:subClassOf to an upstream anchor, not by
              matching the end of the name. This is the part that only
              became possible when BFO and CCO were vendored: before
              that the chain stopped at the first upstream parent and
              every class looked equally unclassifiable.

  section     the term's canonical home. A shared module owns the term
              and the slices carry inlined copies, so `ext` beats a slice
              number rather than the other way round.

  hierarchy   ex:hierarchyID
  pcf         ex:pcfID
  label       rdfs:label
  parents     named rdfs:subClassOf, ";"-joined
  wiring      the Phase-1 bridge: req-cap, req-role, bears-perm, enables
  definition  skos:definition, cut to 160 characters

WHAT THIS IS NOT

It is not a reproduction of the file it replaces. The two agree on all
5,050 rows and on 5,039 of the 5,039 `kind` values that can be derived
without guessing; the differences are recorded in the commit that
introduced this file, and in every case the derived answer is the one the
ontology supports. Two in particular:

  ex:FinancialInstrument was indexed `ice`. It is a CCO Material
  Artifact -- an independent continuant -- and cannot be an information
  content entity.

  ex:BaselineDemandForecast was indexed `other`. It is a CCO Predictive
  Information Content Entity.

`section` differs for the 100 terms declared in more than one file. The
previous index resolved those by taking the first filename in string
order, which put shared genera in section "10" because `apqc_10_0.ttl`
sorts before `apqc_1_0.ttl`. That is an accident of sorting rather than a
fact about the ontology, so it is not reproduced.

WHAT BUILDING IT FOUND

The slices inline the genera they use instead of importing them, and the
copies have drifted. 51 terms carry more than one distinct
skos:definition and 6 carry more than one distinct rdfs:label, so the
same IRI means different things depending on which file you read.
ex:ActOfForecasting is defined one way in apqc-ext.ttl and five slices,
and another way in apqc_10_0.ttl.

A single-value column cannot represent that, and picking one quietly is
how the previous index made it invisible. So the value is chosen by a
stated rule -- the canonical home wins -- and the count of conflicts is
reported on every run and pinned by a test, which is what makes the
number able to go down.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import layout  # noqa: E402

GENERATOR = "tools/ontology/build_index.py"
COMPONENT = "generated.corpus-index"

EX = "https://fandaws.com/ontology/apqc#"
CCO = "https://www.commoncoreontologies.org/"
OBO = "http://purl.obolibrary.org/obo/"

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
RDFS_SUBCLASSOF = "http://www.w3.org/2000/01/rdf-schema#subClassOf"
SKOS_DEFINITION = "http://www.w3.org/2004/02/skos/core#definition"
OWL_ = "http://www.w3.org/2002/07/owl#"
SKOS_ = "http://www.w3.org/2004/02/skos/core#"

COLUMNS = ("iri", "kind", "section", "hierarchy", "pcf", "label", "parents",
           "wiring", "definition")

#: What counts as declaring a term.
DECLARATIONS = (OWL_ + "Class", SKOS_ + "Concept", OWL_ + "ObjectProperty",
                OWL_ + "DatatypeProperty", OWL_ + "AnnotationProperty",
                OWL_ + "NamedIndividual")

#: Ordered most specific first, and the order is the rule: a permission is
#: an information content entity and a capability is not a process, so
#: whichever anchor is reached first wins. Each entry is
#: (kind, [anchor IRIs], readable name of the anchor) -- the readable name
#: is here so a reviewer can check the anchor is the one intended without
#: resolving an opaque CCO identifier.
KIND_ANCHORS = (
    ("capability", (CCO + "ont00001379",), "Agent Capability"),
    ("role", (OBO + "BFO_0000023",), "role"),
    ("ice", (CCO + "ont00000958",), "Information Content Entity"),
    ("agent", (CCO + "ont00001017", CCO + "ont00001180"),
     "Agent / Organization"),
    ("process", (CCO + "ont00000005", OBO + "BFO_0000015"), "Act / process"),
)

#: Shared modules own their terms; slices carry inlined copies. Ordered,
#: and the order is what stops a genus being filed under whichever slice
#: happens to sort first.
CANONICAL_HOMES = (
    ("APQC_ontology/apqc-ext.ttl", "ext"),
    ("APQC_ontology/apqc-catalog.ttl", "catalog"),
    ("APQC_ontology/capabilities_roles.ttl", "cap"),
    ("APQC_ontology/delivery_processes.ttl", "delivery"),
    ("APQC_ontology/capabilities_wiring.ttl", "wiring"),
)

#: (predicate, prefix) for the Phase-1 bridge columns.
WIRING = (
    (EX + "requiresCapability", "req-cap"),
    (EX + "requiresRole", "req-role"),
    (EX + "bearsPermission", "bears-perm"),
    (EX + "enablesProcess", "enables"),
)

DEFINITION_LIMIT = 160


class Refused(SystemExit):
    """Raised rather than emitting an index that cannot mean anything."""


def short(iri: str) -> str:
    for prefix, namespace in (("ex:", EX), ("cco:", CCO), ("obo:", OBO),
                              ("skos:", SKOS_), ("owl:", OWL_)):
        if iri.startswith(namespace):
            return prefix + iri[len(namespace):]
    return iri


def pick(values: dict) -> tuple:
    """One value for a term whose copies disagree, plus whether they did.

    `values` maps a repository-relative path to that file's text. When
    the copies agree there is nothing to decide. When they do not, the
    shared module that owns the term wins over a slice that inlined it,
    and two disagreeing slices fall back to the lexicographically first
    so the output does not depend on filesystem order.

    Returning the conflict flag rather than swallowing it is the point.
    """
    distinct = set(values.values())
    if not distinct:
        return "", False
    if len(distinct) == 1:
        return distinct.pop(), False
    for path, _name in CANONICAL_HOMES:
        if path in values:
            return values[path], True
    return min(values.values()), True


def clean(text: str) -> str:
    """One line, no tabs.

    A definition carrying a newline would end the row early and every
    column after it would belong to a term that does not exist. The
    corpus has multi-line definitions throughout, so this is not
    hypothetical.
    """
    return " ".join(str(text).split())


def load():
    """The corpus, plus the vendored upstream the anchors live in."""
    import rdflib

    graph = rdflib.Graph()
    for path in layout.ontology_files():
        graph.parse(path, format="turtle")
    vendored = layout.vendored_files()
    if not vendored:
        raise Refused(
            "no vendored upstream is declared. Every `kind` below is "
            "decided by walking rdfs:subClassOf to a BFO or CCO anchor, "
            "and with the upstream absent the walk stops at the first "
            "foreign parent -- so every class would be indexed `other` "
            "and the index would look complete.")
    for path in vendored:
        graph.parse(path, format="turtle")
    return graph


def check_anchors(graph) -> None:
    """Refuse if an anchor is not described.

    An anchor that resolves to nothing has no descendants, so its kind
    silently empties and the terms fall through to the next rule. The
    result is a plausible index that is wrong in one whole category, and
    nothing about it looks unusual.
    """
    import rdflib

    missing = []
    for kind, anchors, name in KIND_ANCHORS:
        for anchor in anchors:
            if not list(graph.predicate_objects(rdflib.URIRef(anchor))):
                missing.append("%s (%s, for kind %r)" % (anchor, name, kind))
    if missing:
        raise Refused(
            "%d classification anchor(s) are not described in scope, so "
            "the kinds resting on them would be silently empty:\n  %s"
            % (len(missing), "\n  ".join(missing)))


def descendants(graph, anchors) -> set:
    """Every term reaching one of `anchors` through rdfs:subClassOf."""
    import rdflib

    predicate = rdflib.URIRef(RDFS_SUBCLASSOF)
    seen, stack = set(), [rdflib.URIRef(a) for a in anchors]
    while stack:
        current = stack.pop()
        for subject in graph.subjects(predicate, current):
            if subject not in seen:
                seen.add(subject)
                stack.append(subject)
    return {str(s) for s in seen}


def per_file() -> tuple:
    """Who declares what, and what each file says the term is called.

    Both come from the same pass, because they are the same question
    asked twice: a term declared in eight files has eight chances to
    disagree with itself, and the merged graph cannot tell you which
    file said what.
    """
    import rdflib

    root = layout.repository_root()
    declared: dict = {}
    texts: dict = {"label": {}, "definition": {}}
    for path in layout.ontology_files():
        graph = rdflib.Graph()
        graph.parse(path, format="turtle")
        relative = path.relative_to(root).as_posix()
        for declaration in DECLARATIONS:
            for subject in graph.subjects(rdflib.URIRef(RDF_TYPE),
                                          rdflib.URIRef(declaration)):
                if (isinstance(subject, rdflib.URIRef)
                        and str(subject).startswith(EX)):
                    declared.setdefault(str(subject), set()).add(relative)
        for column, predicate in (("label", RDFS_LABEL),
                                  ("definition", SKOS_DEFINITION)):
            for subject, obj in graph.subject_objects(
                    rdflib.URIRef(predicate)):
                if (isinstance(subject, rdflib.URIRef)
                        and str(subject).startswith(EX)):
                    texts[column].setdefault(str(subject), {})[relative] = (
                        clean(obj))
    return declared, texts


def section_of(files: set) -> str:
    """The term's canonical home.

    A shared module owns the term; the slices inline copies of it. Taking
    the first filename in string order -- which is what produced this
    column before -- files every shared genus under section "10", because
    `apqc_10_0.ttl` sorts ahead of `apqc_1_0.ttl`.
    """
    for path, name in CANONICAL_HOMES:
        if path in files:
            return name
    slices = sorted(
        f.rsplit("/", 1)[-1][len("apqc_"):].split("_", 1)[0]
        for f in files if "/slices/" in f)
    if len(set(slices)) == 1:
        return slices[0]
    if slices:
        return "shared"
    return "other"


def build() -> list:
    import rdflib

    graph = load()
    check_anchors(graph)

    by_kind = [(kind, descendants(graph, anchors))
               for kind, anchors, _name in KIND_ANCHORS]
    declared, texts = per_file()
    conflicts = {"label": [], "definition": []}

    typed: dict = {}
    for subject, obj in graph.subject_objects(rdflib.URIRef(RDF_TYPE)):
        if isinstance(subject, rdflib.URIRef) and str(subject).startswith(EX):
            typed.setdefault(str(subject), set()).add(str(obj))

    def kind_of(iri: str) -> str:
        types = typed.get(iri, set())
        if SKOS_ + "Concept" in types:
            return "catalog"
        if types & {OWL_ + "ObjectProperty", OWL_ + "DatatypeProperty",
                    OWL_ + "AnnotationProperty"}:
            return "property"
        if OWL_ + "NamedIndividual" in types and OWL_ + "Class" not in types:
            return "individual"
        if "APQC_ontology/apqc-ext.ttl" in declared.get(iri, ()):
            return "act-genus"
        for kind, members in by_kind:
            if iri in members:
                return kind
        return "other"

    def one(predicate: str, subject) -> str:
        values = sorted(clean(o) for o in graph.objects(
            subject, rdflib.URIRef(predicate)))
        return values[0] if values else ""

    def chosen(column: str, iri: str) -> str:
        value, conflicted = pick(texts[column].get(iri, {}))
        if conflicted:
            conflicts[column].append(iri)
        return value

    rows = []
    for iri in sorted(declared):
        subject = rdflib.URIRef(iri)

        parents = sorted(short(str(o)) for o in graph.objects(
            subject, rdflib.URIRef(RDFS_SUBCLASSOF))
            if isinstance(o, rdflib.URIRef))

        wiring = []
        for predicate, prefix in WIRING:
            targets = sorted(short(str(o)) for o in graph.objects(
                subject, rdflib.URIRef(predicate))
                if isinstance(o, rdflib.URIRef))
            if targets:
                wiring.append(prefix + ":" + ",".join(targets))

        definition = chosen("definition", iri)[:DEFINITION_LIMIT]

        rows.append((
            short(iri),
            kind_of(iri),
            section_of(declared[iri]),
            one(EX + "hierarchyID", subject),
            one(EX + "pcfID", subject),
            chosen("label", iri),
            ";".join(parents),
            ";".join(wiring),
            definition,
        ))
    return rows, conflicts


def render(rows: list) -> str:
    lines = ["\t".join(COLUMNS)]
    lines += ["\t".join(row) for row in rows]
    return "\n".join(lines) + "\n"


def target() -> Path:
    return layout.repository_root() / layout.component(COMPONENT).path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="compare the index on disk against a fresh build "
                         "and exit 1 if they differ, without writing")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args(argv)

    rows, conflicts = build()
    text = render(rows)

    counts: dict = {}
    for row in rows:
        counts[row[1]] = counts.get(row[1], 0) + 1
    print("  %d row(s)" % len(rows))
    for kind, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        print("    %-12s %5d" % (kind, count))

    for column in ("label", "definition"):
        found = conflicts[column]
        if found:
            print()
            print("  FINDING (corpus): %d term(s) carry more than one "
                  "distinct %s. "
                  "The slices inline copies of the shared genera and the "
                  "copies have drifted, so the same IRI means different "
                  "things depending on which file is read."
                  % (len(found), column))
            for iri in sorted(found)[:4]:
                print("    %s" % short(iri))
            if len(found) > 4:
                print("    ... and %d more" % (len(found) - 4))

    path = Path(args.out) if args.out else target()
    if not path.is_absolute():
        path = layout.repository_root() / path

    if args.check:
        if not path.is_file():
            print("  STALE: %s does not exist" % path)
            return 1
        # Compared as text with line endings normalised. The bytes on
        # disk are checked out through .gitattributes, and a working tree
        # that predates that rule can hold CRLF while the blob is LF --
        # which is a fact about the checkout, not about the index.
        current = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        if current == text:
            print("  the index on disk is what this generator produces")
            return 0
        want = text.splitlines()
        have = current.splitlines()
        differing = [i for i in range(max(len(want), len(have)))
                     if (want[i:i + 1] or [None]) != (have[i:i + 1] or [None])]
        print("  STALE: %s differs from a fresh build -- %d line(s), "
              "%d on disk vs %d generated"
              % (path.name, len(differing), len(have), len(want)))
        for i in differing[:5]:
            print("    line %d" % (i + 1))
            print("      on disk:   %s" % (have[i][:120] if i < len(have)
                                           else "(absent)"))
            print("      generated: %s" % (want[i][:120] if i < len(want)
                                           else "(absent)"))
        return 1

    path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(text)
    root = layout.repository_root()
    shown = (path.relative_to(root).as_posix()
             if path.is_relative_to(root) else str(path))
    print("  wrote %s" % shown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
