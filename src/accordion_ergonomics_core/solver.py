"""Local differential IK. Failure is not proof of global unreachability."""

from dataclasses import asdict
from typing import Any

import mink
import numpy as np
from numpy.typing import NDArray

from .anatomy import digit_dofs
from .distance_limits import DisplacementDistanceLimit, collision_pairs
from .experiment import SolverSettings
from .integration import collision_checked_step
from .scene import Scene, coupled_initial_pose, diagnostics


def solve_contact(
    scene: Scene,
    target: NDArray[np.float64],
    initial: dict[str, float],
    settings: SolverSettings,
    button_id: str = "r1c5",
    frozen_joints: tuple[str, ...] = (),
    contact_required: bool = True,
    finger: str = "index",
    additional_contacts: tuple[tuple[NDArray[np.float64], str, str], ...] = (),
    additional_contact_required: bool = True,
) -> dict[str, Any]:
    model = scene.model
    if (
        scene.contact_profile.additional_collision_pairs
        and settings.collision_avoidance
        and settings.collision_limit_implementation != "displacement"
    ):
        raise ValueError("Explicit self-pair avoidance requires displacement limits")
    q0 = coupled_initial_pose(model, initial)
    configuration = mink.Configuration(model, q=q0)
    requirements = ((target, finger, button_id),) + additional_contacts
    required = [contact_required] + [additional_contact_required] * len(
        additional_contacts
    )
    require_any_contact = any(required)
    contact_tasks: list[mink.Task] = []
    for point, digit, _ in requirements:
        position = mink.FrameTask(
            f"{digit}_pad",
            "site",
            position_cost=settings.position_cost,
            orientation_cost=0.0,
        )
        position.set_target(mink.SE3.from_translation(point))
        normal = mink.AxisAlignTask(f"{digit}_pad", "site", cost=settings.normal_cost)
        normal.set_target(-scene.data.body("keyboard").xmat.reshape(3, 3)[:, 2])
        contact_tasks.extend((position, normal))

    def check_contacts() -> dict[str, Any]:
        checks = [
            diagnostics(scene, point, button, digit)
            for point, digit, button in requirements
        ]
        aggregate = dict(checks[0])
        for key in ("position_error_m", "normal_error_rad"):
            aggregate[key] = max(c[key] for c in checks)
        actual_contacts = [c for c, r in zip(checks, required, strict=True) if r]
        aggregate["target_contact_distance_m"] = (
            max(actual_contacts, key=lambda c: abs(c["target_contact_distance_m"]))[
                "target_contact_distance_m"
            ]
            if actual_contacts
            else 0.0
        )
        if len(checks) > 1:
            aggregate["contact_diagnostics"] = [
                {"finger": r[1], "button_id": r[2], **c}
                for r, c in zip(requirements, checks, strict=True)
            ]
        return aggregate

    posture = mink.PostureTask(model, cost=settings.posture_cost)
    posture.set_target(q0)
    coupled = mink.EqualityConstraintTask(model, cost=1.0)
    # Only requested digits articulate; other digits remain present and frozen.
    active_digits = {r[1] for r in requirements}
    digits = digit_dofs(model)
    inactive = [
        i
        for digit, indices in digits.items()
        if digit not in active_digits
        for i in indices
    ]
    frozen = sorted(
        set(
            (
                inactive
                if scene.contact_profile.inactive_digits_policy == "freeze"
                else []
            )
            + [int(model.joint(name).dofadr[0]) for name in frozen_joints]
        )
    )
    constraints: list[mink.Task] = [coupled]
    if frozen:
        constraints.append(mink.DofFreezingTask(model, frozen))
    limits: list[mink.Limit] = [mink.ConfigurationLimit(model)]
    if settings.collision_avoidance:
        if settings.collision_limit_implementation == "displacement":
            limits.append(
                DisplacementDistanceLimit(
                    model,
                    collision_pairs(model, scene.anatomy_geoms, scene.board_geoms),
                    scene.contact_profile,
                )
            )
        else:
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
        check = check_contacts()
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
        if accepted(check, settings, require_any_contact):
            break
        if (
            iteration == 0
            and settings.collision_avoidance
            and settings.collision_limit_implementation == "displacement"
            and check["max_penetration_m"] > settings.penetration_tolerance_m
        ):
            failure = "initial_collision_violation"
            break
        try:
            velocity = mink.solve_ik(
                configuration,
                [*contact_tasks, posture],
                dt,
                solver="clarabel",
                damping=settings.damping,
                limits=limits,
                constraints=constraints,
            )
            if not np.all(np.isfinite(velocity)):
                raise ValueError("Nonfinite IK velocity")
            if (
                settings.collision_avoidance
                and settings.collision_limit_implementation == "displacement"
            ):
                proposed, step_record = collision_checked_step(
                    scene, configuration.q.copy(), velocity * dt, settings
                )
                history[-1]["integration_step"] = step_record
                if proposed is None:
                    failure = step_record["reason"]
                    break
                configuration.update(q=proposed)
            else:
                configuration.integrate_inplace(velocity, dt)
        except (
            mink.NoSolutionFound,
            mink.NotWithinConfigurationLimits,
            ValueError,
        ) as exc:
            failure = f"{type(exc).__name__}: {exc}"
            break
    scene.data.qpos[:] = configuration.q
    check = check_contacts()
    return {
        "status": "success"
        if accepted(check, settings, require_any_contact)
        else "failed",
        "feasible": None,
        "collision_limit_implementation": settings.collision_limit_implementation,
        "solver_settings": asdict(settings),
        "claim": (
            "Static kinematic candidate only; playing feasibility is unestablished"
        ),
        "failure": failure,
        "termination_reason": (
            "accepted_endpoint"
            if accepted(check, settings, require_any_contact)
            else "solver_error"
            if failure
            else "iteration_budget_exhausted"
        ),
        "diagnostic_reasons": violation_reasons(check, settings, require_any_contact),
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
        "contact_requirements": [
            {"finger": r[1], "button_id": r[2], "surface_contact_required": v}
            for r, v in zip(requirements, required, strict=True)
        ],
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
