# B6: the C-S2 demonstration control is retired (rq-090)

- **Date:** 2026-10-22
- **Actor:** Aaron (the architect)
- **Act:** `rq-090`, **ratified** 2026-10-22T06:41:44-04:00, bound to
  `spike/projections/ws3/freeze2/control-disposition.json` at sha256 `27e2c511…9d7b` (batch WS3-7)
- **Concerns:** Plan v1.1 s3 "the demonstration control" (PF-OPS-2) and task table B6; the designation `rq-089`
  (2026-10-20), which promised this separate act

## What preceded it

The freeze-2 demonstration passed: `OPS-2026-10-22-freeze2-demonstration-passes.md` (IA `a4fd46e`), under the freeze
record `0bd73f8d…ee67`. `fx_cap.check(...)` returned `[]`: C-S2 read **BLOCKED** with `grader-runner`
**built_unverified** (a provisional, model-authored bar), exactly as `rq-089` predicted before results; C-S3 and C-S7
read **VERIFIED** with `ratified_by` carried from `rq-078` / `rq-079`.

## The act, verbatim (the `actNote`)

> I RATIFY rq-090 at SHA-256 27e2c511cfa24d7440b4a1dfa345a39e03889904aec604fb8120314b7aa39d7b.
> I retire C-S2 (grade) from the WS-3 capability target for the remainder of this phase.
> This disposition follows the passing Freeze 2 demonstration recorded in OPS-2026-10-22-freeze2-demonstration-passes.md at IA commit a4fd46e, where the pre-stated control result was observed: C-S2 was BLOCKED, grader-runner was built_unverified, and fx_cap.check(...) returned an empty failure list.
> The Stage D closeout must preserve the complete record: C-S2 was the disclosed demonstration control, behaved as predicted, and was subsequently retired. No conformance score is claimed for it, and neither its built code nor its provisional model-authored bar is deleted or retrospectively granted authority.
> Grading may return in a later phase only as a newly frozen capability with a specification-authored bar and acceptance oracle, each independently reviewed and ratified.
> — Aaron Anthony Damiano, 2026-10-22

## Effect

- **Stage B is complete:** B5 (demonstration) passed and B6 (control disposition) is done. The control never becomes
  an immortal provisional.
- The WS-3 capability target for the rest of the phase is **C-S3 (adjudicate)** and **C-S7 (register)**. The closeout
  reports C-S2 as the disclosed control, retired by this act.
- Next: Stage C (the transformer probe), then Stage D (closeout).

## Sitting length

The operator's statement, verbatim: **"Ratified, 15 min"**. The queue row's `sittingStart`
(`2026-10-17T03:25:31-04:00`) is a stale value carried by the act tool from an earlier session, not this sitting's
start; the stated 15 minutes is the length of record. This is week 4's third sitting (GPE-1 as amended: at most three).
