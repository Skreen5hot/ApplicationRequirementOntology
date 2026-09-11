"""Deterministic projection of the SRS slice -- Arm B step 5 (SPIKE.md 3; ARO v0.5.2 11, 11.1, D15, D20).

WHAT IT EMITS, from eligible Accepted L2 (+) eligible Ratified L3 and nothing else: plan.json in the
loop's shape, the `declared` tier, the Planner Contract, the Builder Brief and the Tester Contract.
Every output embeds the same Projection Input Manifest and its digest, so the seam's identity reaches
every consumer from one place through one manifest -- which is the whole FX-SEAM-A property.

WHAT IT REFUSES TO DO. It does not read the source prose, resolve an ambiguity, or fill a gap (D20).
It does not project a record nobody has acted on: eligibility is read from the ratification queue,
bound to the record's content address (D23), and an unacted record makes the whole projection refuse
with the list of acts it is waiting on. That refusal is the expected state until the architect acts;
routing around it would be the agent simulating ratification, which voids spike 2 (SPIKE.md 4).

DETERMINISM IS CHECKED, NOT ASSUMED (ARO 8.1, 11.1): `--check` projects twice and requires byte
identity; that comparison is the recorded basis of the `Projected` status. Canonical bytes come from
the one canonicalization implementation the spike has (layout_rule.canonical), per D23.

    python spike/projections/project.py --selftest          # synthetic graph + synthetic acts, never the real queue
    python spike/projections/project.py --check             # the real slice: refuses until acted on
    python spike/projections/project.py -o spike/projections/out
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPIKE = HERE.parent
GRAPH = SPIKE / "graph"
L2_PATH = GRAPH / "l2" / "srs-slice.graph.jsonld"
L3_PATH = GRAPH / "l3" / "srs-slice.design.candidates.jsonld"
CONVENTION_PATH = GRAPH / "l3" / "convention-closure.candidate.json"
FRAGMENTS_PATH = GRAPH / "fragments.json"
QUEUE_PATH = SPIKE / "measurements" / "ratification-queue.jsonl"
OUTPUT_NAMES = ("plan", "declared", "plannerContract", "builderBrief", "testerContract")
COMPILER = {"component": "spike.projector", "version": "0.1-draft"}
AGENT_ACTORS = {"agent", "dev-agent", "assistant", "claude", "model", "transformer"}
RATIFYING_ACTS = {"accepted", "ratified", "decided", "affirmed"}
CONVENTION_RECORD = "sr:L3:layout-convention"
ADJUDICATION = "adj:author-agent-repo-home"


def _load_tool(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


layout_rule = _load_tool("spike_layout_rule", GRAPH / "rules" / "layout_rule.py")
fragments_tool = _load_tool("spike_fragments", GRAPH / "fragments.py")
canonical, digest = layout_rule.canonical, layout_rule.digest


class Refused(Exception):
    """Projection declined. Carries what it is waiting on, when that is the reason."""

    def __init__(self, message: str, awaiting: list | None = None):
        super().__init__(message)
        self.awaiting = awaiting or []


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def file_digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------- eligibility

def _live(queue: list[dict]) -> list[dict]:
    superseded = {r.get("supersedes") for r in queue if r.get("supersedes")}
    return [r for r in queue if not r.get("supersededBy") and r.get("id") not in superseded]


def act_for(queue: list[dict], record_id: str, current_digest: str | None, artifact: str | None = None):
    """The act that makes a record eligible, or the reason it is not -> (row | None, reason | None)."""
    rows = [r for r in _live(queue) if r.get("record") == record_id
            or (artifact and r.get("artifact") == artifact)]
    if not rows:
        return None, "%s: not queued" % record_id
    for r in rows:
        actor = (r.get("actor") or "").strip().lower()
        if r.get("actedAt") and actor in AGENT_ACTORS:
            raise Refused("%s records an act by %r; the agent simulated a ratification act and the "
                          "spike is void (SPIKE.md 4)" % (r.get("id"), actor))
    acted = [r for r in rows if r.get("actedAt") and (r.get("act") or "").lower() in RATIFYING_ACTS
             and (r.get("actor") or "").strip()]
    if not acted:
        return None, "%s: queued as %s, no act yet" % (record_id, ", ".join(r["id"] for r in rows))
    for r in acted:
        bound = r.get("recordDigest") or r.get("artifactFileDigest")
        if current_digest is None or bound == current_digest:
            return r, None
    return None, ("%s: acted on at a different content address; the record changed since, so it "
                  "needs a new act (D23)" % record_id)


def eligibility(l2: dict, l3: dict, convention: dict, queue: list[dict],
                convention_artifact: str, rule_artifact: str | None = None,
                rule_digest: str | None = None) -> tuple[dict, list[str]]:
    acts, awaiting = {}, []
    # The derivation rule that produces `files` is itself a governed, content-addressed artifact
    # (ARO 9): it must be ratified at the digest of the bytes about to run.
    row, why = act_for(queue, "rule:layout-derivation", rule_digest, rule_artifact)
    (acts.__setitem__("rule:layout-derivation", row) if row else awaiting.append(why))
    for rec in l2["records"]:
        row, why = act_for(queue, rec["@id"], digest(rec))
        (acts.__setitem__(rec["@id"], row) if row else awaiting.append(why))
    for rec in l3["records"]:
        if rec["@id"] == CONVENTION_RECORD:
            row, why = act_for(queue, rec["@id"], file_digest_or_none(convention_artifact), convention_artifact)
        else:
            row, why = act_for(queue, rec["@id"], digest(rec))
        (acts.__setitem__(rec["@id"], row) if row else awaiting.append(why))
    for adj in l3.get("adjudications", []):
        row, why = act_for(queue, adj["@id"], digest(adj))
        if row and not row.get("decision"):
            why = "%s: acted on without a recorded decision" % adj["@id"]
            row = None
        (acts.__setitem__(adj["@id"], row) if row else awaiting.append(why))
    return acts, awaiting


def file_digest_or_none(path: str | None):
    try:
        return file_digest(SPIKE.parent / path) if path else None
    except OSError:
        return None


# ---------------------------------------------------------------- composing

def _closures(l3: dict) -> dict:
    out = {}
    for rec in l3["records"]:
        for a in rec.get("assertions", []):
            if "proposed" in a:
                out[a["@id"]] = {"proposed": a["proposed"], "record": rec["@id"], "digest": digest(a)}
    return out


def _assertions(l2: dict) -> dict:
    return {a["@id"]: dict(a, record=rec["@id"]) for rec in l2["records"] for a in rec["assertions"]}


def _fragment_index(fragments: dict) -> dict:
    return {f["fragmentId"]: f for f in fragments["fragments"]}


def _render_scope(module: str, realizes: list[str], l2: dict, frags: dict, closures: dict) -> str:
    """A fixed template over ratified fields. No prose is written here: statements are the L2
    assertions' own, fragment text is the source's, closure content is the record's."""
    lines = ["Module %s." % module, "", "REALIZES (L2, source semantics):"]
    by_record = {rec["@id"]: rec for rec in l2["records"]}
    for rid in realizes:
        rec = by_record[rid]
        lines.append("- %s: %s" % (rid, rec["title"]))
        for a in rec["assertions"]:
            lines.append("  [%s] %s" % (a["@id"], a["statement"]))
            for g in a.get("groundedBy", []):
                f = frags[g["fragment"]]
                lines.append("    grounded (%s) in %s, line %s: %s" % (g["role"], f["fragmentId"], f["display"]["lines"], f["text"]))
    mine = {cid: c for cid, c in closures.items()
            if cid.split(":")[1] in _module_prefixes(module)}
    if mine:
        lines.append("")
        lines.append("CLOSURES (L3, ratified design; not source semantics):")
        for cid in sorted(mine):
            lines.append("  [%s] %s" % (cid, canonical(mine[cid]["proposed"]).decode("utf-8").strip()))
    return "\n".join(lines)


