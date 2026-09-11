"""Layout derivation rule -- DRAFT v0.1, a spike artifact (ARO v0.5.2 sections 11.3 and 5.6).

THE PATTERN. plan.json's `unit["files"]` encodes language and repository layout, which
N1 (ARO 4.2) forbids a transformer to infer and no source states. ARO 11.3 supplies them
through exactly two ratified things: one per-project CONVENTION CLOSURE (L3, standalone,
expiring) and one profile-level LAYOUT DERIVATION RULE -- this file -- that derives each
module's files from the component prescriptions (L2) crossed with the convention (L3).
Each derived assertion is an L3-resident mixed-premise derivation (ARO 5.6): it retains
its premise ids and digests, so when either premise lapses the derivation lapses with it,
mechanically.

WHAT THIS DRAFT IS AND IS NOT. It is the rule's mechanics -- deterministic, content-
addressed, premise-retaining, refusing when its precondition is unmet -- exercised on a
SYNTHETIC component set by `--selftest`. It is not a rule over the RLA: the RLA
specification is not on this machine (spike/graph/source-register.json), so no L2
component prescriptions exist to derive from, and the convention closure candidate
beside it carries no authored values. Running this rule over that candidate REFUSES, and
that refusal is the honest current state of the pattern. The input shape (`components`,
`convention`) is spike-defined at minimum viable fidelity; the RLA profile (Phase 3) owns
the real one.

AUTHORITY IS COMPUTED, NEVER STORED (ARO 3.1). The output carries premises and their
facets; it does not carry an authority verdict. A consumer computes eligibility from the
premises' ratification state and the rule's own.

    python spike/graph/rules/layout_rule.py --selftest
    python spike/graph/rules/layout_rule.py --components C.json --convention K.json [-o OUT]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

RULE_REF = "rule:aro-rla:layout-derivation"
RULE_VERSION = "0.1-draft"
#: The convention values the rule reads. All must be authored (non-null) or the rule refuses.
CONVENTION_VALUES = ("language", "sourceRoot", "modulePathPattern", "testFilePattern",
                     "testDiscipline")
#: The placeholders the two path patterns may use.
PLACEHOLDERS = ("{sourceRoot}", "{name}")


class Refused(Exception):
    """The rule's precondition is unmet. Named, so a refusal reads as one."""


def canonical(obj) -> bytes:
    """One canonical serialisation for digesting and for output: sorted keys, no
    insignificant whitespace, a trailing newline, UTF-8."""
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def digest(obj) -> str:
    return "sha256:" + hashlib.sha256(canonical(obj)).hexdigest()


def rule_digest() -> str:
    """The rule is content-addressed by its own source bytes (ARO 9: versioned,
    content-addressed, scope-bounded)."""
    return "sha256:" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _check_convention(convention: dict) -> None:
    if not isinstance(convention, dict):
        raise Refused("the convention is not an object")
    if convention.get("layer") != "L3":
        raise Refused("the convention must be an L3 closure; it declares layer=%r"
                      % convention.get("layer"))
    if "groundedBy" in convention:
        raise Refused("an L3 closure may not carry groundedBy (ARO D17); rationaleSource "
                      "is the permitted citation")
    if convention.get("standalone") is not True:
        raise Refused("a layout convention closes no identifiable L2 underdetermination and "
                      "must carry the operator-attested standalone marker (ARO 5.6)")
    expiry = convention.get("expiry") or {}
    if not expiry.get("value"):
        raise Refused("a standalone closure without an explicit expiry is immortal, which "
                      "ARO 5.6 forbids; none is set (GP-D has no initial value in ARO 16 -- "
                      "the operator sets one)")
    if not convention.get("id") or not convention.get("closureDigest"):
        raise Refused("the convention must carry an id and its content address "
                      "(closureDigest), because derived assertions retain them as premises")
    values = convention.get("values") or {}
    unauthored = [k for k in CONVENTION_VALUES if values.get(k) in (None, "")]
    if unauthored:
        raise Refused("unauthored convention values %s: a closure with unauthored values is "
                      "a form, not a closure, and confers nothing (the dev agent proposes, "
                      "the operator authors -- ARO D20)" % unauthored)
    for key in ("modulePathPattern", "testFilePattern"):
        pattern = values[key]
        leftover = pattern
        for placeholder in PLACEHOLDERS:
            leftover = leftover.replace(placeholder, "")
        if "{" in leftover or "}" in leftover:
            raise Refused("%s %r uses a placeholder outside %s" % (key, pattern, PLACEHOLDERS))


