# 052 — Posture-aware exploration with full-path tradeoff retention

The engine adds `wrist_posture_pareto` alongside the historical palm and
whole-hand Pareto beams. Maximum flexion and deviation departure from the
identified imported reference are **separate axes**, calculated over each actual
sampled edge and accumulated by maxima. Movement variation remains separate.
This is a soft exploration preference; wrist zero is not a required contact pose.
All five fingers remain eligible, including the thumb and little finger in the
new retained arpeggios. The reference world, joints, muscle parameters, contact
checks, collision tolerances and free-finger policy are unchanged.

Three controlled searches change selection mode alone, versus freshly replayed
palm baselines. Seed, initial solved 037 configuration, geometry, assignment
ordering, contact limits, movement settings, beam width 2 and four assignments
per parent match. The fresh baselines reproduce every historical strategy object
exactly. Consumed call counts differ because branches differ; equal caps do not
imply equal execution time or numerical work. Full source/input/dependency archives
preserve selected, failed, pruned and budget-unexplored candidates.

[Independent all-sample audits](audit/result.json) compare every retained complete
path with matching model/state identities:

| Initially selected path | Fingers | Palm mm | Max flexion departure rad | Max deviation departure rad | Wrist variation rad | Worst proxy mm |
|---|---|---:|---:|---:|---:|---:|
| Palm A4309 | 5–2–5–5 | 121.68 | .7776 | .4308 | .4877 | -8.830 |
| Posture C4309 | 1–5–2–5 | 293.29 | .2174 | .3063 | 1.2544 | -16.500 |
| Palm A4310 | 4–3–5–4 | 83.79 | .5919 | .4358 | 1.8035 | -13.965 |
| Posture C4310 | 1–5–5–2 | 253.02 | .2174 | .3063 | 1.2144 | -16.688 |
| Palm stepwise | 5–5–5 | 52.27 | .7771 | .4357 | .1084 | -8.723 |
| Posture stepwise | 2–1–1 | 149.78 | .5841 | .1538 | 1.3518 | -9.578 |

These are meaningful physical strategy differences, **not a general ergonomic
improvement**. Reference departure decreases, but palm travel rises and the
arpeggio proxy concern gets substantially worse. The second C4309 ending has
203.64 mm travel at the same two maximum departures, with greater wrist movement.
It remains available. C4310's ring-ending alternative likewise remains available.
Finger configurations, proximal-joint extremes, free-digit changes, joint margins,
forearm/palm orientation and all independently sampled cross-digit/instrument
checks accompany each path. The latter satisfy configured proxy checks while
cross-digit anatomical validity remains unresolved.

[Policy explanations](selection/result.json) evaluate palm, movement, absolute
posture and whole-hand proxy preferences over complete surviving paths. Same-seed
finite candidate pools combine A/B/C discoveries transparently; they are not a
new exhaustive search. For 4309, movement preference retains the nearly static
wrist B0, posture preference retains C0, and whole-hand preference retains B1's
3–2–3–5 ending with 3.234 mm worst overlap. For 4310 whole-hand preference selects
B0 (4.501 mm), while posture selects C0. Stepwise similarly trades new posture
against historical clearance and movement. No candidate is removed solely for
reference departure or uncalibrated cross-digit overlap. All alternatives and
Pareto layers remain inspectable. Optional technique priority stays in 047/049;
muscle preference is withheld after 051.

Online proxies are still explicitly endpoint-only preliminary descriptors. The
second stage audits every retained complete strategy over the full saved path;
beam-pruned branches and budget-unexplored assignments are not retroactively
certified. `discover_passage(..., final_selection_policy="posture")` exposes this
system without overwriting the alternative paths. Separate policies and extrema
avoid an unvalidated aggregate comfort score.

Movement realism also has measurable tradeoffs. C4309's palm board-normal span
is 37.03–113.31 mm, versus A4309's 53.42–76.79 mm. C4310 spans 11.74–113.31 mm.
C4309 interval path/displacement ratios are 1.18/1.39/1.01, versus A's approximately
1.01/1.00/1.00. Stepwise C spans 69.81–122.45 mm, versus 65.15–83.65 mm; its first
interval detour ratio is 1.28 versus A's 2.12. These describe useful relocation
and numerical detour candidates without defining a hovering threshold. There is
no physiological timing, speed, smoothness, fatigue or force claim. No additional
planning objective is promoted on this evidence alone.

