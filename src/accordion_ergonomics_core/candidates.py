"""Deterministic multi-start contact discovery and physical deduplication."""

from dataclasses import asdict, dataclass, replace
from time import perf_counter
from typing import Any

import numpy as np

from ._engine import mujoco
from .domain import CandidateRealization, PhysicalDescriptors, PlayingState
from .experiment import Experiment
from .instrument import button_at
from .scene import Scene, coupled_initial_pose
from .solver import solve_contact


@dataclass(frozen=True)
class CandidateSettings:
    # Explicit numerical exploration and grouping thresholds, not comfort limits.
    offsets_rad: tuple[dict[str, float], ...]
    palm_dedup_m: float = 0.005
    elbow_dedup_m: float = 0.01
    joint_dedup_rad: float = 0.1
    max_iterations: int = 120

    def __post_init__(self) -> None:
        if self.max_iterations < 1 or any(
            v <= 0 or not np.isfinite(v)
            for v in (self.palm_dedup_m, self.elbow_dedup_m, self.joint_dedup_rad)
        ):
            raise ValueError("Invalid candidate search thresholds")
        if any(
            not np.isfinite(v) for offset in self.offsets_rad for v in offset.values()
        ):
            raise ValueError("Search offsets must be finite radians")


def descriptors(scene: Scene) -> PhysicalDescriptors:
    model, data = scene.model, scene.data
    mujoco.mj_forward(model, data)

    def joint(name: str) -> float:
        return float(data.qpos[model.joint(name).qposadr[0]])

    margins = np.minimum(
        data.qpos - model.jnt_range[:, 0], model.jnt_range[:, 1] - data.qpos
    )
    return PhysicalDescriptors(
        tuple(data.body("capitate_r").xpos),
        tuple(data.body("capitate_r").xmat),
        tuple(data.body("ulna_r").xpos),
        float(margins.min()),
        float(margins[list(range(18)) + list(range(22, 26))].min()),
        (joint("deviation_r"), joint("flexion_r")),
        joint("pro_sup_r"),
        tuple(joint(n) for n in ("elv_angle_r", "shoulder_elv_r", "shoulder_rot_r")),
        tuple(
            joint(n)
            for n in (
                "mcp2_flexion_r",
                "mcp2_abduction_r",
                "pm2_flexion_r",
                "md2_flexion_r",
            )
        ),
    )


def materially_distinct(
    a: PhysicalDescriptors, b: PhysicalDescriptors, settings: CandidateSettings
) -> bool:
    return bool(
        np.linalg.norm(np.array(a.palm_position_world_m) - b.palm_position_world_m)
        > settings.palm_dedup_m
        or np.linalg.norm(np.array(a.elbow_position_world_m) - b.elbow_position_world_m)
        > settings.elbow_dedup_m
        or np.max(
            np.abs(
                np.array(
                    a.wrist_rad
                    + a.shoulder_rad
                    + a.finger_rad
                    + (a.forearm_rotation_rad,)
                )
                - np.array(
                    b.wrist_rad
                    + b.shoulder_rad
                    + b.finger_rad
                    + (b.forearm_rotation_rad,)
                )
            )
        )
        > settings.joint_dedup_rad
    )


def discover_candidates(
    scene: Scene,
    experiment: Experiment,
    source_q: list[float],
    profile_hash: str,
    settings: CandidateSettings,
) -> dict[str, Any]:
    if len(experiment.contacts) != 1 or experiment.contacts[0].finger != "index":
        raise ValueError("Candidate discovery currently supports one index contact")
    started = perf_counter()
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    base = dict(zip(names, source_q, strict=True))
    scene.data.qpos[:] = source_q
    origin = descriptors(scene)
    contact = experiment.contacts[0]
    button = button_at(contact.row, contact.column)
    target = experiment.geometry.surface_world_m(button)
    attempts: list[dict[str, Any]] = []
    candidates: list[CandidateRealization] = []
    for index, offset in enumerate(({},) + settings.offsets_rad):
        initial = dict(base)
        for name, delta in offset.items():
            if name not in initial:
                raise ValueError(f"Unknown search joint: {name}")
            initial[name] += delta
        try:
            coupled_initial_pose(scene.model, initial)
        except ValueError as exc:
            attempts.append(
                {
                    "start_id": str(index),
                    "status": "invalid_initialization",
                    "reason": str(exc),
                    "offset_rad": offset,
                }
            )
            continue
        result = solve_contact(
            scene,
            target,
            initial,
            replace(experiment.solver, max_iterations=settings.max_iterations),
            button.id,
            experiment.frozen_joints,
        )
        result["start_id"] = str(index)
        result["offset_rad"] = offset
        if result["status"] == "success":
            physical = descriptors(scene)
            candidate = CandidateRealization(
                PlayingState(
                    tuple(names), tuple(result["qpos_rad"]), profile_hash, (button.id,)
                ),
                physical,
                str(index),
                float(
                    np.linalg.norm(
                        np.array(physical.palm_position_world_m)
                        - origin.palm_position_world_m
                    )
                ),
            )
            if all(
                materially_distinct(physical, c.descriptors, settings)
                for c in candidates
            ):
                candidates.append(candidate)
                result["candidate_index"] = len(candidates) - 1
            else:
                result["deduplicated"] = True
        attempts.append(result)
    return {
        "candidates": [asdict(c) for c in candidates],
        "attempts": attempts,
        "settings": asdict(settings),
        "elapsed_s": perf_counter() - started,
        "status": "candidates_found" if candidates else "no_solution_found",
        "physical_feasibility": None,
        "coverage": "Finite local starts; human representativeness unknown",
    }
