"""Force-balance failure certificates and explicit hypothetical support probes."""

import json
from pathlib import Path
from typing import Any

import myo_sim
import numpy as np
from scipy.linalg import null_space
from scipy.optimize import linprog

from ._engine import mujoco
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .inverse_wrap import inverse_wrap_diagnostic
from .muscle_validation import native_parity
from .muscles import actuator_moment_matrix, length_derivative_check, muscle_snapshot
from .provenance import compiled_model_digest
from .quality_plots import trace_svg
from .render import render_views
from .scene import build_scene
from .wrist_study import finish_record


def balance_certificate(a, b):
    """Separating hyperplane for the bounded active-force polytope A[0,1]."""
    a = np.asarray(a)
    b = np.asarray(b)
    rows, cols = a.shape
    solved = linprog(
        np.r_[-b, np.ones(cols)],
        A_ub=np.c_[a.T, -np.eye(cols)],
        b_ub=np.zeros(cols),
        bounds=[(-1, 1)] * rows + [(0, None)] * cols,
        method="highs",
    )
    if not solved.success:
        raise ValueError("Static infeasibility certificate optimization failed")
    y = solved.x[:rows]
    required = float(y @ b)
    available = float(np.maximum(0, a.T @ y).sum())
    return dict(
        separating_direction=y.tolist(),
        required_projected_work=required,
        maximum_bounded_active_work=available,
        gap=required - available,
        status="bounded_force_map_separated"
        if required - available > 1e-8
        else "no_separation_above_numerical_tolerance",
        interpretation=(
            "Dual numerical infeasibility evidence; covector "
            "normalization is arbitrary, not physical effort"
        ),
    )


def support_diagnostics(scene, snapshot, contacts):
    m, d = scene.model, scene.data
    d.qpos[:] = snapshot["qpos_rad"]
    mujoco.mj_forward(m, d)
    tangent = null_space(np.array(snapshot["equality_jacobian"]), rcond=1e-10)
    moment = np.array(snapshot["transmission_length_derivative_m_per_rad"])
    gain = np.array(snapshot["active_force_per_activation_n"])
    active = tangent.T @ (moment.T * gain)
    gravity = np.array(snapshot["gravity_bias_nm"])
    joint = np.array(snapshot["joint_passive_nm"])
    passive = moment.T @ np.array(snapshot["passive_muscle_force_n"])
    force_balance = gravity - joint - passive
    matrices = {}
    jp = np.zeros((3, m.nv))
    jr = jp.copy()
    mujoco.mj_jacBody(m, d, jp, jr, m.body("capitate_r").id)
    matrices["palm_wrench"] = np.c_[jp.T, jr.T]
    fingertip = []
    for c in contacts:
        jac = np.zeros((3, m.nv))
        mujoco.mj_jacSite(m, d, jac, None, m.site(c["finger"] + "_pad").id)
        fingertip.append(jac.T)
    if fingertip:
        matrices["required_fingertip_forces"] = np.concatenate(fingertip, axis=1)
    reports = []
    for load, b in [
        ("native", force_balance),
        ("gravity_removed_diagnostic", -joint - passive),
        ("passive_muscle_removed_diagnostic", gravity - joint),
        ("joint_passive_removed_diagnostic", gravity - passive),
    ]:
        certificate = balance_certificate(active, tangent.T @ b)
        direction = tangent @ certificate["separating_direction"]
        reports.append(
            dict(
                load=load,
                certificate=certificate,
                joint_covector=dict(
                    zip(
                        [m.joint(i).name for i in range(m.njnt)],
                        direction.tolist(),
                        strict=True,
                    )
                ),
            )
        )
    support = []
    for name, matrix in matrices.items():
        for bounded in (False, True):
            # Explicit synthetic component bounds: 3N forces, .1Nm palm moments.
            bounds = (
                [(-3, 3)] * (matrix.shape[1])
                if bounded
                else [(None, None)] * matrix.shape[1]
            )
            if bounded and name == "palm_wrench":
                bounds[3:] = [(-0.1, 0.1)] * 3
            a = np.c_[active, tangent.T @ matrix]
            b = tangent.T @ force_balance
            solved = linprog(
                np.r_[np.ones(m.nu), np.zeros(matrix.shape[1])],
                A_eq=a,
                b_eq=b,
                bounds=[(0, 1)] * m.nu + bounds,
                method="highs",
            )
            residual = (
                float(np.linalg.norm(a @ solved.x - b)) if solved.success else None
            )
            support.append(
                dict(
                    kind=name,
                    bounds=bounds,
                    status=str(solved.message),
                    numerical_force_balance=bool(
                        solved.success and residual is not None and residual <= 1e-6
                    ),
                    residual_nm=residual,
                    support_components=solved.x[m.nu :].tolist()
                    if solved.success
                    else None,
                    claim=(
                        "Unbounded support is a span diagnostic; bounded "
                        "values are hypothetical sensitivity, not measured "
                        "playing reactions or strength"
                    ),
                )
            )
    return dict(
        equality_position_error_rad=float(
            max(abs(np.array(snapshot["equality_position_residual_rad"])), default=0)
        ),
        decomposition_norm_nm=dict(
            gravity=float(np.linalg.norm(gravity)),
            joint_passive=float(np.linalg.norm(joint)),
            muscle_passive=float(np.linalg.norm(passive)),
        ),
        load_ablations=reports,
        support_scenarios=support,
        muscle_ranking=(
            "withheld; force geometry and load assumptions require validation"
        ),
    )


