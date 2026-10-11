# 045 — Fixed recorded-strategy and untimed movement audit

The [protocol](protocol.md) defines falsifiable expectations before new ranking
or physiology. [benchmark.json](benchmark.json) binds nine cases to unchanged
042/043 search hashes: eight complete paths (3,511 actual samples) and four
separate attempted held-contact nodes. The latter are not connected motion.
[Audit](audit/result.json) contains every qpos, compiled FK, imported palm/body
orientation in board axes, all digit positions, joint margins/excursions/total
variation/reversals, free-digit motion, plane/nearest-cap-center distances,
independent cross-digit distances and retained musculotendon lengths. No timing,
hover threshold, fatigue or physiological angle limit is invented.

All reconstructed palm costs agree with saved source costs within 1e-10 m.
Maximum adjacent coordinate steps are 0.002898–0.002997 rad under the original
0.003 rad sampling limit; there are no invented joins or solver-history paths.
Sample spacing is not a smoothness/dynamics certificate. Every path begins at
its discovered first contact; the numerical seed-to-first approach is unplanned.
The source's initial joint dictionary is preserved, not called a natural rest.

## Computed comparison

Values below are ranges/excursions over actual saved samples, not comfort limits.
Proxy distances are unconfigured imported rigid intersections, not measured skin.

| Case | Samples | Palm travel mm | Wrist flexion excursion rad | Deviation excursion rad | Palm/base-plane range mm | Worst proxy mm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Stepwise middle/little/index | 522 | 75.193 | 0.681 | 0.560 | 22.6–70.1 | −12.892 |
| Stepwise middle/little/ring | 656 | 84.208 | 0.887 | 0.217 | 4.1–70.1 | −15.485 |
| Original arpeggio index/thumb | 579 | 229.664 | 0.241 | 0.219 | 56.1–133.3 | −12.692 |
| Refined arpeggio little/index, little ending | 375 | 121.677 | 0.256 | 0.117 | 53.4–76.8 | −8.830 |
| Refined arpeggio little/index, index ending | 495 | 140.189 | 0.192 | 0.522 | 53.4–76.8 | −9.208 |
| Generated reversal, index | 403 | 145.077 | 0.182 | 0.569 | 34.3–78.3 | −16.500 |
| Thumb reversal | 427 | 85.274 | 0.296 | 0.078 | 102.8–121.2 | −13.957 |
| Low-excursion index repetition control | 54 | 27.235 | 0.045 | 0.022 | 67.3–76.3 | −8.697 |
| Failed held task | Four separate nodes | — | — | — | 58.1–110.7 across nodes | −14.002 |

Palm travel does not order wrist demands consistently. Shorter stepwise has more
wrist deviation but less flexion than the ring alternative. The short little
arpeggio reduces palm travel, deviation and proxy overlap relative to the original
index/thumb result, while its index-ending alternative has less flexion but much
more deviation. This falsifies a blanket explanation that fifth-finger selection
is necessarily worse in these descriptors. It establishes neither physiological
quality nor optimality: the old and refined arpeggios have different search effort
and discovered first-contact postures. Controlled budgets/initialization follow
in 047. No fixed little-finger penalty is justified by these data.

Free-digit total coordinate variation is substantial in some cases: the reversal's
unassigned middle accounts for 1.357 rad and little 0.602 rad; the ring stepwise's
free index accounts for 1.406 rad. These are summed coordinate changes while both
adjacent samples label that digit free, not independent neural control or motion
speed. The thumb reversal's entire palm stays >102 mm from the board base plane;
that is a point descriptor, not prohibited hovering or a body-surface clearance.
The failed held node approaches an imported little-abduction limit within
5.86e-8 rad but fails contact discovery; proximity itself is not a new rejection.

## Assessment hierarchy at this milestone

| Cases | Existing explicit constraints | Suspicious/unexplained | Current anatomical evidence | Muscle/force analysis |
| --- | --- | --- | --- | --- |
| All eight complete paths | Recorded sample/join checks accepted; previously independent instrument/configured-proxy checks pass | Substantial cross-digit overlap; wrist/palm/free-digit trade-offs | Unsupported as complete anatomical validity; no observed skin/playing calibration | Required before capacity interpretation; lengths recorded, no recruitment claim |
| Held task | Complete path absent; event-1 contact solves fail explicit position/orientation tolerances | Different failed nodes and joint-limit proximity | Attempted states unresolved; not proof of musical impossibility | Counterfactual static screening can be attempted, without repairing failed musical contact |
| Low-excursion repetition control | Same numerical acceptance as other paths | Still −8.697 mm unresolved overlap | Cannot declare an ordinary-looking control anatomical truth | Useful matched control, not measured physiological baseline |

No pose is rejected because of its appearance. No configured collision pass is
promoted to anatomy or human feasibility. All five digits remain eligible.

## Visual grounding and reproduction

[Media manifest](media/result.json) saves exact worst-state qpos, sample indices,
roles, cameras, target requirements, proxy pairs and source references. All nine
cases have overview/keyboard/hand/side and highlighted collision views. The failed
case uses an explicit attempted-contact color and label, not a successful press.
[Stepwise comparison](media/stepwise-worst-comparison.png) and
[arpeggio comparison](media/arpeggio-worst-comparison.png) use identical cameras;
each shows its own worst sample, not synchronized event stages.

Four nine-frame actual-sample GIFs compare stepwise alternatives and original/
refined arpeggio paths. They visibly state **initial approach unplanned**.
Examples: [stepwise index](media/stepwise-index/path/trajectory.gif),
[stepwise ring](media/stepwise-ring/path/trajectory.gif),
[original arpeggio](media/arpeggio-original-thumb/path/trajectory.gif),
[little arpeggio](media/arpeggio-little-repeat/path/trajectory.gif).
Each source graph is generated from actual nodes, attempted edges and beam
pruning. Per-path SVGs in `audit/` show wrist/forearm, shoulder, all-digit plane
distances, proxy concerns and proximal digit coordinates. Every sample is present
in the numerical record. All four views, collision overlays and representative
animation frames were inspected; bones and imported proxies stay distinguishable.

```sh
uv run aec frozen strategy-audit experiments/045-strategy-audit/benchmark.json --output artifacts/045-replay
uv run aec verify artifacts/045-replay --require-complete
uv run aec frozen strategy-audit-media experiments/045-strategy-audit/media.json --output artifacts/045-media-replay
uv run aec verify artifacts/045-media-replay --require-complete
```

Frozen archives preserve executed audit and render source separately; the old
model, geometry and trajectories are unchanged. Both published roots pass complete
integrity verification. Archived-source replay reproduces the numerical result,
full media manifest and all 96 PNG/GIF/SVG artifacts byte-for-byte in this
runtime ([comparison](replay-check.json)). Baseline canonical check: 153 tests, Ruff and ty. Focused
new FK/descriptor/negative-node and existing API/verifier tests: 24 passed;
render/model-restoration plus audit regression checks: five passed. Persistent
`AGENTS.md` now requires this visual provenance and conditional physiology scope
for future sessions. 046 validates the actual retained muscles before screening.
