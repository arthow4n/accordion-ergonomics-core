# Recalculation and calibration boundaries

Schema 2 separates metric instrument geometry, board/torso setup, player range
assumptions, rigid-contact policy and solver configuration. Schema 1 remains a
legacy importer. `experiments/004-profile-recalculation/experiment.json` records
all current defaults explicitly. Lengths use metres, angles radians, rotations
unit quaternions in wxyz order. Board placement is a rigid transform from the
canonical u/v/n frame. Torso placement transforms the imported scaffold.

Every new result embeds the original input and fully resolved profiles, their
canonical JSON SHA256, source/lock/package hashes and a complete compiled MJB
model hash. Rendering compares that model hash before replay. A model mismatch
requires recalculation rather than silently displaying a different world.
MJB hashes are specific to MuJoCo versions; binary portability is not claimed.
Legacy results without a compiled hash retain their original weaker safeguards.

Change an input, then run `uv run aec experiment INPUT --output OUTPUT`.
Published historical experiments remain immutable evidence; new computations
belong in new experiment directories or scratch `artifacts/`.

Supported player calibration currently means explicit joint-range overrides and
rigid torso placement. Finger/palm/limb dimensions are imported, not individually
measured. Uniform coordinate multiplication would also affect inertias, muscle
paths, wrapping surfaces, collision envelopes and anatomical couplings; it is
not offered as physiological personalization. Segment-specific transformation
and validation remain research work. The schema does not claim to support
unimplemented dimensions. Body/strap/instrument-shell contact is absent.

Panel extent and thickness were previously buried constants; they are now
fixture inputs, along with per-row staggering and board orientation. Flat
cylindrical caps are a model limitation. Travel remains unknown (`null`), and
the contact model does not simulate depression or force. Imported collision
coverage and joint ranges are model assumptions, not anatomical measurements.

API evidence: [MuJoCo model editing](https://mujoco.readthedocs.io/en/stable/programming/modeledit.html)
and [Python binary-model serialization](https://mujoco.readthedocs.io/en/latest/python.html).
