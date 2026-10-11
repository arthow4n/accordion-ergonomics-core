"""Rerunnable multi-start experiments from recorded physical states."""

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .candidates import CandidateSettings, discover_candidates
from .cli import run_experiment
from .experiment import Experiment
from .instrument import button_at
from .scene import build_scene


def read_hashed(path: Path, expected: str) -> dict[str, Any]:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f"Recorded evidence changed: {path}")
    return json.loads(raw)


def run_exploration(
    definition: Path, output: Path, render: bool = True
) -> dict[str, Any]:
    raw_definition = definition.read_bytes()
    source = json.loads(raw_definition)
    render = render and source.get("render", True)
    baseline = read_hashed(
        definition.parent / source["baseline_result"], source["baseline_sha256"]
    )
    if baseline["status"] != "success":
        raise ValueError("Exploration needs an accepted recorded state")
    search: dict[str, Any] = dict(source["candidate_search"])
    search["offsets_rad"] = tuple(search["offsets_rad"])
    settings = CandidateSettings(**search)
    from .reachability import merge_parameters

    output.mkdir(parents=True, exist_ok=True)
    records = []
    for contact in source["targets"]:
        contacts = contact.get("contacts", [contact])
        button = button_at(contacts[0]["row"], contacts[0]["column"])
        target_id = contact.get("id", button.id)
        target_dir = output / target_id
        target_dir.mkdir(exist_ok=True)
        input_source = merge_parameters(
            Experiment.from_dict(baseline["input"]).expanded_source(),
            source.get("parameter_patch", {}),
        )
        input_source["id"] = source["id"] + "-" + target_id
        input_source["contacts"] = contacts
        input_source["initial_joints_rad"] = dict(
            zip(baseline["joint_names"], baseline["qpos_rad"], strict=True)
        )
        path = target_dir / "experiment.json"
        path.write_text(json.dumps(input_source, indent=2) + "\n")
        template = run_experiment(path, target_dir / "reference", False)
        experiment = Experiment.from_dict(input_source)
        scene = build_scene(
            experiment.geometry,
            experiment.player,
            experiment.setup,
            experiment.physical_contact,
            tuple(c.finger for c in experiment.contacts),
        )
        result = discover_candidates(
            scene,
            experiment,
            baseline["qpos_rad"],
            template["profiles_sha256"],
            settings,
        )
        result.update(
            button_id=button.id,
            target_id=target_id,
            midi=button.midi,
            resolved_profiles=template["resolved_profiles"],
            profiles_sha256=template["profiles_sha256"],
            provenance=template["provenance"],
            runtime=template["runtime"],
        )
        for index, candidate in enumerate(result["candidates"]):
            saved = dict(template)
            attempt = next(
                a for a in result["attempts"] if a["start_id"] == candidate["start_id"]
            )
            saved.update(attempt)
            candidate_dir = target_dir / f"candidate-{index}"
            candidate_dir.mkdir(exist_ok=True)
            scene.data.qpos[:] = candidate["state"]["joint_angles_rad"]
            if render:
                from .render import render_views

                saved["cameras"] = render_views(
                    scene,
                    candidate_dir / "renders",
                    template["target"]["surface_world_m"],
                    button.id,
                    collision_overlay=True,
                )
            (candidate_dir / "result.json").write_text(
                json.dumps(saved, indent=2, allow_nan=False) + "\n"
            )
        (target_dir / "discovery.json").write_text(
            json.dumps(result, indent=2, allow_nan=False) + "\n"
        )
        records.append(result)
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw_definition).hexdigest(),
        "baseline_state": baseline,
        "targets": records,
    }
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result


def run_planning(definition: Path, output: Path, render: bool = True) -> dict[str, Any]:

    from .planning import PlanningSettings, plan_transition
    from .provenance import compiled_model_digest, project_source_digest
    from .scene import diagnostics
    from .solver import accepted

    raw_definition = definition.read_bytes()
    source = json.loads(raw_definition)
    endpoints = [
        read_hashed(
            definition.parent / source[f"{key}_result"], source[f"{key}_sha256"]
        )
        for key in ("start", "end")
    ]
    start, end = endpoints
    e = Experiment.from_dict(start["input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    if start["joint_names"] != end["joint_names"]:
        raise ValueError("Endpoint coordinate orders differ")
    for endpoint in endpoints:
        other = Experiment.from_dict(endpoint["input"])
        if compiled_model_digest(
            build_scene(
                other.geometry, other.player, other.setup, other.physical_contact
            ).model
        ) != compiled_model_digest(scene.model):
            raise ValueError("Endpoint models differ")
        scene.data.qpos[:] = endpoint["qpos_rad"]
        if not accepted(
            diagnostics(
                scene,
                np.asarray(endpoint["target"]["surface_world_m"]),
                endpoint["target"]["button_id"],
            ),
            other.solver,
        ):
            raise ValueError("Recorded endpoint rejected under the composed model")
    options: dict[str, Any] = dict(source["planning"])
    options["withdrawal_depths_m"] = tuple(options["withdrawal_depths_m"])
    result = plan_transition(
        scene,
        e,
        start["qpos_rad"],
        end["qpos_rad"],
        end["target"]["button_id"],
        PlanningSettings(**options),
    )
    result.update(
        id=source["id"],
        input=source,
        definition_sha256=hashlib.sha256(raw_definition).hexdigest(),
        endpoints=endpoints,
        resolved_profiles=e.resolved_profiles(),
        profile_sha256=start.get("profiles_sha256"),
        provenance={
            **start["provenance"],
            "project_source_sha256": project_source_digest(),
            "compiled_model_sha256": compiled_model_digest(scene.model),
        },
        runtime=start["runtime"],
        contact_policy="Release source; establish destination; no held contacts",
    )
    output.mkdir(parents=True, exist_ok=True)
    if render and result["status"] == "sampled_path_found":
        from PIL import Image

        from .render import render_views

        frames = []
        samples = result["samples"]
        for index, fraction in enumerate(np.linspace(0, 1, 9)):
            sample = samples[round(fraction * (len(samples) - 1))]
            scene.data.qpos[:] = sample["qpos_rad"]
            directory = output / "renders" / f"frame-{index}"
            render_views(
                scene,
                directory,
                end["target"]["surface_world_m"],
                end["target"]["button_id"],
                collision_overlay=True,
            )
            frames.append(Image.open(directory / "collision.png").copy())
        frames[0].save(
            output / "trajectory.gif",
            save_all=True,
            append_images=frames[1:],
            duration=300,
            loop=0,
        )
        result["render_sampling"] = (
            "Nine sample indices; illustrative animation duration, not tempo"
        )
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
