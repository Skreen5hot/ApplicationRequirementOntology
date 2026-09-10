# ARO v0.5 — Application Requirements Ontology and the Specification Graph Pipeline (Published)

**Status:** published · supersedes ARO v0.4, which it absorbs · the external review's conditional approval is discharged herein (five blocking amendments + two hardenings resolved); per that review, no architectural element remains blocking Phase-1 ratification, which completes by the architect's act
**Numbering note:** the review approved "v0.4 after amendments"; issued versions freeze in this program, so the amended text publishes as v0.5.
**Normative dependencies (delivery rule):** this document is complete only in the company of **CP/SM v0.4.1 (frozen)** — in particular §1.2 (AUTHORITATIVE), CP-5, CP-14, CP-16, CP-19, CP-21, §9 — and the substrate `runtime/assembly_ledger.py` @ `1b7f3c1`. Definitions are referenced, never copied. "Teams receive only this text" means: this text **plus its declared normative dependencies**.
**Ratification surface:** the amended decisions (D15, D17, D19, D23, D24) and the additions flagged *(authored)* in §20.
**Change log:** §18.

---

## 0. First principle, thesis, and the interpretation boundary

> **A check must verify its own precondition, or it passes vacuously.**

Applied here: every downstream check assumes the graph faithfully represents the source and verifies that assumption nowhere unless this document builds the verification — including the failure channels the transformer cannot self-report (§4.3). An internally coherent graph can be a coherent misreading; the 0.93 scoreboard was internally coherent too.

**Thesis.** Transform human application specifications into faithful, provenance-preserving, machine-checkable **Specification Graphs** that downstream consumers use without reinterpreting the source prose. The general requirements ontology remains the long-term goal; faithful normalization of a real specification is the proving ground.

**The interpretation boundary (D20).** Three kinds of judgment, three homes, no leakage: **source interpretation** only inside the transformation-and-ratification boundary (transformation acts, diagnostic resolution, ratification acts); **design judgment** only as L3 closure acts; **projection deterministic and non-interpretive** — it MUST NOT add, resolve, strengthen, or reinterpret semantic content. Any component that re-reads the prose, fills in the graph, or resolves an ambiguity locally has violated the architecture.

---

## 1. Position in the program, scope, and non-goals

ARO sits upstream of the Integrated Agent loop and upgrades its founding inputs from *model-proposed* to *derived-from-ratified*: `plan.json`, the capability set, and the `declared` contract tier become deterministic projections of a ratified graph. Three named CP/SM holes are filled by construction: an audit-independent seed source for the coverage matrix (§11.3), the `declared` tier populated for the first time since `exports:null`, and mechanical capability seeding from stimulus→observable-response paths and acceptance clauses.

**Non-goals, hard limits.** ARO does not replace Rungs 1–4 — requirements grain is not seam grain; the graph feeds the loop and never substitutes for it. ARO does not unfreeze v0.4.1. MVP scope rule, carried: *new terms SHOULD be deferred unless they directly support faithful transformation, graph validation, traceability, or deterministic compilation.* ARO's build parallelizes with the loop's Phase 0/1.

---

## 2. The four products and the graph rule (D10, D17)

| # | Product | Contains | Authority home |
|---|---|---|---|
| **L1** | **ARO TBox** | reusable semantics: Requirement, Acceptance Clause, Source Fragment, Interface Specification, Worked Example, Prescribed Invariant, Diagnostic, Trace Assertion, … | committed ontology modules (§15) |
| **L2** | **Specification Graph** | what the source **says or prescribes** | candidate: run root · accepted: `oracles/`-class |
| **L3** | **Design Graph** | **ratified engineering closures** — decisions the source underdetermines. Closure **proposals may originate from an operator or a transformer** (a labeled N1 proposal); **only ratified closures compile.** D24 independently records who proposed. | `oracles/`-class on ratification |
| **L4** | **Realization & Evidence Projection** | what later **happened** | **a projection of the assembly ledger, never a store** — trace assertions carry ledger coordinates `{specDigest, seq, head}`, never copies |

**The graph rule (D17): membership is decided by semantic nature, boundaries by grounding ancestry under the active environment; citation is free.**

- **L2 membership:** the assertion is **source semantics** — directly grounded in Source Fragments, or rule-derived with a derivation whose complete ancestry terminates in grounded AUTHORITATIVE premises, **under the active ratified derivation environment identified by the semantic dependency manifest** (rule set, ontology modules, profile version). Derivability is decidable within a release; it is never "derivable in principle."
- **L3 membership:** the assertion's content is an **engineering closure** — neither asserted by nor derivable from registered sources *under that same active environment*.
- **History never reclassifies:** if a later rule makes closure-content derivable, the old closure keeps its historical membership; the system opens a **`SubsumptionNotice`** (§7) — blocking only on conflict — and the forward path is an operator act superseding or retiring the closure in favor of the new rule-derived L2 assertion. Membership mutates only by supersession, never by environment drift.
- **Schema enforcement (via D23):** L2 shapes require grounding-or-derivation-ancestry; L3 shapes **forbid `aro:groundedBy`** and **permit `aro:rationaleSource`** — an operator choosing `GET /accounts/{id}` may cite the passage that motivated the choice; motivation is citation, not grounding, and never enters the authority basis.

