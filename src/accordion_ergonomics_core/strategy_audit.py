"""Untimed whole-hand diagnostics of exact recorded states; no ergonomic score."""

import hashlib
import json
import os
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

from ._engine import mujoco
from .anatomy import digit_dofs
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .hand_audit import hand_pairs
from .instrument import buttons
from .movement_evidence import state_digest, validate_strategy
from .provenance import compiled_model_digest, current_execution_metadata
from .quality_plots import trace_svg
from .scene import Scene, build_scene
from .wrist import orientation_trace, wrist_descriptors


def curve_length(points):
    return float(np.linalg.norm(np.diff(points, axis=0), axis=1).sum())


def coordinate_descriptors(q, names):
    delta = np.diff(q, axis=0)
    output = {}
    for i, name in enumerate(names):
        nonzero = delta[:, i][np.abs(delta[:, i]) > 1e-10]
        output[name] = {
            "minimum_rad": float(q[:, i].min()),
            "maximum_rad": float(q[:, i].max()),
            "excursion_rad": float(np.ptp(q[:, i])),
            "total_variation_rad": float(np.abs(delta[:, i]).sum()),
            "reversals": int(np.sum(nonzero[1:] * nonzero[:-1] < 0)),
            "reversal_zero_tolerance_rad": 1e-10,
        }
    return output


