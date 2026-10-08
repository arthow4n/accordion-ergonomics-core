# Small v2 right-hand regression and initialization sensitivity

Geometry was validated independently in [034](../034-cba-mounted-orientation/notes.md)
before these studies. Compare the current 20-degree `generic_cba_v2` with the
matched rectangular/full-body control saved under 033/old-*. That control uses
the same full-body reduction, active right-hand coordinates, 16 named additional
index/middle self-pairs, contact requirements and displacement collision adapter.
It is a fresh coarse-world control, not a reinterpretation of earlier research.
The revised component-based wearing placement is part of the comparison: these
results do **not** isolate housing shape from placement.

## Contact positions and posture

Reference C4 targets (world mm) change from (171.965,213.593,982.692) to
(157.573,56.962,942.692): delta (-14.392,-156.631,-40.000). Both control and v2
button normals are (0.5,sqrt(3)/2,0), preserving seated board-frame orientation.
V1's rejected mounting had almost lateral normals; it is not the current control.

| Reference central C4 solve | Coarse control | Physical v2 |
|---|---:|---:|
| Marker position residual (um) | 76.463 | 21.863 |
| Actual active-cap envelope distance (um) | 76.220 | 21.840 |
| Shoulder elevation (deg) | 13.222 | 56.069 |
| Elbow flexion (deg) | 101.360 | 126.175 |
| Forearm pronation/supination coordinate (deg) | -33.986 | -32.290 |
| Wrist deviation coordinate (deg) | -9.554 | -9.653 |
| Wrist flexion coordinate (deg) | 28.945 | 17.405 |

These are solver-coordinate values for selected solutions, not clinical angles,
necessary human posture, or measured effort. Original 11 anatomical couplings
remain; central equality residual is below 3e-17 rad. `central-reviewed/` reruns
the reference after a cosmetic caption correction: compiled model and numerical
qpos are exactly identical to the earlier `central/` baseline used by explore.
The baseline's archived images retain a v1 caption typo despite explicit v2
input/profile/model identity; reviewed images label v2 and replay byte-for-byte.
No result files or execution commitments were rewritten to hide this distinction.

## Finite multistarts

Each target has eight attempts: baseline plus the same seven perturbations as
033 (elbow/forearm +/-0.3, shoulder rotation +/-0.2, wrist flexion -0.15,
middle abduction +/-0.1 rad). Iteration cap 220; finite target identities and
explicit participating fingers are in `explore/experiment.json`.

| Target | Coarse distinct candidates | V2 distinct candidates | Palm candidate diameter coarse/v2 (mm) |
|---|---:|---:|---:|
| C4 index | 2 | 4 | 7.84 / 45.44 |
| D4 index, nearby | 4 | 4 | 34.23 / 89.53 |
| C4 index + C#4 middle | 3 | 4 | 47.81 / 77.68 |
| C4 index + E4 middle | 4 | 4 | 113.79 / 96.59 |
| G6 index, larger relocation | 5 | 4 | 167.90 / 151.41 |

V2 starts 2 and 6 are inadmissible after perturbation; starts 4 and 7 fail initial
collision checks. Other four starts succeed for all five tasks. Coarse outcomes
also depend on starts, including stalled/no-clear-step and collision failures.
All attempt states, reasons and solver histories are retained. Candidate count
is affected by admissibility and deduplication as well as convergence; it is not
coverage of human possibilities. For G6, wrist-flexion coordinates across found
candidates span 48.0 degrees coarse and 59.0 degrees v2. New discoveries neither
minimize movement nor resolve the anatomy's unchecked overlaps.

## Sampled transitions and held contact

Endpoint selection chooses the smallest discovered palm relocation from each
world's own C4 reference; held endpoints minimize maximum joint-coordinate
difference among the discovered two-contact candidates. These are explicit
finite heuristics, not global optima. Identical planner settings use 0.002-rad
sample spacing, 1/2/4/8 cm withdrawals, 2 mm Cartesian steps, 220 waypoint
iterations and bounded RRT seed3309. The v2 large direct attempt fails its sampled
collision check and succeeds after withdrawal; preserve both attempts.

| Task | Coarse result / palm path | V2 result / palm path |
|---|---|---|
| Nearby C4 -> D4 | withdrawal/approach, 50.24 mm | direct interpolation, 35.85 mm |
| Larger C4 -> G6 | direct interpolation, 116.40 mm | withdrawal/approach, 163.74 mm |
| Hold index C4, move middle C#4 -> E4 | no held path found | no held path found |

Accepted ordinary paths have zero recorded sampled penetration under configured
constraints. V2 palm maximum excursions are 35.80/134.26 mm; coarse 43.12/113.76
mm. These are discovered paths, not minimum human-required motion, execution
timing, or continuous validity. Both held searches fail a waypoint solve;
selected endpoints and finite search do not establish impossibility. No active
bellows or left-hand optimization was added.

## Independent clearance and collision limitations

`coverage/` and `old-coverage/` independently audit 17 recorded endpoints each,
with all 230 cross-digit proxy pairs and every instrument solid (including every
cap and fingerboard, not just case walls). This new diagnostic adds no collision
pairs or mask changes. Instrument component minima query actual imported outer
proxies, independently of target markers. Across v2 endpoints the closest panel
clearance is 3.581 mm; closest case/rim clearance is 1.527 mm (thumb/outer rim).
The coarse global envelope comes within 2.72 um of a thumb proxy. Small active
cap penetration is explicitly retained: up to 13.19 um v2 versus 0.44 um coarse,
within existing frozen tolerances. Selected self-pair penetration in solver
reports reaches 57.88 um v2, 51.22 um coarse; do not call these zero-error states.

Unchecked cross-digit overlap counts are 17..31 v2 and 12..26 coarse; maximum
unchecked rigid-proxy depths are 12.808 and 13.300 mm. Central states have 25 and
17 unchecked overlaps respectively. The numerical instrument improvement does
not certify anatomical feasibility. Soft-tissue envelopes, self-collision,
wearing angles and load equilibrium remain uncalibrated. Proxies are preserved;
no geometry/anatomy was shrunk to obtain results.

Four diagnostic views plus collision overlays were inspected for central,
representative two-contact, nearby/large path states and the failed held state.
Geometry's five body views remain in 034. Source archives, lock/profile/model
hashes, all failed attempts, and complete integrity reports accompany records.
97 tests, lint and type checks pass; relevant coverage tests also verify that no
panel/cap is omitted from the independent instrument audit. Integrity validation
is not scientific validity.

## Rerun

Use `uv run aec frozen experiment`, `explore`, `plan`, `held` and
`collision-coverage` with the respective `experiment.json` files and fresh
artifacts outputs. Referenced input paths/hashes are intentional: exploration
uses the exact archived central baseline, paths use selected exact candidates,
and coverage uses recorded endpoints. A renamed output root does not change the
relative paths resolved from the input definition. Reproduce old controls from
033's frozen snapshots if future source diverges. Run `uv run aec verify DIR
--require-complete` for each executed root; the parent summary directory has no
single frozen workflow. No solver iteration history is a playing trajectory.