Why L3 exists (carried): N1 plus a deterministic compiler equals underdetermination — "API required, method unspecified" is faithful and unbuildable; someone decides, N1 rightly bars the transformer from *deciding*, and undocumented limbo is where laundering starts. The compiler consumes **eligible Accepted L2 ⊕ eligible Ratified L3** (§3.2, §11). Why L4 is a projection (carried): a second evidence store with no chain is a second source of truth, and it re-breaks *linked test ≠ executed test*, which only the ledger enforces.

---

## 3. Provenance facets, computed authority, and eligibility (D24, D19)

### 3.1 The four facets (orthogonal, all recorded, none substituting for another)

- **Origin** — the producing act, always by reference: `transformer(actRef)` · `operator(actRef)` · `rule(ruleRef@version, execRef)`. Origin is never a grounding claim, and it never changes.
- **Grounding** — a bundle of Source Fragments with roles (§5.3): required, directly or through complete derivation ancestry, for L2; forbidden for L3 (rationale citation permitted).
- **Ratification** — `unratified` | `ratified(actRef)`. Binds to content-addressed assertions (D23); adds status; never alters origin or grounding — true by construction.
- **Authority** — **computed, never stored**:

  > `AUTHORITATIVE(a)` iff `origin(a)=operator(act)` ∨ `ratified(a)` ∨ (`origin(a)=rule(r,·)` ∧ `r` ratified ∧ every premise AUTHORITATIVE).

  A deterministic, ratified extractor over a registered source is a rule; CP/SM's `spec-derived` lands exactly here. ARO references CP/SM §1.2's class by identity and adds no members.

**Worked example:** `origin: transformer(T-3) · grounding: SP-88 · ratification: R-71 → authority: AUTHORITATIVE` — without pretending ratification changed where the assertion came from. A transformer-proposed closure ratified by act is AUTHORITATIVE with transformer origin; that is the design, not a leak.

### 3.2 Authority is history; eligibility is state

**Authority and gating eligibility are distinct.** Ratification and authorship acts are append-only history: they never un-happen, so AUTHORITATIVE — computed from acts — never disappears when a later dependency lapses. What lapse suspends is **eligibility**, the fold's current view:

> An assertion is **eligible to gate or project at full authority** iff it is AUTHORITATIVE **and** belongs to a currently **effective** Accepted L2 or Ratified L3 graph — one whose semantic dependency manifest has not lapsed — **and** its dependency cone contains no blocking diagnostic **and**, for closures, its declared closure dependencies are current (§5.6). **Provisional eligibility** for machine-clean unratified content is evaluated the same way at its own grade and carries the PROVISIONAL cap.
>
> **Lapse suspends eligibility; it does not rewrite historical provenance or erase the ratification act.** This is the substrate's authority ≠ history rule, applied to ARO's own semantics.

All gating language in this document — §9's acceptance, §11's compilation, CP-5 composition — reads **eligible** content. Re-acceptance after lapse is a new anchoring act over the same historical record.

**Fail-closed asymmetry, in facet terms:** non-authoritative content can open diagnostics, block eligibility, and cap dispositions; it can never confer.

---

## 4. The transformation model (D6, D9, D19)

```
Registered Source(s)  +  Profile  +  Transformer(config)
      ↓ TransformationAct                        — ledger event
Candidate Specification Graph + Diagnostics + Facets
      ↓ validation ladder (§8) · ratification queue (§9)   — ledger events, operator acts
Accepted Specification Graph                     — oracles/-class, embedding the attested head
```

Candidates live in the run root; accepted graphs are ratified standards under `oracles/` per authority ≠ history. Candidate generation may be stochastic; authority attaches to content, not to the generator — ratification binds content-addressed assertions, and only eligible AUTHORITATIVE content gates.

