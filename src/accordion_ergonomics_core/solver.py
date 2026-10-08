"""Local differential IK. Failure is not proof of global unreachability."""

from typing import Any

import mink
import numpy as np
from numpy.typing import NDArray

from .experiment import SolverSettings
from .scene import Scene, coupled_initial_pose, diagnostics


def solve_contact(
    scene: Scene,
    target: NDArray[np.float64],
    initial: dict[str, float],
    settings: SolverSettings,
    button_id: str = "r1c5",
    frozen_joints: tuple[str, ...] = (),
    contact_required: bool = True,
) -> dict[str, Any]:
    model = scene.model
    q0 = coupled_initial_pose(model, initial)
    configuration = mink.Configuration(model, q=q0)
    position = mink.FrameTask(
        "index_pad",
        "site",
        position_cost=settings.position_cost,
        orientation_cost=0.0,
    )
    position.set_target(mink.SE3.from_translation(target))
    normal = mink.AxisAlignTask(
        "index_pad",
        "site",
        cost=settings.normal_cost,
    )
    normal.set_target(-scene.data.body("keyboard").xmat.reshape(3, 3)[:, 2])
    posture = mink.PostureTask(model, cost=settings.posture_cost)
    posture.set_target(q0)
    coupled = mink.EqualityConstraintTask(model, cost=1.0)
    # Unused fingers are frozen in this monophonic experiment, not removed.
    frozen = sorted(
        set(
            list(range(18, 22))
            + list(range(26, model.nv))
            + [int(model.joint(name).dofadr[0]) for name in frozen_joints]
        )
    )
    constraints = [coupled, mink.DofFreezingTask(model, frozen)]
    limits: list[mink.Limit] = [mink.ConfigurationLimit(model)]
    if settings.collision_avoidance:
        limits.append(
            mink.CollisionAvoidanceLimit(
                model,
                [(scene.anatomy_geoms, scene.board_geoms)],
                minimum_distance_from_collisions=scene.contact_profile.collision_minimum_distance_m,
                collision_detection_distance=scene.contact_profile.collision_detection_distance_m,
                gain=scene.contact_profile.collision_gain,
            )
        )
    dt = settings.integration_dt_s
    history = []
    failure: str | None = None
    for iteration in range(settings.max_iterations):
        scene.data.qpos[:] = configuration.q
        check = diagnostics(scene, target, button_id)
        history.append(
            {
                "iteration": iteration,
                **{
                    k: check[k]
                    for k in (
                        "position_error_m",
                        "normal_error_rad",
                        "max_penetration_m",
                        "equality_max_residual_rad",
                        "joint_max_violation_rad",
                    )
                },
            }
        )
        if accepted(check, settings, contact_required):
            break
        try:
            velocity = mink.solve_ik(
                configuration,
                [position, normal, posture],
                dt,
                solver="clarabel",
                damping=settings.damping,
                limits=limits,
                constraints=constraints,
            )
            if not np.all(np.isfinite(velocity)):
                raise ValueError("Nonfinite IK velocity")
            configuration.integrate_inplace(velocity, dt)
        except (
            mink.NoSolutionFound,
            mink.NotWithinConfigurationLimits,
            ValueError,
        ) as exc:
            failure = f"{type(exc).__name__}: {exc}"
            break
    scene.data.qpos[:] = configuration.q
    check = diagnostics(scene, target, button_id)
    return {
        "status": "success"
        if accepted(check, settings, contact_required)
        else "failed",
        "feasible": None,
        "claim": (
            "Static kinematic candidate only; playing feasibility is unestablished"
        ),
        "failure": failure,
        "termination_reason": (
            "accepted_endpoint"
            if accepted(check, settings, contact_required)
            else "solver_error"
            if failure
            else "iteration_budget_exhausted"
        ),
        "diagnostic_reasons": violation_reasons(check, settings, contact_required),
        "state_semantics": "Kinematic configuration; dynamic state unestablished",
        "qvel_rad_s": None,
        "diagnostics": check,
        "initial_qpos_rad": q0.tolist(),
        "frozen_dof_indices": frozen,
        "qpos_rad": configuration.q.tolist(),
        "joint_names": [model.joint(i).name for i in range(model.njnt)],
        "solver_history": history,
        "trajectory": None,
        "contact_required": contact_required,
        "unvalidated": [
            "measured keyboard geometry and body placement",
            "button depression/force",
            "continuous approach, hold and release",
            "muscle actuation/equilibrium",
            "complete self-collision coverage",
            "player-specific anatomy",
            "pad deformation and anatomical validity of generic contact proxy",
        ],
    }


def accepted(
    check: dict[str, Any], settings: SolverSettings, contact_required: bool = True
) -> bool:
    return bool(
        (
            not contact_required
            or abs(check["target_contact_distance_m"]) <= settings.position_tolerance_m
        )
        and check["position_error_m"] <= settings.position_tolerance_m
        and check["normal_error_rad"] <= settings.normal_tolerance_rad
        and check["equality_max_residual_rad"] <= settings.equality_tolerance_rad
        and check["joint_max_violation_rad"] <= settings.joint_tolerance_rad
        and check["max_penetration_m"] <= settings.penetration_tolerance_m
    )


def violation_reasons(
    check: dict[str, Any], settings: SolverSettings, contact_required: bool = True
) -> list[str]:
    dimensions = (
        ("position_error_m", settings.position_tolerance_m),
        ("normal_error_rad", settings.normal_tolerance_rad),
        ("equality_max_residual_rad", settings.equality_tolerance_rad),
        ("joint_max_violation_rad", settings.joint_tolerance_rad),
        ("max_penetration_m", settings.penetration_tolerance_m),
    )
    reasons = [
        f"{name}={check[name]:.6g} exceeds {limit:.6g}"
        for name, limit in dimensions
        if check[name] > limit
    ]
    if (
        contact_required
        and abs(check["target_contact_distance_m"]) > settings.position_tolerance_m
    ):
        reasons.append("Requested fingertip/button contact is outside tolerance")
    return reasons
