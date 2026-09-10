# Corpus index — navigate the graph by `grep`, not by reading slices

`corpus_index.tsv` is a generated, greppable index of every term the corpus
**declares** — classes, SKOS concepts, properties and individuals in the `ex:`
namespace. **Prefer grepping this file over `Read`-ing a whole slice** — a `grep`
returns only the matching rows, so navigation costs a fraction of the tokens.

That advice only holds because the file is now derived and checked. It was not:
this README documented `python scripts/build_index.py` against a `scripts/`
directory that did not exist, so the index could not be rebuilt, could not be
compared against the corpus, and had been text-edited during the namespace
migration. Rows were being read as fact that nothing could vouch for.

Columns (tab-separated):

| col | meaning |
|---|---|
| `iri` | prefixed IRI (`ex:P19945`, `ex:CustomerRole`, `ex:PCF_19238`) |
| `kind` | `process · capability · role · ice · agent · act-genus · catalog · individual · property · other` |
| `section` | canonical home: `ext · catalog · cap · delivery`, a slice `1`–`13`, or `shared` |
| `hierarchy` | APQC hierarchy ID (`1.1.1.1`), from `ex:hierarchyID` |
| `pcf` | APQC element ID, from `ex:pcfID` |
| `label` | `rdfs:label` |
| `parents` | named `rdfs:subClassOf` anchors, `;`-joined, sorted |
| `wiring` | `req-cap:…;req-role:…;bears-perm:…` on processes and roles, `enables:…` on capabilities |
| `definition` | `skos:definition`, cut to 160 characters |

## What `kind` actually means

It is decided by walking `rdfs:subClassOf` to a BFO or CCO anchor — **not** by
the spelling of the IRI. `ex:FinancialInstrument` is not an `ice` however much
the name suggests a document; it is a CCO Material Artifact.

This is only possible because BFO and CCO are vendored under
[`vendor/`](../../vendor/). Without them the walk stops at the first upstream
parent and every class is equally unclassifiable, so the generator **refuses to
run** rather than emitting an index where everything is `other` and nothing
looks wrong.

Anchors, in precedence order — the order is the rule, since a permission is an
information content entity and a capability is not a process:

| kind | anchor |
|---|---|
| `capability` | `cco:ont00001379` Agent Capability |
| `role` | `obo:BFO_0000023` role |
| `ice` | `cco:ont00000958` Information Content Entity |
| `agent` | `cco:ont00001017` Agent, `cco:ont00001180` Organization |
| `process` | `cco:ont00000005` Act, `obo:BFO_0000015` process |

`catalog`, `property` and `individual` come from the declaration itself;
`act-genus` means the term is declared in `apqc-ext.ttl`; `other` means the term
reaches no anchor above.

## What `section` means

The term's **canonical home**, not "a file it appears in". The slices inline the
genera they use rather than importing them, so a shared genus is declared in
`apqc-ext.ttl` *and* in up to fourteen slices. The shared module wins.

`shared` means the term is declared in several slices and in no shared module.

An earlier version of this column resolved multi-file terms by taking the first
filename in string order, which filed every shared genus under section `10` —
because `apqc_10_0.ttl` sorts ahead of `apqc_1_0.ttl`. That was a fact about
sorting, not about the ontology.

## Two things the index will not tell you

**The inlined copies have drifted.** 51 terms carry more than one distinct
`skos:definition` and 6 carry more than one distinct `rdfs:label` — the same IRI
means different things depending on which file you read. `ex:ActOfForecasting`
is defined one way in `apqc-ext.ttl` and five slices, and another way in
`apqc_10_0.ttl`. The index shows the canonical home's value, prints the conflict
count on every run, and `tests/test_corpus_index.py` pins both numbers so they
can only go down deliberately. **If a definition matters to your work, read it
from the module rather than from here.**

**`marker` is not produced.** An earlier version of this table listed it as a
possible `kind`. Nothing derives it, so it has been removed rather than left as
a value somebody filters on and always gets nothing from.

## Recipes

```bash
grep -i "asset maintenance" APQC_ontology/index/corpus_index.tsv # find by label
awk -F'\t' '$2=="capability" && $3=="9"' …                       # capabilities homed in slice 9
grep -P "^ex:P19945\t" …                                          # one process: anchor + wiring + def
awk -F'\t' '$8 ~ /req-cap:ex:CompetitiveAnalysisCapability/' …    # processes requiring a capability
awk -F'\t' '$2=="act-genus"' …                                    # the shared genera
awk -F'\t' '$3=="shared"' …                                       # declared in several slices, no owner
```

## Regenerate

```bash
python tools/ontology/build_index.py            # rewrite the index
python tools/ontology/build_index.py --check    # compare against a fresh build, write nothing
```

Regenerate after **any** change to a slice, `apqc-ext`, `apqc-catalog`, the
capability/role layer, or the vendored extracts. `--check` runs in CI, so a
stale index fails the build rather than sitting in the tree looking current.
