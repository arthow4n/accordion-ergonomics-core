"""Pinned engine muscle/transmission diagnostics and conditional static screening.

These are model estimates with ideal imported equality reactions, no calibrated
skin/button forces, and no dynamics or human-feasibility claim.
"""

from dataclasses import dataclass
from typing import Any

import clarabel
import numpy as np
from scipy.linalg import null_space
from scipy.optimize import linprog, lsq_linear
from scipy.sparse import csc_matrix, eye, vstack

from ._engine import mujoco
from .scene import Scene

# Clarabel exposes its solver API from a Rust extension without complete stubs.
clarabel_backend: Any = clarabel


def actuator_moment_matrix(model, data):
    """Engine transmission d(length)/dq, not its negated pulling moment arm."""
    matrix = np.zeros((model.nu, model.nv))
    for i in range(model.nu):
        start, count = int(data.moment_rowadr[i]), int(data.moment_rownnz[i])
        indices = data.moment_colind[start : start + count]
        matrix[i, indices] = data.actuator_moment[start : start + count]
    return matrix


def equality_jacobian(model, data):
    if mujoco.mj_isSparse(model):
        jacobian = np.zeros((data.nefc, model.nv))
        for i in range(data.nefc):
            start, count = int(data.efc_J_rowadr[i]), int(data.efc_J_rownnz[i])
            jacobian[i, data.efc_J_colind[start : start + count]] = data.efc_J[
                start : start + count
            ]
    else:
        jacobian = data.efc_J.reshape(data.nefc, model.nv).copy()
    return jacobian[data.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY]


def muscle_snapshot(scene: Scene, qpos):
    m, d = scene.model, scene.data
    if (
        m.nu != 63
        or m.na != 63
        or not np.all(m.actuator_gaintype == mujoco.mjtGain.mjGAIN_MUSCLE)
    ):
        raise ValueError(
            "Expected pinned 63-muscle reference; unsupported muscle assembly"
        )
    if not np.all(m.actuator_biastype == mujoco.mjtBias.mjBIAS_MUSCLE) or np.any(
        m.actuator_forcelimited
    ):
        raise ValueError(
            "Force map needs unclipped native muscle gain and passive bias"
        )
    if np.any(m.dof_frictionloss):
        raise ValueError("Unmodeled static friction reaction blocks this screen")
    qpos = np.asarray(qpos)
    if qpos.shape != (m.nq,) or not np.isfinite(qpos).all():
        raise ValueError("Static screen needs finite exact compiled coordinates")
    d.qpos[:] = qpos
    d.qvel[:] = 0
    d.ctrl[:] = 0
    d.act[:] = 0
    mujoco.mj_forward(m, d)
    moment = actuator_moment_matrix(m, d)
    length = d.actuator_length.copy()
    gain = np.array(
        [
            mujoco.mju_muscleGain(
                length[i],
                0.0,
                m.actuator_lengthrange[i],
                m.actuator_acc0[i],
                m.actuator_gainprm[i, :9],
            )
            for i in range(m.nu)
        ]
    )
    passive = np.array(
        [
            mujoco.mju_muscleBias(
                length[i],
                m.actuator_lengthrange[i],
                m.actuator_acc0[i],
                m.actuator_biasprm[i, :9],
            )
            for i in range(m.nu)
        ]
    )
    bias_error = float(np.max(abs(d.actuator_force - passive)))
    gravity = d.qfrc_bias.copy()
    joint_passive = d.qfrc_passive.copy()
    equality = equality_jacobian(m, d)
    eq_positions = d.efc_pos[d.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY].copy()
    d.act[:] = 1
    mujoco.mj_forward(m, d)
    force_error = float(np.max(abs(d.actuator_force - gain - passive)))
    transmission_error = float(
        np.max(abs(d.qfrc_actuator - moment.T @ d.actuator_force))
    )
    d.qacc[:] = 0
    mujoco.mj_inverse(m, d)
    inverse_error = float(
        np.max(abs(d.qfrc_inverse + d.qfrc_constraint - gravity + joint_passive))
    )
    inverse_constraint = d.qfrc_constraint.copy()
    d.act[:] = 0
    mujoco.mj_forward(m, d)
    if max(bias_error, force_error, transmission_error, inverse_error) > 1e-7:
        raise ValueError("Engine force/inverse/transmission convention failed")
    muscle_l0 = np.diff(m.actuator_lengthrange, axis=1)[:, 0] / (
        m.actuator_gainprm[:, 1] - m.actuator_gainprm[:, 0]
    )
    tendon_slack = m.actuator_lengthrange[:, 0] - m.actuator_gainprm[:, 0] * muscle_l0
    return {
        "qpos_rad": qpos.tolist(),
        "actuator_names": [m.actuator(i).name for i in range(m.nu)],
        "musculotendon_length_m": length.tolist(),
        "normalized_muscle_length": ((length - tendon_slack) / muscle_l0).tolist(),
        "derived_optimal_muscle_length_m": muscle_l0.tolist(),
        "derived_rigid_tendon_slack_m": tendon_slack.tolist(),
        "transmission_length_derivative_m_per_rad": moment.tolist(),
        "active_force_per_activation_n": gain.tolist(),
        "passive_muscle_force_n": passive.tolist(),
        "gravity_bias_nm": gravity.tolist(),
        "joint_passive_nm": joint_passive.tolist(),
        "equality_jacobian": equality.tolist(),
        "equality_position_residual_rad": eq_positions.tolist(),
        "engine_checks": {
            "passive_force_error_n": bias_error,
            "active_force_error_n": force_error,
            "transmission_error_nm": transmission_error,
            "inverse_balance_error_nm": inverse_error,
        },
        "engine_inverse_constraint_nm": inverse_constraint.tolist(),
        "inverse_constraint_claim": (
            "Automatic soft contact/limit/equality inverse reactions recorded, "
            "excluded from conditional balance; equality reactions are eliminated "
            "by virtual-displacement projection"
        ),
    }


