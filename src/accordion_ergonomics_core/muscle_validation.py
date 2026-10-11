"""Native/reduced parity, routing probes and conditional static pose experiments."""

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
from .full_body import build_full_body, prescribed_pose
from .muscles import (
    StaticScenario,
    actuator_moment_matrix,
    conditional_static_screen,
    length_derivative_check,
    muscle_snapshot,
)
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene


def native_parity(reference_model, native_model, native_data, snapshot, joint_names):
    for i, name in enumerate(joint_names):
        native_data.qpos[native_model.joint(name).qposadr[0]] = snapshot["qpos_rad"][i]
    native_data.qvel[:] = 0
    native_data.act[:] = 0
    mujoco.mj_forward(native_model, native_data)
    actuator_ids = [
        native_model.actuator(name).id for name in snapshot["actuator_names"]
    ]
    joint_ids = [native_model.joint(name).dofadr[0] for name in joint_names]
    native_moment = actuator_moment_matrix(native_model, native_data)[
        np.ix_(actuator_ids, joint_ids)
    ]
    parameter_errors = {}
    for field in (
        "actuator_gainprm",
        "actuator_biasprm",
        "actuator_dynprm",
        "actuator_gear",
        "actuator_lengthrange",
        "actuator_ctrlrange",
    ):
        parameter_errors[field] = float(
            np.max(
                abs(
                    getattr(native_model, field)[actuator_ids]
                    - getattr(reference_model, field)
                )
            )
        )
    return {
        "parameter_max_errors": parameter_errors,
        "musculotendon_length_max_error_m": float(
            np.max(
                abs(
                    native_data.actuator_length[actuator_ids]
                    - snapshot["musculotendon_length_m"]
                )
            )
        ),
        "moment_matrix_max_error_m_per_rad": float(
            np.max(
                abs(
                    native_moment - snapshot["transmission_length_derivative_m_per_rad"]
                )
            )
        ),
        "gravity_bias_max_error_nm": float(
            np.max(abs(native_data.qfrc_bias[joint_ids] - snapshot["gravity_bias_nm"]))
        ),
        "passive_muscle_force_max_error_n": float(
            np.max(
                abs(
                    native_data.actuator_force[actuator_ids]
                    - snapshot["passive_muscle_force_n"]
                )
            )
        ),
        "actuator_acc0_max_difference": float(
            np.max(
                abs(
                    native_model.actuator_acc0[actuator_ids]
                    - reference_model.actuator_acc0
                )
            )
        ),
    }


def routing_probe(scene, native_model, native_data, case):
    rows = case["traces"]
    q = np.array([s["qpos_rad"] for s in rows])
    length = np.array([s["musculotendon_lengths_m"] for s in rows])
    delta = abs(np.diff(length, axis=0))
    k, muscle = np.unravel_index(delta.argmax(), delta.shape)
    ids = [native_model.joint(name).qposadr[0] for name in case["joint_names"]]
    native_act = native_model.actuator(case["actuator_names"][int(muscle)]).id
    a, b = q[k], q[k + 1]
    probe = []
    for fraction in np.linspace(0, 1, 65):
        coordinate = a + fraction * (b - a)
        scene.data.qpos[:] = coordinate
        scene.data.qvel[:] = 0
        mujoco.mj_forward(scene.model, scene.data)
        native_data.qpos[ids] = coordinate
        native_data.qvel[:] = 0
        mujoco.mj_forward(native_model, native_data)
        moment = actuator_moment_matrix(scene.model, scene.data)[muscle]
        probe.append(
            {
                "fraction": float(fraction),
                "qpos_rad": coordinate.tolist(),
                "reduced_length_m": float(scene.data.actuator_length[muscle]),
                "native_length_m": float(native_data.actuator_length[native_act]),
                "engine_derivative_along_segment_m": float(moment @ (b - a)),
            }
        )
    jumps = abs(np.diff([p["reduced_length_m"] for p in probe]))
    split = int(jumps.argmax())
    low, high = probe[split]["fraction"], probe[split + 1]["fraction"]
    left = probe[split]["reduced_length_m"]
    right = probe[split + 1]["reduced_length_m"]
    # Refine a branch switch independently of any accepted musical trajectory.
    history = []
    for _ in range(30):
        mid = (low + high) / 2
        scene.data.qpos[:] = a + mid * (b - a)
        mujoco.mj_forward(scene.model, scene.data)
        value = float(scene.data.actuator_length[muscle])
        if abs(value - left) < abs(value - right):
            low, left = mid, value
        else:
            high, right = mid, value
        history.append({"fraction_gap": high - low, "length_jump_m": abs(right - left)})
    return {
        "case_id": case["source_reference"]["id"],
        "muscle": case["actuator_names"][int(muscle)],
        "original_sample_pair": [int(k), int(k + 1)],
        "original_length_step_m": float(delta[k, muscle]),
        "diagnostic_probes": probe,
        "branch_refinement": history,
        "claim": (
            "Diagnostic coordinate probes only; not new accepted movement "
            "or animation. Largest jump refinement can also localize a "
            "steep smooth segment; persistence is the evidence."
        ),
    }


