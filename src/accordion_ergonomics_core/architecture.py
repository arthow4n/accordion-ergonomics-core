"""Reproducible anatomical parity, runtime benchmarks and saved-state views."""

import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from time import perf_counter

import myo_sim
import numpy as np
from PIL import Image

from ._engine import mujoco
from .cli import load_input
from .full_body import (
    COLLISION_POLICY,
    FullBodyPosture,
    build_full_body,
    prescribed_pose,
    right_joint_names,
)
from .instrument import button_at
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene, coupled_initial_pose


def timed(operation, batches, iterations=1):
    samples = []
    for _ in range(batches):
        start = perf_counter()
        for _ in range(iterations):
            operation()
        samples.append((perf_counter() - start) / iterations)
    return {"samples_s": samples, "median_s": float(np.median(samples))}


def subtree(model, name):
    root = model.body(name).id
    ids = {root}
    for i in range(root + 1, model.nbody):
        if int(model.body_parentid[i]) in ids:
            ids.add(i)
    return ids


def compare_right_arm(reference, candidate, configurations):
    """Name-bound coordinates verified against fields, FK and both Jacobians."""
    a, b = reference.model, candidate.model
    names = right_joint_names()
    fields = ("jnt_type", "jnt_axis", "jnt_pos", "jnt_range", "jnt_limited")
    field_errors = {}
    for field in fields:
        field_errors[field] = float(
            max(
                np.max(
                    np.abs(
                        np.asarray(getattr(a, field)[a.joint(n).id], dtype=float)
                        - np.asarray(getattr(b, field)[b.joint(n).id], dtype=float)
                    )
                )
                for n in names
            )
        )
    coupling_errors = []
    coupling_links = []
    for i in range(a.neq):
        ea, eb = a.equality(i), b.equality(a.equality(i).name)
        coupling_errors.append(float(np.max(abs(ea.data - eb.data))))
        for field in ("obj1id", "obj2id"):
            ja, jb = int(getattr(ea, field)[0]), int(getattr(eb, field)[0])
            coupling_links.append(a.joint(ja).name == b.joint(jb).name)
    bodies = [a.body(i).name for i in subtree(a, "myoarm_r_root")]
    geoms = [
        a.geom(i).name
        for i in range(a.ngeom)
        if int(a.geom_bodyid[i]) in subtree(a, "myoarm_r_root")
    ]
    geom_field_errors = {}
    for field in (
        "geom_type",
        "geom_size",
        "geom_pos",
        "geom_quat",
        "geom_contype",
        "geom_conaffinity",
    ):
        geom_field_errors[field] = float(
            max(
                np.max(
                    abs(
                        getattr(a, field)[a.geom(n).id]
                        - getattr(b, field)[b.geom(n).id]
                    )
                )
                for n in geoms
            )
        )
    muscle_errors = {}
    for field in (
        "actuator_gainprm",
        "actuator_biasprm",
        "actuator_dynprm",
        "actuator_lengthrange",
    ):
        muscle_errors[field] = float(
            max(
                np.max(
                    abs(
                        getattr(a, field)[i]
                        - getattr(b, field)[b.actuator(a.actuator(i).name).id]
                    )
                )
                for i in range(a.nu)
            )
        )
    mesh_hashes = []
    for name in geoms:
        ai, bi = (
            int(a.geom_dataid[a.geom(name).id]),
            int(b.geom_dataid[b.geom(name).id]),
        )
        if ai < 0:
            continue
        av = a.mesh_vert[a.mesh_vertadr[ai] : a.mesh_vertadr[ai] + a.mesh_vertnum[ai]]
        bv = b.mesh_vert[b.mesh_vertadr[bi] : b.mesh_vertadr[bi] + b.mesh_vertnum[bi]]
        af = a.mesh_face[a.mesh_faceadr[ai] : a.mesh_faceadr[ai] + a.mesh_facenum[ai]]
        bf = b.mesh_face[b.mesh_faceadr[bi] : b.mesh_faceadr[bi] + b.mesh_facenum[bi]]
        mesh_hashes.append(
            {
                "geom": name,
                "vertices_match": np.array_equal(av, bv),
                "faces_match": np.array_equal(af, bf),
            }
        )
    dofa = [int(a.joint(n).dofadr[0]) for n in names]
    dofb = [int(b.joint(n).dofadr[0]) for n in names]
    records = []
    for values in configurations:
        reference.data.qpos[:] = coupled_initial_pose(a, values)
        mapped = {n: float(reference.data.qpos[a.joint(n).qposadr[0]]) for n in names}
        candidate.data.qpos[:] = prescribed_pose(
            b, {**candidate.prescribed_joints, **mapped}
        )
        mujoco.mj_forward(a, reference.data)
        mujoco.mj_forward(b, candidate.data)
        errors = {
            "body_position_m": max(
                float(
                    np.max(
                        abs(reference.data.body(n).xpos - candidate.data.body(n).xpos)
                    )
                )
                for n in bodies
            ),
            "body_rotation_matrix": max(
                float(
                    np.max(
                        abs(reference.data.body(n).xmat - candidate.data.body(n).xmat)
                    )
                )
                for n in bodies
            ),
            "geom_position_m": max(
                float(
                    np.max(
                        abs(reference.data.geom(n).xpos - candidate.data.geom(n).xpos)
                    )
                )
                for n in geoms
            ),
            "geom_rotation_matrix": max(
                float(
                    np.max(
                        abs(reference.data.geom(n).xmat - candidate.data.geom(n).xmat)
                    )
                )
                for n in geoms
            ),
            "pad_position_m": float(
                np.max(
                    abs(
                        reference.data.site("index_pad").xpos
                        - candidate.data.site("index_pad").xpos
                    )
                )
            ),
            "pad_rotation_matrix": float(
                np.max(
                    abs(
                        reference.data.site("index_pad").xmat
                        - candidate.data.site("index_pad").xmat
                    )
                )
            ),
        }
        ja, ra = np.zeros((3, a.nv)), np.zeros((3, a.nv))
        jb, rb = np.zeros((3, b.nv)), np.zeros((3, b.nv))
        mujoco.mj_jacSite(a, reference.data, ja, ra, a.site("index_pad").id)
        mujoco.mj_jacSite(b, candidate.data, jb, rb, b.site("index_pad").id)
        errors["jacobian_position"] = float(np.max(abs(ja[:, dofa] - jb[:, dofb])))
        errors["jacobian_rotation"] = float(np.max(abs(ra[:, dofa] - rb[:, dofb])))
        errors["right_tendon_length_m"] = max(
            float(
                abs(
                    reference.data.ten_length[i]
                    - candidate.data.ten_length[b.tendon(a.tendon(i).name).id]
                )
            )
            for i in range(a.ntendon)
        )
        records.append({"independent_input_rad": values, "errors": errors})
    return {
        "coordinate_map": [
            {"name": n, "reference_dof": x, "candidate_dof": y}
            for n, x, y in zip(names, dofa, dofb, strict=True)
        ],
        "joint_field_max_errors": field_errors,
        "muscle_parameter_max_errors": muscle_errors,
        "bone_mesh_identity": mesh_hashes,
        "geom_field_max_errors": geom_field_errors,
        "coupling_max_error": max(coupling_errors),
        "coupling_links_match": all(coupling_links),
        "bodies_checked": len(bodies),
        "geoms_checked": len(geoms),
        "configurations": records,
        "max_errors": {
            k: max(r["errors"][k] for r in records) for k in records[0]["errors"]
        },
    }


