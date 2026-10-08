# Generic seated CBA setup, not personal calibration

The reference profile is `reference_seated_cba_setup`. It derives placement from
compiled MyoArm torso geometry, an FR-1xb-sized instrument envelope, a
shoulder-relative treble edge and a pelvis-relative seated support plane.
It replaces a floating board for new setup studies; experiments 001–022 retain
their historical worlds. Neither this setup nor the imported anatomy is measured
on an individual. The family below matters more than its nominal member.

## Public evidence inspected on 2026-10-08

| Source | Category and supported relationship | Limits |
|---|---|---|
| [Roland FR-1xb specifications and gallery](https://www.roland.com/uk/products/fr-1xb/) | Manufacturer: 365 mm width, 195 mm depth, 380 mm height; 62 treble buttons. [Official oblique image](https://static.roland.com/assets/images/products/main/fr-1xb-bk_top_open_main.jpg) shows treble board at the right end, beside grille/bellows, with a shaped case. | Overall dimensions do not locate C4 or define the treble surface, shell shape, or open bellows width. No metric reconstruction from the perspective image. |
| [Roland brochure](https://cdn.roland.com/assets/media/pdf/fr-1x_brochure.pdf), PDF page 2 | Manufacturer visual example: compact instrument held near chest and lap, treble axis broadly upright with visible tilt; right forearm approaches from the side. | Seated child and **piano FR-1x**, not adult FR-1xb calibration. Illustrates placement/proportion variability only. |
| [Gorka Hermosa, Accordion Technique Notebook](https://www.gorkahermosa.com/web/img/publicaciones/3568a.pdf), printed pp. 3–4 | Author's pedagogy and front/side photographs of button accordion: relaxed shoulders, chest relationship, lower right keyboard corner near inner thigh/groin, adjusted straps, forearm/hand continuity. | Larger concert instrument; instructional target, not universal anatomy. Specifically keeps bellows off left thigh to avoid friction. |
| [San Francisco Accordion Club, March 2018](https://www.sfaccordionclub.com/newsletter/Mar_2018_NL_OL.pdf), printed p. 5 | Club pedagogy: left-leg support, inner-right-thigh brace, low shoulder and lifted elbow/flat wrist. | Piano advice; conflicts with Hermosa about bellows resting on left leg. Does not establish strap load fractions. |
| Same newsletter, printed p. 3, February 18 public performance report/photos | Public examples: seated instruments near torso/lap, different inclinations/heights and arm approaches, including button instruments; standing examples are visibly different. | Mixed players/instruments and oblique small images; no angle, distance or population statistics extracted. |
| [Accordions Worldwide, placement article](https://www.accordions.com/index/art/correctly.shtml) | Pedagogical counterexample: advises against putting the bottom keyboard section inside the right leg. | Piano context. Confirms disagreement about engagement; not grounds to prohibit all near-thigh stabilization. |

Roland also links [Tatiana Semichastnaya's performance](https://www.youtube.com/watch?v=OhjnHnF3drQ).
The video could not be retrieved in this session; no frame-specific inference is
claimed. Public PDF illustrations/photos and official product imagery above were
actually viewed. Reference media are temporary files in `artifacts/`, not
redistributed research assets. No private photos or measurements were requested.

## Implemented physical abstraction

Canonical player axes are right/forward/up; B remains outward/down/surface normal.
Orientation is `R_player * Rz(yaw) * Ry(long_axis_tilt) * Rx(fore_aft_tilt) * R_B`.
This names operations explicitly; it does not prescribe a universal angle.

The instrument's local axes are u/v/n and its dimensions W/H/D. C4 lies on its
front plane, `outer_edge_inset` inward from the right edge and `c4_top_inset`
below its top. The board's right-edge x coordinate follows the imported neutral
right shoulder plus a setup offset. The shell rear plane stays outside the
outer support of **all three** compiled thorax collision primitives, plus a gap.
Its lowest point follows the assumed thigh-top height above the pelvis/root,
plus clearance. These relationships determine the translation; torso rigid
transforms move the entire setup. Instrument dimension changes recalculate it.

The whole instrument is a **coarse solid box hypothesis**, not a measured
collision shell. It includes the bass/bellows region at catalogue scale without
bellows motion. A shaped real treble case may leave space this box blocks.
The box is an explicit collision envelope: independent distances to every
anatomical proxy are recorded, including fixed torso shapes that engine weld
filtering omits. Do not reduce this envelope to obtain IK success.

Schematic thighs are visual references, not anatomical collision envelopes.
Right inner-thigh reference is 70 mm medial to the neutral shoulder; visual
thigh centers are ±160 mm from root, radius 75 mm, length 320 mm. These are
unmeasured illustration assumptions. A lower treble landmark uses the inner
board edge and middle of instrument depth. Its separation from the reference
is reported; it is **not** a rigid point contact. The left thigh illustrates the
support system; strap forces, pressure, weight sharing and equilibrium are not
solved. Straps are not new independent parameters because they would have no
implemented mechanical effect. The existing torso quaternion places the entire scaffold and support frame; it
does not independently simulate seated torso inclination with stationary thighs.
That extra anatomical degree of freedom is not implemented.

## Parameter family

All ranges except catalogue dimensions are **assumed exploration intervals**,
guided qualitatively by the sources above. None is a measured population bound,
confidence interval or exact recommendation. Numeric uncertainty is unknown;
uncertainty is deliberately broad. They are persisted in profile parameter
provenance and must accompany any future alteration. Combined extremes are not
certified plausible: inspect derived anchors and views before interpreting them.

| Parameter | Nominal | Exploration range | Evidence/rationale |
|---|---:|---:|---|
| Overall W/D/H | 365/195/380 mm | Fixed for this instrument | Roland manufacturer values; tolerance unspecified. Vary only with another identified instrument hypothesis. |
| Rear thorax-plane gap | 10 mm | 0–40 mm | Assumption of close torso relationship, Hermosa qualitative guidance; not skin compression. A support plane can overestimate actual gap. |
| Treble edge relative to right shoulder, x | 0 mm | −30 to +30 mm | Assumption guided by right-side board imagery; imported joint center is not a skin landmark. |
| Thigh-top above pelvis/root | 100 mm | 70–130 mm | Unmeasured seated anatomical support reference; controls board height with fixed instrument height. |
| Shell above thigh-top | 10 mm | 0–40 mm | Assumed near-thigh through weaker engagement/strap support, reflecting competing pedagogies. No force fractions. |
| C4 inset below shell top | 60 mm | 45–95 mm | Assumed mount registration; official image supports inset, not exact metric value. Button lattice remains synthetic. |
| C4 inward from outer case edge | 15 mm | 10–25 mm | Assumed edge margin; not a manufacturer measurement. |
| Yaw | −30° | −45° to 0° | Assumed moderate outward-facing right treble normal; no precise angle inferred from photos. |
| Long-axis side tilt | 0° | −10° to +10° | Assumed broadly upright variation, public visual examples. |
| Fore/aft tilt | 0° | −10° to +10° | Assumed modest inclination; torso-plane anchor recalculates, no photo reconstruction. |

The root z=650 mm nominal only makes a readable seated world; it translates
both anatomy and instrument and is not a player measurement. Keep three levels
separate: reference player/setup, generic variation, optional personalized
calibration later. This phase establishes neither individual ergonomic advice
nor calibrated tissue envelopes, button operation, forces, fatigue or tempo.

## Recalculation, rendering and comparisons

In schema 2, `setup.torso.seated` contains the physical parameters. Omit
`setup.board` for new derived inputs. If expansion includes a cached board pose,
it is ignored and recalculated from the anchors. Resolved profiles record the
parameters, provenance, derived anchors and board transform. Parameter hashes,
compiled model hashes and state guards prevent silently reusing another world.
Legacy profiles omit the new field and retain their previous hashes.

Four standard images retain CLI names: `keyboard` is front, `side` right side,
`overview` oblique, `hand` close treble/arm. Colored landmarks identify shoulder,
elbow, wrist, thigh reference and lower treble reference; board axes are red u,
green v, blue n. Transparent shell/thighs expose their schematic nature.
Render saved states with `uv run aec render RESULT --output DIRECTORY`.

Start with [023](../../experiments/023-reference-seated-setup/notes.md).
A solver acceptance is a static numerical contact, not observed playing posture;
pose diversity and collision coverage must be checked independently. Compare
shoulder-relative metrics rather than absolute heights across world translations.

## What the family experiments establish

[024](../../experiments/024-seated-setup-family/notes.md) samples eight seated
members plus a matched-policy synthetic control. All discover D4/G6 transitions;
G6 best discovered palm relocation spans 109–214 mm seated versus 320 mm synthetic.
These are sampled realizations, not lower bounds. [027](../../experiments/027-yaw-search-refinement/notes.md)
recovers a missing yaw-case C5 and reduces nearby D4 from 213 to 19 mm without
geometry changes: search/branch controls are essential before physical inference.

[025](../../experiments/025-seated-pose-diversity/notes.md) separates accepted
own-world C4 initialization from transferred numeric priors. Seated central and
nearby candidates generally have less wrist flexion than the own-anchor synthetic
candidates, but two-finger near-limit branches remain. [026](../../experiments/026-seated-held-contact/notes.md)
finds held paths with explicit contact auditing and preserves an initialization-
dependent failure. A successful seated path is longer than a successful synthetic
branch; the correction is not a universal movement reduction.

[028](../../experiments/028-seated-collision-coverage/notes.md) finds unchecked
phalangeal overlaps in all 73 audited poses. Gross body/instrument placement is
substantially more plausible; full anatomical playing validity remains unresolved.
Useful current claims concern explicit setup hypotheses and numerical sensitivity,
not human reachability, fatigue, force or individualized recommendations.

## Anatomical lower-body revision (029)

Use [fixed MyoSim pelvis/legs](seated-lower-body.md) for new generic setups. The
023–028 family remains historical evidence on schematic thighs; those numbers
are not silently relabeled as anatomical seated results. The new profile derives
the support plane and independent brace landmark from posed femurs, replacing
both the arbitrary pelvis-relative height and instrument-dependent thigh y.
