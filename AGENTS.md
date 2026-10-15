# Research agent workflow

Read README.md and newest RESEARCH_LOG.md entries before work. Run `uv sync
--locked` and `uv run aec check`. Use uv for Python environments, packages,
locking and canonical execution. Keep reusable code under src/. Prefer MyoSim
resources for anatomical structure
whenever they reasonably provide the components needed; distinguish imported
skeletons from approximate soft-tissue/support envelopes.

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

## Persistent visual and biomechanical evidence requirements

For each substantive contact, planning, selection or physiology milestone,
publish a small inspected set of actual-model whole-hand/contact views, all four
diagnostic views, worst-state collision overlays and actual sampled-path GIFs or
ordered frames where complete paths exist. Include matched cameras for controlled
comparisons, numerical traces and diagrams generated from actual search records.
Save model/source/input hashes, qpos/path references, camera settings, active
contact requirements and exact frame sample indices. Render during the milestone,
not only at catalog publication. Never invent intermediate states, use IK
iteration histories as movement, or turn missing/failed paths into successful
animations. Clearly label an unplanned reference-to-first-contact approach.

For biomechanical research, inspect the pinned compiled muscle/tendon system and
validate native/reduced lengths, moment arms and force conventions before using
capacity estimates. Static recruitment estimates are conditional on stated
objectives, bounds, equality constraints and external-force/reaction scenarios;
they are not measured activations, comfort or dynamic/human feasibility. Button
forces/travel remain unmeasured. Preserve all five candidates; technique priors
are optional and distinct from physical constraints. Use controlled ablations
and multidimensional assessments instead of a universal difficulty score. Keep
historical library/frozen evidence intact and attach versioned reassessments.

## Visualization-first scientific research requirements

Plan visual evidence alongside numerical experiments. For movement, posture,
contact or search milestones, completion requires numerical evidence, independent
validation, inspected physical renders, important failures/counterexamples and an
updated `targets/VISUALS.md`. Report exactly which visual evidence was inspected
before declaring completion. If relevant visuals cannot be produced, document the
specific blocker and incomplete validation.

Render actual saved compiled-model configurations and recorded trajectories.
Include complementary context, keyboard, whole-hand, side and worst-proxy views;
show anatomical/contact uncertainty. Movement studies need board-relative wrist,
palm, knuckle and fingertip diagrams. Search/selection studies need process
visualizations generated from actual hypotheses, attempts, budgets and decisions.
Use matched cameras, physical scale, musical events and diagnostic conventions
for baseline/revised claims. Preserve awkward and failed states explicitly.

For connected paths provide scientific keyframes and enough intermediate actual
samples to inspect motion (typically 30–60 selectively chosen frames). Record the
sampling method and exact indices. Equal display intervals are not physiological
time. Never invent states, join disconnected endpoints, animate IK iterations as
movement, or depict failed paths as completed. No decorative or generative
scientific poses, fabricated activations, or unsupported biomechanical claims.

Bind every visual to model/source/input hashes, trajectory/qpos references,
contact requirements, camera settings, parameters and exact sample indices.
Distinguish physical renders, computed traces, algorithm schematics and hypotheses.
Inspect generated images for clipping, wrong cameras, misleading labels and hidden
uncertainty. Link numerical and visual evidence together in the central guide at
each visually relevant milestone; keep its root README link prominent.

Keep coverage proportional: prefer one complete explanatory comparison over many
redundant screenshots. Use `experiments/NNN-topic/evidence/CASE/` with `dense/`,
`state-INDEX/`, `board-path.png`, `events.svg`, `keyframes.gif`, `detailed.gif` and a
hash-bound `result.json` manifest where applicable. Compress or curate media while
retaining complete machine-readable trajectories and historical frozen evidence.
