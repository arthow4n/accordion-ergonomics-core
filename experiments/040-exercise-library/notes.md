# Varied right-hand targets in the fixed 037 reference

The substantial library study keeps 037's compact `generic_cba_v3`, 380 mm case,
upper anchor −40 mm relative to the neutral shoulder, fixed seated body, stationary
closed bellows, fixed bass/treble cases and prescribed nonplaying left arm.
Original right shoulder/arm/wrist/finger coordinates and couplings remain active.
Only index/middle contact solving is supported. No geometry, joint ranges,
collision masks or proxy sizes were adjusted to manufacture realizations.

## Deliberately varied contact discoveries

`contact-search/` is the authoritative complete frozen run: eight deterministic
starts per target, baseline 037 central contact plus its seven recorded offsets,
220 iterations/start, displacement collision adapter, integration-edge checks,
and the existing 16 index/middle pair hypotheses. Its `render:false` request
suppresses costly candidate renders while retaining all candidate states,
descriptors, attempts, solver histories and provenance. The focused regression
checks that numerical evidence is still published without invoking rendering.

| Physical contact | Musical pitches (MIDI) | Distinct candidates |
|---|---|---:|
| index r1c4 | A3 (57), lower same-row control | 4 |
| index r1c6 | E♭4 (63), upper same-row control | 4 |
| index r1c8 | A4 (69), larger same-row move | 4 |
| index r3c4 | B3 (59), cross-row lower move | 4 |
| index r3c7 | A♭4 (68), cross-row upper move | 4 |
| index r4c5 | C4 (60), alternative physical C4 | 4 |
| index r5c5 | C♯4 (61), alternative physical C♯4 | 5 |
| index r2c8 | B♭4 (70), diagonal relocation | 4 |
| index r1c5 + middle r3c5 | C4+D4 (60+62) | 4 |
| index r1c5 + middle r1c6 | C4+E♭4 (60+63) | 5 |
| index r1c5 + middle r3c6 | C4+F4 (60+65) | 4 |
| index r1c5 + middle r2c7 | C4+G4 (60+67) | 4 |

All 12 requests produce candidates: 96 starts give 60 solver acceptances and 50
distinct branches after deduplication. Two starts per request fail initial
collision checks and one has invalid initialization; the other five are accepted,
with duplicates preserved separately from failure. These failures do not show
physical impossibility. Branches share musical/physical intent, not exercise IDs.
The finite mapping comes from `instrument.buttons()`, not MIDI interval ranking.

The single-index compiled digest is `19af32fd2ec491ec8f7a4ac7a284fcb7f1d0db67d2c806ebf6ac4583859b897d`;
index+middle contact composition uses `de73c1112cb131711f016fef003f1f8c5caadacf7b7f377079d4a8f04ff49bfc`.
Contact marker composition changes compiled bytes; no pose is silently accepted
across those worlds. The physical geometry/anatomy/setup identities remain 037.

## Sampled movement and explicit holds

Five independent frozen plans release central index C4 and establish the named
destination. Each uses 0.002 rad sample spacing, four withdrawal depths
10/20/40/80 mm, 220 waypoint iterations and 500 RRT iterations with seed 3309.
All find incremental withdrawal/RRT/approach paths. Source/destination states are
hashed, and all recorded states remain available.

| Path root | Destination | Samples | Discovered palm arc length (mm) |
|---|---|---:|---:|
| plan-lower | A3 r1c4 | 237 | 56.331 |
| plan-upper | E♭4 r1c6 | 272 | 69.281 |
| plan-distant | A4 r1c8 | 308 | 91.900 |
| plan-cross | B3 r3c4 | 251 | 51.747 |
| plan-equivalent | C4 r4c5 | 251 | 52.293 |

`held-reverse/` holds index r1c5 C4 while middle E4 r2c6→C♯4 r2c5.
Direct interpolation is rejected; 22 waypoint solves produce 517 samples, palm
arc 42.204 mm, maximum held marker residual 86.997 µm.
`held-wide/` holds the same index while middle C♯4 r2c5→G4 r2c7.
Direct interpolation is rejected; 32 waypoint solves produce 622 samples, palm
arc 88.160 mm, maximum held marker residual 81.478 µm. Both retain direct failures,
searched samples and resulting gesture commitments. Held policy preserves only
the explicitly named index contact, not every incidental finger/button relation.

`sequence-compositions.json` defines return C4→A3→C4, alternation
A3→C4→E♭4→C4→A3 and cross-row return C4→B3→C4. These reuse ordered sampled
segments, reversing samples where specified. Exact qpos boundary equality and
compiled identity are checked; there are no hidden posture jumps. Their sampled
palm arcs 112.661/251.223/103.495 mm are sums of actual segment arcs. A reverse
sample path is a kinematic composition, with no timing, forces or dynamics claim.
The frozen `sequences/` workflow regenerates this reusable composition evidence.

Palm arc length sums Euclidean differences of recorded `capitate_r` positions;
joint margins/excursions describe imported coordinates. Solver iteration history
is not a movement trajectory. These are discovered realizations, not proven
minimum necessary movement, lower bounds or universal difficulty measurements.

