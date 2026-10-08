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
unimplemented dimensions. Legacy scenes omit body/strap/instrument-shell contact. The optional
[seated setup](seated-setup.md) adds a coarse collision shell and schematic
support anchors; strap forces and anatomical thighs remain absent.

Panel extent and thickness were previously buried constants; they are now
fixture inputs, along with per-row staggering and board orientation. Flat
cylindrical caps are a model limitation. Travel remains unknown (`null`), and
the contact model does not simulate depression or force. Imported collision
coverage and joint ranges are model assumptions, not anatomical measurements.

API evidence: [MuJoCo model editing](https://mujoco.readthedocs.io/en/stable/programming/modeledit.html)
and [Python binary-model serialization](https://mujoco.readthedocs.io/en/latest/python.html).

## Geometric hand hypotheses

`player.model_mode = "kinematic_geometry_hypothesis"` permits an explicit
`geometric_hand_scale` about the imported `lunate_r` wrist origin. The transform
scales descendant translations, joint anchors, sites, primitive envelopes,
unique mesh assets and inertial geometry. Explicit masses scale cubically and
inertias by the fifth power as a constant-density geometric hypothesis. Forearm,
upper arm and wrist origin stay fixed. Joint axes/ranges and source couplings
are retained, so this is not an individually identified anatomical model.

All muscle actuators and tendons are removed in hypothesis mode, including at
scale 1 for a matched reference. This prevents unchanged muscle parameters from
being silently interpreted as physiological personalization. Scaling in the
imported musculoskeletal mode is rejected. The transformed model is used only
kinematically; no physiological or dynamic validity is claimed. Tests verify
wrist/arm invariance, hand/contact envelope scaling, SI dimensions, imported
ranges, mass/inertia exponents and the absence of actuators/tendons.

This is useful for sensitivity discovery, not evidence that a person's smaller
hand is a uniformly scaled generic hand. Individual finger/limb changes and
muscle recalibration remain unsupported. Proper anatomical scaling also needs
marker/segment calibration and configuration-dependent muscle treatment;
see the primary [OpenSim scaling explanation](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53089158).
MyoArm's contact envelopes are manually designed proxies, as documented in its
[model README](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/arm/README.md).

## Collision implementation and explicit pair hypotheses

New solver settings use displacement distance inequalities and sampled step
backtracking. New input should select `displacement`; published input without
the field preserves `mink_native` behavior. Canonical profile encoding omits the
implied native implementation and its unused guard settings, preserving historic
native-profile hashes. Corrected profiles record implementation, backtracking
count and maximum sampled angular step. Frozen source identifies the algorithm.

Mink 1.3.0 has confirmed displacement-unit and world-parent filtering defects,
documented upstream as unreleased fixes. The dependency stays locked. The project
adapter uses the public Limit contract; sphere fixtures and signed finite-
difference tests validate its arithmetic. A local inequality is not a continuous
collision proof; endpoint and edge checks remain necessary.

`physical_contact.additional_collision_pairs` contains canonical named proxies
with separate hypothesis evidence. Empty policy preserves the imported model and
historical profile hash. Nonempty policy adds engine pairs, changing model and
profile hashes while sizes, meshes and ranges stay fixed. Unknown/duplicate names
and same-body composite envelopes are rejected. Avoidance requires displacement
limits: native Mink filters out masked pairs. Pair distance still describes
uncalibrated imported shapes. Selective constraints do not validate omitted pairs.

## Generic body-anchored seated setup

`setup.torso.seated` activates the reference compact CBA model. Its typed
parameters and per-parameter provenance derive board placement from the imported
neutral shoulder, thorax outer support, instrument size and seated support height.
Explicit legacy board transforms remain supported. Derived inputs can omit
`setup.board`; any cached board transform is recalculated. Resolved profiles
include anchors and all assumptions; hashes change with setup variation.
Seated composition does not alter imported couplings or tissue proxies. See
[023](../../experiments/023-reference-seated-setup/notes.md) for validation and
remaining unchecked middle/ring penetration.
