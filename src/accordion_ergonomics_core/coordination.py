"""Independent cross-digit envelope and free-finger sensitivity diagnostics."""

import json
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np

from ._engine import mujoco
from .anatomy import digit_dofs
from .collision_coverage import audit_collision_coverage
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .hand_audit import hand_pairs
from .instrument import button_at
from .movement_evidence import state_digest
from .provenance import compiled_model_digest
from .quality_plots import trace_svg
from .render import render_views
from .scene import build_scene
from .wrist_study import finish_record


def coordination_audit(scene, states, *, connected=True):
    m, d = scene.model, scene.data
    q = np.array([s["qpos_rad"] for s in states])
    if not states or q.shape != (len(states), m.nq) or not np.isfinite(q).all():
        raise ValueError("Coordination audit needs finite saved configurations")
    pairs = [
        p
        for p in hand_pairs(scene)
        if p["classification"] == "cross_digit_phalangeal_unresolved"
    ]
    d.qpos[:] = m.qpos0
    mujoco.mj_forward(m, d)
    baseline = np.array(
        [mujoco.mj_geomDistance(m, d, *p["geom_ids"], 1, None) for p in pairs]
    )
    minima = np.full(len(pairs), np.inf)
    indices = np.zeros(len(pairs), dtype=int)
    groups = {"/".join(sorted(pair)): [] for pair in combinations(DIGITS, 2)}
    for i, p in enumerate(pairs):
        groups["/".join(sorted(p["digits"]))].append(i)
    traces = []
    distances = []
    for index, state in enumerate(states):
        d.qpos[:] = state["qpos_rad"]
        mujoco.mj_forward(m, d)
        values = np.array(
            [mujoco.mj_geomDistance(m, d, *p["geom_ids"], 1, None) for p in pairs]
        )
        replace = values < minima
        minima[replace] = values[replace]
        indices[replace] = index
        distances.append(values)
        traces.append(
            dict(
                sample_index=index,
                group_minimum_m={
                    g: float(values[ids].min()) for g, ids in groups.items() if ids
                },
                maximum_increase_over_imported_overlap_m=float(
                    np.maximum(
                        0, np.maximum(0, -values) - np.maximum(0, -baseline)
                    ).max()
                ),
            )
        )
    records: list[dict[str, Any]] = []
    for i, p in enumerate(pairs):
        d.qpos[:] = states[int(indices[i])]["qpos_rad"]
        mujoco.mj_forward(m, d)
        details = []
        for geom in p["geom_ids"]:
            body = int(m.geom_bodyid[geom])
            details.append(
                dict(
                    geom=m.geom(geom).name,
                    geom_type=int(m.geom_type[geom]),
                    size_m=m.geom_size[geom].tolist(),
                    body=m.body(body).name,
                    parent=m.body(int(m.body_parentid[body])).name,
                    body_world_m=d.xpos[body].tolist(),
                    body_axes_world=d.xmat[body].reshape(3, 3).tolist(),
                    geom_world_m=d.geom_xpos[geom].tolist(),
                    underlying_meshes=[
                        m.geom(j).name
                        for j in range(m.ngeom)
                        if m.geom_bodyid[j] == body
                        and m.geom_type[j] == mujoco.mjtGeom.mjGEOM_MESH
                    ],
                )
            )
        records.append(
            {k: v for k, v in p.items() if k != "geom_ids"}
            | dict(
                minimum_m=float(minima[i]),
                sample_index=int(indices[i]),
                imported_default_distance_m=float(baseline[i]),
                geometry_at_worst=details,
            )
        )
    q = np.array([s["qpos_rad"] for s in states])
    dofs = digit_dofs(m)
    digits = {}
    for digit, ids in dofs.items():
        free = np.array(
            [s.get("roles", {}).get(digit, "free") == "free" for s in states]
        )
        delta = abs(np.diff(q[:, ids], axis=0))
        edges = free[:-1] & free[1:]
        ranges = m.jnt_range[list(ids)]
        digits[digit] = dict(
            joint_names=[m.joint(i).name for i in ids],
            free_sample_count=int(free.sum()),
            free_joint_variation_rad=float(delta[edges].sum()) if connected else None,
            maximum_free_step_rad=float(delta[edges].max(initial=0))
            if connected
            else None,
            minimum_limit_margin_rad=float(
                np.minimum(q[:, ids] - ranges[:, 0], ranges[:, 1] - q[:, ids]).min()
            ),
            minimum_rad=q[:, ids].min(axis=0).tolist(),
            maximum_rad=q[:, ids].max(axis=0).tolist(),
            trace_rad=q[:, ids].tolist(),
        )
    group_worst = {
        g: min(
            (r for r in records if "/".join(sorted(r["digits"])) == g),
            key=lambda r: r["minimum_m"],
        )
        for g, ids in groups.items()
        if ids
    }
    worst = min(records, key=lambda r: r["minimum_m"])
    d.qpos[:] = states[worst["sample_index"]]["qpos_rad"]
    return dict(
        version="coordination-proxy-v1",
        state_sequence_sha256=state_digest(states),
        sample_count=len(states),
        pair_minima=records,
        group_worst=group_worst,
        digits=digits,
        traces=traces,
        collision_coverage_at_worst=audit_collision_coverage(scene),
        collision_validity="configured checks separate; cross-digit anatomy unresolved",
        baseline_interpretation=(
            "Imported qpos0 overlap is a diagnostic control, "
            "not a permitted-overlap calibration"
        ),
        interpretation=(
            "Rigid envelopes versus body/bone frames; no tissue thickness "
            "calibration or biological coupling ratio. Free-finger movement "
            "is solver behavior, not validated human coordination."
        ),
    )


