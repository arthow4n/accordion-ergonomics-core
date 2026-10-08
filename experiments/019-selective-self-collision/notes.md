# Selective index–middle constraints on unmodified envelopes

Compare the same eight starts and task weights with no added self-pairs versus
the 16 Cartesian pairs between imported index/middle proximal, middle and distal
phalangeal proxies. Same-digit composite envelopes and metacarpals are excluded;
other digit pairs remain outside this hypothesis. Pair names and hypothesis
provenance are explicit profile inputs. The scene adds engine contact pairs and
the displacement limit honors them independently of masks. Geometry, meshes,
ranges and tolerance do not change.

| Task | Distinct candidates, reference | With 16 pairs |
|---|---:|---:|
| Index C4 | 3 | 2 |
| Index C4 + middle Bb3 | 3 | 0 |
| Index C4 + middle C#4 | 2 | 3 |

More constraints can steer local IK into new branches; the count increase for
C#4 is not enlargement of the true feasible set. Bb3 is not found within the
recorded starts/budget, not proved impossible. Rejected colliding/range-invalid
seeds and failures are preserved. Candidate discovery now supports the small
index/middle pair, records both contact bindings and includes every digit in
physical deduplication. Active-joint margins include requested digits.

Independent `coverage/result.json` audits all 13 candidates. Unconstrained dual
poses have 3.22–13.39 mm index/middle phalangeal overlap. The constrained C#4
candidates have zero overlap or 0.00256 mm, within the unchanged 0.1 mm tolerance.
Other anatomical overlaps remain; these are constrained-proxy predictions,
not validated human poses.

![C#4 pair under the selected constraints](index-middle-pairs/c4-csharp4/candidate-0/renders/hand.png)

Reproduce each variant with `uv run aec frozen explore
experiments/019-selective-self-collision/VARIANT/experiment.json --output artifacts/019-VARIANT`.
The coverage definition hashes each saved candidate; run it through
`aec frozen collision-coverage` to reproduce independent queries and representative
highlighted views. Source archives are preserved per variant and audit.
