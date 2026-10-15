# Visual research guide

## Start here — Five-minute introduction

1. Watch the [arpeggio baseline](../experiments/053-playing-region/evidence/arpeggio-baseline/detailed.gif): actual saved states, with a synchronized board diagram.
2. Compare the [wrist-aware counterexample](../experiments/053-playing-region/evidence/arpeggio-posture-counterexample/detailed.gif) and [common top/side paths](../experiments/053-playing-region/evidence/arpeggio-posture-tradeoff.png). Smaller wrist departure can accompany much more hand travel.
3. See [how the index releases and returns](../experiments/054-contact-lifecycle/evidence/repeated-index/detailed.gif), then open its [contact-distance trace](../experiments/054-contact-lifecycle/evidence/repeated-index/contact-distances.svg).
4. Inspect [the held-note failure](../experiments/056-physical-integrity/held-evidence/held-D4-failure/state-1/hand.png). This is an attempted state, not a completed passage.

## Historical visual index

These are frames of the compiled MyoSim/MuJoCo reference, or diagrams generated
from actual search records. Torso and instrument remain fixed. Animation playback
is illustrative; sampled proxy acceptance is not continuous validity or human
feasibility. Unresolved cross-digit intersections are visible and reported.

| Target ID / question | Selected view | Exact machine-readable evidence |
| --- | --- | --- |
| `five-finger-thumb`: free versus frozen unassigned digits | [Matched whole-hand views](../experiments/041-five-finger-contacts/comparison/thumb-policy-hand.png), [contact/collision close-ups](../experiments/041-five-finger-contacts/comparison/thumb-policy-contact_collision.png) | [Comparison and camera/state records](../experiments/041-five-finger-contacts/comparison/result.json), [all-digit independent coverage](../experiments/041-five-finger-contacts/coverage/result.json) |
| `passage-stepwise`: C4–D4–E4, different final finger/buttons | [Middle→little→index animation](../experiments/042-connected-fingerings/stepwise-media/strategy-0/trajectory.gif), [middle→little→ring animation](../experiments/042-connected-fingerings/stepwise-media/strategy-1/trajectory.gif), [matched final event](../experiments/042-connected-fingerings/stepwise-media/alternative-final-event.png) | [Actual search and sampled paths](../experiments/042-connected-fingerings/stepwise/result.json), [frame indices, cameras and all-sample audits](../experiments/042-connected-fingerings/stepwise-media/result.json), [actual beam graph](../experiments/042-connected-fingerings/stepwise-media/search.svg) |
| `passage-thumb-reversal`: thumb C4–Eb4–C4 control | [Computed animation](../experiments/042-connected-fingerings/thumb-reversal-media/strategy-0/trajectory.gif) | [Search/path](../experiments/042-connected-fingerings/thumb-reversal/result.json), [render/audit manifest](../experiments/042-connected-fingerings/thumb-reversal-media/result.json) |
| `generated-dcbc77238f1b5559`: discovered Eb4–G4–Bb4–Eb4 | [Little/index strategy A](../experiments/043-autonomous-discovery/arpeggio-media/strategy-0/trajectory.gif), [strategy B](../experiments/043-autonomous-discovery/arpeggio-media/strategy-1/trajectory.gif), [matched final Eb4](../experiments/043-autonomous-discovery/arpeggio-media/alternative-final-event.png) | [Selected trial and paths](../experiments/043-autonomous-discovery/discovery/evaluation-07.json), [render/audit manifest](../experiments/043-autonomous-discovery/arpeggio-media/result.json), [all trials including earlier thumb strategy](../experiments/043-autonomous-discovery/discovery/result.json) |
| `generated-247e3482c25d6082`: held D4 coordination not found | [Actual failed-contact views](../experiments/043-autonomous-discovery/held-media/failed-contact/hand.png), [failed beam branches](../experiments/043-autonomous-discovery/held-media/search.svg) | [Selected failed trial](../experiments/043-autonomous-discovery/discovery/evaluation-06.json), [state/collision report](../experiments/043-autonomous-discovery/held-media/result.json). No successful animation exists. |
| Autonomous allocation and selection | [Actual generation/evaluation flow](../experiments/043-autonomous-discovery/summary/discovery.svg), [retained musical and physical differences](../experiments/043-autonomous-discovery/summary/selection.svg) | [Grammar, budgets, observations and selection](../experiments/043-autonomous-discovery/discovery/result.json) |

Media paths are available through `ExerciseLibrary.media`; ordered PNGs and
exact sample identities through `frame_sequence`. The [API guide](API.md) shows
how to retrieve diagnostics and reproduce archived rendering in a fresh output
directory. [044](../experiments/044-internal-library/notes.md) records an actual
consumer replay, without duplicating the published images here.

## How the hand moves