**Acceptance identity vs. generation provenance (D19).** Acceptance binds to **graph content** (canonical `graphDigest`, ADR-003) and the **semantic dependency manifest**: registered source digests · profile version · ontology module versions · SHACL shape versions · derivation-rule versions · canonicalization/normalization version. A manifest change **lapses eligibility and requeues** (CP-16's shape; §3.2 governs what lapse means). **Generation provenance** — transformer version, model identity, configuration, prompt, segmentation method — is fully recorded but non-lapsing; a change opens a **`ReevaluationObligation`** (co-reported, backlog-queued, non-blocking). Freshness pressure is a queue; revocation is a human act.

**Defect response is not version churn.** A generation-provenance change **alone** never blocks. But when a defect is subsequently established in a generation-provenance class — *transformer v2.1 misclassified Non-Goal sections as Normative* — an **authoritative defect finding** (`GenerationDefectFinding`, an operator or ratified act) MAY open **blocking** diagnostics against the affected generation-provenance **population**, suspending eligibility through the ordinary cone rule until reviewed. This is defect response, not version-based automatic revocation — and it is why generation provenance is recorded at all: the record is what makes the affected population targetable.

### 4.2 N1 — the Non-Invention Principle (carried verbatim in substance)

A transformation MUST NOT infer unstated: programming language, framework, repository layout, component ownership, runtime environment, deployment model, database, message broker, security mechanism, or implementation approach — unless a registered source states it or a human ratifies it as a closure (→ L3). **Absence must remain absence.** On underdetermination the transformer's legal outputs are the representable absence, an `UnderdeterminationDiagnostic`, or a **labeled closure proposal** into the L3 queue — `transformer`-origin, `model-proposed`, conferring nothing.

### 4.3 The transformer's honesty boundary (§0 applied; D22)

The transformer can self-report ambiguity, conflict, and underdetermination. It cannot self-report what it failed to see: missed clauses, conflated clauses, misgrounded citations. Those channels get independent detectors (§8.2); FX-MISS is their fixture.

---

## 5. Sources, fragments, identity, closures, supersession (D3, D5, D19, D23)

### 5.1 Source Fragments and fragment identity

The abstract grounding unit is the **Source Fragment**; **Text Span** is its RLA-profile implementation:

```json
{ "fragmentId": "sf:<content-derived per the identity formula>",
  "kind": "text-span",
  "source": { "doc": "rla-spec.md", "digest": "sha256:…" },
  "locator": { "codepointRange": [4812, 5147] },
  "normalizationVersion": "norm-1.2",
  "textHash": "sha256:<normalized span text>",
  "anchors": { "before": "sha256:<preceding context>", "after": "sha256:<following context>" },
  "display": { "lines": "142–146" } }
```

**Fragment identity = source digest + fragment kind + canonical locator + normalization version + normalized-content hash** (ADR-003 acceptance criterion). Identical repeated text — even with repeating anchors — cannot collide: the canonical locator (code-point range for text; representation-specific for future kinds) disambiguates within the immutable digest. `display` is metadata only. Migration to a new source digest is a **`migratedFrom` relationship** between distinct fragments; it never pretends the old and new fragments are the same fragment. Future fragment kinds (PDF region, table cell, JSON pointer, diagram element) implement the same abstract identity. The normalization algorithm is versioned in the manifest — otherwise `textHash` drifts silently.

### 5.2 Supersession and requeue

A source edit yields a new digest; dependent acceptances **lapse eligibility** and requeue (§3.2). The transformer proposes fragment migrations (`textHash` + locator resolution under the new digest → migration proposal; unresolvable → `LapsedGroundingDiagnostic`). Profile, shape, rule, and canonicalization versions lapse identically (manifest members); generation-provenance changes do not (§4).

### 5.3 Grounding bundles

One assertion may require several fragments — *"It shall lock after five failures"* does not ground "it" alone. Grounding is a bundle with roles: **primary** (1..n) · **context** · **definition** · **reference**. L2 requires at least one primary fragment directly or via derivation ancestry.

### 5.4 Identity continuity (D3)

`Requirement` ≠ `Expression` ≠ `Specification Record` ≠ `Revision` ≠ `Fragment`. Continuity across source revisions: **mechanical when rule-derived** — a profile's identity policy over source-declared identifiers is a ratified derivation rule; continuity through it is `rule`-origin and AUTHORITATIVE by the standard chain. **Ratified when inferred** — similarity-based continuity is `transformer`-origin and MUST be ratified. Automatic inferred continuity is an N1 breach.

### 5.5 The round trip

When the build discovers via a ledger finding that a ratified assertion is wrong or ambiguous in practice, a **`RealizationConflictDiagnostic`** opens against the graph, carrying the finding's ledger coordinates. Resolutions: graph supersession (with dependent re-verification), a new closure, or a recorded source-amendment request. Without this edge the graph ossifies while the build learns.

### 5.6 Closure dependencies and lifecycle (D19 extension — the L2→L3 edge)

Closures exist to close L2 underdetermination; their lifecycle must therefore depend on what they close.

- **Declared dependencies (semantic, lapse-bearing).** A closure that resolves an **identifiable** underdetermination MUST declare it: `closes` (the `UnderdeterminationDiagnostic` or the unspecified facet of an L2 assertion), `addresses` (the Specification Record(s)), `dependsOn` (specific L2 assertions). Schema-enforced where identifiable.
- **Lapse rule.** Supersession or lapse of any declared dependency **requeues the dependent L3 cone**: the closure's eligibility is suspended until an operator re-ratifies, amends, or retires it. *A stale closure MUST NOT remain eligible for projection merely because its original ratification act remains historically valid* — the §3.2 rule, applied to L3. (The reviewer's case: "use GET" closed "method unspecified"; the requirement becomes "state-altering commands shall use POST"; the closure's `closes` target is superseded; the closure suspends.)
- **Standalone closures** *(authored)*. Some closures — repository layout, framework choice, the N1 list generally — close no identifiable L2 underdetermination. Requiring a dependency edge there would force **fake edges, which is invented grounding one level up**. A free-standing closure instead carries an explicit operator-attested **`standalone`** marker: attested absence of an L2 dependency, honest and visible in the queue display. Standalone closures lapse only with their own manifest and ratification.
- **Rationale is citation, with a courtesy** *(authored)*. `rationaleSource` remains non-lapse-bearing — motivation is not dependency. But supersession of a cited rationale fragment opens a **non-blocking `ReevaluationObligation`** on the citing closure: citation is free; changed motivation is worth a look. No new machinery — the obligation type already exists.
- **Honest limit (§0 discipline).** Semantic conflicts between changed L2 content and existing L3 closures **beyond declared dependencies are not mechanically caught**. The backstops are the round trip (§5.5), review, and the ConflictingStatement diagnostic — which spans layers when opened. Claiming an automatic L2↔L3 semantic-conflict detector would assert a check that does not exist; this is recorded as watch item §17.4.

---

## 6. Statement classification and negative information (D8)

- **Role:** `Normative · Informative · Example · Rationale · Note · Open-Question`
- **Force** (where Normative): `obligation · prohibition · permission`
- **Scope disposition:** `in-scope · non-goal`

*"Shall not store passwords in plaintext"* → Normative + prohibition. *"Billing is outside this release's scope"* → Normative + non-goal. **Gate rule:** role: Normative gates; `Example` never becomes a requirement (the Docker rule, FX-EXAMPLE) and feeds Worked Example extraction instead.

**Negative information, layered:** graph carries three **semantic** states — `prohibited` · `non-goal` · `unspecified` (the source, where covered, is silent); coverage carries its own axis — `covered` · `not yet covered`. **Projection rule:** projections MUST preserve explicit negative content and MUST accompany it with coverage metadata sufficient to distinguish specification silence from unprocessed source (FX-NEG). Silence is only meaningful where coverage says covered.

---

## 7. Diagnostics and obligations

**Transformer-emitted:** `Ambiguity` (interpretations enumerated, unresolved) · `MissingInformation` · `ConflictingStatement` (spans layers when applicable) · `UnsupportedInference` · `UnresolvedReference` · `Underdetermination`.
**Audit-emitted (independent channels):** `MissedClause` · `ConflatedClause` · `MisgroundedAssertion`.
**Build-emitted:** `RealizationConflict` (§5.5).
**System-emitted:** `LapsedGroundingDiagnostic` (§5.2) · `ReevaluationObligation` (§4, §5.6 — non-blocking, co-reported, expiring by review or supersession) · **`SubsumptionNotice`** (§2 — new derivation overlaps an eligible closure; non-blocking unless conflicting; forward path is an operator supersession/retirement act).
**Act-opened:** **`GenerationDefectFinding`** (§4 — blocking, population-scoped, opened only by an authoritative act).

**Lifecycle:** `open → resolved-by-act(ratification | closure | source-amendment | retirement) → lapsed(source-change)`. Resolution is always an act. **Gating cone:** an open blocking diagnostic blocks its dependency cone — not the whole graph; cones co-report. Unchosen interpretations of resolved ambiguities are preserved as record.

> Ambiguity produces information *about* ambiguity, never silently resolved information.

---

## 8. Validation ladder and coverage (D14, D18)

### 8.1 The non-implication ladder (typed claims with recorded bases; none implies another)

`Syntactically-Valid` → `Structurally-Conformant` (SHACL) → `Logically-Consistent` (reasoner) → **`Source-Faithfulness-Audited`** `{auditPopulation, sampleSize, samplingMethod, findings, auditRate, auditor}` → `Ratified` → **`Projected`** (deterministic compile succeeded; **basis: re-projection from the same input manifest and compiler version yields a byte-identical contract** *(authored)*) → `Execution-Verified` (ledger-linked, or the claim is not made).

**`Source-Faithful`** is reserved for content under the profile's **complete** review policy; the Phase-4 reference graph receives **100% review** (§0 applied to an oracle's own precondition). *Realizable* remains out.

