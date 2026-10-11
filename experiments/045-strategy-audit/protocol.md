# 045–048 falsifiable benchmark and controlled hypotheses

Fixed reference: pinned myo-sim 0.2.3 / MuJoCo 3.15.0, imported unscaled right
musculotendon system, generic seated native reduced full body, closed CBA v3.
Do not alter instrument/anatomical geometry, limits, coupling or collision masks.
Historical source/scene/path identities remain authoritative and unchanged.

## Before implementation: expected checks and failure conditions

1. Recorded-sample audit must reproduce saved palm/site FK and path-length cost
   within floating-point tolerance, every join, exact qpos/roles/frame selection
   and model identity. Missing/failed movement cannot produce an accepted GIF.
   Reference-to-first-contact is unplanned unless actual approach evidence exists.
2. Palm travel need not rank wrist/digit excursion, nearest-button/plane distances
   or unresolved overlap in the same order. Compare both stepwise realizations
   and all arpeggio realizations, not only the selected leaf. No posture-angle or
   hovering-distance thresholds have empirical support here.
3. Native arm and reduced assembly should agree in muscle parameters, matched
   right-coordinate lengths and transmission derivatives. Quantify discrepancies
   rather than forcing agreement. Finite differences must match actuator length
   derivatives; engine forces must match sparse-transmission generalized forces.
   Nonfinite, discontinuous or zero unsupported transmissions block their use.
4. Zero-velocity/acceleration static balance must use equality-consistent virtual
   displacements and account separately for joint passive and muscle passive
   forces. Check engine and reconstructed force signs. Report unsupported modes,
   activation bounds, residuals and numerical status. Extreme versus reference
   posture is a sensitivity comparison, not a known physiological rejection.
5. Zero applied button force and labeled hypothetical force scenarios must remain
   separate. No measured accordion force or support reaction is available. Vary
   recruitment objective and force assumptions; lack of equilibrium under one
   condition is not human impossibility, and success is not comfort/endurance.
6. Compare free, frozen and soft coordinated preferences on identical targets,
   seeds and budgets. Any improvement must report actual joint/site/proxy changes,
   including worse counterexamples. No heuristic is imported tendon mechanics.
7. Compare palm-only, whole-hand, validated muscle and optional technique
   assessments on the same considered branches and comparable new-search budgets.
   Keep all five candidates. Identify ordering, initialization and budget effects
   on little-finger choice without a fixed little-finger penalty.
8. Path revisions must preserve event/held continuity and all independent sampled
   checks. Report actual detours and wrist/free-digit excursions, not untimed
   velocity, acceleration, jerk or effort. Preserve failed held and large-overlap
   cases. No interpolation across unavailable intervals or IK history playback.
9. Every milestone retains model-derived matched views, exact sampled animations,
   worst-state overlays and numerical/algorithm traces with state/source/camera
   manifests. Replay numerical outputs and selected renders from saved inputs.
10. Reassess library realizations using separate musical/contact/path/geometric,
    proxy/posture/static/dynamic/human layers. Historical evidence remains intact;
    new assessments are versioned sidecars. Unknown stays unknown.

## Compact fixed benchmark

Two C4–D4–E4 realizations; original index/thumb and both refined little/index
Eb4–G4–Bb4–Eb4 realizations; generated D4–E4–C#4 reversal with ~16.5 mm unresolved
proxy overlap; thumb C4–Eb4–C4; failed generated held D4 coordination; and the
index C4 repetition control. All recorded path samples are analyzed. Failed held
nodes are static attempted states, not an invented trajectory. The initial
reference is the source's numerical seed, not an observed resting hand.

Success means explaining or falsifying a model hypothesis with controlled data.
A negative muscle validation, unchanged ranking, failed coordination preference
or worse revised path is useful evidence and does not license geometry tuning.
