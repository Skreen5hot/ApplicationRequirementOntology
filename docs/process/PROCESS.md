# How this repository is built

Carried over from the BFO-Aligned ValueNet project, which used this method
through eight gated phases. It is written down because the method is worth
more than any of the tools, and because most of it was learned by getting
things wrong in ways that looked right.

Nothing here is aspirational. Every rule below exists because its absence
produced a specific defect that shipped or nearly shipped.

---

## 1. The one idea

**A check must report on the thing it claims to report on.**

That sounds too obvious to write down. It is, by a wide margin, the most
frequent defect this project has found — eight distinct instances, every
one of which produced a green result that meant nothing:

| What was claimed | What was actually measured |
|---|---|
| every tracked file was swept | the three new files were untracked, so none were opened |
| the orchestrator exited 0 | `\| tail` exited 0; the program had failed |
| the category is derived from edges | a helper property; replacing the function with `endswith("Disposition")` passed all 22 tests |
| the corpus is UTF-8 clean | `text=True` decoded as cp1252 and corrupted 3 of 12 files, then blamed the corpus |
| ontology text never becomes markup | the scan matched the comment *explaining* the rule |
| the workflow checks out full history | the string `fetch-depth: 0` appeared in a comment while the step said `1` |
| no fragment went unverified | the test read a key the tool never returned, so it examined an empty list |
| the published checksums verify | they listed three files that are not published and omitted the archive that is |

The pattern is always the same: something adjacent to the question was
measured, and the adjacency was invisible from the result. A passing test
is not evidence. **Evidence is a passing test plus a demonstration that it
can fail.**

---

## 2. Falsification is not optional

Before a check counts as done:

1. **Break the thing it protects.** Revert the fix, plant the defect,
   introduce the typo.
2. **Assert the mutation applied** — `assert mutated != original` — before
   running anything. Three separate "successful falsifications" in ValueNet
   were no-ops: a `.replace()` that matched nothing, a tamper that set a
   value already equal, a mutation calling a function that did not exist.
3. **Require the specific test to fail**, and check *which* tests failed.
   A mutation that fails twenty tests including unrelated ones is usually a
   broken mutation, not a strong check.
4. **Restore, and confirm the restore.**

### Falsify the right thing

A falsification can miss for the same reason a check can. When a corpus
edit failed to move a digest that should have moved, the first conclusion
was that the pin was broken. It was not: the edit had landed on an *object
property's* definition, and the index only reads classes. The pin was
right and the falsification was aimed at something the measurement never
looked at.

Aim mutations at the exact artifact under test, and say which one you hit.

### Stage before you mutate

`git checkout -- <file>` restores from the index. Twice, work that was
never staged was destroyed by "restoring" after a falsification. Stage the
intended state first, or copy it somewhere outside the repository.

---

## 3. Gates, and who holds them

Work happens in phases. Each phase ends at a **gate**, and a gate is held
by a person who did not do the work.

- The gate states its conditions **before** the phase starts.
- Nothing is pushed without explicit authorization.
- A phase that adds tests is expected to be red against the previous
  evidence baseline; the evidence commit follows and makes it green.
- When the reviewer raises a concern and you disagree, say so once, with
  the measurement. If they repeat it, that is the decision — implement it.

The reviewer's job is to find checks that certify more than they prove.
Assume they will, because they did, repeatedly, in every phase.

---

## 4. Evidence artifacts

Some measurements are expensive: a four-browser run, a fresh clone, a
reasoner pass. Those are run deliberately and their results **committed as
records**, then policed by cheap tests on every run.

Rules that took several attempts to get right:

**A record describes a commit it does not live in.** It cannot describe
itself. Say so in the record, and have the test require ancestry rather
than equality.

**Normalise provenance out of any digest meant to detect content change.**
A digest that includes the commit hash, a build stamp, or a generator path
measures the repository's history rather than its content. Classify every
top-level field as content or provenance, and fail when a new field
appears unclassified.

**Scope a freshness digest to what was actually examined.** A browser
review digest that covered the whole artifact went stale on every commit,
because the download bundle's timestamp comes from the commit. Name the
files the check loads. A missing one is fatal, not skipped — a digest over
five of six files is a perfectly stable number describing less than it
claims.

**Two moments, two questions.** At capture time, require the deployment to
be the checkout being measured. After the record is committed the branch
moves on, so repository tests can only ask about the frozen fact. Never
store a value that describes live state; recompute it.

**Bind any digest a record cites.** A bare `sha256` is unfalsifiable — any
64 hex characters satisfy a length check. Record the commit too, and have
the test recompute the digest from that blob.

---

## 5. Say what was not done

The single most valuable habit. Every record carries an explicit
**not covered** section, and tests enforce that it stays honest.

- Playwright's WebKit is **not Safari**. A test forbids the word "Safari"
  anywhere in the browser record except the not-covered note.
- Reading the accessibility tree is **availability for announcement**, not
  an announcement. No screen reader ran, so no announcement was observed —
  and a test scans the record requiring every use of the word to sit inside
  a statement saying so.
