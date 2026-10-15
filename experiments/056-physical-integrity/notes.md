# 056 — Independent geometry, held failure and first-note connections

[The central visual guide](../../targets/VISUALS.md) links the positive and negative
physical evidence. No instrument geometry, imported envelopes, masks, collision
pair hypotheses, joints or muscle parameters were changed.

[Canonical coverage](coverage/result.json) independently queries the recorded
worst phalangeal states of all eight strategy-0 policies in 055, including all
cross-digit proxies regardless of engine filtering and all instrument components.
Each pose retains the exact search SHA, strategy ID, sample index, qpos and
compiled world. All 16 full retained paths were independently queried in 055;
configured/instrument acceptance does not resolve unchecked cross-digit overlap.
[Coverage renders](coverage/renders) expose those rigid proxies in magenta, rather
than hiding them behind skeletal mesh views. Same-segment composite geometry is
not mistaken for a prohibition on every imported overlap. Imported distal-pad
support and thumb orientation remain covered by the five-finger compiled-geometry
regression tests and the unchanged 041 composition; no marker or proxy was moved.

The region arpeggio reduces worst overlap to 3.118 mm; it remains unresolved.
Coordinated arpeggio worsens it to 13.789 mm. Combined strategies have wrist margins
of only a few microradians in some states. Region stepwise brings the capitate
origin as close as 5.43 mm to the board plane. Neither a low marker residual nor
a small capitate distance demonstrates a calibrated palm surface or ordinary
playing. The comparison preserves these counterexamples.

## Held-note failure is not a movement

[Last accepted held D4](held-evidence/held-D4-failure/state-0/hand.png),
[attempted failed chord](held-evidence/held-D4-failure/state-1/hand.png),
[matched side view](held-evidence/held-D4-failure/state-1/side.png),
[actual failed branch graph](held-evidence/held-D4-failure/search.svg).
The parent satisfies the held contact; the attempted chord does not. Its held
marker residual grows from 84 to 452 micrometres, beyond the 100 micrometre
configured tolerance, while distal/cap separation remains approximately 0.9
micrometres. This is failure of the specified target-point requirement, not
evidence that a real held note stops sounding. A diagnostic
interpolation loses the held requirement in 459 sampled states. This interpolation
is explicitly rejected diagnostic evidence, never an accepted path or GIF.
[Exact checks and states](held-evidence/result.json) preserve the failure reasons.
Finite search failure is not evidence of human impossibility.

## Initial approach and zero-cost tie bias

Two revised candidates permit separately computed, independently accepted direct
connections from the resolved index-C4 numerical seed:

- [Stepwise numerical-seed approach](approaches/stepwise-initial/approach-media/detailed.gif),
  [keyframes](approaches/stepwise-initial/approach-media/keyframes.gif): 163 actual samples.
- [Arpeggio numerical-seed approach](approaches/arpeggio-initial/approach-media/detailed.gif),
  [keyframes](approaches/arpeggio-initial/approach-media/keyframes.gif): 235 actual samples.

Both establish the exact original first pose, satisfy the independent sampled
configured/instrument query and the explicit geometric release lifecycle.
These are actual connections to the new selected initial poses, unlike the
rejected old direct approaches in 052. This is candidate-dependent evidence,
not a general solution from arbitrary resting-hand positions. The seed is an
already resolved numerical contact, not an observed rest posture. Extra approach
work is recorded separately from the matched passage-search budgets.

[The approach manifest](approaches/result.json) contains actual computed graphs,
full paths, cameras, requirements, independent queries and exact media frames.
The v3 API can explicitly join these paths to their musical passages because
qpos endpoints match exactly: 535 stepwise / 979 arpeggio samples after removing
the shared boundary. Original frozen passages retain their original unplanned
approach disclosure; the sidecar supplies versioned evidence. Playback has no
musical tempo, force or button-actuation claim.

An optional `initial_selection="seed_distance"` changes first-event zero-cost
ID ties using solved joint distance to the numerical seed, with the surrogate
recorded separately from movement cost. [Its search](seed-distance/result.json)
and [full audit](seed-audit/result.json) show a negative result: retained stepwise
travel rises from 52.27 to 74.29 mm and worst overlap from 8.723 to 12.892 mm.
An initial-posture distance is not a validated approach or whole-passage quality
measure. Historical default ties remain unchanged; the successful new approach
records do not retroactively certify all first-event alternatives.

The optional preparation-control study is recorded separately from the matched
055 searches. Controls are hypotheses for particular future finger/button bindings;
only equality with the next actually retained assignment demonstrates linkage.
No invented next solve or preparatory success is inferred from a role label.

Inspected: matched initial/intermediate/final approach frames, exact joins and
independent distances; valid/failed held states in whole-hand and side views;
all-policy worst-proxy renders, including the combined wrist/proxy counterexamples.
Successful approach playback is separate from failed held diagnostics. Muscle
routing/static force-balance limitations from 046/051 remain unchanged; no effort,
comfort or human-feasibility ranking is added.

```sh
uv run aec frozen collision-coverage experiments/056-physical-integrity/coverage.json --source-snapshot experiments/056-physical-integrity/coverage/source-snapshot.zip --output artifacts/056-coverage-replay
uv run aec frozen playing-review experiments/056-physical-integrity/approaches.json --source-snapshot experiments/056-physical-integrity/approaches/source-snapshot.zip --output artifacts/056-approach-replay
```

The [two-event preparation control](preparation/result.json) uses all five eligible
fingers and six contact solves. Both optional future-target attempts fail; the
engine drops them and finds an unprepared C4–D4 path. The
[attempted thumb preparation](preparation-media/failed-contact/hand.png),
[actual search graph](preparation-media/search.svg), and
[full independent audit](preparation-audit/result.json) retain this negative
result. The prepared role in the failed static frame is a requested target, not
an accepted future contact. No completed preparation animation is manufactured.
