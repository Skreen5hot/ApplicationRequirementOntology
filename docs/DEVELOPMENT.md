# Development

How to work in this repository. For *why* it is built this way, read
`docs/process/PROCESS.md`. For what is actually here and what is not, read
`docs/HANDOFF.md` first.

---

## Setup

Python 3.12. Dependencies are pinned exactly, and the pinning is verified the one way it
can be — by installing into an empty environment and running the suite there:

```bash
python -m venv .venv
.venv/Scripts/activate          # Windows;  source .venv/bin/activate elsewhere
python -m pip install -r requirements-dev.txt
python -m pytest tests/ -q -p no:randomly
```

`tools/` is deliberately not an installed package. It is a directory of scripts that the
tests import by path, so there is no build step between writing a tool and testing the
tool that ships.

Expect roughly four minutes for the suite. Almost all of it is four SHACL passes over
62,000 triples;
the validation record is computed once in a module-scoped fixture because three tests
asking for it separately once outran a ten-minute timeout.

---

## The checks, and what each one actually asserts

Run in this order; each is cheap until the last.

```bash
python tools/layout.py                        # the contract describes the tree
python tools/licensing/disposition.py         # one disposition per tracked file
python tools/licensing/disposition.py --check # nothing unpublishable is tracked
python tools/ontology/vendor_upstream.py      # the extracts cover what the shapes walk
python tools/ontology/corpus_digest.py        # measure the authored ontology
python tools/ontology/validate.py             # the SHACL ladder
python -m pytest tests/ -q -p no:randomly     # all of the above, plus the falsifications
```

| Command | What it will refuse |
|---|---|
| `layout.py` | a declared component whose path does not exist; two components sharing an id; a generated artifact that names no generator and does not admit it has none |
| `disposition.py` | a file matching two rules, or none; an adjudication naming no file; a `LICENSE` naming zero or two recognised licences |
| `disposition.py --check` | a tracked file that may not be redistributed; a vendored extract whose required attribution is missing from `vendor/NOTICE.md` |
| `vendor_upstream.py` | an upstream term this repository names that no extract describes; an extract whose digest is not what the manifest records |
| `validate.py` | exits 1 on any violation, and on a shape set the negative fixture does not exercise |

`validate.py` writes a report with `-o config/validation-report.json`. That file is
gitignored on purpose: it is a measurement, not a pin, and a committed copy would agree
with the ontology only until the next edit. `config/corpus-digest.json` **is** committed,
because a test compares it against a fresh measure — an artifact nothing compares is a
claim, not a measurement.

---

## Adding a file

Every tracked file must be declared in `config/repository-layout.yaml`. An undeclared file
fails the suite in both directions: it has no stated role, and a declared component whose
path is missing is a contract describing something that is not there.

```yaml
  - id: ontology.aro.core          # stable; queries and tests reference the id, not the path
    path: ontology/aro/aro-core.ttl
    role: ontology-module
    description: >-
      What it is, and anything a reader would otherwise have to reconstruct.
```

Roles are not labels — each carries a licensing consequence, and the set of known roles is
read from the licensing tool so the two cannot drift:

| Role | Means |
|---|---|
| `ontology-module`, `ontology-module-set` | authored ontology; in the reasoner scope and the corpus digest |
| `ontology-validation` | SHACL shapes; **not** in the reasoner scope |
| `test-fixture` | expected to be invalid on purpose; must never be loaded as ontology |
| `generated-artifact` | derived; must name a `generator`, or declare itself `orphaned` with the reason |
| `vendored-ontology` | somebody else's, redistributed under their licence, attribution required |
| `third-party-reference` | somebody else's, **not** redistributable |
| `documentation`, `configuration`, `tool`, `project-licence` | as they sound |

Two fields worth knowing:

- **`tracked: false`** — the files may exist locally and must never be committed. Stronger
  than `.gitignore`, because an already-tracked file stays tracked. This is what stands
  between `docs/Reference/` and a second ISO exposure.
- **`generator:` / `orphaned:`** — exactly one is required of a `generated-artifact`. See
  `docs/HANDOFF.md` §5.1 for why this field exists.

Adding a new *role* means adding a licensing rule for it in
`tools/licensing/disposition.py`. The test will tell you; do it deliberately rather than
letting a file inherit a guess.

---

## Adding a shape set

**In the same commit, or not at all:** a new shape set arrives with negative fixture cases
that break it, and each case names the constraint it targets.

