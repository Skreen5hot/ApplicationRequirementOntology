# Handoff plan — the sequence

`HANDOFF.md` is **state**: what is in this repository and what can be trusted.
This is **sequence**: what happens next, in what order, and who owns each piece.

The division running through all of it: **the checks are infrastructure; the
answers are ontology.** A tool can prove that two inlined copies of
`ex:ActOfForecasting` disagree. Deciding which one is right is a judgement about
what the term denotes, and no tool should make it.

---

## 1. Before handover

| item | status |
|---|---|
| Method carried over (`PROCESS.md`) | done |
| Layout contract, licensing, line endings | done |
| ISO exposure removed and verified 404 | done |
| BFO + CCO vendored, pinned, regenerable | done |
| SHACL ladder evaluable, both rungs falsified | done |
| Corpus index derived again (`build_index.py`) | done |
| Well-formedness gate + baseline | done |
| Handoff documents | this file |

Exit criterion: every gate in §2 green on a clean CI checkout, not on a working
tree.

---

## 2. Day one

```bash
git clone https://github.com/Skreen5hot/ApplicationRequirementOntology
cd ApplicationRequirementOntology
python -m venv .venv && .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
```

Then run the six gates. Each should pass; if one does not, that is the first
thing to fix, before any ontology work:

```bash
python tools/layout.py                         # the contract describes the tree
python tools/licensing/disposition.py --check  # nothing unpublishable is tracked
python tools/ontology/vendor_upstream.py       # extracts cover what the shapes walk
python tools/ontology/build_index.py --check   # the corpus index is not stale
python tools/ontology/validate.py --gate       # no new ontology findings
python -m pytest tests/ -q -p no:randomly      # 6-11 minutes
```

Read in this order: `HANDOFF.md` (what is here), `DEVELOPMENT.md` (how to work),
`PROCESS.md` (why it is built this way). The third is the one that explains the
other two, and it is short.

---

## 3. The ARO team's sequence

In dependency order. Each exit criterion is quoted from
`aro-specification-graph-v0.5.2.md` rather than invented here — where the
specification is silent, it says so.

### 3.1 Phase 1 — ratification (blocks everything)

§16: *"architect ratification of this document … Ratification is the architect's
act; this document does not pronounce it."* Nothing in this repository records
that it has happened.

**Exit:** the ratification, or the list of blockers, recorded in the repository.
A decision that lives only in somebody's memory is not a decision the next person
can rely on.

**Owner:** the architect. Not a tooling task.

### 3.2 ADR-003 — assertion and graph identity (do this first among the ADRs)

§16: *"Phase 3 cannot exit without it."* §17 watch item 2 is the argument for
doing it before anything else: *"the statement-provenance pattern shapes every
SHACL rule downstream; decide once, early."*

Covers assertion identity, canonical graph identity, and the fragment locator
criterion (§5.1, D23).

**Exit:** an ADR in `docs/adr/`, and — because this is what makes it real — a
worked example plus the SHACL shape that enforces the chosen pattern, with its
negative fixture.

### 3.3 ADR-002 — planned versus existing

Required before Phase 4. §17 watch item 1 flags the OWL existence trap and
punning; the D21 interim pin holds meanwhile.

### 3.4 Phase 2 — minimal TBox

§16: *"minimal TBox on BFO/CCO; prior-art mapping decisions recorded per D11."*
The modules are listed in §15: `aro-core.ttl`, `aro-requirements.ttl`,
`aro-provenance.ttl`, `aro-transformation.ttl`, `aro-traceability.ttl`,
`aro-verification.ttl`, `aro-diagnostics.ttl`, `aro-design.ttl`.

**Expect to widen the vendored extracts here.** They deliberately drop every
axiom whose object is an anonymous class expression — 44 of them — so they carry
no OWL restrictions. A TBox that reasons over CCO restrictions will need them.
The lever is `STRUCTURAL` in `tools/ontology/vendor_upstream.py`, and the
serialiser will need to handle blank nodes deterministically, which it currently
refuses to do on purpose. That refusal is a guard, not an oversight: read the
docstring before removing it.

Each new module needs a layout component, and each new shape set needs its
negative fixture **in the same commit** — see §5.

---

## 4. Debt register

Everything known to be owed, with an owner and an exit criterion. Nothing here is
hidden; all of it is enforced by a check that fails if it grows.