Use the top projection for row crossing (+u outer, increasing row inward) and the
side projection for outward withdrawal (+n). Both use actual physical cap locations
and metric scales. Imported joint origins are landmarks, not skin markers. Palm
axes are imported body axes, not a calibrated palmar plane. All GIFs are untimed
kinematic playback; numerical sample order is not physiological time.

| What to open | What it explains / fingers | Exact evidence and limits |
| --- | --- | --- |
| [Arpeggio baseline dense](../experiments/053-playing-region/evidence/arpeggio-baseline/detailed.gif), [keyframes](../experiments/053-playing-region/evidence/arpeggio-baseline/keyframes.gif), [top/side path](../experiments/053-playing-region/evidence/arpeggio-baseline/board-path.png) | Eb4–G4–Bb4–Eb4, little–index–little–little. Wrist, palm, knuckles and fingertips move around physical caps. | [053 manifest](../experiments/053-playing-region/evidence/result.json): all actual samples, axes, cameras, event/edge references, source/model/input hashes. Approach to the first note is unplanned; proxy overlap unresolved. |
| [Index release and return](../experiments/054-contact-lifecycle/evidence/repeated-index/detailed.gif), [contact trace](../experiments/054-contact-lifecycle/evidence/repeated-index/contact-distances.svg), [musical timeline](../experiments/054-contact-lifecycle/evidence/repeated-index/events.svg) | Repeated C4 with index: approximately 10 mm old-cap separation on both edges, followed by recontact. | [054 manifest](../experiments/054-contact-lifecycle/evidence/result.json). Actual outer distal envelopes are queried. Neither button depression nor a sounded repetition is established. |
| [Thumb reversal dense](../experiments/054-contact-lifecycle/evidence/thumb-reversal/detailed.gif), [board path](../experiments/054-contact-lifecycle/evidence/thumb-reversal/board-path.png) | Thumb C4–Eb4–C4. Large free-hand movement is visible even with one assigned finger. | [054 manifest](../experiments/054-contact-lifecycle/evidence/result.json). Distinguishes modeled contact from forearm/wrist compensation; no technique recommendation. |
| [Larger relocation dense](../experiments/054-contact-lifecycle/evidence/larger-jump/detailed.gif), [path](../experiments/054-contact-lifecycle/evidence/larger-jump/board-path.png) | Generated Eb4–Bb4–Db4, index/little assignments. Shows actual relocation across separated targets. | [Recorded generated trial](../experiments/043-autonomous-discovery/discovery/evaluation-04.json), [054 audit](../experiments/054-contact-lifecycle/evidence/result.json). A longer musical jump does not itself justify every discovered detour. |
| [Modest repeated control keyframes](../experiments/054-contact-lifecycle/evidence/repeated-index/keyframes.gif) | Little palm movement with index withdrawal; useful scale control. | [054 full traces](../experiments/054-contact-lifecycle/evidence/result.json). Even this control retains unresolved cross-digit proxy overlap. |

Each rendered directory retains context, keyboard, whole-hand and side PNGs at
initial/final/maximum-normal/worst-proxy samples. `state-INDEX/` identifies the
sample; `dense/frame-NN/` and the manifest give exact qpos, active requirements and
roles. Dense playback generally includes 36–48 saved samples plus actual
extrema/events. Scientific keyframes explicitly include musical boundaries and
worst diagnostic states. No states are interpolated for display.

## How fingerings are chosen

Start with the [actual arpeggio search graph](../experiments/053-playing-region/evidence/arpeggio-baseline/search.svg).
Each node is an executed finger/physical-button hypothesis; edges are attempted
movement connections. Colors distinguish retained, beam-pruned, contact-failed and
movement-failed records. Counts show generated, attempted and budget-unexplored
hypotheses. Unexplored alternatives have no numerical rejection.

The [autonomous allocation diagram](../experiments/043-autonomous-discovery/summary/discovery.svg)
and [selection diagram](../experiments/043-autonomous-discovery/summary/selection.svg)
explain generated musical challenges and bounded follow-ups from actual records.
The [052 policy comparison](../experiments/052-posture-selection/selection/result.json)
preserves competing complete fingerings and Pareto tradeoffs. First-event contact
cost has historically been zero; no first-note approach follows from that ranking.
Preparation is an optional future hypothesis, with actual next-binding matches
reported separately in v3 assessments.

## What changed recently

[053 whole-hand analysis](../experiments/053-playing-region/notes.md) replaces a
capitate-only explanation with multiple anatomical landmarks in compiled board
coordinates. [054 contact lifecycle](../experiments/054-contact-lifecycle/notes.md)
adds explicit release/held/proximity observations and an optional geometric gate.
The [common arpeggio plot](../experiments/053-playing-region/evidence/arpeggio-posture-tradeoff.png)
shows the baseline versus 052 wrist-aware counterexample on shared physical axes.
In that older comparison, each strategy has one color; lines include wrist,
capitate and index/little knuckles, and numbers mark events. The older bottom
anatomical-color legend applies to individual plots, not this strategy overlay;
055 corrects that annotation. The paired physical GIFs use identical cameras.

