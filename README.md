# accordion-ergonomics-core

A Python research laboratory for articulated accordion ergonomics. New physical
instrument studies use one [generic closed five-row CBA](docs/research/generic-cba.md):
380 mm compact case with an independent upper wearing anchor (036),
rear-adjacent treble fingerboard, independent rigid cases, closed bellows, finite
62-button C-system treble and 96-button Stradella physical layout. Historical
rectangular worlds remain available with exact replay guards. The laboratory began
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
torso, shoulder and support anchors, with a documented setup family. New seated
profiles use fixed MyoSim pelvis/leg bones and explicitly approximate thigh
support envelopes; historical synthetic-leg results remain preserved.
New programmatic player profiles now use a reduced native MyoFullBody assembly:
original skeletal torso/pelvis, both arms/hands and both legs/feet, with only
the original right-arm coordinates active. Historical inputs explicitly retain
their original backend. See [the architecture comparison](experiments/031-full-body-architecture/notes.md)
and [anatomical foundation](docs/research/full-body-architecture.md).

**Current results are sampled kinematic predictions on assumed geometry with
incomplete anatomical self-collision coverage. Real playing feasibility,
button operation and continuous validity are not established.**
See [RESEARCH_LOG.md](RESEARCH_LOG.md) for findings and failed investigations.

## Exercise target library

The [50-target provisional catalog](targets/CATALOG.md) separates musical intent, physical
named five-finger contacts, search branches and actual frozen evidence. All human
feasibility values remain unknown. Use `uv run aec targets list`,
`uv run aec targets show central-c4`, and `uv run aec targets verify central-c4`.
The [manifest](targets/manifest.json) is machine readable; verification concerns
integrity, not physical truth. See [the library guide](targets/README.md) for
classification, descriptors, archived-source reproduction and search caveats.

Five-digit static controls and an index/ring dyad now retain saved-state contact
close-ups, proxy overlays and a matched frozen/free thumb comparison in
[041](experiments/041-five-finger-contacts/notes.md). Connected five-finger passage
search and autonomous generation remain the next active research milestones.

## Reproduce

Use conventional CPython 3.14 managed by [uv](https://docs.astral.sh/uv/).
The lockfile records the full tested dependency stack. Validation runs locally
for research milestones; automatic GitHub Actions checks are disabled.

```sh
uv sync --locked
uv run aec check
uv run aec frozen cba-geometry experiments/036-instrument-size-fit/compact-upper.json --output artifacts/cba
uv run aec cba-render artifacts/cba/result.json --output artifacts/cba-replay
uv run aec frozen architecture experiments/031-full-body-architecture/experiment.json --output artifacts/full-body-comparison
uv run aec body-render experiments/031-full-body-architecture/myofullbody_reduced/result.json --output artifacts/full-body-replay
uv run aec frozen experiment experiments/029-myosim-seated-lower-body/reference/experiment.json --output artifacts/seated-reference
# Historical family on synthetic thighs (preserved for comparison)
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
ergonomic score is implemented. Contact requests name distinct fingers and
buttons across all five digits. Support for a specification does not guarantee
a successful solve or anatomical validity.
The latest collision audit reveals unchecked finger-proxy overlaps even in
accepted gestures. See [014](experiments/014-collision-coverage/notes.md) and the
measurement protocol before treating a solver acceptance as human feasibility.
Published legacy inputs omit the collision implementation field and retain
Mink-native reproduction semantics. For new studies explicitly set
`solver.collision_limit_implementation = "displacement"`; its step-backtracking
budget and angular sampling resolution are recorded parameters. See 016–020
for dependency falsification, corrected solving and selective collision studies.

Connected five-finger passage search now separates pitches, physical duplicate
buttons, finger assignments and actual sampled movement. See
[042](experiments/042-connected-fingerings/notes.md) for alternate strategies,
recorded algorithm graphs and four actual-state animations, including collision
limitations and held-search failures. Import `ExerciseLibrary`, `Passage`,
`NoteEvent` and `discover_passage` from `accordion_ergonomics_core.research`; the
[consumer example](examples/consume_passage_library.py) retrieves trajectories
and checked media paths without manually browsing experiment directories.

[Autonomous discovery (043)](experiments/043-autonomous-discovery/notes.md) now
composes and physically evaluates generated challenges, allocating follow-up
effort from observed outcomes. The 50-target library includes selected generated
passages, alternate fingerings, exact animations and negative evidence. Use
`generate_challenges` for musical hypotheses or `discover_challenges` for bounded
evaluation; generated notes alone are never treated as physically solved.

[Internal consumer API (044)](targets/API.md) supports passage submission, generated
queries, earlier numerical trials, independent diagnostics, exact frame sequences
and archived-source replay into fresh directories. The [selected visual index](targets/VISUALS.md)
links representative model animations and algorithm diagrams to their source data.

[Biomechanical reassessment (045–048)](experiments/048-library-reassessment/notes.md)
adds pinned-muscle parity/force diagnostics, matched whole-hand/technique search
controls, posture counterexamples and versioned assessments of the existing
50-target library. Native tendon-routing anomalies and unsuccessful conditional
static equilibrium currently prevent a supported muscle effort ranking.

Use `ExerciseLibrary.assessment`, `ranked_comparisons`, `comparison_trajectory`,
`comparison_frame_sequence`, `muscle_screens` and `quality_media` to inspect the
results. [The portable quality example](examples/quality_consumer.py) retrieves
an actual retained little-finger alternative and its archived render command.
Whole-path preferences expose wrist/proxy tradeoffs; they do not certify ordinary
playing or human feasibility. The instrument, body reference and historical
catalog identities remain unchanged.

[Wrist/coordination research (049–052)](experiments/052-posture-selection/notes.md)
now separates signed absolute wrist posture relative to the imported geometric
reference from wrist movement. Posture-aware beam exploration and full-path
Pareto comparisons retain different fingerings and their clearance/travel
tradeoffs. Better reference posture can still produce worse cross-digit overlap.
Native inverse-wrap fallback switches and unsuccessful conditional support probes
keep muscle effort ranking withheld. No clinical neutrality, strain or human
feasibility is claimed.

`ExerciseLibrary.posture_assessment`, `posture_case`, `posture_trajectory`,
`posture_media`, `posture_comparisons` and `posture_evidence` retrieve the v2
assessments and exact model evidence while preserving the original catalog and
v1 API. See [the posture consumer](examples/posture_consumer.py).