def passive_envelope_audit(scene):
    """Independent cross-region queries on unchanged native proxies.

    Adjacent skeleton/support proxies can overlap intentionally. These are
    coverage evidence, not a new blanket anatomical collision policy.
    """
    from itertools import combinations

    m, d = scene.model, scene.data
    mujoco.mj_forward(m, d)
    names = {m.body(i).name for i in range(m.nbody)}
    if "myoarm_l_root" not in names:
        return {"available": False, "reason": "Historical scene lacks left anatomy"}
    right = subtree(m, "myoarm_r_root")
    left = subtree(m, "myoarm_l_root")
    legs = subtree(m, "myolegs_root")

    def region(i):
        body = int(m.geom_bodyid[i])
        return (
            "right"
            if body in right
            else "left"
            if body in left
            else "legs"
            if body in legs
            else "torso_head"
        )

    proxies = [i for i in range(m.ngeom) if m.geom_group[i] == 4]
    explicit = {
        frozenset((int(a), int(b)))
        for a, b in zip(m.pair_geom1, m.pair_geom2, strict=True)
    }
    upstream_pairs = {
        frozenset((p.geomname1, p.geomname2))
        for p in myo_sim.load_spec("myofullbody").pairs
    }
    minimums = {}
    overlaps = []
    count = 0
    for a, b in combinations(proxies, 2):
        ra, rb = region(a), region(b)
        if ra == rb or {ra, rb} == {"right", "torso_head"}:
            continue
        count += 1
        distance = float(mujoco.mj_geomDistance(m, d, a, b, 1.0, None))
        key = "/".join(sorted((ra, rb)))
        minimums[key] = min(distance, minimums.get(key, 1.0))
        if distance < 0:
            overlaps.append(
                {
                    "geoms": [m.geom(a).name, m.geom(b).name],
                    "regions": [ra, rb],
                    "geom_ids": [a, b],
                    "bodies": [m.body(int(m.geom_bodyid[i])).name for i in (a, b)],
                    "upstream_explicit_pair": frozenset(
                        (m.geom(a).name, m.geom(b).name)
                    )
                    in upstream_pairs,
                    "signed_distance_m": distance,
                    "explicit_pair": frozenset((a, b)) in explicit,
                }
            )
    return {
        "available": True,
        "proxy_count": len(proxies),
        "cross_region_pairs_queried": count,
        "minimum_distances_m": minimums,
        "overlaps": overlaps,
        "claim": (
            "Uncalibrated rigid envelope overlaps; within-region and "
            "continuous coverage remain incomplete"
        ),
    }


