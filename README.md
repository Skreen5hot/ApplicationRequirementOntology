# Application Requirement Ontology

This repository develops the **Application Requirement Ontology** and supporting models for representing application specifications as machine-readable **Specification Graphs**.

The ontology is intended to describe requirements, stakeholders, capabilities, constraints, interfaces, acceptance criteria, verification evidence, and the traceability relationships among them. Specification Graphs will provide a structured intermediate representation that software tools and agents can validate, query, and transform.

## Foundations

The ontology will use:

- **Basic Formal Ontology (BFO)** as its top-level ontology.
- **Common Core Ontologies (CCO)** as a principled framework for reusable mid-level concepts and relations.

## Reference Materials

Development will be informed by:

- **ISO/IEC/IEEE 29148:2018(E), Systems and software engineering — Life cycle processes — Requirements engineering**.
- **NASA Systems Engineering Handbook**.
- **NASA Software Engineering and Software Assurance Handbook**.

These publications are reference sources; this repository does not redistribute them or claim conformance with, certification by, or endorsement from ISO, IEC, IEEE, or NASA. Original ontology definitions will be used unless a source explicitly permits reuse.

## Planned Outputs

- An application-requirements ontology in standard Semantic Web formats.
- JSON-LD contexts and models for Specification Graphs.
- Constraint and validation rules for graph instances.
- Traceable mappings between source specifications and ontology concepts.
- Examples demonstrating prose specifications transformed into Specification Graphs.

## Status

This project is experimental and under active development. Its vocabulary, models, and validation rules may change as the ontology is tested against real specifications.
