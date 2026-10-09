# Accordion size and the fixed seated reference (036–037)

**Decision C: retain the 380 mm compact generic case, replace automatic thigh-height
mounting with an explicit upper-region anchor for new research.** The old mounting
algorithm does make near-thigh geometry by construction. That is not evidence that
the old pose was impossible, nor that compact accordions must touch a thigh.
The new reference is geometrically plausible and above the lap; its physical
support by straps has not been demonstrated. See [036](../../experiments/036-instrument-size-fit/notes.md)
for numerical records and [037](../../experiments/037-upper-anchor-regression/notes.md)
for subsequent right-hand regression.

## Public evidence, checked 2026-10-09

| Source | What it establishes | What it does not establish |
|---|---|---|
| [Roland FR-1x brochure](https://cdn.roland.com/assets/media/pdf/fr-1x_brochure.pdf), specifications; [Japanese manufacturer page](https://www.roland.com/jp/products/fr-1xb/) | Button model: H 380, W 365, D 195 mm; compact size and supplied straps | Internal case dimensions, board mounting, player fit |
| [Roland FR-3x manual](https://static.roland.com/assets/media/pdf/FR-3x_OM.pdf), specification p67 | Button model H 390, W 470, D 240 mm; piano model H 430, W 481, D 270 mm | A 430 mm button instrument: that would confuse the two variants |
| [Hohner 2021 catalogue](https://hohner.de/fileadmin/cat/2021/catalogs/AkkordeonCatalog2021/pdf/complete.pdf), Nova III 96 and chromatic specification table | Five-row 72-button model, size pair 39.4 × 20.5 cm, described for smaller players | Closed total width or a calibrated wearing position; do not read two dimensions as three |
| [Pigini 2022 catalogue](https://www.pigini.com/download/PIGINI_2022_CATALOGO_web.pdf), printed pp32–33, 40–41, 46–47 (PDF sheets 19, 22, 26) | Star Jazz 3: five rows, 42 × 22 cm. Primavera C175: five rows, 43 × 18.5 cm. Super Variété: five rows, 43 × 22 cm. Broader professional cases also exist | Table headings say sizes, not explicitly H/W/D. Interpreting the first dimension as case length/height is construction/catalogue convention, with uncertainty; no total-width specification follows |
| [Gorka Hermosa, Accordion Technique Notebook](https://www.gorkahermosa.com/web/img/publicaciones/3568a.pdf), pp3–4 | Upright relaxed seated posture; chest-adjacent bellows; right lower keyboard corner braced near inner thigh/groin; bellows kept off left thigh; player-dependent straps, right slightly looser | A universal case-to-shoulder offset, rigid support plane, mandatory lap weight bearing for every size |
| [SF Accordion Club March 2018](https://www.sfaccordionclub.com/newsletter/Mar_2018_NL_OL.pdf), “Posture to play” | Piano-accordion instruction supports bellows on left leg and braces keyboard inside right thigh; recommends shoulders carry no weight | Universality across chromatic instruments, body sizes and teaching schools |
| [Petosa, The Great Accordion Myth](https://petosa.com/blogs/accordion-culture/the-great-accordion-myth-uncovered-by-joe-petosa), 2016 | For 41-key instruments, keyboard starts below collarbone and ends near inner right thigh; warns short cases can increase strap burden; fit depends on player | Universal chromatic geometry, measured 60/40 load fractions or proof that any floating pose is stable |
| [SF Accordion Club December 2021](https://www.sfaccordionclub.com/newsletter/Dec_2021_NL_OL.pdf), “Accordion Tips: A Good Fit Helps to Prevent Shoulder Tension and Pain” | Pamela Tom reproduces Petosa advice; Jesse Mea recommends lap support regardless of size, with player/chair-dependent adjustments | Its stated weight percentages are instructional opinion, not measured load calibration, and are not model constants |

The Petosa and Jesse Mea references actively favor lap support; they are
not evidence endorsing our higher compact hypothesis. That hypothesis remains
a limited geometric configuration requiring support validation, not a clinical
or pedagogical recommendation. The different left-thigh recommendations are real differences in instruction,
not something to average into a rigid universal plane. Hermosa's seated front
and side photographs were inspected: they illustrate chest proximity and inner
thigh bracing. They are uncalibrated illustrations, not measurements of torso
length, tilt or strap stations. Pigini product photographs were inspected for
axis/structural context, not used for metric reconstruction. Existing construction
sections in [034](../../experiments/034-cba-mounted-orientation/notes.md) remain the
basis of the unchanged 20-degree treble attachment.

The 430 mm experimental case is thus a defensible generic taller hypothesis,
not a Pigini reconstruction. Keep depth 200 mm, treble/bellows/bass widths
150/100/110 mm and the 62/96-button fixtures. Published products vary depth and
width independently; there is no evidence that height requires uniform scaling.
A taller enclosure can house this same keyboard. Board span, pitch, cap size,
B-in-H origin and both finite layouts remain unchanged. Only full-height walls,
backing, bellows envelope and lower strap stations extend. The practical default
remains the compact case, so no unrelated product-profile collection is introduced.

## Audit of old mounting

`physical_cba.derive_physical_setup` in v2 calculates all housing/board/backing
extrema. In canonical torso coordinates it sets
`H.z = max(hip/knee station z) + thigh_radius + support_clearance - min(component z)`.
At the reference radius 75 mm and clearance 10 mm, the lowest point is necessarily
10 mm above this conservative plane. This plane uses the highest station across
both legs; it is not the closest distance to a curved thigh. Its result cannot
independently validate support or sizing. The prior rectangular algorithm in
`seated_setup.derive_setup` makes the analogous box-bottom constraint.

Other decisions are independent: lateral position aligns the outer board rim
with the neutral imported right shoulder, plus an explicit lateral offset.
Anterior position comes from the maximum directional support of three thorax
proxies, plus 10 mm, against the rear instrument extrema. Yaw and both tilts are
prescribed for B; H removes the local 20-degree board rotation. Instrument height
comes from `GenericCBA`, not the older `SeatedSetup.instrument_height_m`; the old
width/depth/C4 inset fields also do not control physical v2. No second independent
vertical shoulder constraint existed. The concern is a hidden lower support
assumption, rather than two conflicting vertical pins.

`lower_body` supplies compiled MyoSim hip/knee stations. Native full-body posture
is separately prescribed and fixed. In these records both definitions agree at
90-degree hip/knee and 5-degree hip abduction. Imported hip-to-knee station length
is about 402 mm; the slight knee/hip vertical difference is retained, not corrected
by moving the case. Shoulder-to-pelvis vertical reference is 474.2 mm. It is an
internal anatomical reference length, not a measured human sitting height.

## New independent anchor and scope

For `generic_cba_v3`, require explicit `case_height_m` (380 or 430 mm in this small
study) and `seated.upper_case_to_shoulder_m`. Set the upper grille corner H.z
relative to the neutral compiled right shoulder in the fixed torso frame. The
selected offset is −40 mm; −80 and 0 mm bracket it as research uncertainty,
not measured population bounds. This places the upper treble region near the
shoulder/chest without consulting thigh height or optimizing a hand solve.
Keep the same lateral rim, torso gap, B yaw −30 degrees and zero tilt. The
representative choice sits midway between the two explicit alternatives and
retains room around the pelvis; it is not claimed uniquely correct.

Changing thigh radius cannot move the new instrument. Changing case height
cannot move any button target. Tests assert these properties, rigid-root
invariance, unchanged fixed anatomical landmarks, 38 active right coordinates
and 11 couplings. The scapular/clavicular/glenohumeral mechanics remain active.
Torso/legs/left arm, treble/bass and closed bellows remain stationary during every
exercise. Frame hierarchy is retained; there is no instrument/strap/bellows dynamics.
The internal root body name `generic_cba_v2` remains a stable hierarchy name;
the serialized selector/specification identifies v3. Exact compiled hashes and
profile guards reject historical accepted states in revised worlds.

## Fit interpretation

At the selected upper anchor, increasing height 380→430 mm lowers the case by
exactly 50 mm while leaving the upper case, board and human unchanged. Approximate
thigh distances decrease from 53.34/52.78 to 3.35/2.78 mm (right/left). The taller
case is near the thigh, not demonstrated supported by it. A 40 mm downward
placement change with that tall case intersects the envelopes by about 37 mm,
including passive imported femur proxies. Preserve this rejected hypothesis.
The compact low hypothesis remains near-thigh at 13.35/12.78 mm; the higher compact
hypothesis clears by about 93 mm. Absence of contact alone does not reject either.

The selected upper treble midpoint is (−80.79,+225.68,−40.00) mm relative to the
neutral shoulder; C4 is (−12.39,+156.51,−140.00) mm. The lower treble midpoint is
(+34.21,−0.21,+64.92) mm from the approximate inner-thigh reference. These landmarks
make the gap explicit; they do not define skin contact. Compact/tall case-height
ratios to shoulder–pelvis vertical length are 0.801/0.907.

Selected neutral closest thorax proxy clearance is 10.842 mm; pelvis right/left
20.215/41.007 mm. Bone convex collision representation minimum is 19.571 mm,
which is not a skin clearance. The saved side views show the rear case forward
of rib bones, consistent with the conservative thorax envelope. Bone meshes,
imported collision proxies and synthetic support capsules remain distinct.
These checks do not validate their shapes, compressibility, strap tension,
pressure, equilibrium, comfort or instrument stability. The taller near-thigh
margins are smaller than plausible uncalibrated envelope changes; 030's 15 mm
radius hypothesis alone exceeds them. No tissue is shrunk to obtain a solve.

Select the compact upper hypothesis for a reproducible stationary reference,
not because of a preferred C4 result. Keep taller cases and lower wearing
positions as controlled evidence. Subsequent action discovery must preserve
known solver-branch sensitivity and independent finger overlap audits.