### 8.2 Coverage — the denominator obeys §0

**Detected-clause coverage** = represented / detected, with independent denominator channels (second segmentation method; normative-marker census; human spot-audit at **GP-A**); channel disagreement above **GP-C** opens `MissedClause`/`ConflatedClause` audits. Invention split: `ungrounded` is zero by schema (a schema property, not an achievement); `misgrounded` is audit-only, reported **with its audit rate**, never a bare zero. Coverage is a completeness control, never a proof of correctness.

---

## 9. Ratification throughput (CP-19 imported)

The ratification unit is the **Specification Record** (Requirement Record is the subtype; Non-Goals, Interface Contracts, Worked Examples, Prescribed Invariants, Journeys bundle identically): fragment text displayed **beside** derived assertions, facet breakdowns, resolved diagnostics, standalone markers, and vacuity-class flags; batched into the CP-19 queue; acts are anchoring operator acts.

**Graded acceptance (D9):** **Provisionally-Accepted** (machine-clean, unratified — consumable downstream under the PROVISIONAL cap, at provisional eligibility) vs. **Accepted** (ratified — full eligibility per §3.2). A ratified derivation rule may confer within its scope, chaining to its ratifying act. The inner loop never blocks on the queue; the acceptance verdict enforces it.

**Derivation rules are a governed authority multiplier:** versioned, content-addressed, scope-bounded, deterministic, tested, ratified, traceable; derived assertions retain `{ruleRef@version, premise IDs, execRef}`; a rule change is a manifest change — its cone lapses and requeues (FX-RULE).

