# 003 — Valid endpoints do not imply a valid supplied path

Linearly interpolate the 38 hinge coordinates between accepted C4/r1c5 and
E5/r1c9 endpoint configurations. Inputs identify both immutable result files
with SHA-256 checks. Sample 101 equally spaced dimensionless progress values.
The start contact may release; no held-contact constraint or tempo is assumed.

```sh
uv run aec transition experiments/003-transition-counterexample/experiment.json
uv run aec render experiments/003-transition-counterexample/result.json
```

**Result: this particular path is invalid under the imported collision model.**
Both endpoints pass recorded endpoint checks. Joint ranges and the 11 imported
linear couplings remain valid across the samples. Nevertheless, 95 of 101
samples exceed the 0.1 mm penetration tolerance. At progress 0.33,
`1mcskin_r` penetrates `keyboard_panel` by **13.49 mm**; a neighboring metacarpal
proxy and adjacent buttons also collide.

![Worst sample collision proxies](renders/collision.png)

Red shows penetrating proxy objects. Standard bone-render views alone did not
make the amount of penetration obvious. MuJoCo's default display hides group4,
where the imported contact shapes live; the added collision camera enables
that group, hides decorative bone meshes and highlights detected penetration.
These manually designed imported proxies are not scanned human skin.

`candidate_valid=false` rejects the **supplied interpolation**.
`global_transition_feasible=null` means we have not tested whether a different
path, such as a withdrawal and repositioning, exists. A failure at a sampled
point is a counterexample to this candidate's continuous validity. Conversely,
absence of sampled collisions would be **inconclusive** between samples; there
is no continuous collision certificate or global path planner here.

No contact-preserving transition, actual button press, actuated equilibrium,
velocity, force, comfort or fatigue is inferred. The progress variable is not
seconds. Existing model contact exclusions and incomplete shell geometry still
limit what “no collision” could establish.

The record includes all sample qpos values, contact pairs/distances, violations,
source hashes and the worst state for `aec render`. Five images reproduced
pixel-identically from that saved state in this environment. A regression test
checks that accepted endpoints plus range/coupling validity do not hide the
intermediate collision. The CLI exits successfully when the audit ran; inspect
its result status for the candidate's outcome.
