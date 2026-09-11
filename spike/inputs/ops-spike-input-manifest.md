> **Receipt.** Pasted into the ARO dev-agent session by the operator on 2026-09-10 (after 16:07 local), together with `srs-seam-slice-plan.json`. Author of record: Ops (coord-j), spec-blind. Stated origin folder: `C:/Users/coord/Documents/aro-spike/`. This local copy is as pasted; no coord-side digest is known.

# ARO spike input — the smallest SRS slice that contains the author-agent seam failure

**Purpose.** This is the minimal input for the ARO **projection-payoff spike**: prove (or disprove) that a
deterministically-projected `plan.json` + `declared` tier makes the author-agent seam-name mismatch stop
flipping — *before* committing to the BFO/CCO ontology. It is a **3-module slice of the SRS**, chosen because
that is the smallest set that still contains the failure. Not the RLA (it builds clean — no failure to fix);
not the whole SRS (that is Phase 4's cost, which the spike exists to defer).

## The failure this slice contains (structural — no SRS content needed to state it)

- `panel-findings-store` **declares** the findings seam: `getFinding(rootDir, id) -> Finding | undefined` and
  `listFindings(rootDir, cycle) -> Finding[]`.
- `author-agent` **consumes** that seam. The **model-proposed** builder reaches for a plausible-but-nonexistent
  **`getFindings`** (plural) instead of the declared `getFinding` / `listFindings` → the contract and the
  builder disagree on the seam name → author-agent stubs/flips run-to-run.
- `contract` **owns the shared types** (`Finding`, `ProposeRevisionsInput`, `ProposeRevisionsResult`) and
  exports no behavior of its own — it is the types module that a projection would emit once and hand to both
  consumers identically.

This is the whole thesis in one seam: the name exists in exactly one authoritative place, but today it is
*re-proposed* by a model at build time, so it drifts. ARO would fix the name once in a ratified graph and
**project it identically** into the contract, the builder brief, and the tester contract — the mismatch
becomes impossible rather than caught.

## The slice — dependency-closed

| module | role in the slice | depends_on | declared seam |
|---|---|---|---|
| `contract` | shared-types owner (projected to both) | — | types only: `Finding`, `ProposeRevisions*` |
| `panel-findings-store` | **declares** the findings seam | `contract` | `getFinding`, `listFindings`, `appendFinding` |
| `author-agent` | **consumes** the seam; where the drift happens | `contract`, `panel-findings-store` | `proposeRevisions` |

Closed set — no dangling dependencies — so it builds standalone.

## The two arms of the spike, and what you supply

**Baseline (no ARO)** — already runnable, no authoring needed:
`srs-seam-slice-plan.json` (in this folder) is the exact model-proposed decompose output for these three
modules. Build it N times against the full SRS spec and observe author-agent drift to `getFindings` / stub.

```
REPO="<a fresh clone or workspace>"
python -m runtime.coord_j "C:/Users/coord/Documents/aro-spike/srs-seam-slice-plan.json" \
  --workspace "$REPO/.spike-ws/baseline-<runtag>" \
  --spec "C:/Users/coord/Specification-Refinement-System/SPEC.md" \
  --driven --install-deps --model sonnet
```

**Treatment (ARO)** — hand-author a faithful graph for the slice, project `plan.json` + the `declared` tier
from it (one seam identity → contract + builder brief + tester contract), build N times, observe whether the
drift disappears.

**What YOU supply as the graph-authoring source (I stay spec-blind to SRS content):** the actual SRS prose for
the three modules —
- the **author-agent** section (its §3 / revise-propose capability),
- the **panel-findings-store** section (the findings-store interface),
- the **contract** section defining `Finding`, `ProposeRevisionsInput`, `ProposeRevisionsResult`.

Paste those three sections beneath this file (or alongside it) as the graph's source. The graph must represent
*that prose faithfully*, not the decompose's `scope` summaries — the decompose is the thing under test, so the
graph cannot be authored from it without begging the question.

## Acceptance (the A/B verdict)

- **Baseline:** across N runs, author-agent's consumed seam name is unstable / wrong (`getFindings` appears;
  author-agent stubs on the mismatch at least some of the time).
- **Treatment:** across N runs, author-agent consumes `getFinding` / `listFindings` **every time** (zero
  drift), because the name was projected, not re-proposed. author-agent builds at least as often as the
  baseline's best run, with the seam mismatch eliminated as a failure cause.
- **Null / negative result is still a win:** if author-agent keeps failing even with the seam projected
  correctly — i.e. the flip actually lives in the executor, not the founding input — you learn ARO's premise
  doesn't hold for this case *for the price of a slice*, not five phases. (The grader-runner data point already
  hinted some failures live downstream of the plan.)

## Constraints that keep this a spike, not Phase 4

1. **Lightest possible graph — plain JSON-LD, NO BFO/CCO.** Just enough structure to carry the seam identity
   and the interface shapes for three modules. Pulling in the upper ontology is the exact risk the spike
   defers; if you reach for it here, the spike has failed as a spike.
2. **Hold out the graph author.** Whoever authors the slice graph must not also be tuning the builder, or you
   prove circularity instead of projection — same discipline as the spec's reference-graph hold-out.
3. **Deterministic projection only.** The projection step may not resolve or invent anything; it just emits
   the ratified seam name and types. If it "helps" the builder, the result is contaminated.

---
*Prepared by Ops (coord-j), spec-blind: the slice boundary and the failure are stated in structural /
interface terms only; the SRS prose for the three sections is yours to paste as the graph's source.*