## What still looks questionable

| Open this | Question / supported observation | Limits and numerical record |
| --- | --- | --- |
| [Wrist-aware palm excursion](../experiments/053-playing-region/evidence/arpeggio-posture-counterexample/detailed.gif), [common path](../experiments/053-playing-region/evidence/arpeggio-posture-tradeoff.png) | Thumb–little–index–little arpeggio reduces wrist-reference departure but palm path rises 122→293 mm and reaches 113 mm outward normal position. | [053 audit](../experiments/053-playing-region/evidence/result.json), [052 findings](../experiments/052-posture-selection/notes.md). No supported hover limit or universal ergonomic policy. |
| [Worst recorded clustered-finger overlay](../experiments/053-playing-region/evidence/arpeggio-posture-counterexample/state-277/collision.png), [same skeletal hand](../experiments/053-playing-region/evidence/arpeggio-posture-counterexample/state-277/hand.png) | Cross-digit phalangeal proxies overlap by approximately 16.5 mm; nonplaying fingers matter. | [053 independent distances](../experiments/053-playing-region/evidence/result.json). Magenta is unresolved unchecked proxy overlap, not measured tissue penetration. |
| [Last valid held-D4 hand](../experiments/056-physical-integrity/held-evidence/held-D4-failure/state-0/hand.png), [attempted failed chord](../experiments/056-physical-integrity/held-evidence/held-D4-failure/state-1/hand.png), [failed branch graph](../experiments/056-physical-integrity/held-evidence/held-D4-failure/search.svg) | Held finger is valid in the parent; attempted extra note loses the held requirement. Separate states, no successful animation. | [056 review](../experiments/056-physical-integrity/held-evidence/result.json): contact checks and rejected diagnostic interpolation. Finite failure is not human impossibility. |
| [Rejected initial approaches](../experiments/052-posture-selection/selection/result.json) | Three direct numerical-seed approaches fail sampled geometry checks; later passage motion can still be connected. | Saved attempts and four-view states in that record. No resting-hand approach, force or complete performance is established. |

## Current capabilities

The internal Python library separates musical passages, physical duplicate buttons,
all five finger assignments, contact solves, sampled path connections, branch
selection, independent geometry and versioned assessments. It generates challenges,
retains alternatives/failures, provides actual-model renders and retrieves exact
ordered frames. See [Python API](API.md). Historical 50 target IDs are preserved.

## Current scientific limitations

Imported rigid envelopes are uncalibrated for skin/tissue and can intersect across
digits despite configured collision acceptance. Masks suppress many anatomical
pairs; independent distances reveal those omissions. Saved sample checks do not
prove continuous clearance. Muscle routing and conditional static force-balance
limitations from [046](../experiments/046-muscle-validation/notes.md) and
[051](../experiments/051-muscle-support/notes.md) still withhold effort rankings.
Button forces/travel, actual actuation, physiological timing, dynamic performance,
human comfort and human feasibility are unmeasured. A better plot or lower metric
cannot establish them. The fixed generic instrument/body assumptions remain.

## Detailed visual index

The historical table above preserves the main 041–044 entry points. Later
whole-hand, muscle and posture milestones are indexed by their inspected manifests:

- [045 whole-hand strategy audit](../experiments/045-strategy-audit/notes.md): eight full paths and failed-held nodes, traces, four views and branch diagrams.
- [046 native muscle validation](../experiments/046-muscle-validation/notes.md): native/reduced routing anomalies and unsuccessful conditional force balance; diagnostic figures, not activations.
- [047 controlled strategies](../experiments/047-whole-hand-comparison/notes.md): matched whole-hand search, optional technique prior and retained little-finger alternatives.
- [048 library reassessment](../experiments/048-library-reassessment/notes.md): versioned v1 evidence and exact archived replay.
- [049 wrist reference](../experiments/049-wrist-posture/notes.md): signed posture versus movement, imported geometric zero rather than clinical neutrality.
- [050 hand coordination](../experiments/050-hand-coordination/notes.md): compiled proxies and frozen/free controls, unresolved overlap.
- [051 native wrapping](../experiments/051-muscle-support/notes.md): routing switches and unsuccessful support probes; no muscle ranking.
- [052 posture selection](../experiments/052-posture-selection/notes.md): two seeds, finite budget control, posture/clearance/travel counterexamples.
- [053 board-relative hand](../experiments/053-playing-region/notes.md): multi-landmark traces, dense and keyframe playback, exact model/camera/sample provenance.
- [054 lifecycle](../experiments/054-contact-lifecycle/notes.md): repeat/reversal/jump/cross-row/overlap observations and negative held-contact evidence.

All physical frames use compiled model geometry and saved qpos. Board plots are
computed projections; search diagrams are algorithmic schematics. Neither adds
new physical evidence. Hashes and reproduction commands reside with each milestone.