---

## 10. Planned versus existing — ADR-002 gate, interim pin (D21)

> **D21 (interim, frozen).** No profile shape types a specified-X as an instance of X, **and no profile axiom — existential restriction or otherwise — may entail the existence of the prescribed entity from the existence of the requirement.** A requirement relates to a **specification-target description** (a kind reference as an information entity), never to an actual instance and never to a class used as an individual (punning discipline deferred to ADR-002; descriptions, not classes-as-values, in the interim). Realization edges (`is-realization-of`, from ledger-evidenced actuals to the description) live only in L4.

**ADR-002 — Specification Targets and Non-Actual Entities** (Phase-4 blocker): the formal OWL pattern for prescription, the punning decision, the naming ladder (specified / implemented / deployed / running) with identity through the prescription. Direction, non-binding: requirements as CCO Directive Information Content Entities.

---

## 11. The compiler boundary (D12, D15)

```
BFO / CCO → ARO TBox → Profile → eligible Accepted L2 ⊕ eligible Ratified L3
                              ↓ deterministic, non-interpretive projection (D20)
      Planner Contract · Builder Brief · Tester Contract · plan.json · seeds
```

Consumers never see raw BFO/CCO IRIs. **Facets flow through:** each projected field carries its assertion's authority facet and layer of origin, so downstream dispositions key on it — and an auditor can see that `GET /accounts/{id}` came from a closure, not the source. Negative content projects with its coverage metadata (§6).

**11.1 The Projection Input Manifest (D15, amended).** Every deterministic projection embeds or content-addresses the **complete projection-input manifest**:

```json
{ "l2": { "graphDigest": "…", "acceptanceHead": {"specDigest":"…","head":"…","seq":…} },
  "l3": [ { "designGraphDigest": "…", "ratificationHead": {…} } ],
  "semanticDependencyManifestDigest": "…",
  "compiler": { "component": "aro-project", "version": "…" } }
```

The projection carries `projectionInputManifestDigest`; the `ProjectionAct` is a ledger event. Without the L3 entries, closures create an audit hole precisely at the compiler boundary — the manifest closes it. Determinism is checked, not assumed: re-projection from the same manifest and compiler yields a byte-identical contract, and that check is the `Projected` status's recorded basis (§8.1).

**11.2 Composition with the frozen loop — no CP/SM change.** CP-5 forbids model-authored acceptance; therefore boundary oracles compile only from **eligible Accepted** acceptance clauses. Plans, contexts, and briefs may compile from Provisionally-Accepted content at provisional eligibility, and the consuming capability caps at PROVISIONAL under v0.4.1 §9's existing rule.

**11.3 What ARO projects into the loop.** `plan.json` from component/interface prescriptions; interface prescriptions with shape payloads populate the **`declared`** tier; stimulus→response paths and acceptance clauses seed capabilities; **Worked Examples** compile to CapabilityExample sources; **Prescribed Invariants** compile to Rung-4 invariant *sources* (registration remains a ratifying act under CP-14); interface requirements supply an **additive** seam-grain matrix seed in union with plan `depends_on` edges — a discrepancy between the two seeds is itself a diagnostic.

**11.4 Integration items (deferred to a CP/SM version bump; the freeze holds):** INT-1 matrix seed union · INT-2 `declared`-tier ingestion rules · INT-3 RealizationConflict as a recognized finding source in the loop's co-reported ledgers.

---

## 12. Term map — ARO ↔ CP/SM (normative appendix; D16)

| ARO | CP/SM | Note |
|---|---|---|
| authority facet (computed) | AUTHORITATIVE (§1.2, by reference) | operator-origin ≙ operator-authored; ratified ≙ ratified; ratified-rule chain ≙ invariant-ratification channel; spec-derived ≙ ratified deterministic extractor over a registered source |
| **eligibility (§3.2)** | **the fold's current view over append-only acts** | authority ≠ history, applied to ARO's own semantics; lapse suspends, never erases |
| Candidate content | `model-proposed(unratified)` | never gates |
| Accepted Graph | ratified standard (`oracles/`-class, attested head) | acceptance = anchoring act |
| semantic dependency manifest | freeze keys / CP-16 supersession | lapse-and-requeue on manifest change only |
| **Projection Input Manifest** | attested-head / freeze-key family | complete input identity at the compiler boundary |
| `ReevaluationObligation` | co-reported debt ledger entry | non-blocking freshness |
| **`GenerationDefectFinding`** | **escape protocol / defect response** | population-scoped, act-opened, blocking |
| Transformation / Projection Acts | ledger events | run-root storage |
| Diagnostic / cone | finding / blocked-cone discipline | lifecycle ≙ finding lifecycle |
| validation statuses | CP-21 typed bases | `Source-Faithfulness-Audited` carries its sample; `Projected` carries its determinism check |
| coverage report | graded `(n, k, provenance)` reporting | independent denominator channels |
| Specification Record + queue | CP-19 unit + queue | display duties imported |
| Provisionally-Accepted | PROVISIONAL | composes via CP-5 + §9 (§11.2) |
| L4 Evidence | assembly-ledger projection | coordinates, never copies |
| reference graph / **constraint set** | **witness / contract** | the founding lesson applied to the reference itself |
| **Worked Example** / **Prescribed Invariant** | CapabilityExample source / Rung-4 invariant source | runtime **Witness** keeps its meaning: receipts |
| Acceptance Clause | boundary-oracle source | eligible-Accepted-only per CP-5 |

