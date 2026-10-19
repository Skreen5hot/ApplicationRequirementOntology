"""The two FX-CAP assertions as EXECUTABLE checks (Plan v1.1 s3, checklist 11.2: "both FX-CAP assertions stated as
executable checks against the extension's output"). Reads only: the OPS ledger-reading extension's output, the WS-3
projection (plan.json, standards.json) and the ratification queue -- never the factory's own capability_status
(self-attestation is forbidden, PF-OPS-3).

  (i)  the demonstration CONTROL capability reads built_unverified -- never VERIFIED -- and it must be PRESENT in the
       output (an absent control would pass over an empty domain: the FX-VAC class);
  (ii) every ratified-bar capability reads VERIFIED with its barProvenance chain intact from queue act to verdict: each
       of its modules carries a non-provisional bar whose actRef names a live, RATIFIED queue row whose act bound
       exactly the bar's bytes, and that act is the one the projection's standards.json cites.

ASSUMED INPUT SHAPE (to be reconciled with the extension's committed format before freeze 2 -- the factory's own
verdict shape, which the extension reads from the ledger rather than trusts):
    {"capabilities": {"<cap>": {"status": "VERIFIED" | "built_unverified" | ...,
                                "barProvenance": [{"module", "provisional", "source", "ratified_by", "actRef"?}]}}}

RECONCILED 2026-10-19 to the extension's EMITTED shape (IA experiments/ops/ledger_reader.py, ops-ledger-reader-1,
calibration record OPS-2026-10-19-b1-ledger-reader-calibration-record.md): capability status is VERIFIED | BLOCKED, and
each module's derived state is in `derived` (verified | built_unverified | authority_not_demonstrated | stub |
inherited_debt | absent). So "the control reads built_unverified -- never VERIFIED" is: status BLOCKED, and every control
module derived built_unverified (the oracle gap) -- not a stub, not inherited debt, not a provenance failure, not absent,
any of which would mean the control failed for a reason other than its held bar.

    check(extension_output, plan, standards, queue_rows, control) -> [failure]   # [] means both assertions hold
"""
from __future__ import annotations

RATIFYING = {"accepted", "ratified", "decided"}


def check(extension_output: dict, plan: dict, standards: dict, queue_rows: list, control: dict) -> list:
    caps = (extension_output or {}).get("capabilities") or {}
    out = []
    # (i) the control: present, and never VERIFIED
    c = control["capability"]
    if c not in caps:
        out.append("(i) the control %s is absent from the extension's output -- an empty domain proves nothing" % c)
    else:
        status = caps[c].get("status")
        if status == "VERIFIED":
            out.append("(i) the control %s reads VERIFIED; a provisional-bar capability must never verify" % c)
        derived = caps[c].get("derived") or {}
        for m in control["modules"]:
            if derived.get(m) != "built_unverified":
                out.append("(i) the control %s: module %s derives %r, not built_unverified (its held bar is not "
                           "what blocks it)" % (c, m, derived.get(m)))
        if any(b.get("provisional") is False for b in caps[c].get("barProvenance") or []):
            out.append("(i) the control %s carries a non-provisional bar" % c)
    # (ii) every ratified-bar capability: VERIFIED with the chain intact
    by_module = {s["module"]: s for s in standards.get("standards") or []}
    live = {r["id"]: r for r in queue_rows}
    dead = {r.get("supersedes") for r in queue_rows if r.get("supersedes")}
    ratified_caps = [x for x in plan.get("capabilities") or []
                     if x["capability"] != c and all(m in by_module for m in x["modules"])]
    if not ratified_caps:
        out.append("(ii) no ratified-bar capability in the plan -- an empty domain proves nothing")
    for x in ratified_caps:
        name = x["capability"]
        v = caps.get(name)
        if v is None:
            out.append("(ii) %s is absent from the extension's output" % name)
            continue
        if v.get("status") != "VERIFIED":
            out.append("(ii) %s reads %r, not VERIFIED" % (name, v.get("status")))
        prov = {b.get("module"): b for b in v.get("barProvenance") or []}
        for m in x["modules"]:
            if (v.get("derived") or {}).get(m) != "verified":
                out.append("(ii) %s: module %s derives %r, not verified" % (name, m, (v.get("derived") or {}).get(m)))
            want, got = by_module[m], prov.get(m)
            if got is None:
                out.append("(ii) %s: no barProvenance for module %s" % (name, m))
                continue
            if got.get("provisional") is not False:
                out.append("(ii) %s: module %s's bar is provisional" % (name, m))
            if got.get("ratified_by") != want["ratified_by"]:
                out.append("(ii) %s: module %s ratified_by %r, the projection cites %r" % (name, m, got.get("ratified_by"), want["ratified_by"]))
            row = live.get(want["actRef"]["queueRow"])
            if (row is None or row["id"] in dead or row.get("act") not in RATIFYING
                    or row.get("actDigest") != want["sha256"] or row.get("artifactFileDigest") != want["sha256"]):
                out.append("(ii) %s: module %s's chain is broken at queue row %s (not a live act binding the bar's bytes %s)"
                           % (name, m, want["actRef"]["queueRow"], want["sha256"]))
    return out
