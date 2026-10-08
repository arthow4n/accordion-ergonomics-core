# Two search artifacts in the setup family

## Missing C5 at −45° yaw

024's three-start/120-iteration search discovers no C5 pose. Reproduce expanded
search with `uv run aec frozen explore experiments/027-yaw-search-refinement/experiment.json --output artifacts/027`.
Eight starts and 300 iterations discover **four** distinct poses under exactly
the same physical profile and collision tolerances. Other starts still fail;
one initialization violates an imported limit. Negative attempts are retained.

`path/experiment.json` selects the least-relocated accepted endpoint before path
search and uses 1 mm withdrawal resolution. `aec frozen plan` finds a direct
joint-interpolation path: relocation **62.54 mm**, palm path 62.60 mm, no detected
penetration. The coarse missing result is not a demonstrated yaw/reachability
boundary. The pose and path retain model hashes and saved-state diagnostic views.

## Large nearby relocation at 0° yaw

024 reports 213.06 mm best discovered C4→D4 relocation even though the target
is nearby. `yaw-zero-d4/experiment.json` explores 16 deterministic starts with
300 iterations, adding shoulder elevation/plane, forearm rotation and index-MCP
perturbations. It finds six distinct poses. The least-relocated candidate moves
the palm **19.16 mm**. Its `path/` finds direct sampled interpolation, palm path
19.17 mm, zero detected penetration, without changing geometry/tolerances.

This specifically falsifies interpreting the original 213 mm discovery as
movement necessity or a physical effect of keyboard yaw alone. Different
branches and budgets change apparent magnitudes. Keep both outcomes; do not
replace the original sweep's rows with the refined result as if they had used
the same search. The normal family still changes physical placement, but its
kinematic numerical sensitivities require search controls.

All four frozen roots verify completely. 028 audits all ten refined endpoint
poses and still finds unchecked phalangeal overlaps. These are search
counterexamples, not global human feasibility certificates.