def audit_states(
    scene: Scene, geometry, states: list[dict], names: list[str], *, connected=True
):
    if not states or names != [
        scene.model.joint(i).name for i in range(scene.model.njnt)
    ]:
        raise ValueError("Audit needs actual states in exact compiled joint order")
    m, d = scene.model, scene.data
    q = np.asarray([s["qpos_rad"] for s in states])
    if q.shape != (len(states), m.nq) or not np.isfinite(q).all():
        raise ValueError("Nonfinite or malformed saved configuration")
    rotation = geometry.rotation
    origin = np.asarray(geometry.origin_m)
    caps = np.array([geometry.surface_world_m(b) for b in buttons()])
    pairs = [
        p
        for p in hand_pairs(scene)
        if p["classification"] == "cross_digit_phalangeal_unresolved"
    ]
    traces = []
    for index, sample in enumerate(states):
        d.qpos[:] = q[index]
        d.qvel[:] = 0
        mujoco.mj_forward(m, d)
        palm = d.body("capitate_r").xpos.copy()
        palm_rotation = rotation.T @ d.body("capitate_r").xmat.reshape(3, 3)
        digits = {finger: d.site(f"{finger}_pad").xpos.copy() for finger in DIGITS}
        distances = [
            (float(mujoco.mj_geomDistance(m, d, *p["geom_ids"], 1.0, None)), p["geoms"])
            for p in pairs
        ]
        worst_distance, worst_pair = min(distances)
        margin = np.minimum(q[index] - m.jnt_range[:, 0], m.jnt_range[:, 1] - q[index])
        margin[~m.jnt_limited.astype(bool)] = np.inf
        traces.append(
            {
                "sample_index": index,
                "source_node_id": sample.get("source_node_id"),
                "source_node_status": sample.get("source_node_status"),
                "qpos_rad": q[index].tolist(),
                "active_contacts": sample.get("active_contacts", []),
                "roles": sample.get("roles", {}),
                "body_axes_board_xyzw": orientation_trace(scene, geometry),
                "palm_world_m": palm.tolist(),
                "palm_board_m": (rotation.T @ (palm - origin)).tolist(),
                "palm_body_axes_in_board": palm_rotation.tolist(),
                "palm_rotation_board_xyzw": Rotation.from_matrix(palm_rotation)
                .as_quat()
                .tolist(),
                "palm_nearest_cap_center_distance_m": float(
                    np.linalg.norm(caps - palm, axis=1).min()
                ),
                "finger_sites_world_m": {f: p.tolist() for f, p in digits.items()},
                "finger_board_plane_distance_m": {
                    f: float((rotation.T @ (p - origin))[2]) for f, p in digits.items()
                },
                "finger_nearest_cap_center_distance_m": {
                    f: float(np.linalg.norm(caps - p, axis=1).min())
                    for f, p in digits.items()
                },
                "minimum_joint_margin_rad": float(margin.min()),
                "closest_limit_joint": names[int(margin.argmin())],
                "worst_cross_digit_proxy_m": worst_distance,
                "worst_cross_digit_pair": worst_pair,
                "musculotendon_lengths_m": d.actuator_length.tolist(),
            }
        )
    palm = np.array([s["palm_world_m"] for s in traces])
    palm_rotations = Rotation.from_quat([s["palm_rotation_board_xyzw"] for s in traces])
    palm_changes = (palm_rotations[:-1].inv() * palm_rotations[1:]).magnitude()
    dofs = digit_dofs(m)
    digit_summary = {}
    for digit in DIGITS:
        free = np.array(
            [s.get("roles", {}).get(digit, "free") == "free" for s in states]
        )
        no_contact = np.array(
            [
                digit not in {c["finger"] for c in s.get("active_contacts", [])}
                for s in states
            ]
        )
        delta = np.diff(q[:, dofs[digit]], axis=0)
        site = np.array([s["finger_sites_world_m"][digit] for s in traces])
        free_edges = free[:-1] & free[1:]
        digit_summary[digit] = {
            "joint_names": [names[i] for i in dofs[digit]],
            "fingertip_path_m": curve_length(site),
            "free_sample_count": int(free.sum()),
            "no_current_contact_sample_count": int(no_contact.sum()),
            "free_joint_total_variation_rad": float(np.abs(delta[free_edges]).sum()),
            "free_fingertip_path_m": float(
                np.linalg.norm(np.diff(site, axis=0)[free_edges], axis=1).sum()
            ),
        }
    worst_index = int(np.argmin([s["worst_cross_digit_proxy_m"] for s in traces]))
    return {
        "version": "whole-hand-untimed-audit-v1",
        "sample_count": len(states),
        "state_sequence_sha256": state_digest(states),
        "joint_names": names,
        "actuator_names": [m.actuator(i).name for i in range(m.nu)],
        "palm_path_m": curve_length(palm),
        "palm_endpoint_displacement_m": float(np.linalg.norm(palm[-1] - palm[0])),
        "palm_rotation_total_rad": float(palm_changes.sum()),
        "maximum_palm_rotation_step_rad": float(palm_changes.max(initial=0)),
        "maximum_joint_step_rad": float(np.abs(np.diff(q, axis=0)).max(initial=0)),
        "joint_descriptors": coordinate_descriptors(q, names),
        "wrist": wrist_descriptors(m, states, names, connected=connected),
        "movement_geometry": {
            "palm_board_normal_minimum_m": min(s["palm_board_m"][2] for s in traces),
            "palm_board_normal_maximum_m": max(s["palm_board_m"][2] for s in traces),
            "palm_path_to_endpoint_displacement_ratio": (
                curve_length(palm) / float(np.linalg.norm(palm[-1] - palm[0]))
                if connected and np.linalg.norm(palm[-1] - palm[0]) > 1e-9
                else None
            ),
            "interpretation": (
                "Untimed geometric relocation/detour descriptors; "
                "no hovering or human smoothness threshold"
            ),
        },
        "digits": digit_summary,
        "minimum_joint_margin_rad": min(s["minimum_joint_margin_rad"] for s in traces),
        "worst_proxy_sample_index": worst_index,
        "worst_proxy_m": traces[worst_index]["worst_cross_digit_proxy_m"],
        "traces": traces,
        "interpretation": (
            "Imported body axes are not a calibrated palmar plane; "
            "cap-center/plane distances are point descriptors, "
            "not collision/press certificates. "
            "No time, effort, comfort or human validity."
        ),
    }


