# Recorded states, finite action search and sensitivity

`aec atlas` re-solves a recorded source contact for the supplied parameter
profile, then discovers index-button endpoint candidates and independently
searches transitions. States carry named radian coordinates, current contact
IDs and a resolved-profile hash. A state from another parameter world is rejected.
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

Headless `render` can also run from an archived source snapshot. The model hash
must match. New configurations should produce new evidence directories, leaving
old experiments inspectable.

## Small simultaneous-contact formulation

`aec experiment` now accepts one or two distinct index/middle contacts.
Both marker/normal tasks are solved together; acceptance independently checks
both actual distal-envelope/button distances, all source equalities, limits
and detected collisions. Unused digits remain present and frozen. This is not
button depression, force, a held-contact path or human feasibility. Candidate
and transition discovery currently explicitly support one index contact only;
unsupported requests are rejected rather than silently solved with another digit.