def route_state(model, data, q, names, muscle):
    data.qpos[[model.joint(n).qposadr[0] for n in names]] = q
    data.qvel[:] = 0
    mujoco.mj_forward(model, data)
    act = model.actuator(muscle).id
    tid = int(model.actuator_trnid[act, 0])
    adr = int(data.ten_wrapadr[tid])
    num = int(data.ten_wrapnum[tid])
    route = []
    for j in range(
        int(model.tendon_adr[tid]), int(model.tendon_adr[tid] + model.tendon_num[tid])
    ):
        kind = int(model.wrap_type[j])
        obj = int(model.wrap_objid[j])
        parameter = float(model.wrap_prm[j])
        part = dict(type=kind, object_id=obj, parameter=parameter)
        if kind in (
            int(mujoco.mjtWrap.mjWRAP_SPHERE),
            int(mujoco.mjtWrap.mjWRAP_CYLINDER),
        ):
            part.update(
                geom=model.geom(obj).name,
                geom_type=int(model.geom_type[obj]),
                geom_size_m=model.geom_size[obj].tolist(),
                geom_world_m=data.geom_xpos[obj].tolist(),
            )
            if parameter >= 0:
                sid = int(parameter)
                local = data.geom_xmat[obj].reshape(3, 3).T @ (
                    data.site_xpos[sid] - data.geom_xpos[obj]
                )
                part.update(
                    sidesite=model.site(sid).name, sidesite_local_m=local.tolist()
                )
        route.append(part)
    return dict(
        qpos_rad=np.asarray(q).tolist(),
        length_m=float(data.actuator_length[act]),
        reported_transmission=actuator_moment_matrix(model, data)[act].tolist(),
        wrap_point_count=num,
        wrap_objects=data.wrap_obj.reshape(-1)[adr : adr + num].tolist(),
        wrap_positions_world_m=data.wrap_xpos.reshape(-1, 3)[adr : adr + num].tolist(),
        compiled_route=route,
    )


