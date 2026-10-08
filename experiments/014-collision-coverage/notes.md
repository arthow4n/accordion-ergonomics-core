# Collision coverage falsifies a stronger interpretation of acceptance

The compiled imported model has **36 anatomical proxies with contype=1 and
conaffinity=0**, so none are automatically compatible with another anatomical
proxy. Its four explicit self-contact pairs all involve thorax and humerus or
radius. Keyboard geometry uses contype=2/conaffinity=1, admitting board/anatomy
contacts. Zero detected penetration therefore says little about finger-to-finger
clearance.

Independent distance queries across digit subtrees find the following unchecked
overlaps. Same-digit geometry is excluded from this audit because capsule and
ellipsoid intentionally compose one envelope. Cross-metacarpal overlaps may
compose the palm; they should not automatically be prohibited either.

| Accepted pose | All cross-digit overlaps | Phalangeal pairs | Largest phalangeal overlap |
|---|---:|---:|---:|
| Single C4 | 12 | 1 | 1.47 mm |
| C4 + Bb3 | 17 | 6 | 9.31 mm |
| C4 + C#4 | 18 | 7 | 14.00 mm |
| G6 relocation | 12 | 1 | 1.47 mm |
| Held-task endpoint | 14 | 3 | 2.43 mm |

![Unchecked index/middle overlap; magenta proxies](renders/two-contact-csharp/collision.png)

These are rigid-proxy distances, not measured tissue intersections. Still, the
large overlaps invalidate treating the dual-contact results as established
anatomical nonpenetration. The baseline already has a 1.47 mm phalangeal overlap;
blindly enabling every self-collision pair would reject that source and confuse
envelope composition with anatomical clearance. We retain numerical records
and downgrade interpretation rather than shrinking envelopes to manufacture
success. Current multi-contact and atlas results remain incomplete-model
predictions.

Reproduce with `uv run aec frozen collision-coverage
experiments/014-collision-coverage/experiment.json --output artifacts/014`.
Inputs hash-check five poses, verify compiled models, query every cross-digit
proxy pair and regenerate four standard views plus a highlighted proxy view.
The auditor reports mask compatibility and explicit-pair membership separately;
it does not pretend to duplicate every engine filter. Rendering restores model
arrays, preserving compiled hashes.

Engine semantics: [MuJoCo collision selection](https://mujoco.readthedocs.io/en/latest/computation.html#selection).
Next: validate finger envelopes, observed human poses and calibration using the
[measurement protocol](../../docs/research/frames-and-measurements.md).
