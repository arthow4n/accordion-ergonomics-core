# 043 — Autonomous musical hypotheses and observed-result allocation

The generator composes passages from stateful interval/voice choices on the
finite C-system keyboard, rather than copying authored note lists. Seed 4301
produced 21 unique three/four-event hypotheses across stepwise, repetition,
reversal, arpeggio-like, jump, chord and held-voice grammar families. Traces retain
available interval/voice choices, directions, selected notes, duplicate/dead-end
rejections and stable musical hashes. This run used a bounded C4–C5 pitch window
and C4–E4 anchor window: a generation prior, not an anatomical reachability limit.
All five fingers and duplicate physical rows remain assignment candidates.

## Actual evaluation and allocation

Seven balanced-family initial trials use the same fixed reference, free unused
digits, displacement collision limits, two assignments per parent and a width-one
beam. Two follow-ups are selected from **observed** records: the arpeggio path
prompted alternate-strategy exploration; the held connected prefix prompted a
larger finite search. Follow-ups widen the beam/assignment budget and use seeded
assignment order. They increase numerical effort without changing the anatomy,
instrument, required-contact tolerance or collision constraints.

The [machine record](discovery/result.json) contains generation actions, every
trial reference, allocation observations, selected targets and 14 explicitly
unevaluated hypotheses. Total executed budgets: 80 contact solves, 51 attempted
movement edges, 229 waypoint solves, 124 RRT iterations and 8,829 RRT collision
edge evaluations. The 329 generated beam assignments condition on actual held
bindings; 1,710 unconditioned event assignment possibilities across all 21
hypotheses are a distinct combinatorial count, not numerical tests. Per-call
iteration limits, deterministic seeds and a per-edge waypoint-call cap are
recorded. Exhausting that cap creates a budget failure, never a fictitious solve.

| Trial | Family | Connected outcome | Selected evidence |
|---|---|---|---|
| 00 | D4–C4–D4–E4 stepwise | 589 samples, index, 173.180 mm palm path | retained |
| 01 | D4–D4–Eb4 repetition | 284 samples, index, 122.132 mm | retained |
| 02 | D4–E4–C#4 reversal | 403 samples, index, 145.077 mm | retained |
| 03 | Eb4–G4–Bb4–Eb4 arpeggio | 579 samples, index/thumb, 229.664 mm | original successful trial retained in search history |
| 04 | Eb4–Bb4–C#4 jump | 483 samples, index/little, 133.353 mm | evaluated, not selected by the five-entry diversity budget |
| 05 | changing Eb4 dyads | first-contact finite failures | negative trial retained |
| 06 | held D4 with G4/E4 voice | one connected seed event, no complete path | selected negative control |
| 07 | arpeggio follow-up | 375/495 samples, index/little, 121.677/140.189 mm | two alternatives retained |
| 08 | held follow-up | endpoint candidates but no accepted complete path | additional negative trial retained |

All seven completed strategies across trials were independently audited at every
saved sample, totaling 3,208 samples. Instrument solids and configured proxy
constraints pass the recorded tolerance. Cross-digit anatomy remains unresolved:
the reversal reaches −16.500 mm phalangeal proxy distance. The two retained
arpeggio strategies reach −8.830/−9.208 mm. No proxy was shrunk, mask relaxed or
joint limit enlarged. These are provisional model discoveries, not human
feasibility or complete tissue-clearance claims. Failed finite searches and the
14 unevaluated hypotheses are not physical impossibility statements.

The arpeggio follow-up produces little `r4c6` → index `r2c7` → little `r2c8`,
then either little `r1c6` or index `r4c6` for Eb4. Those final realizations use
different duplicate-row buttons and different fingers. Their shorter recorded
palm travel relative to trial 03 is an observed search outcome, not a proven
minimum: the initial contact poses, assignment ordering and numerical budgets
also differ. No initial seed-to-first-note approach is claimed.

## Inspected computational visualization

- [Actual generation/evaluation flow](summary/discovery.svg), showing trials,
  combinatorial counts, numeric budgets and observed-result follow-ups.
- [Actual selection differences](summary/selection.svg), showing notes, holds,
  digits, path descriptors and negative evidence, without a difficulty score.
- [Generated stepwise GIF](stepwise-media/strategy-0/trajectory.gif),
  [repetition GIF](repetition-media/strategy-0/trajectory.gif) and
  [reversal GIF](reversal-media/strategy-0/trajectory.gif).
- [Arpeggio strategy 0 GIF](arpeggio-media/strategy-0/trajectory.gif),
  [strategy 1 GIF](arpeggio-media/strategy-1/trajectory.gif) and
  [matched final-event comparison](arpeggio-media/alternative-final-event.png).
- [Generated held failure](held-media/failed-contact/hand.png) and its
  [proxy overlay](held-media/failed-contact/collision.png).

All four overview/side/keyboard/hand views were inspected for each selected
strategy's worst state and the failed held target. Animation frames, search
summaries, the matched alternate final poses and failure overlays were inspected.
Required/moving/free roles follow recorded controls; the held failure uses cyan
for the held **requirement**, without asserting achieved continuity. Complete
fingers remain visible wherever the physical case/anatomy does not occlude them.
The animations use exactly nine saved sample indices each and no new visual
interpolation. Unequal sample spacings and constant GIF durations carry no tempo
or physiological interpretation. The five animations cover 2,146 selected
samples; all-sample reports and frame/qpos/camera/image-hash manifests are linked.

## Library and reproducibility

Five stable `generated-*` target IDs extend the catalog to 50 targets. Each
contains generated provenance, the exact grammar proposal, selection reason,
original and follow-up trial references, physical strategies, diagnostics and
media. The held entry has no complete realization or animation. The original
index/thumb arpeggio and successful unselected jump remain in the discovery
record, with their honest selection status; they are not silently discarded.

Import `generate_challenges` or `discover_challenges` from
`accordion_ergonomics_core.research`. The latter uses the numerical engine and
independent audits; long runs should use the frozen CLI as this experiment does.
The catalog exposes archived-source `reproduce_argv` references. Example from the
checkout root:

```sh
uv run aec frozen discovery experiments/043-autonomous-discovery/generation.json \
  --source-snapshot experiments/043-autonomous-discovery/discovery/source-snapshot.zip \
  --output artifacts/043-replay
uv run aec frozen passage-media experiments/043-autonomous-discovery/arpeggio-media.json \
  --source-snapshot experiments/043-autonomous-discovery/arpeggio-media/source-snapshot.zip \
  --output artifacts/043-arpeggio-replay
```

All seven published frozen roots have complete integrity checks. This checks
hashes and links, not scientific validity. No new runtime dependencies, graphical
application, external deployment or package-release process were introduced.
The next milestone consolidates the consumer API and selected media/evidence
retrieval, including actual archived-source regeneration tests.
