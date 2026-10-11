"""Use the internal library from another working directory; no experiment browsing."""

import json
from pathlib import Path

from accordion_ergonomics_core.research import ExerciseLibrary

library = ExerciseLibrary()
target = "generated-dcbc77238f1b5559"
rankings = library.ranked_comparisons(target, policy="proxy_first")
selected = next(t for t in rankings if t["trial_id"] == "arpeggio-B-4309")["ranking"][0]
trajectory = library.comparison_trajectory("arpeggio-B-4309", selected["id"])
frames = library.comparison_frame_sequence("arpeggio-B-4309", selected["id"])
assessment = library.assessment(target)
print(
    json.dumps(
        {
            "target_id": target,
            "assessment_version": assessment["assessment_version"],
            "selected_strategy": selected["id"],
            "policy": selected["policy"],
            "descriptors": selected["descriptors"],
            "sample_count": len(trajectory["samples"]),
            "saved_frame_count": len(frames),
            "initial_approach": trajectory["first_note_approach"],
            "muscle_pose_records": len(library.muscle_screens(target)),
            "human_feasibility": assessment["human_feasibility"],
            "media_replay_argv": library.reproduce_quality_argv(
                "arpeggio-B-4309", Path("quality-media-replay")
            ),
        },
        indent=2,
    )
)
