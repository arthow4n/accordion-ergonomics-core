# Geometry sensitivity is confounded by pose and planner discovery

Repeat the same 12 index-action queries after recalibrating source C4 under
explicit unmeasured parameter replacements. All numerical budgets and seeds
are recorded. Reference: 9 sampled transitions, 3 missing poses.

| Profile | Sampled transitions / 12 | Changed search outcomes | Largest common relocation change |
|---|---:|---:|---:|
| 19 mm columns, default placement | 9 | — | — |
| 17 mm columns | 9 | 0 | 96.93 mm |
| 21 mm columns | 3 | 6 | 3.96 mm |
| Board 15 mm forward | 9 | 0 | 41.62 mm |
| Board 15 mm toward torso | 7 | 2 | 45.86 mm |

These are changes in discovered realizations, not human feasibility boundaries.
Identical binary search outcomes do not imply stable movement requirements:
17 mm columns keep the same counts but local pose discovery shifts r1c12's
best discovered displacement by almost 97 mm. More starts and calibration are
needed before calling either pose representative or movement minimal.

**Source calibration matters:** moving the board forward initially prevented
source-contact discovery from the single old initialization. Recorded fallback
multi-start search found two valid source poses, allowing the query to continue.
A missing anchor is comparison-unavailable, not zero changed outcomes.

**Falsification of a physical-boundary reading:** at 21 mm, r1c9 has an accepted
endpoint. The initial planner's withdrawal edges penetrate 0.12125 mm, barely
over the 0.1 mm tolerance. Changing withdrawal waypoints from 5 mm to 1 mm
recovers a sampled transition. The [refinement input](refinement.json) and
[record](refinement/result.json) preserve this. Thus at least one apparent
spacing-dependent failure was planner-resolution behavior, not established
physical impossibility. Tolerance was not relaxed.

```sh
uv run aec frozen sweep experiments/008-geometry-sensitivity/experiment.json --output artifacts/sensitivity
uv run aec frozen atlas experiments/008-geometry-sensitivity/refinement.json --output artifacts/refinement
```

Do not conclude an actual FR-1XB has any of these dimensions. Only column spacing
changes in the spacing cases; row spacing, cap dimensions and shape remain fixed.
