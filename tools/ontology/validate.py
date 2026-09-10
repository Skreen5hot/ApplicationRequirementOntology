# SPDX-License-Identifier: Apache-2.0
"""Run the SHACL shapes, and check that they can still fail.

    python tools/ontology/validate.py
    python tools/ontology/validate.py -o config/validation-report.json

Two rungs, and the second is the one that makes the first mean anything.

  conformance   the authored ontology validated against every shape set.
                Violations are findings.

  falsification the bad-examples fixture validated against the same
                shapes. It is built to break them, so violations here are
                the expected result and their *absence* is the finding.

A shape set that reports no violations is ambiguous on its own: the data
might be clean, or the constraint might be selecting nothing. That
happens more easily than it sounds -- a SPARQL constraint filtering on a
namespace prefix string still runs when the string is stale, matches
nothing, and reports success. This repository moved namespaces recently
and had exactly that construct in it, which is why the second rung is
not optional.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import layout  # noqa: E402

FORMAT_VERSION = 1
GENERATOR = "tools/ontology/validate.py"


def load(paths) -> "rdflib.Graph":
    import rdflib

    graph = rdflib.Graph()
    for path in paths:
        graph.parse(path, format="turtle")
    return graph


def shape_sets() -> dict[str, Path]:
    return {c.id: c.resolve()
            for c in layout.components("ontology-validation")}


def run(data, shapes) -> dict:
    from pyshacl import validate as shacl

    conforms, results_graph, results_text = shacl(
        data_graph=data, shacl_graph=shapes, inference="none",
        abort_on_first=False, meta_shacl=False, advanced=True,
        debug=False)

    import rdflib

    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    violations = []
    for result in results_graph.subjects(rdflib.RDF.type, SH.ValidationResult):
        focus = results_graph.value(result, SH.focusNode)
        source = results_graph.value(result, SH.sourceShape)
        message = results_graph.value(result, SH.resultMessage)
        severity = results_graph.value(result, SH.resultSeverity)
        violations.append({
            "focus": str(focus) if focus else None,
            "shape": str(source) if source else None,
            "severity": str(severity).rsplit("#", 1)[-1] if severity else None,
            "message": (str(message)[:200] if message else None),
        })
    violations.sort(key=lambda v: (v["shape"] or "", v["focus"] or ""))
    return {"conforms": bool(conforms), "violations": violations,
            "text": results_text[:4000]}


#: Namespaces the corpus builds on but does not contain. A constraint
#: that walks subClassOf+ into one of these cannot be evaluated without
#: it, and will report every subject as violating.
UPSTREAM = {
    "https://www.commoncoreontologies.org/": "CCO",
    "http://purl.obolibrary.org/obo/": "BFO/OBO",
}


def unresolved_vocabularies(data) -> dict:
    """Upstream terms referenced but not described in scope.

    This is the difference between "the ontology is wrong" and "the
    question was asked without the vocabulary needed to answer it". A
    shape requiring a class to reach a CCO anchor via subClassOf+ has no
    chain to walk when CCO is absent, so it reports every subject as
    violating -- and the report looks exactly like a real defect.
    """
    import rdflib

    out = {}
    for prefix, name in UPSTREAM.items():
        referenced = {str(t) for triple in data for t in triple
                      if isinstance(t, rdflib.URIRef)
                      and str(t).startswith(prefix)}
        described = {iri for iri in referenced
                     if list(data.predicate_objects(rdflib.URIRef(iri)))}
        out[name] = {
            "prefix": prefix,
            "referenced": len(referenced),
            "described_in_scope": len(described),
            "resolvable": len(referenced) == len(described),
        }
    return out


def shapes_depend_on(path: Path) -> list[str]:
    """Which upstream vocabularies a shape set reasons over.

    Read from the shapes' own text, including the SPARQL inside them,
    because a constraint naming a CCO class in a query depends on CCO
    just as much as one naming it as an IRI.
    """
    text = path.read_text(encoding="utf-8")
    return sorted(name for prefix, name in UPSTREAM.items()
                  if prefix in text)


def measure() -> dict:
    root = layout.repository_root()
    scope = layout.ontology_files()
    fixture = layout.component("fixture.apqc-bad-examples").resolve()
    sets = shape_sets()
    if not sets:
        raise SystemExit("no ontology-validation component is declared")

    data = load(scope)
    bad = load([fixture])
    vocabularies = unresolved_vocabularies(data)
    missing = sorted(name for name, info in vocabularies.items()
                     if not info["resolvable"])

    rungs = {}
    for name, path in sorted(sets.items()):
        shapes = load([path])
        depends = shapes_depend_on(path)
        blocked = sorted(set(depends) & set(missing))
        corpus = run(data, shapes)
        against_fixture = run(bad, shapes)
        rungs[name] = {
            "shapes": path.relative_to(root).as_posix(),
            "depends_on": depends,
            "blocked_by_missing_vocabulary": blocked,
            # Violations from a shape set that cannot resolve the
            # vocabulary it reasons over are not findings about the
            # ontology, and counting them as such would be a measurement
            # of the harness.
            "evaluable": not blocked,
            "corpus": {
                "conforms": corpus["conforms"],
                "violations": len(corpus["violations"]),
                "detail": corpus["violations"][:20],
            },
            "fixture": {
                "conforms": against_fixture["conforms"],
                "violations": len(against_fixture["violations"]),
                "detail": against_fixture["violations"][:10],
            },
            # The fixture conforming means the shapes did not fire on data
            # built to break them, which is a broken check reporting
            # success.
            "can_still_fail": not against_fixture["conforms"],
            "fixture_exercises_these_shapes":
                len(against_fixture["violations"]) > 0,
        }

    return {
        "format_version": FORMAT_VERSION,
        "generated_by": GENERATOR,
        "scope": {
            "data_files": len(scope),
            "fixture": fixture.relative_to(root).as_posix(),
            "shape_sets": sorted(sets),
        },
        "upstream_vocabularies": vocabularies,
        "unresolved": missing,
        "rungs": rungs,
        "note": (
            "A shape set reporting no violations is ambiguous by itself: "
            "clean data and a constraint selecting nothing look the same. "
            "can_still_fail is that ambiguity resolved -- the same shapes "
            "run against data built to break them."),
        # Only evaluable rungs can pass or fail. A rung blocked on a
        # missing vocabulary is neither, and saying so is the whole
        # point -- its violation count describes the scope, not the
        # ontology.
        "evaluable_rungs": sorted(n for n, r in rungs.items()
                                  if r["evaluable"]),
        "blocked_rungs": sorted(n for n, r in rungs.items()
                                if not r["evaluable"]),
        # `all()` over an empty sequence is True, so a ladder where every
        # rung is blocked would have reported success having evaluated
        # nothing. It has not passed; it has not run.
        "passed": (any(r["evaluable"] for r in rungs.values())
                   and all(r["corpus"]["conforms"] and r["can_still_fail"]
                           for r in rungs.values() if r["evaluable"])),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args(argv)

    record = measure()
    print("  %d data file(s), %d shape set(s)"
          % (record["scope"]["data_files"], len(record["rungs"])))
    print()
    if record["unresolved"]:
        print("  upstream vocabulary not in scope: %s"
              % ", ".join(record["unresolved"]))
        for name, info in sorted(record["upstream_vocabularies"].items()):
            print("    %-8s %d referenced, %d described in scope"
                  % (name, info["referenced"], info["described_in_scope"]))
        print()

    for name, rung in sorted(record["rungs"].items()):
        corpus, fixture = rung["corpus"], rung["fixture"]
        print("  %s" % name)
        if not rung["evaluable"]:
            print("    NOT EVALUABLE -- reasons over %s, which is not in "
                  "scope" % ", ".join(rung["blocked_by_missing_vocabulary"]))
            print("    %d reported violation(s) describe the scope, not the "
                  "ontology" % corpus["violations"])
            continue
        print("    corpus  %-9s %d violation(s)"
              % ("conforms" if corpus["conforms"] else "VIOLATIONS",
                 corpus["violations"]))
        print("    fixture %-9s %d violation(s)  %s"
              % ("conforms" if fixture["conforms"] else "rejected",
                 fixture["violations"],
                 "" if rung["can_still_fail"]
                 else "<- the shapes did not fire on data built to break "
                      "them"))
    print()
    if not record["evaluable_rungs"]:
        print("  passed: %s -- nothing could be evaluated, so this is not "
              "a result" % record["passed"])
    else:
        print("  passed: %s  (%d of %d rung(s) evaluable)"
              % (record["passed"], len(record["evaluable_rungs"]),
                 len(record["rungs"])))

    if args.out:
        target = Path(args.out)
        target = target if target.is_absolute() else (
            layout.repository_root() / target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(json.dumps(record, indent=2, sort_keys=True,
                                      ensure_ascii=False).encode("utf-8")
                           + b"\n")
        print("  wrote %s" % args.out)
    return 0 if record["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
