# 057 — Integrated whole-hand research library and visual guide

**[Start with the visual research guide](../../targets/VISUALS.md).**
It now explains actual motion, musical contact/release, physical-button/finger
choices, controlled changes, failed hypotheses and scientific limitations across
041–057. The root README and targets README link it prominently. Persistent
`AGENTS.md` and the contact-diagnostics skill require planned, inspected visual
coverage during future milestones, including sufficient intermediate frames,
algorithm records, negative examples and exact provenance.

## What is implemented

`playing_region` measures every saved sample in the verified compiled board
frame: lunate/wrist, capitate, metacarpals, knuckles, all fingertips and palm/
wrist/forearm orientation. Source/upcoming physical caps provide the task-relative
region. Axis excursions, actual path geometry, detours, wrist/finger articulation,
joint margins and independent proxy concerns remain separate.

The lifecycle observer distinguishes established required contacts, maintained
holds, geometrically observed release/recontact, future-target hypotheses and
incidental cap proximity. Actuation remains unknown. An optional geometric gate
checks every accepted edge and retries release within remaining waypoint budgets.
Historical defaults and source archives remain available. The endpoint arithmetic
fix preserves actual graph endpoints; its small subsequent numerical sensitivity
is explicitly measured, not hidden as byte-identical historical replay.

Bounded region selection, soft coordinated palm guidance, their combination and
the historical policy are compared in eight identical-source searches. All five
fingers remain eligible. A negative seed-distance tie policy and failed optional
preparation show why local preferences cannot establish ordinary playing.

## The useful changes, with their costs

| Model comparison | Supported improvement | Costs / unresolved findings |
| --- | --- | --- |
| [Stepwise equivalent events](../055-coordinated-planning/evidence/stepwise-before-after-events.png), [shared paths](../055-coordinated-planning/evidence/stepwise-before-after.png), [coordinated dense playback](../055-coordinated-planning/evidence/stepwise-coordinated-strategy-0/detailed.gif) | Palm normal span 18.50→2.01 mm; worst unresolved overlap 8.723→3.576 mm. | Palm travel 52.27→57.42 mm; wrist movement increases. Index replaces little on different duplicates. Still uncalibrated anatomy. |
| [Arpeggio equivalent events](../055-coordinated-planning/evidence/arpeggio-before-after-events.png), [shared paths](../055-coordinated-planning/evidence/arpeggio-before-after.png), [region dense playback](../055-coordinated-planning/evidence/arpeggio-region-strategy-0/detailed.gif) | Worst overlap 8.830→3.118 mm; maximum capitate normal position 76.79→67.51 mm. | Palm travel 121.68→136.29 mm; wrist variation 0.4877→1.7408 rad; wider normal span toward the board. No universal ergonomic win. |
| [Repeated-note withdrawal](../054-contact-lifecycle/release-depth/release-depth-comparison-events.png), [actual paths](../054-contact-lifecycle/release-depth/release-depth-comparison.png) | At configured 2 rather than 10 mm withdrawal, geometric release remains observed and palm travel falls 27.24→5.63 mm. | This is unmeasured depth sensitivity, not sufficient real button operation. Worst overlap approximately unchanged. |

[All retained policy tradeoffs](evidence/policy-tradeoffs.png) come directly from
[the versioned record](evidence/result.json); both endings remain available.
Coordinated arpeggio worsens overlap; combined policies can approach imported
wrist limits. Region stepwise can bring the capitate origin very close to the
board. No new policy is promoted as the default or called human feasible.

The two primary before/after comparisons each retain identical physical cameras,
shared board-coordinate bounds, equivalent musical events, whole-person context,
keyboard/whole-hand/side views, worst-proxy overlays, actual search graphs,
contact/event diagrams, wrist/finger traces, scientific keyframes and 50–52-frame
actual-sample playback. Separate revised numerical-seed approaches have 38 frames
each. The small repeated-note sensitivity uses its available actual samples.
Display intervals are not physiological time; no intermediate states are invented.

## Initial approach, failure and the Python API

