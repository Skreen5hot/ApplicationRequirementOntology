# Projections — produced on 2026-09-11 (this note is history)

Until 2026-09-11 the projector refused to project the real slice because none of the eleven queued records had been acted on; that refusal, not an absence, was why nothing was under `out/`. The architect acted on all eleven in one sitting, and `python spike/projections/project.py --check` then printed `Projected: byte-identical on re-projection`.

The package is in `out/` (six files, one Projection Input Manifest digest across all of them) and is described, with digests and the two preconditions OPS must confirm before building, in `HANDOFF-TO-OPS.md`. This file stays so the record shows the projection was withheld while the acts were pending, and why.
