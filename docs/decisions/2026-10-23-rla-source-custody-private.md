# The RLA source stays private: registered by digest, never vendored

- **Date:** 2026-10-23 (asked 2026-10-22, answered on resumption)
- **Actor:** Aaron (the architect; the RLA source's authority of record — both RLA bars in force read
  `ratified_by: "operator (RLA source, relayed by ops)"`)
- **Concerns:** Plan v1.1 §6 (the RLA is one of the three Stage-C specifications) and §11.3 (Freeze 3); IA Ops verdict
  `80ec240`, `OPS-2026-10-22-the-rla-spec-hashes-to-34b5b05f-…-the-custody-ruling-is-the-operators.md`, which held for
  this ruling

## The question, as put to the operator

> May the RLA spec (SPEC.md, 4,917 bytes, sha256 34b5b05f…a3dc) be copied into the public ARO repo?

Options offered: **Keep it private (Recommended)** — registered by digest only, the file stays off GitHub, CI tests that
need it lapse by design, and a run that needs the bytes gets them through a local, untracked copy; or **Publish it in
ARO** — vendored at `sources/rla/34b5b05f/SPEC.md`.

## The ruling, verbatim (the option selected)

> Keep it private (Recommended)

## Effect

- The RLA source is **not vendored** in this public repository, now or by default later.
- Its registration (a week-5 act, beside Freeze 3) is **by digest**: `sha256:34b5b05ffa23b8e8033d766e1759b47c815955a2483f31747feb75e62782a3dc`,
  4917 bytes, `norm-spike-1` (LF-only, so normalization is a no-op), document name `SPEC.md` — the values IA Ops
  measured on the box that holds the file (`80ec240`), corroborated by the factory's oracle store `oracles/34b5b05ffa23/`
  in use since 2026-09-11.
- Readers resolve the bytes through the per-source override `ARO_SOURCE_DOC_34B5B05F` (`spike/graph/fragments.py`); where
  no copy is present, fragment work lapses legibly ("source missing: every fragment lapses"), never crashes.
- A copy made for a run is placed in an **untracked** location and never committed.
