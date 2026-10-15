# 055 — Bounded region-aware and coordinated planning comparisons

[Open the matched visual comparison](../../targets/VISUALS.md#what-changed-recently).
Eight searches use **the identical frozen package source** (974fd79c41cf…), the
same compiled anatomy/instrument, solved numerical seed, passage, seeded assignment
ordering, beam width 2, four assignments per parent, contact limits and per-edge
planning caps. All five fingers remain eligible. Only selection mode and soft body
guidance differ. Complete consumed budgets, rejected and unexplored assignments
are retained; equal caps do not imply equal numerical work or branch selection.

- Historical: existing palm-cost beam and movement planner.
- Region: lexicographic maximum cap-relative palm normal offset, planar task
  offset, then travel. This is a descriptive exploration preference, not a
  calibrated admissible playing region. Accumulation uses every saved edge sample.
- Coordinated: soft capitate translation follows the mean requested planar pad
  displacement while retaining initial normal depth during each local solve,
  cost 0.05 (a numerical hypothesis). Named-finger continuation carries this
  guidance into waypoint solves. Orientation remains free. It changes contact
  optimization and the applicable continuation route, not just final ranking.
- Combined: both modifications, with every alternative preserved.

The following are the initially retained strategy-0 paths; strategy-1 alternatives
are equally retained in the full assessments. Normal positions are relative to
the base plane, not palm skin clearance. Overlap is unresolved phalangeal proxy
intersection. Wrist movement is absolute joint-coordinate total variation, not
reference posture, speed or effort.

| Recorded path | Palm mm | Palm n min–max mm | Worst overlap mm | Wrist variation rad | Contact solves | Waypoint solves |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stepwise-historical | 52.27 | 65.15–83.65 | 8.723 | 0.1084 | 20 | 44 |
| stepwise-region | 79.45 | 5.43–69.81 | 9.156 | 1.2823 | 20 | 36 |
| stepwise-coordinated | 57.42 | 68.93–70.95 | 3.576 | 0.6448 | 20 | 67 |
| stepwise-combined | 85.98 | 51.32–58.93 | 8.971 | 1.7910 | 20 | 74 |
| arpeggio-historical | 121.68 | 53.42–76.79 | 8.830 | 0.4877 | 28 | 76 |
| arpeggio-region | 136.29 | 22.55–67.51 | 3.118 | 1.7408 | 28 | 60 |
| arpeggio-combined | 124.48 | 50.36–57.36 | 8.855 | 1.2742 | 28 | 152 |
| arpeggio-coordinated | 143.65 | 69.26–71.61 | 13.789 | 0.5863 | 28 | 88 |

Stepwise coordinated strategy 0 changes little–little–little to
index–index–index on different actual duplicate buttons. Normal span falls
18.50→2.01 mm and worst overlap 8.723→3.576 mm, with travel 52.27→57.42 mm and
wrist variation 0.1084→0.6448 rad. Arpeggio region strategy 0 changes the finger
and physical-button branch: normal maximum falls 76.79→67.51 mm and worst overlap
8.830→3.118 mm; travel rises 121.68→136.29 mm and wrist variation rises
0.4877→1.7408 rad. These are actual model changes, not universal ergonomic wins.

[Stepwise equivalent musical events](evidence/stepwise-before-after-events.png),
[common paths](evidence/stepwise-before-after.png),
[baseline dense](evidence/stepwise-historical-strategy-0/detailed.gif),
[coordinated dense](evidence/stepwise-coordinated-strategy-0/detailed.gif).
[Arpeggio equivalent events](evidence/arpeggio-before-after-events.png),
[common paths](evidence/arpeggio-before-after.png),
[baseline dense](evidence/arpeggio-historical-strategy-0/detailed.gif),
[region dense](evidence/arpeggio-region-strategy-0/detailed.gif).
Both have scientific keyframe GIFs beside detailed playback, actual search graphs,
event/contact timelines, full joint traces, context/keyboard/hand/side and worst
proxy views. All four compared dense movies use the same cameras and identical
board-coordinate bounds derived from their actual points. Event panels compare
musical boundaries, not equal time. Dense movies use 50–52 saved samples including
events, releases and extrema. No display interpolation creates states.

Combined paths reduce normal excursions but push wrist coordinates very near
imported limits and may worsen overlap. Coordinated arpeggio holds normal depth
but worsens overlap to 13.789 mm and increases travel. Region stepwise can bring
the capitate origin to 5.43 mm normal position, with much more wrist compensation;
there is no calibrated palm envelope proving that this is ordinary playing.
None is promoted to the default. Historical behavior remains available.

All 16 retained complete paths satisfy independently queried configured/instrument
proxy checks at every saved sample and show old-cap geometric separation. All
retain unresolved cross-digit overlaps. Unassigned cap proximity cannot establish
actuation. Independent worst-state coverage is in
[056](../056-physical-integrity/coverage/result.json). The absent first-note approach
is evaluated separately, not silently added to musical cost.

A real implementation defect surfaced under guided solving: endpoint arithmetic
`a + 1*(b-a)` can differ by floating-point bits from the recorded endpoint and
break exact graph joins. The fix preserves original endpoint arrays. Two original
crashes, rerunnable inputs and source archives remain in [failures](failures/stepwise.json).
They are programming failures, not failed human movements. New historical controls retain the same assignments and sample counts.
Subsequent local solves amplify endpoint rounding up to 5.52e-7 rad in one
alternative (below the existing 1e-6 rad equality acceptance scale); this is
numerical sensitivity, not byte-identical historical replay. See
[the sensitivity record](historical-sensitivity.json). Policy effects use the
matched new-source baselines. Historical files remain untouched and replay with
their own archives.

Inspected: both equivalent-event panels, dense initial/intermediate/final physical
frames and synchronized paths, common top/side diagrams, all four diagnostic views
and worst-proxy overlays, including the less-overlapped but still unresolved
arpeggio region path. Numerical audits and precise camera/frame/qpos identities:
[stepwise all alternatives](stepwise-audit/result.json),
[arpeggio all alternatives](arpeggio-audit/result.json),
[matched media manifest](evidence/result.json). The algorithm explanation uses the
actual node/edge graphs and budgets, never an invented decision process.

```sh
uv run aec frozen passage experiments/055-coordinated-planning/stepwise-coordinated.json --source-snapshot experiments/055-coordinated-planning/stepwise-coordinated/source-snapshot.zip --output artifacts/055-search-replay
uv run aec frozen playing-study experiments/055-coordinated-planning/matched.json --source-snapshot experiments/055-coordinated-planning/evidence/source-snapshot.zip --output artifacts/055-media-replay
```

Full batch tests, frozen integrity and archived render replay are reported in 057.
