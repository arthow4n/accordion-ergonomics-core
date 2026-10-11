# Recorded warm branches improve finite search coverage

The fixed 037 world is retained exactly: compact `generic_cba_v3`, prescribed
seated body/left arm, closed stationary bellows and fixed cases, native right
mechanics, displacement collision limits, sampled integration checks and the
same 16 named index/middle proxy hypotheses. No anatomy, geometry or wearing
placement changed. These are contact/search descriptors, not human exercise
ratings or feasibility certifications.

## Matched candidate budgets and their limits

Two deterministic panels each run eight candidate starts per target with a
220-iteration cap and unchanged 5 mm palm / 10 mm elbow / 0.1 rad joint
candidate grouping thresholds. Baseline repeats 037's seven perturbations.
Warm/diverse retains its first five perturbations, then replaces two middle
abduction offsets with the two additional accepted C4 branches already recorded
in 037. Joint offsets reconstruct their exact qpos; mismatched joint order,
profile identity, compiled world or unsuccessful warm evidence is rejected.
The source states and their SHA256 commitments are in `experiment.json`.

The current starts/iteration caps are matched, but historical warm-state discovery
was paid for previously. This is an amortized reuse experiment, not an equal-total-
cost comparison or a claim of general algorithm superiority. Ordinary exploration
also performs one 200-iteration reference/template solve per target/panel; those
five overhead solves per panel are preserved under `reference/` and do not enter
the candidate counts. Actual iteration histories, failed attempts and wall times
remain in each `discovery.json`. Wall time includes process/environment effects.

| Contact target | Baseline accepted / distinct | Warm accepted / distinct | Baseline palm diameter (mm) | Warm palm diameter (mm) |
|---|---:|---:|---:|---:|
| Index C4 | 5 / 3 | 6 / 3 | 115.846 | 115.846 |
| Index D4 | 5 / 4 | 6 / 6 | 87.468 | 87.468 |
| Index C4 + middle C#4 | 5 / 4 | 6 / 5 | 30.059 | 41.244 |
| Index C4 + middle E4 | 5 / 4 | 6 / 5 | 104.991 | 127.234 |
| Index G6 | 5 / 4 | 6 / 6 | 91.671 | 121.586 |

All five baseline targets preserve two `initial_collision_violation` failures
(recorded status `failed`, termination category `solver_error`) and one
joint-limit-invalid initialization. Both collision failures remain in the warm
panel. Every warm panel has six accepted attempts; duplicate successes remain
separate from the 3–6 physically distinct candidates. Replacing one invalid
start increases acceptance, while reusing saved branches adds distinct states
for four targets. Neither invalid initialization nor finite search failure
establishes physical impossibility. Reused branches preserve their prior search
cost and uncertainty rather than becoming free coverage.

`result.json` contains stable content-derived state IDs independent of candidate
ordering, status counts, failure termination categories, candidate palm diameters
and ordered one/four/eight-start prefix summaries. Prefix coverage depends on the
specified start order. A diameter measures dispersion of discovered palm
positions, not required relocation between notes. Target identity is separate
from each candidate state's identity. No universal difficulty score is defined.

## Alternative endpoint branch changes an observed nearby movement

`nearby-alternate/` connects 037 C4 discovery candidate-0 to D4 candidate-3.
The original 037 selection used its central pose and D4 candidate-0. The new
pair was selected from recorded branches by smallest discovered endpoint palm
distance, with no claim of global optimization. Endpoint palm distance changes
49.498→22.599 mm; the sampled palm path changes **63.669→34.684 mm**. Both use
037's 500 RRT iterations, 220 waypoint iterations, 0.002 rad sampling and seed
3309. The alternate uses incremental withdrawal/RRT/approach, with 187 saved
samples and zero registered sampled penetration. The source contact is released
before the destination is established; no held contact is asserted.

