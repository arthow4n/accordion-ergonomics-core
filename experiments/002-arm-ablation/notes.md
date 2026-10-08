# 002 — Fixed arm versus whole-arm endpoint candidates

Start with the saved, accepted C4/r1c5 configuration from experiment 001.
The baseline file's SHA-256 is checked before any run. Same board, anatomy,
initial angles, numerical objective and contact normal in every condition.
The old contact is released conceptually; there is no required held contact.

```sh
uv run aec ablation experiments/002-arm-ablation/experiment.json
```

The command writes each generated input, complete result and four renders,
including failed cases. The suite exits normally when all experiments ran;
individual `status` fields determine which endpoints passed. Results do not
claim continuous motion or minimal movement. Unused digits stay frozen.

| Target and mode | Static status | Target displacement | Candidate palm displacement | Wrist deviation margin | Wrist flexion margin | Index abduction margin |
|---|---|---:|---:|---:|---:|---:|
| r1c9, finger only | Failed local search | 76 mm | ~0 mm | 0.51° | 17.58° | 0.00° |
| r1c9, arm enabled | Accepted endpoint | 76 mm | 61.60 mm | 12.15° | 38.63° | 9.32° |
| r3c5, finger only | Failed local search | 38 mm | ~0 mm | 0.51° | 17.58° | 5.40° |
| r3c5, arm enabled | Accepted endpoint | 38 mm | 29.55 mm | 0.45° | 0.73° | 0.55° |

Margins are distance to **imported model limits**, not comfort thresholds.
For rejected candidates they describe an invalid endpoint and must not be
used as ergonomic rankings. The far finger-only candidate penetrates by almost
10 mm and misses its target by about 68 mm; the nearby finger-only candidate
misses by about 21 mm. Neither failure proves those targets globally impossible
with a fixed palm: this is one local search under a normal constraint.

<table><tr><td>Farther target; more palm relocation, larger wrist margins</td><td>Nearer target; less palm relocation, near-limit wrist candidate</td></tr><tr><td><img src="r1c9-arm-enabled/renders/hand.png" width="460" alt="Far target contact with larger wrist margin"></td><td><img src="r3c5-arm-enabled/renders/hand.png" width="460" alt="Near target contact with near-limit wrist"></td></tr></table>

The arbitrary companion *distance terms alone* rank these as 16 versus 3;
they omit actual joint configuration. The farther candidate has larger wrist
margins but changes shoulder elevation about 44°, forearm rotation about 42°,
and elbow about 23°. The nearer candidate changes them about 18°/15°/8°.
Those are distinct physical costs, not grounds for a universal “easier” label.

**Interpretation:** arm freedom changes the solver's available endpoint
configurations. A pitch/grid scalar cannot explain the measured tradeoffs.
**Inconclusive:** whether real players find the farther target straightforward,
or whether geometry *forces* the nearer target to be awkward. A different start,
objective, unused-digit pose or anatomy could produce a better near-target pose.
Do not promote a selected local solution into a necessity claim. We need
multi-start comparisons and measured geometry before stronger conclusions.

All four structured results and all 16 PNGs reproduced identically in a second
run on this environment. `result.json` collects raw joint changes/margins and
palm displacement, with heuristic provenance explicit. It intentionally
contains no ergonomic difficulty scalar and `feasible` remains null.
