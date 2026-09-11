# Handoff — state of the repository

Written 2026-09-10, at commit `da91905` plus the changes in the commit that adds this file.

Read this before `README.md`. The README says what the project is *for*; this says what
is actually here, what is trustworthy, and what is not.

---

## 1. The one-paragraph version

**The method and the infrastructure are ready. The Application Requirement Ontology is
not written yet.** What this repository contains today is (a) a working, tested,
reproducible checking apparatus, (b) a large APQC business-process ontology inherited
from earlier work that serves as the BFO/CCO-aligned foundation, and (c) a ratified-in-
draft specification for the ARO itself, `docs/aro-specification-graph-v0.5.2.md`, whose
Phase 2 onwards is unstarted. A new team can start building ARO modules on day one and
the gates will hold them honest. They should not assume the ontology they are inheriting
is the ARO.

---

## 2. What is ready to rely on

| Area | State |
|---|---|
| Method | `docs/process/PROCESS.md` — 12 sections, carried from the project where it was worked out |
| Layout contract | `config/repository-layout.yaml`, 33 components; every tracked file has a declared role, and both directions are policed |
| Licensing | 4 dispositions, exactly one per tracked file, derived from role plus adjudication; attribution for vendored work is checked, not assumed |
| Upstream vocabulary | BFO 2020 and CCO v2.2 vendored as pinned partial extracts; regenerable and byte-identical; weekly CI job refetches and compares |
| SHACL ladder | `tools/ontology/validate.py`; both shape sets evaluable, both falsified by a negative fixture |
| Corpus digest | `config/corpus-digest.json`; pinned, and compared against a fresh measure by a test |
| Corpus index | `tools/ontology/build_index.py`; derived from the ontology, `--check` in CI, classification anchored in the vendored BFO/CCO |
| Known findings | `config/validation-baseline.json`; 67 of them, gated in CI so the count can only go down |
| Line endings | `.gitattributes`, applied before the corpus grew |
| CI | `.github/workflows/checks.yml`; actions pinned to commit SHAs |
| Tests | 84, all passing, 6-11 minutes (almost all of it SHACL; the machine varies) |

Everything in that table has a test behind it, and — per `PROCESS.md` §2 — the tests have
been falsified: the fix reverted, the specific check required to fail, then restored.

---

## 3. What is actually in the ontology

Not the ARO. The corpus is **62,646 triples across 18 files**, **3,119 authored classes**,
in the `https://fandaws.com/ontology/` namespace:

- 13 section slices of the APQC Process Classification Framework, plus `apqc-catalog.ttl`
  and the shared extension module `apqc-ext.ttl`
- a capability and role layer: 116 classes ending in `Capability`, 95 ending in `Role`
- `capabilities_wiring.ttl`, the Phase-1 bridge from processes to required capabilities
  and roles

Searching it for ARO vocabulary finds APQC business-process names, not ARO classes:
`Stakeholder` matches 7 things, `Requirement` matches 40 — `ApplicableRequirementsDetermination`,
`ChannelRequirements` — and `SourceFragment`, the central identity concept of the
specification, matches nothing. **None of the modules in §15 of the specification exist:**
`aro-core.ttl`, `aro-requirements.ttl`, `aro-provenance.ttl`, `aro-transformation.ttl`,
`aro-traceability.ttl`, `aro-verification.ttl`, `aro-diagnostics.ttl`, `aro-design.ttl`,
`rules/`, `profiles/`, `examples/`.

So the correct mental model is: **an aligned, validated foundation plus a specification,
with the ARO TBox still to be written on top.**

---

## 4. Where the specification stands

`docs/aro-specification-graph-v0.5.2.md` — 391 lines, published at v0.5.2 (amended; v0.5 and v0.5.1 absorbed), with 24 numbered
foundational decisions (D1–D24), a term map, a module architecture (§15), an eight-phase
build (§16) and eight watch items (§17).

Its own §16 says Phase 1 is **architect ratification of the document itself**, and that
"this document does not pronounce it". *Nothing in this repository records that
ratification having happened.* That is the first thing to settle, because Phase 2 depends
on it and two ADRs are hard gates:

- **ADR-003** — assertion identity, canonical graph identity, fragment locator criterion.
  §16: "Phase 3 cannot exit without it."
- **ADR-002** — planned-versus-existing formal pattern. Required before Phase 4.

Neither ADR exists, and there is no `docs/adr/` directory. Creating one and writing those
two is the highest-value early work, and §17 watch item 2 explains why: the
statement-provenance pattern shapes every SHACL rule downstream, so it must be decided
once, early.

---

## 5. What not to trust

### 5.1 Two artifacts nothing here can rebuild

The contract now records these as `orphaned`, `python tools/layout.py` prints them, and
`tests/test_repository_layout.py` fails if the list changes without a decision. They are
still in the tree:

| Component | Problem |
|---|---|
| `APQC_ontology/reports/` | 18.9 MB of reasoner output and gate results. **15 of 17 gate reports name a module path that does not exist here** (`ontology\slices\apqc_1_0.ttl`). All of them assert "D Reasoner: consistent; no unsatisfiable classes (ELK)" — no reasoner of that kind is in this repository, so nothing can reproduce it. `matchability.json` describes an agent fleet of 12, which belongs to a different project. |
| `APQC_ontology/reference/apqc_1_1_1.ttl` | One derived extract; nothing states what from, or how. |

Both were **text-edited** during the namespace migration, which is the one thing a
generated artifact must never need. Until recently the contract described them as
"Regenerated, not edited" — a property nothing could deliver. That is the defect class
`PROCESS.md` opens with, and it was sitting in the contract.

