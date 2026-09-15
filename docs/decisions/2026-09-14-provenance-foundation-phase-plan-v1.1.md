# Provenance Foundation Phase — Plan v1.1 (Public Ratified Edition)

**Publication status:** RATIFIED AND PUBLISHED · supersedes v1.0 · the architect's pre-signature findings AR-1..AR-5 and recommendation REC-1 are dispositioned (§15) · both agent reviews are incorporated · no open findings or registration fields.
**Canonical URL:** [https://github.com/Skreen5hot/ApplicationRequirementOntology/blob/main/docs/decisions/2026-09-14-provenance-foundation-phase-plan-v1.1.md](https://github.com/Skreen5hot/ApplicationRequirementOntology/blob/main/docs/decisions/2026-09-14-provenance-foundation-phase-plan-v1.1.md)
**Publication date:** 2026-09-14
**Copyright:** © 2026 Aaron Anthony Damiano
**Document license:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) · this file-specific notice governs this document; the repository's MIT license governs other repository material.
**External source license:** the registered NASA cFE source is separately licensed under Apache-2.0; this document's CC BY 4.0 license does not relicense that source.
**Ratification:** executed by Aaron Anthony Damiano on 2026-09-14 (§14). This ratification is the new authorization contemplated by the spike closeout; the spike remains CLOSED, its record untouched, and no spike arm is created or reopened.
**Governing texts:** the canonical spike closeout (2026-09-13) and its scoped Phase-1 ratification of ARO v0.5.2 (act D1); ARO v0.5.2 §§2–13 as the graph/queue/projection specification; CP/SM at the pin resolved by WS-2.
**Authorizes (AR-5):** four workstreams (WS-1..4) comprising **three measurement programs** — the F2-verification program, the capability program (build + demonstration), and the transformer-probe program — **whose execution counts (N per protocol, the §4 additional samples, the §6 re-run rule) are governed by their Part II freeze checklists**; no execution starts unfrozen.
**Does NOT authorize:** transformation at scale (which now recedes behind the expanded pilot, per AR-4); any capability-level claim ahead of WS-3 evidence; any code-quality claim; the ADR-002 grounding landing (continues non-blocking per v0.5.2); relaxation of the ADR-002/ADR-003 gates; factory consumption of transformer-derived capability content ahead of INT-4 (§8).
**Duration bound:** five calendar weeks from the act; exceeding it is a finding. Operator load bounded by GP-E (§7), inclusive of WS-4 review, adjudication, and audit.
**Ratification surface:** completed in §14: this plan; GP-E = 4 h/week; boundary decision (a); the external-specification registration; the WS-3 target naming act (REC-1); and the INT-4 assignment. Change log §15; independent review attestation §16.

---

# PART I — THE PLAN

## 0. Charter — the architect's finding, adopted verbatim

> ARO did not prove that it makes AI generate better code. It proved that it can prevent AI interpretations from being mistaken for approved requirements. That is a foundational capability for a trustworthy autonomous build system and warrants continued, measured investment.

The demand side exists: the factory **fails closed** on absent or unratified provenance — `record`, `provisional: False`, `barProvenance` — and produces `built_unverified` and BLOCKED honestly. The ratification queue is the only process producing ratified declarations at scale. This phase makes ARO that supply chain and measures whether the supply can be **sustained** (WS-1), **delivered** (WS-2), **exercised at the ruled grain** (WS-3), and **produced from prose at all** (WS-4). Every claim is a provenance claim; none is a code-quality claim. The honest number will likely **rise** through this phase — through ratified bars — and §8 requires the closeout to make every point of recovery **legible as earned**: traced to a ratification act, never to a relaxed gate.

## 1. Scope

**In:** the three closeout preconditions as WS-1..3; the minimal transformer probe (WS-4); the act tool with read-only programmatic surface; the OPS **instrument extension** (§5); ARO v0.5.3; F6 remedy (a), severable; the INT-4 draft.
**Out:** transformation at scale; the SHACL/ontology buildout; ADR-002/003 resolution (full-program gates; the probe runs on the spike-proven representation, stated, not hidden); new spike arms; re-litigation of the seam result (settled: Arm A shipped and standing; no seam license claimed for ARO, and none is claimed here).

## 2. Sequencing and owners

| Stage | Weeks | Contents |
|---|---|---|
| **A — unblock** | 1 | Ratification act · boundary decision (a) · DEV consistency attestation → architect re-pin act → ARO v0.5.3 · act tool (CLI, `--json`, 0/1/2, read-only) · re-projection · **freeze 1** → F2-verification build (OPS, shipped config) |
| **B — capability grain** | 2–3 | Instrument extension built + calibrated (OPS) · WS-3 graph with capabilities · sittings via the tool · projection · **freeze 2** → capability build + **FX-CAP live demonstration** · FX-SEAM-B per F-04 |
| **C — transformer probe** | 3–4 | Minimal transformer (ARO) ∥ spec prep, sealed seeding, channel calibration (OPS) · **freeze 3** → runs · independent execution (OPS) · screening (ARO) · adjudication + 100% architect review of normative assertions |
| **D — verdict** | 5 | Affordability computation · INT-4 draft · closeout in the canonical idiom · the tee-up decision placed as a *separate* act |

