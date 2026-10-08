"""Finite next-action search; failure is not proof of impossibility."""

import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path
from time import perf_counter
from typing import Any

from PIL import Image, ImageDraw

from .candidates import CandidateSettings, discover_candidates
from .cli import run_experiment
from .domain import PlayingState
from .experiment import ContactRequest, Experiment
from .exploration import read_hashed
from .instrument import button_at, buttons
from .planning import PlanningSettings, plan_transition
from .scene import Scene, build_scene


def reachable_actions(
    state: PlayingState,
    scene: Scene,
    experiment: Experiment,
    requests: tuple[ContactRequest, ...],
    candidate_settings: CandidateSettings,
    planning_settings: PlanningSettings,
    output: Path,
) -> list[dict[str, Any]]:
    """Keep discovered endpoint alternatives and independently searched paths."""
    names = tuple(scene.model.joint(i).name for i in range(scene.model.njnt))
    expected = hashlib.sha256(
        json.dumps(
            experiment.resolved_profiles(), sort_keys=True, allow_nan=False
        ).encode()
    ).hexdigest()
    if expected != state.profile_sha256:
        raise ValueError("State parameter profile differs; recalibrate the anchor")
    if names != state.joint_names:
        raise ValueError("State coordinate names do not match player model")
    output.mkdir(parents=True, exist_ok=True)
    actions = []
    for request in requests:
        button = button_at(request.row, request.column)
        e = replace(experiment, contacts=(request,))
        discovery = discover_candidates(
            scene,
            e,
            list(state.joint_angles_rad),
            state.profile_sha256,
            candidate_settings,
        )
        paths = []
        for candidate in sorted(
            discovery["candidates"], key=lambda c: c["relocation_m"]
        ):
            path = plan_transition(
                scene,
                e,
                list(state.joint_angles_rad),
                candidate["state"]["joint_angles_rad"],
                button.id,
                planning_settings,
            )
            paths.append(
                {
                    "start_id": candidate["start_id"],
                    "endpoint_relocation_m": candidate["relocation_m"],
                    "trajectory": path,
                    "resulting_state": candidate["state"],
                    "descriptors": candidate["descriptors"],
                }
            )
        found = [p for p in paths if p["trajectory"]["status"] == "sampled_path_found"]
        action = {
            "button_id": button.id,
            "midi": button.midi,
            "finger": request.finger,
            "status": "sampled_transition_found"
            if found
            else "no_transition_found"
            if paths
            else "no_pose_found",
            "physical_feasibility": None,
            "discovery": discovery,
            "realizations": paths,
            "best_discovered_relocation_m": min(
                (p["endpoint_relocation_m"] for p in found), default=None
            ),
            "contacts_allowed_to_release": state.contacts,
            "required_preserved_contacts": [],
            "claim": "Finite rigid-proxy search; human feasibility unknown",
        }
        (output / f"{button.id}-{request.finger}.json").write_text(
            json.dumps(action, indent=2, allow_nan=False) + "\n"
        )
        actions.append(action)
        print(
            json.dumps(
                {
                    "button": button.id,
                    "status": action["status"],
                    "candidates": len(paths),
                }
            ),
            flush=True,
        )
    return actions


