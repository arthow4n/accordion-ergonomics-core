# 044 — Internal consumer API and exact archived-render replay

The library can now submit a musical passage, generate/evaluate hypotheses,
retrieve selected and earlier strategies, obtain independent diagnostics and
return exact ordered PNG frames without opening experiment directories.
Generated/curated provenance is explicit for all 50 catalog entries. Musical
intent, physical assignments, configurations, movement, diagnostics and media
remain separate machine-readable records. No deployment or package release.

`ExerciseLibrary` hashes evidence before loading it, matches frame qpos/contact
requirements and roles to actual trajectory samples, matches diagnostics by
state-sequence hash, and checks frozen archive/input integrity before replay.
Replay refuses nonempty directories. An unavailable or unrendered strategy is
not silently converted into accepted media. A single-event consumer search now
produces independently audited static views and no GIF. Direct numerical calls
include independent audits but do not freeze changing source; long research
continues to use the frozen CLI.

## Recorded validation

[validation.json](validation.json) selects published stepwise, thumb reversal,
generated arpeggio and unsuccessful held targets. The frozen
[report](validation/result.json) checks five rendered strategies against their
actual trajectories and all-sample diagnostics (522, 656, 427, 375, 495 samples).
The held target has no complete strategy or successful animation.

The API actually executes the archived 042 stepwise rendering into a fresh
scratch directory. All **37 PNG/GIF/SVG artifacts are byte-identical** in this
runtime. Full strategy reports, matched comparison metadata, failed-contact
state, original numerical provenance and renderer provenance also compare
identically. The replay itself passes complete frozen integrity verification.
This establishes reproduction of recorded computation and images in the current
locked runtime; it does not establish anatomical validity or portable pixel
identity across graphics drivers. Both the executed 044 wrapper and executed
042 renderer have source archives; their identities are deliberately distinct.

All four regenerated worst-state views, final-event whole-hand frame and
published matched alternatives were inspected. Cross-digit proxy intersections
remain visible; the skeletal geometry does not pretend to be measured skin.
The [selected visual index](../../targets/VISUALS.md) reuses exact existing
assets and links each to search, trajectories, cameras and frame/audit manifests,
including unsuccessful held searches and actual discovery diagrams. No extra
rendered image batch is published, avoiding duplicated media.

## Reproduce and consume

```sh
uv sync --locked
uv run aec frozen library-validation experiments/044-internal-library/validation.json --output artifacts/044-library-validation
uv run aec verify artifacts/044-library-validation --require-complete
uv run python examples/consume_passage_library.py
```

The definition's `replay_output` must be empty: move aside a previous scratch
replay or use a new definition/output for another run. Original published evidence
is never overwritten. Verification checks archived hashes and links; the wrapper
actually reruns rendering and records comparisons. Temporary replay PNGs are
regenerable from unchanged definitions and original archived source.

The [API guide](../../targets/API.md) shows complete import examples, bounded
passage submission, generator/discovery distinction, historical trial selection,
frame retrieval and `reproduce`. Tests run consumer imports and an actual new
repetition search from outside the checkout, audit every returned sample, and
check that a static contact cannot become a successful movement animation.
Existing identity, topology, coupling, named-digit, held-path, search-budget,
collision and fabricated-movement tests remain in force. Validation passed:
152 canonical tests, focused final archive-integrity/static-state API checks,
Ruff, ty, locked uv sync, complete 044 frozen verification and catalog integrity
(50 targets / 435 evidence files / 48 catalog-linked frozen roots).

## Limits and next falsifiable work

This completes the provisional 041–044 engine/library program with mandatory
visual evidence throughout. Finite held/changing-chord failures are retained,
not labeled impossible. Beam/cost selection is bounded, not optimal. Sampled
instrument/configured proxy acceptance coexists with substantial unresolved
cross-digit intersections, and every human-feasibility field remains null.
Biological finger coordination, observed skin/contact envelopes, depression
forces, timing and unsampled interval validity still need independent evidence.
The next physical research should compare calibrated envelopes and observed
whole-hand poses, then revisit held/substitution/preparation branches under that
justified policy, without reshaping proxies or the fixed instrument for success.
