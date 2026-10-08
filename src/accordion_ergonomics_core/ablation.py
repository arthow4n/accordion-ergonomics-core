"""Rerunnable finger-only versus whole-arm endpoint ablation.

This explores candidate configurations, never infers a valid path or a minimum
movement, and retains failed cases as evidence rather than hiding them.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .cli import run_experiment
from .experiment import Experiment
from .instrument import button_at

ARM_INDEPENDENT_JOINTS = (
    "elv_angle_r",
    "shoulder_elv_r",
    "shoulder_rot_r",
    "elbow_flexion_r",
    "pro_sup_r",
    "deviation_r",
    "flexion_r",
)


def run_ablation(definition: Path, output: Path) -> dict[str, Any]:
    source = json.loads(definition.read_text())
    if source["schema_version"] != 1:
        raise ValueError("Unsupported ablation schema")
    base_path = definition.parent / source["base_result"]
    base_bytes = base_path.read_bytes()
    if hashlib.sha256(base_bytes).hexdigest() != source["base_result_sha256"]:
        raise ValueError("Ablation starting-state record changed")
    base = json.loads(base_bytes)
    if base["status"] != "success":
        raise ValueError("Ablation requires an accepted starting candidate")
    initial = dict(zip(base["joint_names"], base["qpos_rad"], strict=True))
    geometry = Experiment.from_dict(base["input"]).geometry
    base_button = base["input"]["contacts"][0]
    palm_start = np.asarray(base["diagnostics"]["palm_world_m"])
    cases = []
    for request in source["targets"]:
        button = button_at(request["row"], request["column"])
        for mode, frozen in (
            ("finger-only", ARM_INDEPENDENT_JOINTS),
            ("arm-enabled", ()),
        ):
            case_id = f"{button.id}-{mode}"
            case_dir = output / case_id
            case_dir.mkdir(parents=True, exist_ok=True)
            case_input = dict(base["input"])
            case_input.update(
                {
                    "id": f"{source['id']}/{case_id}",
                    "question": source["question"],
                    "initial_joints_rad": initial,
                    "frozen_joints": list(frozen),
                    "contacts": [
                        {"row": button.row, "column": button.column, "finger": "index"}
                    ],
                    "starting_state": {
                        "source_sha256": source["base_result_sha256"],
                        "contact_preservation_required": False,
                    },
                }
            )
            input_path = case_dir / "experiment.json"
            input_path.write_text(json.dumps(case_input, indent=2) + "\n")
            result = run_experiment(input_path, case_dir, render=True)
            d = result["diagnostics"]
            delta = np.asarray(result["qpos_rad"]) - np.asarray(base["qpos_rad"])
            palm_delta = np.asarray(d["palm_world_m"]) - palm_start
            baseline_point = geometry.surface_world_m(
                button_at(base_button["row"], base_button["column"])
            )
            cases.append(
                {
                    "case_id": case_id,
                    "status": result["status"],
                    "feasible": None,
                    "result": f"{case_id}/result.json",
                    "button": button.id,
                    "midi": button.midi,
                    "target_displacement_m": float(
                        np.linalg.norm(
                            geometry.surface_world_m(button) - baseline_point
                        )
                    ),
                    "grid_heuristic": {
                        "provenance": "Arbitrary companion distance terms; heuristic",
                        "formula": "4*abs(delta_column)+1.5*abs(delta_row)",
                        "value": 4 * abs(button.column - base_button["column"])
                        + 1.5 * abs(button.row - base_button["row"]),
                    },
                    "candidate_palm_displacement_m": float(np.linalg.norm(palm_delta)),
                    "candidate_palm_delta_world_m": palm_delta.tolist(),
                    "joint_delta_rad": dict(
                        zip(base["joint_names"], delta.tolist(), strict=True)
                    ),
                    "joint_margins_rad": d["joint_margins_rad"],
                    "position_error_m": d["position_error_m"],
                    "max_penetration_m": d["max_penetration_m"],
                    "claim": (
                        "Endpoint candidate; local failure does not prove impossibility"
                    ),
                }
            )
    summary = {
        "schema_version": 1,
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(definition.read_bytes()).hexdigest(),
        "cases": cases,
        "trajectory_validated": False,
        "conclusion": (
            "Joint margins and palm movement depend on articulated state; "
            "these fixture results do not establish human ergonomic preference"
        ),
    }
    (output / "result.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n"
    )
    return summary
