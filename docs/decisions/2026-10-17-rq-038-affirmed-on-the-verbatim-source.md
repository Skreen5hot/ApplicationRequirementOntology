# rq-038 (adj:ledger-hash-kind) — decision A affirmed on the verbatim source text

- **Date:** 2026-10-17
- **Actor:** Aaron (the architect)
- **Concerns:** queue row `rq-038`, record `adj:ledger-hash-kind`, decided **A** at `2026-10-17T03:25:58-04:00`,
  bound to `sha256:86cb35d5730a94fb0ca2ffc0c0b7003a4cd661f1e84932995e36d93b2e68b9ff` (unchanged by this record)

## Why this record exists

IA Ops finding 2026-10-17 (HIGH), *"the source passages a decided adjudication shows are a paraphrase, and the copy
rule is opt-in"*: when rq-038 was decided, its `theSourceSays` passages were the dev agent's paraphrase, not the cited
fragments' bytes — one carried the gloss "-- kind is not in the preimage", the other elided `{"code": "H-LEDGER-01"}`
to `...`. Bullet 5 asked that the architect either re-decide on a corrected display or affirm the decision on the
verbatim text. Since ARO `0ee6d51`, `act.py show rq-038` prints `NOT VERBATIM` over each passage with the cited
fragment's own bytes beneath.

## The statement, verbatim

The question put to the architect: whether decision A stands on the verbatim text, or rq-038 is re-presented. After
asking "Are you recommending leaving out \"kind\"? why the reason to include was sound?" and being answered (A puts
`kind` INTO the hash; the pre-amendment line `sha256(seq ‖ prev ‖ payload)` left it out, so a kind-only rewrite kept
every hash and broke W-CS7-Δ1's guarantee), the architect stated:

> stands

## Effect

- rq-038 = **A** stands; it is **not** re-presented. No record, digest or act moves.
- `adj:ledger-hash-kind` remains the one named exception in `tests/test_ws3_source_passages.py`; the exception now
  cites this record. Its passages stay as acted, and `show` keeps printing the verbatim fragments beneath them.
