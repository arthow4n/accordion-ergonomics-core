# Next falsifiable questions

The first milestone tests infrastructure and a static contact proxy. It does
not complete a trustworthy playing model.

1. Repeat single-contact solves with multiple starting postures; preserve candidates and diagnose frozen-finger/regularization bias. Calibrate the board and body placement before interpreting angle magnitudes as real playing.
2. Compare finger-only movement from a fixed arm/palm with arm-enabled movement. Seek a distant grid target relieved by relocation and a nearby grid target forcing a near-limit pose. Report joint/palm changes independently; avoid calling them comfortable merely because IK succeeds.
3. Add approach/contact/release paths with collision checking and maximum-step refinement. IK iteration order is solver history, **not** a physical trajectory. A valid endpoint pair does not establish reachability between them.
4. Add multiple contacts and held events while preserving all requested contact states. Experiment input uses a contacts collection already, but the first solver rejects unsupported simultaneous requests explicitly.
5. Explore reachable actions from a saved physical state under explicit palm/arm movement budgets, then passages/button-and-finger search and targeted challenge generation.

Maintain the boundary: musical intent -> finite physical buttons -> articulated
configurations/contact trajectories -> measured diagnostics -> search.
Candidate measurements include per-joint range margins, wrist/forearm angles,
palm displacement/rotation, elbow/shoulder excursion and contact preservation.
A difficulty scalar is not required. Local solver failure means “not found”,
not “physically impossible”; impossibility needs a validated constraint or
search certificate. Feasibility remains nullable while essential constraints
are unvalidated.

The eventual browser runtime may use a reduced or fitted model, but only after
the lab establishes what the representation predicts reliably.