**Owners.** *Architect:* the act, GP-E, boundary decision, re-pin, F6(a) conferral, all queue acts, WS-4 adjudication + GP-A sample, INT-4 ratification, verdict. *ARO agent:* v0.5.3, act tool, graph extension, transformer, projections, queues, screening pass, INT-4 draft. *IA DEV:* the v0.4.2→v0.4.9 **attestation of consistency with recorded rulings — not per-change ratification**; instrument-extension format review; INT-4 review. *IA OPS:* every measurement — F2 build, instrument extension + calibration, capability build + demonstration, spec seeding (sealed), channel calibration + hand-count anchors, independent execution; INT-4 review. **Standing rules phase-wide:** authors never grade their own work · one instrument per question, and **the mechanism under test never attests itself** · every protocol frozen before its first run against the Part II checklist.

## 3. WS-1 — the ratification budget (precondition 1)

**Method.** (1) **Tooling gate first:** the act tool lands before any new queue opens — operator answers *accept / amend / open diagnostic / decide*; the tool writes lines, digests, per-act timestamps, derives verbs by layer, enforces the agent-actor refusal; CLI with `--json` and 0/1/2 exit codes as a **read-only** programmatic surface; queue presentation scaled to decision-content. Rationale recorded: the spike's rate was measured under file-surgery conditions; the qualitative finding — *comprehension cost, not act count, is the operator's real burden* — is a deliverable. (2) **GP-E stated in the act** (recommendation §7). (3) **Measurement** across WS-3/WS-4 sittings, per-act timestamps, adjudication and audit acts included.

**Starvation taxonomy (PF-OPS-4 adopted).** Three categories, only one a cost: **(a) inter-sitting latency** — queue open between scheduled sittings: the batching design working; reported, **never counted as cost**; **(b) intra-sitting stall** — operator present, blocked elsewhere mid-sitting; reported as friction; **(c) critical-path block** — agent work that cannot proceed pending an act, in blocked calendar hours: **the only category entering the affordability computation.** The tool tags each interval at capture.

**Outcome mapping (binding).** R = acts per specification (WS-3/4 actuals, audit acts included); A = sustained rate × GP-E; cost adjusted by category (c) only. **(i)** clears → precondition 1 discharged, numbers recorded. **(ii)** clears with levers → discharged with lever acts recorded; GP-B gets its first value from evidence. **(iii)** does not clear → **fails, recorded without euphemism**: full-program authorization off the table on this evidence; ARO continues at hand-authored-priority-boundaries scope, which the spike proved viable and WS-2/3 make durable.

## 4. WS-2 — the package-to-factory contract (precondition 2)

**Boundary decision (a), recommended:** projector emits deliverables only (`src/`); test and bar locations travel in the Tester Contract and the declaration channel (F6(b) renders it). Basis: `files` means *deliverables* by the loop's documented contract; D12/D15 oblige projection to honor consumer semantics; (b) would modify shipped behavior Arm A depends on. **F1 is settled in design by this stroke — and settled in fact only by the freeze-1 transport proof (AR-2):** one typed callable signature travels **ARO → projection → declaration channel → the factory's brief and test-author contexts**, arriving with its `record` provenance intact and rendering ENFORCEABLE. The F6(a) `Finding`-types closure is the natural probe payload; if F6(a) is severed, a minimal synthetic typed declaration is authored for the check (one act). **A transport failure is a consumer-side finding owned by IA DEV**, and the F2 program does not run until the channel is proven. **Standing boundary rule:** typed content crosses via the **declaration channel**; `plan.json` stays deliverables-only; no new plan fields for what declarations carry.

**The re-pin (PF-F1):** DEV attests **consistency with recorded rulings** — expressly not per-change ratification, which the record cannot supply. The architect's re-pin is a **closure act over that attestation**, residual expressly assumed, display duties stating what the attestation proves and what it does not. Full audit considered and declined, recorded. v0.5.3 carries the re-pin, projector rule, F-06 fix. **F-04's answer** (INT-2 path in v0.4.9?) arrives with the attestation; *partial* is expected and handled in §5. **Compatibility check (AR-3) — attestation is not behavioral compatibility:** before v0.4.9 becomes the measurement baseline, OPS runs a focused pre/post comparison on three surfaces — **projection-output handling, declaration transport, and INT-2-related behavior** — replaying the spike's recorded consumption inputs and comparing v0.4.9's outputs against the spike-recorded outputs. Every difference is triaged by DEV: **traceable to a recorded ruling** (expected; documented) **or a finding** (blocks the baseline until adjudicated). The re-pin act then rests on a three-part basis, each part typed: **consistency (attested) + compatibility (measured) + residual (assumed by the act)**.

