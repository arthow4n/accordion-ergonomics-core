# MyoSim seated lower-body reference

New programmatic `SeatedSetup()` profiles use fixed MyoSim anatomy. The recommended
serialized baseline is [029](../../experiments/029-myosim-seated-lower-body/notes.md),
with an explicit `setup.torso.seated.lower_body` block. Older serialized inputs
without that block retain their historical synthetic thighs. This compatibility
rule preserves their profile commitments and compiled models; it is not the
recommended new setup. Explicit `lower_body: null` selects the historical scaffold.
For this project, prefer MyoSim anatomy whenever it reasonably supplies the
required structure.

## Assets evaluated and choice

The locked `myo-sim==0.2.3` package supplies these composed assemblies:

| Assembly | Locally compiled qpos / equalities | Relevant structure | Decision |
|---|---:|---|---|
| `myolegs` | 35 / 14 | Bilateral pelvis, femurs, patellae, tibias, talus, calcaneus and toes; passive torso scaffold | Use bone meshes and resolved seated kinematics |
| `myolegs26` | 47 / 28 | Reduced muscles and simplified chain; numerous moving-via-point coordinates; same broad passive torso scaffold | No advantage for a muscle-free fixed skeleton; different source lineage |
| `myofullbody` | Upstream advertises 123 DoF / 416 muscles; not loaded into our solver | Torso, both arms and legs | Unnecessary replacement of the established right-arm assembly |