---

## 13. Fixture corpus — two classes

**Unit class (uniqueness rule):** each fixture fails exactly one check; with that check disabled (test-assembled only; no production disable surface), the suite passes, wrongly.

- **FX-INVENT** — invented framework/path/database → N1 shape gate only.
- **FX-DROP** — detected normative clause unrepresented → detected-clause coverage only.
- **FX-MISS** *(the §0 fixture)* — clause the primary segmenter misses; only the independent denominator channel catches it.
- **FX-CONFLATE** — two clauses merged → audit channel only.
- **FX-MISGROUND** — cited fragment does not support the assertion; schema-clean → audit/adversarial only.
- **FX-EXAMPLE** — "for example, Docker" as candidate requirement → role gate only.
- **FX-AMBIG** — ambiguity → diagnostic with enumerated interpretations + blocked cone; silent resolution fails.
- **FX-NEG** — projection flattening prohibition/non-goal into `unspecified`, or shipping `unspecified` without coverage state → projection-preservation only.
- **FX-CLOSURE** *(two branches)* — (a) a closure claiming `groundedBy`, or any groundless assertion in L2 → the graph rule only; (b) a closure citing `rationaleSource` **passes** — citation is free.
- **FX-LAPSE** *(two branches)* — (a) source edit → fragments lapse, migration proposed, acceptance requeued; a stale acceptance still gating fails; (b) declared-ID continuity flows mechanically under the ratified identity policy while inferred continuity auto-passing fails.
- **FX-RULE** — derivation-rule supersession lapses exactly its dependency cone.
- **FX-EQUIV** *(anti-canonization)* — a semantically equivalent alternative structuring passes the constraint oracle; fails only if the Phase-6 oracle over-fits one modeler's representation.
- **FX-PROJ** *(authored)* — a Builder Brief containing closure-supplied content whose projection-input manifest omits the consumed L3 head → manifest-completeness check only.
- **FX-STALE** *(authored)* — an L2 assertion a closure `closes` is superseded; the closure's eligibility suspends; a projection still consuming it fails → closure-lifecycle rule only.
- **FX-RECLASS** *(authored)* — a newly ratified rule derives content overlapping an eligible closure → `SubsumptionNotice` opens; historical membership unchanged; a suite that silently reclassifies the closure to L2 fails.
- **FX-DEFECT** *(authored, two branches)* — (a) a generation-provenance version change alone stays non-blocking (`ReevaluationObligation`); (b) an act-opened `GenerationDefectFinding` suspends eligibility across exactly the affected population; a suite where (a) blocks or (b) fails to block fails.

**Integration class (composition rule):** **FX-COMPOSE** — invented framework + misgrounded citation + dropped clause in one candidate: all three detectors fire, cones block correctly, diagnostics co-report with correct precedence, no early-exit masking. Single-fault fixtures prove detector uniqueness; multi-fault fixtures prove composition.

Reference-graph authorship is held out from whoever builds the transformer.

---

## 14. Foundational decisions — D1–D24

