# 049 — Signed wrist posture versus wrist movement

The unchanged compiled MyoSim wrist places `deviation_r` then `flexion_r` on
`lunate_r`, downstream of `radius_r/pro_sup_r`. Deviation uses local +z and
[-0.174533, 0.436332] rad; flexion uses local +x and [-0.785398, 0.785398] rad.
These are imported ranges, not clinical thresholds. Compiled single-coordinate
probes turn the distal hand toward the second-metacarpal radial side for positive
deviation and toward the native FCR routing side for positive flexion. The latter
is opposed to the dorsal ECR routing side. Native radius/lunate/capitate axes
coincide at wrist zero, but the metacarpal landmark axis is oblique. Neither body
axes nor a zero coordinate establish observed anatomical neutrality.

[The frozen record](audit/result.json) hashes the pinned anatomical chain and
records axes, ranges, qpos0 and four deliberately identified FK probes. The
reference is **myosim-imported-zero-v1**, a geometric model reference. A 0.05 rad
forearm rotation changes the whole hand in the board frame while leaving the
relative wrist reference axes unchanged. Palm and radius/ulna quaternions in the
keyboard frame are recorded independently; they are not calibrated palmar-plane
measurements. No clinical angle limit or mandatory straight wrist is introduced.

The fixed 045 benchmark and every retained 047 strategy are reassessed: 28
connected paths plus four separate failed-held nodes. Every saved sample has
signed wrist coordinates, reference departures, range fractions, limit margins,
forearm rotation and simultaneous finger coordinates. Summaries preserve signed
min/max, their exact indices, largest reference departure and total variation.
Musical-event samples are explicit. No distribution statistic is interpreted as
time exposure. Separate failed nodes have no variation/path interpretation.

Concrete counterexamples, in radians:

| Saved strategy | Max flexion departure | Max deviation departure | Wrist variation |
|---|---:|---:|---:|
| Frozen stepwise 0 | .7839 | .4351 | .0126 |
| Frozen stepwise 1 | .5858 | .1525 | .9316 |
| Free stepwise 0 | .7771 | .4357 | .1084 |
| Local x10 stepwise 0 | .5818 | .3739 | 1.3337 |
| Arpeggio B4309 0 | .7818 | .4305 | .0513 |
| Arpeggio A4310 0 | .5919 | .4358 | 1.8035 |

The motionless-wrist preference retains a substantially displaced configuration.
The local x10 sensitivity shortens palm travel (52.275 to 40.099 mm) while reducing
maximum reference departures and increasing wrist movement. Its different finger
assignment, free-finger regularization and wrist compensation are linked, so that
comparison is a policy sensitivity rather than an isolated fingering effect.
The same-seed frozen alternatives preserve a cleaner within-search counterexample.
A4310 versus B4310 similarly trades .5919 versus .7771 rad maximum flexion for
much greater movement. Across seeds, these are descriptive counterexamples,
not causal claims about one changed setting.

Two explicitly synthetic +0.1 rad reference shifts test interpretive sensitivity;
neither is an observed neutral wrist. 052 performs full-path policy comparisons.
Initial approaches remain unplanned. Independent instrument/configured checks
and unresolved cross-digit audits accompany rendered cases; model reference
proximity is not anatomical validity, comfort or injury-risk evidence.

Curated actual-model evidence includes initial/final events, middle samples,
maximum flexion/deviation departures and the independently worst proxy state.
Each rendered set has overview, keyboard, side, whole-hand and collision views.
Nine-frame GIFs contain actual saved states and musical-event boundaries only.
Cameras are matched to 047 across competing strategies. All four views and
whole-hand/collision comparisons were inspected; qpos, roles, requirements,
source/model hashes and exact animation indices are in the record.

```sh
uv run aec frozen wrist-study experiments/049-wrist-posture/experiment.json --source-snapshot experiments/049-wrist-posture/audit/source-snapshot.zip --output artifacts/049-replay
uv run aec verify experiments/049-wrist-posture/audit --require-complete
```

The reusable `WristReference`, `wrist_coordinates`, `reference_geometry` and
`wrist_descriptors` functions distinguish coordinate identity, geometric reference
and untimed movement. Regression checks exercise compiled signs, default-axis
alignment, displaced-but-motionless wrists, intermediate extremes and failed-node
semantics. Historical records and model geometry remain unchanged.