**F6 remedy (a), severable:** one L3 closure — `Finding`'s field types as architect-conferred values, the two source examples cited as rationale, never grounding; one act; covered by the re-projection.

**The F2-verification build (PF-OPS-1 + PF-F4 resolved — the claim typed to its power):** OPS; frozen per checklist 1: N = 5, pinned SRS, fresh workspaces, classifier version pinned, **class taxonomy frozen** (definitions versioned before any result is seen), **shipped configuration** with digest recorded, full failure-class distribution captured, spike baseline attached (F2 4/5; F7 1/5; D 1/5).

**Mapping — binds to the F2 class only, stated at N=5's actual power:**
- **0/5** → *F2-class failures reduced from a 0.8 base rate to below detection at N = 5; the boundary is **resolved for this phase's purposes**.* **Residual stated:** rates up to ≈ 0.2 cannot be excluded at this N — P(0/5 | p=0.5) ≈ 3%, but P(0/5 | p=0.2) ≈ 33%. Any later F2-class recurrence — including in the WS-3 build — routes to the escape protocol **without impeaching this discharge**.
- **1/5** → triage the instance by cause signature: *"F2 + the strict type gate and nothing else"* → the boundary is **not** resolved; any other cause → the F2-class discharge stands with the instance recorded in the distribution.
- **≥2/5** → boundary not resolved; escape protocol before Stage B relies on projected packages.
- **All non-F2 classes** read against baseline: baseline-rate recurrence is background; movement is a finding on its own track; neither blocks discharge nor reopens decision (a).
- **The WS-3 capability build is recorded as an additional F2-class sample at zero marginal cost** — the effective N grows through the phase, and the Stage D closeout restates the residual bound at the final N.

## 5. WS-3 — provenance at capability grain (precondition 3)

**Method:** extend the graph to **the WS-3 capability target named and source-digested by a dated Stage-A act (REC-1)** — the agent proposes candidates during Stage A; the architect's naming act records the target's title/region and digest **before Stage B begins**; target selection precedes implementation, under the same pre-registration discipline as every protocol here — with capabilities and acceptance clauses; ratify via the tool (WS-1 data); project under WS-2 rules; OPS builds; the capability machinery runs live.

**Interim capability-boundary pin (PF-O1, until INT-4):** the factory's `capability_lattice` owns structure and ordering; ARO acceptance clauses enter as **boundary-oracle sources** through registration acts; disagreement between a factory-derived boundary and an eligible Accepted clause is a **finding and an adjudication — never a silent override in either direction.**

**The instrument extension (PF-OPS-3 resolved — no self-attestation):** the OPS classifier reads build outcomes; it does not read `barProvenance` chains or capability verdict states. Consuming the factory's own `capability_status` for the demonstration would be **the mechanism under test attesting itself — forbidden.** OPS therefore builds a **ledger-reading extension** (est. 1–2 days), verified before any live reading by **calibration against the existing synthetic corpus**: the extension must reproduce the known verdicts of the Q1/Q2/Q5 and AL-pin synthetic states. DEV reviews the ledger-format read. Calibration record attaches to freeze 2.

**The demonstration control (PF-OPS-2 resolved — no vacuous pass):** assertion (i) requires a provisional-bar capability to *exist* in the live build; if WS-2's acts ratify everything, (i) passes over an empty domain — vacuously, the FX-VAC class. Therefore the WS-3 graph includes **at least one capability whose bar is deliberately held at provisional**, designated **at freeze 2, before results**, recorded as a *demonstration control* (not debt) with its lifecycle pre-stated: after the demonstration, the bar is **ratified or the capability retired by act within the phase** — the control never becomes an immortal provisional, per the no-immortal-eligibility rule. The closeout reports it as control, so the honest scoreboard's `built_unverified` line is legible.

**Exit criteria:**
1. **FX-CAP live demonstration** (reclassified per PF-F2 — *a red test that was never red is theater*): on the live build, read by the calibrated extension: the control capability reads **built_unverified — never VERIFIED**; a ratified-bar capability reads **VERIFIED with its `barProvenance` chain intact** from queue act to capability verdict. Recorded as a demonstration with its evidence basis (CP-21).
2. At least one capability reaches VERIFIED **through ratified bars only**, live.
3. **FX-SEAM-B:** full INT-2 per F-04 → green required; **partial** (expected) → honestly RED, precise gap documented, a scoped INT-2 deliverable *proposal* (not authorization) in the closeout.