- **D1** Reality / specification / design / artifact / activity separated (four products + projection).
- **D2** Requirement is prescriptive information content (CCO Directive ICE direction; ADR-002).
- **D3** Identity ≠ expression ≠ record ≠ revision ≠ fragment; continuity mechanical only via a ratified identity policy over source-declared identifiers; inferred continuity is a ratified act.
- **D4** Need, requirement, design, realization, evidence remain distinct.
- **D5** Grounding = bundles of Source Fragments with roles, retained through derivation ancestry; Fragment abstract, Text Span its RLA implementation; normalization versioned in the manifest.
- **D6** Unsupported information remains absent (N1); on absence: representable absence, a diagnostic, or a labeled L3 proposal — never silent completion.
- **D7** Ambiguity produces diagnostics with enumerated interpretations; unchosen readings preserved.
- **D8** Role × force × scope disposition, with coverage state on its own axis; only role: Normative gates; the §6 projection rule.
- **D9** Candidate content never gates; acceptance is graded and composes with loop dispositions via CP-5 + the PROVISIONAL cap, at the eligibility grade claimed.
- **D10** Evidence is a ledger projection, never a store.
- **D11** BFO/CCO are the approved ontological dependencies; prior art (PROV-O, SHACL ValidationReport, ReqIF, OSLC RM, SysML v2) reviewed and mapped adopt-or-justify; any namespace import beyond BFO/CCO is a dependency-policy expansion requiring architect ratification.
- **D12** ARO shields consumers from raw BFO/CCO identifiers.
- **D13** Profiles govern application-specific constraints; authority-bearing, version-keyed manifest members.
- **D14** Validation claims are distinct typed claims with recorded bases; `Source-Faithfulness-Audited` carries its sample; `Source-Faithful` requires complete review; the reference graph gets 100%; *Realizable* is out.
- **D15** *(amended)* Contracts are deterministic compiled projections that **embed or content-address the complete Projection Input Manifest** — the exact Accepted L2 graph, all Ratified L3 content consumed, their acceptance/ratification heads, the semantic dependency manifest, and the compiler version — with re-projection determinism as the recorded basis of `Projected`.
- **D16** Substrate unification with declared delivery: one authority class (by reference), one ledger, one anchoring model, one queue discipline; the term map is normative; CP/SM v0.4.1 + `1b7f3c1` are normative accompanying dependencies.
- **D17** *(amended)* **Membership by semantic nature; derivability bounded by the active environment.** L2 = source semantics (directly grounded, or rule-derived over grounded AUTHORITATIVE premises under the derivation environment identified by the semantic dependency manifest); L3 = engineering closures (not asserted or derivable under that same environment). L3 forbids `groundedBy`, permits `rationaleSource`. History never reclassifies; environment changes act forward through supersession (`SubsumptionNotice`).
- **D18** Coverage denominators carry independent channels with disclosed rates; invention splits ungrounded (schema-zero) / misgrounded (audit-rated).
- **D19** *(amended)* Acceptance binds to content + the semantic dependency manifest; manifest changes **lapse eligibility** and requeue; generation provenance is recorded, non-lapsing, opens `ReevaluationObligation`s — with the **defect-finding path**: an authoritative `GenerationDefectFinding` may block an affected population. **Ratified L3 closures retain explicit dependencies on the L2 assertions, records, or diagnostics they close; supersession or lapse of those dependencies requeues the dependent L3 cone; a stale closure MUST NOT remain eligible for projection merely because its ratification act remains historically valid.** Standalone closures carry the attested marker. The round trip (RealizationConflict) runs ledger findings back into graph amendment.
- **D20** Source interpretation confined to the transformation-and-ratification boundary; design judgment to L3 closure acts; projection deterministic and non-interpretive.
- **D21** Interim pin per §10 with the OWL existence-entailment prohibition and interim punning discipline; ADR-002 before Phase 4.
- **D22** The transformer's honesty boundary: channels it cannot self-report get independent detectors with fixtures.
- **D23** *(amended)* Assertion identity: stable, machine-addressable, sufficient for grounding, derivation, diagnostics, ratification, supersession, and cone membership; the statement-provenance pattern **and canonical graph identity** fixed by ADR-003 before Phase 3; **one canonicalization implementation** for digest, addressing, and diff, versioned in the manifest; **fragment identity = source digest + kind + canonical locator + normalization version + content hash**, with migration as a relationship, never identity.
- **D24** *(amended)* Orthogonal provenance facets; **authority is computed from append-only acts and is historical — it never disappears on lapse. Eligibility to gate or project is a distinct, fold-computed state predicate (§3.2)**; no facet substitutes for another; no parallel authority class exists.

---

## 15. Module architecture

```
aro-core.ttl          aro-requirements.ttl     aro-provenance.ttl   (facet model; PROV-O mapping recorded, not imported)
aro-transformation.ttl aro-traceability.ttl    aro-verification.ttl
aro-diagnostics.ttl   aro-design.ttl           (L3 shapes: closure dependencies, standalone marker, rationaleSource, no groundedBy)
rules/                (derivation rules + identity policies: versioned, content-addressed, scope-bounded, tested)
profiles/  aro-rla-profile.ttl · aro-rla-shapes.ttl · aro-rla-design-shapes.ttl · aro-rla-context.jsonld
examples/  rla-source.md · rla-hand-authored.jsonld · rla-transformed.jsonld · rla-constraint-set.jsonld
           fx-invent · fx-drop · fx-miss/ · fx-conflate · fx-misground · fx-example · fx-ambig · fx-neg/
           fx-closure/ · fx-lapse/ · fx-rule/ · fx-equiv/ · fx-proj/ · fx-stale/ · fx-reclass/ · fx-defect/ · fx-compose/
later/     aro-stakeholders.ttl · aro-interfaces.ttl · aro-software.ttl   (on demonstrated need)
```

---

## 16. Phased build