def merge_parameters(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Strict nested profile replacement; misspelled paths cannot silently disappear."""
    result = json.loads(json.dumps(base))
    for key, value in patch.items():
        if key not in result:
            raise ValueError(f"Unknown parameter path: {key}")
        if key == "joint_ranges_rad":
            result[key] = {**result[key], **value}
        elif isinstance(value, dict) and isinstance(result[key], dict):
            result[key] = merge_parameters(result[key], value)
        else:
            result[key] = value
    return result


def render_atlas(result: dict[str, Any], output: Path) -> None:
    """Metric board diagram: continuous relocation and missing-search outcomes."""
    e = Experiment.from_dict(result["anchor"]["input"])
    centers = {b.id: e.geometry.center_board_m(b) for b in buttons()}
    actions = {a["button_id"]: a for a in result["actions"]}
    image = Image.new("RGB", (780, 1000), (245, 247, 250))
    draw = ImageDraw.Draw(image)
    draw.text((25, 20), result["id"], fill=(20, 25, 35))
    draw.text(
        (25, 45),
        "Index next actions: best discovered palm relocation (mm)",
        fill=(20, 25, 35),
    )
    draw.text(
        (25, 65),
        "Circle size/blue intensity: relocation; X: search found no path/pose",
        fill=(20, 25, 35),
    )
    max_value = max(
        [a["best_discovered_relocation_m"] or 0 for a in result["actions"]] + [0.001]
    )
    u = [c[0] for c in centers.values()]
    v = [c[1] for c in centers.values()]
    span = max(v) - min(v)
    scale = 760 / span
    for button, center in centers.items():
        x = 400 + (center[0] - (min(u) + max(u)) / 2) * scale
        y = 150 + (center[1] - min(v)) * scale
        action = actions.get(button)
        value = action["best_discovered_relocation_m"] if action else None
        color = (
            (190, 195, 200)
            if value is None
            else (
                int(220 - 180 * value / max_value),
                int(235 - 145 * value / max_value),
                230,
            )
        )
        radius = 15 if value is None else 12 + 12 * value / max_value
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=color,
            outline=(45, 50, 60),
            width=1,
        )
        label = (
            "?" if not action else "X" if value is None else str(round(value * 1000))
        )
        draw.text((x - 7, y - 5), label, fill=(10, 20, 30))
        draw.text((x - 18, y + 26), button, fill=(45, 50, 60))
        if button == result["anchor"]["target"]["button_id"]:
            draw.ellipse(
                (x - radius - 3, y - radius - 3, x + radius + 3, y + radius + 3),
                outline=(230, 130, 15),
                width=2,
            )
    draw.text(
        (25, 970),
        f"Max relocation {max_value * 1000:.1f} mm; sampled checks; no comfort score.",
        fill=(20, 25, 35),
    )
    image.save(output)


def run_atlas(definition: Path, output: Path) -> dict[str, Any]:
    began = perf_counter()
    raw_definition = definition.read_bytes()
    source = json.loads(raw_definition)
    baseline = read_hashed(
        definition.parent / source["baseline_result"], source["baseline_sha256"]
    )
    input_source = merge_parameters(
        Experiment.from_dict(baseline["input"]).expanded_source(),
        source.get("parameter_patch", {}),
    )
    input_source["id"] = source["id"] + "-anchor"
    input_source["initial_joints_rad"] = dict(
        zip(baseline["joint_names"], baseline["qpos_rad"], strict=True)
    )
    output.mkdir(parents=True, exist_ok=True)
    anchor_input = output / "anchor.json"
    anchor_input.write_text(json.dumps(input_source, indent=2) + "\n")
    # Changing the physical world requires re-solving the source contact as well.
    anchor = run_experiment(anchor_input, output / "anchor", False)
    anchor_search = None
    if anchor["status"] != "success":
        e = Experiment.from_dict(input_source)
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
        search: dict[str, Any] = dict(source["candidate_search"])
        search["offsets_rad"] = tuple(search["offsets_rad"])
        anchor_search = discover_candidates(
            scene,
            e,
            baseline["qpos_rad"],
            anchor["profiles_sha256"],
            CandidateSettings(**search),
        )
        (output / "anchor-search.json").write_text(
            json.dumps(anchor_search, indent=2, allow_nan=False) + "\n"
        )
        if anchor_search["candidates"]:
            selected = min(anchor_search["candidates"], key=lambda c: c["relocation_m"])
            input_source["initial_joints_rad"] = dict(
                zip(
                    baseline["joint_names"],
                    selected["state"]["joint_angles_rad"],
                    strict=True,
                )
            )
            anchor_input.write_text(json.dumps(input_source, indent=2) + "\n")
            anchor = run_experiment(anchor_input, output / "anchor", False)
    result: dict[str, Any] = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw_definition).hexdigest(),
        "anchor": anchor,
        "anchor_search": anchor_search,
        "actions": [],
        "parameter_patch": source.get("parameter_patch", {}),
        "elapsed_s": 0.0,
        "status": "no_anchor_solution"
        if anchor["status"] != "success"
        else "completed_search",
    }
    if anchor["status"] == "success":
        e = Experiment.from_dict(input_source)
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
        candidate_options: dict[str, Any] = dict(source["candidate_search"])
        candidate_options["offsets_rad"] = tuple(candidate_options["offsets_rad"])
        planning_options: dict[str, Any] = dict(source["planning"])
        planning_options["withdrawal_depths_m"] = tuple(
            planning_options["withdrawal_depths_m"]
        )
        requests = (
            tuple(ContactRequest(b.row, b.column, "index") for b in buttons())
            if source["targets"] == "all-index"
            else tuple(ContactRequest(**c) for c in source["targets"])
        )
        state = PlayingState(
            tuple(anchor["joint_names"]),
            tuple(anchor["qpos_rad"]),
            anchor["profiles_sha256"],
            (anchor["target"]["button_id"],),
        )
        result["state"] = asdict(state)
        result["actions"] = reachable_actions(
            state,
            scene,
            e,
            requests,
            CandidateSettings(**candidate_options),
            PlanningSettings(**planning_options),
            output / "actions",
        )
        result["actions"] = [
            {
                **{
                    k: v
                    for k, v in action.items()
                    if k not in ("discovery", "realizations")
                },
                "evidence": f"actions/{action['button_id']}-{action['finger']}.json",
                "evidence_sha256": hashlib.sha256(
                    (
                        output
                        / "actions"
                        / f"{action['button_id']}-{action['finger']}.json"
                    ).read_bytes()
                ).hexdigest(),
            }
            for action in result["actions"]
        ]
        result["summary"] = {
            "buttons_explored": len(result["actions"]),
            "sampled_transition_found": sum(
                a["status"] == "sampled_transition_found" for a in result["actions"]
            ),
            "no_pose_found": sum(
                a["status"] == "no_pose_found" for a in result["actions"]
            ),
            "no_transition_found": sum(
                a["status"] == "no_transition_found" for a in result["actions"]
            ),
        }
        render_atlas(result, output / "atlas.png")
    result["elapsed_s"] = perf_counter() - began
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