**Corpus taxonomy, standing:** red-first for mechanisms that do not exist; **integration demonstrations, with recorded bases, for built-but-unexercised mechanisms**; the corpus records each entry's class.

**Claim boundary:** honest capability-level verdicts under provenance — nothing about code quality; no bar is ratified to recover a score, and the deliberate control is the rule's mirror: none is *withheld* to stage a failure either — it is designated, disclosed, and disposed by act.

## 6. WS-4 — the minimal transformer probe

**Objective:** whether a minimal Spec-to-Graph Transformer — candidates + diagnostics, N1-enforcing, honesty-boundary-honoring — produces ratifiable graphs from real prose, on three specifications, against numbers stated before any run.

**Specifications (AR-4a):** **SRS** — *author-contaminated* (the transformer's author hand-authored its slice graph): zero decision weight, labeled. **RLA** — *familiarity-contaminated*: a known, long-running regression target whose content the author has been exposed to throughout the program — supporting evidence only, labeled at its grade, never "uncontaminated." **The external specification is the only genuinely held-out spec and carries the decision weight** — registered per the §14 block (proposed: the NASA cFE requirements document). Held-out reference rule for real Phase-6 untouched; checks derive required/forbidden sets from the spike's ratified slice (a *witness*, used as such) plus the adversarial minimum.

**Denominator channels (PF-OPS-5 resolved — per-spec calibration):** the normative-marker census works on marker-rich formal prose and **systematically undercounts informal specs** ("The system keeps…"). At freeze 3, per spec: the second channel's method is chosen and recorded — marker census for the formal external; **a second independent segmentation pass by a different method** (per ARO §8.2) for the informal RLA/SRS — and **a hand-counted anchor sample** (≈ two pages per spec, **OPS-owned**: instrument calibration, not an authority act, off GP-E) anchors both channels. GP-C disagreements open audits; all resolved before the coverage number is reported.

**Sealed seeding (contamination control):** **OPS seeds the adversarial fixtures** — FX-INVENT, FX-DROP, FX-MISS (the §0 fixture: a miss the transformer's own coverage cannot see), FX-EXAMPLE, FX-AMBIG — into copies of the specs; **placements sealed until evaluation.** The transformer's author never knows where the traps are.

**Review standard (AR-4b — the sampling arithmetic, recorded):** a 10% sample cannot substantiate ≤ 2% on graphs this small — by the rule of three, excluding a 2% rate at ~95% confidence requires ≈ 150 clean samples, more normative assertions than these graphs contain — so sampling is **considered and declined for this probe**: **the architect reviews 100% of generated normative (gating) assertions**, which is simultaneously cheaper than defensible sampling and the standard GP-A already sets for reference artifacts. The misgrounding metric becomes **exact, not estimated**. The screening pass remains as **queue ordering** — the model flags first, the architect reads everything — and flag-vs-review agreement is recorded as free screener calibration. This load counts against GP-E; the §12 calendar is restated accordingly.

**Pre-stated numbers (frozen at freeze 3):** per spec — ungrounded = 0 (schema; a property, not an achievement) · **misgrounded ≤ 2% of normative assertions, computed exactly over the full population under 100% review** · coverage computed with both calibrated channels, all channel audits resolved · all seeded fixtures caught · operator cost (review + ratification + adjudication) within GP-E, pro-rated.

**Evaluation structure:** **independent execution** (OPS — mechanical checks, coverage arithmetic, seal-opening and fixture scoring; not blind, independently executed, valuable as exactly that) · **screening** (ARO agent, full coverage; a model may open findings and only open findings; here it orders the architect's queue) · **100% review + adjudication** (architect: every generated normative assertion read against its cited fragment; the pass claim rests on this complete human basis; load counts against GP-E as WS-1 data).

**Criterion classes (PF-OPS-6 resolved — severity ranked before results):**
- **Invention class — disqualifying for that spec:** ungrounded > 0, misgrounded > 2%, FX-INVENT or FX-EXAMPLE missed. *Rationale: these are the charter's own claim — a transformer that invents fails the thesis, not a threshold.* No re-run cures an invention-class failure within this phase.
- **Completeness class — remediable:** coverage shortfall, FX-DROP or FX-MISS missed. Named; **one recorded re-run of that spec** authorized after a fix; the re-run does not consume the mapping's "one further probe."
- **Diagnostic class — remediable likewise:** FX-AMBIG missed (silent resolution). Same re-run rule.
- **"Pass" for a spec** = zero invention-class failures ∧ completeness/diagnostic classes within bounds or remediated in the single re-run.

**Outcome mapping (binding; AR-4c — one held-out specification licenses a pilot, never scale):** an invention-class failure on **any** spec is disqualifying for that spec — invention is invention at every contamination grade. **Pass on the held-out external** (with RLA passing at its grade, or its failures fully explained) → recorded: *"an **expanded transformer pilot** is authorizable"* — a defined next bounded step: multiple genuinely held-out specifications, held-out evaluation, and either sustained 100% review or a **statistically defensible sampling design at pilot scale** — and **transformation at scale recedes behind that pilot**, additionally gated by ADR-002/ADR-003 and INT-4. External fails on completeness/diagnostic class only → one recorded re-run per the class rules above. External fails invention-class → transformer **deferred**, class recorded; ARO continues as the hand-authored provenance source — a licensed, durable scope, not a consolation.

## 7. Governance parameters

Unchanged: **GP-A** = 10% (100% for reference artifacts) · **GP-C** = any · **GP-D** = 30 days. Set here: **GP-E** — recommended **4 h/week, two sittings ≤ 2 h** (basis: 1.65 h sustained at 6.67 acts/h ≈ 11 acts/sitting ≈ 22/week; the spike slice cost ≈ 12 acts; WS-3 fits in ≤ 2 budget-weeks with headroom for audit acts, which GP-E now includes). **GP-B** takes its first value from WS-1 branch (ii) evidence if it obtains. Probe thresholds stay phase-local (§6) — no parameter minted for a one-phase number.

## 8. INT-4, the verdict, and the decision this phase tees up

**INT-4 — capability-boundary ownership:** the permanent rule for who defines the capability set and boundary oracles when a projected package meets the factory, including the conflict discipline. **ARO agent drafts (Stage D); DEV and OPS review; architect ratifies.** Until then the §5 interim pin holds, and **no transformer-derived capability content reaches the factory** — INT-4 gates the scale-authorization act alongside ADR-002/003.

**Stage D closeout** (canonical idiom): precondition 1 — branch and numbers, category-(c) cost only; precondition 2 — the mapped branch with the residual bound restated at the final effective N, full distribution vs. baseline; precondition 3 — the demonstration record (control disclosed and disposed), FX-SEAM-B state, capability-grain evidence; WS-4 — per-spec, per-class results against frozen numbers, contamination labels intact, seals verified; the INT-4 draft; **the scoreboard with provenance breakdown — every point of recovery traced to its ratification act.** Then **one decision**, teed up and not performed: whether to authorize the **expanded transformer pilot** — the scale act now recedes behind that pilot, and behind ADR-002/ADR-003 and INT-4 — evaluable for the first time against stated preconditions and real rates.

## 9. Honest limits

Single operator; N = 5 per build question (class signals, not fine rates — residuals stated, §4); SRS probe result weightless by contamination; spike-proven representation (ADR-003 unresolved, still a full-program gate); the re-pin rests on a consistency attestation, assumed by act; the misgrounding screen can only open findings — the rate claim rests on complete human review of every generated normative assertion, which also checks the screener; FX-SEAM-B may stay honestly RED on a partial F-04; the demonstration control is disclosed staging, disposed by act; red-first is for mechanisms that do not exist; every scoreboard states its basis; the 0.89→0.33 drop was the ruling working — nothing here buys the old number back, and anything that rises must be shown to have been **earned**.

---

# PART II — IMPLEMENTATION PLAN

## 10. Stage task tables (effort figures are estimates, trued in the record)

**Stage A — unblock (week 1)**

| # | Task | Owner | Deliverable | Verified by | Est. |
|---|---|---|---|---|---|
| A1 | Ratification act (§14) incl. GP-E, decision (a), external spec | Architect | signed instrument in decision record | — | 1 act |
| A2 | Chain attestation (consistency scope) + F-04 answer | DEV | attestation doc | Architect reads; re-pin act A3 | 0.5 d |
| A2b | **Compatibility comparison (AR-3):** three surfaces, spike-recorded outputs vs v0.4.9 | OPS runs; DEV triages diffs | comparison record | all diffs ruled-expected or adjudicated | 0.5–1 d |
| A3 | Re-pin act (closure over A2 + A2b; residual assumed) | Architect | dated act | display duties in act | 1 act |
| A4 | ARO v0.5.3 (re-pin, projector rule, F-06) | ARO agent | v0.5.3 | Architect ratifies | 0.5–1 d + 1 act |
| A5 | Act tool: recording + CLI `--json` + 0/1/2, read-only; queue presentation redesign | ARO agent | tool + short usage note | Operator dry-run on a replayed spike batch | 1–2 d |
| A6 | F6(a) closure draft (field types; examples as rationale) — **payload for the AR-2 transport proof**; if severed, a minimal synthetic typed declaration substitutes (one act) | ARO agent → Architect | ratified closure | 1 act | 0.5 d + 1 act |
| A7 | Re-projection under (a) | ARO agent | package + manifest | byte-identical re-run | 0.5 d |
| A8 | **Freeze 1** (checklist §11.1, incl. **the AR-2 transport proof green**) → F2-verification build, N = 5 | OPS | run record + full class distribution | protocol conformance | 1 d |
| A9 | **WS-3 target naming act (REC-1):** title/region + source digest, from agent candidates — before Stage B | Architect | dated act | freeze-2 cross-check | 1 act |

**Stage B — capability grain (weeks 2–3)**

| # | Task | Owner | Deliverable | Verified by | Est. |
|---|---|---|---|---|---|
| B1 | Instrument extension (ledger + `barProvenance` + capability verdict reader) | OPS | extension | **calibration: reproduces Q1/Q2/Q5 + AL synthetic verdicts**; DEV format review | 1–2 d |
| B2 | WS-3 graph extension: capabilities + acceptance clauses; control candidate proposed | ARO agent | graph + queue batch | spans beside assertions | 2–3 d |
| B3 | Ratification sitting(s) via tool (WS-1 data) | Architect | acts | tool record | 1–2 sittings |
| B4 | Projection + handoff | ARO agent | package | re-projection check | 0.5 d |
| B5 | **Freeze 2** (checklist §11.2, control designated) → capability build + FX-CAP demonstration + SEAM-B attempt | OPS | demonstration record; F2-sample addendum | calibrated extension only | 1 d |
| B6 | Control disposition (ratify or retire, by act) | Architect | dated act | closeout cites it | 1 act |

**Stage C — transformer probe (weeks 3–4; C1 may start during Stage B)**

| # | Task | Owner | Deliverable | Verified by | Est. |
|---|---|---|---|---|---|
| C1 | Minimal transformer (candidates + diagnostics; N1; honesty boundary) | ARO agent | transformer + self-test | fixture dry-run on synthetic prose | 4–6 d |
| C2 | Spec prep: copies, **sealed seeding**, per-spec channel choice, hand-count anchors (~2 pp/spec) | OPS | sealed placement record + calibration note | seal opened only at C5 | 1–1.5 d |
| C3 | **Freeze 3** (checklist §11.3) → three runs | ARO agent (runs) | candidate graphs + diagnostics | manifest digests | 0.5 d |
| C4 | Screening pass (full coverage; findings only) | ARO agent | flag set | — | 0.5 d/spec |
| C5 | Independent execution: mechanical checks, seal-opening, fixture scoring, coverage arithmetic | OPS | evaluation record | frozen numbers | 1–2 d |
| C6 | **100% review of generated normative assertions** (screen-ordered) + adjudication | Architect | review record + acts | tool record; counts in GP-E | 3–4 sittings |
| C7 | Re-run(s) if completeness/diagnostic class only, per §6 | as C3–C6 | recorded re-run | same seals discipline, fresh placements | as needed |

**Stage D — verdict (week 5)**

| # | Task | Owner | Deliverable | Verified by | Est. |
|---|---|---|---|---|---|
| D1 | Affordability computation (tool export; category-(c) cost only) | OPS + tool | numbers | WS-1 mapping | 0.5 d |
| D2 | INT-4 draft | ARO agent | rule draft | DEV + OPS review | 1 d + reviews |
| D3 | Phase closeout (canonical idiom; provenance-broken-down scoreboard; residual bound at final N) | ARO agent drafts | closeout doc | Architect accepts | 1 d + 1 act |
| D4 | INT-4 ratification · the tee-up decision placed (not performed) | Architect | acts | — | 2 acts |

## 11. Protocol-freeze gate checklists (verbatim gates; a run may not start until its list is initialed in the record)

**11.1 Freeze 1 — F2 verification:** classifier version pinned · **class taxonomy frozen and versioned** (no class redefined after results) · shipped-configuration digest recorded · spike baseline table attached (F2 4/5, F7 1/5, D 1/5) · N, workspace, and SRS digest pinned · mapping branches (§4) restated in the protocol · **AR-2 transport proof executed and green** (one typed signature end-to-end with provenance intact; consumer-side failures owned by DEV) · **AR-3 compatibility record attached** (three-surface pre/post comparison; every diff ruled-expected or adjudicated).
**11.2 Freeze 2 — capability build:** instrument-extension **calibration record attached** (synthetic verdicts reproduced) · **demonstration control designated** (which capability, why, lifecycle: ratify-or-retire by act) · both FX-CAP assertions stated as executable checks against the extension's output · SEAM-B expected state per F-04 recorded · **the WS-3 target matches the A9 naming act (title + digest)**.
**11.3 Freeze 3 — probe:** per-spec second-channel method recorded · hand-count anchors attached · **sealed placement record lodged** (OPS custody; opened only at evaluation) · criterion-class ranking attached · the frozen numbers (§6) restated · contamination labels (SRS) restated · re-run rule restated.

## 12. The operator's calendar (predicted acts and sittings — your whole commitment, visible before you sign)

| Stage | Your acts | Est. time |
|---|---|---|
| A | ratification act · re-pin act (over attestation + compatibility) · v0.5.3 act · F6(a) act · **WS-3 target naming act** (5 acts, batchable in one sitting) | ~1–1.5 h |
| B | WS-3 queue (est. 20–30 acts, tool-assisted) · control disposition | 1–2 sittings (≤ 2 h each) + 1 act |
| C | **100% review of generated normative assertions** (screen-ordered) + adjudication, three specs | 3–4 sittings |
| D | closeout acceptance · INT-4 ratification · tee-up decision (separate act, your timing) | ~1 h |
| **Total** | **≈ 7–9 sittings across 5 weeks** | **≈ 14–18 h of the GP-E 20 h envelope — margin reduced by the 100% review standard, and stated** |

Starvation category (a) between your sittings is the design working; only category (c) counts against affordability. One sentence of qualitative check-in per sitting, recorded — that sentence is WS-1 data of the first rank.

## 13. Artifact inventory at phase end

Signed instrument + all dated acts (decision record) · attestation + re-pin act · ARO v0.5.3 · act tool + usage note · re-projected package + manifests · freeze records 1–3 with initialed checklists · F2 run record + class distribution + residual statement at final N · instrument-extension calibration record · capability build + FX-CAP demonstration record + control disposition act · SEAM-B state (green, or gap + INT-2 proposal) · three candidate graphs + diagnostics + sealed-placement record + evaluation records + adjudication/audit records · WS-1 rate tables + starvation taxonomy log + qualitative check-ins · INT-4 draft + reviews · the Stage D closeout with the provenance-broken-down scoreboard.

---

## 14. Executed ratification instrument

> **Act 1 — External specification: REGISTERED.** I register the visible-title artifact *core Flight Executive Software Requirements Specification*, Version 5.1, dated November 20, 2017, from the `nasa/cFE` repository at `docs/cfe requirements.docx`. The repository snapshot is release tag `v7.0.1`, pinned commit `c5fb2b4d540bd55eb6c3707da7dd13eee679d4dd` ([immutable commit permalink](https://github.com/nasa/cFE/commit/c5fb2b4d540bd55eb6c3707da7dd13eee679d4dd)); the registered source file is available at its [commit-pinned permalink](https://github.com/nasa/cFE/blob/c5fb2b4d540bd55eb6c3707da7dd13eee679d4dd/docs/cfe%20requirements.docx). Source repository: [https://github.com/nasa/cFE](https://github.com/nasa/cFE). License: Apache License 2.0 (`Apache-2.0`) under the repository-level LICENSE at the pinned commit; no file-specific exception was observed. Original DOCX SHA-256: `54EB19F20030F87E0E12CDDA59B9CF36E2FE54D1E875427564ACA3B1495BCF7D`; Git blob SHA-1: `55eb0ad80ae607b25fb0c968ece8cc4ba4c06402`; original file size: `292251` bytes. These are the two recorded source digests. The original DOCX is the registered source. Any derived text extraction must be separately registered at Freeze 3 with its source digest, extraction method and version, normalization profile, and SHA-256. — **Aaron Anthony Damiano, September 14, 2026**
>
> **Act 2 — Provenance Foundation Phase Plan v1.1: RATIFIED.** I adopt this plan. Its ratification constitutes the new authorization contemplated by the spike closeout, which remains closed and unmodified. The authorized measurement programs are the F2-verification program, the capability program (build plus FX-CAP demonstration with its designated control), and the transformer-probe program; execution counts are governed by the Part II freeze checklists, and no execution starts unfrozen. The AR-2 transport proof and AR-3 compatibility record are preconditions of Freeze 1; the A9 target-naming act precedes Stage B. **GP-E = 4 hours/week**, structured as two sittings of no more than two hours, provisional and calibrated at Stage D, inclusive of the 100% review standard. **Boundary decision (a) is adopted:** typed content crosses through the declaration channel, `plan.json` remains deliverables-only, F1 is settled in design and proven at Freeze 1, and v0.5.3 carries the rule. The re-pin to CP/SM v0.4.9 is my closure act over DEV's consistency attestation and the OPS compatibility record, with the unaudited residual expressly assumed. The external specification is registered by Act 1 above. The WS-3 capability target is named and digested by the A9 act before Stage B. INT-4 is assigned under §8 and gates the pilot-and-scale ladder. All review findings PF-F1..PF-F5, PF-O1, PF-OPS-1..PF-OPS-6, AR-1..AR-5, and REC-1 are dispositioned in §15. The outcome mappings of §§3–6 and the criterion-class ranking are binding as pre-stated; measurement follows prediction. Transformer success licenses at most an expanded pilot. Transformation at scale is expressly not granted and remains reserved to future acts behind that pilot, ADR-002, ADR-003, and INT-4. — **Aaron Anthony Damiano, September 14, 2026**

## 15. Change log

**v1.0 → v1.1 (final, amended), basis: the architect's pre-signature review.** **AR-1:** the instrument's blank replaced by a **registration block** with an invalid-while-empty rule; concrete candidate proposed (the NASA cFE requirements document, `nasa/cFE`, Apache-2.0 under the cFS release, confirmed at registration); the digest remains a registration-time field by necessity — it hashes the architect's registered copy. **AR-2:** "F1 settled" demoted to *settled in design*; the **freeze-1 transport proof** added — one typed signature end-to-end with provenance intact, F6(a) as payload (synthetic fallback if severed), consumer-side failures owned by IA DEV, the F2 program gated on the proven channel. **AR-3:** the re-pin's basis made three-part and typed — consistency (attested) + **compatibility (measured**: three-surface pre/post comparison replaying spike-recorded consumption, diffs ruled-expected or baseline-blocking**)** + residual (assumed by act); task A2b and checklist 11.1 amended. **AR-4:** (a) RLA relabeled *familiarity-contaminated* — a known regression target is not held-out; the external is the only genuinely held-out spec and carries the decision weight; (b) sampling **considered and declined with the arithmetic recorded** (rule of three: excluding 2% at ~95% needs ≈150 clean samples — more than these graphs contain); the probe standard becomes **100% architect review of generated normative assertions**, metric exact, screening demoted to queue ordering with flag-agreement recorded; calendar restated with reduced, stated margin; (c) the mapping's ceiling corrected — **one held-out spec licenses an expanded pilot, never scale**; the scale act recedes behind the pilot, ADR-002/003, and INT-4; §8's teed decision updated accordingly. **AR-5:** "exactly three runs" corrected to **three measurement programs** whose execution counts are governed by the freeze checklists — which is what was always true. **REC-1 (adopted):** the WS-3 capability target is named and source-digested by a dated Stage-A act (A9) before Stage B; freeze 2 cross-checks it.

**v0.2 → v1.0**, basis: the OPS review. **PF-OPS-1:** the F2 discharge typed to N=5's power — "resolved for this phase's purposes," residual ≤ ~0.2 stated, 1/5 disambiguated by cause signature, recurrence routes without impeaching; *(authored)* the WS-3 build recorded as a zero-cost additional sample, residual restated at final N. **PF-OPS-2:** the demonstration control — designated at freeze 2, disclosed as control, *(authored)* lifecycle pre-stated (ratify-or-retire by act; no immortal provisional). **PF-OPS-3:** the OPS instrument extension with *(authored)* calibration against the existing Q1/Q2/Q5 + AL synthetic corpus as the known-answer set; self-attestation named and forbidden. **PF-OPS-4:** the three-way starvation taxonomy; only critical-path blocks cost. **PF-OPS-5:** per-spec channel calibration at freeze with *(authored)* OPS-owned hand-count anchors (off GP-E) and *(authored)* OPS-owned sealed fixture seeding (the transformer's author never knows the placements). **PF-OPS-6:** criterion classes ranked before results — invention disqualifying (it is the charter's claim), completeness/diagnostic remediable with one recorded re-run. **Closing observation folded (§0, §8):** score recovery must be legible as earned — every point traced to a ratification act. **Part II added** per the architect's direction: stage task tables, the three freeze checklists as literal gates, the operator's calendar, the artifact inventory.
**v0.1 → v0.2** (factory-side review): retained as recorded in the superseded draft — PF-F1 attestation honesty; PF-F2 FX-CAP reclassified (a red test that was never red is theater); PF-F3 layered evaluation; PF-F4 full-distribution protocol; PF-F5 GP-E = 4 with basis; PF-O1 interim pin + INT-4; the three interface requirements.

---

## 16. Independent review attestation

I reviewed the complete public edition against every condition previously raised during the v0.1, v0.2, v1.0, and v1.1 reviews; verified that the external-source registration is self-contained and commit-pinned; checked that GP-E is fixed at 4 hours/week without placeholder brackets; confirmed that the executed Acts 1 and 2 are attributed to Aaron Anthony Damiano and dated September 14, 2026; confirmed that the document distinguishes its CC BY 4.0 publication license from the NASA source's Apache-2.0 license; and audited the publication text for unresolved placeholders, local filesystem paths, mutable pending-file references, and the superseded sampling language.

**Attestation:** On the complete document and evidence available at the publication freeze, every condition I previously raised is satisfied and no other condition remains open. Any condition discovered after the content digest is issued is a finding against this review attestation and does not retroactively alter Aaron Anthony Damiano's ratification acts.

— **OpenAI Codex, independent review assistant, September 14, 2026**