def _module_prefixes(module: str) -> set:
    return {"contract": {"contract"}, "panel-findings-store": {"store"}, "author-agent": {"author-agent", "seam"}}[module]


def project(l2: dict, l3: dict, convention: dict, fragments: dict, queue: list[dict], *,
            independent_derivation: bool = False, verify_fragments=None,
            file_digests: dict | None = None, convention_artifact: str = "",
            rule_artifact: str | None = None, rule_digest: str | None = None) -> dict:
    frags = _fragment_index(fragments)
    missing = sorted({g["fragment"] for a in _assertions(l2).values() for g in a.get("groundedBy", [])} - set(frags))
    if missing:
        raise Refused("L2 cites fragments that do not exist: %s" % missing)
    lapsed = verify_fragments() if verify_fragments else []
    if lapsed:
        raise Refused("grounding lapsed (ARO 5.2): %s" % lapsed)

    acts, awaiting = eligibility(l2, l3, convention, queue, convention_artifact,
                                 rule_artifact, rule_digest)
    if awaiting:
        raise Refused("projection refused: %d record(s) are not eligible" % len(awaiting), awaiting)

    closures = _closures(l3)
    decision = acts[ADJUDICATION].get("decision")
    edges = closures["c:deps:edges"]["proposed"]["depends_on"]
    realizes = closures["c:realizes"]["proposed"]["realizes"]
    assertions = _assertions(l2)

    components = [
        {"id": "c:contract:component", "layer": "L3", "name": "contract", "assertionDigest": closures["c:contract:component"]["digest"]},
        {"id": "c:store:component", "layer": "L3", "name": "panel-findings-store", "assertionDigest": closures["c:store:component"]["digest"]},
        {"id": "a:author-agent:component", "layer": "L2", "name": "author-agent", "assertionDigest": digest(assertions["a:author-agent:component"])},
    ]
    layout = layout_rule.derive(components, convention)
    files = {d["moduleId"]: d["files"] for d in layout["derivations"]}
    provisional = []
    if decision == "A":
        files["author-agent"] = [assertions["a:author-agent:component"]["attributes"]["repoHome"]]
    elif decision == "B":
        raise Refused("adjudication decided B: awaiting the source amendment; author-agent's files cannot be projected", ["source amendment of SRS 5"])
    elif decision == "C":
        provisional.append("author-agent.files (conflict with L2 left open by adjudication C)")
    else:
        raise Refused("adjudication %s decided %r, which is not one of its options" % (ADJUDICATION, decision))

    seam = closures["c:seam:author-agent-reads-store"]["proposed"]
    store_exports = [closures[c]["proposed"] for c in ("c:store:appendFinding", "c:store:getFinding", "c:store:listFindings")]
    author_export = closures["c:author-agent:interface"]["proposed"]
    contract_types = ["Finding", "Disposition", "DispositionKind", "ProposeRevisionsInput", "ProposeRevisionsResult", "RevisionRefusal"]

    def covers(module):
        secs = set()
        for rid in realizes[module]:
            rec = [r for r in l2["records"] if r["@id"] == rid][0]
            for a in rec["assertions"]:
                for g in a.get("groundedBy", []):
                    secs.add(frags[g["fragment"]]["display"]["section"])
        return sorted(secs)

    finding_fields = [f["name"] for f in assertions["a:Finding:fields"]["fields"]]
    disposition_fields = [f["name"] for f in assertions["a:Disposition:record"]["fields"]]
    declarations = {
        "contract": [
            {"name": "Finding", "fields": finding_fields, "layer": "L2", "record": "sr:L2:Finding"},
            {"name": "Disposition", "fields": disposition_fields, "layer": "L2", "record": "sr:L2:Disposition"},
            {"name": "DispositionKind", "enumeration": assertions["a:Disposition:record"]["fields"][1]["enumeration"], "layer": "L2", "record": "sr:L2:Disposition"},
            {"name": "ProposeRevisionsInput", "fields": sorted(closures["c:contract:ProposeRevisionsInput"]["proposed"]["fields"]), "layer": "L3", "record": "sr:L3:module-boundaries"},
            {"name": "ProposeRevisionsResult", "fields": sorted(closures["c:contract:ProposeRevisionsResult"]["proposed"]["fields"]), "layer": "L3", "record": "sr:L3:module-boundaries"},
            {"name": "RevisionRefusal", "fields": sorted(closures["c:contract:RevisionRefusal"]["proposed"]["fields"]), "layer": "L3", "record": "sr:L3:module-boundaries"},
        ],
        "panel-findings-store": [{"name": "FindingInput", "definition": closures["c:store:FindingInput"]["proposed"]["definition"], "layer": "L3", "record": "sr:L3:panel-findings-store-interface"}],
        "author-agent": [],
    }
    signatures = {
        "contract": [],
        "panel-findings-store": [{"export": e["export"], "signature": e["signature"], "layer": "L3", "record": "sr:L3:panel-findings-store-interface"} for e in store_exports],
        "author-agent": [{"export": author_export["export"], "signature": author_export["signature"], "layer": "L3", "record": "sr:L3:module-boundaries"}],
    }
    exports = {m: [s["export"] for s in signatures[m]] + [d["name"] for d in declarations[m]] for m in edges}

    units = []
    for module in sorted(edges):
        units.append({
            "id": module, "files": files[module], "covers": covers(module), "kind": "code",
            "depends_on": sorted(edges[module]),
            "scope": _render_scope(module, realizes[module], l2, frags, closures),
            "signatures": signatures[module], "declarations": declarations[module],
        })

    author_imports = ([{"module": "panel-findings-store", "symbol": s} for s in seam["members"]]
                      + [{"module": "contract", "symbol": t} for t in ("Finding", "Disposition", "DispositionKind")])
    store_imports = [{"module": "contract", "symbol": "Finding"}]

    planner_store = [{"name": e["export"], "signature": e["signature"]} for e in store_exports]
    tester_calls = [{"module": "panel-findings-store", "symbol": s} for s in seam["members"]]
    if independent_derivation:
        # TEST-ASSEMBLED ONLY (ARO 13): the Planner Contract and the bar are derived from the L2 graph
        # by themselves, where the store's read members are absent -- the second derivation path that
        # single-source projection removes. There is no production switch for this.
        planner_store = [{"name": "unspecified", "signature": "unspecified (L2 states no read interface: diag:store-read-interface-unstated)"}]
        tester_calls = [{"module": "panel-findings-store", "symbol": "unspecified"}]

    outputs = {
        "plan": {"units": units, "capabilities": [], "oracles": []},
        "declared": {m: {"module": m, "tier": "declared",
                         "exports": [{"name": s["export"], "signature": s["signature"], "layer": s["layer"], "record": s["record"]} for s in signatures[m]]
                                    + [{"name": d["name"], "shape": {k: v for k, v in d.items() if k not in ("name", "layer", "record")}, "layer": d["layer"], "record": d["record"]} for d in declarations[m]]}
                     for m in sorted(edges)},
        "plannerContract": {"interfaces": {
            "contract": {"exports": [{"name": t} for t in contract_types], "depends_on": [], "forbidden_imports": []},
            "panel-findings-store": {"exports": planner_store, "depends_on": sorted(edges["panel-findings-store"]), "forbidden_imports": []},
            "author-agent": {"exports": [{"name": author_export["export"], "signature": author_export["signature"]}], "depends_on": sorted(edges["author-agent"]), "forbidden_imports": []}}},
        "builderBrief": {"briefs": {
            "contract": {"mustExport": contract_types, "imports": []},
            "panel-findings-store": {"mustExport": exports["panel-findings-store"], "imports": store_imports, "interfacesBlock": {"contract": contract_types}},
            "author-agent": {"mustExport": exports["author-agent"], "imports": author_imports, "callsPerArchitecture": tester_calls,
                             "interfacesBlock": {"contract": contract_types, "panel-findings-store": [e["name"] for e in planner_store]}}}},
        "testerContract": {"tests": {
            "contract": {"assertsExports": contract_types},
            "panel-findings-store": {"assertsExports": exports["panel-findings-store"]},
            "author-agent": {"assertsExports": exports["author-agent"], "assertsCalls": tester_calls}}},
    }

    fd = file_digests or {}
    manifest = {
        "l2": {"graphDigest": fd.get("l2") or digest(l2),
               "acceptanceHead": {"specDigest": l2["source"]["digest"],
                                  "head": sorted(acts[r["@id"]]["id"] for r in l2["records"]),
                                  "seq": len(l2["records"])}},
        "l3": [{"designGraphDigest": fd.get("l3") or digest(l3),
                "ratificationHead": sorted(acts[r["@id"]]["id"] for r in l3["records"] if r["@id"] != CONVENTION_RECORD)},
               {"designGraphDigest": fd.get("convention") or digest(convention),
                "ratificationHead": [acts[CONVENTION_RECORD]["id"]]},
               {"adjudication": ADJUDICATION, "decision": decision, "act": acts[ADJUDICATION]["id"]}],
        "semanticDependencyManifestDigest": digest(l2["semanticDependencyManifest"]),
        "compiler": dict(COMPILER, digest=file_digest(Path(__file__))),
        "provisional": provisional,
        "independentDerivation": independent_derivation,
    }
    manifest_digest = digest(manifest)
    for name in OUTPUT_NAMES:
        outputs[name]["projectionInputManifest"] = manifest
        outputs[name]["projectionInputManifestDigest"] = manifest_digest
    outputs["manifest"] = manifest
    return outputs


