"""Spike 2 -- the operator-throughput rate, derived from the two logs beside this file.

SPIKE.md section 4 and ARO v0.5.2 section 16: spike 2 measures a RATE, not a count --
ratification acts required by Arm B, sustained acts per hour actually achieved, and
every interval the dev agent spent blocked waiting on an act. The Phase-4 entry
condition is required-acts / achieved-rate against the calendar budget.

Derived, never transcribed (docs/process/PROCESS.md section 6): every number the
spike report quotes comes out of this script over the logs, so a number in the
report that stops matching the logs fails here rather than ageing quietly.

The measurement-integrity rule, enforced rather than remembered: an act whose actor
is the agent voids the measurement. This script refuses to compute over such a log.

    python spike/measurements/rate.py                  # table
    python spike/measurements/rate.py --json           # machine form
    python spike/measurements/rate.py --as-of <iso>    # close still-open intervals at a stated moment

No `now()`: an open starvation interval is measured only to a moment the caller states,
so two runs over the same logs print the same numbers (PROCESS.md section 7).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "ratification-queue.jsonl"
STARVATION = HERE / "starvation-log.jsonl"

#: Actors whose acts confer nothing and whose presence in the log voids spike 2.
AGENT_ACTORS = {"agent", "dev-agent", "assistant", "claude", "model", "transformer"}


class Refused(SystemExit):
    """Raised instead of printing a number that would measure nothing."""


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise Refused("%s is missing; there is nothing to measure" % path.name)
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise Refused("%s line %d is not JSON: %s" % (path.name, n, e))
    return out


def _t(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value)


def measure(as_of: str | None = None) -> dict:
    everything = _rows(QUEUE)
    starvation = _rows(STARVATION)
    # A superseded entry (its artifact was re-addressed before anyone acted) is history, not a
    # required act: its successor carries the requirement. It stays in the log because the
    # queue is append-only.
    superseded = {q.get("supersedes") for q in everything if q.get("supersedes")}
    queue = [q for q in everything
             if not q.get("supersededBy") and q.get("id") not in superseded]
    if not queue:
        raise Refused("the ratification queue is empty: a rate over zero required acts "
                      "measures nothing")

    acted = [q for q in queue if q.get("actedAt")]
    for q in acted:
        actor = (q.get("actor") or "").strip().lower()
        if not actor:
            raise Refused("%s records an act with no actor; an act nobody performed "
                          "is not an act" % q.get("id"))
        if actor in AGENT_ACTORS:
            raise Refused("%s records an act by %r: the agent performed, batched or "
                          "simulated a ratification act, which voids spike 2 "
                          "(SPIKE.md section 4)" % (q.get("id"), actor))

    first_queued = min(_t(q["queuedAt"]) for q in queue)
    closed_ends = [_t(s["end"]) for s in starvation if s.get("end")]
    if acted:
        last = max(_t(q["actedAt"]) for q in acted)
    elif as_of:
        last = _t(as_of)
    elif closed_ends:
        last = max(closed_ends)             # the last moment the logs themselves record
    else:
        raise Refused("no act has been recorded, no starvation interval is closed, and no "
                      "--as-of moment was given, so the waiting time has no end to be "
                      "measured to")

    hours = (last - first_queued).total_seconds() / 3600.0
    rate = (len(acted) / hours) if hours > 0 and acted else 0.0

    # Two rates, because the calendar rate above counts the night. An act row may carry
    # `sittingStart`: the moment the operator sat down for the sitting that act belongs to.
    # Rows sharing a sittingStart are one sitting, measured from its start to its last act;
    # the WORKING rate is acts divided by the sum of sitting durations. Rows without a
    # sittingStart contribute to the calendar rate only, and the table says how many.
    sittings: dict[str, list[dt.datetime]] = {}
    for q in acted:
        if q.get("sittingStart"):
            sittings.setdefault(q["sittingStart"], []).append(_t(q["actedAt"]))
    working_hours = sum(max(0.0, (max(ends) - _t(start)).total_seconds() / 3600.0)
                        for start, ends in sittings.items())
    acts_in_sittings = sum(len(v) for v in sittings.values())
    working_rate = (acts_in_sittings / working_hours) if working_hours > 0 else None

    if any(_t(q["actedAt"]) < _t(q["queuedAt"]) for q in acted):
        raise Refused("an act is recorded before its record was queued; the timestamps are not "
                      "the acts' own")

    open_intervals, starved_hours = [], 0.0
    for s in starvation:
        start = _t(s["start"])
        if s.get("end"):
            end = _t(s["end"])
        elif as_of:
            end = _t(as_of)
            open_intervals.append(s.get("id"))
        else:
            raise Refused("starvation interval %s is open and no --as-of moment was "
                          "given" % s.get("id"))
        starved_hours += max(0.0, (end - start).total_seconds() / 3600.0)

    required = len(queue)
    # Both numbers, as directed: acts are RECORDS the operator acts on; assertions are what
    # those records bundle. Bundling is the granularity lever, so it is measured, not assumed.
    assertions_queued = sum(int(q.get("assertions") or 0) for q in queue)
    assertions_ratified = sum(int(q.get("assertions") or 0) for q in acted
                              if (q.get("act") or "").lower() in ("ratified", "accepted"))
    return {
        "requiredActs": required,
        "requiredActsNote": "records queued and not superseded; one act per record "
                            "(see spike/report.md for what is and is not yet queued)",
        "assertionsQueued": assertions_queued,
        "assertionsRatified": assertions_ratified,
        "assertionsPerAct": (round(assertions_queued / required, 2) if required else None),
        "actsPerformed": len(acted),
        "firstQueuedAt": first_queued.isoformat(timespec="seconds"),
        "measuredTo": last.isoformat(timespec="seconds"),
        "elapsedHours": round(hours, 3),
        "achievedActsPerHour": round(rate, 3),
        "achievedActsPerHourNote": "calendar rate: acts over the whole interval the queue has been "
                                   "open, nights included",
        "workingActsPerHour": (round(working_rate, 3) if working_rate is not None else None),
        "workingHours": round(working_hours, 3),
        "actsWithSittingStart": acts_in_sittings,
        "actsWithoutSittingStart": len(acted) - acts_in_sittings,
        "hoursToClearRequired": (round(required / rate, 2) if rate > 0 else None),
        "starvationIncidents": len(starvation),
        "starvationHours": round(starved_hours, 3),
        "starvationIntervalsStillOpen": open_intervals,
        "batches": sorted({q.get("batch") for q in queue if q.get("batch")}),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--as-of", default=None, help="ISO-8601 moment to close open intervals at")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    m = measure(args.as_of)
    if args.json:
        print(json.dumps(m, indent=2))
        return 0
    width = max(len(k) for k in m)
    for k, v in m.items():
        print("  %-*s  %s" % (width, k, v))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Refused as r:
        print("REFUSED: %s" % r, file=sys.stderr)
        raise SystemExit(2)