- A viewport of 320×256 is a **reflow-equivalent**, not an observed 400%
  zoom run, and reflow is WCAG 1.4.10 rather than 1.4.4.

A gate that reports `passed` over an unperformed manual check is the same
overclaim in a different costume. Split the verdict: what the tool can
determine, and the gate, which includes what only a person can state.

**Evidence a tool cannot produce needs an intake path.** If a manual
check's status lives in source, closing it means editing Python — a strange
way to record that somebody listened to a screen reader, and it makes
"performed" a one-word change with nothing attached. Put it in a data file
with a schema that refuses `performed` without the tester, date, platform,
versions, and what was observed.

---

## 6. Derive, never transcribe

Any number in prose is wrong eventually.

ValueNet published a digest — `27931563…` — that nothing in the tree could
reproduce, because the measure had never been implemented. It existed only
as a figure in a plan document. The fix was not a corrected number; it was
an executable normalisation with a pinned result and a falsification.

- Membership lists are derived from two independent sources and the build
  **refuses when they disagree**, rather than preferring one.
- Inventories in documents are regenerated and bound by a test, so a record
  that stops matching the corpus fails rather than quietly ageing.
- A control that lives only in a test is a control the build does not have.
  Put the refusal in the builder *and* the test.

---

## 7. Determinism

If a build is not reproducible, no checksum it publishes means anything.

- Sorted inputs, never filesystem order.
- Timestamps from the commit or `SOURCE_DATE_EPOCH`, never `now()`.
- Bytes copied, never re-serialised. A round trip through a parser produces
  a file that says the same thing and hashes differently.
- Archive metadata pinned: member order, one timestamp, fixed permissions,
  fixed creating system. Zip stores seconds in two-second steps — truncate
  explicitly rather than letting it round.
- Verify across **paths**, not just twice in the same directory. Build in a
  clone at a different depth and compare.

---

## 8. Pin exactly, and pin once

- Python dependencies pinned to exact versions in a requirements file that
  is verified by installing into an empty environment and running the suite
  there. ValueNet's was wrong twice.
- Node pinned in `.nvmrc`, read by both `nvm` and `actions/setup-node`, so
  there is one version rather than two that can drift. A test reads the
  pin and **fails** when the running version differs — a skip is
  indistinguishable from a pass in every summary line.
- GitHub Actions pinned to commit SHAs. A tag can be moved.
- Any external authority pinned to a **commit**, never a branch. A
  remote-tracking ref moves when somebody else pushes, which would let a
  licensing result change with no commit in this repository.

---

## 9. Tests, specifically

- **Test the shipped artifact.** Ranking that ships as JavaScript is tested
  by running that file under Node, not by reimplementing it in Python — a
  reimplementation proves the reimplementation works.
- **Refusals are the interesting tests.** Assert what the build declines to
  do: two labels, a missing definition, an unresolved parent, a mapping on
  an undeclared subject.
- **Guard the guards.** A page list that fetched nothing satisfies every
  naive assertion. Assert that the thing being checked was non-empty.
- **No test may depend on build output.** Reading a gitignored artifact
  makes a test pass, fail, or skip depending on whether somebody built
  first. Generate it in a fixture.
- **A skip is a pass in disguise.** Where a dependency is genuinely
  required, fail; where an environment legitimately cannot run a check,
  move the check to where the environment exists rather than skipping.
- **Never commit behind a green checker.** One commit here rode through on
  `check_site && git commit` while the test suite was red.

---

## 10. Licensing, from the first commit

Decide what may be published before publishing anything.

- Every tracked file gets **exactly one disposition**, derived from
  recorded provenance plus explicit owner adjudications — never a list of
  filenames.
- Both directions are policed: a file matching no rule is a refusal, and an
  adjudication matching no file is an exception granted for nothing.
- Reference material you do not own is **cited, never redistributed**. A
  README saying "this repository does not redistribute them" is not a
  licence; the repository's contents are.
- Licence texts are the pinned instrument, not an SPDX template. ValueNet
  shipped a BSD-3-Clause *template* with `Copyright (c) <year> <owner>`
  placeholders, and the test asserted only a phrase every BSD variant
  contains.

---

## 11. Writing it down

Commit messages carry the reasoning, not the diff. What was wrong, why the
fix is the fix, what was falsified and how. When a defect had a second
defect underneath it, say so — that is the part a reader cannot recover.

Decisions that are *not* being made get recorded too, with their evidence
and what would close them, and a test asserting the status stays open.
Two such records exist in ValueNet: label capitalisation and ontology IRI
form. Neither authorises an edit; both stop the question being rediscovered.

---

## 12. What this costs

This method is slow. In ValueNet it caught, among others: a corrupted
corpus measurement that blamed the corpus, a licence template shipped as a
licence, 45 tests silently dropped by a missing optional dependency, a
bypass control unreachable by keyboard in one browser engine, an ontology
term drawn in a diagram that did not exist, and a checksum file that
verified three files nobody could download.

None of those were found by writing more code. All were found by asking
what a passing result actually demonstrated.
