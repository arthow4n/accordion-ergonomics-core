"""Import with a local path dependency or submodule; no experiment browsing."""

from accordion_ergonomics_core.research import (
    ExerciseLibrary,
    NoteEvent,
    Passage,
    fingering_hypotheses,
)

library = ExerciseLibrary()
passage = Passage("consumer-step", (NoteEvent((60,)), NoteEvent((62,))))
choices = fingering_hypotheses(passage.events[0], seed=7)
print("First-event hypotheses:", len(choices))
print("Named digits:", sorted({h["contacts"][0]["finger"] for h in choices}))
trajectory = library.trajectory("passage-stepwise")
print("Recorded trajectory samples:", len(trajectory["samples"]))
print("Animations:", library.media("passage-stepwise"))
print(
    "Actual frame samples:",
    [f["sample_index"] for f in library.frame_sequence("passage-stepwise")],
)
print(
    "Anatomical validation:",
    library.diagnostics("passage-stepwise")["anatomical_validation"],
)
print("Generated exercises:", len(library.query(generated=True)))
print("Replay in cwd", library.root, ":", library.reproduce_argv("passage-stepwise"))
# For a new bounded numerical search with independent saved-state proxy audits:
# from accordion_ergonomics_core.research import discover_passage
# from accordion_ergonomics_core.passage_search import PassageSearchSettings
# record = discover_passage(passage, settings=PassageSearchSettings())