# ------------------------------------------------------------------ surfaces

def load_real():
    l2, l3, convention, fragments = _json(L2_PATH), _json(L3_PATH), _json(CONVENTION_PATH), _json(FRAGMENTS_PATH)
    queue = _rows(QUEUE_PATH)
    return l2, l3, convention, fragments, queue


def project_real(*, independent_derivation: bool = False) -> dict:
    l2, l3, convention, fragments, queue = load_real()
    return project(l2, l3, convention, fragments, queue,
                   independent_derivation=independent_derivation,
                   verify_fragments=lambda: fragments_tool.verify(FRAGMENTS_PATH),
                   file_digests={"l2": file_digest(L2_PATH), "l3": file_digest(L3_PATH), "convention": file_digest(CONVENTION_PATH)},
                   convention_artifact=str(CONVENTION_PATH.relative_to(SPIKE.parent).as_posix()),
                   rule_artifact=str((GRAPH / "rules" / "layout_rule.py").relative_to(SPIKE.parent).as_posix()),
                   rule_digest=file_digest(GRAPH / "rules" / "layout_rule.py"))


def project_founding_inputs(graph_dir=None, *, independent_derivation: bool = False) -> dict:
    """The surface FX-SEAM-A demands of a projector: the four founding inputs, each carrying the same
    projectionInputManifestDigest. Raises Refused until the slice's records are acted on."""
    out = project_real(independent_derivation=independent_derivation)
    return {k: out[k] for k in ("plan", "plannerContract", "builderBrief", "testerContract")}


