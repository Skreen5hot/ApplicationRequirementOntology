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
        "title": "WS-3 record types — GradeRecord, AdjudicatedReport, LedgerEntry, the C-S5 report",
        "kind": "closure-bundle",
        "closes": ["diag:GradeRecord-fields-by-example"],
        "addresses": ["sr:L2:GradeRecord", "sr:L2:LedgerEntry", "sr:L2:S-S3", "sr:L2:C-S3"],
        "dependsOn": ["a:GradeRecord:fields", "a:LedgerEntry:fields", "a:S-S3:seam", "a:C-S3:W-CS3-D1", "a:C-S3:W-CS3-D2"],
        "standalone": False,
        "assertions": [
            {"@id": "c:ws3:Score-Vector", "@type": "Closure",
             "proposed": {"declarations": ["export type Score = 0 | 1 | 2;", "export type Vector = Record<string, Score>;"],
                          "note": "dimension keys are strings (P1..P11 in the examples); the source does not close the key set, so none is proposed"},
             "rationaleSource": [r("C-S2.determinism", "every score in {0, 1, 2}"), r("S6.S-S2", "the crossing example's vector carries P1..P11")]},
            {"@id": "c:ws3:GradeRecord", "@type": "Closure",
             "proposed": {"fields": [
                 {"name": "rater", "type": "string"},
                 {"name": "model", "type": "string", "optional": True, "note": "in W-CS2-N, absent from the S-S2 example -- optionality is the architect's decision"},
                 {"name": "manifest_hash", "type": "string", "note": "sha256 hex of the manifest"},
                 {"name": "vector", "type": "Vector"},
                 {"name": "evidence", "type": "Record<string, string>", "note": "dimension -> spec.md:<line>"},
                 {"name": "disposition", "type": "string", "optional": True, "note": "as model"},
                 {"name": "readiness", "type": "string", "optional": True, "note": "as model"},
                 {"name": "provisional", "type": "boolean"}]},
             "rationaleSource": [r("C-S2.W-CS2-N", "eight fields"), r("S6.S-S2", "five of them; model, disposition, readiness absent")]},
            {"@id": "c:ws3:RouteResult", "@type": "Closure",
             "proposed": {"fields": [{"name": "route", "type": "Record<string, \"third-rater\">"},
                                     {"name": "contested_knockouts", "type": "string[]"}]},
             "rationaleSource": [r("C-S3.W-CS3-N", "the literal {\"route\": {\"P6\": \"third-rater\"}, \"contested_knockouts\": []}")]},
            {"@id": "c:ws3:AdjudicatedReport", "@type": "Closure",
             "proposed": {"fields": [
                 {"name": "vector", "type": "Vector", "optional": True, "note": "absent when the disposition line is WITHHELD"},
                 {"name": "disposition", "type": "string", "optional": True},
                 {"name": "readiness", "type": "string", "optional": True},
                 {"name": "disposition_line", "type": "\"WITHHELD\" | \"SUSPENDED\"", "optional": True},
                 {"name": "cause", "type": "string", "optional": True, "note": "vacuous-pass:<CL>"},
                 {"name": "queue", "type": "\"human\"", "optional": True},
                 {"name": "contested_knockouts", "type": "string[]"},
                 {"name": "provisional", "type": "boolean"}],
                          "note": "one record covering the three literal outputs the source shows (S-S3, W-CS3-Δ1, W-CS3-Δ2); the alternative -- a tagged union of three shapes -- is equally consistent with the source"},
             "rationaleSource": [r("S6.S-S3", "the adjudicated report"), r("C-S3.W-CS3-D1", "WITHHELD output"), r("C-S3.W-CS3-D2", "SUSPENDED output")]},
            {"@id": "c:ws3:VacuousPassReport", "@type": "Closure",
             "proposed": {"fields": [{"name": "clause", "type": "string"}, {"name": "dimension", "type": "string"},
                                     {"name": "replayed", "type": "true"}],
                          "note": "the C-S5 report's shape is not stated in the region (diag:W-CS3-D2-needs-a-C-S5-report); this is the minimal shape C-S3 reads -- which clause, which dimension it knocks out (R-S5), and that it replayed. The freeze-2 replay fixture must conform to it."},
             "rationaleSource": [r("C-S3.W-CS3-D2", "a replayed stub report on clause <CL>"), r("R-S5", "registered as a contested knockout on the clause's dimension")]},
            {"@id": "c:ws3:LedgerEntry", "@type": "Closure",
             "proposed": {"fields": [{"name": "seq", "type": "number"}, {"name": "prev", "type": "string"},
                                     {"name": "kind", "type": "string", "note": "registration and ratification appear; the set is not closed, so string"},
                                     {"name": "payload", "type": "unknown"}, {"name": "hash", "type": "string"}]},
             "rationaleSource": [r("C-S7.W-CS7-N", "the literal entry"), r("J-S4.chain", "kind ratification")]},
        ],
        "displayDuties": {"whatRatifyingDoes": "these become the `declarations` of grading-types; typed fields are ENFORCEABLE in the factory (F6 rule), so a producer may reject a wrong-typed value"},
    },
    {
        "@id": "sr:L3:grader-runner-interface", "@type": "SpecificationRecord",
        "title": "grader-runner's interface — the rater is injected, every other limb is deterministic",
        "kind": "closure-bundle",
        "closes": [],
        "addresses": ["sr:L2:C-S2", "sr:L2:R-S1", "sr:L2:grader-runner"],
        "dependsOn": ["a:C-S2:W-CS2-N", "a:C-S2:W-CS2-D1", "a:C-S2:W-CS2-D2", "a:C-S2:determinism", "a:R-S1:rule"],
        "standalone": False,
        "assertions": [
            {"@id": "c:grader-runner:assembleManifest", "@type": "Closure",
             "proposed": {"signature": "assembleManifest(specPath: string, rev: string): string[]",
                          "returns": "[`${specPath}@${rev}`, \"method/v0.4.md\", \"skills/fspec-method\"] -- exactly the R-S1 triple"},
             "rationaleSource": [r("R-S1", "context MUST contain exactly {spec@rev, method/v0.4.md, skills/fspec-method}")]},
            {"@id": "c:grader-runner:checkIsolation", "@type": "Closure",
             "proposed": {"signature": "checkIsolation(manifest: string[]): { ok: true } | { ok: false; code: \"G-ISO-01\" }",
                          "rule": "ok iff the manifest is exactly the R-S1 triple for some spec@rev (order-insensitive, no extra entries)"},
             "rationaleSource": [r("C-S2.W-CS2-D2", "manifest containing findings/cycle-3/ -> rejected, G-ISO-01"), r("V-S3", "manifest a subset of the R-S1 triple; violations rejected before adjudication")]},
            {"@id": "c:grader-runner:manifestHash", "@type": "Closure",
             "proposed": {"signature": "manifestHash(manifest: string[]): string",
                          "rule": "sha256 hex of the UTF-8 canonical JSON of the manifest sorted ascending"},
             "rationaleSource": [r("C-S2.determinism", "<H> = sha256 of the manifest -- the serialization is not stated, so one is proposed")]},
            {"@id": "c:grader-runner:verifyGradeRecord", "@type": "Closure",
             "proposed": {"signature": "verifyGradeRecord(record: GradeRecord, resolves: (pointer: string) => boolean): { ok: true } | { ok: false; code: \"G-EVID-01\" | \"G-SCORE-01\" }",
                          "rule": "G-EVID-01 when any evidence pointer does not resolve (resolves is injected: 'checked against derived/' is outside the module); G-SCORE-01 when any score is outside {0, 1, 2}",
                          "note": "G-SCORE-01 is a proposed code: the source states the property but names no code for its violation"},
             "rationaleSource": [r("C-S2.W-CS2-D1", "spec.md:9999 -> verifier rejects, G-EVID-01"), r("C-S2.determinism", "every score in {0, 1, 2}; every evidence pointer resolves at the cited rev")]},
            {"@id": "c:grader-runner:runGrader", "@type": "Closure",
             "proposed": {"signature": "runGrader(invoke: RaterInvoker, rater: string, manifest: string[]): Promise<GradeRecord>",
                          "alsoExports": ["export type RaterInvoker = (manifest: string[]) => Promise<{ model: string; vector: Vector; evidence: Record<string, string>; disposition?: string; readiness?: string }>",
                                          "export class GradeRejectedError extends Error { code: \"G-ISO-01\" }"],
                          "rule": "checkIsolation first -- a contaminated manifest throws GradeRejectedError(G-ISO-01) and the invoker is NEVER called; otherwise the record is the invoker's output plus rater, manifest_hash = manifestHash(manifest), provisional: true"},
             "rationaleSource": [r("C-S2.W-CS2-N", "headless invocation -> grade record with provisional: true"), r("R-S6", "every single-rater record carries provisional: true"), r("C-S2.W-CS2-D2", "the grade never enters adjudication")]},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes grader-runner's signatures; the injected RaterInvoker is what keeps C-S2 testable without a model -- and why C-S2's live bar can honestly stay provisional (the control)"},
    },
    {
        "@id": "sr:L3:adjudicator-interface", "@type": "SpecificationRecord",
        "title": "adjudicator's interface — pure routing, third rater and C-S5 reports as parameters",
        "kind": "closure-bundle",
        "closes": ["diag:third-rater-tie-unwitnessed"],
        "addresses": ["sr:L2:C-S3", "sr:L2:R-S4", "sr:L2:R-S5", "sr:L2:adjudicator"],
        "dependsOn": ["a:C-S3:W-CS3-N", "a:C-S3:W-CS3-D1", "a:C-S3:W-CS3-D2", "a:C-S3:determinism", "a:R-S4:rule", "a:R-S5:rule", "a:V-S2:invariant"],
        "standalone": False,
        "assertions": [
            {"@id": "c:adjudicator:route", "@type": "Closure",
             "proposed": {"signature": "route(a: GradeRecord, b: GradeRecord): RouteResult",
                          "rule": "contested_knockouts = every dimension where either rater scored 0; route[d] = \"third-rater\" for every other dimension where a and b differ. Pure; same inputs, same output."},
             "rationaleSource": [r("R-S4", "either-rater zero -> contested knockout; nonzero disagreement -> third rater"), r("C-S3.W-CS3-N", "P6 2 vs 1 -> third-rater"), r("C-S3.determinism", "a pure function of the two committed vectors")]},
            {"@id": "c:adjudicator:adjudicate", "@type": "Closure",
             "proposed": {"signature": "adjudicate(a: GradeRecord, b: GradeRecord, opts?: { c?: GradeRecord; attacks?: VacuousPassReport[] }): AdjudicatedReport",
                          "rule": ["contested knockouts -> { disposition_line: \"WITHHELD\", contested_knockouts, queue: \"human\" } (no disposition)",
                                   "else a replayed attack -> { disposition_line: \"SUSPENDED\", cause: \"vacuous-pass:<clause>\", queue: \"human\" }, its dimension added to contested_knockouts",
                                   "else every routed dimension takes the value at least two of a, b, c share; vector complete -> provisional: false",
                                   "a routed dimension with no c -> provisional: true, the dimension listed in route (not decided)",
                                   "a routed dimension where a, b and c all differ -> a third-rater tie -> queue: \"human\""],
                          "note": "the rater C invocation itself is NOT in this module: c is a parameter, so the deterministic limb is testable on a replayed rater-C record (A9's fixture) and the agentic call stays with the caller"},
             "rationaleSource": [r("C-S3.W-CS3-N", "after rater C: P6 = C's consensus value, provisional: false"), r("C-S3.W-CS3-D1", "WITHHELD, queue human"), r("C-S3.W-CS3-D2", "SUSPENDED, cause vacuous-pass:<CL>"), r("R-S5", "a verified attack overrides the number"), r("S5.adjudicator", "pure routing fn + third-rater invocation")]},
            {"@id": "c:adjudicator:tie", "@type": "Closure",
             "proposed": {"definition": "a third-rater tie is a routed dimension on which a, b and c are pairwise different",
                          "consequence": "queue: \"human\", the dimension in contested_knockouts, no disposition"},
             "rationaleSource": [r("R-S4", "a third-rater tie -> human -- 'tie' is not defined in the source")]},
            {"@id": "c:adjudicator:disposition-text", "@type": "Closure",
             "proposed": {"rule": "adjudicate does not compute disposition or readiness text; it carries them through only when supplied by the caller",
                          "why": "they recompute 'per method s6.2', which is outside the registered source (diag:external-method-artifacts, left open)"},
             "rationaleSource": [r("V-S2", "the printed lines recompute from the committed GradeRecords per method s6.2")]},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes adjudicator's signatures and the meaning of a third-rater tie; W-CS3-N's second half and W-CS3-Δ2 then run on the two replay fixtures A9 names"},
    },
    {
        "@id": "sr:L3:ledger-interface", "@type": "SpecificationRecord",
        "title": "ledger's interface and hash encoding — append, verify, refuse a rewrite",
        "kind": "closure-bundle",
        "closes": ["diag:hash-preimage-encoding-unstated"],
        "addresses": ["sr:L2:C-S7", "sr:L2:LedgerEntry", "sr:L2:ledger"],
        "dependsOn": ["a:C-S7:W-CS7-N", "a:C-S7:W-CS7-D1", "a:C-S7:determinism", "a:LedgerEntry:fields"],
        "standalone": False,
        "assertions": [
            {"@id": "c:ledger:hash-encoding", "@type": "Closure",
             "proposed": {"rule": "hash = sha256 hex of the UTF-8 canonical JSON of [seq, prev, payload] (keys sorted, compact separators); kind is NOT in the preimage, as the source states",
                          "genesis": "the first entry has seq 1 and prev = 64 zeros",
                          "note": "kind outside the preimage means a rewrite of kind alone keeps the hash; checkAppendOnly still refuses it"},
             "rationaleSource": [r("C-S7.W-CS7-N", "<H7> = sha256(seq || prev || payload); the chain verifies from genesis -- encoding and genesis unstated")]},
            {"@id": "c:ledger:functions", "@type": "Closure",
             "proposed": {"signatures": ["entryHash(seq: number, prev: string, payload: unknown): string",
                                         "nextEntry(chain: LedgerEntry[], kind: string, payload: unknown): LedgerEntry",
                                         "verifyChain(chain: LedgerEntry[]): { ok: true } | { ok: false; seq: number }",
                                         "checkAppendOnly(before: string, after: string): { ok: true } | { ok: false; code: \"H-LEDGER-01\" }",
                                         "appendEntry(ledgerPath: string, kind: string, payload: unknown): LedgerEntry"],
                          "rules": ["nextEntry is pure: seq = last seq + 1, prev = last hash (or genesis)",
                                    "checkAppendOnly: ok iff `after` begins with `before` byte for byte and adds whole JSONL lines",
                                    "appendEntry reads the JSONL file, appends nextEntry as one line, and never rewrites"]},
             "rationaleSource": [r("C-S7.W-CS7-N", "append; the full chain verifies"), r("C-S7.W-CS7-D1", "any rewrite -> exit 1, H-LEDGER-01; verification fails on the tampered copy"), r("S5.ledger", "append-only JSONL + chain verifier + hooks"), r("C-S7.determinism", "bit-stable given payload and chain position")]},
        ],
        "displayDuties": {"whatRatifyingDoes": "fixes the ledger's functions and the hash encoding two implementations must agree on; the hook's decision is checkAppendOnly, so it is built and tested here"},
    },
]

ADJUDICATIONS = [
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
]


def build():
    frags = {f["label"]: f["fragmentId"] for f in json.loads(FRAGMENTS.read_text(encoding="utf-8"))["fragments"]}

    def resolve(obj):
        if isinstance(obj, dict):
            out = {k: resolve(v) for k, v in obj.items()}
            if "cite" in obj and obj["cite"] in frags:
                out = {"cite": frags[obj["cite"]], "label": obj["cite"], **{k: v for k, v in out.items() if k != "cite"}}
            if obj.get("label") in frags and "text" in obj and "fragment" not in obj:
                out = {"fragment": frags[obj["label"]], **out}
            return out
        if isinstance(obj, list):
            return [resolve(v) for v in obj]
        return obj

    cited = {c["cite"] for rec in RECORDS for a in rec["assertions"] for c in a["rationaleSource"]}
    unknown = sorted(c for c in cited if c not in frags and c != "loopToolchain")
    if unknown:
        raise SystemExit("unminted rationale label(s): %s" % unknown)
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
        "adjudications": resolve(ADJUDICATIONS),
    }


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
