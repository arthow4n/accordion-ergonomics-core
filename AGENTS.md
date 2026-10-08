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

For repeated contact/frame debugging, use the repository skill at
`.agents/skills/aec-contact-diagnostics/SKILL.md`. Its deterministic operations
live in the CLI and tests; the skill explains the demonstrated failure modes.

For long experiments while source edits continue, run `aec frozen WORKFLOW`
with uv. It archives the executed source; direct long runs can record hashes
of files different from cached modules. Treat changing search outcomes as
numerical/model evidence, not global human reachability. Refine borderline
withdrawal edges before attributing failures to instrument spacing.
Use `uv run aec verify DIRECTORY --require-complete` to check frozen record
integrity before publishing; it checks hashes and links, not scientific validity.
Older records without frozen metadata may legitimately report partial checking.

Before interpreting accepted poses as collision-valid anatomy, read experiment
014 and run `uv run aec collision-coverage` on recorded pose inputs. Imported
anatomical masks suppress automatic self-collision; four explicit thorax/arm
pairs do not cover fingers. Independent proxy distances and observed/calibrated
envelopes are necessary. Do not repair this by blindly enabling all pairs or
shrinking envelopes until IK succeeds. State contacts require explicit fingers.

For new solves, use explicit `collision_limit_implementation="displacement"`
settings as in experiment 018. Mink 1.3.0 has verified bound-unit and world-pair
filter defects (016); legacy input preserves native behavior for reproduction.
The project adapter needs independent sampled integration-edge checks because
large steps can cross an activation band (017). Named additional self-pairs
are hypotheses on unchanged proxies (019), not full anatomical validation.