@dataclass(frozen=True)
class StaticScenario:
    reaction_per_contact_n: float = 0.0
    objective: str = "activation_squared"
    residual_tolerance_nm: float = 1e-6

    def __post_init__(self):
        if (
            not np.isfinite(self.reaction_per_contact_n)
            or self.reaction_per_contact_n < 0
        ):
            raise ValueError("Hypothetical contact reaction must be finite nonnegative")
        if self.objective not in ("activation_squared", "activation_sum"):
            raise ValueError("Unknown conditional recruitment objective")
        if (
            not np.isfinite(self.residual_tolerance_nm)
            or self.residual_tolerance_nm <= 0
        ):
            raise ValueError("Residual tolerance is a positive numerical parameter")


def conditional_static_screen(
    scene: Scene,
    geometry,
    snapshot: dict,
    contacts: list[dict],
    scenario: StaticScenario,
):
    m, d = scene.model, scene.data
    d.qpos[:] = snapshot["qpos_rad"]
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)
    moment = np.asarray(snapshot["transmission_length_derivative_m_per_rad"])
    gain = np.asarray(snapshot["active_force_per_activation_n"])
    passive_force = np.asarray(snapshot["passive_muscle_force_n"])
    equality = np.asarray(snapshot["equality_jacobian"])
    tangent = null_space(equality, rcond=1e-10)
    reaction = np.zeros(m.nv)
    for contact in contacts:
        jacobian = np.zeros((3, m.nv))
        mujoco.mj_jacSite(m, d, jacobian, None, m.site(contact["finger"] + "_pad").id)
        reaction += jacobian.T @ (
            geometry.rotation[:, 2] * scenario.reaction_per_contact_n
        )
    required_full = (
        np.asarray(snapshot["gravity_bias_nm"])
        - np.asarray(snapshot["joint_passive_nm"])
        - moment.T @ passive_force
        - reaction
    )
    active_full = moment.T * gain
    a, b = tangent.T @ active_full, tangent.T @ required_full
    if scenario.objective == "activation_sum":
        solved = linprog(
            np.ones(m.nu), A_eq=a, b_eq=b, bounds=(0.0, 1.0), method="highs"
        )
        status = str(solved.message)
        activation = solved.x if solved.success else None
    else:
        settings = clarabel_backend.DefaultSettings()
        settings.verbose = False
        settings.tol_feas = 1e-10
        settings.tol_gap_abs = 1e-10
        constraints = vstack((csc_matrix(a), -eye(m.nu), eye(m.nu)), format="csc")
        rhs = np.r_[b, np.zeros(m.nu), np.ones(m.nu)]
        solver = clarabel_backend.DefaultSolver(
            eye(m.nu, format="csc"),
            np.zeros(m.nu),
            constraints,
            rhs,
            [
                clarabel_backend.ZeroConeT(len(b)),
                clarabel_backend.NonnegativeConeT(2 * m.nu),
            ],
            settings,
        )
        solved = solver.solve()
        status = str(solved.status)
        activation = (
            np.asarray(solved.x) if status in ("Solved", "AlmostSolved") else None
        )
    solution_kind = "conditional_recruitment_solution"
    if activation is None:
        fallback = lsq_linear(a, b, bounds=(0.0, 1.0), tol=1e-10, max_iter=500)
        activation = fallback.x
        solution_kind = (
            "bounded_minimum_residual_diagnostic; not a feasible recruitment"
        )
    balance_full = required_full - active_full @ activation
    reaction_coefficients = np.linalg.lstsq(equality.T, balance_full, rcond=1e-10)[0]
    residual_full = balance_full - equality.T @ reaction_coefficients
    residual_projected = a @ activation - b
    residual_norm = float(np.linalg.norm(residual_projected))
    bounds_ok = bool(activation.min() >= -1e-8 and activation.max() <= 1 + 1e-8)
    equality_position_error = float(
        np.max(np.abs(snapshot["equality_position_residual_rad"]), initial=0)
    )
    equality_position_consistent = equality_position_error <= 1e-8
    force_balance_found = bool(
        solution_kind == "conditional_recruitment_solution"
        and bounds_ok
        and residual_norm <= scenario.residual_tolerance_nm
    )
    feasible = force_balance_found and equality_position_consistent
    return {
        "force_balance_found": force_balance_found,
        "equality_position_error_rad": equality_position_error,
        "equality_position_numerical_tolerance_rad": 1e-8,
        "ideal_equality_position_consistent": equality_position_consistent,
        "scenario": {
            "reaction_per_contact_n": scenario.reaction_per_contact_n,
            "force_provenance": (
                "synthetic sensitivity parameter; no measured accordion force"
            ),
            "reaction_direction": (
                "board outward normal on hand at required fingertip sites; "
                "no other support"
            ),
            "objective": scenario.objective,
            "objective_units": (
                "dimensionless activation; squared objective is sum(a^2)/2"
            ),
            "activation_bounds": [0.0, 1.0],
            "residual_tolerance_nm": scenario.residual_tolerance_nm,
            "equality_treatment": (
                "Ideal imported constraints; project onto null(J_eq), "
                "report ideal reaction separately"
            ),
            "external_uncertainty": (
                "No calibrated button force, friction, deformable contact "
                "or additional hand support"
            ),
        },
        "applied_contact_count": len(contacts),
        "total_hypothetical_outward_force_n": len(contacts)
        * scenario.reaction_per_contact_n,
        "solver_status": status,
        "solution_kind": solution_kind,
        "conditional_feasible": feasible,
        "activation": activation.tolist(),
        "maximum_activation": float(activation.max()),
        "sum_squared_activation": float(activation @ activation),
        "sum_activation": float(activation.sum()),
        "force_balance_residual_projected_nm": residual_norm,
        "force_balance_residual_full_nm": float(np.linalg.norm(residual_full)),
        "residual_generalized_nm": residual_full.tolist(),
        "external_reaction_generalized_nm": reaction.tolist(),
        "muscle_active_generalized_nm": (active_full @ activation).tolist(),
        "muscle_passive_generalized_nm": (moment.T @ passive_force).tolist(),
        "ideal_equality_reaction_generalized_nm": (
            equality.T @ reaction_coefficients
        ).tolist(),
        "tangent_dimension": int(tangent.shape[1]),
        "muscle_map_rank": int(np.linalg.matrix_rank(a)),
        "unsupported_required_moment_norm_nm": float(
            np.linalg.norm(null_space(a.T, rcond=1e-10).T @ b)
        ),
        "human_feasibility": None,
        "dynamic_execution": "not_evaluated",
    }


