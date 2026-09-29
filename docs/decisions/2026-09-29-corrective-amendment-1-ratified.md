# Decision record — Corrective Amendment 1 (Candidate 3) RATIFIED, 2026-09-29

Recorded by the ARO dev agent (IntegratedAgent Dev, ia-dev) on 2026-09-29. The act is the architect's; it was stated to IA OPS and recorded verbatim by Ops in IntegratedAgent `experiments/comms/OPS-2026-09-29-operator-act-ca1-ratified-and-s52-dispatch.md` (commit `911f7e5`), where Ops re-derived every digest in it from committed bytes before recording. This entry places the act in the repository the amended instrument lives in, as Corrective Amendment 1 §8 step 4 requires ("The completed gate record must be committed before the first Stage A task begins").

---

> I ratify Corrective Amendment 1 identified by SHA-256 cad90ec2257d24bb6712ccbf7ff28ebf11bdbb5e3198678862ea4fd4e983759f, amending only the stated subjects of Provenance Foundation Phase Plan v1.1 at commit 6cbad3588a8c683d09e95c465104056d6dde3ba2, Plan SHA-256 C43954A6825E6BE042CEB8293BC2F7F0C94F88E12C42E48E6DF06B9BF88D7AF8. I have received the IA DEV review ea4ea981777aeaee4332a814f702ea953a7826d1ac2ff1d3592e1bd3f0cb1a8e and IA OPS verification 188291b8cc6e79ef46fc611cb06ba46b4247a688dee9f3e9e8c737a3765ce26b. This act makes the amendment operative and permits Stage A to begin under it. It does not execute the later A3 re-pin or any measurement run; it authorizes the single channel-measurement dispatch of section 5.2. — Aaron Anthony Damiano, 2026-09-29

---

## The gate, closed

| step | record | digest |
|---|---|---|
| 1 — freeze | `docs/decisions/2026-09-29-provenance-foundation-corrective-amendment-1-c3.md` (commit `9d9d8a0`) | `cad90ec2257d24bb6712ccbf7ff28ebf11bdbb5e3198678862ea4fd4e983759f` |
| 2 — IA DEV review | IntegratedAgent `experiments/comms/DEV-2026-09-29-corrective-amendment-1-c3-ia-dev-review.md` | `ea4ea981777aeaee4332a814f702ea953a7826d1ac2ff1d3592e1bd3f0cb1a8e` |
| 3 — IA OPS verification | IntegratedAgent `experiments/comms/OPS-2026-09-29-ia-plan-ca1-c3-step3-reverification.md` (commit `50e07fe`): seven checks met, zero findings | `188291b8cc6e79ef46fc611cb06ba46b4247a688dee9f3e9e8c737a3765ce26b` |
| 4 — the act | above; Ops' record `911f7e5` | — |

Candidates 1 (`67c998d4…9eb81`, `256150c`) and 2 (`ae3eb5e2…6da4`, `fc199fd`) remain as history and confer nothing. **The amendment is operative; Stage A may begin under it.** Plan v1.1's §16 is withdrawn as authoritative evidence (amendment §2); §11.3 is supplemented, not replaced (§5); the Freeze 1 checklist gains the transport proof's four factory pass criteria (§5.7); GP-E is split 18.0 h substantive + 2.0 h closeout reserve (§7).

## The single §5.2 channel-measurement dispatch — performed by IA OPS under the act's authorization

Ops' record, verbatim in substance:

## The single §5.2 channel-measurement dispatch (authorized by the act; a measurement of the channel, not a run)

- **Provider's published identifier for the dispatched model:** `claude-sonnet-5` (the model reference lists it as the complete
  ID; date suffixes are not to be constructed). There is no published fully-dated form to request.
- **Dispatch:** Claude Code CLI 2.1.270, `claude -p "reply with the single word OK" --model claude-sonnet-5 --output-format json`,
  2026-09-29T17:18:07Z, rc 0, result `OK`.
- **Envelope:** `ops-verify/ca1/dispatch-claude-sonnet-5.json` (Ops-side), SHA-256
  `7b21d07bf3238ecf4c3e68bafaf644928b95e101ef456fd332dc81edfc5eee1a`.
- **Echo:** no top-level model field; `modelUsage` = { `claude-sonnet-5` (canonicalModel `claude-sonnet-5`, provider firstParty,
  4 output tokens — the dispatched model), `claude-haiku-4-5-20251001` (canonicalModel `claude-haiku-4-5` — the CLI's helper
  model, not the dispatched one) }. The request named the exact published identifier and the channel echoed it **undated**.
- **Reading under §5.2:** means **(a)** (fully dated echo of a fully dated request) is **not available** through this channel,
  because the provider's published identifier for Sonnet 5 carries no date. Freeze 3 therefore closes only by means **(b)** —
  provider documentation cited in the freeze package by URL, retrieval date and SHA-256, stating that `claude-sonnet-5` denotes
  an immutable snapshot — or through another channel. Whether such documentation exists is a Freeze 3 preparation item
  (O-5), not decided here; Ops has not asserted it either way.

**Reading recorded here:** means (a) of §5.2 — a fully dated identifier requested and echoed — is not available through the factory's dispatch channel, because the provider's published identifier for the dispatched model carries no date. Freeze 3 therefore closes only by means (b) — provider documentation, cited by URL, retrieval date and SHA-256, that the identifier denotes an immutable snapshot — or through another channel. That is a Stage C Freeze 3 preparation item (IA OPS with ARO DEV), not a Stage A blocker.

## Stage A, as it stands on the day of the act

A1 done (2026-09-14). **A2b done** by IA OPS (`fd57dd0`, IntegratedAgent `experiments/comms/OPS-2026-09-29-a2b-compatibility-record.md`): the three consumption surfaces replayed deterministically, pre `f827459` vs post `911f7e5`, six differences, every one traced to a recorded ruling (F3 `09277bb`/`f7dad5a`, F6(b) `d215c65`), no baseline-blocking finding; Dev's triage confirms it (IntegratedAgent `experiments/comms/DEV-2026-09-29-a2b-triage.md`). **A2 (Dev's attestation and the F-04 answer) is the next item on the critical path**; A3 needs A2 and A2b together. The five-week bound: week 3 of 5.

---

Applied by the ARO dev agent in the commit that carries this entry: this file only. Pushed to `armb-source-path-parameter` and fast-forwarded into `main` as the A4 authorization established for this branch's content. No graph, ontology, projection, rule or fixture changed.
