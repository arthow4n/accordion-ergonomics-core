# Independent instrument size and seated fit

Decision: retain compact dimensions; adopt the independently anchored
`generic_cba_v3` compact-upper reference. [Research note and source audit](../../docs/research/instrument-size-fit.md)
explain evidence categories, instructional differences and uncertainty.

## Controlled design

A: `compact-upper` versus `tall-upper`: change only enclosure/backing/bellows
height 380→430 mm and lower strap stations; preserve every board target, depth,
component width, posture, upper anchor, torso clearance and orientation.
B: `compact-low/upper/high`: identical compact geometry, upper offset −80/−40/0 mm.
C: historical-plane versus chosen compact-upper and alternative tall-high is a
coupled practical comparison, not a size-effect claim. Tall-low is rejected
negative evidence using the same independent anchor family. No case is lowered
to touch a thigh automatically. None of these neutral scenes is a contact solve.

| Candidate | Bottom minus thigh station plane (mm) | Right thigh signed (mm) | Left thigh signed (mm) | All imported proxy minimum (mm) |
|---|---:|---:|---:|---:|
| historical-plane | 10.000 | 11.840 | 11.275 | 3.617 |
| compact-low | 11.508 | 13.347 | 12.783 | 4.045 |
| compact-upper | 51.508 | 53.342 | 52.778 | 10.842 |
| compact-high | 91.508 | 93.337 | 92.773 | 10.842 |
| tall-low | -38.492 | -36.647 | -37.211 | -37.423 |
| tall-upper | 1.508 | 3.348 | 2.784 | 1.472 |
| tall-high | 41.508 | 43.343 | 42.779 | 10.842 |

Every result contains upper/shoulder/pelvis/hip/knee/board/strap landmarks,
relative corner vectors, per-bone convex and all native proxy distances, and
right-arm collision coverage. Passive proxy queries ignore engine masks.
Negative values in tall-low include pelvis and femur proxies; no bone-hull
intersections occur in these seven scenes. Neutral humerus/thorax overlap
predates this study and is not repaired. Thigh capsules are synthetic envelopes.
The 10 mm torso support-plane hypothesis remains, with actual closest thorax
clearance 10.842 mm; planes and signed curved-surface distances differ.

## Saved-state image review

Inspected front, right, left, oblique and treble close-ups for all candidates;
also inspected all four body views of rejected tall-low. The compact-upper gap
is visible in both side views. Taller height extends down without changing the
board/upper region. Compact-low approaches the thigh without penetration;
tall-low enters it. Upper chest remains forward of rib bones under the retained
proxy support hypothesis, not calibrated against skin. Gold strap stations do
not simulate straps or establish force support. Green pelvis/hip/knee, red
shoulder, cyan upper/lower case and canonical board axes are diagnostic landmarks.

[Size front](comparison/size_front.png), [size right](comparison/size_right.png),
[size left](comparison/size_left.png), [size oblique](comparison/size_oblique.png),
[size treble](comparison/size_hand.png).
[Placement front](comparison/placement_front.png), [placement right](comparison/placement_right.png),
[placement left](comparison/placement_left.png), [placement oblique](comparison/placement_oblique.png),
[placement treble](comparison/placement_hand.png).
Coupled sheets are in comparison/coupled_*.png. Full 960×720 saved renders remain
in each root. Full-body cameras are identical across candidates. Treble close-up
centers follow C4 in the placement comparison; this is recorded and must not be
mistaken for a fixed-body camera. Montage inputs/output hashes are in the manifest.
All twelve chosen compact images reproduce byte-for-byte from saved qpos.

## Reproduction

```sh
uv run aec frozen cba-geometry experiments/036-instrument-size-fit/compact-upper.json --output artifacts/036-reproduce
uv run aec cba-render artifacts/036-reproduce/result.json --output artifacts/036-replay
uv run aec verify artifacts/036-reproduce --require-complete
```

Substitute any sibling candidate input for the other cases. To rebuild sheets:

```sh
uv run python -c 'from pathlib import Path; from accordion_ergonomics_core.cba_diagnostics import compare_fit_renders; p=Path("experiments/036-instrument-size-fit"); compare_fit_renders(p,p/"comparison")'
```

Tests independently assert size/target isolation, support-radius independence,
fixed-body frame invariance and exact historical 034 compiled/profile identity.
The seven frozen roots preserve executed package source and dependency hashes.
Transient missing-site construction errors were caught by tests before publication;
those runs produced no accepted records. All curated roots complete integrity
verification; this checks records, not scientific validity. See 037 for the
separately run right-hand regression after selecting the physical reference.
