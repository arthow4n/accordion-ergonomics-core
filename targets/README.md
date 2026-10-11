# Inspect and reproduce the first right-hand target library

This release contains 31 musical/physical target hypotheses. It covers central
and directional controls, row changes, simultaneous index/middle dyads, held-index
coordination, return/alternating sequences and equivalent-pitch physical buttons.
All entries have unknown human feasibility and unresolved anatomical validation.

```sh
uv run aec targets list
uv run aec targets list --family held
uv run aec targets list --status hypothesis
uv run aec targets show held-c4-csharp4-g4
uv run aec targets verify held-c4-csharp4-g4
uv run aec targets verify
uv run aec targets build
```

[CATALOG.md](CATALOG.md) is the generated readable index. [manifest.json](manifest.json)
is the versioned machine-readable release, and [definitions.json](definitions.json)
curates musical identities, physical realizations and actual source selectors.
`targets build` recalculates mappings, statuses, summaries and hash links from
those definitions; it performs no new solve. `show` prints the complete entry.
Each evidence reference supplies `reproduce_argv`: a command argument list that
runs the recorded workflow with its archived source and a scratch output. Run
it from this repository with the locked environment. It can rerun an entire
contact panel, not only one target; its input records the computational budget.
Integrity checks do not prove numerical replay or scientific validity.

## Identity and evidence

Targets have stable curated IDs. Musical intent is a finite ordered sequence of
MIDI pitch collections with no inferred timing or tempo. Realizations specify
physical button IDs, named fingers, and geometric contact/hold/release behavior.
Different physical C4 buttons live within one comparative musical target;
solver branches never become extra musical exercises. Baseline C4 also remains
a separately named control from the early release, sharing evidence deliberately.

Realization IDs hash physical contact events and the reference identity, without
candidate ordering. Branch IDs hash exact compiled identity, joint names and qpos;
movement IDs hash recorded states. These are evidence identities, not claims
that nearby numerical states are disconnected topological IK branches. Candidate
dedup thresholds and distinct counts are specific to each recorded search panel.
The manifest retains several searches and sampled realizations for selected
entries, with actual failure reasons, duplicate successes and budget prefixes.

The physical reference is the 036/037 compact upper `generic_cba_v3` model.
Instrument, native anatomy, fixed posture/wearing setup and contact policy have
separate hashes. Index-only and index/middle contact-site worlds have separately
registered compiled identities; no poses transfer between them. Torso, pelvis,
legs, left arm, both cases and closed stationary bellows remain fixed. Only
index/middle contacts are supported. Coordinates of other fingers remain native,
but their existence is not contact-solver support.

Every realized entry links actual frozen results and candidate files, with
SHA256, source archive, input, dependency provenance, configurations and seeds.
Trajectories remain in those records rather than duplicated in the manifest.
Independent reports join by exact source SHA256, check the compiled identity,
and state the number of audited samples. Missing audits remain missing.
Sequences compose exact recorded samples with qpos/contact equality at every
join, including reverse kinematic traversal. Their audit inheritance covers
those actual samples; it supplies no timing, forces or dynamic reversibility.

## Read the classifications correctly

`hypothesis` specifies targets without a found realization.
`contact_candidates_found` and `sampled_path_found` report numerical discovery
under the configured constraints. `not_found_with_current_search` would report
a finite failure, never impossibility. `collision_policy_rejected` would reject
under an explicitly selected policy. Rejected direct interpolation and failed
initial starts remain visible inside otherwise successful entries.

`independently_audited` means the specified saved-state proxy checks were carried
out and configured hand pairs plus all instrument solids pass. Its scope and
coverage counts are explicit. It does **not** mean complete anatomical clearance:
`native-hand-proxy-report-v1` reports unconfigured cross-digit phalangeal overlaps
as unresolved, distinguishes distal composite envelopes and uncalibrated palm
composition, and changes no anatomy. No measured skin or observed human playing
poses justify a complete hand-collision policy. Large unresolved overlaps remain
prominent negative evidence, including the wider held task's 12.636 mm middle/ring
intersection. These reports cover all right-hand pairs and moving right-anatomy
proxies against instrument solids; they do not certify every moving-arm/passive-
body self-pair or muscle/skin interaction. The fixed passive-body/instrument
reference evidence remains 036. All `human_feasibility` values are null.

## Compare descriptors without a difficulty score

The collection uses deliberate family/direction/span diversity and baseline
counterexamples, rather than an extreme-distance ranking. The same MIDI pitch
can correspond to different physical locations. Simultaneous and held tasks
introduce different coordination constraints from released-contact relocation.

The manifest defines palm path length, palm candidate diameter, joint-coordinate
excursion, joint-limit margins, held residuals and independent signed clearances.
These are descriptors of found model realizations. Path length sums sampled palm
displacements; coordinate excursions are max minus min over samples. Joint margins
refer to imported limits, not comfort. A negative rigid-proxy distance is not
measured tissue penetration. Near-zero cap clearance is expected for contact;
case/rim and panel clearances are reported separately. Forces, fatigue, continuous
interval validity, physiological effort, button travel and human difficulty are
unmeasured.

The two nearby C4→D4 paths (63.669 and 34.684 mm) demonstrate endpoint-branch
sensitivity under matched planning settings. Neither is a necessary movement
minimum. Warm search uses previously paid-for branch evidence, so its matched
current budgets are not matched total research costs. Failed initialization is
not task impossibility. The next validity bottleneck is calibrated hand envelopes
and observed poses, especially inactive middle/ring interactions; unsupported
fingers, active bellows and whole-body strategies remain outside this release.
