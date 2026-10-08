# A discovered sampled path around the board

The same C4→C5 endpoints as counterexample 003 have a discovered kinematic path
under the imported collision model. Direct joint interpolation has 13.49 mm
penetration. Incremental 20 mm keyboard-normal withdrawal, seeded bidirectional
RRT on independent joints, and approach yield 331 checked samples at maximum
0.005 rad coordinate steps, largest penetration 0.03583 mm (0.1 mm numerical
tolerance). The test re-audits all edges at 0.001 rad and also passes.

Palm path length is 223.1 mm, maximum excursion 65.65 mm. These are physical
model descriptors, not difficulty scores. RRT took seven iterations / 368
collision evaluations with seed 614 for the withdrawal bridge. Search bounds,
step sizes, tolerances, inputs and complete states are recorded.

![Discovered path, collision proxies](trajectory.gif)

Animation duration is illustrative; it is not a proposed tempo. Source contact
releases; no held contact is required. Both endpoints are independently
revalidated on the composed model. Imported affine equalities remain exact
under interpolated independent-coordinate paths.

**Negative evidence:** a restricted single-waypoint, no-RRT search failed at
20–180 mm withdrawals. Every waypoint solve passed but connecting segments
collided. Its [definition](single-waypoint-negative.json) and
[result](single-waypoint-negative/result.json) are preserved and rerunnable.
This failure motivated actual path search rather than larger arbitrary costs.

**Limits:** sampled checks do not certify unsampled intervals. Complete
self-collision, body/strap/instrument shell, actuation, force, timing and button
depression are unvalidated. `physical_feasibility` and `continuous_validity`
remain null. No-path outcomes never mean impossibility.

**Rendering correction:** new multi-state callers exposed stale Cartesian
geometry after qpos assignment and persistent overlay colours. Rendering now
runs forward kinematics and restores display arrays. New candidate/path images
were regenerated. A regression verifies pose refresh, distinct images and an
unchanged full compiled-model hash after rendering.

```sh
uv run aec plan experiments/006-transition-search/experiment.json
uv run aec plan experiments/006-transition-search/single-waypoint-negative.json --no-render
```
