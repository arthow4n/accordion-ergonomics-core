"""Sampled collision backtracking for proposed hinge-model IK steps."""

from typing import Any

import numpy as np
from numpy.typing import NDArray

from ._engine import mujoco
from .experiment import SolverSettings
from .scene import Scene


def collision_checked_step(
    scene: Scene,
    start: NDArray[np.float64],
    displacement: NDArray[np.float64],
    settings: SolverSettings,
) -> tuple[NDArray[np.float64] | None, dict[str, Any]]:
    """Backtrack a proposed Δq, testing its edge independently of activation bands.

    This is numerical iteration safety, not a timed playing trajectory. Reject
    colliding seeds; recovery from an invalid configuration is a separate problem.
    Unsampled intervals and omitted self-collision pairs remain unestablished.
    """
    model, data = scene.model, scene.data
    if np.any(model.jnt_type != mujoco.mjtJoint.mjJNT_HINGE):
        raise ValueError("Collision-step angular sampling currently requires hinges")
    data.qpos[:] = start
    mujoco.mj_forward(model, data)
    tolerance = settings.penetration_tolerance_m
    initial_penetration = max([0.0] + [-float(c.dist) for c in data.contact])
    if initial_penetration > tolerance:
        return None, {
            "reason": "initial_collision_violation",
            "maximum_penetration_m": initial_penetration,
        }
    attempts = []
    for backtrack in range(settings.collision_backtrack_steps):
        fraction = 2.0**-backtrack
        delta = displacement * fraction
        count = max(
            1, int(np.ceil(np.max(np.abs(delta)) / settings.collision_edge_step_rad))
        )
        peak = 0.0
        valid = True
        for t in np.linspace(0, 1, count + 1)[1:]:
            data.qpos[:] = start + delta * t
            mujoco.mj_forward(model, data)
            penetration = max([0.0] + [-float(c.dist) for c in data.contact])
            peak = max(peak, penetration)
            if penetration > tolerance:
                valid = False
                break
        attempts.append(
            {
                "fraction": fraction,
                "sampled_edge_valid": valid,
                "maximum_sampled_penetration_m": peak,
            }
        )
        if valid:
            return start + delta, {
                "fraction": fraction,
                "edge_steps": count,
                "attempts": attempts,
                "continuous_validity": None,
            }
    data.qpos[:] = start
    mujoco.mj_forward(model, data)
    return None, {"reason": "no_sampled_clear_step", "attempts": attempts}
