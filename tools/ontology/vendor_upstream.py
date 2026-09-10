# SPDX-License-Identifier: Apache-2.0
"""Vendor the parts of BFO and CCO that this repository's shapes walk.

    python tools/ontology/vendor_upstream.py            # offline verify
    python tools/ontology/vendor_upstream.py --rebuild  # fetch and rewrite
    python tools/ontology/vendor_upstream.py --confirm  # fetch and compare

WHY THIS EXISTS

The shapes ask reachability questions: does this capability reach
cco:ont00001379 through rdfs:subClassOf, does this role reach
obo:BFO_0000023. The corpus asserts the first link -- AnalyticsCapability
subClassOf cco:ont00000568 -- and then the chain stops, because CCO is
not here. Every capability therefore failed, and the validation report
said 202 violations in a voice that sounded like defects in the ontology.

Measured before this landed: 10 of 116 capability classes reached the
anchor. With the upstream in scope, 116 of 116. The 106 in between were a
property of the scope, not of the ontology.

WHAT IS SELECTED

  seeds     every BFO or CCO term named by the authored ontology or by
            the shapes, including the ones that appear only inside SPARQL
            text -- a constraint naming a class in a query depends on it
            exactly as much as one naming it as an IRI.

  closure   the transitive named ancestors and relatives of those seeds
            along rdfs:subClassOf, rdfs:subPropertyOf, owl:inverseOf,
            rdfs:domain and rdfs:range. This is what gives the shapes a
            chain to walk.

  stubs     any other upstream term mentioned by a copied triple, given a
            type declaration and a label and nothing else. Without this
            the extract would reference terms it does not describe, and
            the check for unresolved vocabulary would still fire -- on
            the extract's own annotations.

WHAT IS NOT SELECTED, AND WHAT THAT COSTS

Every axiom whose object is a blank node is dropped: OWL restrictions,
equivalent-class expressions, and the domain and range declarations
written as unions. That is a deliberate narrowing and it has a
consequence worth stating plainly, because the failure mode is a check
that certifies more than it proves:

    A reasoner over this repository plus these extracts derives strictly
    less than one over this repository plus the full upstream. It cannot
    be used to claim the ontology is consistent with BFO or CCO. It
    supports the subClassOf reachability the shapes ask about, and that
    is the claim these files are good for.

The count of dropped axioms is recorded in the manifest rather than
described here, so the size of the omission is a number that moves.

DETERMINISM

The serialiser is written out here rather than delegated, because the
extract's byte digest is recorded and a serialiser that reorders or
re-escapes between library versions would make that digest a measurement
of the library. Triples are sorted, blank nodes are absent by
construction, and literals are escaped by a function in this file. The
round trip is checked on every build: the emitted text is parsed back and
required to carry the same triples that went in.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import layout  # noqa: E402

FORMAT_VERSION = 1
GENERATOR = "tools/ontology/vendor_upstream.py"
PINS = "config/upstream-sources.yaml"
MANIFEST = "config/upstream-extracts.json"
NOTICE = "vendor/NOTICE.md"
CACHE = ".upstream-cache"

RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
OWL = "http://www.w3.org/2002/07/owl#"
DCTERMS = "http://purl.org/dc/terms/"
SKOS = "http://www.w3.org/2004/02/skos/core#"

#: Edges the closure follows. These are the ones a shape can walk or a
#: reader needs in order to place a term; annotation predicates are
#: copied but not followed, or the closure would be the whole ontology.
STRUCTURAL = (
    RDFS + "subClassOf", RDFS + "subPropertyOf", OWL + "inverseOf",
    RDFS + "domain", RDFS + "range",
)

#: Copied for a stub term. A stub says what kind of thing it is and what
#: it is called, which is enough for the reference to resolve and not
#: enough to imply the extract describes it.
STUB_PREDICATES = (RDF + "type", RDFS + "label")

PREFIXES = (
    ("rdf", RDF), ("rdfs", RDFS), ("owl", OWL), ("skos", SKOS),
    ("dcterms", DCTERMS),
    ("xsd", "http://www.w3.org/2001/XMLSchema#"),
    ("obo", "http://purl.obolibrary.org/obo/"),
    ("cco", "https://www.commoncoreontologies.org/"),
)

EXTRACT_BASE = "https://fandaws.com/ontology/vendor/"

_LOCAL = re.compile(r"^[A-Za-z_][A-Za-z0-9_\-]*$")


class Refused(SystemExit):
    """Raised rather than vendoring something unverified."""


# ------------------------------------------------------------- pins


def sources() -> list[dict]:
    import yaml

    root = layout.repository_root()
    raw = yaml.safe_load((root / PINS).read_text(encoding="utf-8")) or {}
    declared = raw.get("sources") or []
    if not declared:
        raise Refused(PINS + " declares no sources")
    for entry in declared:
        for required in ("id", "url", "commit", "sha256", "namespace",
                         "extract", "licence"):
            if not entry.get(required):
                raise Refused("a source in %s declares no %r: %r"
                              % (PINS, required, entry.get("id", entry)))
        if entry["commit"] not in entry["url"]:
            raise Refused(
                "%s pins commit %s but its url does not name it, so the "
                "url is not pinned to that commit"
                % (entry["id"], entry["commit"]))
    return declared


def sha256_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(source: dict, cache: Path) -> bytes:
    """The pinned bytes, from the cache or the network, digest checked.

    The url names a commit, so what it serves cannot change. The digest
    is checked anyway: a proxy, a corporate TLS appliance or a partial
    download are all things that produce different bytes from the same
    url, and none of them announce themselves.
    """
    cache.mkdir(parents=True, exist_ok=True)
    local = cache / (source["id"] + ".ttl")
    if local.is_file():
        data = local.read_bytes()
        if sha256_of(data) == source["sha256"]:
            return data
        local.unlink()

    with urllib.request.urlopen(source["url"], timeout=180) as response:
        data = response.read()
    got = sha256_of(data)
    if got != source["sha256"]:
        raise Refused(
            "%s: %s served %d bytes digesting to %s, but %s pins %s. "
            "Refusing to vendor bytes that are not the pinned ones."
            % (source["id"], source["url"], len(data), got, PINS,
               source["sha256"]))
    local.write_bytes(data)
    return data


# --------------------------------------------------------- selection


def seed_terms(namespaces: tuple) -> set:
    """Upstream IRIs the corpus and the shapes name.

    The shapes are read twice, as a graph and as text. A SPARQL
    constraint that filters on cco:ont00001921 mentions that term inside
    a string literal, so a graph-only sweep does not see it and the
    extract would silently omit exactly the terms the constraints run on.
    """
    import rdflib

    found = set()

    def harvest(graph):
        for triple in graph:
            for term in triple:
                if (isinstance(term, rdflib.URIRef)
                        and str(term).startswith(namespaces)):
                    found.add(str(term))

    data = rdflib.Graph()
    for path in layout.ontology_files():
        data.parse(path, format="turtle")
    harvest(data)

    for entry in layout.components("ontology-validation"):
        path = entry.resolve()
        shapes = rdflib.Graph()
        shapes.parse(path, format="turtle")
        harvest(shapes)
        text = path.read_text(encoding="utf-8")
        for namespace in namespaces:
            found.update(re.findall(re.escape(namespace) + r"[A-Za-z0-9_]+",
                                    text))
    return found


def select(upstream, seeds: set, namespaces: tuple):
    """Seeds, their structural closure, and the stubs that follow.

    Returns (full, stubs, dropped) where `full` are terms whose ground
    description is copied whole and `stubs` are terms mentioned by those
    descriptions and given a declaration only.
    """
    import rdflib

    def is_upstream(term):
        return (isinstance(term, rdflib.URIRef)
                and str(term).startswith(namespaces))

    described = {s for s in seeds
                 if list(upstream.predicate_objects(rdflib.URIRef(s)))}
    undescribed = sorted(seeds - described)
    if undescribed:
        raise Refused(
            "%d term(s) are referenced here but described by no pinned "
            "upstream, so vendoring cannot resolve them:\n  %s"
            % (len(undescribed), "\n  ".join(undescribed)))

    full = set(described)
    frontier = set(full)
    while frontier:
        nxt = set()
        for iri in frontier:
            subject = rdflib.URIRef(iri)
            for predicate in STRUCTURAL:
                for obj in upstream.objects(subject,
                                            rdflib.URIRef(predicate)):
                    if is_upstream(obj) and str(obj) not in full:
                        nxt.add(str(obj))
            for other in upstream.subjects(rdflib.URIRef(OWL + "inverseOf"),
                                           subject):
                if is_upstream(other) and str(other) not in full:
                    nxt.add(str(other))
        full |= nxt
        frontier = nxt

    dropped = 0
    mentioned = set()
    for iri in full:
        for predicate, obj in upstream.predicate_objects(rdflib.URIRef(iri)):
            if isinstance(obj, rdflib.BNode):
                dropped += 1
                continue
            for term in (predicate, obj):
                if is_upstream(term):
                    mentioned.add(str(term))

    return full, sorted(mentioned - full), dropped


def triples_for(upstream, full: set, stubs: list) -> list:
    """Ground triples only. Blank nodes are dropped, and counted above."""
    import rdflib

    out = []
    for iri in sorted(full):
        subject = rdflib.URIRef(iri)
        for predicate, obj in upstream.predicate_objects(subject):
            if isinstance(obj, rdflib.BNode):
                continue
            out.append((subject, predicate, obj))
    for iri in stubs:
        subject = rdflib.URIRef(iri)
        for predicate in STUB_PREDICATES:
            for obj in upstream.objects(subject, rdflib.URIRef(predicate)):
                if not isinstance(obj, rdflib.BNode):
                    out.append((subject, rdflib.URIRef(predicate), obj))
    return out


# ------------------------------------------------------- serialising


def qname(iri: str) -> str:
    for prefix, namespace in PREFIXES:
        if iri.startswith(namespace):
            local = iri[len(namespace):]
            if _LOCAL.match(local):
                return prefix + ":" + local
    return "<" + iri + ">"


def escape(text: str) -> str:
    """Turtle string escaping, written here rather than borrowed.

    The extract's digest is recorded, so the escaping has to be a
    property of this file and not of whichever rdflib is installed. Every
    literal is emitted on one line in the short form; a newline inside a
    definition becomes a backslash-n rather than a triple-quoted block.
    """
    out = text.replace(chr(92), chr(92) * 2).replace('"', chr(92) + '"')
    return (out.replace(chr(13), chr(92) + "r")
               .replace(chr(10), chr(92) + "n")
               .replace(chr(9), chr(92) + "t"))


def term_text(term) -> str:
    import rdflib

    if isinstance(term, rdflib.URIRef):
        return qname(str(term))
    if isinstance(term, rdflib.Literal):
        body = '"' + escape(str(term)) + '"'
        if term.language:
            return body + "@" + term.language
        if term.datatype:
            return body + "^^" + qname(str(term.datatype))
        return body
    raise Refused("a blank node reached the serialiser: %r" % (term,))


def serialise(triples: list, header: list) -> str:
    lines = ["# " + line if line else "#" for line in header]
    lines.append("")
    for prefix, namespace in PREFIXES:
        lines.append("@prefix %-8s <%s> ." % (prefix + ":", namespace))
    lines.append("")

    rows = sorted({(term_text(s), term_text(p), term_text(o))
                   for s, p, o in triples})
    current = None
    for subject, predicate, obj in rows:
        if subject != current:
            if current is not None:
                lines.append("")
            current = subject
        lines.append("%s %s %s ." % (subject, predicate, obj))
    return chr(10).join(lines) + chr(10)


def sortable(obj) -> str:
    import rdflib

    if isinstance(obj, rdflib.Literal):
        return "L%s|%s|%s" % (obj.language or "", obj.datatype or "", obj)
    return str(obj)


def round_trip(text: str, triples: list) -> None:
    """The emitted file must carry the triples that went into it."""
    import rdflib

    back = rdflib.Graph()
    back.parse(data=text, format="turtle")
    want = {(str(s), str(p), sortable(o)) for s, p, o in triples}
    got = {(str(s), str(p), sortable(o)) for s, p, o in back}
    if want != got:
        missing = sorted(want - got)[:3]
        extra = sorted(got - want)[:3]
        raise Refused(
            "the serialised extract does not reparse to what was "
            "selected: %d missing, %d unexpected. e.g. missing %r, "
            "unexpected %r" % (len(want - got), len(got - want),
                               missing, extra))


# ------------------------------------------------------------ header


def licence_as_stated(upstream, source: dict) -> str:
    """What the source file itself says its licence is.

    The SPDX identifier in the pins file is a claim by whoever wrote it.
    This is the same claim checked against the artifact: the substring
    the pin declares must appear in the upstream's own dcterms:license.
    """
    import rdflib

    predicate = rdflib.URIRef(DCTERMS + "license")
    stated = sorted({str(o) for _s, o in upstream.subject_objects(predicate)})
    needle = source["licence"]["licence_statement_contains"]
    matching = [value for value in stated if needle in value]
    if not matching:
        raise Refused(
            "%s: the pinned source states its licence as %s, and none of "
            "those contains %r, which %s declares. Refusing to vendor "
            "under a licence the artifact does not state."
            % (source["id"], stated or "nothing", needle, PINS))
    return matching[0]


def header_lines(source: dict, stated: str, counts: dict) -> list:
    licence = source["licence"]
    return [
        "Generated by %s -- do not edit." % GENERATOR,
        "",
        "A partial extract of %s, pinned." % source["project"],
        "",
        "  release     %s" % source["release"],
        "  commit      %s" % source["commit"],
        "  source      %s" % source["url"],
        "  sha256      %s" % source["sha256"],
        "  licence     %s (%s)" % (licence["spdx"], licence["url"]),
        "  as stated   %s" % stated,
        "",
        licence["attribution"].strip(),
        "",
        "This is not %s. It carries %d terms described in full and %d"
        % (source["project"], counts["full"], counts["stubs"]),
        "declared as stubs, selected because this repository names them or",
        "because a selected term's ancestry passes through them.",
        "",
        "%d axioms about the selected terms were dropped: every one whose"
        % counts["dropped"],
        "object is an anonymous class expression. A reasoner over this file",
        "therefore derives less than one over the upstream, and it cannot be",
        "used to claim consistency with %s." % source["project"],
    ]


def ontology_triples(source: dict, stated: str, counts: dict) -> list:
    import rdflib

    iri = rdflib.URIRef(EXTRACT_BASE + Path(source["extract"]).stem)
    licence = source["licence"]
    return [
        (iri, rdflib.URIRef(RDF + "type"), rdflib.URIRef(OWL + "Ontology")),
        (iri, rdflib.URIRef(OWL + "versionInfo"),
         rdflib.Literal("%s %s, partial extract for the Application "
                        "Requirement Ontology"
                        % (source["project"], source["release"]), lang="en")),
        (iri, rdflib.URIRef(DCTERMS + "source"), rdflib.URIRef(source["url"])),
        (iri, rdflib.URIRef(DCTERMS + "license"),
         rdflib.URIRef(licence["url"])),
        (iri, rdflib.URIRef(RDFS + "comment"),
         rdflib.Literal(
             "Partial extract, not the upstream ontology. %d axioms whose "
             "object is an anonymous class expression were dropped, so a "
             "reasoner over this file derives less than one over %s and "
             "cannot be used to claim consistency with it. Upstream "
             "licence as stated by the source: %s"
             % (counts["dropped"], source["project"], stated), lang="en")),
        (rdflib.URIRef(DCTERMS + "source"), rdflib.URIRef(RDF + "type"),
         rdflib.URIRef(OWL + "AnnotationProperty")),
        (rdflib.URIRef(DCTERMS + "license"), rdflib.URIRef(RDF + "type"),
         rdflib.URIRef(OWL + "AnnotationProperty")),
    ]


# ------------------------------------------------------------- build


def build(cache: Path) -> dict:
    import rdflib

    declared = sources()
    namespaces = tuple(entry["namespace"] for entry in declared)

    upstream = rdflib.Graph()
    per_source = {}
    for entry in declared:
        data = fetch(entry, cache)
        graph = rdflib.Graph()
        graph.parse(data=data.decode("utf-8"), format="turtle")
        per_source[entry["id"]] = graph
        for triple in graph:
            upstream.add(triple)

    seeds = seed_terms(namespaces)
    full, stubs, dropped = select(upstream, seeds, namespaces)
    selected = triples_for(upstream, full, stubs)

    built = {}
    for entry in declared:
        namespace = entry["namespace"]
        mine = [t for t in selected if str(t[0]).startswith(namespace)]
        my_full = sorted(i for i in full if i.startswith(namespace))
        my_stubs = sorted(i for i in stubs if i.startswith(namespace))
        my_dropped = sum(
            1 for iri in my_full
            for _p, o in upstream.predicate_objects(rdflib.URIRef(iri))
            if isinstance(o, rdflib.BNode))
        counts = {"full": len(my_full), "stubs": len(my_stubs),
                  "dropped": my_dropped}
        stated = licence_as_stated(per_source[entry["id"]], entry)
        mine = mine + ontology_triples(entry, stated, counts)
        text = serialise(mine, header_lines(entry, stated, counts))
        round_trip(text, mine)
        built[entry["id"]] = {
            "source": entry,
            "text": text,
            "counts": counts,
            "stated_licence": stated,
            "seeds": sorted(s for s in seeds if s.startswith(namespace)),
            "triples": len(mine),
        }

    built["_totals"] = {"seeds": len(seeds), "full": len(full),
                        "stubs": len(stubs), "dropped": dropped}
    return built


def manifest_of(built: dict) -> dict:
    root = layout.repository_root()
    extracts = {}
    for key, record in sorted(built.items()):
        if key.startswith("_"):
            continue
        entry = record["source"]
        path = root / entry["extract"]
        data = record["text"].encode("utf-8")
        extracts[key] = {
            "extract": entry["extract"],
            "project": entry["project"],
            "release": entry["release"],
            "commit": entry["commit"],
            "source_url": entry["url"],
            "source_sha256": entry["sha256"],
            "licence_spdx": entry["licence"]["spdx"],
            "licence_url": entry["licence"]["url"],
            "licence_as_stated_by_source": record["stated_licence"],
            "namespace": entry["namespace"],
            "seed_terms": record["seeds"],
            "terms_described_in_full": record["counts"]["full"],
            "terms_declared_as_stubs": record["counts"]["stubs"],
            "axioms_dropped_anonymous_object": record["counts"]["dropped"],
            "triples": record["triples"],
            "extract_sha256": sha256_of(data),
            "extract_on_disk_matches": (
                path.is_file()
                and sha256_of(path.read_bytes()) == sha256_of(data)),
        }
    return {
        "format_version": FORMAT_VERSION,
        "generated_by": GENERATOR,
        "pins": PINS,
        "totals": built["_totals"],
        "extracts": extracts,
        "not_covered": [
            "Axioms whose object is an anonymous class expression are "
            "dropped. OWL restrictions, equivalent-class expressions and "
            "union domains and ranges are therefore absent, and a reasoner "
            "over these extracts derives less than one over the upstream.",
            "These extracts cannot be used to claim the ontology is "
            "consistent with BFO or CCO. They support the subClassOf "
            "reachability the shapes ask about.",
            "Only terms this repository names, and their structural "
            "ancestry, are present. A new upstream reference in the corpus "
            "is not covered until this is rebuilt; "
            "tests/test_upstream_vendoring.py fails when that happens.",
            "owl:imports is not emitted. Validation is offline by design, "
            "so nothing resolves over the network at check time.",
        ],
    }


def notice_of(built: dict) -> str:
    """The attribution both upstream licences require.

    Generated rather than written, because an attribution file is exactly
    the kind of document that is correct on the day it is added and
    silently wrong after the next source is vendored. What keeps that
    honest is not this function -- it is the licensing tool, which reads
    the pins and requires each declared attribution to appear here.
    """
    lines = [
        "# Third-party notices",
        "",
        "This repository redistributes partial extracts of the ontologies",
        "below. Both licences require attribution, and this file is that",
        "attribution. It is generated by `" + GENERATOR + "`",
        "from `" + PINS + "`; the licensing check reads the same pins and",
        "fails if an attribution declared there is missing here.",
        "",
        "The extracts are not the upstream ontologies. Each carries only the",
        "terms this repository names plus their structural ancestry, and",
        "drops every axiom whose object is an anonymous class expression.",
        "See the header of each file, and `" + MANIFEST + "`.",
        "",
    ]
    for key, record in sorted(built.items()):
        if key.startswith("_"):
            continue
        entry = record["source"]
        lines += [
            "## " + entry["project"] + " " + entry["release"],
            "",
            entry["licence"]["attribution"].strip(),
            "",
            "- extract: `" + entry["extract"] + "`",
            "- source: " + entry["url"],
            "- commit: `" + entry["commit"] + "`",
            "- licence: " + entry["licence"]["spdx"] + " -- "
            + entry["licence"]["url"],
            "- as stated by the source: " + record["stated_licence"],
            "- %d terms in full, %d stubs, %d axioms dropped"
            % (record["counts"]["full"], record["counts"]["stubs"],
               record["counts"]["dropped"]),
            "",
        ]
    return chr(10).join(lines)


# ------------------------------------------------------------ verify


def verify() -> dict:
    """Offline: are the extracts on disk sufficient and self-consistent?

    Deliberately does not need the network, because this is what runs on
    every push. Rebuilding from upstream is a separate mode -- see
    --confirm -- and it is the one that proves these files are derived
    rather than merely present.
    """
    import rdflib

    root = layout.repository_root()
    declared = sources()
    namespaces = tuple(entry["namespace"] for entry in declared)
    manifest_path = root / MANIFEST
    if not manifest_path.is_file():
        raise Refused(MANIFEST + " is missing; run with --rebuild")
    recorded = json.loads(manifest_path.read_text(encoding="utf-8"))

    vendored = rdflib.Graph()
    findings = []
    if not (root / NOTICE).is_file():
        findings.append(
            NOTICE + " is missing. Both upstream licences require "
            "attribution, and redistributing an extract without it is a "
            "breach whatever the header of the extract says.")
    for entry in declared:
        path = root / entry["extract"]
        if not path.is_file():
            findings.append("%s: %s is missing"
                            % (entry["id"], entry["extract"]))
            continue
        data = path.read_bytes()
        digest = sha256_of(data)
        want = recorded["extracts"].get(entry["id"], {}).get("extract_sha256")
        if digest != want:
            findings.append(
                "%s: %s digests to %s but %s records %s"
                % (entry["id"], entry["extract"], digest[:16], MANIFEST,
                   (want or "nothing")[:16]))
        vendored.parse(data=data.decode("utf-8"), format="turtle")

    seeds = seed_terms(namespaces)
    unresolved = sorted(
        iri for iri in seeds
        if not list(vendored.predicate_objects(rdflib.URIRef(iri))))
    if unresolved:
        findings.append(
            "%d upstream term(s) named here are not described by any "
            "extract, so a shape walking through them still has no chain: "
            "%s" % (len(unresolved), ", ".join(unresolved[:6])))

    dangling = set()
    for triple in vendored:
        for term in triple:
            if (isinstance(term, rdflib.URIRef)
                    and str(term).startswith(namespaces)
                    and not list(vendored.predicate_objects(term))):
                dangling.add(str(term))
    dangling = sorted(dangling)
    if dangling:
        findings.append(
            "%d term(s) are mentioned by an extract and described by no "
            "extract: %s" % (len(dangling), ", ".join(dangling[:6])))

    return {
        "seeds": len(seeds),
        "vendored_triples": len(vendored),
        "unresolved_seeds": unresolved,
        "dangling_references": dangling,
        "findings": findings,
        "ok": not findings,
    }


# --------------------------------------------------------------- cli


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true",
                    help="fetch the pinned upstreams and rewrite the "
                         "extracts and the manifest")
    ap.add_argument("--confirm", action="store_true",
                    help="fetch and rebuild in memory, then require the "
                         "files on disk to be byte-identical. This is what "
                         "shows the extracts are derived from the pins "
                         "rather than edited by hand")
    ap.add_argument("--cache", default=None)
    args = ap.parse_args(argv)

    root = layout.repository_root()
    cache = Path(args.cache) if args.cache else (root / CACHE)

    if not (args.rebuild or args.confirm):
        record = verify()
        print("  %d seed term(s), %d vendored triple(s)"
              % (record["seeds"], record["vendored_triples"]))
        for finding in record["findings"]:
            print("  FINDING: %s" % finding)
        if record["ok"]:
            print("  extracts present, digests match, every reference "
                  "resolves")
        return 0 if record["ok"] else 1

    built = build(cache)
    totals = built["_totals"]
    print("  %d seed(s) -> %d term(s) in full, %d stub(s), %d axiom(s) "
          "dropped" % (totals["seeds"], totals["full"], totals["stubs"],
                       totals["dropped"]))

    manifest = manifest_of(built)
    differing = [key for key, record in manifest["extracts"].items()
                 if not record["extract_on_disk_matches"]]

    for key, record in sorted(manifest["extracts"].items()):
        print("    %-4s %-40s %6d triple(s)  %s"
              % (key, record["extract"], record["triples"],
                 "same" if record["extract_on_disk_matches"] else "DIFFERS"))

    notice = notice_of(built)
    notice_path = root / NOTICE
    if not (notice_path.is_file()
            and notice_path.read_bytes() == notice.encode("utf-8")):
        differing.append(NOTICE)
        print("    %-4s %-40s %6s          DIFFERS" % ("", NOTICE, ""))

    if args.confirm:
        if differing:
            print()
            print("  FINDING: %d extract(s) on disk are not what rebuilding "
                  "from the pinned sources produces: %s"
                  % (len(differing), ", ".join(sorted(differing))))
            return 1
        print("  every extract is byte-identical to a fresh build from the "
              "pinned upstreams")
        return 0

    for key, record in sorted(built.items()):
        if key.startswith("_"):
            continue
        target = root / record["source"]["extract"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(record["text"].encode("utf-8"))
        print("  wrote %s" % record["source"]["extract"])

    notice_path.parent.mkdir(parents=True, exist_ok=True)
    notice_path.write_bytes(notice.encode("utf-8"))
    print("  wrote %s" % NOTICE)

    manifest = manifest_of(built)
    (root / MANIFEST).write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True,
                   ensure_ascii=False).encode("utf-8") + b"\n")
    print("  wrote %s" % MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
