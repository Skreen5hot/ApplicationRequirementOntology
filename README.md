# Application Requirement Ontology

> **New here?** Read [`docs/HANDOFF.md`](docs/HANDOFF.md) first. It states what is actually
> in this repository today and what is not — in particular, that the ARO modules described
> below are specified but not yet written, and that the ontology currently in the tree is
> the APQC foundation they will be built on. [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md)
> is how to run things; [`docs/process/PROCESS.md`](docs/process/PROCESS.md) is why it is
> built this way.

This repository develops the **Application Requirement Ontology** and supporting models for representing application specifications as machine-readable **Specification Graphs**.

The ontology is intended to describe requirements, stakeholders, capabilities, constraints, interfaces, acceptance criteria, verification evidence, and the traceability relationships among them. Specification Graphs will provide a structured intermediate representation that software tools and agents can validate, query, and transform.

## Foundations

The ontology will use:

- **Basic Formal Ontology (BFO)** as its top-level ontology.
- **Common Core Ontologies (CCO)** as a principled framework for reusable mid-level concepts and relations.

Both are vendored under [`vendor/`](vendor/) as pinned partial extracts rather than resolved over the network at validation time. Each carries only the terms this repository names plus their named ancestry, which is what the SHACL constraints walk when they ask whether a capability reaches `cco:Agent Capability`. The extracts are **not** the upstream ontologies: every axiom whose object is an anonymous class expression is dropped, so a reasoner over them derives less than one over BFO or CCO and they cannot be used to claim consistency with either.

Provenance, digests and licences are in [`config/upstream-sources.yaml`](config/upstream-sources.yaml) (the pins) and [`config/upstream-extracts.json`](config/upstream-extracts.json) (what was taken and what was left). Attribution, which both licences require, is in [`vendor/NOTICE.md`](vendor/NOTICE.md) and is checked rather than assumed.

To rebuild them from the pinned sources:

```
python tools/ontology/vendor_upstream.py --rebuild   # fetch and rewrite
python tools/ontology/vendor_upstream.py --confirm   # fetch and compare
python tools/ontology/vendor_upstream.py             # offline verify
```

## Reference Materials

Development will be informed by:

- **ISO/IEC/IEEE 29148:2018(E), Systems and software engineering — Life cycle processes — Requirements engineering**.
- **NASA Systems Engineering Handbook**.
- **NASA Software Engineering and Software Assurance Handbook**.

These publications are reference sources; this repository does not redistribute them or claim conformance with, certification by, or endorsement from ISO, IEC, IEEE, or NASA. Original ontology definitions will be used unless a source explicitly permits reuse.

That is a different disposition from the BFO and CCO extracts above, which **are** redistributed, because their licences permit it with attribution. The distinction is enforced rather than described: `config/repository-layout.yaml` declares the reference material `tracked: false`, and `python tools/licensing/disposition.py --check` fails if any of it is ever committed.

## Planned Outputs

- An application-requirements ontology in standard Semantic Web formats.
- JSON-LD contexts and models for Specification Graphs.
- Constraint and validation rules for graph instances.
- Traceable mappings between source specifications and ontology concepts.
- Examples demonstrating prose specifications transformed into Specification Graphs.

## Status

This project is experimental and under active development. Its vocabulary, models, and validation rules may change as the ontology is tested against real specifications.