def _check_components(components: list) -> None:
    if not isinstance(components, list) or not components:
        raise Refused("no component prescriptions: the rule derives from L2 components and "
                      "there are none (nothing to derive is not the same as deriving nothing)")
    seen = set()
    for c in components:
        for k in ("id", "name", "assertionDigest"):
            if not (isinstance(c, dict) and c.get(k)):
                raise Refused("component %r lacks %r" % (c, k))
        # A component may be an L2 prescription (the source names it) or an L3 closure (the
        # operator drew the boundary because the source did not). Either way the derivation is
        # L3-resident and the premise records its own layer, so a lapse propagates correctly.
        if c.get("layer", "L2") not in ("L2", "L3"):
            raise Refused("component %s has layer %r; L2 (prescribed) or L3 (closed) are the "
                          "two kinds of premise this rule accepts" % (c["id"], c.get("layer")))
        if c["name"] in seen:
            raise Refused("two components prescribe the module name %r; the layout would "
                          "collide" % c["name"])
        seen.add(c["name"])


def derive(components: list, convention: dict) -> dict:
    """(L2 component prescriptions x L3 convention) -> the per-module `files` derivations."""
    _check_convention(convention)
    _check_components(components)
    values = convention["values"]

    def fill(pattern: str, name: str) -> str:
        return pattern.replace("{sourceRoot}", values["sourceRoot"]).replace("{name}", name)

    derivations = []
    for c in sorted(components, key=lambda c: c["name"]):       # sorted: never input order
        entry = {
            "moduleId": c["name"],
            "files": [fill(values["modulePathPattern"], c["name"]),
                      fill(values["testFilePattern"], c["name"])],
            "language": values["language"],
            "layer": "L3",
            "kind": "mixed-premise-derivation",
            "premises": [
                {"id": c["id"], "layer": c.get("layer", "L2"), "digest": c["assertionDigest"]},
                {"id": convention["id"], "layer": "L3", "digest": convention["closureDigest"]},
            ],
            "rule": {"ref": RULE_REF, "version": RULE_VERSION},
        }
        entry["derivedDigest"] = digest(entry)
        derivations.append(entry)

    out = {
        "rule": {"ref": RULE_REF, "version": RULE_VERSION, "digest": rule_digest()},
        "convention": {"id": convention["id"], "digest": convention["closureDigest"]},
        "derivations": derivations,
    }
    out["outputDigest"] = digest(out)
    return out


# ------------------------------------------------------------------ selftest

def _synthetic():
    """A component set and convention that are NOT the RLA's. Labeled so in every id."""
    components = [
        {"id": "l2:SYNTHETIC:component:parser", "layer": "L2", "name": "parser",
         "assertionDigest": "sha256:" + "1" * 64},
        {"id": "l2:SYNTHETIC:component:analyzer", "layer": "L2", "name": "analyzer",
         "assertionDigest": "sha256:" + "2" * 64},
        {"id": "l2:SYNTHETIC:component:contract", "layer": "L2", "name": "contract",
         "assertionDigest": "sha256:" + "3" * 64},
    ]
    convention = {
        "id": "l3:SYNTHETIC:closure:layout-convention", "layer": "L3", "standalone": True,
        "expiry": {"kind": "date", "value": "2026-12-31"},
        "values": {"language": "typescript", "sourceRoot": "src",
                   "modulePathPattern": "{sourceRoot}/{name}.ts",
                   "testFilePattern": "tests/{name}.test.ts",
                   "testDiscipline": "one test file per module, named after it"},
    }
    convention["closureDigest"] = digest(convention)
    return components, convention


