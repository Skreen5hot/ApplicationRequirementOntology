# FX-SEAM-A — the founding-input seam divergence, on the real seam (authored RED at Phase 1.5)

**Specified by:** ARO v0.5.2 §13 (FX-SEAM-A), §16 (Phase 1.5, Phase 5 gate), §18 item 3. Work order: SPIKE.md §2. Target per Amendment 1 (docs/decisions/2026-09-10-phase-1.5-amendments.md): the SRS 3-module slice.
**Status:** RED. Green at Phase 5. The red half runs in `tests/test_fx_seam.py` as a strict expected-failure: it executes and must fail; a silent green fails the suite.

## What it reproduces

The `getFindings` family, on the seam Ops isolated: `panel-findings-store` declares the findings read API as `listFindings` / `getFinding`; a second model reading (the ArchitecturePlan) re-proposes it as `getFindings`; the brief's architecture section and the author-agent bar, both downstream of the architecture, carry the re-proposed name. Four founding inputs, derived independently, none carrying a Projection Input Manifest:

| seam | plan.json | Planner Contract | Builder Brief | Tester Contract |
|---|---|---|---|---|
| `panel-findings-store.findings-read` | listFindings | **getFindings** | **getFindings** (architecture section; the interfaces block says listFindings) | **getFindings** |
| `panel-findings-store.appendFinding` | appendFinding | appendFinding | appendFinding | appendFinding — control |
| `author-agent.proposeRevisions` | proposeRevisions | proposeRevisions | proposeRevisions | proposeRevisions — control |

`plan.json` is the supplied decompose, reduced. The other three are **representative**: no baseline run has been captured, so they state the drift the Ops manifest names. Arm 0's per-run capture (architecture exports for the store, the brief's interfaces block, the bar's expected names, the built author-agent's imports) replaces them; until then the fixture reproduces the class, not a measured run.

## Two facts the index records but cannot see

- The SRS prose names **none** of these functions and no `panel-findings-store` component (spike/report.md, F-14). The one authoritative place for this seam is an L3 closure the architect ratifies; projection carries it identically to all four consumers.
- `Finding` is declared twice in the plan (in `contract` and again in `panel-findings-store`): an owner divergence a name-equality check does not see. Projection removes it by construction.

## The one check it fails, and why it is near-tautological

Under single-graph projection every consumer receives the seam's identity from one eligible graph through one Projection Input Manifest, so the divergence is **unrepresentable**. This guards the projection **mechanism**, not the world; FX-SEAM-B keeps the larger claim honest. **Uniqueness rule (§13):** with single-source projection disabled — test-assembled independent derivation only — the mismatch reappears and a suite lacking this check passes, wrongly.

## What turns it green

A projection compiler declared as `tool.aro-project`, exposing `project_founding_inputs(graph_dir, *, independent_derivation=False)` and returning the four documents keyed as in `seams.json`, each carrying the same non-null `projectionInputManifestDigest`. The spike's own projector (`spike/projections/project.py`) is a draft of that surface; it refuses to project unratified closures, so it cannot turn this green until the slice's records are ratified.

## Not covered

Whether the class is currently live on HEAD is Arm 0's question; no Arm 0 result exists. The three representative documents are not run artifacts.
