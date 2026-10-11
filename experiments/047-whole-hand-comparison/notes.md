# 047 — Matched whole-hand selection and posture ablations

Ten frozen searches use the same fixed model and numerical starting pose.
Six arpeggio trials compare A (palm-ranked seeded baseline), B (whole-hand
Pareto beam) and D (optional educational 2/3/4 exploration priority), with seeds
4309/4310. All use beam width 2, four assignments per parent, 240 contact
iterations, identical movement limits, all five eligible fingers and no optional
preparation. Actual consumed budgets and every failed/unexplored branch remain
in the records. Four stepwise trials change only free/frozen/local-reference
posture policy at seed 4309. No instrument, proxy, muscle or collision parameter
changes are involved.

The B online vector includes palm path (m), wrist and digit total variation
(rad), and **event-endpoint-only** proxy penetration (m). Nondominated layers
retain tradeoffs; wrist/proxy/digit/palm tie order is a declared research
preference. The first contact has no approach cost because its approach is
unplanned, not because a seed-to-contact trajectory was accepted. D prioritizes
2/3/4 hypotheses using the supplied [2017 instructional approach](https://playingchromaticaccordion.blogspot.com/2017/).
It retains all hypotheses, including thumb/little, and records budget-unexplored
ones. The priority is technique-specific, not muscle strength or anatomical law.

## Controlled results

[comparison/result.json](comparison/result.json) independently audits every
sample of both complete strategies from all ten trials, including all configured
hand pairs and instrument solids. Traces use actual sample indices, never time.
For each trial's initially selected strategy:

| Trial | Fingers, by event | Palm mm | Wrist total variation rad | Worst cross-digit mm |
|---|---|---:|---:|---:|
| A 4309 | 5,2,5,5 | 121.677 | .4877 | -8.830 |
| B 4309 | 3,2,3,4 | 118.767 | .0513 | -13.599 |
| D 4309 | 3,2,3,3 | 96.298 | .0462 | -3.234 |
| A 4310 | 4,3,5,4 | 83.795 | 1.8035 | -13.965 |
| B 4310 | 3,3,3,3 | 115.689 | .1718 | -4.501 |
| D 4310 | 4,2,2,2 | 96.927 | 1.2549 | -4.856 |
| Free stepwise | 5,5,5 | 52.275 | .1084 | -8.723 |
| Frozen stepwise | 5,5,5 | 48.333 | .0126 | -8.652 |
| Local x3 stepwise | 5,4,5 | 64.636 | .2715 | -9.157 |
| Local x10 stepwise | 2,4,2 | 40.099 | 1.3337 | -9.037 |

The baseline A4309 reproduces the historical adaptive arpeggio's **entire
strategy objects exactly**, including both trajectories. The original marker-
distance low-budget arpeggio and later seeded high-budget arpeggio were
confounded; the new controls separate selection preference from those old
budget/order differences. A4310 changes fingering and dramatically reduces palm
travel while increasing wrist variation. This supports initialization/order and
palm-cost effects, not a universal useful/poor judgment of finger 5.

At A4309 event 0, every discovered contact has zero movement cost. The
ID tie break retains the first two seeded little-finger hypotheses and prunes
the solved middle-finger alternative. B retains that middle-finger branch using
its lower endpoint proxy overlap. At the final A event, the little-finger ending
then wins on measured palm travel versus the index ending. Thus ordering, beam
width, omitted first-approach cost and geometric objective all have recorded
roles; no strength advantage or anatomical digit superiority was evaluated.

B reduces wrist variation under both seeds, but is not a complete physical
improvement: **B4309's first path has a worse intermediate proxy intersection**
than A. Event-endpoint risk misses this. Its second strategy, 3/2/3/5, has
134.252 mm palm travel, .0912 rad wrist variation and -3.234 mm worst overlap.
The little finger is retained as an informative lower-overlap alternative.
D4309 improves all three listed descriptors versus A4309, but D4310's wrist
variation is much higher; technique compatibility is not ergonomic validation.

## Coordination hypothesis and counterexamples

The local-reference policy multiplies Mink's unassigned-digit posture cost by
3 or 10. The reference is each solve's actual input q, not an observed neutral
hand. Costs weight angular errors in radians; Mink squares them in its numerical
objective (x3 therefore changes that diagonal contribution by x9). This is a
soft numerical sensitivity model, not a fixed biological coupling matrix.
Imported joint equalities remain enforced independently.

Free unassigned articulation is observed, freezing produces zero corresponding
joint variation, and stronger regularization changes strategies. No monotonic
benefit is found: x3 increases free-joint motion after the search changes branch;
x10 trades shorter palm travel for much more wrist motion. Frozen also retains
substantial proxy intersections. None of these policies is declared more
humanlike. Per-digit and wrist traces preserve these counterexamples.

## Muscle gate and visuals

Every endpoint of all 20 complete paths is screened under zero/1/3 N synthetic
contact reaction scenarios. None of 216 endpoint screens finds conditional
static equilibrium. These are endpoint estimates, not full-path muscle
validation. Variant C remains explicitly **withheld**, rather than using
least-residual coefficients as effort scores or rejecting human feasibility.

Matched media directories show actual event/sample states, whole-hand/keyboard
views, worst-sample overlays and recorded branch graphs. Animation captions state
that the initial approach is unplanned. Each GIF is an illustrative ordered
subsample of the recorded path, with no fabricated intermediate q or tempo.
B4309 includes both strategies so the intermediate-risk counterexample remains
visible. Search records retain the legacy `pruned_beam_cost` spelling in the
first B runs; selection records identify the actual Pareto criterion. Current
plots display it as policy pruning, and future runs use `pruned_beam_policy`.

```sh
uv run aec frozen passage experiments/047-whole-hand-comparison/arpeggio-B-4309.json --source-snapshot experiments/047-whole-hand-comparison/arpeggio-B-4309/source-snapshot.zip --output artifacts/047-replay
uv run aec frozen selection-comparison experiments/047-whole-hand-comparison/comparison.json --output artifacts/047-comparison
uv run aec frozen passage-media experiments/047-whole-hand-comparison/arpeggio-B-4309-media.json --output artifacts/047-media
```

Use the matching published source archive for exact replay. The fixed model and
sampled configured checks pass; unresolved uncalibrated cross-digit geometry,
missing reactions and dynamic/human feasibility remain open.

## Initial-input correction

During reassessment, `expanded_source()` was found to retain original input
joints after the passage runner replaced its seed with the solved 037 pose.
The frozen paths and their audits use exact saved q and are unaffected. The 045
seed dictionary and 046 `reference-seed`/synthetic probe must not be interpreted
as the executed seed; those two static probes have 0.3 rad equality residual.
Future inputs now materialize replaced joints and record resolved initial q.
Static screens also report an equality-position gate. The historical records
remain intact; 048 adds a matched solved-seed supplement and explicit sidecar
corrections. Imported-default and actual recorded path poses remain consistent.
