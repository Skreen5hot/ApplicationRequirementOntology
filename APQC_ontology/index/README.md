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
grep -i "asset maintenance" ontology/index/corpus_index.tsv      # find by label
awk -F'\t' '$2=="capability" && $3=="9"' …                       # all capabilities in slice 9
grep -P "^ex:P19945\t" …                                          # one process: anchor + wiring + def
awk -F'\t' '$8 ~ /req-cap:ex:CompetitiveAnalysisCapability/' …    # processes requiring a capability
```

## Regenerate

```bash
python scripts/build_index.py      # after ANY change to a slice / ext / catalog / capability layer
```

The index is a derived artifact; it is committed so agents need no build step, but it can
go stale — regenerate it after a corpus change (and before relying on it in a review).