def length_derivative_check(scene: Scene, qpos, step_rad: float = 1e-6):
    """Independent coordinate probes, not a contact path or timed movement."""
    m, d = scene.model, scene.data
    if m.nq != m.nv or np.any(m.jnt_type != mujoco.mjtJoint.mjJNT_HINGE):
        raise ValueError("Derivative probe is specific to the pinned hinge anatomy")
    if not np.isfinite(step_rad) or step_rad <= 0:
        raise ValueError("Derivative step must be positive")
    qpos = np.asarray(qpos).copy()
    d.qpos[:] = qpos
    d.qvel[:] = 0
    mujoco.mj_forward(m, d)
    actual = actuator_moment_matrix(m, d)
    finite = np.zeros_like(actual)
    for j in range(m.nv):
        d.qpos[:] = qpos
        d.qpos[j] += step_rad
        mujoco.mj_forward(m, d)
        plus = d.actuator_length.copy()
        d.qpos[:] = qpos
        d.qpos[j] -= step_rad
        mujoco.mj_forward(m, d)
        finite[:, j] = (plus - d.actuator_length) / (2 * step_rad)
    d.qpos[:] = qpos
    mujoco.mj_forward(m, d)
    error = np.abs(actual - finite)
    i, j = np.unravel_index(error.argmax(), error.shape)
    return {
        "step_rad": step_rad,
        "maximum_error_m_per_rad": float(error.max()),
        "per_actuator_maximum_error_m_per_rad": error.max(axis=1).tolist(),
        "worst_actuator": m.actuator(int(i)).name,
        "worst_joint": m.joint(int(j)).name,
        "engine_derivative_m_per_rad": float(actual[i, j]),
        "finite_difference_m_per_rad": float(finite[i, j]),
        "claim": (
            "Independent off-constraint coordinate probes of length geometry; "
            "not an accepted movement"
        ),
    }
