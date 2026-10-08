# Endpoint exports must replay their selected state

Review of 012 found that its exported endpoint input names the correct G6
contact but initializes from the C4 atlas anchor. Its saved endpoint qpos,
diagnostics and renders are valid under the recorded model; rerunning that
input may choose another local-IK configuration. Its experiment identifier and
initial-state metadata were inherited from the anchor as well.

The export now records all selected joint coordinates as its initial condition,
uses its own identifier and distinguishes the atlas source state. This new
frozen rerun preserves 012's published records and reproduces its selected
300.29 mm relocation. The independently rerun `replayed/result.json` accepts
the exported G6 configuration with maximum qpos difference below 1e-12 rad.
A regression checks target, identifier, coordinates, profile and model hashes.

Reproduce the selection with `uv run aec frozen exercise
experiments/015-exercise-endpoint-replay/experiment.json --output artifacts/015`.
Then run `uv run aec experiment artifacts/015/endpoint-input.json --output
artifacts/015-replayed`. To use the archived algorithm, run that experiment
through `aec frozen experiment` with `--source-snapshot` from this directory.
Selection views are unchanged from 012; independent replay views are published
under `replayed/renders/`. Collision-coverage limitations from 014 still apply.
