"""Select demanding realizations by discovered physical movement."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import numpy as np

from .domain import ContactRequirement, PhysicalAction, Trajectory
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import buttons
from .planning import PlanningSettings, audit_path
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import build_scene, diagnostics
from .solver import accepted


def run_exercise(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    atlas_path = definition.parent / source["atlas_result"]
    atlas = read_hashed(atlas_path, source["atlas_sha256"])
    anchor = atlas["anchor"]
    e = Experiment.from_dict(anchor["input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    if (
        compiled_model_digest(scene.model)
        != anchor["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Atlas model changed; explicitly recalculate the action space")
    profiles = e.resolved_profiles()
    profile_hash = hashlib.sha256(
        json.dumps(profiles, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    candidates = sorted(
        (a for a in atlas["actions"] if a["best_discovered_relocation_m"] is not None),
        key=lambda a: a["best_discovered_relocation_m"],
        reverse=True,
    )
    attempts = []
    selected = None
    for action in candidates:
        evidence = read_hashed(
            atlas_path.parent / action["evidence"], action["evidence_sha256"]
        )
        realized = sorted(
            (
                p
                for p in evidence["realizations"]
                if p["trajectory"]["status"] == "sampled_path_found"
            ),
            key=lambda p: p["endpoint_relocation_m"],
        )
        for realization in realized:
            path = realization["trajectory"]
            waypoints = path.get(
                "waypoints_qpos_rad",
                [path["samples"][0]["qpos_rad"], path["samples"][-1]["qpos_rad"]],
            )
            settings = replace(
                PlanningSettings(), max_joint_step_rad=source["fine_audit_step_rad"]
            )
            audit = audit_path(scene, waypoints, e, settings)
            attempts.append(
                {
                    "button_id": action["button_id"],
                    "start_id": realization["start_id"],
                    "fine_sampled_constraints_satisfied": audit[
                        "sampled_constraints_satisfied"
                    ],
                    "maximum_penetration_m": audit["maximum_penetration_m"],
                }
            )
            if audit["sampled_constraints_satisfied"]:
                selected = (action, evidence, realization, waypoints, audit)
                break
        if selected:
            break
    output.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "attempts": attempts,
        "status": "no_refined_candidate_found",
        "human_feasibility": None,
    }
    if selected:
        action, evidence, realization, waypoints, audit = selected
        state = realization["resulting_state"]
        event = PhysicalAction(
            action["button_id"],
            action["finger"],
            profile_hash,
            (ContactRequirement(anchor["target"]["button_id"], "index"),),
        )
        trajectory = Trajectory(
            tuple(anchor["joint_names"]),
            tuple(tuple(q) for q in waypoints),
            profile_hash,
            source["fine_audit_step_rad"],
        )
        result.update(
            status="sampled_model_exercise_found",
            action=asdict(event),
            trajectory=asdict(trajectory),
            audit=audit,
            endpoint_descriptors=realization["descriptors"],
            selected_endpoint_relocation_m=realization["endpoint_relocation_m"],
            selected_evidence_sha256=action["evidence_sha256"],
            selection="Largest discovered endpoint relocation; no global minimum claim",
            **current_execution_metadata(scene.model),
            atlas_execution_provenance=anchor["provenance"],
            resolved_profiles=profiles,
        )
        q = np.asarray([s["qpos_rad"] for s in audit["samples"]])
        result["joint_excursions_rad"] = {
            name: float(q[:, i].max() - q[:, i].min())
            for i, name in enumerate(anchor["joint_names"])
        }
        result["musical_events"] = [
            {
                "midi": anchor["target"]["midi"],
                "button_id": anchor["target"]["button_id"],
                "finger": "index",
                "event": "surface_contact",
            },
            {
                "midi": action["midi"],
                "button_id": action["button_id"],
                "finger": action["finger"],
                "event": "surface_contact",
            },
        ]
        target = scene.data.site(f"target_{action['button_id']}").xpos.copy()
        saved = dict(anchor)
        saved["qpos_rad"] = state["joint_angles_rad"]
        saved["input"] = json.loads(json.dumps(anchor["input"]))
        button = next(b for b in buttons() if b.id == action["button_id"])
        saved["input"] = e.expanded_source()
        saved["input"]["id"] = source["id"] + "-endpoint"
        saved["input"]["contacts"] = [
            {"row": button.row, "column": button.column, "finger": action["finger"]}
        ]
        saved["input"]["initial_joints_rad"] = dict(
            zip(anchor["joint_names"], state["joint_angles_rad"], strict=True)
        )
        saved["experiment_id"] = saved["input"]["id"]
        input_bytes = (
            json.dumps(saved["input"], indent=2, allow_nan=False) + "\n"
        ).encode()
        (output / "endpoint-input.json").write_bytes(input_bytes)
        saved["input_sha256"] = hashlib.sha256(input_bytes).hexdigest()
        scene.data.qpos[:] = state["joint_angles_rad"]
        saved["diagnostics"] = diagnostics(scene, target, action["button_id"])
        if not accepted(saved["diagnostics"], e.solver):
            raise ValueError("Selected endpoint no longer passes contact checks")
        saved["claim"] = "Accepted endpoint derived from a recorded atlas realization"
        saved["source_qpos_rad"] = anchor["qpos_rad"]
        saved["initial_qpos_rad"] = list(state["joint_angles_rad"])
        saved["termination_reason"] = "independently_validated_derived_endpoint"
        saved.pop("solver_history", None)
        saved["profiles_sha256"] = profile_hash
        saved["resolved_profiles"] = profiles
        saved.update(current_execution_metadata(scene.model))
        saved["source_execution_provenance"] = anchor["provenance"]

        saved["target"] = {
            "button_id": action["button_id"],
            "midi": action["midi"],
            "surface_world_m": target.tolist(),
            "normal_world": e.geometry.rotation[:, 2].tolist(),
        }
        saved["targets"] = [{**saved["target"], "finger": action["finger"]}]
        saved["derived_from_atlas_action"] = action["evidence_sha256"]
        (output / "endpoint.json").write_text(
            json.dumps(saved, indent=2, allow_nan=False) + "\n"
        )
        result["cameras"] = {}
        for name, index in [
            ("source", 0),
            ("middle", len(audit["samples"]) // 2),
            ("destination", len(audit["samples"]) - 1),
        ]:
            scene.data.qpos[:] = audit["samples"][index]["qpos_rad"]
            result["cameras"][name] = render_views(
                scene,
                output / "renders" / name,
                target.tolist(),
                action["button_id"],
                collision_overlay=True,
            )
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
