# 050 — Cross-digit envelope controls and free-finger behavior

[The independent record](audit/result.json) revisits the exact 049 configurations,
queries every unresolved cross-digit phalangeal pair, and records group-wise
traces for all ten digit combinations. For each pair it preserves the minimum,
exact sample, imported-default control distance, rigid shape/type/size, geom and
body positions, body axes, parent body and underlying imported bone meshes.
The existing topology classifications remain unchanged. The worst states also
run the canonical collision-coverage calculation, including actual instrument
solid distances and collision masks/explicit pairs.

An imported default already has about 1.470 mm middle/ring envelope overlap.
That is negative evidence about the proxy reference, not permission for equivalent
overlap elsewhere. Many recorded worst pairs are **different pairs that are
separated at qpos0**, so the larger findings cannot all be explained by that
one source-default intersection.

| Actual saved path | Worst group | Worst distance mm | Same pair at qpos0 mm | Free-digit variation rad |
|---|---|---:|---:|---:|
| B4309 0, wrist-first | middle/ring | -13.599 | +7.082 | .037 |
| B4309 1, proxy-first | middle/ring | -3.234 | -1.470 | 1.736 |
| Frozen stepwise 0 | middle/ring | -8.652 | +17.755 | 0 |
| Frozen stepwise 1 | index/ring | -10.032 | +27.945 | 0 |
| Large-overlap reversal | middle/ring | -16.500 | +5.413 | 2.678 |

The low-free-motion/frozen controls still intersect. Conversely, the retained
little-finger ending moves unassigned digits more while reducing worst overlap.
Free-finger motion is therefore neither a biological impossibility test nor a
monotonic proxy for clearance. Per-digit native joint traces, signed extrema,
limit margins and maximum/free-edge variation expose curling, extension and
configuration changes without imposing invented coupling ratios. Failed held
nodes remain separate configurations and have null motion statistics.

Matched whole-hand/bone and rigid-proxy views inspect middle/ring, ring/little
and index/thumb interactions, both B4309 strategies, frozen digits and failed
held contacts. Their body frames and underlying meshes are distinct from the
capsule/ellipsoid support envelopes. The geometry is imported; tissue thickness,
deformation and playing-pose calibration are unknown. No mesh-distance query is
presented as calibrated bone or skin contact. All four diagnostic views and worst
pair overlays were inspected. These states link the exact 049 sampled animations;
failed held configurations have no invented motion.

Meaningful existing constraints remain the configured instrument/support geometry,
imported joint/equality constraints and explicitly named separation hypotheses,
within their numerical scope. The extra cross-digit queries remain unresolved
anatomical concerns. Large new intersections in previously separated pairs merit
inspection and provisional retention, but do not justify blindly enabling all
pairs, shrinking fingers or calling a path human-infeasible. The overlap increase
relative to qpos0 is a transparent sensitivity descriptor, not a calibrated
allowed-overlap subtraction. 052 uses raw full-path proxy values as a declared
soft comparison preference and retains alternatives.

```sh
uv run aec frozen coordination-study experiments/050-hand-coordination/experiment.json --source-snapshot experiments/050-hand-coordination/audit/source-snapshot.zip --output artifacts/050-replay
uv run aec verify experiments/050-hand-coordination/audit --require-complete
```

`coordination_audit` is reusable and preserves the difference between connected
movement and separate attempted nodes. No anatomy, collision masks, ranges,
contact policy or free-finger solver policy was changed in this milestone.
