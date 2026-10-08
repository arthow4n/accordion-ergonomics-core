# Frames and measurements

Use metres, radians and seconds internally. Joint qpos values in this prototype
are all hinge angles; never assume that for a future free-joint model.

## Canonical frames

World W is right handed: +x player's right, +y forward away from the torso,
+z upward. The upstream scaffold has right shoulder at negative x and anterior
at negative y; rotate its fixed root 180° around z. Preserve its 1m root height
as imported model placement, not a measured seated player. Tests assert the
actual anatomical right shoulder is now positive x.

Board B is right handed: +u toward the outer edge, +v downward toward higher
pitch, +n out of the playing surface. Increasing row index goes **inward**
(-u), toward the bellows; increasing logical column goes downward (+v).
`R_WB = [[1,0,0],[0,0,1],[0,-1,0]]`. Its determinant is +1, and
`p_W = origin_W + R_WB p_B`. The board normal is world +y; pressing normal is -y.
Front diagnostic view sees world +x on its left, matching the manual diagram.
The fixture has no measured tilt. Rigid button top is n=height; board top is n=0.

The origin is the base plane under row1/col5 C4. Logical column 5 also maps to
row4 C4; those centers are offset by half a same-row spacing down the board.
The first *physical* button varies by row; never renumber away missing edges.
Source app “horizontal” coordinates are not world horizontal distances.

Frame markers are red +u, green +v, blue +n. Camera azimuth in MuJoCo describes
look direction, so -90° is the keyboard-facing camera from world +y. Camera
parameters are written to result.json. The failed initial camera is retained
as evidence, not used as a standard view.

## Minimum calibration before real ergonomic inference

| Measure | How to record | Why it matters |
|---|---|---|
| Center coordinates | Flat photo perpendicular to board with ruler in the same plane, identify every pitch/row/button; retain raw photo and calibration | Confirms staggering, finite edge locations and whether a regular lattice is adequate |
| Same-row and adjacent-row separations | Calipers across several centers, report repeated readings, tool precision, center-estimation uncertainty | Affects finger reach and skin clearance; one spacing is insufficient if board is curved |
| Button diameter/cap profile/protrusion | Several buttons with calipers and side photograph; distinguish released/depressed state | Determines surface contact and neighbor collision |
| Travel | Measure released/fully depressed relative to fixed board surface, preferably a side video with scale | Separates touching from operating a button |
| Plane orientation/curvature | Side/top orthographic references, straightedge or point measurements; avoid perspective estimates | Required before treating world pose as real instrument pose |
| Board pose relative to body | Record reproducible posture, straps/chair setup, shoulder and torso landmarks, and identified board origin in same 3D frame | Changes shoulder/elbow reach even with identical pitches |
| Player scale | Upper arm/forearm/hand/finger lengths and repeatable joint-range observations | Imported generic anatomy may not match the player |

Absolute instrument shell dimensions, forces, tempo and fatigue need not block
the first *kinematic fixture* test. Body/shell collision becomes necessary
before strong real-world feasibility claims. Unknown measurements remain
unknown; fixture values carry assumption provenance. Do not estimate scale
from a perspective manufacturer's photograph without uncertainty and checks.

## Next evidence acquisition, prioritized by experiments 008–014

The kinematic laboratory is operational. Physical setup changes discovered
movement, and imported hand proxies do not enforce general self-collision.
Complete the following calibration record before trusting human action or
exercise recommendations.

1. **Hand envelopes and pose references.** With consent, record right-hand dorsal,
   palmar and side views with a scale in the local measurement plane. Identify
   fingertips, approximate joint landmarks and segment widths as well as lengths;
   retain repeated readings and uncertainty. Photograph relaxed fingers and a
   few comfortable known single- and two-button contacts from keyboard-facing
   and side views. Include buttons and scale so contact/palm orientation can be
   reconstructed. The target is checking proxy coverage, not diagnosing mobility.
   Do not force the model's unusual poses or personally test a demanding solver
   exercise merely to confirm it.
2. **Board metric coordinates.** Record every physical button ID against the
   finite row/column diagram. A perpendicular scaled photograph checks staggering;
   center-to-center readings across several consecutive centers reduce
   center-estimation noise. Divide a multi-gap reading by its number of gaps,
   preserve the raw length, and repeat in each row. Measure neighboring-row
   displacement in both board axes rather than a single diagonal distance.
   Check regular-lattice residuals before fitting one spacing to all 62 centers.
3. **One reproducible setup.** Record board origin and normal in the same frame
   as torso/right shoulder, with chair, straps, instrument orientation and
   representative upper-arm/forearm lengths. Document landmark conventions and
   repeated repositioning error. Experiment 008 changes discovered movement
   substantially at ±15 mm placement, so board-only measurement is insufficient.
   Shoulder skin landmarks are not automatically anatomical joint centers.
4. **Button operation, separately from surface contact.** Record released cap
   diameter/profile/protrusion and fully depressed cap position relative to a
   fixed board reference in a side view with scale. Repeat multiple buttons and
   trials, preserving raw video/readings. Report travel as unknown if depression
   is not observable. Force needs a suitable calibrated instrument and a defined
   measurement method; it cannot be inferred from travel or IK. Travel and force
   remain unknown until this evidence exists.

Store raw observations, instrument/player/setup identifiers, date, tools,
coordinate frame, uncertainty and source category alongside derived values.
Use new profiles for measured FR-1XB and measured players; leave the synthetic
reference unchanged. Individual segment scaling is not implemented and must
be validated before importing readings as anatomical transforms. Joint-range
overrides can be recorded independently, with their own evidence.

Calibration acceptance should reproduce observed contacts, compare predicted
marker positions and palm orientation to observations, and distinguish
intentional same-envelope overlaps from forbidden cross-finger penetration.
Preserve model failures. Then rerun the same atlas, geometry/player sweeps and
held-task records under measured profiles. State whether conclusions persist;
matching one pose does not validate the entire reachable action space.
