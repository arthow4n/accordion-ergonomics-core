# One representative closed five-row CBA (generic_cba_v2)

This is a functional geometric hypothesis, not a commercial reconstruction or a
measured ergonomic instrument. The historical finite 62-button FR-1xb C-system
mapping is retained on an independently specified medium-sized case with 96 bass
buttons. No single manufacturer sells the exact combination represented here.
`rectangular_v0` remains the implicit selector for historical inputs and hashes;
new work selects `geometry.geometry_model = "generic_cba_v2"` explicitly.

## Public reference investigation (2026-10-09)

| Source | What it establishes | What it does not establish |
|---|---|---|
| [Roland FR-3xb specifications](https://www.roland.com/au/products/fr-3xb/) | Published 470 × 240 × 390 mm overall dimensions, 92 treble and 120 bass buttons | Component dimensions, mounting angle or lattice pitch |
| [Roland FR-3xb oblique photograph](https://static.roland.com/assets/images/products/gallery/fr-3xb_top_gal.jpg) | Five-row board around outer treble edge, distinct from grille; caps above board; end-face bass board, bellows between cases, upper strap hardware | Perspective is not metric calibration; open bellows are not closed width |
| [FR-3x/3xb official manual](https://cdn.roland.com/assets/media/pdf/FR-3x_OM.pdf), pp13,18–19,21 | Slanted six-row bass array; two bass and four chord rows; upper/lower shoulder holders, adjustable bass strap | No measured bass spacing, board cross-section or force equilibrium |
| [Hohner catalog](https://hohner.de/fileadmin/documents/instruments/accordions/hohner-accordion-catalog.pdf), Nova/specification sections | Nova III 96: 72 buttons in five rows, 96 basses, published 39.4 × 20.5 cm; two-size entry is not an unambiguous 3D bounding box | Closed case width, individual surface positions |
| [Hohner Nova III 96 bass/rear oblique](https://img.kytary.com/eshop_de/velky_v2/na/637680009322800000/caac4250/64908054/hohner-nova-iii-96-black-b-stepped.jpg) and [front/treble oblique](https://www.ikebe-gakki.com/Contents/ProductSubImages/0/112352_sub01_LL.jpg) | Same model from opposite sides: board cap protrusion; lateral bass playing face; rearward hand strap next to bass array; treble-board shoulder distinct from anterior grille | B-system photograph provides structure, not our C-system pitch mapping; neither photo provides mm measurements |
| [Pigini catalog](https://www.pigini.com/download/PIGINI_2022_CATALOGO_web.pdf), standard table | Primavera C175: five rows, 77 buttons, 96 basses, published 43 × 18.5 cm | No calibrated component section; not chosen as an exact template |
| [Pigini Polaris](https://www.pigini.com/wp-content/uploads/2022/04/POLARIS_new_closed.jpg) | Supplementary closed-case/bellows and slanted bass-board structure | This is a **piano** instrument, excluded as treble CBA evidence |
| [Weltmeister maker catalog (distributor-hosted)](https://www.lataudio.eu/Weltmeister_picss/Roll_over_images/Information/Weltmeister_Katalog.pdf), Romance 602/603 | Five-row compact CBAs, 60 treble/72 bass; catalog explicitly describes 4 mm stepped grip | Stepped construction is a real alternative, not proof of a flat universal CBA surface |

Official photographs/manual were inspected directly; Hohner perspectives were
compared visually. Downloaded reference assets and PDF rasterizations remain in
`artifacts/cba-references`, not redistributed as project evidence. Image URLs
identify exactly which views informed structure. Published sizes establish
plausible scale only: no averaging of catalog entries, uniform scaling, or
perspective-derived precision is used.

Additional end-on [FR-3xb](https://static.roland.com/assets/images/products/gallery/fr-3xb_angle_gal.jpg)
and closed [FR-1xb](https://static.roland.com/assets/images/products/gallery/fr-1xb_angle_closed_gal.jpg)
views resolve front versus rear: the board is carried by the **rear-adjacent
outer cheek**, with the grille/register area extending forward from its inner
edge. Treating an oblique view as a front-corner attachment was a rejected first
draft (see 032/rejected-front-attachment). A front-grille-mounted block is not
our representative conventional structure.

[Hohner construction patent DE3638517C1](https://patents.google.com/patent/DE3638517C1/en)
describes conventional rear-adjacent fingerboard placement separately from its
proposed forward relocation. [Hohner EP3435368A1](https://patents.google.com/patent/EP3435368A1/en)
also distinguishes changed forward keyboard placement from prior layouts.
These are primary structural distinctions, **not** evidence that their proposed
geometry or claimed ergonomic benefits apply to our generic CBA. They do not
supply our metric mounting angle or dimensions.

The selected interpretation is an outer board slanting rearward from an extended
case cheek. Product pictures support that relation but determine no mounting angle.
We choose a flat board with constant released cap height. Weltmeister's stepped
alternative is explicitly outside this one profile. Rim radii, grille holes,
registers, internal reeds and bellows fold mechanics are omitted. Angular and
metric calibration remain necessary for conclusions about actual instruments.

## Construction sections and the angle revision (034)

The owner challenged the local 55° angle, then explicitly requested evidence
beyond perspective product pictures. The short-lived 30° trial was also only a
hypothesis and was not published as validated geometry. The following primary
construction records now guide the cross-section:

| Source | Direct structural evidence | Limits |
|---|---|---|
| [Johann Pascher build notes](https://www.hyperbox.org/en/h/The_building_of_a_diatonic_Harmonika.htm) and [cut drawing](https://www.hyperbox.org/de/h/bilder/schnittsz.gif) | Drawn section shows the rear-adjacent board extending mostly outward with a gentle rearward slope; distinct cover, action, board, rear wall and closed cases. Author describes screwing keyboard to rear case edge from inside. | A handmade diatonic instrument using chromatic action, not a five-row CBA. The drawing labels overall sizes but does not specify a board angle or establish drafting accuracy. No exact angle is extracted. |
| Fadeev & Kuznetsov, *Repair of harmonicas, bayans and accordions*, 2nd ed., 1971: [p49 fig25](https://djvu.online/jpg/n/K/e/nKeZ6VMzQPck1/049.jpg), [p145 fig66](https://djvu.online/jpg/n/K/e/nKeZ6VMzQPck1/145.jpg), [p151 fig70](https://djvu.online/jpg/n/K/e/nKeZ6VMzQPck1/151.jpg), [catalog/text](https://ru.djvu.online/file/nKeZ6VMzQPck1) | Actual transverse sections of three-row bayans separate grille, case, fingerboard and button mechanism; stepped constructions have near-forward cap normals. Fig70 explicitly labels rear/front case walls and the board. | Historical three-row stepped bayan variants, not a measured modern flat five-row CBA; no angular or metric transfer. Scans stay local, not redistributed. |
| [Hohner DE3006581A1](https://patents.google.com/patent/DE3006581A1/en), description figs1–3 | Distinguishes flat and stepped grip plates and protruding caps. Its 15° refers to button axis versus lever normal. | That mechanical angle is **not** a measured board-to-case angle. Drawing assets could not be obtained from this record; text alone is used. |

These sections reject the steep-wing interpretation as the default for this
reference. We choose **20°** of rearward slope for the flat board. This is
engineering judgment supported qualitatively by a directly drawn shallow
section and contrasting near-forward bayan caps, not a measured 20° commercial
specification or an averaged universal angle. The same 12 mm panel, 4 mm released
caps and musical lattice remain. Independently choose H origin (78,100,−160) mm
for B so its inner back edge meets the case shoulder near H.u=0 and its outer
edge stays ahead of the rear case plane. Case return joins the *backing* edge,
not the panel underside; all resulting primitive seams are audited. No dimensions
or angle were tuned to obtain IK success. V1 is reproduced with its archived
source; current parsing explicitly rejects that retired selector rather than
silently assigning v2 geometry to it.

## Geometric specification (all following metrics are chosen assumptions)

Metres internally. H origin is the upper outer corner of the treble grille;
+u is toward the outer treble edge, +v down, +n anterior, normal to the grille.
H is independent of treble playing frame B. H-to-world includes the prescribed
instrument yaw/tilt. B retains canonical +u outer, +v down, +n released cap normal.

| Component | Extent / transform in H |
|---|---|
| Treble housing | Main u −150..0, v 0..380, n −200..0 mm; rear-adjacent shaped cheek extends u to approximately +83 mm; 6 mm walls |
| Fingerboard B | Origin (78,100,−160) mm, rotation +20° about H.v; 12 mm thick |
| Board surface | B.u −78..12, B.v −41..221 mm, B.n=0; 90 × 262 mm |
| Usable treble centers | Existing finite row/column IDs; 19 mm same-row pitch, 16.454 mm adjacent-row separation, existing staggers |
| Treble caps / targets | Radius 6.5 mm; cylinder base B.n=0, top/target B.n=4 mm; normal R_HB[:,2] |
| Treble board backing | B.u −78..12, B.v −100..280, B.n −18..−12 mm; full-height angled case wall |
| Board edge guards | 4 mm wide strips adjacent to usable panel, top B.n=2 mm, below released caps |
| Closed bellows | H.u −250..−150 mm, same 380 × 200 mm height/depth; four 12 mm envelope walls |
| Bass assembly A | Origin H=(−250,0,0) mm, identity rotation in closed reference |
| Bass housing | A.u −110..0, A.v 0..380, A.n −200..0 mm; six 6 mm walls |
| Bass board L | Origin A=(−116,45,−145) mm; L.x=A.n, L.y=A.v, L.z=−A.u |
| Bass panel | L.x −16..76, L.y −17..332 mm, L.z −8..0 mm; released surface 6 mm outside case |
| Bass caps | 96 cylinders, 4.5 mm radius, 3 mm height; no travel/force model |

`target_rNcM = T_WH T_HB (−(N−1) row_pitch,
(M−5+stagger[N−1]) column_pitch, cap_height)`.
Target normal is `R_WH R_HB (0,0,1)`. It never derives from the global case box.
The outer board edge extends sideways and toward the rear of the grille plane;
the inner edge meets a case shoulder roughly 145 mm behind the grille plane. “Offset” therefore is a vector and
orientation, not a guessed anterior-only lift. Cross-section diagnostics show
this explicitly, including the rear return and case backing enclosing the keyboard cheek.

Bass IDs are `bass_r1c1` through `bass_r6c16`. Zero-based row i, column j gives
L=(12i,18j+9i,3) mm. The constant shear makes slanted columns, not an alternating
rectangular dot grid. Six physical rows support the conventional two-bass/four-
chord structure; pitch, chord quality, fifth progression direction and reference
C button are deliberately **unassigned**. The manual establishes conventional
roles but this finite generic array has no verified musical mapping yet.

Shoulder-holder landmarks on the treble assembly are (−25,10,−150) and
(−25,370,−150) mm. They indicate upper/lower attachment stations; separate rings
and loaded strap paths are not modeled. Bass hand-strap stations are
A=(−110,15,−175), (−110,365,−175) mm. A visual strip 40 mm outward of the end
face and rearward of the button region illustrates the hand passage; it is not
a collision-valid leather strap, hand fit, force model or active left-hand task.

## Hierarchy, collisions and independent checks

`generic_cba_v2 → treble_assembly → keyboard → right caps/targets`;
`generic_cba_v2 → closed_bellows_connection`;
`generic_cba_v2 → bass_assembly → bass_fingerboard → bass caps/targets`.
Both case frames remain rigid. `BellowsConfiguration` names the closed interface
and rejects nonzero opening. Its independent `bass_relative` rigid transform
supports pure hypothetical frame tests, not physical opening studies. A future
bellows model can supply relative rotation/translation without redefining either
keyboard. No slider joint or deformation law is implied.

Collision walls, panels, backing, edge guards, caps and bellows envelope all retain
contype=2/conaffinity=1 (same anatomy compatibility as the old board). Bellows
fold ribs and hand-strap strip are visual-only and explicitly named. No global
filled envelope remains. Thin closed walls avoid inventing solid space between
the cases and exterior board; case interiors are hollow with no internal reed
model. Housing grille is a coarse solid exterior plane; holes are omitted since
this model studies hand-scale obstacles. Walls are not tissue contact supports.

The treble shoulder joins the grille edge; the rear return joins the rear wall,
angled backing and panel border. Thin top/bottom wing closures join those walls.
These deliberate seams overlap by up to approximately 8 mm under primitive
distance queries; they are structural junctions outside the button region.
The end closures use small convex prisms via MuJoCo's built-in mesh interface,
not external CAD or a filled global volume. Bass panel backs enter the end wall
by 2 mm. Other unrelated components meet or separate;
`cba-geometry` independently queries every component pair and records overlaps.
Cap bases touch their panels. Caps do not intersect neighboring caps; target
sites and compiled normals are checked numerically for every button.

Historical geometry serialization omits the new default selector so old profile
commitments and compiled worlds stay exact. New profiles record the selector and
complete generic specification, while MJB guards cover actual compiled geometry.
Old qpos may be an explicitly labeled numerical seed; it is never accepted as a
pose in the new world without a new solve and audit. Replay rejects changed worlds.

## Mounted reference and remaining uncertainty

The prescribed seated MyoFullBody reduction is unchanged: original right-arm
coordinates, couplings and anatomical proxies; passive torso/left arm/legs remain
fixed. Shoulder anchors are extracted from the unchanged native right attachment.
Case rear and bottom extrema, including the board shoulder, replace the old
rectangular-shell origin rule. The board rim is shoulder-relative; lowest case
edge clears the approximate MyoSim femur-centered support envelope by 10 mm.
Rear component extrema clear the conservative imported thorax support plane by
10 mm. `SeatedSetup` angles specify the **playing board B**, preserving the
canonical frame contract: `R_H = R_B R_HB^T`. At reference B yaw −30°, the
housing yaw is −10°, not −30°. The first mounted 032/033 implementation mistakenly
applied −30° to H, then composed its 55° board tilt, yielding an almost lateral
85° button normal. Those frozen records retain that mistake for reproduction;
[034](../../experiments/034-cba-mounted-orientation/notes.md) corrects it and
rerenders the saved state. Actual component distances are queried too.
The old instrument width/depth/height/C4 insets are ignored by this version;
profile records preserve them as legacy setup inputs, not generic metric evidence.

These planes can put the case visibly forward of the rib meshes; the meshes
are bones, whereas imported proxies and thigh capsules are approximate support
envelopes. The reference is a supported clearance hypothesis, not fitted worn
placement or load equilibrium. Shoulder straps have landmarks only; no chair,
pressure, forces, or measured garment thickness. The left arm remains the native
prescribed generic pose, visibly below/behind the bass board; it is not positioned
to create artificial playing contact. Future left-hand studies need their own
anatomical activation, marker, collision and wearing-position validation.

## Reproduce

```sh
uv run aec frozen cba-geometry experiments/034-cba-mounted-orientation/experiment.json --output artifacts/034
uv run aec cba-render artifacts/034/result.json --output artifacts/034-replay
uv run aec verify artifacts/034 --require-complete
```

Six instrument views, a metric treble section and five mounted views accompany
the saved numerical state. The section is a coordinate-derived engineering
illustration; `instrument_top_section.png` separately renders actual MuJoCo
geometry. The geometry reference is a neutral prescribed arm state, not a playing
pose. Experiment 033 is a superseded v1 search record, not a v2 validation.
[035](../../experiments/035-cba-v2-regression/notes.md) supplies the current
small multistart comparison, ordinary transitions, unsuccessful held-contact
search and independent all-solid collision audit. Unchecked anatomical overlap
still precludes human-feasibility claims.
