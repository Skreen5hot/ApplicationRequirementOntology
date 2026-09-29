# Decision record — approval of the decision memo, and the ruling that Plan v1.1 governs (2026-09-29)

Recorded by the ARO dev agent (IntegratedAgent Dev, ia-dev) on 2026-09-29. Both acts are the architect's; their words
are quoted verbatim. The memo approved is IntegratedAgent
`experiments/comms/DEV-2026-09-29-decision-memo-graph-spike-and-gaps.md` (commit `fadf68a`); the execution plan it
produced is `experiments/comms/PLAN-2026-09-29-memo-execution.md`. The governing instrument is
`docs/decisions/2026-09-14-provenance-foundation-phase-plan-v1.1.md`, SHA-256 `c43954a6…d7af8`, ratified 2026-09-14
(§14), recorded at `6cbad35`. Nothing below amends Plan v1.1 or the 2026-09-14 closeout act; section 3 is the operative
reading of the two approvals together.

---

> I approve the memo, now we need a formal plan with who is responsible you (Dev), Opps, and myself (please only give me
> essenital tasks I am the bottle neck I defere to you and Opps to make sustainable everyday decisions) — Architect,
> 2026-09-29

> Plan v1.1 governs; read the memo as its Dev/Ops execution — Architect, 2026-09-29

---

## 1. What the record did not carry, and now does

The memo and its plan were written from the shared remote record, which did not contain Plan v1.1: it was ratified
on 2026-09-14, committed locally on 2026-09-15 and never pushed, so its stated canonical URL on `main` did not resolve
and neither memo reviewer saw it. Beside it sits *Corrective Amendment 1* (2026-09-15, "ARO DEV", untracked, UNRATIFIED
CANDIDATE), whose §8 gate — ARO DEV freeze, **IA DEV review**, **IA OPS verification**, architect act, all bound to one
SHA-256 — must complete before any Stage A task begins. Under the ruling above, that gate is the first item on the
critical path, and the IA DEV review is owed by the agent recording this.

## 2. The ruling, applied

**Plan v1.1 governs.** Its scope, workstreams WS-1..4, owners (§2), governance parameters (§7: GP-E = 4 h/week, two
sittings ≤ 2 h), calendar (§12), duration bound (five calendar weeks from 2026-09-14, ending 2026-10-19) and executed
instrument (§14: Act 1 registering the cFE specification; Act 2 ratifying the plan) stand as ratified. The 2026-09-14
closeout act stands unamended: the memo's D2 "scope amendment" and D6 "suspension" are **not** recorded as acts; both
reduce to the readings below. **The memo is its Dev/Ops execution**: the memo's mechanisms are how IntegratedAgent
Dev and Ops carry out the tasks v1.1 assigns them, under v1.1's owners and calendar.

## 3. Operative reading — memo into Plan v1.1

| Plan v1.1 | memo | operative reading |
|---|---|---|
| WS-1 act tool (accept / amend / open diagnostic / decide; writes lines, digests, per-act times; agent-actor refusal; CLI, `--json`, exit 0/1/2, read-only surface) — the tooling gate before any new queue | D2 plan-side declarations ratification store: kinds `source-derived` (digest + span **required**; lapses on digest change) and `design` | **one mechanism.** The act tool is the operator-facing surface; the store is its factory-facing output, which the loop already fails closed on (`record`, `provisional: False`, `barProvenance`). D2-minimal is WS-1's tooling gate. §§2–13 remain the specification of records and closures. |
| §7 GP-E = 4 h/week | memo Q2 | answered |
| §2 owners: all queue acts are the architect's | memo Q3 | answered; a named reviewer would be an amendment to v1.1 |
| WS-2 package-to-factory contract; boundary decision (a) taken; F2-verification N = 5 (OPS), frozen per checklist 1 | D5 conditional | decided; D5 collapses into WS-2 |
| WS-3 provenance at capability grain on the registered cFE specification | precondition 3 / A7 | the target is named by Act 1 |
| Amendment §4 held-out normative-clause coverage (clause census frozen by OPS with stable IDs and locators; diagnostics counted separately; 100%) and WS-4 | D3 grounding-coverage instrument (separate mechanically verified pass; both directions; planted misreadings as acceptance) | **one instrument**, built to §4's definitions if the amendment is ratified, to WS-4's otherwise; D3's disciplines are its acceptance |
| WS-1 outcome mapping: R acts per specification, A = sustained rate × GP-E, starvation categories (a)/(b)/(c) | D4 two rates | same measurement; the L2-acceptance / L3-ratification split is added to the WS-1 report |
| "Out": SHACL/ontology buildout, ADR-002/003, transformation at scale; "In": WS-4 probe, ARO v0.5.3 | D1, D6 | D1 stands under both; D6 is a pointer at v1.1's "Out" — nothing outside WS-1..4 is authorized |
| five calendar weeks from 2026-09-14 | — | **at risk, not breached**: two of five weeks elapsed with the plan unpushed, no Stage A task begun, the §8 gate unstarted. Recorded here as the bound's state on the day of the ruling. |

## 4. What follows from the ruling, by owner

- **Architect:** the acts v1.1 §12 lists, on v1.1's calendar; plus the push of `6cbad35` and the merge to `main`, which
  publishes v1.1 as its own notice states (IntegratedAgent ledger row `a4-aro-merge-authorization`); plus, after the §8
  reviews, ratifying or declining Corrective Amendment 1 by a dated act citing its SHA-256 and both review digests.
- **IA Dev:** the §8 step-2 review of Corrective Amendment 1 (first); then WS-1's tooling gate as D2-minimal; the
  DEV consistency attestation the re-pin chain needs (A2); D3 as the coverage instrument; the plan and seed kept to v1.1.
- **IA Ops:** the §8 step-3 verification; the F2-verification build (WS-2) and the instrument extension (WS-3) as v1.1
  assigns them; verification of D2-minimal and D3 through the real controller and the real-spec acceptance gate.
- **Everyday decisions** inside WS-1..4 are Dev's and Ops', recorded in the IntegratedAgent ledger; only acts, changes
  to recorded instruments, new arms or targets, and unresolved Dev/Ops disagreement reach the architect.

---

Applied by the ARO dev agent in the commit that carries this entry: this file, and `docs/HANDOFF.md` /
`docs/HANDOFF-PLAN.md` pointed at Plan v1.1 as governing. Committed locally on `armb-source-path-parameter` on top of
`6cbad35`; **not pushed** — the push publishes v1.1 and is the architect's act (row `a4-aro-merge-authorization`).
No graph, ontology, projection, rule or fixture changed; the layout gate and the spike's tests are the proof.

---

**A4 executed (recorded act, 2026-09-29).** The architect: "authorize the A4 push and merge." Applied by the ARO dev agent in the commit that carries this note: `armb-source-path-parameter` pushed to origin (carrying `6cbad35` Plan v1.1, `1d86a74` this ruling record, `256150c` Candidate 1, `fc199fd` Candidate 2, and this note) and fast-forwarded into `main`, so Plan v1.1's canonical URL resolves and every act since 2026-09-13 is on `main`. IA OPS' s8 step 3 is unblocked from this push. The sentences above that say "not pushed" were true when written and are kept as history.