This is a counterexample to treating one branch's recorded movement as necessary
movement. Neither path is a proven human or model minimum. Solver iteration
history is separate from the physical trajectory samples. Nine render indices
were generated; publication retains frames 0/4/8 plus the illustrative GIF.
Animation duration is not musical tempo. All four middle-sample views and the
collision overlay were inspected. Replaying saved sample 93 with the guarded
compiled world gives five byte-identical PNGs in this EGL/Mesa environment;
`render-replay.json` records that environment-specific comparison.

`nearby-alternate/hand-audit/` queries all 276 hand proxy pairs at every sample,
plus 1,225,224 instrument-solid/anatomical-proxy distances. Configured pairs and
instrument tolerances pass at all 187 samples. However, cross-digit phalangeal
proxy distance reaches **−8.758469 mm**, and complete anatomical validity remains
unresolved. The worst hand sample 169's four views and collision overlay were
inspected; visible plausibility does not override this negative evidence.
The policy is `native-hand-proxy-report-v1`, documented in 038. Passing the
configured policy does not make all native overlapping envelopes anatomical
certificates. Continuous unsampled validity and real-world playability remain
unestablished; `human_feasibility` remains null.

`warm-coverage/` independently checks every one of the 25 warm-panel candidate
endpoints against all hand pairs and all instrument solids. Each endpoint is
linked by its result SHA256; library enrichment must match that hash rather than
transfer a similar-looking state. Novel D4 and simultaneous C4/E4 branches have
selected diagnostic renders. All 25 pass both configured pairs and instrument tolerances; all 25 retain
unresolved anatomical validation. Their deepest cross-digit phalangeal distance
is −10.316211 mm. Four views and collision overlays were inspected for both
selected new branches. Saved-state D4 candidate-4 replay reproduces all four
normal views byte-for-byte (`warm-coverage/render-replay.json`). These audit
outcomes remain separate from the solver's acceptance status.

## Reproduce and inspect

```sh
uv run aec frozen search-reliability experiments/039-search-reliability/experiment.json --output artifacts/039-search
uv run aec frozen plan experiments/039-search-reliability/nearby-alternate/experiment.json --output artifacts/039-nearby
uv run aec frozen hand-audit experiments/039-search-reliability/nearby-alternate/hand-audit/experiment.json --output artifacts/039-nearby-audit
uv run aec frozen hand-audit experiments/039-search-reliability/warm-coverage/experiment.json --output artifacts/039-warm-audit
uv run aec verify experiments/039-search-reliability experiments/039-search-reliability/nearby-alternate experiments/039-search-reliability/nearby-alternate/hand-audit experiments/039-search-reliability/warm-coverage --require-complete
```

The reusable implementation is `src/accordion_ergonomics_core/search_reliability.py`;
ordinary exploration remains the solver. The outer portable definition regenerates
the generated panel inputs for the checkout; their recorded resolved baseline
paths describe this execution. The outer frozen manifest commits generated panel files; trajectory and endpoint
audits are separate frozen roots. The committed repeat disables redundant endpoint
renders. The initial fully rendered execution remains in scratch artifacts; its
comparison against the final repeat is recorded in `repeat-comparison.json`: all
80 attempt statuses, underlying failures and qpos arrays, and all candidate state
and descriptor arrays, reproduce exactly. Rendering and executed-source metadata
are allowed to differ. Complete per-start solver histories remain committed in
both discovery and candidate records; the curated tree is approximately 30 MB
mostly compressible JSON, with only selected PNGs.
Integrity verification checks commitments and links, not scientific validity.

Five focused tests cover hash/coordinate/world-guarded warm starts, matched budget
and deterministic panel generation, status/duplicate/missing-evidence distinctions,
order-independent state identity and replay of a recorded warm branch under the
current reference contact constraints. Ruff and module ty checks pass. Initial
full-suite execution passed checks and historical tests through 78% before it was
stopped to relieve concurrent memory pressure; the final program-level full check
is handled separately. No solver architecture, collision envelopes, dynamics or
additional-finger contact support was changed.
