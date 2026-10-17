# Decision record — A9 restated against the amended SRS, 2026-10-17

Recorded verbatim by the ARO dev agent on 2026-10-17, at the architect's statement in session. The act is the
architect's. It re-anchors the WS-3 naming act (`2026-10-01-a9-ws3-target-naming-act.md`, with its region amendment
`2026-10-01-a9-region-amendment.md`) to the source registered on 2026-10-17
(`2026-10-17-srs-source-amendment-and-registration.md`). Re-acceptance after a source lapse is a new anchoring act over
the same historical record (ARO §3.2). The earlier records are not edited. Nothing in the quoted block is paraphrased.

---

> A9 restated: the WS-3 target and its region (lines 43–53 and 73–76) are read against the registered SRS src:srs-spec@2, sha256 109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614.
>
> — Aaron Anthony Damiano, 2026-10-17

---

## What it changes, and what it does not

- **Changes:** the source the A9 target is read against. It moves from `src:srs-spec` (`2428b115…`) to `src:srs-spec@2`
  (`109e1b50…`).
- **Unchanged:** the target ("SRS adjudication and registration core": C-S2, C-S3, C-S7) and the region. The amendment
  edited line 74 only and shifted no line, so lines 43–53 and 73–76 name the same text in both versions, apart from
  W-CS7-N's formula.
- `spike/graph/ws3/build_l2.py` cites this record. A test checks that the region and digest it states equal the
  graph's `regionLines` and source digest, so the restatement and the graph cannot drift apart.
