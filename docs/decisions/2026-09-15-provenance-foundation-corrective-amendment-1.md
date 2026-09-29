# Corrective Amendment 1 — Provenance Foundation Phase Plan v1.1

**Status:** UNRATIFIED CANDIDATE · drafted by ARO DEV · no operative effect until the review, verification, and ratification gate in §8 is complete.
**Draft date:** 2026-09-15
**Amended instrument:** `docs/decisions/2026-09-14-provenance-foundation-phase-plan-v1.1.md`
**Immutable plan commit:** `6cbad3588a8c683d09e95c465104056d6dde3ba2` (`6cbad35`)
**Immutable plan SHA-256:** `C43954A6825E6BE042CEB8293BC2F7F0C94F88E12C42E48E6DF06B9BF88D7AF8`
**Document license:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/), matching the amended instrument.

## 1. Amendment rule and entry gate

The signed Plan v1.1 identified above remains byte-for-byte immutable. This amendment does not rewrite it, replace its historical text, reopen the closed spike, or enlarge the phase authorization. Once ratified, this amendment controls only the subjects expressly listed below; every other Plan v1.1 provision remains in force.

Where this amendment conflicts with Plan v1.1 on one of those subjects, this amendment governs prospectively. No Stage A task may begin, and no work may be charged to the phase, until the gate in §8 is complete. Work performed before that gate cannot satisfy a Stage A entry or exit condition.

## 2. Withdrawal of Plan v1.1 §16

Upon ratification of this amendment, Plan v1.1 §16, **“Independent review attestation,” is withdrawn as authoritative evidence**. It remains visible only as immutable historical text.

The withdrawn §16:

- confers no authority;
- satisfies no review, verification, freeze, entry, exit, or closure condition;
- must not be cited as evidence that findings were resolved; and
- is not revived by later agreement with any statement it contains.

This withdrawal makes no finding about the identity, intent, or process of the purported reviewer. The content-addressed IA DEV review and IA OPS verification required by §8 supersede it for this amendment's limited scope.

## 3. Ratification authorizes—but does not execute—the A3 re-pin

Plan v1.1 Act 2 authorizes the Stage A sequence and authorizes Aaron to consider the later A3 re-pin. **Neither Act 2 nor ratification of this amendment executes A3, changes the active CP/SM pin, or establishes CP/SM v0.4.9 as the measurement baseline.**

A3 occurs only through a separate, dated architect act issued after both of these artifacts exist:

1. **A2:** IA DEV's consistency attestation and F-04 answer; and
2. **A2b:** IA OPS's three-surface compatibility record, with every difference either traced to a recorded ruling or adjudicated.

The A3 act must identify the exact A2 and A2b artifacts by SHA-256, name CP/SM v0.4.9 and its immutable source revision, state what the evidence proves and does not prove, expressly assume the unaudited residual, and record any open finding. An unresolved baseline-blocking finding prevents A3. A3 must not be inferred, backdated, or bundled into Act 2, this amendment, or A4.

Until A3 is issued, the pre-A3 pin remains active. A4 may implement and publish the new pin only after A3 and must cite the A3 act.

## 4. Held-out normative-clause coverage

For the genuinely held-out external specification, the binding normative-clause coverage threshold is **100%**. It is an exact population result, not a rounded estimate.

Before the first held-out run, IA OPS must freeze the denominator as a clause census with a stable ID and source locator for every detected normative clause. IA OPS must derive and reconcile that census using the Plan v1.1 independent denominator channels; every channel disagreement and every `MissedClause` or `ConflatedClause` audit must be resolved before the denominator is frozen. The denominator must be non-zero and its manifest and digest must be recorded.

A denominator clause counts as covered only when the frozen output contains either:

1. at least one correctly grounded candidate assertion preserving the clause's normative force and scope; or
2. where faithful assertion is blocked by ambiguity or underdetermination, an explicit clause-linked `AmbiguityDiagnostic` or `UnderdeterminationDiagnostic` that preserves the unresolved alternatives or absence.

Diagnostics must be reported separately and do not count as assertions. A clause with no such assertion or diagnostic is uncovered. Multiple outputs for one clause count once; one output may not silently satisfy multiple clauses unless each clause is separately linked and the full meaning of each is preserved.

The evaluation record must publish numerator, denominator, percentage, and the clause-by-clause disposition. Pass requires `covered = denominator`, exactly 100%. Any result below 100% is a completeness-class failure and follows the Plan v1.1 single-re-run rule; rounding cannot convert a shortfall into a pass. The SRS and RLA retain their stated contamination grades and do not dilute or substitute for the held-out threshold.