def render_body(scene, output, cameras=None):
    """Skeleton-only views. Hide research fixture without changing its model."""
    output.mkdir(parents=True, exist_ok=True)
    m, d = scene.model, scene.data
    mujoco.mj_forward(m, d)
    if cameras is None:
        root = d.body("Full Body").xpos.copy()
        center = root + np.array([0, 0.12, 0.08])
        cameras = {
            "front": dict(
                lookat=center.tolist(), distance=2.05, azimuth=-90, elevation=0
            ),
            "right": dict(
                lookat=center.tolist(), distance=2.05, azimuth=180, elevation=0
            ),
            "left": dict(lookat=center.tolist(), distance=2.05, azimuth=0, elevation=0),
            "oblique": dict(
                lookat=center.tolist(), distance=2.05, azimuth=-125, elevation=-15
            ),
            "hand": dict(
                lookat=(
                    (d.body("lunate_r").xpos + d.body("distph3_r").xpos) / 2
                ).tolist(),
                distance=0.38,
                azimuth=-65,
                elevation=-25,
            ),
        }
    groups = m.geom_group.copy()
    before = compiled_model_digest(m)
    try:
        for i in range(m.ngeom):
            if (
                m.geom(i).name.startswith("approximate_")
                or int(m.geom_bodyid[i]) == m.body("keyboard").id
                or int(m.geom_bodyid[i]) == 0
            ):
                m.geom_group[i] = 5
        option = mujoco.MjvOption()
        option.geomgroup[:] = 0
        option.geomgroup[0] = 1
        option.sitegroup[:] = 0
        option.flags[mujoco.mjtVisFlag.mjVIS_TENDON] = False
        with mujoco.Renderer(m, height=720, width=960) as renderer:
            for name, settings in cameras.items():
                camera = mujoco.MjvCamera()
                for key, value in settings.items():
                    setattr(camera, key, value)
                renderer.update_scene(d, camera=camera, scene_option=option)
                renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SKYBOX] = False
                Image.fromarray(renderer.render()).save(output / f"{name}.png")
    finally:
        m.geom_group[:] = groups
    if compiled_model_digest(m) != before:
        raise ValueError("Body rendering changed model identity")
    return cameras


def replay_body(result_path, output):
    record = json.loads(result_path.read_text())
    e = load_input(result_path.parent / "experiment.json")
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    if compiled_model_digest(s.model) != record["provenance"]["compiled_model_sha256"]:
        raise ValueError("Compiled anatomy differs from saved state")
    s.data.qpos[:] = record["qpos_rad"]
    cameras = render_body(s, output, record["body_cameras"])
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "saved_result_sha256": hashlib.sha256(
                    result_path.read_bytes()
                ).hexdigest(),
                "cameras": cameras,
                **current_execution_metadata(s.model),
            },
            indent=2,
        )
        + "\n"
    )


def rss_bytes():
    for line in Path("/proc/self/status").read_text().splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("Linux RSS unavailable")


