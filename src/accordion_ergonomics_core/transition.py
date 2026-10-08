"""Falsify a supplied joint-space path with sampled collision counterexamples.

A detected violation rejects this candidate. An absence of sampled violations
is inconclusive between samples, and never proves a valid playing trajectory.
Progress is dimensionless; no tempo or dynamical feasibility is assumed.
"""

import hashlib
import json
import os
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np

from .experiment import Experiment
from .instrument import button_at
from .provenance import anatomy_digest, project_source_digest


def run_transition(
    definition: Path, output: Path, render: bool = True
) -> dict[str, Any]:
    os.environ.setdefault("MUJOCO_GL", "egl")
    from ._engine import mujoco
    from .scene import build_scene, diagnostics

    source = json.loads(definition.read_text())
    if source["schema_version"] != 1 or source["interpolation"] != "linear-hinge-qpos":
        raise ValueError("Unsupported transition experiment")
    count = source["samples"]
    if type(count) is not int or count < 3:
        raise ValueError("At least three recorded sample points are required")
    endpoints = []
    for key in ("start", "end"):
        raw = (definition.parent / source[f"{key}_result"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != source[f"{key}_sha256"]:
            raise ValueError(f"Recorded {key} endpoint changed")
        result = json.loads(raw)
        if result["status"] != "success":
            raise ValueError("This experiment requires two accepted endpoint poses")
        if result["provenance"]["anatomy_source_sha256"] != anatomy_digest():
            raise ValueError("Anatomical source differs from the recorded endpoint")
        endpoints.append(result)
    start, end = endpoints
    if start["input"]["geometry"] != end["input"]["geometry"]:
        raise ValueError("Endpoints use different boards or placements")
    if start["joint_names"] != end["joint_names"]:
        raise ValueError("Endpoints use different joint coordinate order")
    experiment = Experiment.from_dict(start["input"])
    scene = build_scene(experiment.geometry)
    if not np.all(scene.model.jnt_type == mujoco.mjtJoint.mjJNT_HINGE):
        raise ValueError("Linear interpolation currently supports hinge-only models")
    q0, q1 = (np.asarray(r["qpos_rad"]) for r in endpoints)
    contact = start["input"]["contacts"][0]
    button = button_at(contact["row"], contact["column"])
    target = experiment.geometry.surface_world_m(button)
    records = []
    worst_index = 0
    worst_penetration = -1.0
    for index, progress in enumerate(np.linspace(0.0, 1.0, count)):
        q = q0 + progress * (q1 - q0)
        scene.data.qpos[:] = q
        check = diagnostics(scene, target, button.id)
        reasons = []
        for quantity, threshold in (
            ("max_penetration_m", experiment.solver.penetration_tolerance_m),
            ("joint_max_violation_rad", experiment.solver.joint_tolerance_rad),
            ("equality_max_residual_rad", experiment.solver.equality_tolerance_rad),
        ):
            if check[quantity] > threshold:
                reasons.append(quantity)
        records.append(
            {
                "progress": float(progress),
                "qpos_rad": q.tolist(),
                "violations": reasons,
                "max_penetration_m": check["max_penetration_m"],
                "joint_max_violation_rad": check["joint_max_violation_rad"],
                "equality_max_residual_rad": check["equality_max_residual_rad"],
                "contacts": check["contacts"],
                "fingertip_world_m": check["pad_world_m"],
            }
        )
        if check["max_penetration_m"] > worst_penetration:
            worst_index, worst_penetration = index, check["max_penetration_m"]
    invalid = any(record["violations"] for record in records)
    scene.data.qpos[:] = records[worst_index]["qpos_rad"]
    mujoco.mj_forward(scene.model, scene.data)
    output.mkdir(parents=True, exist_ok=True)
    cameras = {}
    if render:
        from .render import render_views

        cameras = render_views(
            scene,
            output / "renders",
            target.tolist(),
            button.id,
            collision_overlay=True,
        )
    runtime = {
        "python": platform.python_version(),
        "packages": {p: version(p) for p in ("mujoco", "myo-sim", "numpy", "pillow")},
    }
    result = {
        "schema_version": 1,
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(definition.read_bytes()).hexdigest(),
        "status": "failed" if invalid else "inconclusive",
        "candidate_valid": False if invalid else None,
        "endpoint_statuses": [start["status"], end["status"]],
        "global_transition_feasible": None,
        "claim": (
            "This supplied path violates modeled constraints; other paths may exist"
            if invalid
            else "Sampling found no violation; intervals remain unvalidated"
        ),
        "contact_policy": "Start contact may release; no held contact requirement",
        "timing_s": None,
        "runtime": runtime,
        "render_state": {
            "input": start["input"],
            "model": start["model"],
            "qpos_rad": records[worst_index]["qpos_rad"],
            "target": start["target"],
            "provenance": start["provenance"],
            "runtime": runtime,
            "collision_overlay": True,
        },
        "provenance": {
            "anatomy_source_sha256": anatomy_digest(),
            "project_source_sha256": project_source_digest(),
        },
        "worst_sample_index": worst_index,
        "maximum_detected_penetration_m": worst_penetration,
        "samples": records,
        "cameras": cameras,
        "unvalidated": [
            "intervals between samples",
            "button operation",
            "actuated dynamics",
            "complete physical collision coverage",
        ],
    }
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
