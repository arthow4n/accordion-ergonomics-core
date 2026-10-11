"""Controlled trial records and full sampled whole-hand comparisons."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .movement_evidence import validate_strategy
from .muscles import (
    StaticScenario,
    conditional_static_screen,
    length_derivative_check,
    muscle_snapshot,
)
from .passage_media import independent_samples, search_diagram
from .provenance import compiled_model_digest, current_execution_metadata
from .quality_plots import trace_svg
from .scene import build_scene
from .strategy_audit import audit_states, plots


def run_selection_comparison(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    muscle_evidence = read_hashed(
        definition.parent / source["muscle_result"], source["muscle_sha256"]
    )
    output.mkdir(parents=True, exist_ok=True)
    trials: list[dict[str, Any]] = []
    scene = None
    for request in source["cases"]:
        saved = read_hashed(
            definition.parent / request["search_result"], request["search_sha256"]
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Comparison model differs from recorded search")
        search_diagram(saved, output / (request["id"] + "-search.svg"))
        strategies: list[dict[str, Any]] = []
        for strategy in saved["strategies"]:
            validate_strategy(saved, strategy)
            audit = audit_states(
                scene, e.geometry, strategy["samples"], saved["joint_names"]
            )
            independent = independent_samples(
                scene, strategy["samples"], e.solver.penetration_tolerance_m
            )
            plots(
                audit,
                output / (request["id"] + "-" + strategy["id"] + "-traces.svg"),
                request["id"] + " | " + strategy["id"] + " | actual untimed samples",
            )
            # Only static endpoints are screened here; not a path capacity certificate.
            screens = []
            for event_index, event in enumerate(strategy["events"]):
                snap = muscle_snapshot(scene, event["qpos_rad"])
                derivative = length_derivative_check(scene, event["qpos_rad"], 1e-6)
                for force in (0.0, 1.0, 3.0):
                    screen = conditional_static_screen(
                        scene,
                        e.geometry,
                        snap,
                        event["contacts"],
                        StaticScenario(force),
                    )
                    screen["event_index"] = event_index
                    screen["length_derivative_max_error_m_per_rad"] = derivative[
                        "maximum_error_m_per_rad"
                    ]
                    screen["eligible_for_muscle_ranking"] = (
                        screen["conditional_feasible"]
                        and derivative["maximum_error_m_per_rad"] <= 1e-7
                    )
                    screens.append(screen)
            strategies.append(
                dict(
                    id=strategy["id"],
                    status=strategy["status"],
                    contacts=[x["contacts"] for x in strategy["events"]],
                    whole_hand=audit,
                    independent_audit=independent,
                    static_endpoint_screens=screens,
                    muscle_path_evaluation="not_validated",
                )
            )
        trials.append(
            dict(
                source=request,
                settings=saved["settings"],
                budget=saved["budget"],
                status=saved["status"],
                selection_records=saved["selection_records"],
                strategies=strategies,
                first_note_approach="not_planned",
            )
        )
    if scene is None:
        raise ValueError("Comparison requires recorded trials")
    trace_svg(
        output / "consumed-budgets.svg",
        "Matched caps; actual consumed budgets differ",
        [
            dict(
                label="Actual calls/counts (not time)",
                series={
                    key: [t["budget"][key] for t in trials]
                    for key in (
                        "contact_solves",
                        "attempted_movement_edges",
                        "movement_waypoint_solves",
                    )
                },
            )
        ],
        x_axis="ordered independent trial index; not a movement",
    )
    completed = [t for t in trials if t["strategies"]]
    trace_svg(
        output / "selection-tradeoffs.svg",
        "Selected strategy-0: actual independent descriptors",
        [
            dict(
                label="Palm path (m)",
                series={
                    "palm": [
                        t["strategies"][0]["whole_hand"]["palm_path_m"]
                        for t in completed
                    ]
                },
            ),
            dict(
                label="Wrist total variation (rad), no effort interpretation",
                series={
                    n: [
                        t["strategies"][0]["whole_hand"]["joint_descriptors"][n][
                            "total_variation_rad"
                        ]
                        for t in completed
                    ]
                    for n in ("flexion_r", "deviation_r")
                },
            ),
            dict(
                label="Worst independently sampled cross-digit distance (m)",
                series={
                    "proxy": [
                        t["strategies"][0]["independent_audit"]["worst_cross_digit"][
                            "distance_m"
                        ]
                        for t in completed
                    ]
                },
            ),
        ],
        x_axis="ordered complete trial index; not a movement",
    )
    result = dict(
        id="selection-comparison-047",
        input=source,
        definition_sha256=hashlib.sha256(raw).hexdigest(),
        trials=trials,
        completed_plot_order=[t["source"]["id"] for t in completed],
        budget_plot_order=[t["source"]["id"] for t in trials],
        muscle_variant=dict(
            status="withheld_not_a_validated_path_rank",
            reason=(
                "046 route failures and conditional balance failures; "
                "endpoints do not validate a path"
            ),
            source_id=muscle_evidence["id"],
        ),
        artifact_sha256={
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.glob("*.svg")
        },
        **current_execution_metadata(scene.model),
    )
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    metadata = output / "execution.json"
    if metadata.exists():
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
    return result
