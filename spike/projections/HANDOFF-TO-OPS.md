# Handoff to OPS — the treatment arm's founding inputs (status: READY, pending two confirmations)

**From:** ARO dev agent. **To:** OPS (coord-j), who own Arm 0 and the treatment builds (architect's direction, 2026-09-10). **Governing:** ARO v0.5.2 §16 with Amendment 1 (target: the SRS 3-module slice) — `docs/decisions/2026-09-10-phase-1.5-amendments.md`.

## Status

**Projected on 2026-09-11** after the architect acted on all eleven records in `spike/measurements/ratification-queue.jsonl` (five L2 records accepted, three L3 bundles and the layout convention ratified, the layout rule ratified at its content address, the adjudication decided **C**). Re-projection is byte-identical; that check is the recorded basis of the `Projected` status (ARO §8.1). The package is in `spike/projections/out/`.

| file | sha256 | what it is |
|---|---|---|
| `out/plan.json` | `243eef68…4259` | the loop's shape: `units[{id, files, covers, kind, depends_on, scope, signatures, declarations}]`, `capabilities: []`, `oracles: []` |
| `out/declared.json` | `744667e4…77c7` | the `declared` tier per module; every export carries `layer` (L2 or L3) and the record it came from |
| `out/planner-contract.json` | `8f731f15…5011` | the ArchitecturePlan shape: per-module exports and `depends_on` |
| `out/builder-brief.json` | `70af2bed…68e6` | per-module `mustExport`, `imports`, `interfacesBlock`, `callsPerArchitecture` |
| `out/tester-contract.json` | `7a4e707b…7ed9` | per-module `assertsExports`, `assertsCalls` |
| `out/projection-input-manifest.json` | `e9ba467b…7340` | the one manifest every file above embeds, with its digest |

Every file carries the same `projectionInputManifestDigest`. If any two differ, the package is not a projection and must not be built. Regenerate at any time with:

```
python spike/projections/project.py --check                      # must print: Projected: byte-identical on re-projection
python spike/projections/project.py -o spike/projections/out
```

## What the projection says about the seam under test

The read seam `author-agent → panel-findings-store` reaches every consumer as the same two members, `listFindings` and `getFinding`, from one ratified record (`sr:L3:findings-read-seam`) through one manifest: the store's plan signatures, the Planner Contract's exports, the author-agent brief's imports and its architecture section, and the author-agent bar's `assertsCalls` all carry them. `getFindings` appears nowhere. That is the treatment arm's founding-input state; whether the build honors it is what the builds measure.

**Adjudication C, and what it means for the build.** The architect chose to relocate `author-agent` to `src/author-agent.ts` for this spike with the conflict against SRS §5 (`.claude/agents/author`) left open. The manifest records `provisional: ["author-agent.files (conflict with L2 left open by adjudication C)"]`. The treatment arm therefore reproduces the baseline's module shape exactly, and the PROVISIONAL cap applies to author-agent's file layout (ARO §11.2). Read the treatment result with that in view.

## Preconditions OPS must confirm before building

1. **Same source in both arms.** Amendment 1 pins the target to the SRS at `sha256:2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450` (the copy at `C:/Users/aaron/OneDrive/Documents/SPEC.md`). The baseline command in the Ops manifest reads `C:/Users/coord/Specification-Refinement-System/SPEC.md`. Confirm the two files are byte-identical; if not, the arms read different sources and the A/B is void.
2. **Same plan file.** `spike/inputs/srs-seam-slice-plan.json` is a re-serialised paste; bind it to the coord-side original's digest before treating the baseline as the same plan.

## How to run the treatment arm

The projected `plan.json` is consumable by the loop as it stands (`python -m runtime.coord_j out/plan.json --workspace … --spec <SRS>`). The Planner Contract, Builder Brief and Tester Contract are what the loop's architect dispatch, brief renderer and bar author would otherwise derive independently; feeding them in place of those derivations is the treatment. How that substitution is wired inside the loop is IA-side work; the ARO side supplies the inputs and their manifest, nothing more.

## Arm 0 capture list (adopted by the architect, 2026-09-10)

Per baseline run, capture and keep:

- the ArchitecturePlan's exports for `panel-findings-store` (the architect dispatch's output);
- the author-agent brief's interfaces block, and its architecture section, as rendered;
- the author-agent bar's expected export and call names;
- the built author-agent's imports from `panel-findings-store` (`imported_members` shape);
- the rendered `listFindings` signature in the brief (the plan stores the truncated `Finding[`; routed to IA DEV as an external finding, capture only).

Classify each flip: **A** if any two of the first three disagree (founding-input divergence), **B** if they agree and only the build diverged. The treatment arm's result is read against that classification.

## Acceptance (unchanged from the Ops manifest)

Baseline: `getFindings` appears; author-agent stubs on the mismatch at least some of the time. Treatment: author-agent consumes the projected members every time, and builds at least as often as the baseline's best run with the seam mismatch eliminated as a cause. Null result is a result: if author-agent still fails with the seam projected, the flip lives in the executor.
