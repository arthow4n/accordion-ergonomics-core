# accordion-ergonomics-core

A Python research laboratory for articulated accordion ergonomics, starting
with a Roland FR-1XB-style five-row C-Griff right-hand keyboard. The first
prototype composes MyoArm with a finite 3D button fixture, solves one index
fingertip contact, checks imported joint limits/couplings and collision proxies,
and renders four views without a desktop session.

**Current result: a static kinematic candidate on assumed geometry. Real playing
feasibility, button operation and continuous transitions are not yet established.**
See [RESEARCH_LOG.md](RESEARCH_LOG.md) for findings and failed investigations.

## Reproduce

Use conventional CPython 3.14 managed by [uv](https://docs.astral.sh/uv/).
The lockfile records the full tested dependency stack.

```sh
uv sync --locked
uv run aec check
uv run aec experiment experiments/001-single-contact/experiment.json
uv run aec render artifacts/single-contact/result.json
```

The experiment writes structured input/state/solver history/diagnostics/version
and source hashes to `artifacts/single-contact/result.json` and four PNGs in
`renders/`. `artifacts/` is scratch space. Curated published evidence lives in
[experiments/001-single-contact](experiments/001-single-contact/notes.md).
Use `--output <directory>` to publish deliberately, and `--no-render` for a
solver-only run. A failed solve still saves its state and renders, then exits 1.

Headless rendering uses EGL by default; it requires system EGL/OpenGL drivers
(e.g. Mesa `libegl1` and `libgl1-mesa-dri` on Ubuntu). This environment renders
through software Mesa despite harmless device-permission messages. No DISPLAY,
interactive viewer or GPU access is required for the tested setup. Renderer
bytes can differ across driver versions; numerical state is the evidence.

## Research boundaries

- [Evidence audit and stack decisions](docs/research/evidence.md)
- [SI units, frames, calibration measurements](docs/research/frames-and-measurements.md)
- [Next falsifiable experiments](docs/research/roadmap.md)

Finite topology, metric geometry, anatomical model constraints, numerical
solver weights and ergonomic hypotheses have distinct provenance. Unknown
button travel is represented by null. No grid-distance difficulty or universal
ergonomic score is implemented. Contact requests are a collection; unsupported
chords are rejected explicitly until the solver can validate them.
