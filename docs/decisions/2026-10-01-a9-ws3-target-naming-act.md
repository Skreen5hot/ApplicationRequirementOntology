# Decision record — A9: WS-3 capability-target naming act (REC-1), 2026-10-01

Recorded verbatim by the ARO dev agent on 2026-10-01, at the architect's statement in session. The act is the
architect's. It is Plan v1.1 Stage A task A9 (§5, REC-1; §14 Act 2), the last Stage A act before Stage B. Nothing
in the quoted block is paraphrased.

---

> A9 — WS-3 target naming act (REC-1). I name the WS-3 capability target: "SRS adjudication and registration core" — capabilities C-S2 (grade), C-S3 (adjudicate) and C-S7 (register), from the registered SRS src:srs-spec, sha256 2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450.
>
> Region: lines 43–53 and 73–75, with the supporting rules, seams and invariants in §4, §6 and §7 cited in DEV-2026-10-01-a9-ws3-target-candidates.md.
> This act governs WS-3's target. The "WS-3 … on the registered cFE specification" reading in the 2026-09-29 memo-approval record (line 47) is corrected: the cFE remains WS-4's held-out specification and is not a WS-3 target.
> Line numbers refer to the registered copy at that digest, not to any later working copy.
> The demonstration control is designated at freeze 2, as Plan v1.1 §5 requires; Dev proposes C-S2. Freeze 2 also records the two replay fixtures C-S3 needs: a C-S5 report and a third-rater record.
>
> — Aaron Anthony Damiano, 2026-10-01

---

## Where each cited artifact lives

| cited | where | identity |
|---|---|---|
| registered SRS (`src:srs-spec`) | `spike/graph/source-register.json`; source text `SPEC.md` | sha256 `2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450` |
| the candidates document | IntegratedAgent, branch `graph-materialization-build`, `experiments/comms/DEV-2026-10-01-a9-ws3-target-candidates.md` | commit `1a02106`, blob sha256 `94cadafb98ace0120ec206d89c4472376723833ae2b345c832d8239aea2f0fd2` |
| Ops' cross-checks of that document | same branch, `experiments/comms/OPS-2026-10-01-a9-*.md` | `a97ca75`, `2178303`, `5417fbf` (all VERIFIED) |
| the corrected reading | `docs/decisions/2026-09-29-memo-approval-act.md`, line 47 | left unedited; this record governs |

The memo-approval record is not edited: the correction lives here, in a dated act, and the earlier record stays
as it was stated. Ops cross-checks the named target (title and digest) against this record at freeze 2
(Plan v1.1 §11.2). Stage B opens with IA Dev's D-8, the WS-3 graph extension over this region.
