# C1 — the minimal Spec-to-Graph Transformer: design

Plan v1.1 task **C1** (WS-4, §6): *minimal transformer (candidates + diagnostics; N1; honesty boundary) — ARO agent —
transformer + self-test — verified by a fixture dry-run on synthetic prose.* This note fixes what is built before it is
built. It is the author's design, not a measurement: the transformer's author never grades it (Plan §2 standing rules),
never sees OPS's sealed placements (§6), and never computes its own coverage (ARO §4.3).

## What it is

```
registered source (bytes + digest) ─▶ segment ─▶ propose (model) ─▶ GATES (code) ─▶ candidate graph + diagnostics + run manifest
```

One command, one source per run:

```
python spike/transformer/transform.py --source <file> --digest sha256:<…> --registered-as <src:id> -o <run-root>
```

## The four stages

1. **Segment (deterministic).** The source is normalized exactly as `spike/graph/fragments.py` does (`norm-spike-1`: NFC,
   CR/CRLF→LF) and its digest is checked against `--digest`; a mismatch refuses the run. The text is cut into
   **sections** (by heading) for the model, and every non-blank line becomes a **mintable span** — a fragment is minted
   with the existing identity formula (`sf:` + sha256 of digest|text-span|range|normalization|text-hash). No other
   fragment kind exists, so nothing can be cited that is not a verbatim span of the registered bytes.

2. **Propose (the model; untrusted).** Each section goes to the model via `claude -p` (never an API key) with the section's
   lines numbered. The model returns JSON only:
   - `assertions[]`: `@type` (Requirement | AcceptanceClause | Definition | Constraint), `role`, `force`, optional
     `target`, `statement`, and `groundedBy[]` = `{line, quote, role: primary|context|definition|reference}`;
   - `diagnostics[]`: one of the transformer-emitted catalog (ARO §7) — `Ambiguity` (with ≥ 2 enumerated
     `interpretations`), `MissingInformation`, `ConflictingStatement`, `UnsupportedInference`, `UnresolvedReference`,
     `Underdetermination` — each with `evidence[] = {line, quote}`;
   - `closureProposals[]` (optional): N1's third legal output, routed to an L3 queue file, `model-proposed`, conferring
     nothing.
   The prompt states N1, D7 (ambiguity is reported, never resolved) and the absence rule verbatim. The model is a
   proposer only; nothing it says is trusted until stage 3.

3. **Gate (code; the honesty boundary enforced, not requested).** Each gate drops or converts, and logs what it did:
   - **G-GROUND** — every `quote` must be a contiguous substring of the cited line's normalized text; it is minted as a
     fragment over exactly that sub-range. A citation that does not match is not repaired: the assertion is
     **rejected** (logged). An L2 assertion with no surviving `primary` fragment is rejected. ⇒ **ungrounded = 0 by
     construction**, which is ARO §8.2's "a schema property, not an achievement".
   - **G-N1** — a fixed lexicon of the ARO §4.2 categories (language, framework, repository layout, ownership, runtime,
     deployment, database, broker, security mechanism, implementation approach) with named exemplars. An assertion whose
     statement names one that no cited fragment contains is **converted** into an `UnsupportedInference` diagnostic (the
     statement kept as the diagnostic's text, never as an assertion). This is the FX-INVENT shape gate; misgrounding that
     is schema-clean stays audit-only (FX-MISGROUND), and the transformer does not claim to catch it.
   - **G-AMBIG** — an `Ambiguity` with fewer than two interpretations is rejected as malformed (a "resolved"
     ambiguity is silent resolution). Whether an ambiguity was *noticed* is not self-reportable; FX-AMBIG measures it.
   - **G-SHAPE** — enums, required fields, and the L2/L3 split (L2 needs ≥ 1 primary `groundedBy`; closure proposals
     carry no `groundedBy`, only `rationaleSource`).

4. **Emit.** The run root receives:
   - `candidate.graph.jsonld` — the shape of `spike/graph/l2/srs-ws3.graph.jsonld`: `status: candidate`,
     `facetsDefault.origin = transformer(act:transformer:<run-id>)`, `ratification: unratified`, `records[]`,
     `diagnostics[]`, and `coverage.detectedClauseCoverage = "not computed by the transformer: independent channels
     (ARO 8.2; Plan v1.1 s6 — OPS)"`;
   - `fragments.json` — every minted fragment, in the existing record shape;
   - `closures.l3-queue.json` — closure proposals, if any;
   - `run-manifest.json` — source digest, transformer version + file digests, prompt digest, model id, per-section model
     output digests, and the **gate log** (every rejection and conversion, with its reason). Generation provenance is
     recorded and non-lapsing (ARO §4).

## The honesty boundary, as code

| the transformer MAY | it MAY NOT |
|---|---|
| propose assertions grounded in verbatim spans | emit an assertion without a primary verbatim span (G-GROUND) |
| report ambiguity, conflict, underdetermination, missing information | resolve an ambiguity, or report one with < 2 readings (G-AMBIG) |
| propose L3 closures, labeled `model-proposed` | state an unstated implementation choice as fact (G-N1) |
| record what its gates rejected | report its own coverage, misses, conflations or misgroundings (ARO §4.3) |

All output is candidate content: transformer-origin, unratified, **never gates** (D9) until the architect ratifies it
(C6, 100% review of generated normative assertions).

## Self-test (C1's deliverable "transformer + self-test")

- **Unit pins with a stubbed model** (the model call is an injected seam): each gate red-first — an invented quote is
  rejected; a database name with no grounding becomes `UnsupportedInference`; a one-reading ambiguity is rejected; a
  digest mismatch refuses the run; the emitted graph validates against the slice's shape; the run is byte-deterministic
  given the same model outputs.
- **Fixture dry-run on synthetic prose** (the plan's verification): a small synthetic spec written for this purpose —
  never a copy of SRS, RLA or cFE text, and never informed by OPS's placements — with planted examples of each fixture
  class (an invitation to invent, a droppable clause, an ambiguity, an example-not-requirement). One live `claude -p`
  run; the result is recorded as a dry run, not a measurement.

## Not in C1 (named so nobody reads them as done)

- the independent coverage channels, hand-count anchors and sealed seeding (C2, OPS);
- the screening pass (C4) and evaluation (C5, OPS); the review (C6, architect);
- **registration of the RLA source** (it is not vendored here; `source-register.json` lists it unregistered) and the
  **registered text extraction of the cFE DOCX** (Plan §14 Act 1: method, version, normalization, SHA-256, at Freeze 3).
  Both are Freeze-3 preconditions raised with OPS separately.