def run_muscle_validation(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    benchmark = read_hashed(
        definition.parent / source["audit_result"], source["audit_sha256"]
    )
    saved = read_hashed(
        definition.parent / source["reference_result"], source["reference_sha256"]
    )
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != saved["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Muscle study changed the reference scene")
    arm = myo_sim.load_spec("myoarm_r").compile()
    arm_data = mujoco.MjData(arm)
    native_spec, prescribed, _ = build_full_body(
        "myofullbody_native", e.setup, e.player.full_body_posture
    )
    native = native_spec.compile()
    native_data = mujoco.MjData(native)
    native_data.qpos[:] = prescribed_pose(native, prescribed)
    names = saved["joint_names"]
    seed = np.array(
        [
            e.initial_joints_rad.get(name, scene.model.qpos0[i])
            for i, name in enumerate(names)
        ]
    )
    extreme = seed.copy()
    for name in source["synthetic_extreme_joints"]:
        i = names.index(name)
        low, high = scene.model.jnt_range[i]
        extreme[i] = low + source["synthetic_range_fraction"] * (high - low)
    poses: list[dict] = [
        {
            "id": "reference-seed",
            "qpos_rad": seed.tolist(),
            "contacts": [{"finger": "index"}],
            "kind": "numerical playing seed; not observed rest",
        },
        {
            "id": "native-default",
            "qpos_rad": scene.model.qpos0.tolist(),
            "contacts": [],
            "kind": "imported defaults; not measured neutral",
        },
        {
            "id": "synthetic-extreme",
            "qpos_rad": extreme.tolist(),
            "contacts": [],
            "kind": "synthetic diagnostic posture; no musical validity",
        },
    ]
    for case in benchmark["cases"]:
        case_id = case["source_reference"]["id"]
        if case["state_kind"] == "connected_sampled_path":
            original = read_hashed(
                definition.parent / source["benchmark_definition"],
                source["benchmark_definition_sha256"],
            )
            ref = next(c for c in original["cases"] if c["id"] == case_id)
            original_saved = read_hashed(
                (definition.parent / source["benchmark_definition"]).parent
                / ref["search_result"],
                ref["search_sha256"],
            )
            strategy = next(
                s for s in original_saved["strategies"] if s["id"] == ref["strategy_id"]
            )
            indices = {
                i
                for i, s in enumerate(strategy["samples"])
                if s["event_index"] is not None
            }
            indices.add(case["worst_proxy_sample_index"])
            length = np.asarray([s["musculotendon_lengths_m"] for s in case["traces"]])
            largest_step, _ = np.unravel_index(
                abs(np.diff(length, axis=0)).argmax(),
                abs(np.diff(length, axis=0)).shape,
            )
            indices.update((int(largest_step), int(largest_step) + 1))
        else:
            indices = set(range(case["sample_count"]))
        for i in sorted(indices):
            state = case["traces"][i]
            poses.append(
                {
                    "id": f"{case_id}-state-{i}",
                    "case_id": case_id,
                    "sample_index": i,
                    "qpos_rad": state["qpos_rad"],
                    "contacts": state["active_contacts"]
                    if state["source_node_status"] is None
                    else [],
                    "kind": case["state_kind"],
                    "source_state_status": state["source_node_status"],
                }
            )
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    for pose in poses:
        snapshot = muscle_snapshot(scene, pose["qpos_rad"])
        derivative = length_derivative_check(
            scene, pose["qpos_rad"], source["finite_difference_step_rad"]
        )
        parity = {
            "native_arm": native_parity(scene.model, arm, arm_data, snapshot, names),
            "native_full_body": native_parity(
                scene.model, native, native_data, snapshot, names
            ),
        }
        native_ok = all(
            p["musculotendon_length_max_error_m"] < 1e-10
            and p["moment_matrix_max_error_m_per_rad"] < 1e-10
            and max(p["parameter_max_errors"].values()) == 0
            for p in parity.values()
        )
        geometry_ok = (
            derivative["maximum_error_m_per_rad"]
            <= source["derivative_tolerance_m_per_rad"]
        )
        validity = (
            "validated_native_and_length_derivatives"
            if native_ok and geometry_ok
            else "force_geometry_discrepancy"
        )
        snapshot["force_geometry_validation"] = validity
        screens = [
            conditional_static_screen(
                scene,
                e.geometry,
                snapshot,
                pose["contacts"],
                StaticScenario(force, objective),
            )
            for force in source["reaction_scenarios_n"]
            if pose["contacts"] or force == 0
            for objective in source["objectives"]
        ]
        for screen in screens:
            screen["force_geometry_validation"] = validity
            screen["eligible_for_validated_muscle_selection"] = (
                native_ok and geometry_ok and screen["conditional_feasible"]
            )
        reports.append(
            {
                "pose": pose,
                "snapshot": snapshot,
                "length_derivative_check": derivative,
                "native_parity": parity,
                "static_screens": screens,
            }
        )
    routing = [
        routing_probe(scene, arm, arm_data, case)
        for case in benchmark["cases"]
        if case["state_kind"] == "connected_sampled_path"
    ]
    motion_audits = [
        motion_derivative_audit(
            scene,
            arm,
            arm_data,
            case,
            source["finite_difference_step_rad"],
            source["derivative_tolerance_m_per_rad"],
        )
        for case in benchmark["cases"]
        if case["state_kind"] == "connected_sampled_path"
    ]
    result = {
        "id": "muscle-validation-046",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "model_system": {
            "retained_actuators": scene.model.nu,
            "retained_tendons": scene.model.ntendon,
            "retained_equalities": scene.model.neq,
            "all_peak_forces_explicit": bool(
                np.all(scene.model.actuator_gainprm[:, 2] > 0)
            ),
            "native_arm_model_sha256": compiled_model_digest(arm),
            "native_full_model_sha256": compiled_model_digest(native),
            "native_full_nq": native.nq,
            "native_full_nu": native.nu,
            "constraint_scope": (
                "Other full-body coordinates prescribed for parity; "
                "reduced model removes them and implicitly supplies "
                "fixed-base reactions"
            ),
        },
        "musculotendon_inventory": musculotendon_inventory(scene.model),
        "joint_names": names,
        "scene_input": saved["scene_input"],
        "poses": reports,
        "routing_probes": routing,
        "motion_derivative_audits": motion_audits,
        "assessment_scope": (
            "Static engine estimates only; nonunique recruitment, "
            "unknown support/press forces, no dynamic or human validity"
        ),
        **current_execution_metadata(scene.model),
    }
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    metadata = output / "execution.json"
    if metadata.exists():
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
    return result


def motion_derivative_audit(scene, native_model, native_data, case, step, tolerance):
    """Direction probes at every actual sample, not a velocity/time assignment."""
    q = np.array([s["qpos_rad"] for s in case["traces"]])
    m, d = scene.model, scene.data
    native_joints = [
        native_model.joint(name).qposadr[0] for name in case["joint_names"]
    ]
    native_actuators = [
        native_model.actuator(name).id for name in case["actuator_names"]
    ]
    native_dofs = [native_model.joint(name).dofadr[0] for name in case["joint_names"]]
    reports = []
    maximum_by_muscle = np.zeros(m.nu)
    native_length_error = 0.0
    native_moment_error = 0.0
    for index, coordinate in enumerate(q):
        direction = q[min(index + 1, len(q) - 1)] - q[max(index - 1, 0)]
        norm = np.max(abs(direction))
        direction = direction / norm if norm else direction
        d.qpos[:] = coordinate
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        actual_matrix = actuator_moment_matrix(m, d)
        actual = actual_matrix @ direction
        native_data.qpos[native_joints] = coordinate
        native_data.qvel[:] = 0
        mujoco.mj_forward(native_model, native_data)
        native_length_error = max(
            native_length_error,
            float(
                np.max(
                    abs(
                        native_data.actuator_length[native_actuators]
                        - d.actuator_length
                    )
                )
            ),
        )
        native_moment_error = max(
            native_moment_error,
            float(
                np.max(
                    abs(
                        actuator_moment_matrix(native_model, native_data)[
                            np.ix_(native_actuators, native_dofs)
                        ]
                        - actual_matrix
                    )
                )
            ),
        )
        d.qpos[:] = coordinate + step * direction
        mujoco.mj_forward(m, d)
        plus = d.actuator_length.copy()
        d.qpos[:] = coordinate - step * direction
        mujoco.mj_forward(m, d)
        finite = (plus - d.actuator_length) / (2 * step)
        error = abs(actual - finite)
        maximum_by_muscle = np.maximum(maximum_by_muscle, error)
        worst = int(error.argmax())
        reports.append(
            {
                "sample_index": index,
                "maximum_error_m_per_rad": float(error[worst]),
                "worst_actuator": m.actuator(worst).name,
                "engine_direction_derivative_m_per_rad": float(actual[worst]),
                "finite_direction_derivative_m_per_rad": float(finite[worst]),
                "consistent_within_numerical_tolerance": bool(
                    error[worst] <= tolerance
                ),
            }
        )
    d.qpos[:] = q[-1]
    mujoco.mj_forward(m, d)
    return {
        "case_id": case["source_reference"]["id"],
        "sample_count": len(q),
        "step_rad": step,
        "derivative_tolerance_m_per_rad": tolerance,
        "direction_definition": (
            "Actual neighboring joint-space direction normalized by "
            "largest coordinate component; no time or velocity"
        ),
        "per_actuator_maximum_error_m_per_rad": dict(
            zip(case["actuator_names"], maximum_by_muscle.tolist(), strict=True)
        ),
        "failure_sample_indices": [
            s["sample_index"]
            for s in reports
            if not s["consistent_within_numerical_tolerance"]
        ],
        "native_arm_length_max_error_m": native_length_error,
        "native_arm_moment_max_error_m_per_rad": native_moment_error,
        "samples": reports,
    }


def musculotendon_inventory(model):
    """Compiled imported routes and force parameters, without modifying them."""
    return {
        "actuators": [
            {
                "name": model.actuator(i).name,
                "transmission_type": int(model.actuator_trntype[i]),
                "tendon": model.tendon(int(model.actuator_trnid[i, 0])).name,
                "gear": model.actuator_gear[i].tolist(),
                "gain_parameters": model.actuator_gainprm[i].tolist(),
                "bias_parameters": model.actuator_biasprm[i].tolist(),
                "activation_parameters": model.actuator_dynprm[i].tolist(),
                "length_range_m": model.actuator_lengthrange[i].tolist(),
                "control_range": model.actuator_ctrlrange[i].tolist(),
            }
            for i in range(model.nu)
        ],
        "tendons": [
            {
                "name": model.tendon(i).name,
                "stiffness": float(model.tendon_stiffness[i]),
                "damping": float(model.tendon_damping[i]),
                "wraps": [
                    {
                        "type": int(model.wrap_type[j]),
                        "object_id": int(model.wrap_objid[j]),
                        "parameter": float(model.wrap_prm[j]),
                    }
                    for j in range(
                        model.tendon_adr[i], model.tendon_adr[i] + model.tendon_num[i]
                    )
                ],
            }
            for i in range(model.ntendon)
        ],
        "interpretation": (
            "Wrap object IDs refer to this compiled model; source snapshot and "
            "model identity are required. Parameters are imported, not calibrated."
        ),
    }
