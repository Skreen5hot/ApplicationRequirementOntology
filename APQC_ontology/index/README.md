# Corpus index — navigate the graph by `grep`, not by reading slices

`corpus_index.tsv` is a generated, greppable index of every `ex:`/`perf:` class and
individual across the 13 slices + `apqc-ext` + `apqc-catalog` + the capability/role
layer. **Prefer grepping this file over `Read`-ing a whole slice** — a `grep` returns
only the matching rows, so navigation costs a fraction of the tokens.

Columns (tab-separated):

| col | meaning |
|---|---|
| `iri` | prefixed IRI (`ex:P19945`, `ex:CustomerRole`, `ex:PCF_19238`) |
| `kind` | `process · capability · role · ice · agent · act-genus · catalog · individual · property · marker · other` |
| `section` | slice `1`–`13`, or `ext · catalog · cap · delivery · wiring` |
| `hierarchy` | APQC hierarchy ID (`1.1.1.1`) |
| `pcf` | APQC element ID |
| `label` | `rdfs:label` |
| `parents` | named `rdfs:subClassOf` anchors, `;`-joined |
| `wiring` | process → `req-cap:…;req-role:…`; capability → `enables:…` (Phase-1 bridge) |
| `definition` | `skos:definition` (truncated to 160 chars) |

## Recipes

```bash
grep -i "asset maintenance" APQC_ontology/index/corpus_index.tsv # find by label
awk -F'\t' '$2=="capability" && $3=="9"' …                       # all capabilities in slice 9
grep -P "^ex:P19945\t" …                                          # one process: anchor + wiring + def
awk -F'\t' '$8 ~ /req-cap:ex:CompetitiveAnalysisCapability/' …    # processes requiring a capability
```

## Regenerate — you cannot, yet

This section used to read `python scripts/build_index.py`. **There is no `scripts/`
directory in this repository, and no tool here writes this file.** The paths in the
recipes above were wrong for the same reason: they said `ontology/index/`, which is
where the file lived in an earlier tree.

That matters more here than for the other orphaned artifacts, because this README
tells you to grep this file *in preference to reading a slice*. A stale row is
therefore read as fact. As of the last check it holds 5,051 rows over a corpus of
3,119 authored classes, and nothing can tell you whether that is right.

`config/repository-layout.yaml` records the component as `orphaned` with that reason,
and `tests/test_repository_layout.py` fails if the list of such components changes
without somebody deciding it should. Until a generator lands:

- **Verify anything you take from here** against the slice it names before relying on it.
- Prefer `python tools/layout.py` and the modules themselves for anything load-bearing.
- Writing the generator is a small, well-defined first task, and it discharges a debt
  the contract already records. See `docs/HANDOFF.md`.