## Independent audits and unresolved anatomy

`endpoint-coverage/` runs canonical collision-coverage on every authoritative
candidate. `endpoint-hand-audit/` applies versioned native hand reporting to all 50
endpoints. `movement-audit/` audits every recorded sample of five plans and the
reverse hold; `held-wide-audit/` audits all 622 wide-hold samples. All-solid path
audits query every instrument solid against all 36 moving anatomical proxies;
hand audits query 276 hand pairs independently of engine masks. Policy attribution
and minimum-distance sample indices are explicit in each report.

Canonical endpoint coverage retains 11–22 unchecked cross-digit overlaps; minimum
case/rim, panel and cap clearances are 0.244 mm, 4.010 mm and 9.953 µm.
Every endpoint and movement satisfies the configured index/middle separation
hypotheses; all seven movements also satisfy the independent instrument-proxy
penetration tolerance. This does not complete anatomical validity. Endpoint hand
reports retain 25–36 unresolved intersections including same-digit articulation
and palm composition; maximum cross-digit phalangeal depth 13.513 mm. Ordinary
paths retain worst unresolved cross-digit phalangeal depths 8.68–9.00 mm.
Reverse hold retains 2.744 mm. Wide hold retains 12.636 mm between unchanged middle
and ring `midph3_coll_r`/`midph4_coll_r` at sample 558. The suspicious wide result
is deliberately retained as an anatomically unresolved coordination hypothesis.
The report does not assert that every proxy intersection is real tissue overlap.

Inspect the native-hand policy investigation in 038 for source distinctions and
classification limits. Configured separation satisfaction, independently audited
instrument clearance and unresolved hand anatomy are separate claims. Human
feasibility remains null for every result. Button depression, continuous validity,
strap support, calibrated skin, effort, fatigue and human difficulty are unproved.

## Interruption, curated images and replay

The first render-heavy batch exited 247 during its fifth target while simultaneous
full test/render jobs were running. The cause is not proven. The root
`interrupted-run.json` and assembled `result.json` disclose interruption and only
four completed targets. Original frozen archive, definition, completed discovery
records and the four exact candidate 0 files used by plans are retained unchanged;
other candidate states remain inside discovery records. Missing results are not
solver failures. The subsequent full 96-start no-render run is authoritative.

All four overview/keyboard/side/hand diagnostics were inspected for the lower
contact, lower-path midpoint, reverse-held last state and both suspicious held
worst states; collision overlays were inspected for the two held audits. Cases and
body stay fixed. Bone visuals do not override numerical proxy overlap reports.
Only selected renders are curated; omitted render paths in original camera
metadata refer to transient images, while all numerical records remain intact.
`replay-check.json` records four byte-identical lower-contact images reproduced
from saved qpos with the original frozen source and same software EGL environment.
Pixel equality is environment-specific and is not scientific validation.

## Reproduction

```sh
uv run aec frozen explore experiments/040-exercise-library/contact-search/experiment.json --output artifacts/040-contacts-replay
uv run aec frozen plan experiments/040-exercise-library/plan-equivalent/experiment.json --output artifacts/040-equivalent-replay
uv run aec frozen held experiments/040-exercise-library/held-wide/experiment.json --output artifacts/040-held-replay
uv run aec frozen collision-coverage experiments/040-exercise-library/endpoint-coverage/experiment.json --output artifacts/040-coverage-replay
uv run aec frozen hand-audit experiments/040-exercise-library/movement-audit/experiment.json --output artifacts/040-audit-replay
uv run aec frozen render experiments/040-exercise-library/same-row-lower/candidate-0/result.json --source-snapshot experiments/040-exercise-library/source-snapshot.zip --output artifacts/040-image-replay
uv run aec verify experiments/040-exercise-library/contact-search --require-complete
```

Definitions deliberately link to exact published hashed states; a fresh-chain
comparison must update paths/hashes explicitly rather than silently substitute
new branch orderings. Frozen verification proves file/source/lock commitments,
not numerical replay, full tissue validity or human playability. Focused no-render
and exact sequence continuity regressions pass; Ruff and ty pass. The root
milestone records the final full-suite validation and catalog publication.

## Published catalog and exact sequence workflow

The [catalog](../../targets/CATALOG.md) contains 31 targets/33 physical realizations
across six families, with 14 recorded sampled movement strategies. Two physical
realizations remain hypotheses. Every evaluated realization links actual contact
and/or movement evidence; independent hand and instrument reports match the
exact source hash and compiled variant. No human feasibility label is assigned.

`sequences/` freezes the reusable exact-composition workflow, regenerating the
three ordered trajectories from hashed segment records with exact qpos/contact
joins and a sample-state commitment. Run `uv run aec frozen sequence
experiments/040-exercise-library/sequences/experiment.json --output artifacts/040-sequences`.
The early `sequence-compositions.json` remains a separate construction record,
not a new solve. All 14 frozen roots verify completely; integrity does not
upgrade anatomical validity.

Final stable `uv run aec check`: 120 tests pass, Ruff formatting/lint and ty pass.
The library verifies 161 evidence files across 26 frozen roots.