[Separate first-note connections](../056-physical-integrity/approaches/result.json)
reach the revised first poses exactly from the resolved numerical index-C4 seed,
with independently accepted sampled proxies and geometric lifecycle. The API can
explicitly join them into 535/979-sample seed-to-passage geometry. This does not
start at an observed resting hand or establish timed playing. Historical passages
retain their original approach disclosure; new evidence lives in a versioned sidecar.

[Held-note negative evidence](../056-physical-integrity/held-evidence/result.json)
keeps a valid parent and failed attempted chord separate. No successful held GIF
is fabricated. [Failed thumb preparation](../056-physical-integrity/preparation-media/failed-contact/hand.png)
is a requested future target that was dropped after failure. [Canonical coverage](../056-physical-integrity/coverage/result.json)
queries recorded worst states of all eight policy paths without altering masks or
envelopes. The historical simultaneous index/ring static control remains linked,
without pretending it establishes a held transition.

The importable API adds `playing_assessment`, `playing_cases`, `playing_case`,
`playing_search`, `playing_trajectory`, `playing_media`, `playing_comparisons`,
`playing_reviews`, `playing_initial_approach`, `playing_complete_trajectory` and
`measure_playing_strategy`. It preserves the original 50 targets, v1 and v2 APIs,
complete historical states and frozen source identities. Benchmark-only passages
are explicit. Consumers can inspect alternative branches, budgets, every saved
landmark/contact sample, unresolved geometry and exact checked media.
[API documentation](../../targets/API.md) and
[the external consumer](../../examples/playing_consumer.py) demonstrate local use;
no service or package publication is introduced.

## Reproducibility and inspected evidence

[Archived replay](replay-check.json) reproduces all 80 selected stepwise media
files byte-for-byte in this runtime, including physical PNGs, dense/keyframe GIFs,
plots and diagrams. [Frozen integrity](verification.json) checks source/input/media
hashes and source links; it is not scientific validation. The final validation
record is [validation.json](validation.json): 197 tests, Ruff and ty pass,
27 new and 42 historical completed frozen roots verify completely, and the
consumer works from outside the checkout. Two pre-fix programming-error archives
retain their exact inputs/source and exception, without a numerical result; they
are not included among completed frozen runs or accepted movements.

Inspected during the milestones: all four physical diagnostic views for both
baseline/revised passages at their recorded worst samples; equivalent-event
panels; actual intermediate dense frames and synchronized board projections;
worst-proxy overlays including worse combined strategies; repeated-note contact
traces and 10/2 mm matched frames; valid/failed held states; failed thumb preparation;
separate numerical-seed approach frames; and the actual all-policy tradeoff table.
The guide labels physical renders, computed projections, algorithm schematics,
failed attempts and uncertainty. Early 053 overlay annotation limitations remain
explicit; the current 055 strategy overlay legend is corrected.

```sh
uv run aec frozen playing-library experiments/057-playing-library/library.json --source-snapshot experiments/057-playing-library/evidence/source-snapshot.zip --output artifacts/057-library-replay
uv run aec frozen playing-study experiments/057-playing-library/replay.json --source-snapshot experiments/055-coordinated-planning/evidence/source-snapshot.zip --output artifacts/057-render-replay
uv run aec verify experiments/057-playing-library/evidence --require-complete
uv run aec check
```

## What remains

Implementation work can extend bounded approach search and compare future-binding
preparation policies across more seeds, with actual release gating and branch
budgets. These are optional follow-ups, not grounds to start another large program.
The present controls already show that isolated normal-depth, initial-distance or
posture objectives can worsen other dimensions.

Model questions need observations/calibration: finger/hand envelopes and ordinary
coordination, palm/knuckle pose relative to rows, instrument setup, and measured
cap travel/force. Without them, proxy intersections, rigid support geometry and
button proximity cannot establish tissue clearance, sounding notes or comfort.
The native tendon-routing and unsuccessful force-balance limitations from 046/051
remain; muscle effort rankings are withheld. Timed dynamics, personalized anatomy,
fatigue and human feasibility are longer-term work, not delivered conclusions.
