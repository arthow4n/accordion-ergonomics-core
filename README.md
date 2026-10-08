# accordion-ergonomics-core

A Python research laboratory for articulated accordion ergonomics, starting
with a Roland FR-1XB-style five-row C-Griff right-hand keyboard. The first
prototype composes MyoArm with a finite 3D button fixture, solves one index
fingertip contact, checks imported joint limits/couplings and collision proxies,
and renders four views without a desktop session. A second experiment compares
finger-only and arm-enabled candidates from a recorded physical configuration.
A third audits a supplied path and exposes collisions between valid endpoints.
Explicit profiles now support recalculation; multi-start contact discovery and
seeded withdrawal/path search preserve diverse configurations and trajectories.
A 62-button index atlas and parameter sweeps quantify discovered movement;
small simultaneous contacts and explicit geometric hand hypotheses are supported.
Atlas-derived model challenges and held-contact waypoint search are reproducible.
Displacement collision limits and sampled IK-step backtracking address two
confirmed defects in the locked Mink release. Named self-pair hypotheses can
constrain selected phalanges without altering imported envelopes. A new generic
seated setup derives an FR-1xb-sized shell and board placement from explicit
torso, shoulder and support anchors, with a documented setup family.

**Current results are sampled kinematic predictions on assumed geometry with
incomplete anatomical self-collision coverage. Real playing feasibility,
button operation and continuous validity are not established.**
See [RESEARCH_LOG.md](RESEARCH_LOG.md) for findings and failed investigations.

## Reproduce

Use conventional CPython 3.14 managed by [uv](https://docs.astral.sh/uv/).
The lockfile records the full tested dependency stack.

```sh
uv sync --locked
uv run aec check
uv run aec frozen experiment experiments/023-reference-seated-setup/experiment.json --output artifacts/seated-reference
uv run aec frozen sweep experiments/024-seated-setup-family/experiment.json --output artifacts/seated-family
uv run aec experiment experiments/001-single-contact/experiment.json
uv run aec render artifacts/single-contact/result.json
uv run aec ablation experiments/002-arm-ablation/experiment.json
uv run aec transition experiments/003-transition-counterexample/experiment.json
uv run aec explore experiments/005-pose-diversity/experiment.json
uv run aec plan experiments/006-transition-search/experiment.json
uv run aec frozen atlas experiments/007-index-atlas/experiment.json --output artifacts/atlas
uv run aec frozen sweep experiments/008-geometry-sensitivity/experiment.json --output artifacts/sensitivity
uv run aec frozen exercise experiments/012-large-relocation/experiment.json --output artifacts/exercise
uv run aec frozen held experiments/013-held-index-transition/experiment.json --output artifacts/held
uv run aec frozen collision-coverage experiments/014-collision-coverage/experiment.json --output artifacts/coverage
uv run aec frozen limit-probe experiments/016-displacement-limit-probe/experiment.json --output artifacts/probe
uv run aec frozen experiment experiments/018-collision-step-backtracking/experiment.json --output artifacts/corrected-contact
```

The experiment writes structured input/state/solver history/diagnostics/version
and source hashes to `artifacts/single-contact/result.json` and four PNGs in
`renders/`. `artifacts/` is scratch space. Curated published evidence lives in
[experiments/001-single-contact](experiments/001-single-contact/notes.md).
Use `--output <directory>` to publish deliberately, and `--no-render` for a
solver-only run. A failed solve still saves its state and renders, then exits 1.

Headless rendering uses EGL by default; it requires system EGL/OpenGL drivers
(e.g. Mesa `libegl1` and `libgl1-mesa-dri` on Ubuntu). This environment renders
through software Mesa despite harmless device-permission messages. No DISPLAY,
interactive viewer or GPU access is required for the tested setup. Renderer
bytes can differ across driver versions; numerical state is the evidence.

## Research boundaries

- [Evidence audit and stack decisions](docs/research/evidence.md)
- [SI units, frames, calibration measurements](docs/research/frames-and-measurements.md)
- [States, action exploration, sweeps and frozen execution](docs/research/action-laboratory.md)
- [Recalculation profiles and limitations](docs/research/profiles.md)
- [Public evidence and generic seated setup family](docs/research/seated-setup.md)
- [Next falsifiable experiments](docs/research/roadmap.md)

Finite topology, metric geometry, anatomical model constraints, numerical
solver weights and ergonomic hypotheses have distinct provenance. Unknown
button travel is represented by null. No grid-distance difficulty or universal
ergonomic score is implemented. Contact requests are a collection; unsupported
gestures beyond the implemented index/middle pair are rejected explicitly.
The latest collision audit reveals unchecked finger-proxy overlaps even in
accepted gestures. See [014](experiments/014-collision-coverage/notes.md) and the
measurement protocol before treating a solver acceptance as human feasibility.
Published legacy inputs omit the collision implementation field and retain
Mink-native reproduction semantics. For new studies explicitly set
`solver.collision_limit_implementation = "displacement"`; its step-backtracking
budget and angular sampling resolution are recorded parameters. See 016–020
for dependency falsification, corrected solving and selective collision studies.
