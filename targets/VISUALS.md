# Selected computational evidence

These are frames of the compiled MyoSim/MuJoCo reference, or diagrams generated
from actual search records. Torso and instrument remain fixed. Animation playback
is illustrative; sampled proxy acceptance is not continuous validity or human
feasibility. Unresolved cross-digit intersections are visible and reported.

| Target ID / question | Selected view | Exact machine-readable evidence |
| --- | --- | --- |
| `five-finger-thumb`: free versus frozen unassigned digits | [Matched whole-hand views](../experiments/041-five-finger-contacts/comparison/thumb-policy-hand.png), [contact/collision close-ups](../experiments/041-five-finger-contacts/comparison/thumb-policy-contact_collision.png) | [Comparison and camera/state records](../experiments/041-five-finger-contacts/comparison/result.json), [all-digit independent coverage](../experiments/041-five-finger-contacts/coverage/result.json) |
| `passage-stepwise`: C4–D4–E4, different final finger/buttons | [Middle→little→index animation](../experiments/042-connected-fingerings/stepwise-media/strategy-0/trajectory.gif), [middle→little→ring animation](../experiments/042-connected-fingerings/stepwise-media/strategy-1/trajectory.gif), [matched final event](../experiments/042-connected-fingerings/stepwise-media/alternative-final-event.png) | [Actual search and sampled paths](../experiments/042-connected-fingerings/stepwise/result.json), [frame indices, cameras and all-sample audits](../experiments/042-connected-fingerings/stepwise-media/result.json), [actual beam graph](../experiments/042-connected-fingerings/stepwise-media/search.svg) |
| `passage-thumb-reversal`: thumb C4–Eb4–C4 control | [Computed animation](../experiments/042-connected-fingerings/thumb-reversal-media/strategy-0/trajectory.gif) | [Search/path](../experiments/042-connected-fingerings/thumb-reversal/result.json), [render/audit manifest](../experiments/042-connected-fingerings/thumb-reversal-media/result.json) |
| `generated-dcbc77238f1b5559`: discovered Eb4–G4–Bb4–Eb4 | [Little/index strategy A](../experiments/043-autonomous-discovery/arpeggio-media/strategy-0/trajectory.gif), [strategy B](../experiments/043-autonomous-discovery/arpeggio-media/strategy-1/trajectory.gif), [matched final Eb4](../experiments/043-autonomous-discovery/arpeggio-media/alternative-final-event.png) | [Selected trial and paths](../experiments/043-autonomous-discovery/discovery/evaluation-07.json), [render/audit manifest](../experiments/043-autonomous-discovery/arpeggio-media/result.json), [all trials including earlier thumb strategy](../experiments/043-autonomous-discovery/discovery/result.json) |
| `generated-247e3482c25d6082`: held D4 coordination not found | [Actual failed-contact views](../experiments/043-autonomous-discovery/held-media/failed-contact/hand.png), [failed beam branches](../experiments/043-autonomous-discovery/held-media/search.svg) | [Selected failed trial](../experiments/043-autonomous-discovery/discovery/evaluation-06.json), [state/collision report](../experiments/043-autonomous-discovery/held-media/result.json). No successful animation exists. |
| Autonomous allocation and selection | [Actual generation/evaluation flow](../experiments/043-autonomous-discovery/summary/discovery.svg), [retained musical and physical differences](../experiments/043-autonomous-discovery/summary/selection.svg) | [Grammar, budgets, observations and selection](../experiments/043-autonomous-discovery/discovery/result.json) |

Media paths are available through `ExerciseLibrary.media`; ordered PNGs and
exact sample identities through `frame_sequence`. The [API guide](API.md) shows
how to retrieve diagnostics and reproduce archived rendering in a fresh output
directory. [044](../experiments/044-internal-library/notes.md) records an actual
consumer replay, without duplicating the published images here.
