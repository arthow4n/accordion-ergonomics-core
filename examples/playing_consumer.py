"""Run from any directory with uv --project /path/to/checkout; no remote service."""

import json
import sys
from pathlib import Path

from accordion_ergonomics_core.research import ExerciseLibrary

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
library = ExerciseLibrary(root)
summary = []
for ident in ("stepwise-coordinated-strategy-0", "arpeggio-region-strategy-0"):
    case = library.playing_case(ident)
    complete = library.playing_complete_trajectory(ident)
    media = library.playing_media(ident)
    search = library.playing_search(ident)
    summary.append(
        dict(
            case=ident,
            board_landmarks=list(case["region"]["landmarks"]),
            musical_samples=case["region"]["sample_count"],
            samples_from_numerical_seed=len(complete["samples"]),
            contact_lifecycle=[
                edge["lifecycle"] for edge in case["region"]["intervals"]
            ],
            palm_path_m=case["whole_hand"]["palm_path_m"],
            worst_unresolved_proxy_m=case["whole_hand"]["worst_proxy_m"],
            search_budget=search["budget"],
            detailed_playback=[
                str(p) for p in media["paths"] if p.name == "detailed.gif"
            ],
            human_feasibility=None,
        )
    )
print(json.dumps(summary, indent=2))
