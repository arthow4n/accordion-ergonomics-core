"""Reproduce selected named-contact states and independently expose proxy concerns."""

import hashlib
import json
from pathlib import Path
from typing import Any

from PIL import Image

from .anatomy import DIGITS
from .collision_coverage import audit_collision_coverage
from .experiment import Experiment
from .exploration import read_hashed
from .hand_audit import audit_hand_pose
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import build_scene


def run_contact_report(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    output.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for request in source["poses"]:
        saved = read_hashed(definition.parent / request["result"], request["sha256"])
        e = Experiment.from_dict(saved["input"])
        scene = build_scene(
            e.geometry,
            e.player,
            e.setup,
            e.physical_contact,
            tuple(c.finger for c in e.contacts),
        )
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Contact report model identity differs")
        scene.data.qpos[:] = saved["qpos_rad"]
        hand = audit_hand_pose(scene)
        coverage = audit_collision_coverage(scene)
        concerns = [
            p
            for p in hand["pairs"]
            if p["classification"] == "cross_digit_phalangeal_unresolved"
            and p["signed_proxy_distance_m"] < 0
        ]
        worst = (
            min(concerns, key=lambda p: p["signed_proxy_distance_m"])
            if concerns
            else None
        )
        roles = {
            d: "required"
            if any(c.finger == d for c in e.contacts)
            else "frozen"
            if e.physical_contact.inactive_digits_policy == "freeze"
            else "free"
            for d in DIGITS
        }
        cameras = (
            render_views(
                scene,
                output / "renders" / request["id"],
                saved["target"]["surface_world_m"],
                saved["target"]["button_id"],
                collision_overlay=True,
                highlighted_proxy_names=tuple(worst["geoms"]) if worst else (),
                contact_roles=roles,
                closeup=True,
                views_to_render=tuple(request["views"]) if "views" in request else None,
                camera_overrides=request.get("camera_overrides"),
                button_roles={
                    c["button_id"]: "required" for c in saved["contact_requirements"]
                },
                state_label=(
                    f"{request['id']} | solver {saved['status']} | marker error "
                    f"{saved['diagnostics']['position_error_m'] * 1000:.3f} mm"
                ),
            )
            if request.get("render", True)
            else {}
        )
        records.append(
            {
                "id": request["id"],
                "source": request,
                "qpos_rad": saved["qpos_rad"],
                "initial_qpos_rad": saved["initial_qpos_rad"],
                "frozen_dof_indices": saved["frozen_dof_indices"],
                "joint_names": saved["joint_names"],
                "contact_requirements": saved["contact_requirements"],
                "inactive_digits_policy": e.physical_contact.inactive_digits_policy,
                "solver_status": saved["status"],
                "diagnostics": saved["diagnostics"],
                "coverage": coverage,
                "hand": hand,
                "worst_cross_digit": worst,
                "cameras": cameras,
                "roles": roles,
                **current_execution_metadata(scene.model),
            }
        )
    comparisons: list[dict[str, Any]] = []
    for comparison in source.get("comparisons", []):
        left, right = [
            next(r for r in records if r["id"] == comparison[key])
            for key in ("left", "right")
        ]
        if (
            left["joint_names"] != right["joint_names"]
            or left["initial_qpos_rad"] != right["initial_qpos_rad"]
        ):
            raise ValueError(
                "Policy comparison requires matched coordinates and initial state"
            )
        for view in comparison["views"]:
            if left["cameras"][view] != right["cameras"][view]:
                raise ValueError("Comparison cameras must be identical")
            frames = []
            for record in (left, right):
                with Image.open(
                    output / "renders" / record["id"] / (view + ".png")
                ) as im:
                    frames.append(im.copy())
            image = Image.new("RGB", (1920, 720))
            image.paste(frames[0], (0, 0))
            image.paste(frames[1], (960, 0))
            image.save(output / (comparison["id"] + "-" + view + ".png"))
        comparisons.append(
            {
                **comparison,
                "maximum_joint_difference_rad": max(
                    abs(a - b)
                    for a, b in zip(left["qpos_rad"], right["qpos_rad"], strict=True)
                ),
                "claim": "Matched saved static states, no naturalness ranking",
            }
        )
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "poses": records,
        "comparisons": comparisons,
        "artifact_sha256": {
            str(f.relative_to(output)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(output.rglob("*.png"))
        },
        "claim": "Saved static model states; anatomy and human feasibility unresolved",
    }
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
