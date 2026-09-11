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
| Spike 2 | 11 acts / 28 assertions performed in one sitting; **working rate 1.08 acts/h** over a 10.15 h sitting span, calendar rate 0.75 acts/h; individual act times not kept, recorded transparently on every row (§5) |
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
| sitting | one, 2026-09-10T20:30 to 2026-09-11T06:39 (10.15 h span) |
| working acts per hour | 1.084 |
| hours to clear the required acts | 14.58 as it happened |
| starvation incidents | 2 — `sv-001` (B1, 0.034 h) and `sv-002` (B1+B2, 0.033 h), each closed at a session end with "no act received" |

**Reading it honestly.** The eleven acts are real: the projector verified every one against its record's content address and projected. Their individual times were not kept. The architect's statement, recorded verbatim on every acted row (`actTimesNote`): *"I only know the start time as recorded and end time."* So every row carries `actedAt` = the sitting's end (06:39, the time the architect wrote on the last record) and `sittingStart` = the start as the architect recorded it, 08:30 — which can only precede the end as 20:30 on 2026-09-10; an 08:30 start on the 11th would postdate both the end and the file's save at 06:40. The rows keep the original value in the note, and the date is a one-field correction if wrong. Two consequences: the **working rate is a lower bound** — 1.08 acts per hour spreads eleven acts over a ten-hour span that includes the night, not over attentive time — and the **calendar rate** (0.75) counts the queue's whole open interval. The bundling lever is measured, not assumed: 11 acts carried 28 assertions; had each assertion been its own record the count would have been 28 acts plus the adjudication and the rule. The starvation log records only intervals in which the agent was present and blocked; the queue was open 14.6 h between the last agent session and the acts, with no agent waiting. **For Phase 4's entry condition** (ARO §16, §17.6): at 2.55 assertions per act and 1.08 acts per hour, a real specification's hundreds of records price out at hours to days of operator sittings, and GP-B (batch cadence) and record granularity are the levers — exactly what §16 says to calibrate first if the count demands it.

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
| F-20 | **Act times were not kept per act.** Ten acted rows carried `2026-09-11T08:30:00-04:00` (the architect's recorded start, which read as a future time on that date); rq-012 carried 06:39:00, the end. The architect: "I only know the start time as recorded and end time." | **resolved transparently** 2026-09-11: every acted row now carries `sittingStart` 2026-09-10T20:30, `actedAt` 2026-09-11T06:39, and the statement and the original value in `actTimesNote`; rq-011's `batchSize` restored; the rate tool reports calendar and working rates separately (§5) |

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

1. Confirm the sitting's start date in `actTimesNote` (recorded as 2026-09-10T20:30 from your "08:30"); one field on each row if it is wrong.
2. Optionally record adjudication C as a dated line in the decision record, in the same idiom as GP-D; the queue row is the act, the record is where the operational decisions are read.
3. OPS: confirm the two preconditions in the handoff note and build; Arm 0 remains theirs.
4. F-04 and F-06 as spec matters; F-03 and F-09 (delivery of dependencies; the Phase-1 ratification record) as governance matters.

---

## Addendum A — artifacts received after the first close (2026-09-10T16:27:54-04:00)

Kept as history. The operator supplied the Ops spike-input manifest and the slice plan by paste; both are under `spike/inputs/` with local digests (`0c9bd222…` for the plan, `1847eb1e…` for the manifest). Findings F-13 to F-17 were raised in that reassessment and are dispositioned in §9 above.
