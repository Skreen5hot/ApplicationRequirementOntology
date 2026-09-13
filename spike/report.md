# ARO Phase-1.5 spike -- canonical closeout (2026-09-13)

**Status:** the spike is CLOSED. This document is the canonical record. It consolidates Ops' comparative report
(IntegratedAgent `3a13d0f`, `experiments/comms/OPS-2026-09-13-spike-comparative-report.md`) with the verified
outcomes of F6, F7, F7b and F7c that followed it, and it SUPERSEDES the Arm B report of 2026-09-11, which is kept
below as Part II, byte-identical, because its findings register (F-01..F-20), its Spike-2 measurement and its
verify commands remain the record of what the ARO side did. Where Part I and Part II disagree, Part I governs.

**Governing text:** ARO v0.5.2 section 16 (Phase 1.5: Arm 0 precondition, two arms, outcome mapping "recorded
before measurement, and binding once stated"), with Amendments 1 and 2 (`docs/decisions/2026-09-10-phase-1.5-
amendments.md`). **Written by:** the ARO dev agent, from the committed record on both repositories; the arm
measurements are Ops' (coord-j), taken blind to this side, and are cited, not re-derived. **No runtime, graph,
ontology or projection was changed to produce this document.**

---

## 0. The verdict in one paragraph

The seam-flip class was LIVE at baseline (Arm 0: drift 3/5) and Arm A alone killed it (original Arm A 0/5;
the control that removed only Arm A's declared-seams block put it back at 4/5), so the pre-stated mapping's
first branch applies verbatim: **ship A into the loop immediately, regardless of ARO -- ARO's license rests on
the faithfulness/N1/provenance incident class.** Arm B also killed the flip (0/5 in every projected
configuration) but on the seam axis that adds nothing A did not already earn. What Arm B DID earn is the
incident class the mapping names: F-14 (every seam name in the founding plan is an N1 invention; the seam is
not in the source), F3 (a ratified declaration never reaching the test author), F6 (a producer inventing a
type the ratified declaration does not state) and, downstream of them, F7/F7b/F7c (a provisional bar
behaving as an acceptance gate; the authority ledger recording VERIFIED from `built=True`). Every one of those
is now a verified mechanism in the factory that fails closed on absent or unratified provenance. The spike
therefore licenses ARO's provenance role and does NOT license the full program on this evidence; section 9
states the recommendation and its preconditions.

## 1. What the spike asked, and the mapping it is judged against

Section 16, quoted at the level that binds:

- *Class live -- A alone kills -> ship A into the loop immediately, regardless of ARO; ARO's license rests on
  the faithfulness/N1/provenance incident class.*
- *B kills and A does not -> the strongest license; the full program proceeds.*
- *Neither -> a third cause exists; escape-protocol triage before either investment.*
- *Spike 2 measures a rate, not a count: ratification acts required by Arm B, and sustained acts per hour
  actually achieved, with starvation incidents recorded. The Phase-4 entry condition is required-acts divided
  by achieved-rate against the calendar budget.*
- *Duration bound: one to two days; exceeding it is itself a finding.*

The arms' kill-interpretation was void until Arm 0 ran. Arm 0 ran (Ops, `e0ca050`), after Part II was first
closed; Part II section 2 ("no Arm 0 record exists") is therefore superseded by section 2 below.

## 2. Arm measurements -- every arm, one instrument, one protocol

Ops' frozen protocol for every arm: pinned SRS `sha256:2428b115...9450`; fresh workspace, fresh empty
`--standards-dir`, fresh `--runs-dir` per run; `--driven --install-deps --model sonnet`; **N = 5 fixed, no run
excluded, nothing repaired during a batch**; one instrument (`capture.py`) and one read-only counter
(`count_run.py`) applied identically. "Drift" = the invented `getFindings` reaching a bar or a build in place of
the declared `listFindings` family. Records: `C:\Users\coord\Documents\aro-spike\{arm0, armA-control, armA,
armB, armB-postF3, armA-namesonly}` (Ops-side, outside this repository by design).

| arm | code | what the test author received for a dependency | drift (bar or build) | author-agent verified | dominant author-agent stub cause | real_work mean |
|---|---|---|---|---|---|---|
| **Arm 0** (baseline) | `e0ca050` | nothing structured (model-proposed plan, independent derivation) | **3/5** | 2/5 | -- | -- |
| **Control** (Arm A minus `declared_seams`) | `886ef2e` | Arm A's derivation without the seams block | **4/5** | 1/5 | -- | -- |
| **Arm A, original** | `f827459` | member names + params, stated as exact (unratified) | **0/5** | **5/5** | -- | 0.40 |
| **Arm A, names-only** (post F3 ruling) | `e8a0353` | unratified member NAMES only, NON-NORMATIVE, shapes withheld, bar PROVISIONAL | **0/5** | 1/5 | withheld-params call-shape misuse 3/5 (-> F7) | 0.17 |
| **Arm B, pre-F3** | `f827459` runtime | graph-projected plan `243eef68`, ratified declarations reaching developer briefs only | **0/5** | 1/5 | F3 `source` missing 3/5; F2 | -- |
| **Arm B, post-F3** | `e8a0353` | as above, ratified declarations reaching the test author too | **0/5** | 0/5 | F6 invented `replay` type 4/5; F2 (contract 5/5, store 3/5, author-agent 1/5) | 0.10 |
| **Arm B, post-F6(b)** (outside the spike, per the F6 ruling) | `d215c65` | as above; producer told an unratified type is not enforceable | 0/5 | 1/5 | **F2 + strict type gate, and nothing else** (4/5); F6 class 0/5 | 0.40 |

Two facts about the instrument itself:

- **SYSTEM VERDICT was BLOCKED in all 35 spike runs** (`oracle cover 0.00`, `G2: unprovable`) and in every run
  since. It never discriminated an arm; it measures steady-state non-certifiability, not the seam.
- Original Arm A's 5/5 is preserved for its original configuration and does NOT carry over (operator ruling,
  2026-09-13): under the names-only rule the same plan gives 1/5, and the difference is exactly the withheld
  parameters. The kill (0/5) survives the ruling; the build win does not.

## 3. The findings ladder the spike surfaced, and how each closed

The spike's value was not the seam number. It was a ladder of one-level-down failures, each found only because
the level above had been closed, each verified independently by Ops against its pre-fix revision.

| finding | class | disposition | where verified |
|---|---|---|---|
| **F-14** the seam is not in the source (every seam name and two of three modules are N1 inventions) | faithfulness / N1 | **stands**; adjudication C chosen by the architect; the graph carries the seam as ratified L3 with its N1 origin explicit | Part II sections 0, 9 |
| **F-16** plan renders `listFindings` returning the truncated `Finding[` as binding | founding-input corruption | **fixed loop-side** (IA-PLANSIG, `7920e60`): a corrupt plan signature is REFUSED at load, never rendered as binding | IA `tests/test_plan_signature_integrity.py` |
| **F1** projected typed `signatures[]` dropped by the loop's schema; builders recovered types from prose | package-to-loop boundary | **open** (see section 7); no stub traced to it | `OPS-2026-09-12-armb-result.md` |
| **F2** `files` lists `tests/<m>.test.ts`; the loop treats listed files as deliverables and type-checks them | package-to-loop boundary | **unresolved, unowned** (section 7) | every Arm B batch |
| **F3** the ratified `Finding` declaration reached developer briefs and never the test-author brief; author-agent stubbed on the field it was never told about (3/5) | provenance seam | **CLOSED**: operator ruling -- a declaration reaches the test author as normative only when source-grounded and ratified; unratified member names only, non-normative; an oracle-gap diagnostic names withheld semantics. Post-F3 Arm B: class **3/5 -> 0/5** | `OPS-2026-09-13-postf3-armb-result.md`; ledger `f3-testauthor-underbriefed` |
| **F4** the graph's seam note quoting `getFindings` rendered into every brief | leak, unconsumed | recorded; 0 consumption in 5 runs; not scrubbed (censoring plan text was judged worse) | `OPS-2026-09-12-armb-result.md` |
| **F5** `fragments.py --verify` raised `PermissionError` on an ACL-denied source instead of reporting the lapse | package, minor | **fixed** on this branch (`0df3d86`); source path parameterized (`ARO_SOURCE_DOC`, `0face74`) so Ops can verify independently; six projected digests unchanged | this repository |
| **F6** the store invented and enforced `replay: string`; the ratified declaration states field NAMES only; author-agent stubbed on it 4/5 | ratification gap (one level below F3) | **remedy (b) VERIFIED** (`d215c65`): producer-invented `typeof` on any ratified field **0/5** (was 4/5); typed-field `FindingValidationError` **0/5** (was 4/5); F3 class still 0/5. **Remedy (a) DEFERRED** (section 8) | `OPS-2026-09-13-f6-verified.md`; ledger `f6-verify` |
| **F7** under the names-only rule a provisional bar guessed the call shape wrong 3/5 and the module STUBBED on a probe | provisional bar as gate | **ruled and VERIFIED** (`05c0f0f`): a provisional bar is an observational probe -- pass or fail it cannot verify, classify implementation failure, redispatch, burn retry budget or stub; the artifact is kept and graded `built_unverified / oracle_gap`; ratified bars keep full authority. Ops 9/9, four F7-dependent probes fail pre-fix; live RLA: provisional-only store 0.00 real / 1.00 exists, repo store 0.33 / 1.00, no stub, no retry | `OPS-2026-09-13-f7-verified.md` |
| **F7b** the probe branch was narrowed to `fault == implementation`; the class F7 was priced on (a THROW from a `src/` frame, `fault: unknown`) still stubbed | enforcement gap in F7 | **VERIFIED** (`b210841`): the classifier's own predicates exposed (`module_threw_under_test`), consulted under a provisional bar only; classifier output unchanged; ratified path untouched. Ops 12/12, P9 falsified pre-fix | `OPS-2026-09-13-f7b-verified-closed.md`, `-f7b-verified.md` |
| **F7c** three rung consumers did not know `built_unverified`; the AUTHORITY ledger recorded `UnitVerified` on any `built=True` BEFORE the grade, so a provisional pass read VERIFIED at the capability level and a provisional throw read stub (dependents inherited debt) | provenance at the authority record | resume + rank **fixed** (`a48bc32`); the authority ledger **ruled** (adopt (a)+(b), vocabulary closed) and **BUILT** (`6e93e63`): grade-boundary seam; `UnitVerified` = exactly "passed a ratified bar", carrying `barProvenance`; every other rung recorded with `graded`; the reader accepts only explicit `provisional: False` and fails closed as "authority not demonstrated". **VERIFIED** twice (manual `ccc6cca` 5/5; daemon `ad521ad` 7/7; Q1/Q2/Q5 fail pre-fix; ratified behaviour identical) | `OPS-2026-09-13-f7c-verified-closed.md`, `-f7c-reactive-verified.md` |

Also closed on the way, outside the spike's arms but inside its arc: `pipeline-floor` (a provisional pipeline
bar retired; a source-grounded string-only-totality bar ratified, `da0af853`); `parser-redraw` (a spec-grounded
parser bar authored, verified 6/6, ratified, `e128f728`); two whitespace assertions (SRS `ledger`, RLA `parser`)
ruled model-authored overreach and retired, with the instruction never to modify the executor to satisfy an
invented constraint; and `ratified-bar-durability` (ratified bars are tracked repository content; provisional
model bars are not; Ops' adversarial material stays outside the shared repository).

## 4. Human ratification cost -- the rate, as the spec demanded it be measured

**Spike 2 (this repository, `spike/measurements/rate.py` over the queue and starvation logs; Part II section 5):**

| measure | value |
|---|---|
| required acts (records queued, not superseded) | **11** (five L2 records, three L3 closure bundles, the layout convention and rule, one adjudication) |
| assertions bundled / ratified | **28 / 28** (2.55 per act) |
| sitting | one, 2026-09-11 05:00-06:39, **1.65 h** |
| working rate | **6.67 acts/h** |
| calendar rate (queue opened 2026-09-10 16:04, measured to 06:39 next day) | **0.754 acts/h**; **14.58 h** to clear |
| starvation incidents | **2** (`sv-001`, `sv-002`), each closed at a session end with "no act received" |
| individual act times | **not kept** (F-20); the sitting's bounds are the architect's own statement |

**The factory side of the same arc (IntegratedAgent `experiments/comms/OBLIGATIONS.md`):** nine ledger rows
owned by the operator, every one a human act -- three ratification acts (`pipeline-bar-ratify` YES, with an
explicit source anchor; `executor-floor-ratify` NO to two whitespace assertions the source never imposed;
`parser-redraw` directing a spec-grounded bar), three repository/record decisions (`ratified-bar-durability`,
`tracked-index-rewrite`, `armb-canonical-source`), one scheduling call (`armb-severity-call`) and two policy
rulings (`f3-arm-a-conflict`, `f6-field-type-ruling`) -- plus three rulings recorded only as relayed documents
(pipeline-floor `cc000d0`, F7 `0935ddd`, F7c `a4aef4f`). Twelve operator acts on the record in three days,
none of which the agents could perform, batch or simulate, and none of which were.

**Reading it against the Phase-4 entry condition.** The spec says the human is the scarce resource and that a
count extrapolates badly, so this is an illustration, not a projection: at the measured calendar rate, a real
specification's "hundreds of Specification Records" (spec section 16, operator-load risk) is on the order of
**hundreds of calendar hours**, or tens of working hours if sittings could be sustained at 6.67 acts/h -- which
one sitting of 1.65 h does not demonstrate. **No calendar budget has been stated by the architect**, so the
entry condition cannot be evaluated; that absence is itself the first precondition in section 9.

## 5. Provenance conclusions

1. **Names reaching the consumers is what kills the seam flip -- in either arm.** Arm 0 3/5, control 4/5,
   every configuration that carried the declared member names 0/5 (Arm A original, Arm A names-only, Arm B in
   all three states). The graph is a sufficient source of those names; it is not a necessary one.
2. **The graph found what the extracted slice cannot see:** F-14 (the founding plan's seams are inventions;
   the source has no such API), F3 (the ratified declaration existed and was not delivered to the one consumer
   that needed it) and F6 (a type nobody ratified was enforced as if someone had). These are the
   faithfulness/N1/provenance incidents the mapping names as ARO's license, and each one was ratified or ruled
   by a human on the strength of a span-cited record.
3. **"Ratified" now has teeth in the factory, and it needs a source.** The F3/F6/F7/F7c mechanisms are
   loop-side and graph-independent, but each one keys on provenance -- `record` on a declaration, `provisional:
   False` on a bar, `barProvenance` on the authority ledger -- and fails closed without it. A provisional bar
   is a probe; an unratified type is neither invented nor enforced; `UnitVerified` means a ratified bar passed
   and a historical record without provenance is "authority not demonstrated". The graph's ratification queue
   (section 4) is the only process in this program that produces ratified declarations at scale; the factory
   without it produces `built_unverified` and BLOCKED, honestly.
4. **Conformance credit fell when honesty rose, and that is the ruling working.** The RLA proactive baseline
   moved from `real_work ~0.89` to **0.33 / code_exists 1.00 / BLOCKED** (parser and pipeline on ratified bars;
   contract and analyzer built-unverified on provisional ones). The operator directed that contract and
   analyzer bars NOT be ratified merely to recover the old score; ratification stays a separate,
   source-grounded act.
5. **Arm A versus Arm B on build outcome is not a fair contest on this slice** (Ops' own reading, adopted):
   Arm B's extra stubs are F2 and F6 -- package-to-loop interop and a ratification gap -- that Arm A's looser
   producers and `src/`-only plan never trigger. On the one axis the spike was designed for they tie at zero.

## 6. Limitations, stated so the conclusions are read for what they cover

- **N = 5 per arm, one slice, one seam, one source.** The findings-store read API of one SRS section. Nothing
  here says how the rates behave on a second seam or a second specification.
- **Order.** Part II was closed before Arm 0 existed; Arm 0 ran afterwards. The mapping's precondition is
  met, but by the record, not by the sequence the spec intended.
- **SYSTEM VERDICT never discriminated** (BLOCKED in every run); `real_work` did, and it is now on a different
  scale than the pre-F7 numbers (item 5.4), so pre- and post-F7 means are not comparable.
- **The two Arm A configurations are not the same policy.** Original Arm A stated unratified params as exact
  (later ruled out); names-only is the surviving configuration. Its 1/5 build win was then repriced by F7 --
  which was fixed AFTER the spike stopped and is measured only on the non-graph RLA smoke, never re-measured on
  the Arm A plan (no new arm, by direction).
- **F2 confounds every Arm B build outcome** from post-F3 onward; the seam result is unaffected, the build
  result is not interpretable as a graph result.
- **The RLA plan has 0 capabilities**, so F7c's capability view -- the part the ruling was about -- is
  exercised live only through the authority ledger's payload, not through a capability verdict.
- **Ops' batch records and adversarial fixtures are outside this repository** by design; the numbers above
  are cited from their committed verdict documents, which name the record paths.
- **Individual act times were not kept** (F-20); the working rate is one sitting's bounds.
- **The L2 graph is a hand-authored slice**, not a transformation; detected-clause coverage (ARO section 8.2)
  was not computed; no upper-ontology import; the full SHACL suite was not run for the spike (nothing touched
  the ontology scope) and was not run for this closeout either (nothing touched it).
- **Duration bound exceeded** (Part II section 12: ~80 minutes of agent time across a 15 h calendar span, most
  of it the queue waiting for a human) -- itself a finding, and the direct form of section 4's rate.

## 7. Unresolved: F2, the package-to-loop boundary

The projected `plan.json` lists `tests/<module>.test.ts` under each unit's `files`; the loop treats every listed
file as a deliverable and type-checks it at the module gate, while the factory's own bar lives elsewhere
(`coord-tests/`). Arm A (`files` = `src/` only): 0 such errors in any run. Arm B: `contract` 4/5 then 5/5,
`store` 3/5 -> 4/5, `author-agent` 1/5 -> after F6, **every remaining author-agent stub (4/5) is F2 plus the
strict type gate and nothing else**. It is the dominant Arm-B-only stub cause and the reason section 5.5 holds.

It is unowned because it is a decision, not a defect, and it sits on a boundary both sides declined to move
unilaterally: the loop's behaviour is documented and Arm A never triggers it; the projection's `files` follow
adjudication C and the layout convention rq-001 the architect ratified. The two readings on the table --
(a) the projector emits deliverables only (`src/`), with the bar's location carried elsewhere in the
projection; (b) the loop's `files` contract admits declared test files as non-deliverables -- are the
architect's and the operator's to choose between; neither was taken. Until it is, Arm B build outcomes stay
uninterpretable as graph outcomes. F1 (projected typed signatures dropped by the loop schema) is the same
boundary, one field over, and would be settled by the same decision together with F6 remedy (a).

## 8. Deferred: F6 remedy (a)

The operator's ruling, verbatim: *"Remedy (a) is deferred. The graph team may later propose explicit field
types as an L3 design closure, but those types become normative only through a separate, deliberate
ratification act."* Remedy (b) is verified (section 3). The factory side is ready for (a): the proof that a
RATIFIED type constraint is enforceable while an absent one is neither invented nor enforced is pinned
(`tests/test_f3_ratified_provenance.py`, the F6 rule), and the brief boundary renders ENFORCEABLE versus NO
RATIFIED TYPE from the declaration's own content. What (a) requires of this repository is one L3 closure
carrying `Finding`'s field types with span citations (F-19 records that the source states the field set only
by two literal examples, `replay` in one), one ratification act, and a re-projection -- and the standing
instruction that no such type be inferred from an example. Not proposed here; recorded as the next
graph-side act if the architect wants it.

## 9. Recommendation -- go / no-go, against the mapping as pre-stated

**On the seam metric: the mapping's first branch, applied as written.** Class live (Arm 0 3/5); A alone kills
(0/5; control 4/5). Arm A's mechanism -- declared member names reaching every consumer, under the F3 ruling's
names-only, non-normative form -- **is shipped in the loop and stays.** No further license for ARO flows from
the seam number, and none is claimed.

**On the faithfulness/N1/provenance class: GO, bounded.** Recommend that ARO proceed **as the ratified-
provenance source for the factory's provenance boundaries** -- the graph's ratification queue producing the
declarations and bars that `record`, `provisional: False` and `barProvenance` now demand -- and that this be
the program's next measured step rather than the full transformation. The evidence for it is F-14, F3 and F6:
three real incidents of the class the mapping names, each caught by a span-cited record and closed by a human
act, none visible to the extracted slice. That evidence is one slice deep.

**On the full program (Phase 2 onward, transformation at scale): NO-GO on this evidence**, for three reasons
that are each a precondition, not a verdict on the ontology:

1. **The Phase-4 entry condition cannot be evaluated** -- there is no stated calendar budget to divide the
   required acts by. The measured rate (0.754 calendar acts/h; two starvations in 14.6 h; one 1.65 h sitting)
   is the only number, and at that rate a real specification is hundreds of calendar hours. **Precondition:
   the architect states the budget.**
2. **The package-to-loop boundary is undecided** (F2, F1, and F6 remedy (a) sit on it), so every Arm B build
   number is confounded. **Precondition: one decision, (a) or (b) in section 7, taken by the architect and the
   operator together, then one re-projection.**
3. **The provenance mechanisms are live but the capability view is unexercised** (0 capabilities in the RLA
   plan). **Precondition: a plan with capabilities on a real target before any capability-level claim is made
   about ratified provenance.**

Any re-measurement after those preconditions would be a new authorization, not a reopening: the operator's
standing instruction is that the spike is stopped and no new arm is created. This document proposes no arm.

## 10. Verify (both repositories; nothing here changes what these return)

This repository (unchanged by this closeout; the gate and the fixtures are the proof of that):

    python spike/graph/fragments.py --verify spike/graph/fragments.json      # ARO_SOURCE_DOC set, or a legible lapse
    python spike/projections/project.py --check                              # byte-identical re-projection, exit 0
    python spike/measurements/rate.py                                        # 11 acts / 28 assertions, the two rates
    python -m pytest tests/test_fx_seam.py -q -p no:randomly -rxX            # 4 passed, 3 xfailed (strict)
    python tools/layout.py                                                   # exit 0

IntegratedAgent, branch `graph-materialization-build` (the mechanisms in section 3, each with its pins):

    python -m pytest tests/test_plan_signature_integrity.py tests/test_f3_ratified_provenance.py \
                     tests/test_f7_provisional_probe.py tests/test_composition_bridge.py -q      # F-16, F3, F6, F7/F7b/F7c
    python -m runtime.obligations                                            # exit 0: 29 CLOSED, 0 OPEN

---

# Part II -- the Arm B report as first closed (2026-09-11), kept byte-identical as history

Superseded by Part I where they disagree (section 2 of Part II in particular: Arm 0 has since run). Its
findings register, Spike-2 measurement, falsifications and verify commands remain the ARO-side record.

# Phase 1.5 spike — Arm B report (ARO dev agent)

**Work order:** SPIKE.md. **Governing text:** ARO v0.5.2 §16 with CP/SM v0.4.1 as its declared dependency; where brief and specification disagree the specification wins and the disagreement is a finding (SPIKE.md §0). **Amendments in force:** Amendment 1 (target substituted: the SRS 3-module slice) and Amendment 2 (graph authorship), signed by the architect on 2026-09-10 and recorded verbatim in `docs/decisions/2026-09-10-phase-1.5-amendments.md` (commit `bbdf6bf`).
**Sessions:** 2026-09-10, 15:43–16:07 (first pass, RLA target, blocked), 16:07–16:28 (reassessment on the new artifacts), 18:30–18:46 (execution under the amendments); 2026-09-11, 06:39–06:50 (the architect's acts landed; projection produced). Non-interactive; the architect was present only between sessions. Agent session id `675f4c87-f66d-4b13-9b01-71a46f18d31c`.
**Repository state:** written against `ef066ad`; commits added: `bbdf6bf` (the decision record), `5d2acd1` (GP-D), `972955b` (the F-10 path fix), and the commit carrying this report, which lands the spike work under the `spike-artifact` role (§11).

---

## 0. The headline finding — the seam is not in the source

The seam this spike exists to project — the findings read API that `author-agent` consumes from the findings store, the `getFindings` family — **does not exist in the SRS.** The prose contains no `getFinding`, `listFindings`, `appendFinding` or `getFindings`. §5's decomposition has no `panel-findings-store` component and no `contract` component. §6 has a seam *into* the findings store (S-S4, from panel/attack) and none out of it. And §5 homes `author-agent` at `.claude/agents/author`, an agent charter, where the baseline plan builds `src/author-agent.ts`.

So the baseline plan is a live specimen of the misreading class ARO exists to catch: two of its three modules and every one of its seam names are inventions under N1 (ARO §4.2), and one of its facts contradicts the specification outright. None of that is the loop's fault as a loop; it is what a model-proposed decompose is. **The thesis survives in its true form — one ratified place, projected identically — and for this seam class the ratified place is the architect's Design Graph (L3), not the specification.** The consequence for the measurement is the price: the slice's graph is five L2 records and ten assertions, but four L3 records and nineteen closures plus one adjudication, and the projector could not emit a single seam name until the architect conferred those values — which happened on 2026-09-11, eleven acts in one sitting. Spike 2 measured that.

Recorded as F-14 (§9); the architect's disposition: "the most valuable output of the spike so far."

## 1. State at close

| what | state |
|---|---|
| Source | **registered**: the SRS at `sha256:2428b115…` (`spike/graph/source-register.json`); 12 fragments minted and re-verified against it (`spike/graph/fragments.py`) |
| L2 graph | **authored, candidate**: 5 Specification Records, 10 assertions, every one span-cited; 4 diagnostics open (`spike/graph/l2/srs-slice.graph.jsonld`) |
| L3 candidates | **authored, candidate**: 3 closure bundles (19 closures) + the layout convention + 1 adjudication with three options and their consequences (`spike/graph/l3/`) |
| Ratification queue | **11 records queued, 11 acted** on 2026-09-11 (five L2 accepted, three L3 bundles + convention + rule ratified, adjudication decided **C**); 28 assertions bundled, 28 ratified (`spike/measurements/ratification-queue.jsonl`) |
| Projector | **projected the real slice; byte-identical on re-projection** (`spike/projections/project.py --check`, exit 0) |
| Projections | **produced**: six files in `spike/projections/out/`, one manifest digest `e9ba467b…7340` across all of them (§6) |
| FX-SEAM-A / B | **re-authored on the real seam, RED**; B now asserts against the real projected tier; guards green; `4 passed, 3 xfailed` |
| Spike 2 | 11 acts / 28 assertions performed in one sitting of 1.65 h (05:00–06:39 on 2026-09-11); **working rate 6.67 acts/h**, calendar rate 0.75 acts/h; individual act times not kept, recorded transparently on every row (§5) |
| Arm 0 | **no result exists**; branch not selectable; capture list handed to OPS (§2) |
| Handoff to OPS | **ready**: `spike/projections/HANDOFF-TO-OPS.md` carries the package digests and the adjudication's consequence; two OPS confirmations precede any build (same source bytes, same plan) |

## 2. Arm 0 — branch taken, and the external results consumed

**Branch taken: none.** No Arm 0 record exists in the IntegratedAgent repository (searched for every term ARO §16 uses, and `git log --all`). Per ARO §16 the arms' kill-interpretation is void until Arm 0 shows the class live or suppressed, so Arm B's seam result is not reported under any branch. The per-run capture list the architect adopted is in the handoff note: the ArchitecturePlan's exports for the store, the brief's interfaces block and architecture section, the bar's expected names, the built author-agent's imports, and the rendered `listFindings` signature. Each flip is to be classified **A** (founding inputs disagree) or **B** (inputs agree, build diverged) — the plan alone cannot tell (F-15).

External inputs consumed, with digests in `spike/graph/source-register.json`: the IA repo at `d97f536` (live, read-only); CP/SM v0.4.1 (`8af25eed…`), with v0.4.2–v0.4.9 also present (F-04); the substrate pin `1b7f3c1` (resolves); the SRS (registered); the Ops manifest and the slice plan as pasted (`spike/inputs/`, local digests only — the coord-side originals must be bound before any A/B).

## 3. Seam results per the branch

Withheld (§2). What the fixtures say without a branch:

- **FX-SEAM-A** (`examples/fx-seam-a/`) indexes four seams across the four founding inputs. One diverges — `panel-findings-store.findings-read` as `listFindings` in the plan and `getFindings` in the Planner Contract, the brief's architecture section and the bar — and three controls agree. `plan.json` is the supplied decompose, reduced; the other three are representative of the drift Ops named, to be replaced by Arm 0's capture. The projection half is RED: no Phase-5 compiler exists, and the spike's own projector refuses until the records are acted on, which is the correct RED.
- **FX-SEAM-B** (`examples/fx-seam-b/`): the projected `declared` tier exports `appendFinding`, `getFinding`, `listFindings` (all L3, and labeled so); the built author-agent imports `getFindings`. RED by design; green is the INT-2 composition milestone, as the architect's disposition confirms.
- Both guard halves pass and both discriminate tests pass (the offending name reconciled in memory clears the violation). RED halves run under strict expected-failure (§7).

## 4. Arm B, step by step (SPIKE.md §3)

| step | status | evidence |
|---|---|---|
| 1 Register the source | **done** | `src:srs-spec` registered at the digest Amendment 1 pins; fragments are text spans per ARO §5.1 (source digest + kind + code-point range + normalization version + text hash); `--verify` re-checks them |
| 2 Hand-author the lightest graph | **done, candidate** | 5 L2 records / 10 assertions; facets recorded (origin transformer, grounding bundles with roles, ratification unratified; authority never stored); role/force/scope on every gating assertion; one classification flagged for review (the C-S8 determinism note) |
| 3 D21 | **honored; no expressiveness failure** | every target is a specification-target description; nothing entails an instance (§8) |
| 4 Layout pattern | **ratified and exercised** | convention rq-001 (values authored by the architect, standalone attested, expiry 2026-10-11 or source-digest supersession, GP-D = 30 days recorded) + rule rq-012 at its content address; the rule derived every module's `files` in the projection with L2 and L3 premises (§8) |
| 5 Project deterministically | **projected** | byte-identical re-projection; one manifest digest across five outputs; the read seam identical in plan, planner contract, brief and bar; author-agent's `files` PROVISIONAL under adjudication C (§6) |
| 6 Queue, never confer | **done** | 11 live records with the ARO §9 display duties per item; no act performed, batched or simulated by the agent; all eleven acted on by the architect on 2026-09-11 |

## 5. Spike 2 — both numbers, and the starvation log

Derived by `python spike/measurements/rate.py` over the two logs. The tool refuses any act by an agent actor (falsified on a mutated copy), refuses an act timestamped before its record was queued, and reports two rates: the **calendar** rate (acts over the whole time the queue has been open, nights included) and the **working** rate (acts over the sittings in which they were made, when rows carry `sittingStart`).

| measure | value |
|---|---|
| required acts (records queued, not superseded) | 11 |
| assertions bundled in those records | 28 (+1 for rq-001, queued before the field existed) |
| assertions per act | 2.55 |
| acts performed / assertions ratified | **11 / 28** |
| queue open since | 2026-09-10T16:04:00-04:00 |
| measured to | 2026-09-11T06:39:00-04:00, the end of the architect's sitting (14.583 h after the queue opened) |
| calendar acts per hour | 0.754 |
| sitting | one, 2026-09-11T05:00 to 06:39 (1.65 h) |
| working acts per hour | 6.667 |
| hours to clear the required acts | 14.58 as it happened |
| starvation incidents | 2 — `sv-001` (B1, 0.034 h) and `sv-002` (B1+B2, 0.033 h), each closed at a session end with "no act received" |

**Reading it honestly.** The eleven acts are real: the projector verified every one against its record's content address and projected. Their individual times were not kept. The architect's statements, recorded verbatim on every acted row (`actTimesNote`): *"I only know the start time as recorded and end time,"* then, asked for the start, *"I started at 5am this morning."* So every row carries `actedAt` = the sitting's end (06:39, the time the architect wrote on the last record) and `sittingStart` = 05:00 on 2026-09-11. The note also keeps the field's history: the rows first carried `08:30:00`, the agent's format example, and an interim reading of 20:30 the evening before, both superseded by the architect's correction. Two rates follow: the **working rate**, 6.67 acts per hour over the 1.65 h sitting, which is the number spike 2 exists for; and the **calendar rate**, 0.75, which counts the queue's whole open interval including the night. The bundling lever is measured, not assumed: 11 acts carried 28 assertions (17 per hour of sitting); had each assertion been its own record the count would have been 28 acts plus the adjudication and the rule. The starvation log records only intervals in which the agent was present and blocked; the queue was open 14.6 h between the last agent session and the acts, with no agent waiting. **For Phase 4's entry condition** (ARO §16, §17.6): at 2.55 assertions per act and 6.67 acts per hour, a real specification's hundreds of records price out at tens of hours of operator sittings for the records alone, before the closures each record's underdetermination adds; GP-B (batch cadence) and record granularity are the levers, and this slice's ratio of 19 closures to 10 source assertions is the number to carry into that calibration.

**What is queued, by batch.** B1 (16:04): rq-001 layout convention, rq-002 layout rule (superseded). B2 (18:43): rq-003…rq-007 the five L2 records for 100 % span review; rq-008 the findings-store interface (8 closures); rq-009 the read seam (2); rq-010 module boundaries (8); rq-011 the adjudication; rq-012 the rule re-addressed (supersedes rq-002 because the rule's content changed — a changed rule is a new content address and a new act, ARO §9, D23).

## 6. The projector, and why the projections do not exist

`spike/projections/project.py` composes plan.json (loop shape), the `declared` tier, the Planner Contract, the Builder Brief and the Tester Contract from eligible Accepted L2 ⊕ eligible Ratified L3, embedding one Projection Input Manifest (L2 graph digest and acceptance head, each L3 record's digest and ratification head, the semantic-dependency-manifest digest, the compiler's own digest) in every output. It reads no prose; `scope` is a fixed template over ratified statements, fragment texts and closure content (D20). Eligibility is read from the queue and bound to each record's content address: unacted, stale-address, agent-actor and lapsed-grounding states all refuse, and each refusal names what it awaits. The layout rule must itself be ratified at the digest of the bytes about to run.

Until 2026-09-11 it refused the real slice with eleven awaited acts, which was its correct state: emitting closure content nobody had conferred would have been the agent conferring authority. Once the architect's acts landed it projected, and re-projection is byte-identical — the recorded basis of `Projected` (ARO §8.1). The package is in `spike/projections/out/`: six files, one manifest digest (`e9ba467b…7340`). **What the projection says about the seam:** the read seam reaches every consumer as the same two members, `listFindings` and `getFinding`, from one ratified record through one manifest — the store's plan signatures, the Planner Contract's exports, the author-agent brief's imports and architecture section, and the author-agent bar's calls; `getFindings` appears nowhere. **Adjudication C** relocates author-agent to `src/author-agent.ts` for the spike with the conflict against SRS §5 left open; the manifest records author-agent's `files` as PROVISIONAL, so the treatment arm reproduces the baseline's module shape under the ARO §11.2 cap. The self-test (synthetic slice, synthetic operator, never the real queue) still stands as the evidence the mechanism was ready before the acts: eleven checks, all passing.

## 7. FX-SEAM-A/B — encoding, and what was falsified

Seven tests in `tests/test_fx_seam.py`: four green guards, three strict expected-failures. Strict xfail runs and must fail; a silent green fails the suite. It is not a skip. Leaving them plainly red until Phase 5 would teach everyone to stop reading CI; the choice is stated so it can be overruled. What turns each green is written in the fixture READMEs as a demanded interface (`tool.aro-project` for A; `integration.loop-seam-gate` for B).

Falsified today: the A guard caught two fixture-authoring defects of mine (a control seam pointed at a unit id; the re-authored index had three seams where the guard demands four) and both were fixed by correcting the fixture, not the guard; both discriminate tests reconcile the divergent name in memory and require silence; the rule's and the projector's self-tests assert every mutation applied before checking its effect.

## 8. D21 findings and the layout-pattern verdict

**D21:** no expressiveness failure. Every L2 target is a kind description (`capability C-S8`, `record Finding`, `component author-agent`, `seam S-S4`); no shape types a specified-X as an X; nothing entails an instance from a requirement. The prescription/realization boundary was honored without strain at this fidelity, which says nothing about ADR-002's harder cases.

**Layout pattern (ARO §11.3): mechanism verified, price confirmed in structure, rate not yet measured.** The rule is deterministic, premise-retaining and lapse-propagating on synthetic inputs; it now accepts L3 component closures as premises, which the slice needs. On the real candidate it refuses because no expiry is set, and none can be defaulted: GP-D has no initial value (F-07). Two acts per project plus one rule per profile is exactly what the queue holds for the pattern (rq-001, rq-012). Fallbacks (b) and (c) are **not recommended**: there is no evidence against the pattern, only an unmeasured operator.

## 9. Findings register

Dispositions from the architect's direction of 2026-09-10 are applied where given.

| id | finding | status |
|---|---|---|
| F-01 | Brief placeholders unfilled (`<RLA_SPEC_PATH>`, `<IA_REPO_PATH>`, `<IA_HEAD_COMMIT>`); two resolved by search | open for the RLA; moot for the slice |
| F-02 | RLA specification absent on this machine | **superseded** by Amendment 1 |
| F-03 | Normative dependencies not delivered with the brief; located in the IA repo and digested | open (architect) |
| F-04 | ARO pins CP/SM v0.4.1; the IA repo carries v0.4.9; whether that is the bump INT-1..3 await decides FX-SEAM-B's path | open (architect) |
| F-05 | No Arm 0 record; the mapping cannot be entered | open (OPS own Arm 0) |
| F-06 | ARO cites IA-WIRING; the IA history has IA-SEAM / IA-CSEAM | open (spec amendment) |
| F-07 | GP-D had no initial value; a standalone closure could not be ratified with a default expiry | **resolved** 2026-09-11: GP-D = 30 days, a dated act in the decision record, set with rq-001 |
| F-08 | Brief describes a tree that does not exist; BFO/CCO already vendored; nothing imported by the spike | recorded |
| F-09 | Phase-1 ratification of ARO v0.5.2 not recorded in the repository | open (architect) |
| F-10 | **Repo gate red before the spike**: the layout contract named `…v0.5.md`, the tree has `…v0.5.2.md`; `python tools/layout.py` exited 1 and two layout tests failed | **resolved** 2026-09-11 on the architect's confirmation that v0.5.2 is authoritative: contract path and four doc references updated and committed; the layout gate is green |
| F-11 | `test-fixture` role could not host the §15 fixture corpus (Turtle-only, validator-loaded); FX-SEAM-A/B were undeclared and uncommittable | **resolved** by the architect's act of 2026-09-11 (decision record): role `spike-artifact` added, one component for `spike/`, the two fixtures declared under it at their §15 location in `examples/`, the spike work committed |
| F-12 | Tools carry Apache-2.0 SPDX headers; LICENSE is MIT | recorded (outside scope) |
| F-13 | Source substitution RLA → SRS slice | **resolved** by Amendment 1, recorded verbatim, committed |
| F-14 | **The seam is not in the source** (§0): every seam name and two of three modules are N1 closures; author-agent's repo home conflicts with the plan | **stands**; carried prominently; the adjudication is queued (rq-011) |
| F-15 | A- vs B-class not decidable from the plan; per-run capture list | **adopted**; handed to OPS |
| F-16 | Plan renders `listFindings` returning the truncated `Finding[` as a binding signature | **routed external** to IA DEV's queue; capture kept in the Arm 0 list; nothing more here |
| F-17 | Graph-author contamination | **resolved** by Amendment 2 (100 % span review; values conferred by the architect; non-graduating) |
| F-18 | The plan types the store's `cycle` as `number` and author-agent's `cycleId` as a string like `cycle-3`; the read seam cannot be typed without a decision | new; flagged inside rq-009 (`c:seam:cycle-identity`) |
| F-19 | `Finding`'s field set is stated only by two literal examples; `replay` appears in one | new; `diag:Finding-fields-by-example`, non-blocking, in the L2 graph |
| F-20 | **Act times were not kept per act.** Ten acted rows carried `2026-09-11T08:30:00-04:00` (the architect's recorded start, which read as a future time on that date); rq-012 carried 06:39:00, the end. The architect: "I only know the start time as recorded and end time." | **resolved transparently** 2026-09-11: every acted row now carries `sittingStart` 2026-09-11T05:00 (the architect: "I started at 5am this morning"), `actedAt` 2026-09-11T06:39, and the statements and the field's history in `actTimesNote`; rq-011's `batchSize` restored; the rate tool reports calendar and working rates separately (§5) |

## 10. What was falsified

- `layout_rule.py --selftest`: 11 checks, including determinism under reversed input, the lapse cone, five refusals, L3 premises.
- `project.py --selftest`: 11 checks (§6), synthetic content only.
- `rate.py`: refuses an empty queue, an actor-less act, an agent act (mutated copy, exit 2), an open interval with no end.
- `fragments.py`: a `startsWith` guard on every span; `--verify` against the registered digest.
- Fixtures: two authoring defects caught by the guard (§7).
- Layout contract: every spike component resolves; the only `MISSING` is F-10. `tests/test_repository_layout.py` + `tests/test_licensing.py`: 19 passed, 2 failed, both F-10.

## 11. What was not done, stated plainly

- **No act was performed, batched or simulated by the agent.** All eleven were the architect's, on 2026-09-11. The agent filled one derived field at the architect's instruction (`closureDigest`, a content address over the architect's authored values) and bound rq-001 to the resulting file digest; that confers nothing.
- The projections are written, but OPS have not been told to build: two preconditions in the handoff note (same source bytes in both arms; the plan bound to the coord-side original) are theirs to confirm first, and the adjudication's consequence must be read before comparing arms.
- Committed, in order: the decision record (the amendments, then GP-D, then F-11), the F-10 path fix, and — under the `spike-artifact` role the architect's F-11 act created — the whole of `spike/`, the two fixtures under `examples/`, `tests/test_fx_seam.py`, and the contract and licensing entries that declare them. The projections under `spike/projections/out/` are committed as the evidence record they are; the projector regenerates them byte-identically.
- F-10 not fixed; the IA repository not modified; the full SHACL suite not run (nothing here touches the ontology scope, shapes or the validator's fixture set).
- The L2 graph covers the slice's spans only; detected-clause coverage (ARO §8.2) is not computed — this is a hand-authored slice, not a transformation.

## 12. Duration against the bound

About 80 minutes of agent time across four sessions; a calendar span of 15 h 07 m from the first command (2026-09-10 15:43) to the projection (2026-09-11 06:42), most of it the queue waiting overnight for an operator. The architect's eleven acts landed in one sitting ending 06:39 on 2026-09-11. Inside the one-to-two-day bound. The treatment builds, which are OPS's, are outside it.

## 13. Verify

```
python spike/graph/fragments.py --verify spike/graph/fragments.json
python spike/graph/rules/layout_rule.py --selftest
python spike/projections/project.py --selftest
python spike/projections/project.py --check          # Projected: byte-identical on re-projection, exit 0
python spike/measurements/rate.py
python -m pytest tests/test_fx_seam.py -q -p no:randomly -rxX
python tools/layout.py                                # exit 0 (F-10 fixed 2026-09-11)
```

## 14. What the architect is asked for, in order

1. Nothing further on the queue: the sitting is recorded as you stated it (05:00–06:39, 2026-09-11).
2. Optionally record adjudication C as a dated line in the decision record, in the same idiom as GP-D; the queue row is the act, the record is where the operational decisions are read.
3. OPS: confirm the two preconditions in the handoff note and build; Arm 0 remains theirs.
4. F-04 and F-06 as spec matters; F-03 and F-09 (delivery of dependencies; the Phase-1 ratification record) as governance matters.

---

## Addendum A — artifacts received after the first close (2026-09-10T16:27:54-04:00)

Kept as history. The operator supplied the Ops spike-input manifest and the slice plan by paste; both are under `spike/inputs/` with local digests (`0c9bd222…` for the plan, `1847eb1e…` for the manifest). Findings F-13 to F-17 were raised in that reassessment and are dispositioned in §9 above.