The third, `APQC_ontology/index/corpus_index.tsv`, **has been discharged** —
`tools/ontology/build_index.py` now writes it, CI compares it against a fresh build on
every push, and the contract names the generator instead of admitting there is none. It
was the worst of the three, because its README told readers to grep it in preference to
reading a slice.

For the two that remain, the team should pick one of:

1. **Write the generators**, as was done for the index.
2. **Delete them.** `tools/ontology/validate.py` already supersedes the gate reports with
   something reproducible. Deleting somebody else's evidence is not a call to make
   quietly, which is why it has been left.

### 5.2 Sixty-seven open findings against the ontology

All recorded in `config/validation-baseline.json` and gated in CI, so the number can only
go down:

| shape set | findings | what |
|---|---|---|
| `validation.apqc-shapes` | 10 | 5 process classes missing `ex:pcfID`, the same 5 missing `skos:example` — `AuthorArchitecture`, `AuthorImplementationPlan`, `AuthorRoadmap`, `EvaluateOutput`, `ImplementPhase` |
| `validation.wellformedness` | 57 | the drift in §5.3 — 51 definitions, 6 labels |
| `validation.capabilities-roles-shapes` | 0 | — |

These are real defects in the corpus, not artifacts of scope. `--record` refuses to raise
any of these counts without an explicit reason, so the register cannot quietly grow.

### 5.3 The inlined slice copies have drifted

Found while writing the index generator, and new: **51 terms carry more than one
distinct `skos:definition`, and 6 carry more than one distinct `rdfs:label`.** The
slices inline the shared genera instead of importing them, and the copies have moved
apart, so the same IRI means different things depending on which file is read.
`ex:ActOfForecasting` is defined one way in `apqc-ext.ttl` and five slices, and another
way in `apqc_10_0.ttl`.

The previous index hid this by reading one file. `build_index.py` resolves it by a stated
rule — the canonical home wins — and reports the count on every run.

**It is now a gate.** `shapes/wellformedness_shapes.ttl` asserts that no authored term
carries two values of the same property in the same language, and
`python tools/ontology/validate.py --gate` fails if the count rises. The SHACL run and
`build_index.py` reach 57 independently, by different routes, which is the corroboration
— neither is evidence alone.

This is a real corpus defect and **it is not fixed**. Fixing it means deciding which
definition is right for each of the 51 terms, which is a judgement about what the term
denotes. See `docs/HANDOFF-PLAN.md`.

### 5.4 The vendored extracts are partial, deliberately

`vendor/bfo/` and `vendor/cco/` carry only the terms this repository names plus their
named ancestry. **44 axioms were dropped** — every one whose object is an anonymous class
expression. A reasoner over them derives strictly less than one over BFO or CCO, and they
**cannot be used to claim consistency with either**. If the ARO work needs OWL
restrictions from upstream — and §16 Phase 2 probably will — the extractor's `STRUCTURAL`
closure needs widening and the blank-node drop needs revisiting. That is a known,
recorded limit, not an oversight.

---

## 6. Outside the repository

- **The ISO purge is still outstanding.** Commit `c22d707` served ISO/IEC/IEEE 29148 from
  a public raw URL. History has been rewritten and force-pushed, but an unreferenced
  commit still resolves by SHA on GitHub until Support purges it. **This requires a
  request to GitHub Support and is not something a tool can do.** Until then, treat the
  exposure as live. The PDFs remain on disk, gitignored, and `tracked: false` in the
  contract with a test asserting they are absent from the index.
- **`main` is ahead of `origin/main`.** Nothing here has been pushed since the vendoring
  commit.

---

## 7. Suggested first week

1. **Settle Phase 1.** Record the architect's ratification of `aro-specification-graph-v0.5.2.md`,
   or record what is blocking it. Everything downstream is gated on it.
2. **Create `docs/adr/` and write ADR-003.** Assertion identity and the fragment locator
   criterion. §17 watch item 2 is the argument for doing it before anything else.
3. **Decide the two remaining orphans** — `APQC_ontology/reports/` and
   `APQC_ontology/reference/`. Write generators, or delete. Either is fine; leaving them
   is not. The index shows what discharging one looks like.
4. **Fix the ten findings**, or record why they stand. Lower the pinned count in the same
   commit — the test message says so.
5. **Start `aro-core.ttl`** with a matching shape set *and* a matching negative fixture in
   the same commit. `capabilities_roles_shapes.ttl` shipped without one and reported zero
   violations for as long as its vocabulary was missing; see §8 below.
6. **Ask for the GitHub Support purge.**

---

## 8. The one habit worth keeping

`PROCESS.md` is not decoration. Its opening claim — *a check must report on the thing it
claims to report on* — was violated four times during the setup of this repository alone,
including once inside the layout contract and once in the licensing tool's own failure
path, which raised `NameError` instead of reporting the breach it had correctly detected.
Both were found by falsification: reverting the fix and requiring the specific check to
fail.

The concrete rule: **a new shape set arrives with its negative fixture in the same
commit.** `capabilities_roles_shapes.ttl` did not, and for as long as CCO was absent it
reported 202 violations that were entirely an artifact of the scope; the moment CCO
landed it reported zero, and there was nothing to distinguish that zero from a constraint
selecting nothing. It has nine named negative cases and three positive controls now.

---

## 9. Where to look

| Question | File |
|---|---|
| How is this repository built? | `docs/process/PROCESS.md` |
| How do I run things? | `docs/DEVELOPMENT.md` |
| What is the ARO meant to be? | `docs/aro-specification-graph-v0.5.2.md` |
| Where does file X live, and what is it? | `config/repository-layout.yaml`, `python tools/layout.py` |
| May this be published? | `python tools/licensing/disposition.py` |
| What did we take from BFO/CCO? | `config/upstream-extracts.json`, `vendor/NOTICE.md` |
| Is the ontology valid? | `python tools/ontology/validate.py` |