def selftest() -> int:
    import copy

    components, convention = _synthetic()
    failures = []

    def check(name, ok, detail=""):
        print("  %s  %s%s" % ("ok  " if ok else "FAIL", name, (" -- " + detail) if detail else ""))
        if not ok:
            failures.append(name)

    first = canonical(derive(components, convention))
    second = canonical(derive(list(reversed(components)), convention))
    check("deterministic: two runs, reversed input order, byte-identical output", first == second)

    base = derive(components, convention)
    mutated = copy.deepcopy(components)
    mutated[0]["assertionDigest"] = "sha256:" + "f" * 64
    assert mutated != components, "the mutation did not apply"      # PROCESS.md 2: assert it
    after = derive(mutated, convention)
    changed = [d["moduleId"] for d, e in zip(base["derivations"], after["derivations"])
               if d["derivedDigest"] != e["derivedDigest"]]
    check("a premise change reaches exactly its own derivation (lapse cone)",
          changed == ["parser"], str(changed))
    check("every derivation retains both premise ids and digests",
          all(len(d["premises"]) == 2 and all(p["digest"] for p in d["premises"])
              for d in base["derivations"]))
    check("no authority is stored in the output",
          not any("authority" in d or "eligible" in d for d in base["derivations"]))

    def refuses(name, mutate):
        k = copy.deepcopy(convention)
        mutate(k)
        assert k != convention, "the mutation did not apply: " + name
        try:
            derive(components, k)
        except Refused as r:
            check("refuses: " + name, True, str(r)[:70])
        else:
            check("refuses: " + name, False, "it derived instead")

    def unauthor(k):
        k["values"]["language"] = None

    def no_expiry(k):
        k["expiry"] = {"kind": "date", "value": None}

    def not_standalone(k):
        k["standalone"] = False

    def grounded(k):
        k["groundedBy"] = ["sf:x"]

    refuses("an unauthored convention value", unauthor)
    refuses("a standalone closure without expiry", no_expiry)
    refuses("a convention missing the standalone marker", not_standalone)
    refuses("a closure claiming groundedBy", grounded)

    try:
        derive([], convention)
    except Refused:
        check("refuses: an empty component set", True)
    else:
        check("refuses: an empty component set", False)

    closed = copy.deepcopy(components)
    closed[0]["layer"] = "L3"
    closed[0]["id"] = "l3:SYNTHETIC:closure:component:parser"
    assert closed != components, "the mutation did not apply"
    mixed = derive(closed, convention)
    parser_entry = [d for d in mixed["derivations"] if d["moduleId"] == "parser"][0]
    check("an L3 component closure derives, and its premise records layer L3",
          parser_entry["premises"][0]["layer"] == "L3" and parser_entry["layer"] == "L3")
    try:
        derive([dict(components[0], layer="L4")], convention)
    except Refused:
        check("refuses: a component from any other layer", True)
    else:
        check("refuses: a component from any other layer", False)

    print()
    print("  rule digest %s" % rule_digest())
    print("  %d check(s) failed" % len(failures) if failures else "  all checks passed")
    return 1 if failures else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--components")
    ap.add_argument("--convention")
    ap.add_argument("-o", "--out")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not (args.components and args.convention):
        ap.error("--components and --convention are required unless --selftest")
    components = json.loads(Path(args.components).read_text(encoding="utf-8"))
    convention = json.loads(Path(args.convention).read_text(encoding="utf-8"))
    try:
        out = derive(components, convention)
    except Refused as r:
        print("REFUSED: %s" % r, file=sys.stderr)
        return 2
    data = canonical(out)
    if args.out:
        Path(args.out).write_bytes(data)
    else:
        sys.stdout.write(data.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
