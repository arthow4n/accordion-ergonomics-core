# Research log

## 2026-10-08 — CI setup failure diagnosed remotely

The first pushed workflow failed before checkout: GitHub could not resolve
`astral-sh/setup-uv@v10`. The latest release tag is v10.2.0 but no v10 major alias
exists. Remote job annotations exposed the cause even though unauthenticated
log download returned HTTP 403. Pin checkout v7.0.1 and setup-uv v10.2.0 to
verified tag commit hashes. Local canonical checks pass; remote execution is
pending the corrected push. Do not confuse a workflow file with working CI.

## 2026-10-08 — First headless contact slice; surface errors caught by diagnostics

**Started by GPT-6.1 Sol, reasoning effort Medium, in Codex.**

**Question:** Can the current MuJoCo/MyoArm/Mink stack place an anatomical right
arm at one CBA button while preserving imported constraints and producing
reproducible headless evidence?

**Result:** Static contact candidate found on the explicitly synthetic metric
fixture: C4 at r1c5, index finger, about 0.059 mm marker error; 11 joint couplings
preserved to floating-point precision; no joint-limit violation; approximately
0.033 mm proxy penetration, below the recorded 0.1 mm numerical tolerance.
This establishes infrastructure and a bounded static result, not real playing
feasibility. Wrist deviation and index abduction are each within about 0.5° of
an imported range boundary. A successful solve is not an ergonomic endorsement.

![Whole articulated right limb and board](experiments/001-single-contact/renders/overview.png)
![Index contact close-up](experiments/001-single-contact/renders/hand.png)

**Failures that changed the implementation:**

- An early low-residual solution had no actual fingertip contact. The pad marker used an unresolved MjSpec quaternion while the capsule orientation was specified in Euler angles. Derive from *compiled* geometry instead.
- A volar capsule support touched with the middle phalanx penetrating about 1 mm. It also selected the proximal capsule pole, so it was inappropriate as a fingertip marker.
- A distal capsule pole still let the overlapping fingertip ellipsoid penetrate about 3 mm. Use the distal outer support envelope of both imported shapes and verify actual signed contact distances.
- Initial diagnostic cameras saw the keyboard from behind. Camera look-direction convention is now encoded; test board normal and compare its pitch staggering with the manual.

The misleading historical “success” is retained and explicitly invalidated in
[experiment notes](experiments/001-single-contact/notes.md); failed poses are
useful evidence. Numerical weights and tolerances are solver settings, not
physical constants or biomechanical comfort thresholds.

**Instrument audit:** Both prior repositories agree on finite bounds and pitch
anchor. Roland's p50 diagram supports that mapping but contradicts the app
embedding at equal logical columns: downward offsets are `[0,.5,1,.5,1]`,
not `[0,-.5,0,.5,0]`. Metric half-spacing remains a regular-lattice assumption.
No existing friction/crossing scalar is treated as established biomechanics.

**Tooling:** src-layout, mandatory uv/lockfile, Ruff, ty, pytest; canonical
`uv run aec check`, experiment and saved-state render commands. CPython 3.14.7
works with latest maintained stack distributions. Announced Python 3.14.8 has
no uv-managed download here yet. Ty cannot resolve MuJoCo's native wildcard
symbols; an explicit untyped engine boundary contains that limitation.
EGL software rendering works without DISPLAY despite device-permission messages.
No managed cloud status tool or network-policy file is available on this executor;
ordinary HTTPS checkout/package retrieval succeeded.

**Next:** Multiple starts and movement-budget ablations, then measured geometry,
body placement and collision-validated approach/release paths. The physical
trajectory and button press are still missing; `feasible` remains null.