`capabilities_roles_shapes.ttl` shipped without one. While CCO was missing it reported 202
violations that were purely an artifact of the scope; the moment CCO was vendored it
reported zero — and nothing distinguished that zero from a constraint selecting nothing.
It now has nine named negative cases in `APQC_ontology/apqc_bad_examples.ttl` and three
positive controls, because a fixture where everything fails cannot show that a constraint
discriminates.

The fixture is validated **alone**, so each case states the `subClassOf` edges it needs
rather than inheriting them from the corpus.

`tests/test_ontology_checks.py::CAPABILITY_ROLE_CONSTRAINTS` lists the constraint messages
by name. A count would have been satisfied by any nine violations.

---

## Working with the vendored upstream

BFO and CCO are pinned partial extracts, not `owl:imports`. Nothing resolves over the
network at validation time.

```bash
python tools/ontology/vendor_upstream.py            # offline verify — runs in CI
python tools/ontology/vendor_upstream.py --confirm  # fetch and require byte-identity
python tools/ontology/vendor_upstream.py --rebuild  # fetch and rewrite
```

**When you must rebuild:** whenever the corpus or the shapes name an upstream term that is
not yet vendored. The offline check catches it — that is exactly what it is for — and the
message names the terms.

**Adding an upstream:** add an entry to `config/upstream-sources.yaml` with the raw URL
**containing the commit SHA**, the `sha256` of what it serves, and a
`licence_statement_contains` substring that the source's own `dcterms:license` must
contain. The build refuses to vendor under a licence the artifact does not itself state.
Then `--rebuild`, which also rewrites `vendor/NOTICE.md`.

**What the extracts leave out:** every axiom whose object is an anonymous class expression
— 44 of them today. That is recorded in each file's header and in
`config/upstream-extracts.json`, and it means these files cannot support a consistency
claim against BFO or CCO. If ARO work needs those restrictions, widen `STRUCTURAL` in
`tools/ontology/vendor_upstream.py` and revisit the blank-node drop; the serialiser will
need to handle blank nodes deterministically, which it currently refuses to do on purpose.

Downloads cache in `.upstream-cache/` (gitignored). The weekly CI job re-fetches and
requires the committed extracts to be byte-identical.

---

## Conventions

**Falsify every check.** A passing test is not evidence. Evidence is a passing test plus a
demonstration that it can fail: revert the fix, require *that specific* check to fail,
restore, confirm. Two real bugs in this repository were found this way, one of them in the
failure branch of a check that had correctly detected a licence breach and then crashed
instead of reporting it.

**Stage before you mutate.** `git checkout --` restores from the index; unstaged work is
destroyed.

**Commit messages carry the reasoning, not the diff.** What was wrong, why the fix is the
fix, what was measured, and what is still not covered. `git log` in this repository is the
worked example.

**Say what was not done.** Every record states its own limits. A partial extract that does
not say it is partial is the defect this whole method is about.

**Line endings are content.** `.gitattributes` pins LF repository-wide. A CRLF inside a
`skos:definition` is part of that literal's value, and any digest over a file git is free
to re-encode is not a digest.

**Derive, never transcribe.** Paths come from the layout contract. Licences are read from
`LICENSE` and from the upstream artifact. Counts are measured. A number typed into a
document is a claim that stops being true silently.

---

## Traps this repository has already hit

Listed because they cost time here, and none of them announces itself.

- **`| head` and `| tail` mask exit codes.** The pipeline exits with the *last* command's
  status. Twice a failing program looked like a passing one.
- **`text=True` in `subprocess` decodes as cp1252 on Windows**, which corrupts multi-byte
  sequences and then blames the file. Decode explicitly as UTF-8.
- **rdflib renames blank nodes on every parse.** A raw triple-set comparison reports every
  OWL restriction as both added and removed. Compare ground triples plus a blank-node
  *shape* digest with identities erased — `tools/ontology/corpus_digest.py` is the worked
  version, and `sh:sourceShape` in a validation report had the same problem.
- **`all()` over an empty sequence is `True`.** The validation ladder once reported success
  having evaluated no rung at all. `validate.passed_of` is the guard, tested against an
  empty record because that state can no longer be reached from the repository itself.
- **Scanning file text finds the comment explaining the rule.** The namespace check failed
  on a Turtle comment mentioning `example.org`. Parse and check terms.
- **A green shape set is ambiguous on its own.** Clean data and a constraint selecting
  nothing look identical.
