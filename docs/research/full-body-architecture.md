# Full-body anatomical foundation

Experiment [031](../../experiments/031-full-body-architecture/notes.md) adopts
**`myofullbody_reduced` for new programmatic player profiles**. It derives the
entire body from the locked MyoSim `myofullbody` builder, retains the original
right-arm research system, and bakes a prescribed torso/left-arm/leg posture.
`myoarm_r` remains available and historical inputs continue selecting it.
`myofullbody_native` is an experimental prescribed-coordinate comparator.
No accordion geometry, topology, button metric, support mechanics or left-hand
playing task changes are part of this phase.

## What upstream actually builds

The tested distribution is `myo-sim==0.2.3`, as installed by `uv sync --locked`.
Its installed Python/component XML files are the primary implementation evidence;
031 records their aggregate source hash, package versions and compiled identities.
The [upstream repository](https://github.com/MyoHub/myo_sim),
[composition code](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/build/compose.py)
and [mirroring code](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/build/utils.py)
explain the mechanisms; live `main` is not a dependency commitment.

`build_fullbody_spec` builds the active torso, attaches the original right-arm
fragment at `arm_attach_r`, mirrors that fragment and attaches it at
`arm_attach_l`, then attaches the bilateral leg fragment to an identity frame
on `Full Body`. It adds native full-body contacts and sensors. The skull, jaw
and cervical meshes come from the upstream rigid head chain. No custom limbs,
skin or replacement skeleton are introduced.

The right fragment is exactly the `build_right_arm_spec` used by `myoarm_r`.
`myoarm_r` and `myoarms` use `make_torso_passive`, which deletes torso joints,
equalities, actuators and tendons while keeping its anatomical scaffold.
`myotorso_arm_r` and `myotorso_arms` retain the active torso. `myolegs` uses the
same passive scaffold plus the standard leg fragment and free root. Those are
all compiled and inventoried in 031, rather than inferred from their names.

| Upstream assembly | Joints | qpos / velocity coordinates | Actuators | Tendons | Equalities | Explicit pairs |
|---|---:|---:|---:|---:|---:|---:|
| myoarm_r | 38 | 38 / 38 | 63 | 67 | 11 | 4 |
| myoarms | 76 | 76 / 76 | 126 | 134 | 22 | 33 |
| myolegs | 29 | 35 / 34 | 80 | 80 | 14 | 26 |
| myotorso | 18 | 18 / 18 | 210 | 210 | 15 | 0 |
| myotorso_arm_r | 56 | 56 / 56 | 273 | 277 | 26 | 4 |
| myotorso_arms | 94 | 94 / 94 | 336 | 344 | 37 | 33 |
| myofullbody | 123 | 129 / 128 | 416 | 424 | 51 | 75 |

“123” is a joint count, **not 123 independent scalar degrees of freedom**.
The native free root contributes seven qpos and six velocity coordinates.
There are 51 scalar joint equalities: 15 torso, 11 per arm, and 14 bilateral
knee/patella dependencies. With the free root removed by the supported
`add_root_freejoint=False` option, 122 scalar coordinates remain; 71 are
independent after those equalities. Torso abdomen and knee motion include slides.

Torso joints drive a coupled lumbar chain, with two abdomen translations locked
by equalities. Each shoulder retains sternoclavicular/acromioclavicular,
scapular and humeral cancellation joints linked to shoulder elevation and its
plane angle; elbow, pronation/supination, wrist and all digit chains follow.
Hip, knee, ankle, subtalar and toe chains remain native. Leg knee translation,
secondary rotation and patellar transforms are polynomial dependencies.

**Composition is not single-subject anatomical validation.** The torso scaffold
sacrum and the leg-fragment pelvis are separate descendants of the common fixed
root, not one articulated pelvis-to-sacrum joint. The leg attachment uses rounded
1.57-radian rotations, whereas the torso uses higher-precision pi/2 values;
compiled pelvis axes differ slightly. This is inherited unchanged and tested.
The head is rigid; this phase does not introduce cervical/head motion.

The left mirror reflects local z positions, from-to points, mesh scale and
inertial products, adjusts axial vectors and quaternion components, and renames
side references. It uses the right mesh files under mirrored mesh definitions.
A non-neutral compiled test verifies world x reflection for shoulder, elbow,
palm and index distal landmarks to 1e-11 m, with equivalent named angles.
Mirroring is a symmetry construction, not evidence about an individual left arm.

The upstream sources distinguish MoBL/MyoHand upper extremity, the constrained
lumbar-spine/MyoBack torso and Rajagopal-derived legs. Their conversion/manual
adjustment and muscle-model limitations remain; see
[evidence.md](evidence.md). More anatomy does not establish greater physiological
accuracy, realistic muscle recruitment or measured soft tissue.

## Derived model and prescribed prototype

`full_body.py` starts with the public `myo_sim.load_spec("myofullbody")` API.
Upstream exposes editable `MjSpec`, root options, passive-torso deletion, and
arm-to-hand pruning, but no ready-made right-arm-only-active full-body preset.
We use MuJoCo's supported compile/edit/delete/frame mechanisms for this reduction.
The locked builder mutates its registration's `build_kwargs` dictionary; our root
option wrapper restores it on both success and failure. No installed assets are
edited, and a regression verifies the unmodified native model still has nv=128.

The reduced builder:

1. Compiles the native assembly at the named root frame and resolves a recorded
   prescribed posture and every scalar upstream equality.
2. Captures passive body transforms from compiled FK relative to their actual
   parents. For attached passive roots, replaces the attachment frame with an
   identity frame before writing those resolved transforms.
3. Deletes passive joints, their equalities, sensors and non-right muscle/tendon
   systems. Keeps all bodies, skeletal meshes and the original right-arm chain,
   63 muscle actuators, 67 tendons and 11 equalities. Passive wrap/site geometry
   is retained but hidden; removing it offers no demonstrated need in this phase.
4. Applies the explicitly named legacy right-arm diagnostic collision policy.
   Existing optional named right-finger pair hypotheses remain available.

This gives 38 compiled/solver coordinates, matching the historical right arm.
For an index-only solve, 16 inactive digit coordinates freeze, leaving 22
nonfrozen coordinates and 11 independent coordinates after shoulder equalities.
Those counts are distinct from the QP dimension, which remains 38.

The prescribed native comparator keeps all 416 actuators, 424 tendons and 51
equalities, and uses `DofFreezingTask` on the 84 non-right coordinates. Its QP
still has 122 variables. Passive velocities must satisfy the freezing constraint
within 1e-9 displacement, then their roundoff is set to zero before integration.
The collision-step sampler admits only hinges and explicitly prescribed,
stationary slides; moving slides/free joints still reject. A joint-range lock or
adding constant equalities alone would retain compiled runtime costs. Setting
actuator forces to zero would retain tendon evaluation. A separate projected
coordinate solver would add a second numerical path and is unnecessary given
the measured reduced-model runtime.

This is a static kinematic reduction. It is not equivalent to a full-body dynamic
simulation, gait system, muscle-control model or loaded chair/support equilibrium.
Changing a passive posture requires recompiling the reduced body and yields a
new model/profile identity. Use the native comparator to investigate prescribed
coordinate costs, not unconstrained full-body IK.

## Generic seated frame and right-arm parity

The comparison reuses the existing assumed 0.65 m root height and canonical
180-degree world-z rotation: world +x is player's right, +y anterior, +z up.
The unmodified native model uses root (-0.025, 0.1, 1) m. Aligning its root frame
is sufficient to compare neutral torso and right-arm kinematics with `myoarm_r`;
no right-joint name/index equivalence is assumed without field/FK checks.

The recorded body-only reference assumes upright torso, 90-degree hip/knee flexion,
5-degree hip abduction, 0.1-radian shoulder elevation and 0.35-radian elbow
flexion at rest, with neutral wrists/digits. The left arm rests freely; it is
not fitted to the accordion. No ground or chair is asserted. `FullBodyPosture`
records generic torso/left-arm/leg parameters; for existing seated setups the
recorded `SeatedLegs` hip/knee parameters take precedence, preserving the current
instrument/support calculation. Right-arm rest values are recorded separately
from playing IK inputs. All parameter choices are assumptions.

18 controlled configurations compare all right-arm body/geometry transforms,
marker position/orientation, positional/rotational Jacobians, muscle parameters,
tendon lengths, bone vertices/faces, ranges and all 11 equality links/coefficients.
Additional tests rotate the root, compare every native/reduced body and bone
under nonzero torso/left-arm posture, and verify a coupled directional Jacobian
against finite differences. This is right-arm kinematic parity, not identical
full-body dynamics. Native independent spine motion can change dynamic quantities
that this phase does not validate.

Right-hand contact markers still use the outer support of the compiled distal
capsule and ellipsoid. No phalanx scaling, range edits or coupling changes are
used to force parity. The existing single-/dual-contact tests and numerical
failure cases remain in the regression suite. Frozen C4 solves use the explicit
displacement collision adapter and sampled integration-edge checks.

## Collision policy and negative evidence

`legacy_right_arm_proxies_and_four_self_pairs_v1` retains the imported right-arm
proxy masks and four thorax/right-arm pairs; 031 also retains the existing 16
selective finger-pair hypotheses from 029. Non-right proxies stay in the model
but have zero automatic collision masks; extra native pairs are removed from
this matched-policy research scene. This is explicit incomplete coverage,
not a claim that left arm or legs are collision-valid. The upstream inventory
retains the unmodified 75-pair policy separately.

Independent cross-region queries preserve left-upper-arm/thorax and
abdomen/thorax/pelvis overlaps up to about 87 mm in the generic rest reference.
The audit identifies whether each pair is registered in the unmodified upstream
assembly and includes numeric IDs/body names for unnamed proxies. Some source
proxies intentionally compose broader envelopes; adjacent overlapping bones or
proxies cannot simply be treated as forbidden collisions. We do not shrink
geometry or blanket-enable pairs to obtain successful IK. Full finger coverage,
within-region passive checks, calibrated tissue and observed poses remain open.
The independently audited right-finger overlaps from 014 also persist.

Thus a successful C4 solve certifies only the stated numerical/diagnostic policy.
Anatomical completeness, right-arm kinematic equivalence, collision coverage,
solver reliability and biomechanical validity remain separate conclusions.

## Why retain the reduction for now, and when to revisit it

The reduced model remains the default for the current right-arm research phase.
Its justification is preserving the existing small active system while deriving
complete skeletal anatomy from upstream composition. The measured median C4
solve is 0.323 s reduced versus 0.634 s prescribed native: about 0.31 s saved
per solve, which can accumulate over repeated searches. This study did not
benchmark a complete atlas or establish a general performance ordering.
The saving is modest in absolute terms, and the benchmark supports keeping a
reduced option without requiring it to be the default.

The trade-off is explicit. Reduction increases setup time (2.399 s versus
1.403 s native), adds frame-baking/pruning code, and removes runtime articulation,
non-right muscle/tendon systems, constraints and sensors for the prescribed
body parts. All skeletal meshes and tested right-arm kinematics remain. The
fixed body must be rebuilt to change its prescribed posture. No anatomical
accuracy advantage or full-body dynamic equivalence is claimed.

This is a revisitable active-system choice. Future left-hand research will
likely use the same upstream full-body foundation with the **left arm and hand
active**, while prescribing or baking the **right arm, torso, pelvis and legs**,
analogous to the current right-active model. Left-hand support alone does not
require activating every body coordinate or retaining all muscle dynamics.
That left-active derivation is not implemented or validated yet; it needs its
own upstream parity, fingertip construction, coupling/range, collision-policy
and saved-state identity checks. Current right-arm states cannot be reused as
accepted states in it merely because coordinate counts happen to match.

Revisit the default when left-arm tasks are introduced, when both hands need
coordinated motion, or when posture changes, setup overhead or adapter maintenance
outweigh the measured repeated-solve saving. Compare a task-specific left-active
or both-arms-active reduction with prescribed native again under the actual
workload. Native remains an available alternative and may become the default if
its flexibility and simpler upstream ownership prove more useful. Keep current
and historical model identities explicit through any such change.

## Maintenance and migration

Native composition owns pelvis, spine, both shoulder attachments, mirrored arm
and bilateral legs. The project no longer needs to extract/prune/rename a second
leg skeleton for new body scenes. Its remaining custom work is compiled passive
FK baking, explicit posture parameters and collision-policy selection. There is
more preparation than the previous fixed-leg adapter, but no duplicated anatomy,
manual left-arm assembly or new skeletal assets. Benchmarks/inspection/replay
live separately in `architecture.py`; they are research tooling, not model code.

The old lower-body adapter remains for historical reproduction and for the
unchanged instrument setup anchor calculations. Removing it in this phase would
alter the instrument/body placement calculation, so that migration is deferred.
Future MyoSim upgrades must re-run field/FK/mesh/equality/parity and collision
checks; native composition alone does not promise compatibility.

`PlayerProfile()` selects the reduced assembly. `Experiment.from_dict` explicitly
uses the recorded `anatomy.model` and rejects disagreement with `player.model`.
Legacy profile serialization omits the new posture field, preserving historical
profile commitments; historical MJB guards remain strict. New profile/model
hashes include the assembly and prescribed posture. Even when nq=38 in both
models, historical accepted states cannot pass the new compiled-world guard.
Frozen records are never rewritten. Full-body body-render replay checks the
complete MJB before applying the saved qpos and restores renderer display arrays.

See 031 for measured costs, raw samples, all diagnostic views and reproduction.
