# Decision record — amendment to A9: the WS-3 region, 2026-10-01

Recorded verbatim by the ARO dev agent on 2026-10-01, at the architect's statement in session. The act is the
architect's. It amends one value of the A9 naming act (`docs/decisions/2026-10-01-a9-ws3-target-naming-act.md`),
which is otherwise unchanged and is not edited. Nothing in the quoted block is paraphrased.

---

> amend A9's region to 73–76
>
> — Aaron Anthony Damiano, 2026-10-01

---

## What the act was asked, and what it changes

Asked (IA ledger row `aaron-ws3-region-line-76`; ARO queue item rq-036; IA Ops finding
`findings-2026-10-01-the-region-containment-gate-widens-its-own-region-by-one-line.md`): C-S7's determinism note is
line 76, one past A9's "73–75". The two options were to (1) amend A9's region to 73–76, keeping the clause, or
(2) drop the clause. The architect chose (1).

**Effect, read mechanically:** A9's region "lines 43–53 and 73–75" becomes **"lines 43–53 and 73–76"**. The second
range, which begins at 73, now ends at 76. The first range is untouched. The registered digest
(`2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450`) is unchanged, and the line numbers still refer
to it.

**Consequences in the graph:**
- `a:C-S7:determinism` (line 76) is inside the acted region.
- `diag:C-S7-determinism-beyond-the-acted-region` is closed by this act.
- C-S7's queue item is re-bound without the beyond-region flag.

`spike/graph/ws3/build_l2.py` reads this record alongside A9's, so the region in the graph and in its gate is the
amended one, read from the record and not retyped.
