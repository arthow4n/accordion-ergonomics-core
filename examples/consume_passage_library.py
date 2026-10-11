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
print("Replay in cwd", library.root, ":", library.reproduce_argv("passage-stepwise"))
# For a new bounded numerical search (then audit before physical acceptance):
# from accordion_ergonomics_core.research import discover_passage
# from accordion_ergonomics_core.passage_search import PassageSearchSettings
# record = discover_passage(passage, settings=PassageSearchSettings())
