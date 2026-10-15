# 054 — Contact, release and held-note semantics

The independent lifecycle observer evaluates actual saved states and both distal
proxies' outer union against the old/next physical cap. It distinguishes event
contact acceptance, held contact checks at every sample, observed geometric
separation, destination recontact, and nonassigned digit/cap proximity. Mechanical
button actuation remains unknown. The separation band is the existing endpoint
position tolerance, not invented skin thickness or measured cap travel.

[Repeated-index playback](evidence/repeated-index/detailed.gif),
[keyframes](evidence/repeated-index/keyframes.gif),
[contact distances](evidence/repeated-index/contact-distances.svg), and
[event timeline](evidence/repeated-index/events.svg) show the index leaving and
returning to C4 twice. Maximum signed distal-envelope/cap separation is 9.99 mm
on both edges. This validates geometric separation under the declared convention;
it does not establish a sounded repetition or performance timing.

The [thumb C4–Eb4–C4 reversal](evidence/thumb-reversal/detailed.gif) separates
14.68/43.08 mm from its prior caps. The [larger-jump example](evidence/larger-jump/detailed.gif)
uses index/little movement and has a separate [board diagram](evidence/larger-jump/board-path.png).
Full FK and independent collision diagnostics also retain cross-row stepwise and
substantial middle/ring or ring/little proxy counterexamples in
[the numerical manifest](evidence/result.json). No unassigned digit/cap pair on
an unrelated musical cap falls inside the declared contact band in these five
paths. This is a narrow sampled result, not exhaustive accidental-note exclusion;
source/upcoming proximity is reported separately, and cap forces/travel are absent.

The original [held D4 search](held-evidence/search.svg) fails to complete.
[Its attempted chord](held-evidence/failed-contact/hand.png) is explicitly negative
static evidence. The paired independent held check in
[056](../056-physical-integrity/held-evidence/result.json) finds a valid parent and
a failed attempted held contact. No animation joins those endpoints as a passage.
Changing chords and same-button substitution remain representable hypotheses,
not evidence of solved held-note performance.

An opt-in `PassageSearchSettings(release_policy="geometric")` now independently
gates every returned movement edge. A path without observed release retries
named-finger withdrawal within the remaining waypoint budget; an unsuccessful
retry cannot be accepted. Historical default behavior is preserved. The
[five-eligible-finger repeated-note control](geometric-repeat/result.json) succeeds
with three contact solves, two movement edges and ten waypoint solves; all five
digits are eligible even though marker-distance ordering chooses index here.
The strict band remains a research convention, not calibrated actuation mechanics.

Preparation controls are saved with their actual chosen-next bindings. The new
assessment reports which optional hypotheses match the eventual branch; it does
not retrospectively label an unchosen hypothesis as successful anticipation.
First-note movement remains separate from the connected musical passage.

Inspected: repeated-index, thumb and jump initial/final/extreme hand montages,
their dense saved-sample frames, contact-distance/event diagrams, failed-held
whole-hand states and corresponding numerical diagnostics. Initial media reuse
the matched 052 cameras; close side/keyboard views in 056 clarify the negative
case. All four standard views and worst-proxy overlays are retained in each
rendered case. Rigid cross-digit overlaps remain unresolved (8.70–16.50 mm).

```sh
uv run aec frozen playing-study experiments/054-contact-lifecycle/study.json --source-snapshot experiments/054-contact-lifecycle/evidence/source-snapshot.zip --output artifacts/054-replay
uv run aec frozen passage experiments/054-contact-lifecycle/geometric-repeat.json --source-snapshot experiments/054-contact-lifecycle/geometric-repeat/source-snapshot.zip --output artifacts/054-repeat-replay
uv run aec verify experiments/054-contact-lifecycle/evidence experiments/054-contact-lifecycle/held-evidence experiments/054-contact-lifecycle/geometric-repeat --require-complete
```