### 4.1 Fifty-one drifted definitions and six drifted labels — *ARO team*

The same IRI means different things depending on which file is read.
`ex:ActOfForecasting` is defined one way in `apqc-ext.ttl` and five slices, and
another way in `apqc_10_0.ttl`.

Recorded in `config/validation-baseline.json` as
`validation.wellformedness: 57`, gated in CI.

**The root cause is architectural, and it is your call.** The slices *inline* the
shared genera instead of importing `apqc-ext.ttl`. That was deliberate — the
layout contract says "slices mirror what they use rather than importing it" — and
it is what allows fourteen copies of a term to drift apart. Two ways out:

1. **Fix the values.** 57 judgements about what each term means. The gate then
   goes to 0 and stays there.
2. **Remove the mechanism.** Have the slices import the extension module. The
   whole class of defect disappears, at the cost of the self-containment the
   slices were designed for.

The shape catches the symptom either way. Only you can choose between these.

**Exit:** `validation.wellformedness` at 0 in the baseline, re-recorded.

### 4.2 Ten APQC findings — *ARO team*

5 process classes missing `ex:pcfID`, the same 5 missing `skos:example`:
`AuthorArchitecture`, `AuthorImplementationPlan`, `AuthorRoadmap`,
`EvaluateOutput`, `ImplementPhase`. Adding a `pcfID` requires knowing the APQC
element ID, which is a fact about the source, not about the code.

**Exit:** `validation.apqc-shapes` at 0.

### 4.3 Two orphaned artifacts — *ARO team*

`APQC_ontology/reports/` (18.9 MB, asserting an ELK reasoner result nothing here
can reproduce, and a `matchability.json` describing an agent fleet from a
different project) and `APQC_ontology/reference/apqc_1_1_1.ttl`.

Both are declared `orphaned` in the layout contract with the reason, and
`tests/test_repository_layout.py` fails if that list changes without a decision.

**Either** write the generators — `build_index.py` is the worked example of
discharging one — **or** delete them. `tools/ontology/validate.py` already
supersedes the gate reports with something reproducible. Leaving them is the one
option that is not fine.

**Exit:** the orphan list empty, or the components gone from the contract.

### 4.4 CI runtime — *whoever it annoys first*

CI runs the SHACL ladder twice: once inside the suite and once for `--gate`, in its
own process. They cannot share a report, because a
test may not read build output (`PROCESS.md` §9). The lever is marking the SHACL
tests slow and splitting the run. Not urgent; it will be.

---

## 5. Conventions that must survive

Each of these exists because it was violated first. They are not style.

- **A new shape set arrives with its negative fixture in the same commit.**
  `capabilities_roles_shapes.ttl` did not, and spent its whole life either
  reporting the scope or reporting a zero nobody could interpret.
  `tests/test_ontology_checks.py` enforces it.
- **Regenerate the index** after any corpus change. `--check` runs in CI.
- **Re-vendor** when a module names an upstream term not yet extracted. The
  offline check names the missing terms.
- **Never `git push --tags` or `--mirror` on this repository.** A
  `backup-before-pdf-removal` tag once held four copyrighted PDFs alive; it was
  never pushed, and pushing tags would have re-uploaded an ISO standard to a
  repository that had just been recreated to remove it.
- **Falsify every check against a state verified different.** Not assumed
  different: an attempt to falsify `build_index.py --check` once edited a line
  that did not contain what the edit searched for, so the file never changed and
  the check passed correctly. The test was broken, not the tool.
- **Say what was not done.** Every record states its own limits. A partial
  extract that does not say it is partial is the defect this whole method exists
  to catch.

---

## 6. What "handover complete" means

Declarable, so it does not drift:

1. Phase 1 ratification recorded, or its blockers recorded (§3.1).
2. `docs/adr/` exists and ADR-003 is written (§3.2).
3. The team has run all six gates on their own machine and CI is green on a
   commit of theirs.
4. Someone on the team has fixed one finding and re-recorded the baseline —
   the smallest end-to-end proof that they can operate the machinery, not just
   read about it.
5. A decision recorded on §4.1 and §4.3, even if the decision is "not yet".

Item 4 is the one that matters. Everything else can be true of a repository
nobody has actually picked up.
