# 042 — Connected five-finger passage search

The fixed native compact-upper world now accepts musical events separately from
physical duplicate buttons, finger assignments, poses and sampled movement.
Every digit is eligible by default. Unassigned digits articulate under the
existing posture regularizer. No instrument, imported joint limit, equality or
collision envelope was changed. All new solves use displacement collision limits.

## Actual bounded search

`Passage` and `NoteEvent` carry pitches and optional hold-to-next requirements.
`fingering_hypotheses` enumerates physical duplicate-row choices and distinct
finger assignments, retaining exact held finger/button bindings. A bounded beam
solves contacts from the actual parent pose, attempts a sampled movement edge,
and ranks connected children by cumulative discovered palm travel. Event-zero
contact solves have no claimed seed-to-contact approach trajectory. The retained
beam is not optimal and excluded hypotheses are not anatomical impossibilities.

Single-contact changes reuse the withdrawal/RRT planner with named source and
arrival fingers. Multiple contacts use incremental withdrawal, reposition and
approach while auditing required held contacts at every sampled state. The
continuation's achieved endpoint becomes the actual graph node; an independent
pose is never silently joined to it. Repeated identical unheld bindings require
withdrawal before re-contact. Joint interpolation is explicitly audited at
0.003 rad maximum sample increments in these experiments; unsampled intervals
remain unresolved. Large IK steps retain the existing integration backtracking.

Optional future-finger preparation initially prevented all four C4 seed solves.
The [negative prefix](preparation-prefix/result.json) retains those attempts.
The recovery retries required contacts without the optional preparation target,
retaining the failed preparation solve. Selected stepwise strategies have no
successful preparation controls; their free-finger motion is not labeled as
intentional preparation. Recent code also records exact Cartesian controls and
preparation proposal budgets for new runs. Frozen snapshots reproduce older
trace formats without changing their identities.

| Definition | Contact solves | Movement edges | Generated event assignments | Result |
|---|---:|---:|---:|---|
| preparation prefix | 4 | 0 | 10 | no complete passage |
| stepwise C4–D4–E4 | 30 | 16 | 40 | two connected strategies |
| repeated C4 | 10 | 8 | 10 | two connected strategies |
| thumb C4–Eb4–C4 | 10 | 8 | 10 | two connected strategies |
| held C4 + ring E4–F4 | 6 | 2 | 10 | contact candidates, no connected passage |
| held C4 + repeated E4 | 8 | 3 | 12 | contact candidates, no connected passage |

These are event-assignment/contact/edge counts, not total QP iterations. Settings
record every per-solve/waypoint/RRT limit; movement attempts record waypoint calls,
solver outcomes and RRT evaluations. Optional preparation proposals are separate
from event assignment counts. The thumb-only and index/ring restrictions are
experimental search controls, not pedagogical or anatomical exclusions. Marker
proximity orders their proposals; it is never a contact-validity certificate.
All finite failures and unexplored-budget statuses remain machine-readable.

## Outcomes and independent checks

The stepwise strategies share C4 middle `r4c5` → D4 little `r3c5`, then select
E4 index `r5c6` (522 samples, 75.193 mm discovered palm travel) or ring `r2c6`
(656 samples, 84.208 mm). These are actual alternate physical realizations of the
same pitches. Four selected trajectories were independently audited at every
sample: these two, the first repetition (54 samples) and first thumb reversal
(427 samples), totaling 1,659 samples. Every audit checks all 276 hand proxy pairs
and every active right-anatomy proxy against every instrument solid, with exact
witness sample indices. Configured hand pairs and instrument constraints pass
at the recorded tolerance. Unconfigured cross-digit anatomy remains unresolved.

Worst phalangeal proxy distances are −12.892/−15.485 mm for the stepwise
strategies, −8.697 mm for repetition and −13.957 mm for thumb reversal. These are
substantial proxy overlaps, not measured tissue penetration. Animated captions
report sample concerns, and static collision overlays show their witness pairs.
No path is claimed anatomically clear, human feasible, continuous or playable
at the illustrative GIF speed. The second repetition/thumb strategy remains
available numerically but has no independent media audit in this milestone.

The held E4→F4 endpoint solves succeed for two retained index-held C4 branches,
but withdrawal/continuation fails. Repeating E4 while holding C4 also fails the
finite search. Held marker errors in intermediate attempts and sample rejection
indices remain explicit. No held animation was produced. Failures do not prove
human or model impossibility; no masks/proxies were weakened to obtain success.

## Inspected visual evidence

- [Actual stepwise search graph](stepwise-media/search.svg): nodes, edges,
  generated/attempted/unexplored counts, pruning and costs come from the record.
- [Strategy 0 GIF](stepwise-media/strategy-0/trajectory.gif) and
  [strategy 1 GIF](stepwise-media/strategy-1/trajectory.gif).
- [Matched final-event comparison](stepwise-media/alternative-final-event.png).
- [Repeated-note GIF](repetition-media/strategy-0/trajectory.gif) and
  [thumb reversal GIF](thumb-reversal-media/strategy-0/trajectory.gif).
- [Stepwise worst collision](stepwise-media/strategy-1/worst-state/collision.png),
  [preparation failure](preparation-prefix-media/failed-contact/hand.png) and
  [held-contact problem](held-ring-media/failed-contact/collision.png).

All four overview/side/keyboard/hand diagnostic views were inspected for each
selected trajectory's worst state and each preserved failed control. Animation
frames and alternate final states were inspected with matched camera definitions.
The skeleton shows complete digits; the opaque case can occlude distal details.
Proxy overlays expose unresolved composition rather than polishing it away.

Every physical frame uses an exact saved `qpos` sample. `result.json` media
manifests contain source-search hash, model/source identity, cameras, roles,
frame indices, qpos and image hashes. No solver iteration is a playing frame.
The sampler includes every event boundary; missing/failed/jumping/substituted
movement evidence is rejected. There is no additional visual smoothing.

## Consumer API and replay

The [catalog](../../targets/CATALOG.md) adds five passage targets including
negative held cases. `ExerciseLibrary` loads targets, exact trajectories,
independent reports and checked media paths; `discover_passage` accepts new
musical input. The [consumer example](../../examples/consume_passage_library.py)
is tested from an unrelated working directory. Both actual repetition searches
in the numerical test produce identical joint arrays and compiled fingertip FK
confirms more than 9 mm outward release, rather than inferring it from labels.

Each result directory has its own frozen source archive and a
`definition_reference` to the adjacent JSON. Example archived-source replay:

```sh
uv run aec frozen passage experiments/042-connected-fingerings/stepwise-recovery.json \
  --source-snapshot experiments/042-connected-fingerings/stepwise/source-snapshot.zip \
  --output artifacts/042-replay
uv run aec frozen passage-media experiments/042-connected-fingerings/stepwise-media.json \
  --source-snapshot experiments/042-connected-fingerings/stepwise-media/source-snapshot.zip \
  --output artifacts/042-media-replay
```

Run these from the checkout root, as with the catalog's root-relative
`reproduce_argv`. Frozen integrity checks hashes and links;
scientific validity is separately reported. The next stage generates varied
musical hypotheses and allocates additional search from observed outcomes.
