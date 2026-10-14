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

## Versioned biomechanical evidence (045–048)

The historical manifest is unchanged. `targets/assessments-v1.json` links a
hash-bound `biomechanics-v1` sidecar for all 50 targets. Deep evidence covers the
fixed nine-case benchmark; other targets explicitly retain unassessed fields.
Static muscle results are conditional, and current screening does not support a
muscle effort ranking. There is no ordinary-playing or human-feasibility pass.

```python
from accordion_ergonomics_core.research import ExerciseLibrary

library = ExerciseLibrary()
quality = library.assessment("generated-dcbc77238f1b5559")
alternatives = library.ranked_comparisons(
    "generated-dcbc77238f1b5559", policy="proxy_first"
)
trajectory = library.comparison_trajectory("arpeggio-B-4309", "strategy-1")
frames = library.comparison_frame_sequence("arpeggio-B-4309", "strategy-1")
conditional_screens = library.muscle_screens("generated-dcbc77238f1b5559")
media_paths = library.quality_media("generated-dcbc77238f1b5559")
```

`proxy_first` and `wrist_first` use complete independently audited sample paths
and preserve Pareto tradeoffs. They are research preferences on uncalibrated
proxies, not universal comfort scores. The little-finger alternative remains
available. `quality_evidence("comparison")` or `quality_evidence("muscle")`
returns exact committed records including selection reasoning and assumptions.
`reproduce_quality_argv("arpeggio-B-4309", output)` retrieves the actual archived
media replay command; roles `assessment`, `seed`, `audit`, `muscle` and
`comparison` replay their matching workflows. Execute from the library root.

For new searches, `PassageSearchSettings` optionally supports
`selection_mode="whole_hand_pareto"`, `technique_prior="234_exploration"`,
`inactive_digits_policy="freeze"` and `unassigned_posture_multiplier`.
The defaults preserve historical selection. The technique prior only orders
exploration and retains all five fingers. Local posture multipliers are numerical
sensitivity parameters relative to the input q, not biological coupling laws.
Online proxy descriptors cover event endpoints; inspect the independent full
path before using them as movement diagnostics. A muscle selection mode is
explicitly unsupported while its validation/capacity gates remain unresolved.
New `discover_passage` results also include full sampled whole-hand audits and
resolved initial q. No initial approach is claimed unless separately recorded.

The [portable example](../examples/quality_consumer.py) is tested from a directory
outside this checkout. The [048 visual index](../experiments/048-library-reassessment/notes.md)
links exact static comparisons, actual-sample animations and algorithm plots.

## Wrist posture and coordination v2 (049–052)

The historical 50-target/53-realization catalog and `biomechanics-v1` interfaces
remain intact. A separately hash-bound `posture-coordination-v2` assessment adds
new complete strategies, model-reference-relative posture and explicit unknowns.

```python
from accordion_ergonomics_core.research import ExerciseLibrary

library = ExerciseLibrary()
assessment = library.posture_assessment("generated-dcbc77238f1b5559")
case = library.posture_case("arpeggio-C-4309-strategy-0")
path = library.posture_trajectory(case["id"])
media = library.posture_media(case["id"])
comparisons = library.posture_comparisons(assessment["target_id"])
```

`case["wrist"]` identifies the imported geometric reference/provenance and signed
coordinate extrema, event/sample values, limit margins and variation separately.
`whole_hand` and `independent_audit` expose full-path coordination, instrument and
uncalibrated cross-digit diagnostics for new candidates. `posture_evidence` returns
checked paths for historical wrist, coordination, muscle, selection, gallery,
budget-audit and canonical collision-coverage records. The muscle record identifies
the 59-actuator tested local subset and withheld effort ranking. Reference-choice
sensitivity, Pareto alternatives and separate rejected initial approaches are in
the selection record. Missing physical media and unassessed targets are explicit.

`posture_media` checks every returned artifact and provides exact static qpos,
cameras, active requirements and ordered frame/sample indices. A complete saved
musical path still has an unplanned first approach. Failed held nodes have no
trajectory; an approach diagnostic is not a successful performance. Illustrative
GIF playback does not establish tempo. No `safe`, `comfortable` or `human_feasible`
flag is added.

For newly submitted passages, select `PassageSearchSettings(selection_mode=
"wrist_posture_pareto")` to explore bounded reference-posture alternatives.
`discover_passage(..., final_selection_policy="posture")` then audits every complete
beam survivor and returns its policy preference and all alternatives. Available
final policies are `palm`, `movement`, `posture` and `whole_hand`. None re-solves
beam-pruned or budget-unexplored branches, and none establishes a human optimum.
The original call signature/default behavior remains available.

Run [the consumer](../examples/posture_consumer.py) from another working directory:

```sh
uv run --project /path/to/accordion-ergonomics-core python /path/to/accordion-ergonomics-core/examples/posture_consumer.py --root /path/to/accordion-ergonomics-core
```

[052 notes](../experiments/052-posture-selection/notes.md) and the matched physical
comparison galleries document why improved reference posture alone is insufficient.
