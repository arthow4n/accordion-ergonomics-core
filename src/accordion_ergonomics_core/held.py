"""Small held-index / moving-middle kinematic experiment with independent audits."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np

from .domain import ContactRequirement, PlayingState
from .experiment import Experiment
from .exploration import read_hashed
from .planning import PlanningSettings, audit_path
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import Scene, build_scene, diagnostics
from .solver import accepted, solve_contact


def held_audit(
    scene: Scene,
    points: list[list[float]],
    e: Experiment,
    target: np.ndarray,
    button_id: str,
    max_step_rad: float,
) -> dict[str, Any]:
    audit = audit_path(
        scene, points, e, replace(PlanningSettings(), max_joint_step_rad=max_step_rad)
    )
    maximum_error = 0.0
    maximum_normal = 0.0
    maximum_gap = 0.0
    violations = []
    for index, sample in enumerate(audit["samples"]):
        scene.data.qpos[:] = sample["qpos_rad"]
        check = diagnostics(scene, target, button_id, "index")
        maximum_error = max(maximum_error, check["position_error_m"])
        maximum_normal = max(maximum_normal, check["normal_error_rad"])
        maximum_gap = max(maximum_gap, abs(check["target_contact_distance_m"]))
        if not accepted(check, e.solver):
            violations.append(index)
    audit.update(
        held_position_error_max_m=maximum_error,
        held_normal_error_max_rad=maximum_normal,
        held_contact_distance_max_m=maximum_gap,
        held_violation_sample_indices=violations,
        held_geometry_satisfied=not violations,
    )
    return audit


def run_held(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    start, end = [
        read_hashed(
            definition.parent / source[f"{key}_result"], source[f"{key}_sha256"]
        )
        for key in ("start", "end")
    ]
    if any(r["status"] != "success" for r in (start, end)):
        raise ValueError("Held experiment requires accepted gesture endpoints")
    e = Experiment.from_dict(start["input"])
    if [c.finger for c in e.contacts] != ["index", "middle"]:
        raise ValueError("This small experiment holds index while middle moves")
    scene = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "middle")
    )
    actual_model = compiled_model_digest(scene.model)
    if any(
        r["provenance"]["compiled_model_sha256"] != actual_model for r in (start, end)
    ):
        raise ValueError("Recorded gesture models differ from the composed model")
    held_target = np.asarray(start["targets"][0]["surface_world_m"])
    held_id = start["targets"][0]["button_id"]
    if end["targets"][0] != start["targets"][0]:
        raise ValueError("Index held requirements differ")
    q0 = start["qpos_rad"]
    q1 = end["qpos_rad"]
    direct = held_audit(
        scene, [q0, q1], e, held_target, held_id, source["max_joint_step_rad"]
    )
    normal = e.geometry.rotation[:, 2]
    departure = np.asarray(start["targets"][1]["surface_world_m"])
    arrival = np.asarray(end["targets"][1]["surface_world_m"])
    depth = source["withdrawal_m"]
    step = source["cartesian_step_m"]
    if not all(np.isfinite(v) and v > 0 for v in (depth, step)):
        raise ValueError("Withdrawal and waypoint steps must be finite positive metres")
    legs = [
        (departure, departure + normal * depth),
        (departure + normal * depth, arrival + normal * depth),
        (arrival + normal * depth, arrival),
    ]
    waypoints = [q0]
    solves = []
    failure = None
    names = start["joint_names"]
    moving_id = end["targets"][1]["button_id"]
    for leg, (a, b) in enumerate(legs):
        count = max(1, int(np.ceil(np.linalg.norm(b - a) / step)))
        for index, t in enumerate(np.linspace(0, 1, count + 1)[1:]):
            final = leg == 2 and index == count - 1
            solve = solve_contact(
                scene,
                held_target,
                dict(zip(names, waypoints[-1], strict=True)),
                replace(e.solver, max_iterations=source["waypoint_iterations"]),
                held_id,
                additional_contacts=((a + t * (b - a), "middle", moving_id),),
                additional_contact_required=final,
            )
            solves.append({"leg": leg, "leg_progress": float(t), "result": solve})
            if solve["status"] != "success":
                failure = "waypoint_solver_no_solution"
                break
            waypoints.append(solve["qpos_rad"])
        if failure:
            break
    searched = held_audit(
        scene, waypoints, e, held_target, held_id, source["max_joint_step_rad"]
    )
    found = (
        failure is None
        and searched["sampled_constraints_satisfied"]
        and searched["held_geometry_satisfied"]
    )
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "sampled_held_path_found" if found else "no_held_path_found",
        "physical_feasibility": None,
        "continuous_validity": None,
        "button_depression": None,
        "contact_policy": "Index geometry held; middle may release; force unmodeled",
        "direct_audit": direct,
        "searched_audit": searched,
        "waypoint_solves": solves,
        "waypoints_qpos_rad": waypoints,
        "failure": failure,
        "resolved_profiles": e.resolved_profiles(),
        **current_execution_metadata(scene.model),
        "source_execution_provenance": start["provenance"],
        "unvalidated": [
            "unsampled intervals",
            "holding force",
            "button travel",
            "complete self-collision",
            "human pose plausibility",
        ],
    }
    profile_hash = hashlib.sha256(
        json.dumps(e.resolved_profiles(), sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    contact_requirements = (ContactRequirement(held_id, "index"),)
    if found:
        contact_requirements += (ContactRequirement(moving_id, "middle"),)
    result["resulting_state"] = asdict(
        PlayingState(
            tuple(names), tuple(waypoints[-1]), profile_hash, contact_requirements
        )
    )
    output.mkdir(parents=True, exist_ok=True)
    if found:
        from .cli import run_experiment

        pose_source = e.expanded_source()
        pose_source["id"] = source["id"] + "-resulting-gesture"
        pose_source["contacts"] = end["input"]["contacts"]
        pose_source["initial_joints_rad"] = dict(zip(names, waypoints[-1], strict=True))
        path = output / "resulting-gesture.json"
        path.write_text(json.dumps(pose_source, indent=2) + "\n")
        pose = run_experiment(path, output / "resulting-gesture", False)
        if pose["status"] != "success":
            raise ValueError("Resulting gesture fails independent contact revalidation")
        result["resulting_gesture_result"] = "resulting-gesture/result.json"
        result["resulting_gesture_sha256"] = hashlib.sha256(
            (output / "resulting-gesture" / "result.json").read_bytes()
        ).hexdigest()

    for name, q in [("source", q0), ("last", waypoints[-1])]:
        scene.data.qpos[:] = q
        render_views(
            scene,
            output / "renders" / name,
            held_target.tolist(),
            held_id,
            collision_overlay=True,
        )
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