## 5. Freeze 3 replacement gate and OPS execution

This section replaces Plan v1.1 §11.3 for every transformer-probe measurement run and changes the C3 measurement-run owner from ARO DEV to IA OPS. ARO DEV supplies the frozen runnable transformer and may run only synthetic self-tests. **IA OPS alone introduces and executes the sealed measurement inputs.** ARO DEV and the transformer author must not receive the seeded input contents or fixture placements until IA OPS has committed the corresponding outputs and opened the seal for evaluation.

No measurement run may start until IA OPS has initialed a content-addressed Freeze 3 package. The package consists of a complete pre-run manifest plus append-only execution receipts whose required fields are fixed by that manifest. Unless a stronger format-specific rule is stated, file digests are SHA-256 over exact bytes and structured manifests state their canonical serialization.

### 5.1 Transformer pin

- repository and exact commit;
- clean/dirty state, with any permitted patch captured and digested;
- version, entry point, invocation, source-tree manifest, and executable or package digest;
- parser, segmenter, normalizer, canonicalizer, schema, ontology/profile, shape, derivation-rule, and tool versions and digests; and
- dependency lockfiles and the resolved dependency inventory.

### 5.2 Model pin

- provider, endpoint/API version, exact model identifier, and immutable model snapshot or weights digest;
- tokenizer and inference-runtime versions where separately selectable;
- seed and every decoding/inference parameter, including temperature, top-p/top-k where applicable, token limits, stop sequences, penalties, response format, tool-choice mode, and parallel-tool setting; and
- the requirement that each execution receipt capture the provider-returned model revision or system fingerprint with every response.

A mutable model alias is insufficient. If the execution service cannot identify an immutable model snapshot or equivalent immutable model artifact, Freeze 3 does not close and the measurement run is unauthorized.

### 5.3 Prompt and configuration pin

- exact bytes and SHA-256 for every system, developer, user, repair, retry, and adjudication prompt or template;
- exact few-shot examples, tool descriptions and schemas, output schemas, prompt order, message roles, template engine/version, substitutions, and serialization rules;
- the fully resolved non-secret configuration, CLI arguments, feature flags, retry/backoff policy, timeout policy, concurrency, cache state and policy, and network/tool access policy; and
- identifiers and versions for credentials or secret-backed services without recording secret values. Redaction must not hide any value that can alter transformation semantics.

### 5.4 Input pin and seal

- the registered original source digest and every derived extraction's bytes, digest, extraction tool/version, normalization profile, and locator mapping;
- the exact unseeded per-spec input manifest;
- the exact OPS-seeded per-run input digest and a sealed placement manifest under IA OPS custody;
- the frozen normative-clause denominator manifest required by §4; and
- the contamination label and decision weight for each specification.

IA OPS must introduce the sealed input only after the transformer, model, prompts, configuration, environment, and run plan are frozen. No preview, exploratory execution, prompt repair, or author-visible diagnostic may use a measurement input.

### 5.5 Environment pin

- execution-environment image or VM digest, operating system and architecture;
- language runtimes, package-manager versions, resolved packages, drivers, accelerator type, and relevant deterministic-runtime settings;
- locale, encoding, time zone, clock policy, filesystem/input ordering, working directory, and environment-variable allowlist;
- network isolation or explicit endpoint allowlist, cache state, and external tool versions; and
- the command line and orchestration artifact that reproduce the run.

### 5.6 Run-count pin and custody

The primary measurement count is exactly **three runs: one run for each of SRS, RLA, and the held-out external specification**. IA OPS assigns the run IDs and input digests before execution. There are no measurement-input warm-ups, hidden trials, best-of-N selections, or discarded outputs.

The existing completeness/diagnostic remedy permits at most **one corrective re-run per specification** and no invention-class re-run. Thus the phase permits three primary runs and no more than three conditional corrective re-runs. Each authorized re-run requires its own re-initialed Freeze 3 manifest, fresh OPS-sealed fixture placements, and a new run ID; it supplements rather than replaces the primary record.

A crash, timeout, partial output, policy refusal, or infrastructure failure is a recorded run outcome, not a silently replaceable attempt. It consumes that scheduled run. This amendment authorizes no infrastructure-replacement attempt outside the stated completeness/diagnostic re-run branch; any other replacement requires a new architect-ratified protocol amendment. Every attempt and output remains in the evaluation record.

Any post-freeze change to a pinned item invalidates the affected freeze before execution. After an output is observed, the change and any permitted re-run must be recorded as a new, superseding freeze; the original run remains reportable.