def run_muscle_support(definition: Path, output: Path):
    source = json.loads(definition.read_text())
    old = read_hashed(
        definition.parent / source["muscle_result"], source["muscle_sha256"]
    )
    seed = read_hashed(definition.parent / source["seed_result"], source["seed_sha256"])
    e = Experiment.from_dict(old["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if compiled_model_digest(scene.model) != old["provenance"]["compiled_model_sha256"]:
        raise ValueError("Muscle support changed anatomy")
    output.mkdir(parents=True, exist_ok=True)
    native = myo_sim.load_spec("myoarm_r").compile()
    nd = mujoco.MjData(native)
    names = old["joint_names"]
    poses: list[dict[str, Any]] = []
    routes: list[dict[str, Any]] = []
    requested = [
        dict(id=p["id"], qpos_rad=p["qpos_rad"], contacts=[])
        for p in seed["poses"]
        if p["id"] == "resolved-playing-seed"
    ]
    requested.append(
        dict(id="native-default", qpos_rad=scene.model.qpos0.tolist(), contacts=[])
    )
    requested.extend(
        dict(
            id=p["pose"]["id"],
            qpos_rad=p["pose"]["qpos_rad"],
            contacts=p["pose"]["contacts"],
        )
        for p in old["poses"]
        if p["pose"]["id"] in source["pose_ids"]
    )
    for p in requested:
        snapshot = muscle_snapshot(scene, p["qpos_rad"])
        diagnostic = support_diagnostics(scene, snapshot, p["contacts"])
        if diagnostic["equality_position_error_rad"] > 1e-8:
            raise ValueError("Static investigation requires equality-consistent poses")
        poses.append(
            dict(
                pose=p,
                snapshot=snapshot,
                diagnostics=diagnostic,
                length_derivative_check=length_derivative_check(scene, p["qpos_rad"]),
                native_parity=native_parity(scene.model, native, nd, snapshot, names),
            )
        )
    for selected in source["route_cases"]:
        probe = next(p for p in old["routing_probes"] if p["case_id"] == selected)
        muscle = probe["muscle"]
        points = probe["diagnostic_probes"]
        j = int(np.argmax(abs(np.diff([p["reduced_length_m"] for p in points]))))
        low = points[j]["fraction"]
        high = points[j + 1]["fraction"]
        a = np.array(points[0]["qpos_rad"])
        b = np.array(points[-1]["qpos_rad"])
        for _ in range(30):
            mid = (low + high) / 2
            left = route_state(native, nd, a + low * (b - a), names, muscle)["length_m"]
            right = route_state(native, nd, a + high * (b - a), names, muscle)[
                "length_m"
            ]
            v = route_state(native, nd, a + mid * (b - a), names, muscle)["length_m"]
            if abs(v - left) < abs(v - right):
                low = mid
            else:
                high = mid
        pair: list[dict[str, Any]] = []
        for side, fraction in [("before", low), ("after", high)]:
            q = a + fraction * (b - a)
            n = route_state(native, nd, q, names, muscle)
            reduced = route_state(scene.model, scene.data, q, names, muscle)
            reduced["inverse_wrap_diagnostic"] = inverse_wrap_diagnostic(
                scene.model, scene.data, muscle + "_tendon"
            )
            n["inverse_wrap_diagnostic"] = inverse_wrap_diagnostic(
                native, nd, muscle + "_tendon"
            )
            entry = dict(side=side, fraction=fraction, native=n, reduced=reduced)
            directory = output / f"{selected}-{side}"
            target = e.geometry.surface_world_m(button_at(1, 5)).tolist()
            cams = render_views(
                scene,
                directory,
                target,
                "r1c5",
                collision_overlay=True,
                state_label=f"{muscle} | {side} branch diagnostic; not movement",
                camera_overrides=source["cameras"],
                highlighted_tendon_names=(muscle + "_tendon",),
            )
            entry["media"] = dict(
                directory=directory.name,
                cameras=cams,
                qpos_rad=q.tolist(),
                active_contacts=[],
            )
            pair.append(entry)
        routes.append(
            dict(
                case_id=selected,
                muscle=muscle,
                original_sample_pair=probe["original_sample_pair"],
                fraction_gap=high - low,
                length_jump_m=abs(
                    pair[1]["native"]["length_m"] - pair[0]["native"]["length_m"]
                ),
                states=pair,
                interpretation=(
                    "Bisection probes are off-trajectory diagnostics, "
                    "never movement frames"
                ),
            )
        )
    trace_svg(
        output / "support.svg",
        "Conditional support probes and load decomposition",
        [
            dict(
                label="Generalized force norms (Nm)",
                series={
                    k: [p["diagnostics"]["decomposition_norm_nm"][k] for p in poses]
                    for k in ("gravity", "joint_passive", "muscle_passive")
                },
            ),
            dict(
                label=(
                    "Bounded active-force separation gap; arbitrary "
                    "covector normalization"
                ),
                series={
                    load: [
                        next(
                            r["certificate"]["gap"]
                            for r in p["diagnostics"]["load_ablations"]
                            if r["load"] == load
                        )
                        for p in poses
                    ]
                    for load in (
                        "native",
                        "gravity_removed_diagnostic",
                        "passive_muscle_removed_diagnostic",
                        "joint_passive_removed_diagnostic",
                    )
                },
            ),
        ],
        x_axis="independent static pose index; not a trajectory",
    )
    route_diagnostics = [
        d
        for r in routes
        for state in r["states"]
        for d in state["native"]["inverse_wrap_diagnostic"]
    ]
    trace_svg(
        output / "inverse-wrap.svg",
        "Native inverse-wrap root/fallback diagnostics",
        [
            dict(
                label="Native point discrepancy (m)",
                series={
                    "independent scalar root": [
                        d["native_to_root_distance_m"] for d in route_diagnostics
                    ],
                    "native fallback average": [
                        d["native_to_fallback_distance_m"] for d in route_diagnostics
                    ],
                },
            ),
            dict(
                label="Signed residual at pinned inverse-wrap initial z",
                series={
                    "residual": [
                        d["residual_at_pinned_initial_z"] for d in route_diagnostics
                    ],
                },
            ),
        ],
        x_axis="PQ before/after, DELT3 before/after; independent probes, not movement",
    )
    errors = {}
    for audit in old["motion_derivative_audits"]:
        for name, error in audit["per_actuator_maximum_error_m_per_rad"].items():
            errors[name] = max(errors.get(name, 0), error)
    for pose in old["poses"] + poses:
        for name, error in zip(
            pose["snapshot"]["actuator_names"],
            pose["length_derivative_check"]["per_actuator_maximum_error_m_per_rad"],
            strict=True,
        ):
            errors[name] = max(errors.get(name, 0), error)
    subset = dict(
        numerical_tolerance_m_per_rad=1e-7,
        excluded_actuators={n: e for n, e in errors.items() if e > 1e-7},
        passed_tested_probes=[n for n, e in errors.items() if e <= 1e-7],
        scope=(
            "Native parity and sampled local derivative probes; "
            "no global route or human capacity validation"
        ),
        usable_quantities="Routed lengths/local transmissions; no effort ranking",
    )
    return finish_record(
        definition,
        output,
        source,
        dict(
            id="muscle-support-051",
            poses=poses,
            routes=routes,
            operating_quantity_subset=subset,
            muscle_ranking="withheld",
        ),
        scene,
    )
