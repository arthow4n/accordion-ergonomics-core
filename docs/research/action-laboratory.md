# Recorded states, finite action search and sensitivity

`aec atlas` re-solves a recorded source contact for the supplied parameter
profile, then discovers index-button endpoint candidates and independently
searches transitions. States carry named radian coordinates, explicit button
and finger bindings and a resolved-profile hash. State schema 2 rejects ambiguous
legacy contact strings; archived schema-1 algorithms remain replayable. A state
from another parameter world is rejected, as is a state whose declared contacts
fail independent current-geometry validation.
Candidate descriptors preserve palm pose, elbow position, wrist/forearm/shoulder
and finger articulation and both all-coordinate and active-coordinate margins.

The three-start full-board experiment is a finite search, not an exhaustive
reachability proof. `sampled_transition_found`, `no_pose_found` and
`no_transition_found` are separate outcomes. Global human feasibility and
continuous validity remain unknown. Relocation is the best discovered accepted
path endpoint's palm displacement; it is not a globally minimized displacement.
The board image uses continuous measurements; X denotes a missing discovered
solution. All attempted poses/paths remain in per-action JSON, referenced by
hash from the compact atlas index.

`aec sweep` applies strict named profile patches, recalibrates the source
contact, and repeats identical queries. It compares search status and palm
relocation separately. If source-contact discovery fails, comparison is
unavailable rather than "no changes". Misspelled parameters are rejected.
Player range overrides receive explicit assumed provenance unless supplied
with their own evidence; imported dimensions are not individualized.

## Freeze executing source

Long experiments can outlive source edits in an autonomous workspace. Cached
Python modules otherwise run old code while a hash reads newly edited files.
Use:

```sh
uv run aec frozen atlas experiments/007-index-atlas/experiment.json --output artifacts/atlas
uv run aec frozen sweep experiments/008-geometry-sensitivity/experiment.json --output artifacts/sweep
```

The runner copies package code, writes a deterministic `source-snapshot.zip`
and executes that copy in the current locked uv environment. It records source,
archive and lock hashes. Input definitions are read/hash-recorded from the same
bytes. To rerun the exact archived algorithm, add `--source-snapshot PATH`.
Recorded dependency versions and anatomy hashes still matter; a source archive
alone does not preserve dependencies. Canonical execution remains `uv run`.

Check a published frozen record without rerunning its numerical search:

```sh
uv run aec verify experiments/018-collision-step-backtracking experiments/022-held-contact-with-self-pairs --require-complete --output artifacts/verification.json
```

The verifier checks archived source bytes, executed-source/lock commitments,
resolved profile hashes where recorded, exact input bytes and workflow-specific
referenced evidence. It handles pose discovery, coverage audits, atlas/sweep,
held/exercise/plan and collision-limit records. `--input PATH` supplies the raw
definition for a single output directory when it lives elsewhere. Missing
metadata is reported as `partial`; mismatches are `invalid` and exit nonzero.
`--require-complete` also fails partial verification. Tests audit the seven
latest heterogeneous records and inject archive, input, profile and lock
changes. This is integrity verification, not numerical reproduction, dependency
preservation, authentication or physiological validation. Unhashed result
fields and rendered pixels are not certified by this command.

Headless `render` can also run from an archived source snapshot. The model hash
must match. New configurations should produce new evidence directories, leaving
old experiments inspectable.

## Small simultaneous-contact formulation

`aec experiment` now accepts one or two distinct index/middle contacts.
Both marker/normal tasks are solved together; acceptance independently checks
both actual distal-envelope/button distances, all source equalities, limits
and detected collisions. Unused digits remain present; the default freezes
them, while an explicitly sourced `inactive_digits_policy=allow_articulation`
allows imported digit movement. This is not button depression, force or human
feasibility. Pose discovery supports an index primary contact with an optional
middle contact; both bindings and all digit articulation are preserved.
Transition and atlas discovery currently support single-index requests.
Unsupported requests are rejected rather than silently solved with another digit.

`aec held` is a separate small index-held/middle-moving experiment: it constrains
the held contact while building Cartesian withdrawal/translation/approach
waypoints, then audits every sampled configuration independently. It exports
the resulting gesture, which need not equal the supplied local-IK endpoint.
No holding force or continuous certificate is inferred.
Additional declared self-pair distances are queried independently along the
held path, including when engine contact registration is absent. Experiment 022
demonstrates held motion under 16 selected pairs. Optional animation uses saved
audit samples and records display timing separately from unmodeled playing tempo.

`aec exercise` selects a large discovered relocation from a hash-checked atlas,
refines its edge audit and exports the physical action, trajectory, excursions,
musical surface-contact events and independently checked endpoint. Its ranking
is descriptive, not a universal difficulty score or proof of minimum relocation.

## Collision coverage is part of the contract

`aec collision-coverage` checks recorded compiled models, enumerates mask and
explicit-pair policy and independently queries cross-digit proxy distances.
Imported proxies disable automatic anatomical self-collision; only four explicit
thorax/arm pairs remain. General finger clearance is not enforced. Diagnostic
magenta highlights unchecked overlaps separately from detected contacts.
The [014 audit](../../experiments/014-collision-coverage/notes.md) identifies large
overlaps in dual-contact poses. Neither the atlas nor held-task successes are
certificates of full anatomical nonpenetration. Envelopes need validation before
broader ergonomic conclusions, rather than arbitrary shrinking or relaxed costs.

Experiments 019–020 subsequently add a selective 16-pair index/middle phalangeal
hypothesis without resizing. C#4 dual-contact candidates and six sampled index
transitions are found under those constraints; omitted pairs remain unvalidated.
`aec explore` accepts named multi-contact targets and strict parameter patches
so matched studies can separate pair policy from geometry and solver changes.