## 6. F2 0/5 statistical correction

For zero observed F2-class failures in five independent trials, the exact one-sided 95% Clopper-Pearson upper confidence bound is:

`1 - 0.05^(1/5) = 0.4507197...`, approximately **45.1%**.

Accordingly, Plan v1.1's statement that the residual is approximately 20% is withdrawn. A result of **0/5 remains the phase decision threshold** for the Plan v1.1 branch “resolved for this phase's purposes,” but it is only a bounded phase-governance rule. It does not establish that the population F2-class failure rate is below 20%, and it must not be reported as doing so.

The run record and Stage D closeout must show the observed count, effective N, method, confidence level, and exact upper bound. If the effective sample grows and still contains zero F2-class failures, the bound is recomputed as `1 - 0.05^(1/N)`. The additional WS-3 observation remains separately identified; combining it is permitted only if the record defends the same Bernoulli trial definition and independence assumptions.

## 7. GP-E: substantive-work stop and closeout reserve

GP-E remains **4 hours per week, in no more than two sittings of no more than 2 hours each, for five calendar weeks**. Within that 20-hour envelope:

- no more than **18.0 cumulative hours** may be used for substantive phase work; and
- **2.0 hours are reserved exclusively for closeout**.

Substantive phase work includes operator review, ratification-queue work, adjudication, audit, measurement review, remediation decisions, and other phase work outside final closeout. At 18.0 substantive hours, all further substantive work stops: no additional run, re-run, review population, remediation, or scope may be started. The stop applies even if a weekly allowance remains.

The reserved 2.0 hours may be used only to assemble and read the final evidence package, record unfinished or failed work truthfully, complete the Stage D scoreboard and closeout record, and issue or decline the Stage D closeout, INT-4, and tee-up acts. It may not be converted into execution, remediation, or additional evidence generation.

If closeout cannot be completed within the reserved 2.0 hours, the phase stops with an explicit incomplete-closeout finding. Time may not be borrowed from another week or extended beyond 20.0 hours without a new dated architect act that states the reason and the effect on the affordability finding. IA OPS must maintain the cumulative ledger with separate `substantive` and `closeout-reserve` categories and report remaining balances after every sitting.

## 8. Review, verification, and ratification gate

Authority attaches to content, not to this draft's filename or status label. The following sequence is mandatory before Stage A begins:

1. **ARO DEV drafts.** ARO DEV freezes this candidate, records its SHA-256, and identifies the immutable Plan v1.1 anchors stated above. This is authorship, not approval.
2. **IA DEV reviews factory-facing semantics.** The review must address at least the authorization/execution distinction for A3, the unchanged active pin before A3, A2/A2b/A3/A4 ordering, baseline activation, declaration-channel and transport-proof effects, and any impact on factory contracts or consumers. Findings block the gate until dispositioned in a new candidate.
3. **IA OPS verifies the amendment.** Verification must confirm the 100% held-out coverage computation is executable, the Freeze 3 manifest is complete, OPS can preserve seal custody and execute the inputs without author exposure, run counts and failure handling are unambiguous, the 45.1% correction is reproduced, and the 18+2 hour ledger stops mechanically. Findings block the gate until dispositioned in a new candidate.
4. **Aaron ratifies.** Aaron issues a separate dated act that cites the exact amendment SHA-256 and the exact IA DEV and IA OPS review-record digests. Ratification makes this amendment operative; it does not execute A3 or any measurement run.

Every review, verification, and ratification record must bind to the same amendment SHA-256. Any change to this candidate after a review invalidates that review for the changed candidate. The completed gate record must be committed before the first Stage A task begins.

## 9. Required ratification statement

The architect's later act should state, in substance:

> I ratify Corrective Amendment 1 identified by SHA-256 `[AMENDMENT SHA-256]`, amending only the stated subjects of Provenance Foundation Phase Plan v1.1 at commit `6cbad3588a8c683d09e95c465104056d6dde3ba2`, Plan SHA-256 `C43954A6825E6BE042CEB8293BC2F7F0C94F88E12C42E48E6DF06B9BF88D7AF8`. I have received the IA DEV review `[RECORD SHA-256]` and IA OPS verification `[RECORD SHA-256]`. This act makes the amendment operative and permits Stage A to begin under it. It does not execute the later A3 re-pin or any measurement run. — Aaron Anthony Damiano, `[DATE]`

The bracketed fields are intentionally incomplete in this unratified candidate. A statement with any field empty, or bound to mismatched content, does not ratify the amendment.
