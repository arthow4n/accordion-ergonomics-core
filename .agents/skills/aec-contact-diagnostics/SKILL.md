---
name: aec-contact-diagnostics
description: Validate contact geometry, coordinate-frame changes, and saved MuJoCo playing poses in accordion-ergonomics-core using headless numerical checks and renders. Use when changing anatomical composition or contact markers, or investigating a visually implausible IK result.
---

# AEC contact diagnostics

Run from the repository root. Read `docs/research/frames-and-measurements.md`
when changing frames and `experiments/001-single-contact/notes.md` when changing
fingertip contact. Their findings distinguish schematic topology, synthetic
metric assumptions and imported anatomical proxies.

Use the existing deterministic commands:

```sh
uv run aec check
uv run aec experiment experiments/001-single-contact/experiment.json
uv run aec render artifacts/single-contact/result.json
```

For movement restrictions, reproduce the recorded ablation with
`uv run aec ablation experiments/002-arm-ablation/experiment.json`.
Failed cases are expected evidence there; inspect each case's result.json.

Check contact against compiled geometry, not uncompiled quaternion fields:
MjSpec Euler orientations resolve at compilation. Imported distal capsule and
ellipsoid overlap; a marker on one can be inside the other's support envelope.
A low marker residual alone is not a contact certificate. Inspect signed
fingertip/button distance, all detected penetration, joint-limit violations,
all 11 model couplings and the exact frozen-joint list.

Inspect overview, keyboard, side and hand PNGs. Match red outward, green down
(higher pitch), blue outward normal against the canonical frame and Roland
reference. The camera azimuth describes look direction; a rear view can hide
an incorrectly approached button. Distinguish visible bone meshes from
collision proxies. MuJoCo hides group4 by default; use the trajectory audit
collision.png or `render_views(..., collision_overlay=True)` to expose imported
contact shapes and highlight penetration. If rendering needs different drivers, record that; pixel
identity is specific to a rendering environment.

Preserve inputs, source/package hashes, solver settings and useful rejected
poses when publishing a finding. Explicitly invalidate misleading successes.
Keep solver iteration history separate from physical trajectories. A local
failure is not proof of impossibility; a static candidate with unvalidated
press/dynamics/path constraints does not establish human playing feasibility.
Record new uncertainty in RESEARCH_LOG.md before publishing a model conclusion.

For multi-state callers, `render_views` refreshes forward kinematics and restores
overlay arrays. Its regression checks that saved poses produce different images
and that rendering preserves the compiled model. Do not remove these safeguards.

Use `uv run aec frozen atlas DEFINITION --output DIRECTORY` (or `sweep`, `plan`,
`explore`, `experiment`) for long runs concurrent with source edits. The command
archives and executes immutable package source. Replay its exact algorithm with
`--source-snapshot DIRECTORY/source-snapshot.zip`. Keep the recorded dependency
lock and instrument/anatomy inputs; source isolation does not calibrate physics.
Search-resolution failures near collision tolerance need refinement before any
measurement sensitivity is interpreted as a physical boundary.