Three optional direct approaches from the **resolved numerical C4 contact seed**
are saved separately. They fail sampled checks: arpeggio instrument penetration
reaches 7.749 mm; stepwise reaches 1.239 mm. They are diagnostic interpolations,
not successful beginning-to-end performances or resting-hand approaches.
Worst/initial/final diagnostic states are rendered in four views with overlays;
no rejected approach GIF is produced. The subsequent musical paths remain
connected. More capable approach planning is an open task.

The two declared synthetic reference shifts test preference sensitivity without
claiming clinical neutrality. Two seeds support the observed reduction in
reference departure; finite caps, existing IK regularization, unmeasured anatomy
and reference choice still limit robustness. The five-assignment control changes only assignments per parent (4→5): contact
solves rise 28→35 and movement edges 24→30, while both complete sample sequences
remain hash-identical. This is a narrow budget sensitivity, not exhaustive
reachability or general seed/budget invariance.

[Matched maximum-flexion views](gallery/result.json) compare baseline and changed
strategies at the same physical scale and cameras. [Audit media](audit/result.json)
include actual initial/final events, intermediate samples, wrist extremes, worst
collision states, all four views and nine-sample GIFs containing each event.
Every image and frame links qpos, roles, contact requirements, model/input/source
hashes and exact sample indices. The initial approach is labeled unplanned.
Before/after tendon diagnostics remain separate from playing paths. Rendered
four-view, whole-hand and worst-proxy sets were inspected throughout the milestone.

The [v2 library sidecar](library/result.json) preserves all 50 historical musical
targets and 53 realizations, and attaches new strategy evidence instead of rewriting
frozen claims. `ExerciseLibrary.posture_assessment`, `posture_case`,
`posture_trajectory`, `posture_media`, `posture_comparisons` and `posture_evidence`
retrieve the qualified descriptors, decision records and hash-checked media.
Unassessed entries remain explicit; observed neutral posture, tissue clearance,
button forces, timing, strain, comfort and human feasibility remain unknown.
The v1 assessment/trajectory interfaces remain available.

```sh
uv run aec frozen passage experiments/052-posture-selection/arpeggio-C-4309.json --source-snapshot experiments/052-posture-selection/arpeggio-C-4309/source-snapshot.zip --output artifacts/052-search-replay
uv run aec frozen wrist-study experiments/052-posture-selection/audit.json --source-snapshot experiments/052-posture-selection/audit/source-snapshot.zip --output artifacts/052-audit-replay
uv run aec frozen posture-selection experiments/052-posture-selection/selection.json --source-snapshot experiments/052-posture-selection/selection/source-snapshot.zip --output artifacts/052-selection-replay
uv run aec frozen posture-gallery experiments/052-posture-selection/gallery.json --source-snapshot experiments/052-posture-selection/gallery/source-snapshot.zip --output artifacts/052-gallery-replay
```


The inspected C arpeggio also keeps nonplaying long fingers in a more closely
clustered flexed configuration. The independent overlaps and full joint traces
support that concern; appearance alone does not establish tissue penetration or
a biological coordination rule. The whole-hand comparison retains this negative
result rather than promoting posture-only selection as an ergonomic default.

[Canonical collision coverage](coverage/result.json) directly reads the recorded
worst C states by strategy ID and exact sample index. No proxy masks are changed.
[Archived renderer replay](replay-check.json) reproduces all 37 selected PNG/GIF/SVG
artifacts, including the actual sampled GIF, exactly in this runtime. Playback and
raster-byte identity do not establish tempo or physiology.

Validation: locked uv sync; 185 canonical tests, Ruff and ty pass. All 42 frozen
045–052 roots pass complete integrity checking. The external consumer and a live
repeated-note final-selection control pass. Three palm replays preserve historical
strategy objects; all 37 selected archived render artifacts reproduce exactly.
See [validation](validation.json) and [integrity records](verification.json).
