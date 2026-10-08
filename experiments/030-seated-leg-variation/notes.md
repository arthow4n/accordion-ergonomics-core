# Modest seated-leg/envelope variation and a solver-seed counterexample

029 is the nominal anatomical reference. Here change one lower-body assumption
at a time, keeping the original right-arm geometry, instrument dimensions, yaw,
collision policy, displacement solver and 200-iteration budget. All lower-body
bone transforms and shell/board poses are recalculated from the changed profile.
This is a small exploratory family, not a measured population distribution.

| Case | Change from 029 | Shell/board height change | C4 solve |
|---|---|---:|---|
| `hips80` | Hip flexion 80° instead of 90° | −6.2 mm | Fails from the original 023 numeric seed, 471 mm marker residual |
| `hips80-reseeded` | Same 80° physical setup; numeric seed from accepted 029 joints | −6.2 mm | Accepted, 0.0397 mm marker residual |
| `hips100` | Hip flexion 100° | +69.5 mm | Accepted, 0.0388 mm marker residual |
| `radius90` | Approximate support radius 90 instead of 75 mm | +15.0 mm | Accepted, 0.0034 mm marker residual |

Height dependence is asymmetric because the conservative support plane selects
the higher femur endpoint. At 80°, the hips dominate; at 100°, knees dominate.
The entire box is kept above that plane, not force-balanced on a particular thigh
contact. This is an honest conservative abstraction, not evidence of loaded
support. The larger support capsules can overlap near the hips: they are coarse
reference envelopes, not a mutually nonpenetrating tissue model.

## Solver failure is not an anatomical boundary

The original 80° case exhausted iterations with its arm above the head and no
contact. Preserve its failed four-view renders and complete solver history; this
is a rejected numerical state, never a playing trajectory. A raw numeric prior
from 029, recorded in `seed_origin`, lets the same 80° world converge with zero
registered penetration and range violation. It is **re-solved and revalidated**
under the changed profile, not reused as an accepted foreign-world state.

The nearby 6.2 mm placement change can expose initialization/branch sensitivity.
Neither the first failure nor its very large residual is a reachability limit.
The successful cases' shoulder elevations span roughly 13–23°, wrist flexion
23–30°, and deviation near −9.5°; these are discovered branches, not measured
human posture or proof of a preferred leg angle.

All four standard views were inspected for each case, including the failed
case. Examples: [80° re-solved side](hips80-reseeded/renders/side.png),
[100° side](hips100/renders/side.png),
[90 mm envelope front](radius90/renders/keyboard.png).
The new anatomy remains recognizable as seated across these assumptions. Foot
height and shin inclination change; chair/ground contact is still uncalibrated.
No skeletal scaling, torso movement, proxy shrinking or extra library was used.

Independent `coverage/` audits all three successful variation poses and still
finds unchecked phalangeal overlaps, with maxima about 2.37/3.02/1.56 mm for
80° re-solved / 100° / 90 mm radius. These candidates are not certified anatomical
or human playing poses. All sampled shell/approximate-thigh distances are
positive, but that is only coarse-envelope clearance.

## Reproduce and integrity

```sh
uv run aec frozen experiment experiments/030-seated-leg-variation/hips80/experiment.json --output artifacts/hips80
uv run aec frozen experiment experiments/030-seated-leg-variation/hips80-reseeded/experiment.json --output artifacts/hips80-reseeded
uv run aec frozen experiment experiments/030-seated-leg-variation/hips100/experiment.json --output artifacts/hips100
uv run aec frozen experiment experiments/030-seated-leg-variation/radius90/experiment.json --output artifacts/radius90
uv run aec frozen collision-coverage experiments/030-seated-leg-variation/coverage/experiment.json --output artifacts/leg-variation-coverage
```

The first command exits unsuccessfully by design; its frozen record remains
complete evidence. Five new numerical roots verify completely, including an
exported staged checkout. Saved-state replay of the successful 80° case matches
all four PNGs byte-for-byte in this rendering environment and preserves its MJB
manifest. `comparison.json` links/hash-commits the four source result files.

## CI portability correction

The first 029 milestone passed 81 local tests but failed CI when a test required
the new derived-profile hash to equal the recorded local hash on another host.
Baked nontrivial FK/rotations have environment-dependent floating-point arithmetic.
The follow-up regression requires all serialized fields to match, with 1e−12
absolute tolerance on floating values, and requires repeat compilation to have
identical MJB hashes **within the current runtime**. Historical 023 still uses its
exact recorded profile/MJB checks. This tests physical/frame equivalence without
pretending last-bit numerical identity is universally portable.

Production saved-state profile/model guards remain exact and unchanged. They can
reject a replay across numerical environments; re-solve the recorded input rather
than silently accepting a foreign model. Frozen integrity verification checks
file commitments, not cross-host numerical identity or human biomechanics.
