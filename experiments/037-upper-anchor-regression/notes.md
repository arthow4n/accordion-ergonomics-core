# Right-hand regression after the independent fit decision

Use the [036 compact-upper reference](../036-instrument-size-fit/notes.md):
380 mm case, upper H corner 40 mm below the neutral torso-attached shoulder.
C4 rises 41.507603 mm from 035; all horizontal target coordinates, board normals,
finite button geometry, case dimensions, anatomy and prescribed seated posture
remain the same. The v3 selector and new diagnostic landmark sites identify the
revised world. Old accepted states are not silently accepted here. The fit
choice preceded these solves and was not optimized for their results.

The torso, legs and left arm remain fixed. Treble, bass and closed bellows remain
fixed throughout each exercise. All 38 imported right-arm/hand coordinates and
11 couplings remain; shoulder mechanics are not artificially frozen. Preserve
035's displacement adapter, sampled integration checks and 16 named unmodified
index/middle proxy-pair hypotheses. These do not cover all finger self-collision.

## Contact and branch evidence

Fresh central solve uses the same numerical initial joint values as 035.
Eight attempts per target reuse its seven perturbations and 220-iteration
multistart cap. Every target has five accepted attempts; two perturbations fail
`initial_collision_violation`, and one produces an invalid initialization.
Duplicates are separate from solver failures. No failed initialization establishes
an anatomical reachability boundary. Candidate-0 values below are selected
examples; all alternatives, qpos/joint names, residuals and histories are saved.

| Target | Distinct candidates | Candidate-0 residual (µm) | Discovered palm diameter (mm) |
|---|---:|---:|---:|
| Index C4 | 3 | 99.003 | 115.846 |
| Index nearby D4 | 4 | 84.088 | 87.468 |
| Index C4 + middle C#4 | 4 | 65.579 | 30.059 |
| Index C4 + middle E4 | 4 | 83.699 | 104.991 |
| Index larger G6 relocation | 4 | 51.694 | 91.671 |

Maximum-residual contact diagnostics, individual contact reports and full
joint configurations are in each candidate's result.json. These are rigid
released-cap contacts, not depression or demonstrated playing feasibility.
Central equality residual is 2.78e-17 rad and registered maximum penetration is
zero. Actual central active-cap envelope distance is approximately its marker
residual, within the frozen 0.1 mm contact tolerance.

| Selected central joint coordinate (degrees) | 035 lower plane mount | 037 upper anchor |
|---|---:|---:|
| Shoulder elevation | 56.069 | 23.931 |
| Elbow flexion | 126.175 | 110.335 |
| Forearm pro/sup | −32.290 | −34.780 |
| Wrist deviation | −9.653 | 16.462 |
| Wrist flexion | 17.405 | 43.955 |

The selected branch reduces shoulder elevation while increasing wrist flexion.
These solver-coordinate changes are not measured comfort, effort or a unique
necessary posture. The large palm candidate diameters expose branch sensitivity;
do not credit instrument size, which is unchanged, or describe the new default
as easier on the basis of this branch.

## Small transitions and held attempt

`nearby/` connects central C4 to nearby candidate-0 using sampled incremental
withdrawal/RRT/approach: palm path 63.669 mm. `larger/` finds a direct sampled
joint interpolation to G6 candidate-0: 162.518 mm. Both use the existing 0.002 rad
sampling and explicit endpoint hashes. Their selected branches differ from 035,
so comparing its 35.85/163.74 mm paths does not isolate the wearing-height effect
on a global minimum movement. Solver iteration histories are not trajectories.

`held/` holds index C4 while middle moves C#4→E4. Direct interpolation is rejected;
a 22-waypoint solve finds a sampled held path. Maximum held marker residual
81.478 µm, normal error 0.000597 rad and active held-cap distance 54.238 µm;
palm path 71.282 mm, registered sampled penetration zero. This is a found
continuation for these branches, not proof that 035's failed search was physical
impossibility or that higher placement generally improves held playing.
Continuous validity and button operation remain unestablished.

## Independent collision audit and rendering

`coverage/` independently audits central plus all 19 distinct contact endpoints
against every instrument solid and unchanged right anatomical proxies. Across
20 endpoints: minimum case/rim clearance 2.437 mm, panel clearance 4.023 mm,
and cap clearance 23.403 µm. Unchecked cross-digit overlap counts remain 11–20,
maximum rigid-proxy depth 10.318 mm. `held-coverage/` independently audits the
resulting held endpoint: 15 unchecked overlaps, maximum depth 10.318 mm.
These invalidate any claim of fully collision-valid anatomy. Intermediate
finger coverage has not been certified; sampled engine/pair validity of the
path does not close that gap. No proxies or collision masks were weakened.
Passive-body/instrument proximity is separately established at the fixed-body
reference in 036; the current moving right-arm instrument audit covers all solids.

Inspected all four saved-state views for central, simultaneous, larger contact,
ordinary-path middle states and held last state, plus highlighted held collision
coverage. The cases remain fixed and the lap gap persists during exercises.
Some original playing images carry the stable root's v2 caption; explicit inputs,
profiles and hashes identify v3. `central-reviewed/` reruns after correcting that
caption, with exactly the same compiled model and qpos as central. All four
reviewed images reproduce byte-for-byte from its saved state. Archived images
and source commitments remain unchanged.

## Reproduction and integrity

```sh
uv run aec frozen experiment experiments/037-upper-anchor-regression/central.json --output artifacts/037-central
uv run aec frozen explore experiments/037-upper-anchor-regression/explore/experiment.json --output artifacts/037-explore
uv run aec frozen plan experiments/037-upper-anchor-regression/nearby/experiment.json --output artifacts/037-nearby
uv run aec frozen plan experiments/037-upper-anchor-regression/larger/experiment.json --output artifacts/037-larger
uv run aec frozen held experiments/037-upper-anchor-regression/held/experiment.json --output artifacts/037-held
uv run aec frozen collision-coverage experiments/037-upper-anchor-regression/coverage/experiment.json --output artifacts/037-coverage
uv run aec frozen collision-coverage experiments/037-upper-anchor-regression/held-coverage/experiment.json --output artifacts/037-held-coverage
uv run aec render experiments/037-upper-anchor-regression/central-reviewed/result.json --output artifacts/037-replay
uv run aec verify experiments/037-upper-anchor-regression/held --require-complete
```

All eight frozen roots verify with complete integrity. Definitions deliberately
point to published hashed inputs; for a wholly new chain update the relative
paths and hashes explicitly. Original central input bytes are also preserved
beside both central result roots so verification includes their input commitment.
100 tests, Ruff and ty passed; five focused frame/render/identity tests passed
after the final optional diagnostic/caption adjustments. Verification checks
hashes and links, not physical validity. No atlas expansion, strap equilibrium,
active instrument motion or additional anatomy was introduced.
