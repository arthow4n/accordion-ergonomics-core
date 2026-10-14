"""Read versioned wrist/coordination evidence from outside this checkout."""

import argparse
import json
from pathlib import Path

from accordion_ergonomics_core.research import ExerciseLibrary

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
args = parser.parse_args()
library = ExerciseLibrary(args.root)
case_id = "arpeggio-C-4309-strategy-0"
case = library.posture_case(case_id)
trajectory = library.posture_trajectory(case_id)
media = library.posture_media(case_id)
for name, summary in case["wrist"]["summary"].items():
    print(
        name,
        summary["minimum_rad"],
        summary["maximum_rad"],
        "reference departure",
        summary["maximum_reference_departure_rad"],
        "variation",
        summary["total_variation_rad"],
    )
print("reference", case["wrist"]["reference"])
print("saved samples", len(trajectory["samples"]))
print(
    "worst proxy distance", case["independent_audit"]["worst_cross_digit"]["distance_m"]
)
print("actual GIF", next(p for p in media["paths"] if p.suffix == ".gif"))
print("first approach", media["first_note_approach"])
muscle = json.loads(library.posture_evidence("muscle").read_text())
print("muscle ranking", muscle["muscle_ranking"])
print(
    "local operating subset",
    len(muscle["operating_quantity_subset"]["passed_tested_probes"]),
)
assert len(library.posture_record()["targets"]) == 50
assert (
    trajectory["samples"][0]["qpos_rad"] == media["animation"]["frames"][0]["qpos_rad"]
)
