# Explicit profiles reproduce the legacy fixture

Question: can instrument, setup, player ranges and contact policy become inputs
without changing the existing result accidentally?

The explicit schema-2 input compiles to the same complete model hash as legacy
001 and recovers the same 0.05905 mm marker error. Four standard views were
inspected; replay from the saved result succeeds with a verified compiled-model
hash. Tests also rotate the board, translate the torso independently, check all
62 compiled targets and override one wrist range. Twenty checks pass.

This is a reproducibility boundary, not new anatomical evidence. No segment
scaling is implemented. See [profile limitations](../../docs/research/profiles.md).

```sh
uv run aec experiment experiments/004-profile-recalculation/experiment.json
uv run aec render artifacts/single-contact/result.json
```