def benchmark_worker(definition, assembly, batches, iterations):
    """One isolated process per architecture, warm imports and repeated samples."""
    from .collision_coverage import audit_collision_coverage
    from .solver import solve_contact

    e = load_input(definition)
    p = replace(e.player, model=assembly, full_body_posture=None)
    baseline_rss = rss_bytes()
    build = timed(
        lambda: build_scene(e.geometry, p, e.setup, e.physical_contact), batches
    )
    s = build_scene(e.geometry, p, e.setup, e.physical_contact)
    retained_rss = rss_bytes()
    m, d = s.model, s.data
    if assembly == "myoarm_r":
        from .lower_body import attach_fixed_lower_body

        spec = myo_sim.load_spec("myoarm_r")
        spec.body("Full Body").pos = list(e.setup.torso_origin_m)
        spec.body("Full Body").quat = list(e.setup.torso_rotation_wxyz)
        attach_fixed_lower_body(spec, e.setup)
    else:
        spec, _, _ = build_full_body(assembly, e.setup, FullBodyPosture())
    compile_time = timed(spec.compile, batches)
    d.qpos[:] = coupled_initial_pose(m, {**s.prescribed_joints, **e.initial_joints_rad})
    mujoco.mj_forward(m, d)
    jp, jr = np.zeros((3, m.nv)), np.zeros((3, m.nv))

    def jac():
        mujoco.mj_jacSite(m, d, jp, jr, m.site("index_pad").id)

    fk = timed(lambda: mujoco.mj_kinematics(m, d), batches, iterations)
    forward = timed(lambda: mujoco.mj_forward(m, d), batches, iterations)
    jac()  # prerequisite FK/comPos already evaluated by forward
    jacobian = timed(jac, batches, iterations)
    pairs = [(g, b) for g in s.anatomy_geoms for b in s.board_geoms]

    def distances():
        for a, b in pairs:
            mujoco.mj_geomDistance(m, d, a, b, 1.0, None)

    collision = timed(distances, batches, max(1, iterations // 100))
    solves = []
    target = e.geometry.surface_world_m(button_at(1, 5))
    for _ in range(batches):
        start = perf_counter()
        r = solve_contact(s, target, e.initial_joints_rad, e.solver)
        solves.append(
            {
                "elapsed_s": perf_counter() - start,
                "status": r["status"],
                "iterations": len(r["solver_history"]),
                "failure": r["failure"],
                "diagnostics": r["diagnostics"],
                "qpos_rad": r["qpos_rad"],
                "frozen_dof_indices": r["frozen_dof_indices"],
            }
        )
    # Synthetic local relocation retains the actual solver and collision checks.
    seed = {n: float(d.qpos[m.joint(n).qposadr[0]]) for n in right_joint_names()}
    point = d.site("index_pad").xpos.copy() + np.array([0.002, 0, 0])
    local = []
    for _ in range(batches):
        start = perf_counter()
        r = solve_contact(s, point, seed, e.solver, contact_required=False)
        local.append(
            {
                "elapsed_s": perf_counter() - start,
                "status": r["status"],
                "iterations": len(r["solver_history"]),
                "failure": r["failure"],
                "diagnostics": r["diagnostics"],
            }
        )
    import tempfile

    with tempfile.TemporaryDirectory() as t:
        rendering = timed(lambda: render_body(s, Path(t)), batches)
    return {
        "assembly": assembly,
        "collision_policy": COLLISION_POLICY,
        "dimensions": {
            k: int(getattr(m, k))
            for k in (
                "nq",
                "nv",
                "njnt",
                "nu",
                "ntendon",
                "neq",
                "npair",
                "nbody",
                "ngeom",
            )
        },
        "compiled_mjb_bytes": int(mujoco.mj_sizeModel(m)),
        "model_buffer_bytes": int(m.nbuffer),
        "configured_data_arena_bytes": int(m.narena),
        "rss_baseline_bytes": baseline_rss,
        "rss_after_repeated_build_bytes": retained_rss,
        "peak_rss_bytes": int(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        ),
        "right_coordinates": len(right_joint_names()),
        "qp_variable_dimension": m.nv,
        "index_nonfrozen_coordinates": m.nv - len(s.passive_joints) - 16,
        "index_independent_coordinates_after_equalities": 11,
        "passive_coordinates_frozen": len(s.passive_joints),
        "setup_build": build,
        "anatomy_only_compile": compile_time,
        "kinematics": fk,
        "full_forward": forward,
        "right_pad_jacobian": jacobian,
        "collision_query_all_right_fixture_pairs": collision,
        "distance_pairs": len(pairs),
        "five_view_render": rendering,
        "representative_c4_solves": solves,
        "synthetic_2mm_relocations": local,
        "coverage": audit_collision_coverage(s),
        **current_execution_metadata(m),
    }


def inspect_upstream():
    records = []
    for name in (
        "myoarm_r",
        "myoarms",
        "myolegs",
        "myotorso",
        "myotorso_arm_r",
        "myotorso_arms",
        "myofullbody",
    ):
        m = myo_sim.load_spec(name).compile()
        records.append(
            {
                "name": name,
                "dimensions": {
                    k: int(getattr(m, k))
                    for k in (
                        "nq",
                        "nv",
                        "njnt",
                        "nu",
                        "ntendon",
                        "neq",
                        "npair",
                        "nbody",
                    )
                },
                "root_pos_m": m.body("Full Body").pos.tolist(),
                "joints": [
                    {
                        "name": m.joint(i).name,
                        "type": int(m.jnt_type[i]),
                        "qposadr": int(m.jnt_qposadr[i]),
                        "dofadr": int(m.jnt_dofadr[i]),
                        "range": m.jnt_range[i].tolist(),
                    }
                    for i in range(m.njnt)
                ],
                "equalities": [
                    {
                        "name": m.equality(i).name,
                        "a": m.joint(int(m.eq_obj1id[i])).name,
                        "b": m.joint(int(m.eq_obj2id[i])).name
                        if m.eq_obj2id[i] >= 0
                        else None,
                        "coefficients": m.eq_data[i, :5].tolist(),
                    }
                    for i in range(m.neq)
                ],
                "parent_map": {
                    m.body(i).name: m.body(int(m.body_parentid[i])).name
                    for i in range(1, m.nbody)
                },
                "compiled_model_sha256": compiled_model_digest(m),
            }
        )
    return records


def run_architecture(definition, output):
    """Inputs are copied into each architecture record for independent replay."""
    raw = definition.read_bytes()
    config = json.loads(raw)
    source = definition.parent / config["reference_input"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != config["reference_sha256"]:
        raise ValueError("Reference experiment hash mismatch")
    e = load_input(source)
    output.mkdir(parents=True, exist_ok=True)
    from .cli import run_experiment
    from .collision_coverage import audit_collision_coverage
    from .scene import diagnostics

    assemblies = ("myoarm_r", "myofullbody_native", "myofullbody_reduced")
    reference = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    configurations = [{}, e.initial_joints_rad]
    rng = np.random.default_rng(config["seed"])
    for _ in range(config["parity_samples"]):
        configurations.append(
            {
                "elv_angle_r": float(rng.uniform(-0.8, 0.8)),
                "shoulder_elv_r": float(rng.uniform(0.05, 1.2)),
                "shoulder_rot_r": float(rng.uniform(-0.8, 0.8)),
                "elbow_flexion_r": float(rng.uniform(0.2, 2.0)),
                "pro_sup_r": float(rng.uniform(-1.0, 1.0)),
                "deviation_r": float(rng.uniform(-0.1, 0.3)),
                "flexion_r": float(rng.uniform(-0.6, 0.6)),
                **{
                    n: float(rng.uniform(*reference.model.joint(n).range[0]))
                    for n in ()
                },
                **{
                    n: float(rng.uniform(0.05, 1.2))
                    for n in (
                        "mcp2_flexion_r",
                        "pm2_flexion_r",
                        "md2_flexion_r",
                        "mcp3_flexion_r",
                        "pm3_flexion_r",
                        "md3_flexion",
                        "mcp4_flexion_r",
                        "pm4_flexion",
                        "md4_flexion_r",
                        "mcp5_flexion_r",
                        "pm5_flexion_r",
                        "md5_flexion_r",
                    )
                },
                "cmc_flexion": float(rng.uniform(-0.5, 0.5)),
                "cmc_abduction": float(rng.uniform(-0.3, 0.5)),
                "mp_flexion_r": float(rng.uniform(-0.5, 0.5)),
                "ip_flexion_r": float(rng.uniform(-1.0, 0.3)),
            }
        )
    parity = {}
    for assembly in assemblies[1:]:
        candidate = build_scene(
            e.geometry, replace(e.player, model=assembly), e.setup, e.physical_contact
        )
        parity[assembly] = compare_right_arm(reference, candidate, configurations)
    results = {}
    for assembly in assemblies:
        print(f"Benchmarking {assembly}", flush=True)
        code = (
            "import sys; sys.path.insert(0, sys.argv.pop(1)); "
            "from accordion_ergonomics_core.architecture import benchmark_worker; "
            "import json; from pathlib import Path; "
            "print(json.dumps(benchmark_worker(Path(sys.argv[1]),sys.argv[2],"
            "int(sys.argv[3]),int(sys.argv[4]))))"
        )
        child = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(Path(__file__).parent.parent),
                str(source.resolve()),
                assembly,
                str(config["batches"]),
                str(config["iterations"]),
            ],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "MUJOCO_GL": "egl"},
        )
        result = json.loads(child.stdout)
        results[assembly] = result
        directory = output / assembly
        directory.mkdir(exist_ok=True)
        (directory / "benchmark.json").write_text(json.dumps(result, indent=2) + "\n")
        input_record = e.expanded_source()
        input_record["id"] = config["id"] + "-" + assembly
        input_record["anatomy"]["model"] = assembly
        input_record["player"]["model"] = assembly
        if assembly != "myoarm_r":
            from dataclasses import asdict

            input_record["player"]["full_body_posture"] = asdict(FullBodyPosture())
        experiment_path = directory / "experiment.json"
        experiment_path.write_text(json.dumps(input_record, indent=2) + "\n")
        # Principal playing solve uses canonical workflow records/diagnostic views.
        playing = run_experiment(experiment_path, directory / "playing", True)
        (directory / "playing" / "experiment.json").write_bytes(
            experiment_path.read_bytes()
        )
        playing_input = load_input(experiment_path)
        playing_scene = build_scene(
            playing_input.geometry,
            playing_input.player,
            playing_input.setup,
            playing_input.physical_contact,
        )
        playing_scene.data.qpos[:] = playing["qpos_rad"]
        (directory / "playing" / "passive-envelope-audit.json").write_text(
            json.dumps(passive_envelope_audit(playing_scene), indent=2) + "\n"
        )
        # Generic rest reference is body-only and independent of fixture/task.
        model_input = load_input(experiment_path)
        scene = build_scene(
            model_input.geometry,
            model_input.player,
            model_input.setup,
            model_input.physical_contact,
        )
        rest = {"elbow_flexion_r": 0.35, "shoulder_elv_r": 0.1}
        scene.data.qpos[:] = coupled_initial_pose(
            scene.model, {**scene.prescribed_joints, **rest}
        )
        cameras = render_body(scene, directory / "renders")
        state = {
            "input": input_record,
            "qpos_rad": scene.data.qpos.tolist(),
            "joint_names": [scene.model.joint(i).name for i in range(scene.model.njnt)],
            "body_cameras": cameras,
            "diagnostics": diagnostics(
                scene, model_input.geometry.surface_world_m(button_at(1, 5))
            ),
            "coverage": audit_collision_coverage(scene),
            "passive_envelope_audit": passive_envelope_audit(scene),
            "playing_status": playing["status"],
            "claim": (
                "Assumed seated skeletal rest reference; "
                "no ergonomic or collision-valid anatomy claim"
            ),
            **current_execution_metadata(scene.model),
        }
        (directory / "result.json").write_text(json.dumps(state, indent=2) + "\n")
        replay_body(directory / "result.json", directory / "saved-replay")
        image_hashes_match = all(
            (directory / "renders" / f"{n}.png").read_bytes()
            == (directory / "saved-replay" / f"{n}.png").read_bytes()
            for n in cameras
        )
        (directory / "replay-validation.json").write_text(
            json.dumps({"image_hashes_match": image_hashes_match}, indent=2) + "\n"
        )
    result = {
        "input": config,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "upstream": inspect_upstream(),
        "parity": parity,
        "benchmarks": results,
        "artifact_sha256": {
            p.relative_to(output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.rglob("*"))
            if p.is_file()
            and p != output / "result.json"
            and p.name not in ("execution.json", "source-snapshot.zip")
        },
        "platform": platform.platform(),
        **current_execution_metadata(reference.model),
    }
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