def plots(audit, path: Path, label: str):
    q = np.asarray([s["qpos_rad"] for s in audit["traces"]])
    names = audit["joint_names"]
    rows = audit["traces"]
    trace_svg(
        path,
        label,
        [
            {
                "label": "Wrist and forearm (rad)",
                "series": {
                    n: q[:, names.index(n)]
                    for n in ("flexion_r", "deviation_r", "pro_sup_r")
                },
            },
            {
                "label": "Shoulder coordinates (rad)",
                "series": {
                    n: q[:, names.index(n)]
                    for n in ("elv_angle_r", "shoulder_elv_r", "shoulder_rot_r")
                },
            },
            {
                "label": "Palm/fingertip distance to board base plane (m)",
                "series": {
                    "palm": [s["palm_board_m"][2] for s in rows],
                    **{
                        f: [s["finger_board_plane_distance_m"][f] for s in rows]
                        for f in DIGITS
                    },
                },
            },
            {
                "label": "Unresolved cross-digit proxy signed distance (m)",
                "series": {
                    "worst pair": [s["worst_cross_digit_proxy_m"] for s in rows]
                },
            },
            {
                "label": "Imported proximal digit flexion coordinate (rad)",
                "series": {
                    f: q[:, names.index(audit["digits"][f]["joint_names"][0])]
                    for f in DIGITS
                },
            },
        ],
    )


def run_strategy_audit(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    scene = None
    for case in source["cases"]:
        saved = read_hashed(
            definition.parent / case["search_result"], case["search_sha256"]
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Audit model differs from original recorded model")
        if case["strategy_id"] is not None:
            strategy = next(
                s for s in saved["strategies"] if s["id"] == case["strategy_id"]
            )
            validate_strategy(saved, strategy)
            states = strategy["samples"]
            if not states:
                raise ValueError("Benchmark movement requires complete actual samples")
        else:
            strategy = None
            states = [
                {
                    "qpos_rad": n.get("qpos_rad", n["contact_solve"]["qpos_rad"]),
                    "source_node_id": n["id"],
                    "source_node_status": n["status"],
                    "active_contacts": n["contacts"],
                    "roles": {c["finger"]: "attempted" for c in n["contacts"]},
                }
                for n in saved["nodes"]
            ]
        audit = audit_states(
            scene,
            e.geometry,
            states,
            saved["joint_names"],
            connected=strategy is not None,
        )
        audit["state_kind"] = (
            "connected_sampled_path"
            if strategy
            else "separate_attempted_nodes; not movement"
        )
        if strategy is None:
            for key in (
                "palm_path_m",
                "palm_endpoint_displacement_m",
                "palm_rotation_total_rad",
                "maximum_palm_rotation_step_rad",
                "maximum_joint_step_rad",
            ):
                audit[key] = None
            for descriptor in audit["joint_descriptors"].values():
                descriptor["total_variation_rad"] = None
                descriptor["reversals"] = None
            for descriptor in audit["digits"].values():
                for key in (
                    "fingertip_path_m",
                    "free_joint_total_variation_rad",
                    "free_fingertip_path_m",
                ):
                    descriptor[key] = None
        audit["source_reference"] = case
        audit["first_note_approach"] = {
            "status": "not_planned",
            "source_claim": saved["initial_seed_claim"],
            "reference_initial_joints_rad": saved["scene_input"]["initial_joints_rad"],
        }
        if strategy:
            if abs(audit["palm_path_m"] - strategy["cost_palm_path_m"]) > 1e-10:
                raise ValueError("Saved path cost and compiled FK disagree")
            plots(audit, output / (case["id"] + ".svg"), case["id"])
        cases.append(audit)
    if scene is None:
        raise ValueError("Empty benchmark")
    result = {
        "id": "strategy-audit-045",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "cases": cases,
        "artifact_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.glob("*.svg")
        },
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
