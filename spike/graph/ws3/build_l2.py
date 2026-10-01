"""WS-3 L2 graph -- what the source says about the A9 target, at capability grain (Plan v1.1 s5).

The content below is hand-authored by the dev agent under Amendment 2 (the architect performs 100% span review; the
graph is non-graduating). This script only resolves each cited span LABEL to the fragment id minted for it in
spike/graph/ws3/fragments.json, so an id can never be mistyped, and writes the graph canonically:

    python spike/graph/ws3/build_l2.py                 # writes spike/graph/l2/srs-ws3.graph.jsonld
    python spike/graph/ws3/build_l2.py --check         # exit 1 if the file on disk differs from a rebuild

Target, named by the architect's A9 act (docs/decisions/2026-10-01-a9-ws3-target-naming-act.md): "SRS adjudication
and registration core" -- C-S2 grade, C-S3 adjudicate, C-S7 register -- registered SRS sha256 2428b115...c89450,
lines 43-53 and 73-75, with the supporting rules, components, seams and invariants. Line numbers are against that
digest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAGMENTS = HERE / "fragments.json"
OUT = HERE.parent / "l2" / "srs-ws3.graph.jsonld"
DIGEST = "sha256:2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450"

N = {"role": "Normative", "force": "obligation", "scope": "in-scope"}


def g(label, role="primary", why=None):
    """A grounding citation by span label; the fragment id is resolved at build time."""
    c = {"label": label, "role": role}
    if why:
        c["why"] = why
    return c


def target(kind, name, label=None):
    t = {"@type": "SpecificationTargetDescription", "kind": kind, "name": name}
    if label:
        t["label"] = label
    return t


RECORDS = [
    # ---------------------------------------------------------------- capabilities (the A9 target)
    {
        "@id": "sr:L2:C-S2", "@type": "SpecificationRecord", "title": "C-S2 grade",
        "assertions": [
            {"@id": "a:C-S2:capability", "@type": "Requirement", **N,
             "target": target("capability", "C-S2", "grade"),
             "statement": "The system provides capability C-S2, grade: an agentic capability consisting of one isolated rater invocation.",
             "groundedBy": [g("C-S2.header"),
                            g("J-S1.chain", "context", "places C-S2 as step 2 of first-grade: run twice, isolated, raters A and B, each manifest pinned to the rev"),
                            g("S2.coverage-map", "context", "C-S2 serves J-S1 and J-S2")]},
            {"@id": "a:C-S2:W-CS2-N", "@type": "AcceptanceClause", "witness": "W-CS2-N (nominal)", **N,
             "statement": "Given a headless invocation whose context manifest is exactly {spec@<SHA>, method/v0.4.md, skills/fspec-method}, C-S2 produces a grade record of the form {\"rater\", \"model\", \"manifest_hash\", \"vector\", \"evidence\", \"disposition\", \"readiness\", \"provisional\": true}.",
             "input": "headless invocation with context manifest exactly {spec@<SHA>, method/v0.4.md, skills/fspec-method}",
             "outputs": ["grade record {rater, model, manifest_hash, vector, evidence, disposition, readiness, provisional: true}"],
             "groundedBy": [g("C-S2.W-CS2-N")]},
            {"@id": "a:C-S2:determinism", "@type": "AcceptanceClause", "witness": "C-S2 determinism note", **N,
             "statement": "The vector varies across runs and is masked; the asserted properties are: every score is in {0, 1, 2}; every evidence pointer resolves at the cited rev (checked against derived/); <D> and <R> recompute from the vector per method s6.2; provisional = true on every single-rater record; <H> = sha256 of the manifest.",
             "properties": ["every score in {0, 1, 2}", "every evidence pointer resolves at the cited rev (checked against derived/)",
                            "disposition and readiness recompute from the vector per method s6.2",
                            "provisional = true on every single-rater record", "manifest_hash = sha256 of the manifest"],
             "masks": ["vector"],
             "sourceNote": "cross-run stability of the vector is what O-03 calibration measures, not what this witness asserts (source's own words)",
             "classificationNote": "titled a note, but states properties in the normative register; classified Normative as the slice classified C-S8's note -- the alternative reading (Note) is preserved here",
             "groundedBy": [g("C-S2.determinism")]},
            {"@id": "a:C-S2:W-CS2-D1", "@type": "AcceptanceClause", "witness": "W-CS2-Δ1 (one factor: unresolvable evidence — negative witness)", **N,
             "statement": "Given a grade record citing spec.md:9999, the verifier rejects it with {\"code\": \"G-EVID-01\"}, and no S-S2 crossing occurs -- the absence is the assertion.",
             "input": "grade record citing spec.md:9999",
             "outputs": ["rejection {\"code\": \"G-EVID-01\"}"],
             "properties": ["no S-S2 crossing occurs"],
             "groundedBy": [g("C-S2.W-CS2-D1")]},
            {"@id": "a:C-S2:W-CS2-D2", "@type": "AcceptanceClause", "witness": "W-CS2-Δ2 (one factor: contaminated manifest — witnesses R-S1)", **N,
             "statement": "Given a manifest containing findings/cycle-3/, the invocation is rejected with {\"code\": \"G-ISO-01\"}, and the grade never enters adjudication.",
             "input": "manifest containing findings/cycle-3/",
             "outputs": ["rejection {\"code\": \"G-ISO-01\"}"],
             "properties": ["the grade never enters adjudication"],
             "groundedBy": [g("C-S2.W-CS2-D2"), g("R-S1", "context", "the rule this negative witness enforces")]},
        ],
    },
    {
        "@id": "sr:L2:C-S3", "@type": "SpecificationRecord", "title": "C-S3 adjudicate",
        "assertions": [
            {"@id": "a:C-S3:capability", "@type": "Requirement", **N,
             "target": target("capability", "C-S3", "adjudicate"),
             "statement": "The system provides capability C-S3, adjudicate.",
             "groundedBy": [g("C-S3.header"),
                            g("J-S1.chain", "context", "places C-S3 as step 3 of first-grade: adjudicates the two grade records into an adjudicated report"),
                            g("S2.coverage-map", "context", "C-S3 serves J-S1, J-S2 and J-S3")]},
            {"@id": "a:C-S3:W-CS3-N", "@type": "AcceptanceClause", "witness": "W-CS3-N (nominal)", **N,
             "statement": "Given rater A with P6 = 2 and rater B with P6 = 1 and no zeros elsewhere, C-S3 routes {\"route\": {\"P6\": \"third-rater\"}, \"contested_knockouts\": []}; after rater C, the adjudicated vector carries P6 = C's consensus value and provisional: false.",
             "input": "grade records A (P6 = 2) and B (P6 = 1), no zeros elsewhere; then rater C's record",
             "outputs": ["{\"route\": {\"P6\": \"third-rater\"}, \"contested_knockouts\": []}",
                         "adjudicated vector with P6 = C's consensus value, provisional: false"],
             "diagnostic": "diag:W-CS3-N-third-rater-is-agentic",
             "groundedBy": [g("C-S3.W-CS3-N"), g("R-S4", "context", "the routing rule this witness satisfies")]},
            {"@id": "a:C-S3:determinism", "@type": "AcceptanceClause", "witness": "C-S3 determinism note", **N,
             "statement": "Routing is a pure function of the two committed vectors: bit-stable, recomputable by anyone from the record.",
             "properties": ["routing is a pure function of the two committed vectors", "bit-stable", "recomputable by anyone from the record"],
             "classificationNote": "titled a note, but states a property in the normative register; classified Normative -- the alternative reading (Note) is preserved here",
             "groundedBy": [g("C-S3.determinism"), g("V-S2", "context", "the invariant that pins this property at the report level")]},
            {"@id": "a:C-S3:W-CS3-D1", "@type": "AcceptanceClause", "witness": "W-CS3-Δ1 (one factor: either-rater zero)", **N,
             "statement": "Given rater B scoring P3 = 0, C-S3 returns {\"disposition_line\": \"WITHHELD\", \"contested_knockouts\": [\"P3\"], \"queue\": \"human\"}; no disposition is printed while a knockout is contested (method s6.3).",
             "input": "rater B scores P3 = 0",
             "outputs": ["{\"disposition_line\": \"WITHHELD\", \"contested_knockouts\": [\"P3\"], \"queue\": \"human\"}"],
             "properties": ["no disposition is printed while a knockout is contested"],
             "groundedBy": [g("C-S3.W-CS3-D1"), g("R-S4", "context", "either-rater zero -> contested knockout -> human queue")]},
            {"@id": "a:C-S3:W-CS3-D2", "@type": "AcceptanceClause", "witness": "W-CS3-Δ2 (one factor: verified vacuous-pass report present — witnesses R-S5)", **N,
             "statement": "Given a zero-free adjudicated vector and a replayed stub report on clause <CL>, C-S3 returns {\"disposition_line\": \"SUSPENDED\", \"cause\": \"vacuous-pass:<CL>\", \"queue\": \"human\"}.",
             "input": "zero-free adjudicated vector + replayed stub report on clause <CL>",
             "outputs": ["{\"disposition_line\": \"SUSPENDED\", \"cause\": \"vacuous-pass:<CL>\", \"queue\": \"human\"}"],
             "diagnostic": "diag:W-CS3-D2-needs-a-C-S5-report",
             "groundedBy": [g("C-S3.W-CS3-D2"), g("R-S5", "context", "the rule this witness satisfies")]},
        ],
    },
    {
        "@id": "sr:L2:C-S7", "@type": "SpecificationRecord", "title": "C-S7 register (ledger)",
        "assertions": [
            {"@id": "a:C-S7:capability", "@type": "Requirement", **N,
             "target": target("capability", "C-S7", "register"),
             "statement": "The system provides capability C-S7, register (ledger); this capability plus its store is method O-02.",
             "groundedBy": [g("C-S7.header"),
                            g("J-S1.chain", "context", "places C-S7 as step 4 of first-grade: appends the registration with payload.rev = the rev graded"),
                            g("J-S4.chain", "context", "C-S7 appends the ratification event; ratification exists only as a ledger event citing the exact rev"),
                            g("S2.coverage-map", "context", "C-S7 serves J-S1 and J-S4")]},
            {"@id": "a:C-S7:W-CS7-N", "@type": "AcceptanceClause", "witness": "W-CS7-N (nominal)", **N,
             "statement": "Appending {\"seq\": 7, \"prev\": \"<H6>\", \"kind\": \"registration\", \"payload\": {\"spec\", \"rev\", \"vector\"}, \"hash\": \"<H7>\"} yields an entry where <H7> = sha256(seq || prev || payload) and the full chain verifies from genesis; hashes are masked.",
             "input": "a registration payload {spec, rev, vector} at chain position 7",
             "outputs": ["ledger line {seq, prev, kind: \"registration\", payload, hash}"],
             "properties": ["hash = sha256(seq || prev || payload)", "the full chain verifies from genesis"],
             "masks": ["prev", "hash"],
             "diagnostic": "diag:hash-preimage-encoding-unstated",
             "groundedBy": [g("C-S7.W-CS7-N")]},
            {"@id": "a:C-S7:W-CS7-D1", "@type": "AcceptanceClause", "witness": "W-CS7-Δ1 (negative witness)", **N,
             "statement": "Any rewrite of an existing ledger line makes the hook exit 1 with {\"code\": \"H-LEDGER-01\"}, and chain verification fails loudly on the tampered copy.",
             "input": "a rewrite of an existing ledger line",
             "outputs": ["hook exit 1, {\"code\": \"H-LEDGER-01\"}"],
             "properties": ["chain verification fails loudly on the tampered copy"],
             "groundedBy": [g("C-S7.W-CS7-D1"), g("V-S1", "context", "append-only over ledger/** is the invariant this witness defends")]},
            {"@id": "a:C-S7:determinism", "@type": "AcceptanceClause", "witness": "C-S7 determinism note", **N,
             "statement": "Entries are bit-stable given payload and chain position; hash fields are the only masks, carried with the chain-verification property.",
             "properties": ["entries bit-stable given payload and chain position", "hash fields are the only masks"],
             "classificationNote": "titled a note, but states a property in the normative register; classified Normative -- the alternative reading (Note) is preserved here",
             "groundedBy": [g("C-S7.determinism")]},
        ],
    },
    # ---------------------------------------------------------------- rules (SRS s4), each with its invariant (s7)
    {
        "@id": "sr:L2:R-S1", "@type": "SpecificationRecord", "title": "R-S1 grader isolation (with V-S3)",
        "assertions": [
            {"@id": "a:R-S1:rule", "@type": "Requirement", **N, "target": target("rule", "R-S1", "grader isolation"),
             "statement": "A grading invocation's context MUST contain exactly {spec@rev, method/v0.4.md, skills/fspec-method} -- no prior grades, findings, scores, or revision intent -- and the record MUST carry the manifest hash.",
             "witnessedBy": ["a:C-S2:W-CS2-N", "a:C-S2:W-CS2-D2"],
             "groundedBy": [g("R-S1")]},
            {"@id": "a:V-S3:invariant", "@type": "PrescribedInvariant", **N,
             "statement": "Over every grading invocation: the manifest is a subset of the R-S1 triple, its hash is recorded, and violations are rejected before adjudication.",
             "generator": "n >= 50 runs plus seeded contaminated manifests", "pinnedBy": "a:C-S2:W-CS2-D2",
             "groundedBy": [g("V-S3")]},
        ],
    },
    {
        "@id": "sr:L2:R-S4", "@type": "SpecificationRecord", "title": "R-S4 adjudication routing (with V-S2)",
        "assertions": [
            {"@id": "a:R-S4:rule", "@type": "Requirement", **N, "target": target("rule", "R-S4", "adjudication routing"),
             "statement": "Either-rater zero -> contested knockout -> human queue, disposition withheld. Nonzero disagreement -> third rater; a third-rater tie -> human.",
             "witnessedBy": ["a:C-S3:W-CS3-N", "a:C-S3:W-CS3-D1"],
             "absence": "the third-rater-tie branch (-> human) has no witness in the source -- see diag:third-rater-tie-unwitnessed",
             "groundedBy": [g("R-S4")]},
            {"@id": "a:V-S2:invariant", "@type": "PrescribedInvariant", **N,
             "statement": "Every printed disposition and readiness line recomputes, by pure function, from the committed GradeRecords per method s6.2 -- anyone, later, reaches the same verdict from the same record.",
             "generator": "all reports across n >= 50 runs, plus seeded corrupted records", "pinnedBy": "a:C-S3:W-CS3-N",
             "sourceNote": "this, not bit-identical model output, is what 'a grade is reproducible' means; model-output stability is O-03's measurement (source's own words)",
             "groundedBy": [g("V-S2")]},
        ],
    },
    {
        "@id": "sr:L2:R-S5", "@type": "SpecificationRecord", "title": "R-S5 a verified attack overrides the number",
        "assertions": [
            {"@id": "a:R-S5:rule", "@type": "Requirement", **N, "target": target("rule", "R-S5", "a verified attack overrides the number"),
             "statement": "A replayed vacuous-pass report suspends the disposition of the affected rev regardless of vector, registered as a contested knockout on the clause's dimension.",
             "witnessedBy": ["a:C-S3:W-CS3-D2"],
             "groundedBy": [g("R-S5")]},
        ],
    },
    {
        "@id": "sr:L2:R-S6", "@type": "SpecificationRecord", "title": "R-S6 provisional is labelled",
        "assertions": [
            {"@id": "a:R-S6:rule", "@type": "Requirement", **N, "target": target("rule", "R-S6", "provisional is labelled"),
             "statement": "Every single-rater record carries provisional: true; every rendered report carries both lines (method s6.2.6).",
             "witnessedBy": ["a:C-S2:W-CS2-N"],
             "scopeNote": "the render side is witnessed at Part II W-JO1, outside the A9 region; only the single-rater limb is in scope here",
             "groundedBy": [g("R-S6")]},
        ],
    },
    # ---------------------------------------------------------------- records (SRS s4), shapes by literal example
    {
        "@id": "sr:L2:GradeRecord", "@type": "SpecificationRecord", "title": "GradeRecord record",
        "assertions": [
            {"@id": "a:GradeRecord:record", "@type": "Requirement", **N, "target": target("record", "GradeRecord"),
             "statement": "GradeRecord is an event record, per W-CS2-N.",
             "groundedBy": [g("S4.records")]},
            {"@id": "a:GradeRecord:fields", "@type": "InterfaceSpecification", **N, "target": target("record-shape", "GradeRecord"),
             "statement": "A GradeRecord carries rater, model, manifest_hash, vector (dimension -> score), evidence (dimension -> spec.md:<line>), disposition, readiness and provisional; the source states this shape only by literal example (W-CS2-N and the S-S2 crossing example), and model, disposition and readiness appear in W-CS2-N only.",
             "fields": [
                 {"name": "rater", "examples": ["A"], "groundedIn": ["C-S2.W-CS2-N", "S6.S-S2"]},
                 {"name": "model", "examples": ["<M>"], "groundedIn": ["C-S2.W-CS2-N"], "presence": "absent from the S-S2 crossing example"},
                 {"name": "manifest_hash", "examples": ["<H>", "9c41…"], "groundedIn": ["C-S2.W-CS2-N", "S6.S-S2"]},
                 {"name": "vector", "form": "dimension P1..P11 -> score in {0, 1, 2}", "groundedIn": ["C-S2.W-CS2-N", "S6.S-S2", "C-S2.determinism"]},
                 {"name": "evidence", "form": "dimension -> spec.md:<line>", "examples": ["spec.md:214"], "groundedIn": ["C-S2.W-CS2-N", "S6.S-S2"]},
                 {"name": "disposition", "examples": ["<D>"], "groundedIn": ["C-S2.W-CS2-N"], "presence": "absent from the S-S2 crossing example"},
                 {"name": "readiness", "examples": ["<R>"], "groundedIn": ["C-S2.W-CS2-N"], "presence": "absent from the S-S2 crossing example"},
                 {"name": "provisional", "examples": ["true"], "groundedIn": ["C-S2.W-CS2-N", "S6.S-S2", "R-S6"]},
             ],
             "shapeStatedBy": "example only",
             "diagnostic": "diag:GradeRecord-fields-by-example",
             "groundedBy": [g("C-S2.W-CS2-N"), g("S6.S-S2")]},
        ],
    },
    {
        "@id": "sr:L2:LedgerEntry", "@type": "SpecificationRecord", "title": "LedgerEntry record",
        "assertions": [
            {"@id": "a:LedgerEntry:record", "@type": "Requirement", **N, "target": target("record", "LedgerEntry"),
             "statement": "LedgerEntry is an event record and is hash-chained.",
             "groundedBy": [g("S4.records"), g("V-S1", "context", "append-only over ledger/** is the invariant the record's classification points at")]},
            {"@id": "a:LedgerEntry:fields", "@type": "InterfaceSpecification", **N, "target": target("record-shape", "LedgerEntry"),
             "statement": "A LedgerEntry carries seq, prev, kind, payload and hash; kind takes at least the values registration (W-CS7-N) and ratification (J-S4); the source states this shape only by literal example.",
             "fields": [
                 {"name": "seq", "examples": ["7"], "groundedIn": ["C-S7.W-CS7-N"]},
                 {"name": "prev", "examples": ["<H6>"], "groundedIn": ["C-S7.W-CS7-N"]},
                 {"name": "kind", "examples": ["registration", "ratification"], "groundedIn": ["C-S7.W-CS7-N", "J-S4.chain"], "presence": "the value set is not stated as closed"},
                 {"name": "payload", "form": "for a registration: {spec, rev, vector}", "groundedIn": ["C-S7.W-CS7-N", "J-S1.chain"]},
                 {"name": "hash", "form": "sha256(seq || prev || payload)", "groundedIn": ["C-S7.W-CS7-N"]},
             ],
             "shapeStatedBy": "example only",
             "groundedBy": [g("C-S7.W-CS7-N"), g("J-S4.chain", "context", "the second kind value, ratification")]},
        ],
    },
    # ---------------------------------------------------------------- components (SRS s5)
    {
        "@id": "sr:L2:grader-runner", "@type": "SpecificationRecord", "title": "Component grader-runner",
        "assertions": [
            {"@id": "a:grader-runner:component", "@type": "Requirement", **N, "target": target("component", "grader-runner"),
             "statement": "The decomposition includes a component grader-runner (headless invocation wrapper + manifest assembler + record verifier), whose repo home is tools/grader-runner/ and which serves C-S2.",
             "attributes": {"description": "headless invocation wrapper + manifest assembler + record verifier", "repoHome": "tools/grader-runner/", "serves": ["C-S2"]},
             "groundedBy": [g("S5.grader-runner"), g("S5.table-header", "definition", "names the columns: Component, Repo home, Serves")]},
        ],
    },
    {
        "@id": "sr:L2:adjudicator", "@type": "SpecificationRecord", "title": "Component adjudicator",
        "assertions": [
            {"@id": "a:adjudicator:component", "@type": "Requirement", **N, "target": target("component", "adjudicator"),
             "statement": "The decomposition includes a component adjudicator (pure routing fn + third-rater invocation), whose repo home is tools/adjudicator/ and which serves C-S3.",
             "attributes": {"description": "pure routing fn + third-rater invocation", "repoHome": "tools/adjudicator/", "serves": ["C-S3"]},
             "groundedBy": [g("S5.adjudicator"), g("S5.table-header", "definition", "names the columns: Component, Repo home, Serves")]},
        ],
    },
    {
        "@id": "sr:L2:ledger", "@type": "SpecificationRecord", "title": "Component ledger",
        "assertions": [
            {"@id": "a:ledger:component", "@type": "Requirement", **N, "target": target("component", "ledger"),
             "statement": "The decomposition includes a component ledger (append-only JSONL + chain verifier + hooks), whose repo homes are ledger/ and .githooks/ and which serves C-S7.",
             "attributes": {"description": "append-only JSONL + chain verifier + hooks", "repoHome": ["ledger/", ".githooks/"], "serves": ["C-S7"]},
             "groundedBy": [g("S5.ledger"), g("S5.table-header", "definition", "names the columns: Component, Repo home, Serves")]},
            {"@id": "a:decomposition:traceability", "@type": "PrescribedInvariant", **N,
             "statement": "Every component is traceable to the capabilities it serves; no component serves nothing.",
             "groundedBy": [g("S5.traceable")]},
        ],
    },
    # ---------------------------------------------------------------- seams (SRS s6)
    {
        "@id": "sr:L2:S-S2", "@type": "SpecificationRecord", "title": "Seam S-S2 — grader-runner → adjudicator",
        "assertions": [
            {"@id": "a:S-S2:seam", "@type": "InterfaceSpecification", **N, "target": target("seam", "S-S2"),
             "statement": "Seam S-S2 has producer grader-runner and consumer adjudicator; its contract is a verified GradeRecord; its crossing example is the literal {\"rater\": \"A\", \"vector\": {P1..P11}, \"evidence\": {\"P6\": \"spec.md:214\"}, \"manifest_hash\": \"9c41…\", \"provisional\": true}; status filled.",
             "attributes": {"producer": "grader-runner", "consumer": "adjudicator", "contract": "verified GradeRecord",
                            "crossingExample": {"rater": "A", "vector": {"P1": 2, "P2": 2, "P3": 2, "P4": 2, "P5": 2, "P6": 1, "P7": 2, "P8": 2, "P9": 2, "P10": 1, "P11": 2},
                                                "evidence": {"P6": "spec.md:214"}, "manifest_hash": "9c41…", "provisional": True},
                            "status": "filled"},
             "groundedBy": [g("S6.S-S2"), g("S6.table-header", "definition", "names the columns: Seam, Producer → Consumer, Contract, Crossing example, Status")]},
        ],
    },
    {
        "@id": "sr:L2:S-S3", "@type": "SpecificationRecord", "title": "Seam S-S3 — adjudicator → orchestrator",
        "assertions": [
            {"@id": "a:S-S3:seam", "@type": "InterfaceSpecification", **N, "target": target("seam", "S-S3"),
             "statement": "Seam S-S3 has producer adjudicator and consumer orchestrator; its contract is the adjudicated report; its crossing example is the literal {\"vector\": {…}, \"disposition\": \"D-3 Specification-complete\", \"readiness\": \"BLOCKED — O-04\", \"contested_knockouts\": [], \"provisional\": false}; status filled.",
             "attributes": {"producer": "adjudicator", "consumer": "orchestrator", "contract": "adjudicated report",
                            "crossingExample": {"vector": "{…}", "disposition": "D-3 Specification-complete", "readiness": "BLOCKED — O-04", "contested_knockouts": [], "provisional": False},
                            "status": "filled"},
             "absence": "the consumer, orchestrator, is outside the A9 region -- see diag:out-of-region-endpoints",
             "groundedBy": [g("S6.S-S3"), g("S6.table-header", "definition", "names the columns")]},
        ],
    },
    {
        "@id": "sr:L2:S-S6", "@type": "SpecificationRecord", "title": "Seam S-S6 — orchestrator → ledger",
        "assertions": [
            {"@id": "a:S-S6:seam", "@type": "InterfaceSpecification", **N, "target": target("seam", "S-S6"),
             "statement": "Seam S-S6 has producer orchestrator and consumer ledger; its contract is a LedgerEntry; its crossing example is the W-CS7-N line; status filled.",
             "attributes": {"producer": "orchestrator", "consumer": "ledger", "contract": "LedgerEntry", "crossingExample": "the W-CS7-N line", "status": "filled"},
             "absence": "the producer, orchestrator, is outside the A9 region -- see diag:out-of-region-endpoints",
             "groundedBy": [g("S6.S-S6"), g("C-S7.W-CS7-N", "definition", "the crossing example the seam row points to")]},
        ],
    },
]

DIAGNOSTICS = [
    {"@id": "diag:W-CS3-N-third-rater-is-agentic", "@type": "UnderdeterminationDiagnostic", "blocking": False,
     "cone": ["a live, deterministic oracle for W-CS3-N's second half"],
     "statement": "C-S3's routing limb is a pure function, but W-CS3-N's second half runs rater C -- the adjudicator component is 'pure routing fn + third-rater invocation'. A live acceptance test of the whole witness depends on an agentic invocation; a deterministic one needs a replayed rater-C record.",
     "evidence": ["C-S3.W-CS3-N", "S5.adjudicator"],
     "legalOutputs": "this diagnostic; a replay fixture recorded at freeze 2 (A9 act: 'a third-rater record')",
     "status": "open"},
    {"@id": "diag:W-CS3-D2-needs-a-C-S5-report", "@type": "UnderdeterminationDiagnostic", "blocking": False,
     "cone": ["W-CS3-Δ2's input"],
     "statement": "W-CS3-Δ2's input includes a replayed stub report from C-S5 (attack), which is outside the A9 region. The source does not state the report's shape in the region.",
     "evidence": ["C-S3.W-CS3-D2", "R-S5"],
     "legalOutputs": "this diagnostic; a replay fixture recorded at freeze 2 (A9 act: 'a C-S5 report')",
     "status": "open"},
    {"@id": "diag:hash-preimage-encoding-unstated", "@type": "MissingInformation", "blocking": False,
     "statement": "W-CS7-N defines hash = sha256(seq || prev || payload) but does not state how seq and payload are encoded before concatenation (serialization, separator, key order). Two conforming implementations can disagree on every hash.",
     "evidence": ["C-S7.W-CS7-N", "C-S7.determinism"],
     "legalOutputs": "this diagnostic; a labeled closure proposal at L3 for the architect to confer",
     "status": "open"},
    {"@id": "diag:third-rater-tie-unwitnessed", "@type": "MissingInformation", "blocking": False,
     "statement": "R-S4's branch 'a third-rater tie -> human' has no witness; neither W-CS3-N nor W-CS3-Δ1 exercises it, and the source does not define a tie among three raters.",
     "evidence": ["R-S4", "C-S3.W-CS3-N", "C-S3.W-CS3-D1"],
     "status": "open"},
    {"@id": "diag:GradeRecord-fields-by-example", "@type": "MissingInformation", "blocking": False,
     "statement": "GradeRecord's fields are stated only through two literal examples, which differ: model, disposition and readiness appear in W-CS2-N but not in the S-S2 crossing example. Whether they are optional, and whether the field set is closed, is not stated.",
     "evidence": ["S4.records", "C-S2.W-CS2-N", "S6.S-S2"],
     "status": "open"},
    {"@id": "diag:out-of-region-endpoints", "@type": "UnderdeterminationDiagnostic", "blocking": False,
     "cone": ["S-S3's consumer and S-S6's producer"],
     "statement": "The orchestrator (SRS s5, 'state machine over J-S1-J-S4') is the consumer of S-S3 and the producer of S-S6 but is not in the A9 region. The region's seams therefore have one in-region endpoint each; FX-SEAM-B over them is partial by construction unless a harness stands in for the orchestrator.",
     "evidence": ["S6.S-S3", "S6.S-S6", "S5.traceable"],
     "status": "open"},
    {"@id": "diag:external-method-artifacts", "@type": "MissingInformation", "blocking": False,
     "statement": "W-CS2-N's manifest, R-S1 and the C-S2 determinism note cite method/v0.4.md, skills/fspec-method and method s6.2 / s6.3, none of which is in the registered source. What 'recompute per method s6.2' computes is therefore not stated in the region.",
     "evidence": ["C-S2.W-CS2-N", "C-S2.determinism", "R-S1", "C-S3.W-CS3-D1"],
     "status": "open"},
    {"@id": "diag:ledger-hooks-repo-home", "@type": "ConflictingStatement", "spansLayers": True, "blocking": False,
     "cone": ["projection of the ledger component's files"],
     "statement": "SRS s5 homes the ledger at ledger/ and .githooks/; the hook half (W-CS7-Δ1: 'hook exit 1') is a git hook, not a module a TypeScript build emits. Like the slice's author-agent, the source is univocal and the conflict is with the factory's realization; it is recorded, not resolved, here.",
     "evidence": ["S5.ledger", "C-S7.W-CS7-D1"],
     "status": "open"},
    {"@id": "diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash", "@type": "ConflictingStatement",
     "cone": ["c:ledger:hash-encoding (rq-034) and any C-S7 bar or oracle"],
     "statement": "W-CS7-N puts kind outside the hash preimage (sha256(seq || prev || payload)); W-CS7-Δ1 says chain verification fails loudly on ANY rewrite of an existing line. A kind-only rewrite keeps every hash, so the two cannot both hold. Source-internal.",
     "evidence": ["C-S7.W-CS7-N", "C-S7.W-CS7-D1"],
     "blocks": ["a:C-S7:W-CS7-N", "a:C-S7:W-CS7-D1"],
     "raisedByAct": "rq-034",
     "legalOutputs": "adj:ledger-hash-kind (A: amend the source; B: design closure against the literal; C: narrow reading of Δ1)",
     "status": None},   # status and blocking DERIVED from the act row at build (raised_by_act)
    {"@id": "diag:C-S7-determinism-beyond-the-acted-region", "@type": "UnderdeterminationDiagnostic", "blocking": False,
     "cone": ["a:C-S7:determinism, and any ratified bar or oracle for C-S7 that would rest on it"],
     "statement": "a:C-S7:determinism is grounded on line 76 (C-S7's determinism note), one line beyond the A9 act's '73–75'. C-S2's and C-S3's determinism notes lie inside the region, so the bound may be a transcription boundary rather than a decision to exclude -- but that is the architect's to say. Either the act's region is amended to 73–76, or the clause leaves the record.",
     "evidence": ["C-S7.determinism", "C-S7.header"],
     "legalOutputs": "an architect act amending A9's region (the clause stays), or a decision at rq-017 to drop the clause (it moves to coverage.notYetCovered); no C-S7 bar or oracle rests on it until then (Ops finding 2026-10-01, bullet 7)",
     "status": "closed",
     "closedBy": "docs/decisions/2026-10-01-a9-region-amendment.md -- the architect: 'amend A9's region to 73–76'"},
]

WS3 = {
    "target": {"act": "docs/decisions/2026-10-01-a9-ws3-target-naming-act.md", "title": "SRS adjudication and registration core",
               "capabilities": ["C-S2", "C-S3", "C-S7"]},   # regionLines and beyondRegion are READ from the act at build
    "demonstrationControlCandidate": {
        "capability": "C-S2", "proposedBy": "aro-dev-agent",
        "why": "C-S2 is agentic (one isolated rater invocation) and its vector is masked; holding its bar provisional is natural, not staged",
        "status": "proposed -- designated at freeze 2, before results (Plan v1.1 s5); lifecycle: ratified or the capability retired by act within the phase",
    },
    "replayFixturesForFreeze2": ["a C-S5 stub report (W-CS3-Δ2)", "a rater-C GradeRecord (W-CS3-N)"],
}

COVERAGE = {
    "axis": "covered · not yet covered — separate from the semantic states prohibited · non-goal · unspecified (ARO 6)",
    "covered": {
        "SRS §2": "J-S1 (24), J-S4 (30) and the coverage map (32), as context only",
        "SRS §3": None,   # derived at build from the capability records' primary spans, inside the acted region
        "SRS §4": "the Records line (85); R-S1, R-S4, R-S5, R-S6 (87, 90–92)",
        "SRS §5": "table header; grader-runner, adjudicator and ledger rows; the traceability sentence",
        "SRS §6": "table header; S-S2, S-S3, S-S6",
        "SRS §7": "V-S1 (context), V-S2, V-S3",
    },
    "notYetCovered": "everything else in Part I and all of Part II, including R-S2, R-S3, the conflict record (94) and V-S4 -- silence outside the covered spans is unprocessed source, not specification silence",
    "detectedClauseCoverage": "not computed: hand-authored, not a transformation (ARO 8.2)",
}


ACT = HERE.parents[2] / "docs" / "decisions" / "2026-10-01-a9-ws3-target-naming-act.md"
QUEUE = HERE.parents[1] / "measurements" / "ratification-queue.jsonl"


def raised_by_act(diag, queue):
    """A diagnostic the ARCHITECT opened through the act tool is derived from that act row, never retyped (IA Ops
    finding 2026-10-01): open while the row stands as `diagnostic-opened`, closed once a later row supersedes it
    and that row is acted; blocking iff the note says BLOCKING. The note is carried verbatim."""
    row = queue[diag["raisedByAct"]]
    if row.get("act") != "diagnostic-opened":
        raise SystemExit("%s names %s, which is not a diagnostic-opened act" % (diag["@id"], row["id"]))
    rec = {"item": row["id"], "actor": row["actor"], "actedAt": row["actedAt"], "note": row["actNote"]}
    conferred = [r for r in queue.values() if r.get("supersedes") == row["id"] and r.get("act") in ("accepted", "ratified", "decided")]
    if conferred:
        return dict(diag, status="closed", blocking=False, actRecord=rec,
                    closedBy="%s %s by %s" % (conferred[0]["id"], conferred[0]["act"], conferred[0]["actor"]))
    return dict(diag, status="open", blocking="BLOCKING" in row["actNote"], actRecord=rec)

CAPABILITY_RECORDS = ("sr:L2:C-S2", "sr:L2:C-S3", "sr:L2:C-S7")


def acted_region(act_path=ACT):
    """The region AS THE ARCHITECT STATED IT, read from the verbatim act record -- never retyped (Ops finding
    2026-10-01: a test constant widened 73-75 to 73-76 by itself). -> [[first, last], ...] inclusive."""
    import re
    quoted = "\n".join(l[1:].strip() for l in act_path.read_text(encoding="utf-8").splitlines() if l.startswith(">"))
    m = re.search(r"Region: lines ([0-9]+)[–-]([0-9]+) and ([0-9]+)[–-]([0-9]+)", quoted)
    if not m:
        raise SystemExit("the A9 act record states no 'Region: lines a–b and c–d' -- refusing to guess a region")
    a, b, c, d = map(int, m.groups())
    region = [[a, b], [c, d]]
    # Amendments, in date order: "amend A9's region to x–y" replaces the range that BEGINS at x (2026-10-01:
    # "amend A9's region to 73–76"). An amendment that matches no range's start is refused, never guessed.
    for amendment in sorted(act_path.parent.glob("*-a9-region-amendment*.md")):
        said = "\n".join(l[1:].strip() for l in amendment.read_text(encoding="utf-8").splitlines() if l.startswith(">"))
        for lo, hi in re.findall(r"region to ([0-9]+)[–-]([0-9]+)", said):
            hits = [rng for rng in region if rng[0] == int(lo)]
            if len(hits) != 1:
                raise SystemExit("%s amends a range starting at %s, which A9 does not have" % (amendment.name, lo))
            hits[0][1] = int(hi)
    return region


AMENDMENTS = sorted((HERE.parents[2] / "docs" / "decisions").glob("*-a9-region-amendment*.md"))


def in_region(line, region):
    return any(lo <= line <= hi for lo, hi in region)


def build():
    frags = json.loads(FRAGMENTS.read_text(encoding="utf-8"))
    by_label = {f["label"]: f for f in frags["fragments"]}
    def fid(label):
        return by_label[label]["fragmentId"]

    region = acted_region()
    queue = {json.loads(l)["id"]: json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()}

    beyond = [{"assertion": a["@id"], "label": c["label"], "line": int(by_label[c["label"]]["display"]["lines"]),
               "diagnostic": a.get("diagnostic")}
              for rec in RECORDS if rec["@id"] in CAPABILITY_RECORDS for a in rec["assertions"]
              for c in a["groundedBy"] if c["role"] == "primary"
              and not in_region(int(by_label[c["label"]]["display"]["lines"]), region)]
    undisclosed = [b["assertion"] for b in beyond if not b["diagnostic"]]
    if undisclosed:
        raise SystemExit("primary span(s) beyond the acted region with no diagnostic: %s" % undisclosed)
    # SRS s3 coverage is DERIVED, never retyped (Ops finding 2026-10-01, bullet 4): each capability's covered lines
    # are the min..max of its primary spans, and each range must lie inside the acted region.
    spans = {}
    for rec in RECORDS:
        if rec["@id"] in CAPABILITY_RECORDS:
            spans[rec["@id"].split(":")[-1]] = [int(by_label[c["label"]]["display"]["lines"])
                                                for a in rec["assertions"] for c in a["groundedBy"] if c["role"] == "primary"]
    # (no range guard here: every out-of-region primary span is already refused above unless disclosed, and the
    #  derived range is pinned by test_section_3_coverage_is_derived_... -- Ops showed a guard here was dead code)
    section3 = ", ".join("%s (%d–%d)" % (cap, min(v), max(v)) for cap, v in spans.items())
    ws3 = dict(WS3, target=dict(WS3["target"], regionLines=region, regionSource="the verbatim act record, parsed at build",
               amendments=[str(a.relative_to(HERE.parents[2])).replace("\\", "/") for a in AMENDMENTS]),
               beyondRegion=beyond)

    def resolve(obj):
        if isinstance(obj, dict):
            if set(obj) >= {"label", "role"} and obj.get("label") in by_label and "fragment" not in obj:
                return {"fragment": fid(obj["label"]), **{k: resolve(v) for k, v in obj.items()}}
            return {k: resolve(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [resolve(v) for v in obj]
        return obj

    def resolve_evidence(d):
        d = dict(d)
        d["evidence"] = [fid(e) for e in d["evidence"]]
        return d

    missing = sorted({c["label"] for r in RECORDS for a in r["assertions"] for c in a["groundedBy"]} - set(by_label))
    if missing:
        raise SystemExit("unminted span label(s): %s" % missing)
    return {
        "@context": {
            "@vocab": "https://fandaws.com/ontology/aro/spike-1.5/vocab#",
            "sf": "https://fandaws.com/ontology/aro/spike-1.5/fragment/",
            "_note": "The same flat spike vocabulary as spike:l2:srs-slice. No class or property is defined behind these terms; nothing here becomes the ARO TBox or the Phase-4 reference graph.",
        },
        "@id": "spike:l2:srs-ws3",
        "@type": "SpecificationGraph",
        "layer": "L2",
        "status": "candidate",
        "title": "SRS adjudication and registration core (WS-3) — what the source says (L2), at capability grain",
        "authoredUnder": "docs/decisions/2026-09-10-phase-1.5-amendments.md — Amendment 2 (the dev agent authors; the architect performs 100% span review; non-graduating); target named by docs/decisions/2026-10-01-a9-ws3-target-naming-act.md",
        "source": {"registeredAs": "src:srs-spec", "doc": "SPEC.md", "digest": DIGEST, "fragments": "spike/graph/ws3/fragments.json"},
        "semanticDependencyManifest": {
            "registeredSourceDigests": [DIGEST], "profileVersion": "none — spike, minimum viable fidelity",
            "ontologyModuleVersions": [], "shaclShapeVersions": [], "derivationRuleVersions": [],
            "canonicalizationVersion": "spike-canonical-json-1 (sorted keys, compact separators, UTF-8, trailing newline)",
            "normalizationVersion": "norm-spike-1",
        },
        "facetsDefault": {
            "origin": {"kind": "transformer", "actRef": "act:aro-dev-agent:2026-10-01:hand-authoring", "note": "hand-authored by a model-driven agent, therefore transformer-origin; ratification never changes this"},
            "ratification": "unratified",
            "_authority": "computed, never stored (ARO 3.1): with these facets, not AUTHORITATIVE",
        },
        "d21": "Every target below is a specification-target description (a kind reference), never an instance; no assertion entails that the described thing exists.",
        "ws3": ws3,
        "records": resolve(RECORDS),
        "diagnostics": [resolve_evidence(raised_by_act(d, queue) if d.get("raisedByAct") else d) for d in DIAGNOSTICS],
        "coverage": dict(COVERAGE, covered=dict(COVERAGE["covered"], **{"SRS §3": section3})),
    }


def render(graph):
    return json.dumps(graph, ensure_ascii=False, indent=2) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    text = render(build())
    if args.check:
        on_disk = OUT.read_text(encoding="utf-8") if OUT.exists() else None
        if on_disk != text:
            print("srs-ws3.graph.jsonld differs from a rebuild", file=sys.stderr)
            return 1
        print("srs-ws3.graph.jsonld matches a rebuild")
        return 0
    OUT.write_bytes(text.encode("utf-8"))
    print("%d record(s), %d assertion(s), %d diagnostic(s) -> %s" % (
        len(RECORDS), sum(len(r["assertions"]) for r in RECORDS), len(DIAGNOSTICS), OUT.relative_to(HERE.parents[2])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
