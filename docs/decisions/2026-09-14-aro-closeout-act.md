# Decision record — ARO closeout act, 2026-09-14

Recorded verbatim by the ARO dev agent at the architect's instruction, in session, on 2026-09-14. The acts are the
architect's. ARO v0.5.2 §16 makes the Phase-1.5 outcome mapping binding once stated and names Phase 1 as the
architect's ratification act ("this document does not pronounce it"); §18 and the closing line of the document
say the ratification instrument, once issued, is recorded in the specification's own record and in the repo
decision record. This is that record for the closeout act. Nothing in the quoted block is paraphrased; the
agent's own framing is confined to the sections that follow it, each of which records one reading rather than
assuming it.

---

> ARO closeout act. The 2026-09-13 canonical closeout is accepted; the outcome mapping's first branch is recorded as applied: Arm A shipped and standing; no seam license claimed for ARO. Phase-1 ratification of ARO v0.5.2 is granted, scoped: the graph, ratification-queue, and projection machinery (§§2–13) stand as the specification for ARO's role as the ratified-provenance source for the factory's provenance boundaries — the program's next measured step. Transformation at scale and beyond (Phases 6–8) are deferred, not denied, behind the three §9 preconditions; any re-measurement is a new authorization, and the standing instruction holds: the spike is closed, no new arm. The calendar budget (precondition 1) is recorded as deferred until full-program re-authorization is contemplated. Adjudication C is recorded as a dated line per the same idiom as GP-D. — Architect, 2026-09-14

---

## Closeout accepted (recorded act, 2026-09-14)

**The canonical closeout is `spike/report.md` Part I as committed at `80c1c9c`** (branch
`armb-source-path-parameter`), with the 2026-09-11 Arm B report kept byte-identical below it as Part II.
Accepted as the record of the Phase-1.5 spike. The spike is CLOSED. Ops (coord-j) measured the closeout's
twelve checkable claims true from their own account before this act (IntegratedAgent
`experiments/comms/OPS-2026-09-13-aro-spike-closeout-verified.md`); that verdict did not and does not take the
decision below — the architect does, here.

## Outcome mapping, first branch — recorded as applied (recorded act, 2026-09-14)

The mapping (ARO v0.5.2 §16, binding once stated): *Class live — A alone kills → ship A into the loop
immediately, regardless of ARO; ARO's license rests on the faithfulness/N1/provenance incident class.*

Measured (Ops, N = 5 per arm, one protocol): class live — Arm 0 `e0ca050` drift 3/5; A alone kills — Arm A
`f827459` 0/5, and the control that removed only Arm A's declared-seams block (`886ef2e`) 4/5. **Applied:** Arm
A's mechanism — declared member names reaching every consumer, in the names-only, non-normative form the
2026-09-13 F3 ruling requires — is shipped in the IntegratedAgent loop (branch `graph-materialization-build`)
and **standing**. **No seam license is claimed for ARO**: Arm B also killed the flip (0/5 in every projected
configuration), and on the seam axis that adds nothing A had not already earned.

## Phase-1 ratification of ARO v0.5.2 — granted, SCOPED (recorded act, 2026-09-14)

**Granted, with this scope and no other:** *the graph, ratification-queue, and projection machinery (§§2–13)
stand as the specification for ARO's role as the ratified-provenance source for the factory's provenance
boundaries — the program's next measured step.*

One reading recorded rather than assumed. The factory's provenance boundaries are the ones the closeout's
section 5 names and IntegratedAgent has since built and Ops has verified: `record` on a declaration (F3),
`provisional: False` on a bar (F7), `barProvenance` on the authority ledger (F7c), each failing closed without
a ratified source. ARO's ratification queue is the process this program has for producing that source at
scale; the ratification granted here is of the machinery that produces it, as specified in §§2–13. The
specification's own §16 Phase-1 line names a broader surface (the D-set, term map, D21 pin, ADR gates and the
outcome mapping); the architect's scope is the one quoted above, and this record extends it to nothing.
Spike finding F-09 ("Phase-1 ratification of ARO v0.5.2 not recorded in the repository") is resolved to this
scope by this entry. Per the specification's closing line, a dated pointer to this entry is placed in the
specification's own record section in the commit that carries this file.

## Phases 6–8 — deferred, not denied (recorded act, 2026-09-14)

*Transformation at scale and beyond (Phases 6–8) are deferred, not denied, behind the three §9 preconditions;
any re-measurement is a new authorization, and the standing instruction holds: the spike is closed, no new
arm.* The three preconditions are those of `spike/report.md` Part I section 9: (1) a stated calendar budget
for the Phase-4 entry condition; (2) one decision on the package-to-loop boundary (F2, F1, F6 remedy (a)),
then one re-projection; (3) a plan with capabilities on a real target before any capability-level claim about
ratified provenance. None is taken here.

## Calendar budget (precondition 1) — deferred (recorded act, 2026-09-14)

*The calendar budget (precondition 1) is recorded as deferred until full-program re-authorization is
contemplated.* The Phase-4 entry condition (required acts divided by achieved rate against the calendar
budget, §16) therefore remains unevaluable by design until that time; the measured rates stand as recorded
(`spike/measurements/rate.py`: 11 acts / 28 assertions; 6.667 working and 0.754 calendar acts per hour; two
starvation incidents). Changed only by another dated line.

## Adjudication C — author-agent repo home (act of 2026-09-11; recorded here 2026-09-14)

**Decision: C — "Relocating closure for the spike, conflict left open."** Decided by the architect with the
rq-011 act (`spike/measurements/ratification-queue.jsonl`: record `adj:author-agent-repo-home`, record digest
`sha256:e7ae4b9b…ba95d`, options A "Honor the source" / B "Source-amendment request" / C as chosen; queued
2026-09-10T18:43:12-04:00; acted 2026-09-11T06:39:00-04:00, sitting start 05:00 per the architect; actor
Aaron; `decision: "C"`). Effective 2026-09-11. Consequence, as projected (`spike/projections/HANDOFF-TO-OPS.md`):
`author-agent` is placed at `src/author-agent.ts` for this spike only, its `files` marked PROVISIONAL in the
Projection Input Manifest, and the conflict with SRS §5 (`.claude/agents/author`) is left open. Recorded in
the same idiom as GP-D, as Part II section 14 item 2 requested and the closeout act instructs: the queue row is
the act; this is where the operational decision is read. Changed only by another dated line.

---

Applied by the ARO dev agent in the commit that carries this entry: this file; an Addendum B and a one-line
status change in `spike/report.md` Part I (Part II untouched, still byte-identical to the 2026-09-11 report);
and one dated pointer line in the specification's record section, per the specification's own instruction.
No graph, ontology, projection, rule, fixture or runtime was changed; the layout gate, the projector's
byte-identical check and the spike's test files are the proof, run in that commit.
