# 046 — Native muscle parity, routing failures and conditional static capacity

The pinned MyoSim 0.2.3 / MuJoCo 3.15.0 reference retains **63 muscle
actuators, 67 tendons and 11 joint equalities**. The compiled route inventory,
force parameters, matched native arm/full-body comparisons and 54 static poses
are in [static/result.json](static/result.json). The torso, accordion and
prescribed nonplaying anatomy remain fixed. No muscle parameter, proxy,
collision policy or reference geometry was changed.

## Tests and findings

Native versus reduced lengths, selected-coordinate transmissions and passive
forces agree at numerical precision. The full-body actuator `acc0` differs,
but all 63 force scales are explicit positive F0 parameters; no inferred
acceleration-based force scaling enters these calculations. Engine transmission
is **d(length)/dq**; muscle force is negative pulling force. `M.T @ force`
reproduces engine generalized actuator force. At zero velocity/acceleration,
`qfrc_inverse + qfrc_constraint = qfrc_bias - qfrc_passive` reproduces the
engine's signs. Zero activation still produces passive muscle force.

Parity is not sufficient validation. Central finite differences of actuator
lengths disagree with reported transmissions at five selected poses and ten
of the 3,511 actual recorded path samples. The discrepancies involve PQ,
DELT3 and narrow EDC2/EDC4 route-switch regions. All actual-sample native/reduced
length and transmission comparisons still agree. Bisection across large route
steps preserves PQ jumps of about **1.310 mm**, and DELT3 jumps of
**1.893–1.920 mm**, across coordinate gaps around 4e-14 radians; three other
paths refine smoothly instead. At stepwise sample 19, PQ's pro/supination
length derivative is about -0.003093 m/rad, versus engine -0.0001543 m/rad;
changing the difference step reproduces the discrepancy. This falsifies the
assumption that every retained transmission represents the local routed-length
derivative. The defect is inherited by the reduced model; composition repair
or parameter tuning is not justified by these results.

## Static screen and its assumptions

Each selected exact q is evaluated with zero velocity, acceleration and
activation. Imported equality constraints are treated as ideal reactions by
projecting balance onto their tangent nullspace. Automatic soft joint-limit,
contact and constraint forces are recorded but excluded as uncalibrated
support. Joint passive forces and passive muscle forces are included separately.
The remaining equation uses engine active gains at this posture, 0–1
activation bounds and two explicitly different recruitment objectives:
`sum(a*a)/2` and `sum(a)`. These are conditional estimates, not measured effort
or predicted neural recruitment.

Zero button force is tested, alongside **synthetic 1 N and 3 N outward board
reaction per specified contact**. These numbers are scenario parameters, not
accordion measurements. No other hand support, skin reaction or button travel
is modeled. Failed held states have no assumed pressing reaction. The numerical
force-balance tolerance is 1e-6 Nm, not a physiological tolerance.

**None of 220 static optimizations finds equilibrium under these assumptions**,
including imported defaults, the numerical reference seed and the repetition
control. Bounded least-residual fits are preserved as diagnostics only; their
coefficients are not feasible recruitment vectors. Projected residual norms are
roughly 0.00094–0.00903 Nm. Tangent-space rank is complete (27); bounded unilateral
force balance fails rather than a missing transmission direction. Numerical
fixtures with an explicitly constructed balanced right-hand side succeed under
both objectives, testing the solver without changing scientific experiment data.

The screen cannot yet justify an effort ranking or a human rejection. Unknown
support reactions, imported force/route properties, equality approximations and
missing skin/button mechanics remain relevant. Successful static equilibrium,
if found under another assumption, would still not establish dynamic capacity,
comfort or human feasibility. Muscle-aware fingering selection is gated off
where force geometry or conditional balance fails.

## Visual and reproduction evidence

[media/result.json](media/result.json) binds exact q, active requirements,
cameras, force diagnostics and hashes to five complete four-view/overlay sets.
[Matched reference/extreme](media/reference-vs-extreme.png) is a synthetic
sensitivity comparison, not an observed resting posture. The
[PQ route pair](media/pq-route-before-after.png) displays actual samples 19/20;
its length jump is numerical route evidence, not a visible tissue discontinuity.
Length plots use every actual path sample; route plots use clearly labeled
coordinate probes, never accepted trajectories or animation frames. Separate
static-pose residual plots do not imply temporal activation.

Actual kinematic animations remain linked to exact source states in
[045 media](../045-strategy-audit/media/result.json), including both stepwise
strategies and original/refined arpeggios. They do not show muscle-driven motion;
the newly identified routing concerns apply to their stated paths.

```sh
uv run aec frozen muscle-validation experiments/046-muscle-validation/experiment.json --output artifacts/046-static
uv run aec frozen muscle-media experiments/046-muscle-validation/media.json --output artifacts/046-media
uv run aec verify experiments/046-muscle-validation/static experiments/046-muscle-validation/media --require-complete
```

Use each published `source-snapshot.zip` with `--source-snapshot` for exact
archived-code replay. Future source changes must not reinterpret the frozen
conditional estimates as calibrated physiology.
