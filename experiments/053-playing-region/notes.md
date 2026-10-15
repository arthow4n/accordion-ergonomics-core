# 053 — Whole hand in the compiled keyboard frame

[Open the visual guide](../../targets/VISUALS.md). The new `playing-study`
workflow records every saved movement sample: lunate/wrist, capitate, five
metacarpal origins, five proximal-joint/knuckle origins, all five pad sites,
and lunate/capitate/radius orientations. These imported joint landmarks are not
measured surface anatomy or a calibrated palmar plane.

The compiled keyboard origin/rotation and physical cap centers are checked against
the canonical geometry. Increasing row moves inward (-u); +v increases pitch and
+n leaves the board. Relevant regions use the actual source/upcoming cap locations,
without an arbitrary rigid boundary. Full paths retain axis excursions, planar
cap-relative offsets, rotation, wrist/forearm/finger traces and per-event detours.

The fixed arpeggio counterexample reproduces 121.68 versus 293.29 mm palm travel.
Normal depth spans 53.42–76.79 versus 37.03–113.31 mm. The changed path also moves
across rows; a keyboard-facing rendering alone conflates these effects. Worst
unresolved phalangeal distance changes from -8.830 to -16.500 mm. No strategy is
promoted based on its reference posture or appearance.

[Common board-coordinate plot](evidence/arpeggio-posture-tradeoff.png),
[baseline dense playback](evidence/arpeggio-baseline/detailed.gif),
[counterexample dense playback](evidence/arpeggio-posture-counterexample/detailed.gif),
[counterexample keyframes](evidence/arpeggio-posture-counterexample/keyframes.gif),
[actual search](evidence/arpeggio-posture-counterexample/search.svg),
[joint/collision traces](evidence/arpeggio-posture-counterexample/joints.svg).
[The manifest](evidence/result.json) binds full FK, source/input/model hashes,
independent all-sample proxy queries, cameras, qpos and exact frame indices.
Playback selects 42 saved-sample indices plus events/extrema; display time is not
performance time. The reference-to-first-note approach remains unplanned.

Inspected: all four diagnostic views plus the worst-proxy overlay at arpeggio
sample 277; first/final/extreme whole-hand montages for all three paths; common
board top/side plot and representative dense frames. Initial scratch plot clipped
fingertips; published output includes them. The numerical traces, rather than
render appearance, establish excursion. Anatomical tissue and unsampled intervals
remain unresolved.

Reproduce:

```sh
uv run aec frozen playing-study experiments/053-playing-region/study.json --source-snapshot experiments/053-playing-region/evidence/source-snapshot.zip --output artifacts/053-replay
uv run aec verify experiments/053-playing-region/evidence --require-complete
```

Baseline 185 tests passed. Focused frame/landmark/lifecycle tests pass; complete
batch validation is recorded in 057. Historical geometry and trajectories remain
unchanged. Some plotting annotations are refined in the matched 055 comparison.
