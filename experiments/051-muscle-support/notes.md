# 051 — Native inverse-wrap fallback and static support blockers

[The frozen investigation](diagnostics/result.json) narrows the inherited routing
failure without modifying native anatomy or muscle parameters. PQ's 1.310023 mm
jump and DELT3's 1.893010 mm jump reproduce in native MyoArm and the reduced world.
The refined fraction gap is 1.4552e-11; corresponding coordinate differences are
near floating-point precision. Routing topology stays constant, while duplicated
inverse-wrap points jump. PQ's side site is at the cylinder center; DELT3's second
side site is inside its 12.5 mm spherical wrap. They therefore invoke inverse
wrapping rather than ordinary exterior wrapping.

Independent scalar inverse-wrap roots distinguish the two native outputs:

| Native probe | Distance to independent root | Distance to fallback average |
|---|---:|---:|
| PQ before | 7.624198 mm | <1e-12 mm |
| PQ after | <1e-10 mm | 7.624198 mm |
| DELT3 before | <1e-12 mm | 13.703664 mm |
| DELT3 after | 13.703664 mm | <1e-12 mm |

The pinned [MuJoCo 3.15.0 inverse-wrap implementation](https://github.com/google-deepmind/mujoco/blob/3.15.0/src/engine/engine_util_misc.c)
initializes z=0.9999999 and returns a default average point when its initial scalar
residual is positive. Here a near-zero residual changes sign across nearly
identical coordinates. The alternate branch uses the root-side point. This
explains the observed route jump as a native numerical fallback switch, rather
than a changed wrapping object, reduced-model composition error or pulling-force
sign mistake. [MuJoCo's modeling documentation](https://mujoco.readthedocs.io/en/stable/modeling.html)
distinguishes interior side-site inverse wrapping from exterior wrapping.

`inverse_wrap_diagnostic` records the exact projected endpoints, interior side
site, native point, independent root/residual, fallback point and discrepancies.
The root is **diagnostic only**. It does not replace native tendon lengths,
transmissions or force evaluation. A production correction would require engine
routing and derivative validation across configurations; switching to guessed
anatomical routes or replacing lengths while retaining inconsistent native
transmissions is not defensible. No geometry/engine patch is claimed.

Native/reduced parameter, length and transmission parity is retained at the tested
ordinary recorded poses. At the near-zero-residual bisection probes, the assemblies
can fall on opposite fallback branches at identical copied coordinates because
of floating-point transforms. The difference then equals the corresponding route
jump. This near-switch sensitivity is recorded separately; parity must not be
asserted there merely from shared geometry. No accepted movement was fabricated. Across the
historical sampled-direction probes and tested coordinate probes, 59 actuators
pass the specified local derivative checks; PQ, DELT3, EDC2 and EDC4 are excluded.
The record exposes this limited operating-quantity subset. Passing those probes
supports descriptive native lengths and tested local transmissions, not globally
validated musculotendon geometry, strength, comfort or an effort ranking.

Five equality-consistent poses include native defaults, the resolved 037 playing
seed, actual PQ samples 19/20 and the arpeggio's first event. The pinned engine's
pulling, passive-force, transmission and inverse/equality conventions remain
checked. Joint passive force is zero in these controls. Passive muscle and gravity
contributions are preserved separately. A separating-hyperplane calculation
certifies that required projected force lies outside A[0,1]; full map rank alone
had not established unilateral/bounded capacity. Certificate normalization is
arbitrary and its gap is not a physiological force or effort score.

Removing gravity alone or passive muscle tension alone remains insufficient.
Even an unbounded six-component palm support wrench does not restore balance.
The tested pressing-state fingertip support span also fails. These results narrow
the explanation beyond missing palm support alone; free-digit force requirements,
route/force-model validity and unknown contact mechanics remain unresolved.
Bounded component probes (3 N forces and .1 Nm palm moments) are hypothetical
sensitivity scenarios, not measured accordion loads. No force constants were fit.
The earlier two recruitment objectives remain in frozen 046 evidence; this
milestone examines bounded feasibility and load/support decomposition separately.
Muscle-aware search remains withheld.

Actual-model four-view/collision sets and separate tendon-only close-ups show the
compiled routes at deliberately identified before/after diagnostic configurations.
Tendon display width is a visual override restored after rendering, not anatomical
thickness or a model correction. Before/after probes are not movement or playing
animations. Their cameras, exact qpos, native/reduced route arrays and hashes are
recorded. The corresponding original kinematic paths and full length traces
remain in 045/046. All four physical views and tendon views were inspected.

```sh
uv run aec frozen muscle-support experiments/051-muscle-support/experiment.json --source-snapshot experiments/051-muscle-support/diagnostics/source-snapshot.zip --output artifacts/051-replay
uv run aec verify experiments/051-muscle-support/diagnostics --require-complete
```