- **Phase 1 — architect ratification of this document** (amended D-set, term map, D21 pin, ADR gates). Ratification is the architect's act; this document does not pronounce it.
- **Phase 2 — minimal TBox** on BFO/CCO; prior-art mapping decisions recorded per D11.
- **ADR-003** — assertion identity + canonical graph identity + **fragment locator criterion**: Phase 3 cannot exit without it.
- **Phase 3 — RLA profile**: JSON-LD context, SHACL shapes (L2/L3/fragment/classification/closure-dependency), the identity policy as a ratified rule, the single canonicalization component.
- **ADR-002** — planned-vs-existing formal pattern: before Phase 4.
- **Phase 4 — reference graph + constraint set**: hand-authored reference graph (held-out author, 100% source-faithfulness review) through the full pipeline manually, ratified alongside the **transformation acceptance constraint set** (required/forbidden assertions keyed to fragments, traceability constraints, coverage and diagnostic expectations, competency-query answers, graph invariants).
- **Phase 5 — projection compiler**: contracts + plan.json + seeds, Projection Input Manifests embedded, determinism checks recorded; success gate: the RLA pipeline runs against projected contracts and the terminal result is truthful.
- **Phase 6 — automated transformation.** Oracle = the constraint set (the contract); the reference graph is its first witness. Canonical diff only where the profile prescribes a pattern; elsewhere equivalence under constraints; ambiguous regions yield permitted alternatives or diagnostics, never silently chosen readings. FX-EQUIV is the anti-canonization tripwire.
- **Phase 7 — adversarial suite**: both fixture classes; audit calibration (GP-A, GP-C); stochasticity policy under the shared canonicalizer.
- **Phase 8 — generalization**: second profile; broader model per the §1 scope rule.

Exit per phase: its fixtures behave as specified, prior fixtures hold, every acceptance and projection act anchored. **Governance parameters:** GP-A audit sampling (initial 10%; 100% for the reference graph) · GP-B ratification batch cadence · GP-C detection-channel disagreement threshold (initial: any) · GP-D re-evaluation review cadence.

---

## 17. Watch items

1. **ADR-002 depth** — the OWL existence trap and punning; the interim pin holds meanwhile.
2. **ADR-003 selection pressure** — the statement-provenance pattern shapes every SHACL rule downstream; decide once, early; the fragment-locator criterion is in its acceptance set.
3. **Oracle-equivalence policy per profile** — prescribed-pattern regions (diff) vs. constraint-equivalence; FX-EQUIV is the tripwire.
4. **Undeclared L2↔L3 semantic conflicts** — mechanically caught only through declared dependencies; backstops are the round trip, review, and cross-layer ConflictingStatement. A bounded mechanism, stated as such (§5.6).
5. **Derivation-rule scope creep** — the authority multiplier is governed but attractive; watch rule count and scope per release; `SubsumptionNotice` volume is the early signal.
6. **Operator load** — hundreds of Specification Records per real spec; measure queue depth from Phase 4; calibrate GP-B/GP-D.
7. **Multi-source precedence** — conflicts across registered sources are `ConflictingStatement` diagnostics; precedence is a closure, never an inference.
8. **INT-1..3** — await a CP/SM version bump; nothing here presumes it.

---

## 18. Change log — v0.4 → v0.5 (published)

The review's five blockers and two hardenings, dispositioned:

1. **Authority vs. eligibility (blocker 1):** §3.2 added — authority is computed from append-only acts and is historical; **eligibility** is the fold-computed state predicate (effective graph, current manifest, clean cone, current closure dependencies); lapse suspends eligibility and rewrites nothing; §11.2 and all gating language now read *eligible* content; D24 amended. No new authority class (D16 holds).
2. **Projection Input Manifest (blocker 2):** D15 amended; §11.1 — complete input identity (L2 + all consumed L3 + manifest + compiler), content-addressed, ProjectionAct on the ledger; *(authored)* re-projection determinism as the recorded basis of `Projected`; FX-PROJ added.
3. **L3 by decision authority, not origin (blocker 3):** §2 table and prose reworded — ratified engineering closures, proposals from operator or transformer, D24 records who proposed; resolves the document's own conflict between §2's wording and D24's orthogonality.
4. **Closure lifecycle (blocker 4):** §5.6 added; D19 amended — declared closure dependencies (closes/addresses/dependsOn) are lapse-bearing; stale closures lose eligibility despite historically valid ratification; *(authored)* the **standalone** attested marker for free-standing closures (forced fake edges would be invented grounding one level up); *(authored)* rationale supersession opens a non-blocking ReevaluationObligation; the honest limit on undeclared conflicts stated and watch-listed; FX-STALE added.
5. **Bounded derivability (blocker 5):** D17 amended — derivability relative to the active ratified derivation environment in the manifest; history never reclassifies; *(authored)* `SubsumptionNotice` + operator supersession as the forward path; FX-RECLASS added.
6. **Fragment locator (ADR-003 criterion):** §5.1 and D23 amended — identity formula with canonical locator and normalization version; migration is a relationship, never identity.
7. **Defect-finding hardening:** §4 — `GenerationDefectFinding`, act-opened, population-scoped, blocking through the ordinary cone rule; version change alone never blocks; FX-DEFECT added *(authored, two branches)*.
8. **Numbering:** published as v0.5 (issued versions freeze); the review's approval conditions are discharged; Phase-1 ratification is the architect's act and is not pronounced here.

**Unchanged:** everything on the review's now-solid list — the orthogonal facet model, Source Fragments, the D21 OWL guard, the classification split, `Source-Faithfulness-Audited`, the constraint-set-as-contract oracle, derivation-rule governance, FX-EQUIV and FX-COMPOSE — and the v0.3 keep-list beneath it.
