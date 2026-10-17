"""WS-3 L3 -- closure CANDIDATES for the A9 target, bundled into Specification Records for ratification.

Amendment 2 (ii): every value below is conferred by the architect from these labeled candidates; nothing here is
inferred into the source. L3 forbids groundedBy (ARO D17): source passages appear only as rationaleSource, cited by
span label and resolved to the fragment id minted in spike/graph/ws3/fragments.json.

    python spike/graph/ws3/build_l3.py            # writes spike/graph/l3/srs-ws3.design.candidates.jsonld
    python spike/graph/ws3/build_l3.py --check    # exit 1 if the file on disk differs from a rebuild

Design, in one line per record (IA experiments/comms/DEV-2026-10-01-d8-part2-design.md):
  - four modules -- grading-types (types only), grader-runner, adjudicator, ledger -- realizing C-S2, C-S3, C-S7;
  - every agentic or out-of-region input is a PARAMETER (the rater, the evidence resolver, the C-S5 report), so each
    limb is testable without a model and the replay fixtures A9 names plug in directly;
  - the hook's logic is a ledger function; only the .githooks/ wrapper is outside the build (adjudicated).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FRAGMENTS = HERE / "fragments.json"
FRAGMENTS_2428 = HERE / "fragments-2428b115.json"   # the pre-amendment fragments (src:srs-spec, 2428b115)
OUT = HERE.parent / "l3" / "srs-ws3.design.candidates.jsonld"


def r(label, why):
    return {"cite": label, "why": why}


TOOLCHAIN = {"cite": "loopToolchain", "why": "the factory builds TypeScript modules imported as ./name.ts and tests with node:test -- a toolchain fact, not a statement in the SRS"}

RECORDS = [
    {
        "@id": "sr:L3:ws3-module-boundaries", "@type": "SpecificationRecord",
        "title": "WS-3 module boundaries — a types-only module, three capability modules, their edges",
        "kind": "closure-bundle",
        "closes": [],
        "addresses": ["sr:L2:grader-runner", "sr:L2:adjudicator", "sr:L2:ledger", "sr:L2:GradeRecord", "sr:L2:LedgerEntry"],
        "dependsOn": ["a:grader-runner:component", "a:adjudicator:component", "a:ledger:component",
                      "a:GradeRecord:fields", "a:LedgerEntry:fields", "a:S-S2:seam", "a:S-S3:seam", "a:S-S6:seam"],
        "standalone": False,
        "assertions": [
            {"@id": "c:ws3:grading-types", "@type": "Closure",
             "proposed": {"component": "grading-types",
                          "responsibility": "types-only module; zero runtime logic; owns GradeRecord, Score, Vector, RouteResult, AdjudicatedReport, VacuousPassReport, LedgerEntry and the rejection codes, so the three seams share one declaration of each record"},
             "rationaleSource": [r("S5.table-header", "s5 lists no shared-types component; three seams (S-S2, S-S3, S-S6) carry records between different components, so a single owner prevents divergent copies"),
                                 r("S4.records", "GradeRecord and LedgerEntry are named s4 records")]},
            {"@id": "c:ws3:deps:edges", "@type": "Closure",
             "proposed": {"depends_on": {"grading-types": [], "grader-runner": ["grading-types"],
                                         "adjudicator": ["grading-types"], "ledger": ["grading-types"]}},
             "rationaleSource": [r("S6.S-S2", "grader-runner -> adjudicator crosses as a GradeRecord VALUE; neither imports the other"),
                                 r("S6.S-S6", "the ledger's producer is the orchestrator, outside the region; the ledger imports no capability module")]},
            {"@id": "c:ws3:realizes", "@type": "Closure",
             "proposed": {"realizes": {"C-S2": ["grader-runner"], "C-S3": ["adjudicator"], "C-S7": ["ledger"]},
                          "capabilityPaths": {"C-S2": "grade", "C-S3": "adjudicate", "C-S7": "register"}},
             "rationaleSource": [r("S5.grader-runner", "serves C-S2"), r("S5.adjudicator", "serves C-S3"), r("S5.ledger", "serves C-S7")]},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes the four module units the WS-3 projection emits, their depends_on, and the capability -> modules map the factory reads as `capabilities`"},
    },
    {
        "@id": "sr:L3:ws3-field-types", "@type": "SpecificationRecord",
        "title": "WS-3 record types — as amended by the architect at rq-031 (and rq-033 item 4)",
        "kind": "closure-bundle",
        "closes": ["diag:GradeRecord-fields-by-example"],
        "addresses": ["sr:L2:GradeRecord", "sr:L2:LedgerEntry", "sr:L2:S-S3", "sr:L2:C-S3"],
        "dependsOn": ["a:GradeRecord:fields", "a:LedgerEntry:fields", "a:S-S3:seam", "a:C-S3:W-CS3-D1", "a:C-S3:W-CS3-D2"],
        "standalone": False,
        "amendmentOf": ["rq-031", "rq-033"],
        "assertions": [
            {"@id": "c:ws3:Score-Vector", "@type": "Closure",
             "proposed": {"declarations": ["export type Score = 0 | 1 | 2;", "export type Vector = Record<string, Score>;"],
                          "note": "dimension keys are strings (P1..P11 in the examples); the source does not close the key set, so none is proposed"},
             "rationaleSource": [r("C-S2.determinism", "every score in {0, 1, 2}"), r("S6.S-S2", "the crossing example's vector carries P1..P11")],
             "conferred": "as proposed (rq-031: 'Items 1, 3, 5, 6 as proposed')"},
            {"@id": "c:ws3:GradeRecord", "@type": "Closure",
             "proposed": {"fields": [
                 {"name": "rater", "type": "string"},
                 {"name": "model", "type": "string", "note": "REQUIRED (rq-031 (2)): model identity is provenance; the S-S2 crossing example is an abbreviation and is not a valid GradeRecord as written"},
                 {"name": "manifest_hash", "type": "string", "note": "sha256 hex of the manifest"},
                 {"name": "vector", "type": "Vector"},
                 {"name": "evidence", "type": "Record<string, string>", "note": "dimension -> spec.md:<line>"},
                 {"name": "disposition", "type": "string", "optional": True, "note": "derived value, never trusted from a single rater (rq-031 (2))"},
                 {"name": "readiness", "type": "string", "optional": True, "note": "as disposition"},
                 {"name": "provisional", "type": "boolean"}]},
             "rationaleSource": [r("C-S2.W-CS2-N", "eight fields"), r("S6.S-S2", "five of them; model, disposition, readiness absent")],
             "conferred": "amended at rq-031 (2)"},
            {"@id": "c:ws3:RouteResult", "@type": "Closure",
             "proposed": {"fields": [{"name": "route", "type": "Record<string, \"third-rater\">"},
                                     {"name": "contested_knockouts", "type": "string[]"}]},
             "rationaleSource": [r("C-S3.W-CS3-N", "the literal {\"route\": {\"P6\": \"third-rater\"}, \"contested_knockouts\": []}")],
             "conferred": "as proposed (rq-031)"},
            {"@id": "c:ws3:AdjudicatedReport", "@type": "Closure",
             "proposed": {"union": "AdjudicatedReport = Printed | Pending | Withheld | Suspended",
                          "variants": {
                              "Printed": {"vector": "Vector", "disposition?": "string", "readiness?": "string",
                                          "contested_knockouts": "[]", "provisional": "false",
                                          "note": "disposition and readiness are ABSENT until method s6.2 is registered as a source (rq-033 (4)); the S-S3 crossing example therefore abbreviates"},
                              "Pending": {"route": "Record<string, \"third-rater\">", "contested_knockouts": "[]", "provisional": "true",
                                          "note": "a routed dimension awaits rater C; no disposition (rq-031 (4), rq-033 (2b))"},
                              "Withheld": {"disposition_line": "\"WITHHELD\"", "contested_knockouts": "[string, ...string[]] -- at least one: an either-rater zero or a third-rater tie",
                                           "queue": "\"human\"", "note": "no disposition field (rq-031 (4)); a tie produces this variant (rq-033 (3))"},
                              "Suspended": {"disposition_line": "\"SUSPENDED\"", "cause": "`vacuous-pass:${string}`",
                                            "contested_knockouts": "string[] -- includes the attacked clause's dimension (R-S5), alongside any zero-knockouts",
                                            "queue": "\"human\""}},
                          "discriminant": "disposition_line on Withheld and Suspended; Pending is the variant with route and provisional: true; Printed has neither",
                          "precedence": "SUSPENDED > WITHHELD > PENDING > PRINTED (rq-033 (2a)): exactly one variant for every input"},
             "rationaleSource": [r("S6.S-S3", "the adjudicated report (Printed)"), r("C-S3.W-CS3-N", "routing, then provisional: false"), r("C-S3.W-CS3-D1", "WITHHELD"), r("C-S3.W-CS3-D2", "SUSPENDED"), r("R-S5", "regardless of vector")],
             "conferred": "amended at rq-031 (4); Printed's disposition/readiness made optional by rq-033 (4)"},
            {"@id": "c:ws3:VacuousPassReport", "@type": "Closure",
             "proposed": {"fields": [{"name": "clause", "type": "string"}, {"name": "dimension", "type": "string"},
                                     {"name": "replayed", "type": "true"}],
                          "note": "the C-S5 report's shape is not stated in the region (diag:W-CS3-D2-needs-a-C-S5-report); this is the minimal shape C-S3 reads -- which clause, which dimension it knocks out (R-S5), and that it replayed. The freeze-2 replay fixture must conform to it."},
             "rationaleSource": [r("C-S3.W-CS3-D2", "a replayed stub report on clause <CL>"), r("R-S5", "registered as a contested knockout on the clause's dimension")],
             "conferred": "as proposed (rq-031)"},
            {"@id": "c:ws3:LedgerEntry", "@type": "Closure",
             "proposed": {"fields": [{"name": "seq", "type": "number"}, {"name": "prev", "type": "string"},
                                     {"name": "kind", "type": "string", "note": "registration and ratification appear; the set is not closed, so string"},
                                     {"name": "payload", "type": "unknown"}, {"name": "hash", "type": "string"}]},
             "rationaleSource": [r("C-S7.W-CS7-N", "the literal entry"), r("J-S4.chain", "kind ratification")],
             "conferred": "as proposed (rq-031); what the hash covers is adj:ledger-hash-kind's, not this record's"},
        ],
        "displayDuties": {"whatRatifyingDoes": "these become grading-types' declarations; the union makes illegal report states unrepresentable, and typed fields are ENFORCEABLE in the factory (F6 rule)"},
    },
    {
        "@id": "sr:L3:grader-runner-interface", "@type": "SpecificationRecord",
        "title": "grader-runner's interface — as amended by the architect at rq-032",
        "kind": "closure-bundle",
        "closes": [],
        "addresses": ["sr:L2:C-S2", "sr:L2:R-S1", "sr:L2:R-S6", "sr:L2:grader-runner"],
        "dependsOn": ["a:C-S2:W-CS2-N", "a:C-S2:W-CS2-D1", "a:C-S2:W-CS2-D2", "a:C-S2:determinism", "a:R-S1:rule", "a:R-S6:rule"],
        "standalone": False,
        "amendmentOf": ["rq-032", "rq-040"],
        "assertions": [
            {"@id": "c:grader-runner:assembleManifest", "@type": "Closure",
             "proposed": {"signature": "assembleManifest(specPath: string, rev: string): string[]",
                          "returns": "[`${specPath}@${rev}`, \"method/v0.4.md\", \"skills/fspec-method\"] -- exactly the R-S1 triple"},
             "rationaleSource": [r("R-S1", "context MUST contain exactly {spec@rev, method/v0.4.md, skills/fspec-method}")],
             "conferred": "as proposed (rq-032: 'Items 1 and 3 as proposed')"},
            {"@id": "c:grader-runner:checkIsolation", "@type": "Closure",
             "proposed": {"signature": "checkIsolation(manifest: string[], specPath: string, rev: string): { ok: true } | { ok: false; code: \"G-ISO-01\" }",
                          "rule": "ok iff the manifest is exactly the R-S1 triple for THAT spec@rev (order-insensitive, no extra entries); a manifest pinned to any other rev is G-ISO-01"},
             "rationaleSource": [r("C-S2.W-CS2-D2", "manifest containing findings/cycle-3/ -> rejected, G-ISO-01"), r("V-S3", "manifest a subset of the R-S1 triple; violations rejected before adjudication"), r("J-S1.chain", "each context-manifest pinned to the rev graded")],
             "conferred": "amended at rq-032 (2)"},
            {"@id": "c:grader-runner:manifestHash", "@type": "Closure",
             "proposed": {"signature": "manifestHash(manifest: string[]): string",
                          "rule": ["canonicalManifest = [...manifest].sort() -- ECMAScript's default lexicographic UTF-16 code-unit ordering, without mutating the caller's array",
                                   "returns the lowercase SHA-256 hexadecimal digest of the UTF-8 bytes of JSON.stringify(canonicalManifest), with no added whitespace"]},
             "rationaleSource": [r("C-S2.determinism", "<H> = sha256 of the manifest -- the serialization is not stated, so one is conferred")],
             "conferred": "amended at rq-040 (3)"},
            {"@id": "c:grader-runner:verifyGradeRecord", "@type": "Closure",
             "proposed": {"signature": "verifyGradeRecord(record: GradeRecord, resolves: (pointer: string) => boolean): { ok: true } | { ok: false; code: \"G-EVID-01\" | \"G-SCORE-01\" | \"G-PROV-01\" }",
                          "rule": ["G-EVID-01 when any evidence pointer does not resolve (resolves is injected)",
                                   "G-SCORE-01 when any score is outside {0, 1, 2}",
                                   "G-PROV-01 when provisional is not true (R-S6)",
                                   "when several apply, the first of G-EVID-01, G-SCORE-01, G-PROV-01 is returned"],
                          "note": "G-SCORE-01 and G-PROV-01 are proposed codes: the source states the properties but names no code for their violation"},
             "rationaleSource": [r("C-S2.W-CS2-D1", "spec.md:9999 -> verifier rejects, G-EVID-01"), r("C-S2.determinism", "every score in {0, 1, 2}; every evidence pointer resolves"), r("R-S6", "every single-rater record carries provisional: true")],
             "conferred": "amended at rq-032 (4)"},
            {"@id": "c:grader-runner:runGrader", "@type": "Closure",
             "proposed": {"signature": "runGrader(invoke: RaterInvoker, rater: string, manifest: string[], specPath: string, rev: string): Promise<GradeRecord>",
                          "alsoExports": ["export type RaterInvoker = (manifest: string[]) => Promise<{ model: string; vector: Vector; evidence: Record<string, string>; disposition?: string; readiness?: string }>",
                                          "export class GradeRejectedError extends Error { code: \"G-ISO-01\" }"],
                          "rule": ["checkIsolation(manifest, specPath, rev) first -- a contaminated or mis-pinned manifest throws GradeRejectedError(G-ISO-01) and the invoker is NEVER called",
                                   "after isolation succeeds, runGrader computes canonicalManifest (as manifestHash defines it) ONCE, passes that exact canonical array to invoke, and computes manifest_hash from that same array; the caller-supplied ordering is never passed to the rater",
                                   "the record is the invoker's output plus rater, manifest_hash, provisional: true"]},
             "rationaleSource": [r("C-S2.W-CS2-N", "headless invocation -> grade record with provisional: true"), r("R-S6", "every single-rater record carries provisional: true"), r("C-S2.W-CS2-D2", "the grade never enters adjudication")],
             "conferred": "amended at rq-032 (5) and rq-040 (5)"},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes grader-runner's signatures. It does NOT designate the demonstration control: that remains the freeze-2 act (rq-032)."},
    },
    {
        "@id": "sr:L3:adjudicator-interface", "@type": "SpecificationRecord",
        "title": "adjudicator's interface — as amended by the architect at rq-033",
        "kind": "closure-bundle",
        "closes": ["diag:third-rater-tie-unwitnessed", "diag:adjudicator-not-total-over-declared-inputs"],
        "addresses": ["sr:L2:C-S3", "sr:L2:R-S4", "sr:L2:R-S5", "sr:L2:adjudicator"],
        "dependsOn": ["a:C-S3:W-CS3-N", "a:C-S3:W-CS3-D1", "a:C-S3:W-CS3-D2", "a:C-S3:determinism", "a:R-S4:rule", "a:R-S5:rule", "a:V-S2:invariant"],
        "standalone": False,
        "amendmentOf": ["rq-033", "rq-044", "rq-063"],
        "assertions": [
            {"@id": "c:adjudicator:route", "@type": "Closure",
             "proposed": {"signature": "route(a: GradeRecord, b: GradeRecord): RouteResult",
                          "rule": ["FIRST: a and b must carry identical vector key sets, else throw AdjudicationInputError { code: \"A-DIM-01\" } and produce no RouteResult (rq-063 item 5)",
                                   "contested_knockouts = every dimension where either rater scored 0; route[d] = \"third-rater\" for every other dimension where a and b differ. Pure; same inputs, same output."]},
             "rationaleSource": [r("R-S4", "either-rater zero -> contested knockout; nonzero disagreement -> third rater"), r("C-S3.W-CS3-N", "P6 2 vs 1 -> third-rater"), r("C-S3.determinism", "a pure function of the two committed vectors")],
             "conferred": "amended at rq-063 item 5 (route validates its inputs); the routing rule itself as proposed at rq-033 item 1"},
            {"@id": "c:adjudicator:adjudicate", "@type": "Closure",
             "proposed": {"signature": "adjudicate(a: GradeRecord, b: GradeRecord, opts?: { c?: GradeRecord; attacks?: VacuousPassReport[] }): AdjudicatedReport",
                          "rule": ["FIRST: validation per c:adjudicator:input-domain -- before any routing or report construction",
                                   "K = the deduplicated union of (i) every dimension where a or b scores 0, (ii) every routed dimension on which a, b and a supplied c are pairwise different (a third-rater tie), and (iii) every dimension named by a replayed attack; K is emitted in canonical order (c:adjudicator:canonical-order)",
                                   "precedence SUSPENDED > WITHHELD > PENDING > PRINTED; no early exit masks a higher variant",
                                   "SUSPENDED: any replayed attack -> { disposition_line: \"SUSPENDED\", cause: \"vacuous-pass:<clause>\", contested_knockouts: K, queue: \"human\" } -- the complete K, including coexisting zero and tie dimensions",
                                   "WITHHELD: else K non-empty (a zero-knockout or a third-rater tie) -> { disposition_line: \"WITHHELD\", contested_knockouts: K, queue: \"human\" }",
                                   "PENDING: else a routed dimension with no c -> { route, contested_knockouts: [], provisional: true }",
                                   "PRINTED: else every routed dimension takes the value at least two of a, b, c share -> { vector, contested_knockouts: [], provisional: false }"],
                          "note": "rater C's invocation is not in this module: c is a parameter, so the deterministic limb runs on a replayed rater-C record (A9's fixture)"},
             "rationaleSource": [r("C-S3.W-CS3-N", "after rater C: P6 = C's consensus value, provisional: false"), r("C-S3.W-CS3-D1", "WITHHELD, queue human"), r("C-S3.W-CS3-D2", "SUSPENDED, cause vacuous-pass:<CL>"), r("R-S5", "a verified attack overrides the number, regardless of vector"), r("S5.adjudicator", "pure routing fn + third-rater invocation")],
             "conferred": "amended at rq-033 (2a), (2b) and rq-063 item 2 (the complete contested-knockout set K)"},
            {"@id": "c:adjudicator:tie", "@type": "Closure",
             "proposed": {"definition": "a third-rater tie is a routed dimension on which a, b and c are pairwise different",
                          "consequence": "the WITHHELD variant: the dimension in contested_knockouts, queue: \"human\", no disposition"},
             "rationaleSource": [r("R-S4", "a third-rater tie -> human -- 'tie' is not defined in the source")],
             "conferred": "amended at rq-033 (3): the definition as proposed; the consequence is the WITHHELD variant; item 3 accepted as presented at rq-063"},
            {"@id": "c:adjudicator:disposition-text", "@type": "Closure",
             "proposed": {"rule": "adjudicate neither computes nor carries disposition or readiness: they are ABSENT from every report until method s6.2 is registered as a source",
                          "why": "they recompute 'per method s6.2', which is outside the registered source; diag:external-method-artifacts stays open"},
             "rationaleSource": [r("V-S2", "the printed lines recompute from the committed GradeRecords per method s6.2")],
             "conferred": "amended at rq-033 (4); item 4 accepted as presented at rq-063"},
            {"@id": "c:adjudicator:input-domain", "@type": "Closure",
             "proposed": {"rule": ["route(a, b): a and b must carry identical vector key sets",
                                   "adjudicate(a, b, opts): a, b and a supplied c must carry identical vector key sets, and every supplied attack's dimension must be one of those keys",
                                   "otherwise adjudicate throws AdjudicationInputError { code: \"A-DIM-01\" } and produces NO report -- a missing dimension is never guessed or skipped"],
                          "note": "the narrowing route your rq-044 note offered ('narrowing the accepted input types with explicit validation and failure behavior'); A-DIM-01 is a proposed code, as G-SCORE-01 and G-PROV-01 were"},
             "rationaleSource": [r("C-S3.determinism", "a pure function of the two committed vectors -- defined only if the vectors share their dimensions")],
             "conferred": "amended at rq-063 item 5 (validation applies to both public functions, before routing or report construction)"},
            {"@id": "c:adjudicator:agreed-dimensions", "@type": "Closure",
             "proposed": {"rule": "a dimension on which a and b agree (and neither is 0) takes that value unchanged in the PRINTED vector; c's score on it is ignored. c decides only the routed dimensions"},
             "rationaleSource": [r("R-S4", "only nonzero disagreement goes to the third rater")],
             "conferred": "as proposed (rq-063: item 6 accepted as presented; resolves rq-044 point 2)"},
            {"@id": "c:adjudicator:canonical-order", "@type": "Closure",
             "proposed": {"rule": "route keys, contested_knockouts and PRINTED vector keys are emitted in ascending ECMAScript default sort order (UTF-16 code units) -- the same rule rq-040 conferred for the canonical manifest; contested_knockouts carries no duplicates",
                          "note": "under this rule P10 sorts before P2; a numeric-aware order would be a different value to confer"},
             "rationaleSource": [r("C-S3.determinism", "bit-stable, recomputable by anyone from the record -- requires one ordering")],
             "conferred": "as proposed (rq-063: item 7 accepted as presented; resolves rq-044 point 3)"},
            {"@id": "c:adjudicator:attack-cause", "@type": "Closure",
             "proposed": {"rule": ["with several replayed attacks, cause names the clause that sorts first (the same canonical order); every attacked dimension still enters contested_knockouts",
                                   "two reports on the same clause count once"],
                          "note": "the ratified union (rq-043) gives Suspended a single cause: string; reporting every clause would need that ratified type amended, so it is not proposed here"},
             "rationaleSource": [r("C-S3.W-CS3-D2", "cause: vacuous-pass:<CL> -- one clause"), r("R-S5", "registered as a contested knockout on the clause's dimension")],
             "conferred": "as proposed (rq-063: item 8 accepted as presented; resolves rq-044 point 4)"},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes adjudicator's signatures, the variant precedence, the meaning of a tie, and -- with the four PROPOSED closures -- a single defined output for every permitted input, closing your rq-044 diagnostic"},
    },
    {
        "@id": "sr:L3:ledger-interface", "@type": "SpecificationRecord",
        "title": "ledger's interface and hash encoding — append, verify, refuse a rewrite",
        "kind": "closure-bundle",
        "closes": ["diag:hash-preimage-encoding-unstated"],
        "addresses": ["sr:L2:C-S7", "sr:L2:LedgerEntry", "sr:L2:ledger"],
        "dependsOn": ["a:C-S7:W-CS7-N", "a:C-S7:W-CS7-D1", "a:C-S7:determinism", "a:LedgerEntry:fields"],
        "standalone": False,
        "amendmentOf": ["rq-034", "rq-042"],
        "assertions": [
            {"@id": "c:ledger:hash-encoding", "@type": "Closure",
             "proposed": {"rule": "hash = sha256 hex of the UTF-8 canonical JSON of [seq, prev, kind, payload] (keys sorted, compact separators) -- the amended source's four-field preimage",
                          "genesis": "the first entry has seq 1 and prev = 64 zeros",
                          "consequence": "a rewrite of kind alone changes the hash, so verifyChain fails on the tampered copy (W-CS7-Δ1 holds for every field)"},
             "rationaleSource": [r("C-S7.W-CS7-N", "<H7> = sha256(seq || prev || kind || payload) in the amended source; encoding and genesis unstated")],
             "conferred": "amended at rq-042 (1), on the source as amended by the architect (rq-038 = A)"},
            {"@id": "c:ledger:functions", "@type": "Closure",
             "proposed": {"signatures": ["entryHash(seq: number, prev: string, kind: string, payload: unknown): string",
                                         "nextEntry(chain: LedgerEntry[], kind: string, payload: unknown): LedgerEntry",
                                         "verifyChain(chain: LedgerEntry[]): { ok: true } | { ok: false; seq: number }",
                                         "checkAppendOnly(before: string, after: string): { ok: true } | { ok: false; code: \"H-LEDGER-01\" }",
                                         "appendEntry(ledgerPath: string, kind: string, payload: unknown): LedgerEntry"],
                          "rules": ["nextEntry and verifyChain use the same four-field preimage as entryHash; a kind-only rewrite fails verifyChain",
                                    "nextEntry is pure: seq = last seq + 1, prev = last hash (or genesis)",
                                    "checkAppendOnly: ok iff `after` begins with `before` byte for byte and adds whole JSONL lines",
                                    "appendEntry reads the JSONL file, appends nextEntry as one line, and never rewrites"]},
             "rationaleSource": [r("C-S7.W-CS7-N", "append; the full chain verifies"), r("C-S7.W-CS7-D1", "any rewrite -> exit 1, H-LEDGER-01; verification fails on the tampered copy"), r("S5.ledger", "append-only JSONL + chain verifier + hooks"), r("C-S7.determinism", "bit-stable given payload and chain position")],
             "conferred": "amended at rq-042 (2)-(4): entryHash takes kind; checkAppendOnly and appendEntry as proposed"},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes the ledger's functions and the hash encoding two implementations must agree on; the hook's decision is checkAppendOnly, so it is built and tested here"},
    },
]

ADJUDICATIONS = [
    {
        "@id": "adj:ledger-hash-kind", "@type": "Adjudication", "notACandidate": True,
        "presentedPer": "Amendment 2 (ii): presented as an adjudication, not a candidate; raised by the architect's diagnostic at rq-034",
        "conflict": "diag:W-CS7-N-vs-W-CS7-D1-kind-outside-the-hash",
        "theSourceSays": [
            {"label": "C-S7.W-CS7-N", "text": "<H₇> = sha256(seq ‖ prev ‖ payload) -- kind is not in the preimage", "layer": "L2, accepted at rq-037"},
            {"label": "C-S7.W-CS7-D1", "text": "any rewrite of an existing line -> hook exit 1 ...; chain verification fails loudly on the tampered copy", "layer": "L2, accepted at rq-037"},
        ],
        "theProblem": "a rewrite of kind alone (registration -> ratification) keeps every hash, so chain verification does NOT fail on that tampered copy; the hook's append-only check still refuses it",
        "options": [
            {"id": "A", "label": "Amend the source: kind enters the preimage",
             "content": "the SRS author amends W-CS7-N to hash = sha256(seq || prev || kind || payload); the spec is re-registered; c:ledger:hash-encoding is redrafted on [seq, prev, kind, payload].",
             "consequence": "the cleanest result, and the most expensive: SPEC.md's digest changes, and every fragment's identity includes the digest, so EVERY grounding in the slice and in WS-3 migrates (ARO 5.2); the A9 act and its amendment name the old digest and are re-stated; every accepted item re-binds. C-S7 waits for all of it."},
            {"id": "B", "label": "A design closure against the literal: kind enters the preimage at L3",
             "content": "c:ledger:hash-encoding hashes [seq, prev, kind, payload]; the conflict stays an OPEN diagnostic beside it, naming W-CS7-N's literal formula as departed from.",
             "consequence": "W-CS7-Δ1 becomes true and C-S7 can verify soon; but the ledger's bar then contradicts W-CS7-N's accepted literal ('sha256(seq || prev || payload)'), so a conforming implementation of the SOURCE would fail the bar. The departure is visible, not hidden."},
            {"id": "C", "label": "Read Δ1's chain clause narrowly",
             "content": "record the interpretation that Δ1's 'chain verification fails loudly' covers rewrites of seq, prev or payload, and that a kind-only rewrite is caught by the hook (checkAppendOnly, H-LEDGER-01). The preimage stays as the source states.",
             "consequence": "nothing is rebuilt and both accepted clauses stand; the C-S7 bar tests kind-tampering through the hook, not the chain. The weaker guarantee for kind is a recorded reading of the source, not a change to it."},
        ],
        "decision": None,
    },
    {
        "@id": "adj:ledger-hooks-repo-home", "@type": "Adjudication", "notACandidate": True,
        "presentedPer": "Amendment 2 (ii): presented as an adjudication, not a candidate",
        "conflict": "diag:ledger-hooks-repo-home",
        "theSourceSays": {"label": "S5.ledger", "text": "| `ledger` (append-only JSONL + chain verifier + hooks) | `ledger/`, `.githooks/` | C-S7 |", "layer": "L2"},
        "theFactorySays": {"cite": "loopToolchain", "value": "one TypeScript module per unit, src/<module>.ts; a git hook is not a module", "layer": "none — a toolchain fact, confers nothing"},
        "options": [
            {"id": "A", "label": "Hook logic in the module, wrapper outside the build",
             "content": "the ledger unit is src/ledger.ts and exports checkAppendOnly; .githooks/pre-commit is a two-line wrapper that calls it and exits 1 on H-LEDGER-01. The wrapper is listed as a non-built deliverable.",
             "consequence": "W-CS7-Δ1's decision ('refuse a rewrite, H-LEDGER-01') is built and tested; only the git wiring ('hook exit 1') is untested by the factory. The capability can verify; the hook's exit code is a documented gap."},
            {"id": "B", "label": "Source-amendment request",
             "content": "ask the SRS author to restate W-CS7-Δ1 as a function-level witness; until amended, W-CS7-Δ1 stays an L2 obligation the build cannot discharge.",
             "consequence": "C-S7 cannot reach VERIFIED until the source is amended and re-registered (the digest changes, fragments migrate)."},
            {"id": "C", "label": "Exclude W-CS7-Δ1 from the C-S7 bar",
             "content": "C-S7's ratified bar covers W-CS7-N and the determinism note only; W-CS7-Δ1 is recorded as uncovered.",
             "consequence": "C-S7 can verify, on a narrower bar; the tamper guarantee is unmeasured."},
        ],
        "decision": None,
    },
    {
        "@id": "adj:ws3-module-homes", "@type": "Adjudication", "notACandidate": True,
        "presentedPer": "Amendment 2 (ii): presented as an adjudication, not a candidate. Found while projecting WS-3: "
                        "the slice's layout convention (rq-001) expired on 2026-10-11 and was bound to the superseded "
                        "source, so nothing ratified says where these three modules' files go",
        "citesCurrentSource": True,     # decided on src:srs-spec@2, so it cites the CURRENT fragments, with their text
        "conflict": "diag:ws3-module-homes",
        "theSourceSays": [{"label": "S5.grader-runner", "layer": "L2, accepted (repoHome tools/grader-runner/)"},
                          {"label": "S5.adjudicator", "layer": "L2, accepted (repoHome tools/adjudicator/)"}],
        "theFactorySays": {"cite": "loopToolchain", "value": "one TypeScript module per unit at src/<module>.ts; a bar at test/<module>.test.mjs imports ../src/<module>.ts", "layer": "none — a toolchain fact, confers nothing"},
        "precedents": ["the slice: adj:author-agent-repo-home was decided A -- the accepted L2 home was honoured",
                       "WS-3: adj:ledger-hooks-repo-home was decided A at rq-035 -- the ledger unit is src/ledger.ts, departing from the source's ledger/"],
        "notInQuestion": "grading-types has no L2 home (it is an L3 module, rq-061), so it is src/grading-types.ts under every option; the ledger stays src/ledger.ts (rq-035)",
        "options": [
            {"id": "A", "label": "Factory layout, as rq-035 did for the ledger",
             "content": "grader-runner is src/grader-runner.ts and adjudicator is src/adjudicator.ts. The accepted homes tools/grader-runner/ and tools/adjudicator/ are listed in plan.json as departed from, by this decision.",
             "files": {"grading-types": "src/grading-types.ts", "grader-runner": "src/grader-runner.ts", "adjudicator": "src/adjudicator.ts"},
             "consequence": "the queued bars and oracles (rq-067..rq-072) stand as written and WS-3 can project once they are acted. The built tree does not follow s5's layout for these two components; the departure is recorded in the plan, not hidden."},
            {"id": "B", "label": "Honour the accepted L2 homes",
             "content": "grader-runner is tools/grader-runner/grader-runner.ts and adjudicator is tools/adjudicator/adjudicator.ts (the file name inside each home is model-proposed; the home is the source's).",
             "files": {"grading-types": "src/grading-types.ts", "grader-runner": "tools/grader-runner/grader-runner.ts", "adjudicator": "tools/adjudicator/adjudicator.ts"},
             "consequence": "the built tree follows s5 for both. The adjudicator bar (rq-067) and the C-S3 oracle (rq-069) import ../src/adjudicator.ts, so both are rewritten and re-queued: Ops re-verifies them and C-S3's acts move to a later sitting."},
            {"id": "C", "label": "Source-amendment request",
             "content": "ask the SRS author to restate s5's homes for the build.",
             "consequence": "the source digest changes again and every fragment migrates, as on 2026-10-17; nothing in WS-3 projects until the amended source is registered."},
        ],
        "decision": None,
    },
]


L2 = HERE.parent / "l2" / "srs-ws3.graph.jsonld"
QUEUE = HERE.parents[1] / "measurements" / "ratification-queue.jsonl"


def blocked_assertions(l2):
    """{assertion id: why} for every L2 assertion a bundle must not rest on silently: one listed beyond the acted
    region, or one pointing at an OPEN, blocking diagnostic (Ops finding 2026-10-01, the L3 hop of the region
    question)."""
    diags = {d["@id"]: d for d in l2["diagnostics"]}
    out = {b["assertion"]: "beyond the acted region (line %d; %s)" % (b["line"], b["diagnostic"])
           for b in l2["ws3"].get("beyondRegion", [])}
    for rec in l2["records"]:
        for a in rec["assertions"]:
            d = diags.get(a.get("diagnostic"))
            if d and d["status"] == "open" and d.get("blocking"):
                out.setdefault(a["@id"], "blocked by %s" % d["@id"])
    for d in l2["diagnostics"]:
        if d["status"] == "open" and d.get("blocking"):
            for x in d.get("blocks", []):
                out.setdefault(x, "blocked by %s" % d["@id"])
    return out


def undisclosed_blocked_dependencies(records, l2):
    """[(record, [assertions])] where a bundle depends on a blocked assertion its blockedDependencies does not
    name -- or names one that is no longer blocked (a stale disclosure is as wrong as a missing one)."""
    blocked = blocked_assertions(l2)
    bad = []
    for rec in records:
        hit = sorted(x for x in rec["dependsOn"] + rec["closes"] + rec["addresses"] if x in blocked)
        if hit != sorted(rec.get("blockedDependencies", [])):
            bad.append((rec["@id"], hit))
    return bad


def build():
    minted = json.loads(FRAGMENTS.read_text(encoding="utf-8"))["fragments"]
    frags = {f["label"]: f["fragmentId"] for f in minted}
    texts = {f["label"]: f["text"] for f in minted}
    # DECIDED adjudications are historical decisions about the source as it stood: they keep citing the fragments
    # they were decided on (the pre-amendment set), so their bytes -- and the architect's decisions -- stay bound.
    pinned = {f["label"]: f["fragmentId"] for f in json.loads(FRAGMENTS_2428.read_text(encoding="utf-8"))["fragments"]}

    def resolve(obj, frags=frags):
        if isinstance(obj, dict):
            out = {k: resolve(v, frags) for k, v in obj.items()}
            if "cite" in obj and obj["cite"] in frags:
                out = {"cite": frags[obj["cite"]], "label": obj["cite"], **{k: v for k, v in out.items() if k != "cite"}}
            if obj.get("label") in frags and "text" in obj and "fragment" not in obj:
                out = {"fragment": frags[obj["label"]], **out}
            return out
        if isinstance(obj, list):
            return [resolve(v, frags) for v in obj]
        return obj

    undisclosed = undisclosed_blocked_dependencies(RECORDS, json.loads(L2.read_text(encoding="utf-8")))
    if undisclosed:
        raise SystemExit("closure bundle(s) depend on a blocked L2 assertion without disclosing it "
                         "(declare it in blockedDependencies): %s" % undisclosed)
    cited = {c["cite"] for rec in RECORDS for a in rec["assertions"] for c in a["rationaleSource"]}
    unknown = sorted(c for c in cited if c not in frags and c != "loopToolchain")
    if unknown:
        raise SystemExit("unminted rationale label(s): %s" % unknown)
    queue = {json.loads(l)["id"]: json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()}
    for rec in RECORDS:
        if rec.get("amendmentOf"):
            rec["amendmentNotes"] = [{"item": i, "act": queue[i]["act"], "actor": queue[i]["actor"],
                                      "actedAt": queue[i]["actedAt"], "note": queue[i]["actNote"]}
                                     for i in rec["amendmentOf"]]
    return {
        "@context": {"@vocab": "https://fandaws.com/ontology/aro/spike-1.5/vocab#",
                     "_note": "Same flat spike vocabulary as the L2 graph. No BFO/CCO. Non-graduating (Amendment 2 iii)."},
        "@id": "spike:l3:srs-ws3:candidates",
        "@type": "DesignGraph",
        "layer": "L3",
        "status": "candidate",
        "title": "SRS adjudication and registration core (WS-3) — closure CANDIDATES (L3), bundled for ratification",
        "rule": "Amendment 2 (ii): every value below is conferred by the architect from these labeled candidates. Source passages appear only under rationaleSource, never under groundedBy (ARO D17).",
        "facetsDefault": {"origin": {"kind": "transformer", "actRef": "act:aro-dev-agent:2026-10-01:closure-proposals", "label": "model-proposed; confers nothing (ARO 4.2)"},
                          "grounding": "absent (forbidden for L3)", "ratification": "unratified",
                          "_authority": "computed, never stored: not AUTHORITATIVE until the architect's act"},
        "rationaleSources": {"l2": "spike/graph/l2/srs-ws3.graph.jsonld and its fragments (spike/graph/ws3/fragments.json) -- cited, never grounding",
                             "loopToolchain": "IntegratedAgent runtime (TypeScript modules imported as ./name.ts; node:test) -- a toolchain fact, not a statement in the SRS. Citation only.",
                             "design": "IntegratedAgent experiments/comms/DEV-2026-10-01-d8-part2-design.md"},
        "records": resolve(RECORDS),
        "adjudications": [resolve(with_source_text(a, texts), frags) if a.get("citesCurrentSource")
                          else resolve(a, pinned) for a in ADJUDICATIONS],
    }


def with_source_text(adj, texts):
    """The source passages an adjudication puts beside the factory fact, copied from the minted fragments -- never
    retyped, so the text the architect reads is the text whose hash the fragment carries."""
    out = dict(adj)
    out["theSourceSays"] = [dict(s, text=texts[s["label"]]) for s in adj["theSourceSays"]]
    return out


def render(graph):
    return json.dumps(graph, ensure_ascii=False, indent=2) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)
    text = render(build())
    if args.check:
        ok = OUT.exists() and OUT.read_text(encoding="utf-8") == text
        print("srs-ws3.design.candidates.jsonld %s a rebuild" % ("matches" if ok else "differs from"),
              file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 1
    OUT.write_bytes(text.encode("utf-8"))
    print("%d closure record(s), %d closure(s), %d adjudication(s) -> %s" % (
        len(RECORDS), sum(len(x["assertions"]) for x in RECORDS), len(ADJUDICATIONS), OUT.relative_to(HERE.parents[2])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