def run_coordination_study(definition: Path, output: Path):
    source = json.loads(definition.read_text())
    wrist = read_hashed(
        definition.parent / source["wrist_result"], source["wrist_sha256"]
    )
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    scene = None
    cameras = source["cameras"]
    for case in wrist["cases"]:
        request = case["source"]
        saved = read_hashed(
            definition.parent / request["search_result"], request["search_sha256"]
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        if compiled_model_digest(scene.model) != case["compiled_model_sha256"]:
            raise ValueError("Coordination changed recorded model")
        if case["strategy_id"]:
            strategy = next(
                s for s in saved["strategies"] if s["id"] == case["strategy_id"]
            )
            states = strategy["samples"]
        else:
            states = [
                dict(
                    qpos_rad=n.get("qpos_rad", n["contact_solve"]["qpos_rad"]),
                    active_contacts=n["contacts"],
                    roles={c["finger"]: "attempted" for c in n["contacts"]},
                )
                for n in saved["nodes"]
            ]
        if state_digest(states) != case["state_sequence_sha256"]:
            raise ValueError("Coordination states differ from wrist evidence")
        audit = coordination_audit(scene, states, connected=bool(case["strategy_id"]))
        directory = output / case["id"]
        directory.mkdir()
        trace_svg(
            directory / "coordination.svg",
            case["id"] + " | untimed samples",
            [
                dict(
                    label="Cross-digit group signed rigid-proxy minima (m)",
                    series={
                        g: [t["group_minimum_m"][g] for t in audit["traces"]]
                        for g in audit["group_worst"]
                    },
                ),
                dict(
                    label="Proximal finger coordinate (rad); coordination unvalidated",
                    series={
                        digit: [q[0] for q in audit["digits"][digit]["trace_rad"]]
                        for digit in DIGITS
                    },
                ),
            ],
        )
        media = []
        if case["id"] in source["render_cases"]:
            selected = [
                audit["group_worst"][g]
                for g in ("middle/ring", "little/ring", "index/thumb")
            ]
            for pair in selected:
                index = pair["sample_index"]
                state = states[index]
                scene.data.qpos[:] = state["qpos_rad"]
                contacts = (
                    state.get("active_contacts")
                    or saved["strategies"][0]["events"][-1]["contacts"]
                )
                c = contacts[0]
                label = "/".join(sorted(pair["digits"]))
                sub = f"{label.replace('/', '-')}-state-{index}"
                actual = render_views(
                    scene,
                    directory / sub,
                    e.geometry.surface_world_m(
                        button_at(c["row"], c["column"])
                    ).tolist(),
                    c["button_id"],
                    collision_overlay=True,
                    highlighted_proxy_names=tuple(pair["geoms"]),
                    contact_roles=state.get("roles", {}),
                    state_label=(
                        f"{case['id']} | {label} | exact sample {index} | "
                        "unresolved envelope"
                    ),
                    camera_overrides=cameras,
                )
                media.append(
                    dict(
                        directory=f"{case['id']}/{sub}",
                        sample_index=index,
                        qpos_rad=state["qpos_rad"],
                        active_contacts=state.get("active_contacts", []),
                        roles=state.get("roles", {}),
                        cameras=actual,
                        pair=pair,
                    )
                )
        reports.append(
            dict(
                id=case["id"],
                source=case["source"],
                strategy_id=case["strategy_id"],
                audit=audit,
                media=media,
            )
        )
    if scene is None:
        raise ValueError("Empty coordination benchmark")
    return finish_record(
        definition,
        output,
        source,
        dict(id="coordination-study-050", cases=reports),
        scene,
    )
