"""Corrected initial-pose provenance and ideal-equality screening control."""

import hashlib
import json
import os
from pathlib import Path

import myo_sim
import numpy as np

from ._engine import mujoco
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .muscle_validation import native_parity
from .muscles import (
    StaticScenario,
    conditional_static_screen,
    length_derivative_check,
    muscle_snapshot,
)
from .passage_media import independent_samples
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import build_scene


def run_seed_capacity(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    baseline = read_hashed(
        definition.parent / source["baseline_result"], source["baseline_sha256"]
    )
    historical = read_hashed(
        definition.parent / source["muscle_result"], source["muscle_sha256"]
    )
    e = Experiment.from_dict(historical["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != historical["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Seed audit changed model identity")
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    if names != baseline["joint_names"]:
        raise ValueError("Seed joint order differs")
    seed = np.asarray(baseline["qpos_rad"])
    extreme = seed.copy()
    for name in source["synthetic_extreme_joints"]:
        i = names.index(name)
        low, high = scene.model.jnt_range[i]
        extreme[i] = low + source["synthetic_range_fraction"] * (high - low)
    native = myo_sim.load_spec("myoarm_r").compile()
    native_data = mujoco.MjData(native)
    poses = [
        ("resolved-playing-seed", seed, [{"finger": "index"}]),
        ("resolved-synthetic-extreme", extreme, []),
    ]
    historical_ref = next(
        p for p in historical["poses"] if p["pose"]["id"] == "reference-seed"
    )
    poses.append(
        ("historical-uncoupled-input", np.array(historical_ref["pose"]["qpos_rad"]), [])
    )
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    cameras = source.get("cameras")
    for name, q, contacts in poses:
        snap = muscle_snapshot(scene, q)
        derivative = length_derivative_check(scene, q, 1e-6)
        parity = native_parity(scene.model, native, native_data, snap, names)
        screens = [
            conditional_static_screen(
                scene, e.geometry, snap, contacts, StaticScenario(force, obj)
            )
            for force in source["reaction_scenarios_n"]
            if contacts or force == 0
            for obj in ("activation_squared", "activation_sum")
        ]
        audit = independent_samples(
            scene, [{"qpos_rad": q.tolist()}], e.solver.penetration_tolerance_m
        )
        scene.data.qpos[:] = q
        eq = max(abs(x) for x in snap["equality_position_residual_rad"])
        screen = screens[0]
        label = (
            f"{name} | equality residual {eq:.4g} rad | "
            f"static residual {screen['force_balance_residual_projected_nm']:.4g} Nm | "
            "no initial approach, no muscle execution"
        )
        cameras = render_views(
            scene,
            output / name,
            e.geometry.surface_world_m(button_at(1, 5)).tolist(),
            "r1c5",
            collision_overlay=True,
            highlighted_proxy_names=tuple(audit["worst_cross_digit"]["geoms"]),
            contact_roles={"index": "required"} if contacts else {},
            button_roles={"r1c5": "required" if contacts else "free"},
            camera_overrides=cameras,
            state_label=label,
        )
        reports.append(
            dict(
                id=name,
                qpos_rad=q.tolist(),
                snapshot=snap,
                native_parity=parity,
                derivative_check=derivative,
                static_screens=screens,
                independent_proxy_audit=audit,
                cameras=cameras,
            )
        )
    result = dict(
        id="resolved-seed-capacity-048",
        input=source,
        definition_sha256=hashlib.sha256(raw).hexdigest(),
        poses=reports,
        seed_provenance=(
            "Exact saved 037 solved pose; "
            "historical scene_input was stale original input"
        ),
        historical_correction=(
            "046 reference-seed and synthetic-extreme are "
            "off equality manifold; they are not resolved playing seeds"
        ),
        first_note_approach="not_planned",
        artifact_sha256={
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob("*.png")
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