def write_outputs(outputs: dict, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    names = {"plan": "plan.json", "declared": "declared.json", "plannerContract": "planner-contract.json",
             "builderBrief": "builder-brief.json", "testerContract": "tester-contract.json", "manifest": "projection-input-manifest.json"}
    written = {}
    for key, name in names.items():
        data = canonical(outputs[key])
        (out_dir / name).write_bytes(data)
        written[name] = "sha256:" + hashlib.sha256(data).hexdigest()
    return written


def check_determinism(project_fn) -> tuple[bool, dict]:
    first = {k: canonical(v) for k, v in project_fn().items()}
    second = {k: canonical(v) for k, v in project_fn().items()}
    return first == second, {k: "sha256:" + hashlib.sha256(v).hexdigest() for k, v in first.items()}


# ------------------------------------------------------------------ selftest

def _synthetic():
    """A tiny graph and act ledger that are NOT the slice's. Every id says SYNTHETIC. The acts are by a
    SYNTHETIC operator over synthetic content; the real queue is never read or written here."""
    frag = {"fragmentId": "sf:SYNTHETIC1", "label": "S", "text": "the synthetic sentence", "display": {"lines": "1", "section": "SYN §1"}, "textHash": "sha256:x"}
    l2 = {"@id": "spike:l2:SYNTHETIC", "source": {"digest": "sha256:" + "0" * 64},
          "semanticDependencyManifest": {"normalizationVersion": "norm-spike-1"},
          "records": [
              {"@id": "sr:L2:C-S8", "title": "SYN C-S8", "assertions": [{"@id": "a:C-S8:W-CS8-N", "statement": "syn", "groundedBy": [{"fragment": "sf:SYNTHETIC1", "role": "primary"}]}]},
              {"@id": "sr:L2:Finding", "title": "SYN Finding", "assertions": [{"@id": "a:Finding:fields", "statement": "syn", "fields": [{"name": "id"}, {"name": "text"}], "groundedBy": [{"fragment": "sf:SYNTHETIC1", "role": "primary"}]}]},
              {"@id": "sr:L2:Disposition", "title": "SYN Disposition", "assertions": [{"@id": "a:Disposition:record", "statement": "syn", "fields": [{"name": "finding_id"}, {"name": "kind", "enumeration": ["resolved", "rejected"]}], "groundedBy": [{"fragment": "sf:SYNTHETIC1", "role": "primary"}]}]},
              {"@id": "sr:L2:author-agent", "title": "SYN author-agent", "assertions": [{"@id": "a:author-agent:component", "statement": "syn", "attributes": {"repoHome": ".claude/agents/author"}, "groundedBy": [{"fragment": "sf:SYNTHETIC1", "role": "primary"}]}]},
              {"@id": "sr:L2:S-S4", "title": "SYN S-S4", "assertions": [{"@id": "a:S-S4:seam", "statement": "syn", "groundedBy": [{"fragment": "sf:SYNTHETIC1", "role": "primary"}]}]},
          ]}
    def closure(cid, proposed):
        return {"@id": cid, "@type": "Closure", "proposed": proposed}
    l3 = {"@id": "spike:l3:SYNTHETIC", "records": [
        {"@id": "sr:L3:panel-findings-store-interface", "assertions": [
            closure("c:store:component", {"component": "panel-findings-store"}),
            closure("c:store:appendFinding", {"export": "appendFinding", "signature": "appendFinding(a)"}),
            closure("c:store:getFinding", {"export": "getFinding", "signature": "getFinding(a)"}),
            closure("c:store:listFindings", {"export": "listFindings", "signature": "listFindings(a)"}),
            closure("c:store:FindingInput", {"type": "FindingInput", "definition": "Omit<Finding,'id'>"})]},
        {"@id": "sr:L3:findings-read-seam", "assertions": [closure("c:seam:author-agent-reads-store", {"members": ["listFindings", "getFinding"]})]},
        {"@id": "sr:L3:module-boundaries", "assertions": [
            closure("c:contract:component", {"component": "contract"}),
            closure("c:contract:ProposeRevisionsInput", {"fields": {"proposalId": "string"}}),
            closure("c:contract:ProposeRevisionsResult", {"fields": {"proposalId": "string"}}),
            closure("c:contract:RevisionRefusal", {"fields": {"finding_id": "string"}}),
            closure("c:author-agent:interface", {"export": "proposeRevisions", "signature": "proposeRevisions(i)"}),
            closure("c:deps:edges", {"depends_on": {"contract": [], "panel-findings-store": ["contract"], "author-agent": ["contract", "panel-findings-store"]}}),
            closure("c:realizes", {"realizes": {"contract": ["sr:L2:Finding", "sr:L2:Disposition"], "panel-findings-store": ["sr:L2:S-S4", "sr:L2:Finding"], "author-agent": ["sr:L2:C-S8", "sr:L2:author-agent"]}})]},
        {"@id": CONVENTION_RECORD, "assertions": []},
    ], "adjudications": [{"@id": ADJUDICATION, "options": ["A", "B", "C"]}]}
    convention = {"id": "l3:SYNTHETIC:closure:layout-convention", "layer": "L3", "standalone": True,
                  "expiry": {"kind": "date", "value": "2026-12-31"},
                  "values": {"language": "typescript", "sourceRoot": "src", "modulePathPattern": "{sourceRoot}/{name}.ts",
                             "testFilePattern": "tests/{name}.test.ts", "testDiscipline": "one per module"}}
    convention["closureDigest"] = digest(convention)
    fragments = {"fragments": [frag]}
    queue = []
    n = 0
    for rec in l2["records"] + [r for r in l3["records"] if r["@id"] != CONVENTION_RECORD]:
        n += 1
        queue.append({"id": "SYN-%02d" % n, "record": rec["@id"], "recordDigest": digest(rec), "actedAt": "2026-01-01T00:00:00+00:00", "act": "ratified", "actor": "SYNTHETIC-operator"})
    queue.append({"id": "SYN-conv", "record": CONVENTION_RECORD, "artifact": "SYN-convention", "artifactFileDigest": None, "actedAt": "2026-01-01T00:00:00+00:00", "act": "ratified", "actor": "SYNTHETIC-operator"})
    queue.append({"id": "SYN-adj", "record": ADJUDICATION, "recordDigest": digest(l3["adjudications"][0]), "actedAt": "2026-01-01T00:00:00+00:00", "act": "decided", "decision": "C", "actor": "SYNTHETIC-operator"})
    queue.append({"id": "SYN-rule", "record": "rule:layout-derivation", "artifact": "SYN-rule", "artifactFileDigest": "sha256:SYNTHETIC", "actedAt": "2026-01-01T00:00:00+00:00", "act": "ratified", "actor": "SYNTHETIC-operator"})
    return l2, l3, convention, fragments, queue


def selftest() -> int:
    l2, l3, convention, fragments, queue = _synthetic()
    failures = []

    def check(name, ok, detail=""):
        print("  %s  %s%s" % ("ok  " if ok else "FAIL", name, (" -- " + detail) if detail else ""))
        if not ok:
            failures.append(name)

    def run(q=None, **kw):
        return project(l2, l3, convention, fragments, queue if q is None else q,
                       rule_artifact="SYN-rule", rule_digest="sha256:SYNTHETIC", **kw)
    same, digests = check_determinism(run)
    check("deterministic: two projections, byte-identical outputs", same)
    out = run()
    md = {k: out[k]["projectionInputManifestDigest"] for k in OUTPUT_NAMES}
    check("every founding input carries the same Projection Input Manifest digest", len(set(md.values())) == 1)
    names = {
        "plan": [s["export"] for s in out["plan"]["units"][2]["signatures"]],
        "planner": [e["name"] for e in out["plannerContract"]["interfaces"]["panel-findings-store"]["exports"]],
        "brief": [i["symbol"] for i in out["builderBrief"]["briefs"]["author-agent"]["imports"] if i["module"] == "panel-findings-store"],
        "tester": [c["symbol"] for c in out["testerContract"]["tests"]["author-agent"]["assertsCalls"]],
    }
    check("the read seam's members agree across plan, planner, brief and tester (by construction)",
          set(names["brief"]) == set(names["tester"]) and set(names["brief"]) <= set(names["planner"]) <= set(names["plan"]), str(names))
    check("author-agent's files follow adjudication C (relocating closure, provisional)",
          out["plan"]["units"][0]["id"] == "author-agent"
          and out["plan"]["units"][0]["files"] == ["src/author-agent.ts", "tests/author-agent.test.ts"]
          and bool(out["manifest"]["provisional"]))

    ind = run(independent_derivation=True)
    check("test-assembled independent derivation reintroduces the divergence",
          ind["testerContract"]["tests"]["author-agent"]["assertsCalls"][0]["symbol"] == "unspecified"
          and ind["builderBrief"]["briefs"]["author-agent"]["imports"][0]["symbol"] == "listFindings")

    short = [r for r in queue if r["id"] != "SYN-03"]
    assert short != queue
    try:
        run(short)
    except Refused as r:
        check("refuses when one record has no act, naming it", any("sr:L2:Disposition" in a for a in r.awaiting), str(r.awaiting))
    else:
        check("refuses when one record has no act, naming it", False, "it projected")

    no_rule = [r for r in queue if r["id"] != "SYN-rule"]
    assert no_rule != queue
    try:
        run(no_rule)
    except Refused as r:
        check("refuses when the layout rule itself is not ratified at its content address", any("rule:layout-derivation" in a for a in r.awaiting))
    else:
        check("refuses when the layout rule itself is not ratified at its content address", False, "it projected")

    stale = copy.deepcopy(queue)
    stale[0]["recordDigest"] = "sha256:" + "f" * 64
    try:
        run(stale)
    except Refused as r:
        check("an act at a stale content address does not confer (D23)", any("different content address" in a for a in r.awaiting))
    else:
        check("an act at a stale content address does not confer (D23)", False)

    voided = copy.deepcopy(queue)
    voided[1]["actor"] = "dev-agent"
    try:
        run(voided)
    except Refused as r:
        check("an act by the agent voids the projection outright", "void" in str(r))
    else:
        check("an act by the agent voids the projection outright", False)

    try:
        run(verify_fragments=lambda: ["sf:SYNTHETIC1"])
    except Refused as r:
        check("lapsed grounding refuses (ARO 5.2)", "lapsed" in str(r))
    else:
        check("lapsed grounding refuses (ARO 5.2)", False)

    undecided = copy.deepcopy(queue)
    undecided[[r["id"] for r in undecided].index("SYN-adj")]["decision"] = "B"
    try:
        run(undecided)
    except Refused as r:
        check("adjudication B waits on the source amendment", "source amendment" in str(r))
    else:
        check("adjudication B waits on the source amendment", False)

    print()
    print("  compiler digest %s" % file_digest(Path(__file__)))
    print("  %d check(s) failed" % len(failures) if failures else "  all checks passed")
    return 1 if failures else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true", help="project the real slice twice and require byte identity")
    ap.add_argument("-o", "--out", help="write the real slice's projections here")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if args.check or not args.out:
            same, digests = check_determinism(project_real)
            print("Projected: %s" % ("byte-identical on re-projection" if same else "NOT deterministic"))
            for k, v in digests.items():
                print("  %-16s %s" % (k, v))
            if not same:
                return 1
        if args.out:
            written = write_outputs(project_real(), Path(args.out))
            for name, d in written.items():
                print("  %-32s %s" % (name, d))
        return 0
    except Refused as r:
        print("REFUSED: %s" % r, file=sys.stderr)
        for a in r.awaiting:
            print("  awaiting  %s" % a, file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