These are actual local compiled counts for the first two models, not the upstream
advertised independent anatomical DoF counts. The standard legs are derived from
[Rajagopal et al. 2016](https://doi.org/10.1109/TBME.2016.2586891), as documented by
[MyoSim's leg README](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/leg/README.md).
The reduced model has a gait2392/gait9dof18 lineage instead. The
[upstream assembly registry](https://github.com/MyoHub/myo_sim) documents passive
torso and full-body alternatives. These are anatomical model references,
not observations of seated accordion players. Current upstream pages can change;
actual geometry comes from the locked package, whose complete file digest is
recorded with every result. No third-party imagery is copied into this repository.

## Composition and coordinate frames

Evaluate `myolegs` with the same `Full Body` root position/quaternion as MyoArm.
Both assemblies use the same passive torso scaffold and root/sacrum placement.
Keep the arm's sacrum/torso; remove the leg assembly's duplicate sacrum subtree.
Keep the original leg pelvis and bilateral bone meshes, including patellae and
feet. No handmade replacement femur or knee geometry is introduced.

Set the upstream hip and knee coordinates, evaluate all 14 polynomial equality
couplings (including knee translation/rotation and patellar motion), then run
forward kinematics. Bake each body's **compiled** pose relative to its compiled
parent. Remove lower-body joints, actuators, tendons, sensors, wrapping objects,
contacts and decorative room geometry before attaching the retained bone subtree
with a `seated_` prefix. The original mesh assets and transforms remain intact.
The arm solver still has 38 qpos/velocity coordinates, 63 actuators and 11
couplings. No lower-body muscle simulation or stepping is involved.

The imported leg pelvis uses an OpenSim-style basis internally. MyoSim's composed
frames resolve that basis into its scaffold; our existing root rotation then
maps into world +x player right, +y forward, +z up. Do not manually substitute
that basis or infer compiled orientation from raw quaternion fields. Regression
checks compare bone positions/orientations against the original posed assembly,
including under a rigid torso rotation, and preserve the historical 023 MJB hash.

## Fixed pose and honest parameter family

| Parameter | Reference | Exploratory range | Evidence and uncertainty |
|---|---:|---:|---|
| Bilateral hip flexion | 90° | 80–100° | Assumed seated pose; teaching's upright/right-angle sitting is qualitative guidance, not a measured interval |
| Bilateral hip abduction | 5° | 0–10° | Assumed modest leg separation; no population measurement |
| Bilateral knee flexion | 90° | 80–100° | Assumed fixed seated bend; original MyoSim knee couplings retained |
| Thigh capsule radius | 75 mm | 60–90 mm | Approximate support envelope, **not imported anatomy or calibrated tissue** |
| Brace station along hip→knee axis | 0.45 | 0.30–0.60 | Assumed mid/proximal thigh engagement; no measured bracing station |
| Root position/quaternion | (0,0,0.65) m / canonical upright | Existing setup profile | Absolute root height is a placement assumption; no chair or ground contact calibration |

The reference angles are convenient nominal assumptions, not universal exact
posture. Broad implementation rejection bounds are not the exploratory range.
Pedagogical context comes from [Hermosa's notebook, pp. 3–4](https://www.gorkahermosa.com/web/img/publicaciones/3568a.pdf)
and the distinctions in [seated-setup.md](seated-setup.md). Their guidance is
neither an anatomical constraint nor proof of our numeric angles. Generic anatomy
and fixed pose are distinct from optional personal calibration.

## Skeleton versus support envelopes

White bone meshes are imported anatomical structure, with collision masks zero.
Translucent blue capsules are explicit approximate soft-tissue/support envelopes:
their centerlines run between the **compiled hip and knee landmarks**, with an
assumed radius. They are visual/support diagnostics, not solver collision anatomy.
All imported lower-limb collision proxies are removed, rather than claiming they
form a seated tissue surface. The arm's original collision proxies remain intact.

The orange right-thigh brace landmark is independent of accordion placement:
interpolate the hip→knee centerline at `support_fraction`, project an assumed
upper-medial direction (30° inward from torso-up) perpendicular to the femur axis,
and offset by the capsule radius. This angular choice is a heuristic, not a
measured contact normal. The cyan landmark is the separate treble support corner.
Their separation is reported, not constrained to zero.

Vertical support uses a different, conservative plane: the highest endpoint of
either femur capsule along torso-up, plus the assumed radius. Place the whole
shell above that plane by `support_clearance_m`. The old
`support_height_above_root_m` input is **legacy-only** when anatomical legs are
selected; the derived plane supersedes it. Rear thorax clearance, shoulder-relative
outer edge, instrument dimensions and board orientation retain the existing model.

Query signed shell-to-capsule distances explicitly even though fixed masks suppress
engine contacts. Diagnostics report them separately as
`approximate_support_envelope_distances_m`; they do not confer an anatomical
collision certificate. The first attempt using the upper-medial brace height as
the vertical plane was rejected for intersecting the capsules. Neither proxy
radius nor skeletal dimensions were shrunk to hide this error.

## Limits

There is no support-force equilibrium, strap mechanics, seat, foot/ground contact,
skin surface, soft-tissue calibration or individualized anatomy. A clearance of
10 mm represents near support with unresolved material compression and support
geometry; it is not actual loaded contact. Skeleton realism improves the reference
frame but does not certify the accordion posture. The finite keyboard lattice and
coarse case/bellows box remain hypotheses at Roland's overall published scale.
Unchecked finger overlaps remain a separate known problem. Lowering the keyboard
changes arm solutions and can increase wrist flexion; smaller shoulder angles do
not establish improved technique or lower effort.

## Small variation check and numerical portability

[030](../../experiments/030-seated-leg-variation/notes.md) samples hips at 80/100°
and an assumed 90 mm thigh radius. All have positive coarse shell/envelope
clearance; 80° needs another seed to find a central contact. The conservative
higher-endpoint plane changes board height by −6/+70 mm for the hip cases and
+15 mm for radius alone. Those are model sensitivities, not measured human ranges.
Unchecked finger overlaps remain in every successful variation pose.

New nontrivial baked transforms need not have identical last-bit arithmetic on
all hosts. CI compares recorded geometry/profile fields within 1e−12 and exact
repeat model compilation within its own runtime. Production state/model guards
still use exact hashes: a cross-environment mismatch requires re-solving the
recorded inputs, never bypassing the guard. Local byte-identical image replay
therefore establishes reproducibility only in the recorded rendering environment.
