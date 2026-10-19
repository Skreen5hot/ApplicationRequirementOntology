"""The WS-3 projector -- from the accepted L2 graph and the ratified L3 design to a buildable, provenance-carrying
package (IA plan D-8 part 2b; DEV-2026-10-01-d8-part2-design.md, as answered by Ops). Separate from the slice's
projector, whose bytes stay identical; it reuses only that projector's act rule (`act_for`).

WHAT IT EMITS, and nothing it emits is written here -- every value is read from an acted record:
  - plan.json: four units, `capabilities` and `oracles` (the first projection where both are non-empty), the
    departures from the L2 repo homes the architect decided, the known limits (open non-blocking diagnostics), and the
    provisional demonstration control;
  - the standards bundle oracles/<spec-12>/ -- the ratified module bars and standards.json, each entry's
    `ratified_by` "<actor> via <rq-id> (<act digest>)" with a structured `actRef` beside it (Ops, Q1);
  - the acceptance tests the oracle descriptors name (test/acceptance/<capability>.test.mjs);
  - the NON-BUILT channel: the .githooks/ wrapper and its script, digest-pinned, NEVER in plan.json files
    (rq-035 = A, condition 2), each with the act that ratified it;
  - projection-input-manifest.json, whose digest every JSON output carries.

WHAT IT REFUSES. Any L2 record, L3 record, adjudication or WS3-5 file that a named human has not acted on at its
current content address (D23); an adjudication without a decision; an open BLOCKING diagnostic; adj:ws3-module-homes
decided C (awaiting a source amendment); lapsed grounding; and a ratified bar, oracle or hook that imports a path
which is not its unit's planned file -- under adj:ws3-module-homes = B the bars must be rewritten first, and this is
what says so. Refusal lists everything it waits on.

    python spike/projections/ws3/project.py --check     # project twice, require byte identity; rc 3 while refused
    python spike/projections/ws3/project.py -o spike/projections/ws3/out
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import posixpath
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GRAPH = ROOT / "spike" / "graph"
L2_PATH = GRAPH / "l2" / "srs-ws3.graph.jsonld"
L3_PATH = GRAPH / "l3" / "srs-ws3.design.candidates.jsonld"
FRAGMENTS_PATH = GRAPH / "ws3" / "fragments.json"
QUEUE_PATH = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
COMPILER = {"component": "spike.projector.ws3", "version": "0.1-draft"}

sys.path.insert(0, str(GRAPH / "ws3"))
import build_l2  # noqa: E402  -- derive_status: a diagnostic's status is derived from acts, never read as a literal
from queue_l2 import digest  # noqa: E402  -- the one canonical record digest every WS-3 row is bound with
from queue_bars import ITEMS  # noqa: E402  -- the WS3-5 files: bars, oracles, the non-built hook


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


slice_projector = _load("spike_slice_projector", ROOT / "spike" / "projections" / "project.py")
act_for, Refused = slice_projector.act_for, slice_projector.Refused

# Which ratified L3 record carries each module's interface. Record NAMES, not values: every value is read from them.
MODULE_RECORD = {"grading-types": "sr:L3:ws3-field-types", "grader-runner": "sr:L3:grader-runner-interface",
                 "adjudicator": "sr:L3:adjudicator-interface", "ledger": "sr:L3:ledger-interface"}
BOUNDARIES = "sr:L3:ws3-module-boundaries"
HOMES = "adj:ws3-module-homes"
HOOKS = "adj:ledger-hooks-repo-home"
# rq-035 = A, condition (1): "the verifier code at src/ledger.ts is a recorded deviation from the S5 home". Checked
# against the act's own note below, so a different decision or note refuses instead of projecting this literal.
LEDGER_FILE = "src/ledger.ts"
BAR_DIR, ACCEPTANCE_DIR = "test", "test/acceptance"     # where the factory runs a bar and an oracle (loopToolchain)


def file_digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def ratified_by(row) -> str:
    return "%s via %s (%s)" % (row["actor"], row["id"], row["actDigest"])


def act_ref(row) -> dict:
    return {"queueRow": row["id"], "act": row["act"], "actor": row["actor"], "actedAt": row["actedAt"],
            "actDigest": row["actDigest"], "bound": row.get("recordDigest") or row.get("artifactFileDigest")}


# ------------------------------------------------------------------------------------------------- eligibility

def eligibility(l2, l3, queue_rows, files):
    """Every act the projection rests on -> ({key: row}, [awaiting]). Never raises for a missing act: the refusal
    lists them all at once, so the operator sees the whole remaining batch."""
    acts, awaiting = {}, []

    def need(key, current, artifact=None):
        row, why = act_for(queue_rows, key, current, artifact)
        if row:
            acts[key] = row
        else:
            awaiting.append(why)

    for rec in l2["records"]:
        need(rec["@id"], digest(rec))
    for rec in l3["records"]:
        need(rec["@id"], digest(rec))
    for adj in l3["adjudications"]:
        need(adj["@id"], digest(adj))
        if adj["@id"] in acts and not acts[adj["@id"]].get("decision"):
            awaiting.append("%s: acted on without a recorded decision" % adj["@id"])
            del acts[adj["@id"]]
    for item in ITEMS:
        need(item["file"], file_digest(files[item["file"]]), item["file"])
    return acts, awaiting


def blocking_open(l2, queue_rows):
    by_id = {r["id"]: r for r in queue_rows}
    derived = [build_l2.derive_status(d, by_id) for d in build_l2.DIAGNOSTICS]
    return ([d for d in derived if d["status"] == "open" and d.get("blocking")],
            [d for d in derived if d["status"] == "open" and not d.get("blocking")])


# ------------------------------------------------------------------------------------------------- composing

def _closures(rec):
    return {a["@id"]: a["proposed"] for a in rec["assertions"]}


def _imports(text, test_dir):
    """The repository paths a test file imports, resolved from where the factory runs it."""
    rel = re.findall(r"""from\s+['"](\.\.?/[^'"]+)['"]""", text)
    joined = [posixpath.normpath(posixpath.join(test_dir, p)) for p in rel]
    joined += ["/".join(parts) for parts in
               (re.findall(r"'([^']+)'", m) for m in re.findall(r"join\(top,\s*([^)]*)\)", text))]
    return sorted(set(joined))


def project(l2, l3, fragments, queue_rows, files, *, verify_fragments=None, input_digests=None):
    frags = {f["fragmentId"]: f for f in fragments["fragments"]}
    cited = {g["fragment"] for rec in l2["records"] for a in rec["assertions"] for g in a.get("groundedBy", [])}
    if cited - set(frags):
        raise Refused("L2 cites fragments that do not exist: %s" % sorted(cited - set(frags)))
    lapsed = verify_fragments() if verify_fragments else []
    if lapsed:
        # A lapse is a refusal like any other and must be as legible: it names what it awaits, so a runner that
        # cannot read the source (the GitHub Actions class, 2026-10-01..18) prints an `awaiting:` line rather than
        # a bare REFUSED (test_the_live_check_refuses_legibly_or_projects_never_crashes).
        raise Refused("grounding lapsed (ARO 5.2): %s" % lapsed,
                      ["a readable copy of the registered source at its pinned digest (%s) -- the registered path "
                       "under sources/srs/, or an ARO_SOURCE_DOC_<8 hex> override; lapsed: %s"
                       % (fragments["source"].get("digest"), "; ".join(lapsed))])

    acts, awaiting = eligibility(l2, l3, queue_rows, files)
    blocking, known_limits = blocking_open(l2, queue_rows)
    awaiting += ["%s is OPEN and BLOCKING" % d["@id"] for d in blocking]
    if awaiting:
        raise Refused("WS-3 projection refused: %d item(s) are not eligible" % len(awaiting), awaiting)

    records = {r["@id"]: r for r in l3["records"]}
    adjs = {a["@id"]: a for a in l3["adjudications"]}
    bound = _closures(records[BOUNDARIES])
    edges = bound["c:ws3:deps:edges"]["depends_on"]
    realizes, paths = bound["c:ws3:realizes"]["realizes"], bound["c:ws3:realizes"]["capabilityPaths"]
    if set(edges) != set(MODULE_RECORD):
        raise Refused("the ratified module set %s is not the projector's %s" % (sorted(edges), sorted(MODULE_RECORD)))

    # FILES -- from decided adjudications only.
    homes = acts[HOMES]["decision"]
    if homes == "C":
        raise Refused("%s decided C: awaiting the source amendment; no module file can be projected" % HOMES,
                      ["source amendment of SRS s5 (rq %s)" % acts[HOMES]["id"]])
    chosen = next((o for o in adjs[HOMES]["options"] if o["id"] == homes), None)
    if not chosen or not chosen.get("files"):
        raise Refused("%s decided %r, which is not an option that fixes files" % (HOMES, homes))
    hooks = acts[HOOKS]
    if hooks.get("decision") != "A" or LEDGER_FILE not in (hooks.get("actNote") or ""):
        raise Refused("%s (%s) does not place the ledger at %s; the ledger's file cannot be projected"
                      % (HOOKS, hooks["id"], LEDGER_FILE))
    files_of = dict(chosen["files"], ledger=LEDGER_FILE)
    if set(files_of) != set(MODULE_RECORD):
        raise Refused("the decided files cover %s, not every module" % sorted(files_of))

    # a ratified test must import the files the plan builds, or it would grade a module that does not exist
    unit_of = {item["file"]: item for item in ITEMS}
    mismatched = []
    for path, item in unit_of.items():
        text = files[path].decode("utf-8")
        if item["kind"] == "module bar":
            want = [files_of[item["unit"]]]
            got = [p for p in _imports(text, BAR_DIR) if not p.startswith("node:")]
        elif item["kind"] == "capability oracle":
            want = sorted(files_of[m] for m in realizes[item["capability"]])
            got = [p for p in _imports(text, ACCEPTANCE_DIR) if not p.startswith("node:")]
        elif item["kind"] == "non-built delivery descriptor":
            continue                                       # a record about files, not code: checked below
        else:   # non-built: the wrapper runs the script and imports nothing; whatever .ts the script loads must be built
            got = [p for p in _imports(text, ".") if p.endswith(".ts")]
            want = [p for p in got if p in files_of.values()]
        if sorted(got) != sorted(want):
            mismatched.append("%s imports %s; the plan builds %s" % (path, sorted(got), sorted(want)))
    if mismatched:
        raise Refused("ratified test(s) import paths the plan does not build (rewrite and re-ratify them)", mismatched)

    # UNITS -- each module's scope is its L3 record's closures over the L2 assertions that record depends on.
    l2_assertions = {a["@id"]: a for rec in l2["records"] for a in rec["assertions"]}

    def scope(module):
        rec = records[MODULE_RECORD[module]]
        lines = ["Module %s." % module, "", "REALIZES (L2, source semantics):"]
        for aid in rec["dependsOn"]:
            a = l2_assertions[aid]
            lines.append("  [%s] %s" % (aid, a["statement"]))
            for g in a.get("groundedBy", []):
                f = frags[g["fragment"]]
                lines.append("    grounded (%s) in %s, line %s: %s" % (g["role"], f["fragmentId"], f["display"]["lines"], f["text"]))
        lines += ["", "CLOSURES (L3, ratified design; not source semantics):"]
        for cid, val in sorted(_closures(rec).items()):
            lines.append("  [%s] %s" % (cid, json.dumps(val, sort_keys=True, ensure_ascii=False)))
        if module == "grading-types":
            lines.append("  [c:ws3:grading-types] %s" % json.dumps(bound["c:ws3:grading-types"], sort_keys=True, ensure_ascii=False))
        return "\n".join(lines)

    def covers(module):
        return sorted({frags[g["fragment"]]["display"]["section"]
                       for aid in records[MODULE_RECORD[module]]["dependsOn"]
                       for g in l2_assertions[aid].get("groundedBy", [])
                       if frags[g["fragment"]]["display"].get("section")})

    def signatures(module):
        out = []
        for cid, val in sorted(_closures(records[MODULE_RECORD[module]]).items()):
            for s in ([val["signature"]] if val.get("signature") else []) + list(val.get("signatures") or []) + list(val.get("alsoExports") or []):
                out.append({"signature": s, "closure": cid, "record": MODULE_RECORD[module]})
        return out

    units = [{"id": m, "files": [files_of[m]], "covers": covers(m), "kind": "code", "depends_on": sorted(edges[m]),
              "scope": scope(m), "signatures": signatures(m)} for m in sorted(edges)]

    # DEPARTURES -- computed from the accepted homes and the decided files, never asserted.
    departures = []
    for m in sorted(edges):
        a = l2_assertions.get("a:%s:component" % m)
        if not a:
            continue
        home = a["attributes"]["repoHome"]
        homes_list = home if isinstance(home, list) else [home]
        if not any(files_of[m].startswith(h) for h in homes_list):
            by = acts[HOOKS] if m == "ledger" else acts[HOMES]
            departures.append({"module": m, "l2RepoHome": homes_list, "file": files_of[m], "assertion": a["@id"],
                               "decidedBy": "%s (%s, decision %s)" % (by["id"], by["record"], by["decision"])})

    # BARS, ORACLES, NON-BUILT -- each carries the act that ratified its exact bytes.
    spec12 = l2["source"]["digest"].split(":")[-1][:12]
    std_dir = "oracles/%s" % spec12
    standards, oracles, nonbuilt, out_files = [], [], [], {}
    # THE DELIVERY DESCRIPTOR (rq-071, 2026-10-18): a file digest binds bytes, not mode or install path, so every
    # non-built file is delivered only as the acted descriptor states it -- and the descriptor must name each file at
    # the very bytes its own act bound.
    desc_item = next(i for i in ITEMS if i["kind"] == "non-built delivery descriptor")
    delivery = json.loads(files[desc_item["file"]].decode("utf-8"))
    by_source = {d["source"]: d for d in delivery["deliverables"]}
    hook_items = [i for i in ITEMS if i["kind"] == "non-built deliverable"]
    stale = ["%s: the descriptor says %s, the acted file is %s" % (i["file"], (by_source.get(i["file"]) or {}).get("sha256"),
                                                                  file_digest(files[i["file"]]))
             for i in hook_items if (by_source.get(i["file"]) or {}).get("sha256") != file_digest(files[i["file"]])]
    if stale or set(by_source) != {i["file"] for i in hook_items}:
        raise Refused("the non-built delivery descriptor does not describe the acted hook files", stale or sorted(by_source))
    # rq-081 (2026-10-19): the C-S7 oracle is BOUND to the ratified non-built set by the digests it pins; each pin must
    # be the acted bytes of the wrapper, the script and the descriptor, or the oracle would vouch for a different set.
    c_s7 = next(i for i in ITEMS if i["kind"] == "capability oracle" and i["capability"] == "C-S7")
    pins = dict(re.findall(r"const PINNED_(WRAPPER|SCRIPT|DELIVERY) = '(sha256:[0-9a-f]{64})'", files[c_s7["file"]].decode("utf-8")))
    wanted = {"WRAPPER": next(i["file"] for i in hook_items if i["file"].endswith("/pre-commit")),
              "SCRIPT": next(i["file"] for i in hook_items if i["file"].endswith("/check-ledger.mjs")),
              "DELIVERY": desc_item["file"]}
    unpinned = ["%s pins %s = %s; the acted file is %s" % (c_s7["file"], k, pins.get(k), file_digest(files[f]))
                for k, f in sorted(wanted.items()) if pins.get(k) != file_digest(files[f])]
    if unpinned:
        raise Refused("the C-S7 oracle is not bound to the acted non-built delivery set", unpinned)
    for item in ITEMS:
        row, data = acts[item["file"]], files[item["file"]]
        name = item["file"].rsplit("/", 1)[-1]
        if item["kind"] == "module bar":
            standards.append({"module": item["unit"], "lang": "js", "source": "spec", "provisional": False,
                              "ratified_by": ratified_by(row), "actRef": act_ref(row), "sha256": file_digest(data)})
            out_files["%s/%s" % (std_dir, name)] = data
        elif item["kind"] == "capability oracle":
            cap = item["capability"]
            oracles.append({"capability": cap, "path": paths[cap], "acceptance_test": "%s/%s" % (ACCEPTANCE_DIR, name),
                            "ratified_by": ratified_by(row), "ratified_at": row["actedAt"], "actRef": act_ref(row),
                            "sha256": file_digest(data)})
            out_files["%s/%s" % (ACCEPTANCE_DIR, name)] = data
        elif item["kind"] == "non-built deliverable":
            d = by_source[item["file"]]
            drow = acts[desc_item["file"]]
            nonbuilt.append({"path": d["installAt"], "sha256": file_digest(data), "mode": d["mode"],
                             "ratified_by": ratified_by(row), "actRef": act_ref(row),
                             "deliveryRatifiedBy": ratified_by(drow), "deliveryActRef": act_ref(drow),
                             "placement": "placed by Ops in the build workspace before the C-S7 oracle runs (%s, condition 2)" % acts[HOOKS]["id"]})
            out_files["nonbuilt/%s" % d["installAt"]] = data
    planned = {f for u in units for f in u["files"]}
    if planned & {n["path"] for n in nonbuilt}:
        raise Refused("a non-built deliverable is in plan.json files (%s, condition 2)" % acts[HOOKS]["id"])

    control = l2["ws3"]["demonstrationControlCandidate"]
    covered = {s["module"] for s in standards} | {m for o in oracles for m in realizes[o["capability"]]}
    provisional = ["%s (%s): no ratified bar or oracle -- %s; %s" % (control["capability"], paths[control["capability"]],
                                                                     control["why"], control["status"])]
    if any(m in covered for m in realizes[control["capability"]]):
        raise Refused("the demonstration control %s has a ratified bar or oracle" % control["capability"])

    manifest = {
        "l2": {"graphDigest": (input_digests or {}).get("l2") or digest(l2),
               "acceptanceHead": {"specDigest": l2["source"]["digest"], "registeredAs": l2["source"].get("registeredAs"),
                                  "head": sorted(acts[r["@id"]]["id"] for r in l2["records"])}},
        "l3": {"designGraphDigest": (input_digests or {}).get("l3") or digest(l3),
               "ratificationHead": sorted(acts[r["@id"]]["id"] for r in l3["records"]),
               "adjudications": [{"adjudication": a["@id"], "decision": acts[a["@id"]]["decision"], "act": acts[a["@id"]]["id"]}
                                 for a in l3["adjudications"]]},
        "files": [{"artifact": i["file"], "kind": i["kind"], "sha256": file_digest(files[i["file"]]), "act": acts[i["file"]]["id"]}
                  for i in ITEMS],
        "fragmentsDigest": (input_digests or {}).get("fragments") or digest(fragments),
        "compiler": dict(COMPILER, digest=(input_digests or {}).get("compiler") or "unpinned"),
        "standardsKey": {"dir": std_dir, "rule": "the first 12 hex of the registered source digest; equals the factory's "
                         "standards.spec_digest(spec text) because the registered source has no CR and no BOM"},
    }
    md = "sha256:" + hashlib.sha256(canonical(manifest)).hexdigest()
    plan = {"units": units,
            "capabilities": [{"capability": c, "path": paths[c], "modules": sorted(realizes[c])} for c in sorted(realizes)],
            "oracles": sorted(oracles, key=lambda o: o["capability"]),
            "departures": departures,
            "knownLimits": [{"diagnostic": d["@id"], "statement": d["statement"]} for d in known_limits],
            "provisional": provisional,
            "nonBuilt": "nonbuilt/manifest.json -- never in any unit's files",
            "projectionInputManifestDigest": md}
    out = {"plan.json": canonical(plan),
           "projection-input-manifest.json": canonical(manifest),
           "%s/standards.json" % std_dir: canonical({"schema": "coord-standards/1",
                                                      "standards": sorted(standards, key=lambda s: s["module"]),
                                                      "projectionInputManifestDigest": md}),
           "nonbuilt/manifest.json": canonical({"deliverables": nonbuilt,
                                                "repositoryRequirement": delivery["repositoryRequirement"],
                                                "failClosed": delivery["failClosed"],
                                                "projectionInputManifestDigest": md})}
    out.update(out_files)
    return out


# ------------------------------------------------------------------------------------------------- surfaces

def load_real():
    l2 = json.loads(L2_PATH.read_text(encoding="utf-8"))
    l3 = json.loads(L3_PATH.read_text(encoding="utf-8"))
    fragments = json.loads(FRAGMENTS_PATH.read_text(encoding="utf-8"))
    rows = [json.loads(l) for l in QUEUE_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
    files = {i["file"]: (ROOT / i["file"]).read_bytes() for i in ITEMS}
    return l2, l3, fragments, rows, files


def project_real():
    l2, l3, fragments, rows, files = load_real()
    return project(l2, l3, fragments, rows, files,
                   verify_fragments=_verify,
                   input_digests={"l2": file_digest(L2_PATH.read_bytes()), "l3": file_digest(L3_PATH.read_bytes()),
                                  "fragments": file_digest(FRAGMENTS_PATH.read_bytes()),
                                  "compiler": file_digest(Path(__file__).read_bytes())})


def _verify():
    sys.path.insert(0, str(GRAPH))
    import fragments as F
    return F.verify(FRAGMENTS_PATH)


def write(outputs, out_dir: Path):
    for name, data in sorted(outputs.items()):
        p = out_dir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return {name: file_digest(data) for name, data in sorted(outputs.items())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)
    try:
        first = project_real()
        if args.check:
            second = project_real()
            if first != second:
                print("NOT DETERMINISTIC: two projections differ in %s" % sorted(k for k in first if first[k] != second.get(k)))
                return 1
    except Refused as e:
        print("REFUSED: %s" % e)
        for w in e.awaiting:
            print("  awaiting: %s" % w)
        return 3
    if args.out:
        digests = write(first, Path(args.out))
    else:
        digests = {k: file_digest(v) for k, v in sorted(first.items())}
    for name, d in digests.items():
        print("  %-48s %s" % (name, d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
