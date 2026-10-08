# Unrequested digit movement is a modeling choice

Six index-button queries compare freezing unused digits with allowing their
imported articulation. Both cases find two sampled transitions. Allowing motion
adds an accepted r4c8 endpoint, but its transition is not found with the recorded
budget: 2 paths/4 missing poses becomes 2 paths/3 missing poses/1 missing path.
This does not establish that unused fingers are irrelevant, or that r4c8 is
impossible. Their four coordinates per digit are bound by anatomical body
subtrees rather than hard-coded coordinate indices. Candidate descriptors now
preserve every digit's articulation.

The initial attempt failed because Mink rejects an empty freezing constraint;
the solver now omits that constraint when no coordinates need freezing. A
regression covers this branch. Execution archives preserve the final algorithm.

Reproduce with `uv run aec frozen sweep
experiments/011-inactive-digit-policy/experiment.json --output artifacts/011`.
The results are restricted, finite rigid-proxy searches. See
[014](../014-collision-coverage/notes.md) before interpreting self-collision.
