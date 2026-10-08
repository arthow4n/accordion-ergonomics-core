"""Reproduce collision-limit units and world-filter behavior on synthetic spheres."""

import hashlib
import json
import warnings
from dataclasses import asdict
from pathlib import Path
from typing import Any

import mink
import numpy as np
from PIL import Image, ImageDraw

from ._engine import mujoco
from .distance_limits import DisplacementDistanceLimit, collision_pairs
from .profiles import ContactProfile
from .provenance import current_execution_metadata


def render_probe(model: Any, q: list[float], output: Path) -> dict[str, Any]:
    data = mujoco.MjData(model)
    data.qpos[:] = q
    mujoco.mj_forward(model, data)
    output.mkdir(parents=True, exist_ok=True)
    cameras = {}
    with mujoco.Renderer(model, height=480, width=640) as renderer:
        for name, azimuth, elevation in (
            ("front", -90, 0),
            ("top", -90, 90),
            ("side", 180, 0),
            ("oblique", -60, -25),
        ):
            camera = mujoco.MjvCamera()
            camera.lookat[:] = [0.015, 0, 0]
            camera.distance = 0.12
            camera.azimuth, camera.elevation = azimuth, elevation
            renderer.update_scene(data, camera=camera)
            picture = Image.fromarray(renderer.render())
            ImageDraw.Draw(picture).text(
                (12, 12), name + " | synthetic spheres", fill="white"
            )
            picture.save(output / (name + ".png"))
            cameras[name] = {
                "lookat_m": [0.015, 0, 0],
                "distance_m": 0.12,
                "azimuth_degrees": azimuth,
                "elevation_degrees": elevation,
            }
    return cameras


def run_probe(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    policy = ContactProfile(**source["physical_contact"])
    records = []
    for fixture, xml in source["fixtures_xml"].items():
        model = mujoco.MjModel.from_xml_string(xml)
        for dt in source["integration_dt_s"]:
            for implementation in ("mink_native", "displacement"):
                c = mink.Configuration(model)
                initial = c.q.tolist()
                pairs = collision_pairs(
                    model, [model.geom("moving").id], [model.geom("fixed").id]
                )
                if implementation == "displacement":
                    limit = DisplacementDistanceLimit(model, pairs, policy)
                else:
                    limit = mink.CollisionAvoidanceLimit(
                        model,
                        [(["fixed"], ["moving"])],
                        minimum_distance_from_collisions=policy.collision_minimum_distance_m,
                        collision_detection_distance=policy.collision_detection_distance_m,
                        gain=policy.collision_gain,
                    )
                pair_count = (
                    len(limit.pairs)
                    if isinstance(limit, DisplacementDistanceLimit)
                    else len(limit.geom_id_pairs)
                )
                inequality = limit.compute_qp_inequalities(c, dt)
                task = mink.FrameTask(
                    "tip", "site", position_cost=1, orientation_cost=0
                )
                task.set_target(
                    mink.SE3.from_translation(np.asarray(source["target_world_m"]))
                )
                frozen = (
                    [mink.DofFreezingTask(model, [0])] if fixture == "siblings" else []
                )
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    velocity = mink.solve_ik(
                        c,
                        [task],
                        dt,
                        solver="clarabel",
                        limits=[limit],
                        constraints=frozen,
                    )
                c.integrate_inplace(velocity, dt)
                gap = float(mujoco.mj_geomDistance(model, c.data, 0, 1, 1.0, None))
                record = {
                    "fixture": fixture,
                    "implementation": implementation,
                    "dt_s": dt,
                    "initial_qpos": initial,
                    "final_qpos": c.q.tolist(),
                    "joint_types": ["slide"] * model.njnt,
                    "qpos_units": "metres",
                    "signed_gap_m": gap,
                    "pair_count": pair_count,
                    "G": None if inequality.G is None else inequality.G.tolist(),
                    "h_m": None if inequality.h is None else inequality.h.tolist(),
                    **current_execution_metadata(model),
                }
                if dt == source["render_dt_s"]:
                    root = output / "renders" / fixture / implementation
                    record["cameras"] = render_probe(model, c.q.tolist(), root)
                records.append(record)
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "resolved_contact_policy": asdict(policy),
        "cases": records,
        "claim": "Synthetic numerical falsification; no anatomical inference",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
