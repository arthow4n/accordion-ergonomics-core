# Internal Python consumer API

Use the checkout as an editable local path dependency, or import its `src` from
a Git submodule. Keep the repository evidence alongside the package. The locked
research environment is installed with `uv sync --locked`; no publication,
release workflow or service is required. An explicit `ExerciseLibrary(root)`
supports another checkout location. Numerical entry points also accept `root`.

```python
from pathlib import Path
from accordion_ergonomics_core.research import (
    ExerciseLibrary,
    Passage,
    NoteEvent,
    fingering_hypotheses,
    discover_passage,
    generate_challenges,
    discover_challenges,
)
from accordion_ergonomics_core.passage_search import PassageSearchSettings
from accordion_ergonomics_core.planning import PlanningSettings

library = ExerciseLibrary()
targets = library.query(generated=True, finger="little")
target = library.target("passage-stepwise")
search = library.search_record(target["id"])
strategy_id = search["strategies"][0]["id"]
path = library.trajectory(target["id"], strategy_id)
audit = library.diagnostics(target["id"], strategy_id)
frames = library.frame_sequence(target["id"], strategy_id)
gifs = library.media(target["id"], role="animation")
# frames contain actual sample indices, qpos, requirements, hashes and PNG Paths.

passage = Passage("consumer-repeat", (NoteEvent((60,)), NoteEvent((60,))))
choices = fingering_hypotheses(passage.events[0], seed=7)
# Hypotheses include all five digits and finite duplicate-row buttons, without IK.
settings = PassageSearchSettings(
    beam_width=1,
    assignments_per_parent=1,
    fingers=("index",),
    prepare_next=False,
    assignment_order="marker_distance",
    contact_iterations=120,
    planning=PlanningSettings(
        withdrawal_depths_m=(0.01,),
        max_joint_step_rad=0.01,
        waypoint_iterations=120,
        rrt_iterations=0,
        waypoint_solve_limit=12,
    ),
)
result = discover_passage(passage, settings=settings)
# Includes independent_strategy_audits over each complete strategy's actual states.
# Optional output=Path("new-evidence") saves search, static views and actual-path GIFs.
# Failed searches and one-event static poses produce no successful movement GIF.

hypotheses = generate_challenges()  # Seeded grammar; not physical results.
# Costlier bounded evaluation, with independent diagnostics and observed allocation:
# discovered = discover_challenges(Path("new-discovery"))

# Earlier generated trials are distinct evidence, not silently replaced:
arpeggio = library.query(family="arpeggio", generated=True)[0]
earlier = library.trajectory(arpeggio["id"], trial_id="evaluation-03")
earlier_audit = library.diagnostics(arpeggio["id"], trial_id="evaluation-03")

# Executes archived source and unchanged definitions into an empty directory:
# library.reproduce("passage-stepwise", Path("new-render-replay"))
# Set media=False to rerun numerical search instead; resource cost is much greater.
```

Strategy IDs come from `search_record` or a realization's
`movement_attempts[].selector.strategy_id`; stable catalog realization IDs are
separate identities. Generated `search_trials` expose both original and follow-up
records. Diagnostics are linked by the exact state-sequence hash. Missing
strategies, audits or media raise errors, and hash mismatches cannot silently
produce accepted frames. Single-event contact is static evidence, not movement.

A `NoteEvent` accepts simultaneous MIDI pitches and optional `hold_to_next`
pitches. Held bindings retain both physical button and named digit; repeated
unheld presses of the same cap require computed release. All five digits remain
eligible by default; the small control above deliberately restricts assignment
to index for a fast consumer test. Unassigned digits still articulate. Contact,
movement and independent diagnostic acceptance remain separate statuses.

`discover_passage` returns actual search nodes, attempted edges, budgets and
complete sampled paths where found. `discover_challenges` saves every evaluated
trial, generation choices and selection evidence. These direct calls document
the current execution identity. For long runs during source editing, use
`uv run aec frozen passage DEFINITION --output DIRECTORY` or the frozen
`discovery` workflow; direct calls do not archive concurrently changing source.
`library.reproduce` invokes the original frozen workflow and source snapshot.
It refuses a nonempty output directory. Runtime graphics versions may change
image bytes; actual state, camera, sample and source identities remain inspectable.

The [tested consumer example](../examples/consume_passage_library.py) works from
outside the repository. Tests also submit an actual new passage from another
working directory. The [visual index](VISUALS.md) and
[044 replay report](../experiments/044-internal-library/validation/result.json)
link media to exact computational evidence. Proxy overlap, finite failures,
unsampled intervals, forces, timing and human feasibility remain unresolved.
