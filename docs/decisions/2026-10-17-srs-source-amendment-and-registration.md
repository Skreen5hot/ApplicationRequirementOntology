# Decision record — the SRS source amendment (W-CS7-N) and its registration, 2026-10-17

Recorded verbatim by the ARO dev agent on 2026-10-17, at the architect's statement in session. The act is the
architect's, both as author of record of the SRS and as registrar. It carries out the adjudication the architect
decided at queue item **rq-038** (`adj:ledger-hash-kind`, option **A**: *amend the source so that kind enters the
hash preimage*), and the rebuild instruction at **rq-042**. Nothing in the quoted block is paraphrased.

---

> edit line 74 for me, register it, scope (b)
>
> — Aaron Anthony Damiano, 2026-10-17

---

## What was asked, and what was done

**Asked:**
1. Should the dev agent make the one-line edit, or should the author make it?
2. Should the amended source be registered?
3. Should the Stage A slice migrate as well: (a) migrate everything, or (b) leave the slice on the old digest as
   a closed, historical record and move only WS-3?

**Done, mechanically:**

| step | what | identity |
|---|---|---|
| pinned | the pre-amendment source, copied byte for byte to `C:/Users/aaron/OneDrive/Documents/SPEC-2428b115.md` | sha256 `2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450`, 42702 B |
| amended | `C:/Users/aaron/OneDrive/Documents/SPEC.md`, line 74 (W-CS7-N) **only**: `sha256(seq ‖ prev ‖ payload)` → `sha256(seq ‖ prev ‖ kind ‖ payload)`. A diff against the pinned copy shows exactly one changed line; the file grew 9 bytes; no line shifted | sha256 `109e1b5026845a573dad17a9fd2ad2e603a2d46175ba2b6d77f17cb18115c614`, 42711 B |
| registered | `spike/graph/source-register.json` gains `src:srs-spec@2` (the new digest; `amends` the old). The old entry `src:srs-spec` now points at the pinned copy and records `supersededBy` (for WS-3) and `stillBinds` (the slice) | — |
| scope (b) | the slice's `spans.json` and `fragments.json` read the pinned copy. Its fragment ids are unchanged (same digest); `fragments.py --verify` matches every fragment; `project.py --check` is byte-identical (plan sha256 `8f9496a4…c55c9`) | — |

## What follows (ARO §5.2; the architect's rq-042 note)

- **WS-3 lapses and requeues.** Its fragments are re-minted under `109e1b50…`, each with a `migratedFrom` link to its
  pre-amendment fragment. Migration is a relationship, never an identity (D23). No pre-amendment fragment identity
  or dependency is carried forward into the rebuilt records.
- **Re-acceptance is a new anchoring act** over the same historical record (ARO §3.2). The rebuilt WS-3 records
  return to the architect as a re-acceptance batch, sized to GP-E.
- **Still to be re-stated by the architect.** The A9 naming act (`2026-10-01-a9-ws3-target-naming-act.md`) and its
  region amendment name the old digest. Its line numbers are unchanged, since no line shifted, so the re-statement is
  a one-line act naming the new digest. It is presented with the re-acceptance batch; this record does not make it.
- **Unchanged:** the Stage A slice, its acts (rq-003 … rq-014), its projection, and the A8 F2-verification result, all
  bound to `2428b115…`.
