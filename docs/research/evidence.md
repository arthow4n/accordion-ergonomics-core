# Evidence audit — 2026-10-08

This project begins with a laboratory fixture, not calibrated FR-1XB geometry.

## Instrument evidence

| Quantity | Category | Evidence and limitation |
|---|---|---|
| 62 right-hand buttons; C-Griff Europe mode | Manufacturer | [Roland brochure](https://cdn.roland.com/assets/media/pdf/fr-1x_brochure.pdf), specifications |
| Five row counts 12/13/12/13/12 | Derived from manufacturer diagram | [Owner's Manual p50](https://cdn.roland.com/assets/media/pdf/FR-1x_OM.pdf#page=50), visually counted and compared with both repositories |
| Finite coordinate bounds; C4=r1c5; MIDI 54–91 | Derived + implementation evidence | Manual p50 and repository mappings below; MIDI here denotes untransposed pitch assignment, not register-dependent acoustic octave |
| Same pitch on rows 1/4 and 2/5 | Derived from diagram | Full physical buttons enumerated; duplicate rows differ at boundaries (F#3 only on row4) |
| Relative row staggering | Derived from diagram | Equal logical columns have downward offsets `[0, .5, 1, .5, 1]` column spacings. The schematic supports alignment/order, not exact half-spacing in millimetres |
| 19 mm same-row centers; sqrt(3)/2 row spacing | Assumption | Synthetic triangular lattice, explicitly specified in experiment.json; no measurement |
| 13 mm diameter; 4 mm height | Assumption | Simulation fixture dimensions only |
| Button travel, force curve, cap shape, real curvature | Unknown | Not silently filled in; travel is null, rigid flat cylindrical buttons used only for static contact |
| Board-to-player translation, plane angle | Assumption | Fixed before solve, generic upright frame; no fitted instrument placement |
| Torso, arm, finger lengths/limits/couplings | Imported model | MyoSim 0.2.3; source-derived, not measured for this player |
| “Uncomfortable” angles or scalar difficulty | Unvalidated hypothesis | No comfort threshold or scalar is implemented |

A schematic showing curved *edges* does not establish a curved 3D playing surface.

## Repository inspection

Read-only shallow checkouts were inspected; no code was imported wholesale.

- [accordion-fingering-practice-midi at c1da37f](https://github.com/arthow4n/accordion-fingering-practice-midi/tree/c1da37ffae5f3b9fe61e8328ce7107145082d8e3): `src/core/cba/cbaLayout.ts`, `cba.test.ts`, `cbaErgonomics.ts`, `src/core/instrument/stradella.ts`. Finite bounds, pitch anchor, duplication and curated Stradella MIDI voicings are useful evidence. Stradella voicings can depend on device/register settings and are deferred here.
- [accordion-lead-sheet-companion at 7ce1a41](https://github.com/arthow4n/accordion-lead-sheet-companion/tree/7ce1a41119673b127541600cd2b08e328be5bab0): `src/lib/cba/keyboardLayout.ts`, `keyboardLayout.test.ts`, `grid.ts`, `melodyPath.ts`, `src/lib/stradella/layout.ts`, `transitions.ts`. Versioned finite layout and event/held-note representations are useful. They distinguish pitch topology from drawing offsets, but the physical embedding still needs correction against the manufacturer diagram.

The practice app's column/row weights 2.5/1.2, descending multiplier 1.8,
reversal penalty 2.2, and support-row bonuses are heuristics. Claims about gravity,
“devil rows” and collapsing hands are hypotheses, not published biomechanics.
Its out-of-range fallback invents a button at r1c5 for an unavailable pitch; this
project instead returns no mappings. The companion's 4/1.5 distance weights,
finger-crossing penalty 6 and squared stretch penalty likewise do not establish
physical feasibility. Treat its “physicalDelta” as pitch-coordinate arithmetic,
not a measured displacement or crossing detector.

**Spatial discrepancy:** the app drawing offsets `[0,-.5,0,.5,0]` disagree with
manual p50 when applied to its *absolute logical pitch columns*. In Roland's
diagram, at col5, C#4 in row2 is below C4 in row1, D4 in row3 is another half step
below C#4, and row4 C4 aligns with row2 C#4. The corrected fixture uses
`[0,.5,1,.5,1]`. Rows 1/3/5 still align as sets of centers modulo one full column.
This is a diagram-derived hypothesis for the metric embedding; caliper/photo
measurement should confirm it before ergonomic use.

## Stack decision and verification

Checked maintained distributions from PyPI metadata and primary documentation
on 2026-10-08. Installed and locked: MuJoCo 3.15.0, MyoSim 0.2.3, Mink 1.3.0,
NumPy 2.5.3, SciPy 1.18.1, Clarabel 0.11.1, Pillow 12.3.0; development Ruff
0.16.10, ty 0.0.85, pytest 9.1.1. These resolve and run on conventional CPython
3.14.7, the newest uv-managed stable build available in this environment.
Python 3.15 is still a release candidate as of this audit ([official announcement](https://www.python.org/downloads/release/python-3150rc3/)).
Python 3.14.8 is announced by Python.org, but `uv python install 3.14.8` reports
no managed download. This patch-level lag is recorded; update when uv provides it.
Supported minor version is explicitly `>=3.14,<3.15` until a new stack is tested.

- [MuJoCo](https://mujoco.readthedocs.io/en/stable/python.html): actual MjSpec composition, compiled poses, collision proxies and EGL rendering worked headlessly. No viewer dependency. Current state uses kinematics and collision inspection, not forward muscle-driven playing.
- [MyoSim](https://github.com/MyoHub/myo_sim/tree/93b0ca8f4ec90c9899ee7f05fee561e9911da91b): inspected current source and its arm README. Packaged 0.2.3 yields 38 scalar coordinates, 63 actuators, 11 equality constraints, fixed passive anatomical torso. Joint ranges and contact proxies have conversion/manual-adjustment provenance. These are not individually validated accordion biomechanics. Pin the anatomy release exactly to preserve this research object; record its installed source digest.
- [Mink](https://github.com/kevinzakka/mink): current release supports hard `EqualityConstraintTask` constraints, joint limits and collision-avoidance inequalities. All 11 imported couplings survive the solve. Local differential IK can converge, stall or pass through penetration because its linearized constraints are not a global collision-free path proof. Independent endpoint validation remains mandatory.
- [OpenSim/Moco](https://opensim-org.github.io/opensim-moco-site/): defer. Its muscle-driven optimal-control scope may address later effort/physiology questions; installing a second simulator would not establish unknown board geometry. No compatibility/performance claim is made without an experiment.
- [music21](https://music21.org/music21docs/): defer. Pitch/button mapping needs no harmony package. Later music generation/import can adapt to project-owned events and contact requirements.

MuJoCo's native pybind wildcard exports ship without typing stubs in this
installation. Ty reports unresolved attributes even for `MjModel` and
`mj_forward`. `_engine.py` explicitly isolates that untyped native boundary;
project domain inputs retain annotations and validation. No global type-check
rule was disabled.

## Generic seated setup evidence (023)

[Seated setup provenance](seated-setup.md) distinguishes Roland catalogue
365/195/380 mm overall dimensions from the unmeasured button lattice, case shape
and mount registration. Public pedagogy and inspected illustrations support
qualitative torso/thigh/upright-board relationships; disagreements about bellows
and thigh engagement remain documented. Broad numeric family intervals are
assumptions, not photo-derived measurements or population bounds. The implemented
solid shell is a separate conservative geometry hypothesis. Straps/support forces
and personalized calibration are not identified. Historical synthetic records
are preserved.

## MyoSim seated lower-body anatomy (029)

Prefer MyoSim resources for anatomical structure. The locked `myolegs` assembly
provides the pelvis and original bilateral bone meshes/kinematic chain (Rajagopal
lineage); `myolegs26` was inspected but adds no benefit to this fixed-skeleton
composition. See [seated-lower-body.md](seated-lower-body.md) for upstream primary
references, evaluated assets, exact adaptation and frame checks. Recorded whole-
package and compiled-model hashes bind the actual imported anatomy.

Keep these evidence categories distinct: imported bone geometry and joint
couplings; **assumed** seated angles/root pose; **approximate** femur-centered
support capsules; **assumed** brace station/direction and shell clearance; derived
board placement. A fixed bone mesh is not skin or a calibrated contact envelope.
No metric posture or tissue thickness is inferred from a photograph. 023–028
retain their original synthetic thighs and historical physical worlds.

## Native full-body assembly and kinematic reduction (031)

[031](../../experiments/031-full-body-architecture/notes.md) compiles the locked
MyoSim 0.2.3 `myoarm_r`, `myoarms`, `myolegs`, torso/arms assemblies and
`myofullbody`. The selected new default derives the whole skeleton from native
full-body composition and bakes prescribed passive posture, retaining the
original right-arm geometry, 38 coordinates, 63 actuators and 11 couplings.
Controlled compiled FK, Jacobians, bone meshes, tendon lengths and parameters
support right-arm parity; repeated measured runtimes support the reduction.
See [full-body-architecture.md](full-body-architecture.md) for source mechanisms,
benchmarks, migration and unresolved coverage.

Keep imported anatomical lineages separate: upper extremity from
[MoBL/MyoHand](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/arm/README.md),
spine/torso from
[constrained lumbar spine/MyoBack](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/torso/README.md),
legs from
[Rajagopal conversion](https://github.com/MyoHub/myo_sim/blob/main/myo_sim/models/leg/README.md),
and rigid cervical/skull/jaw meshes from upstream head resources. The native
assembly uses a shared root with separate sacrum and leg-pelvis descendants;
this phase preserves rather than recalibrates that relationship. Upstream
reported conversion/manual adjustments and muscle/soft-tissue limitations still
apply. The phase does not test original OpenSim equivalence or muscle force.

Generic seated angles, root height and relaxed left-arm posture are **assumed**.
Unchanged thigh capsules are **approximate support envelopes**. Native collision
proxies are uncalibrated rigid envelopes, distinct from skeletal meshes. New
independent queries expose up to about 87 mm left-arm/torso and torso/pelvis
proxy overlaps; right-hand coverage remains incomplete. We preserve that
negative evidence without shrinking envelopes or certifying accepted solves as
collision-valid human anatomy. No accordion metric/geometry changes or new
support/left-hand playing mechanics are inferred from anatomical completeness.
