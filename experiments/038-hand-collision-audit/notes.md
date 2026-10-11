# Native hand proxy reporting policy v1

This investigation keeps the 037 compact upper wearing anchor and all imported
geometry unchanged. It independently queries every pair among the 24 right-hand
collision proxies, including pairs omitted by the solver and engine masks. It
also audits every saved sample of the nearby, larger and held-index trajectories;
solver iteration histories are not trajectories. Numerical conclusions are
limited to those samples.

`native-hand-proxy-report-v1` is a **reporting policy**, not a complete anatomical
collision constraint policy. The 16 existing index/middle separation pairs remain
explicit geometric hypotheses on unchanged proxies. A negative distance for an
unconfigured pair is not silently accepted as anatomically valid or promoted to
a proven tissue intersection. Human feasibility remains null.

## Source anatomy and pair classification

The locked `myo-sim` native `models/arm/assets/myoarm_r_chain.xml` distinguishes
bone visualization meshes from `myohand_coll` shapes. The index distal body,
for example, contains a 7 mm-radius capsule and a 5×8×2 mm ellipsoid, as well as
the separate `2distph_r` bone mesh. The skeletal body and joint hierarchy provides
an anatomical component assignment; it does not establish observed skin shape,
compliance or a calibrated tissue penetration threshold. These imported collision
shapes are proxies, not subject-specific measured soft tissue.

The five distal capsule/ellipsoid pairs occupy the same segment and intentionally
compose its outer contact envelope. Their internal overlap must not be forbidden.
Articulating same-digit segment intersections remain separately unresolved;
joined envelopes at a flexing joint do not prove separate tissue penetration.
Cross-digit pairs involving a metacarpal proxy may represent composite palm
coverage, so their overlaps are reported as unresolved palm composition.
Cross-digit phalangeal intersections outside the 16 selected pairs are stronger
collision concerns, but still lack independent tissue calibration. Thumb and
little-finger phalanges are identified by body ancestry, not spelling prefixes.

All 276 hand pairs are queried with `mj_geomDistance`, without automatic mask,
adjacent-body or explicit-pair selection. Each record separately reports mask
compatibility, compiled explicit-pair membership and configured hypothesis
membership. The 037 world retains incompatible automatic anatomical masks;
its 16 selected hand pairs are explicit compiled engine pairs. This differs from
014's earlier four thorax/arm-only explicit-pair world. Reporting engine contact
counts alone would miss the remaining hand pairs.

No imported geometry is shrunk, repositioned or replaced. No universal rejection
threshold is invented for unresolved pairs. The configured hypothesis uses the
saved solver penetration tolerance; failure there is a policy rejection. Passing
it does not certify complete hand nonpenetration.

## Reproduction and evidence

Run `uv run aec frozen hand-audit
experiments/038-hand-collision-audit/experiment.json --output artifacts/038`.
The definition hash-checks every input, reconstructs each exact contact world,
and checks compiled-model identity before transferring qpos. The report stores
per-pair minimum signed distance and the original sample index, per-sample
unresolved overlap counts, configured-policy rejection records and representative
worst cross-digit phalangeal state. Source samples remain in immutable 037
records; they are not duplicated as a second trajectory. Selected renders use
those saved states and four standard diagnostic views plus a proxy overlay.

Full proxy distances are not a calibrated anatomical audit. This milestone does
not certify muscles, joint soft tissue, skin, friction, button operation, straps,
continuous intervals or human playability. Existing instrument and held-contact
audits remain separately attributable to 037; this report adds complete hand-pair
coverage at its recorded samples rather than rewriting those earlier results.

## Findings

The 24 recorded requests contain 1,260 states: native neutral, 20 accepted
contact endpoints, 261 nearby path samples, 578 larger relocation samples and
400 held-index continuation samples. All 16 configured index/middle separation
hypotheses pass at these samples. Every request retains unresolved anatomical
validation because omitted pairs and calibrated tissue geometry are unvalidated.

| Record | Largest unresolved cross-digit phalangeal overlap | Maximum such overlapping pairs |
|---|---:|---:|
| Native neutral | 1.470 mm | 2 |
| Central C4 | 8.652 mm | 10 |
| Nearby sampled path | 8.702 mm | 10 |
| Larger sampled path | 8.723 mm | 10 |
| Held-index sampled continuation | 7.418 mm | 5 |

The largest neutral overlap is between middle/ring proximal phalangeal proxies.
Central and ordinary-path maxima involve middle distal capsule and ring distal
ellipsoid. Held continuation's largest overlap is middle/ring proximal capsules
at sample 322, whereas its starting and ending contact configurations have only
2.973 and 1.651 mm maxima. This is concrete negative evidence against using
endpoint checks as a proxy for hand validity throughout a held movement. It also
shows why constraining only the played index/middle pair does not cover the rest
of the hand.

Four diagnostic views and overlays were inspected for neutral, central and all
three path worst states. Neutral overview and side confirm the resting hand below
the board; the fixed target-centered hand camera partly crops its fingers, so it
cannot resolve neutral intersections visually. Distance queries remain decisive.
The held overlay exposes a middle/ring proximal envelope intersection. Images
show proxy concerns; their apparent plausibility never upgrades tissue validity.

The complete run independently queries 8,255,520 instrument/proxy sample pairs.
Every instrument solid (including each cap, all panels, rim and both cases) stays
within the configured instrument penetration tolerance for all 1,260 states.
The smallest sampled clearance is the held path's 13.744 µm cap clearance;
neutral's smallest instrument clearance is 10.842 mm. Passing these unchanged
rigid-proxy constraints does not resolve the hand overlaps above. Instrument
acceptance and incomplete anatomy are separate report fields.

A separate [render replay manifest](render-replay.json) records 25 diagnostic PNG
hashes and saved rendered-state identities. Independent frozen hand-only and
complete all-solid executions regenerate all 25 images byte-for-byte. The larger
path's fixed start-target hand camera partly crops its end-state fingers too;
its numerical pair minima remain the evidence. Camera cropping is a diagnostic
limitation, not grounds to dismiss an intersection.
