# Research agent workflow

Read README.md and newest RESEARCH_LOG.md entries before work. Run `uv sync
--locked` and `uv run aec check`. Use uv for Python environments, packages,
locking and canonical execution. Keep reusable code under src/.

Preserve source distinctions in docs/research/evidence.md. Real instrument
metric constants require provenance; synthetic fixtures must remain labeled.
Use the canonical frames in docs/research/frames-and-measurements.md and update
frame tests whenever composition changes.

For model/contact changes: run the affected experiment into artifacts/, inspect
all four diagnostic views, check actual collision distances and imported
couplings, and reproduce rendering from the saved state. Do not infer physical
contact from marker position alone. A compiled MjSpec can resolve orientation
differently from its uncompiled quaternion fields. Imported collision surfaces
can overlap, so contact must respect their outer envelope.

Keep useful successes and negative evidence in experiments/ with notes and
rerunnable inputs; keep transient files in artifacts/. Update the root research
log newest-first after meaningful findings. Explain any incomplete validation
or solver failure. Solver iteration history is not a playing trajectory.

Commit and push coherent validated milestones autonomously as authorized by
the project owner. Do not rewrite published history. No external messages or
changes to the evidence repositories are implied by that authorization.
