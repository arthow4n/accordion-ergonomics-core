"""Audit unchecked cross-digit proxy overlaps without changing collision policy."""

import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any

from ._engine import mujoco
from .experiment import Experiment
from .exploration import read_hashed
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import Scene, build_scene


def audit_collision_coverage(scene: Scene) -> dict[str, Any]:
    """Distance-query all cross-digit proxies, independent of engine masks.

    Masks describe only one collision filter. Explicit pairs bypass that filter;
    other engine filters still apply. Proxy overlap is not measured tissue overlap.
    """
    model, data = scene.model, scene.data
    mujoco.mj_forward(model, data)
    digit_geoms: dict[str, list[int]] = {}
    for digit, name in zip(
        ("thumb", "index", "middle", "ring", "little"),
        ("firstmc_r", "secondmc_r", "thirdmc_r", "fourthmc_r", "fifthmc_r"),
        strict=True,
    ):
        root = model.body(name).id
        bodies = {root}
        for i in range(root + 1, model.nbody):
            if int(model.body_parentid[i]) in bodies:
                bodies.add(i)
        digit_geoms[digit] = [
            g for g in scene.anatomy_geoms if int(model.geom_bodyid[g]) in bodies
        ]
    explicit = {
        tuple(sorted((int(a), int(b))))
        for a, b in zip(model.pair_geom1, model.pair_geom2, strict=True)
    }
    overlaps = []
    tested = 0
    for digit1, digit2 in combinations(digit_geoms, 2):
        for a in digit_geoms[digit1]:
            for b in digit_geoms[digit2]:
                tested += 1
                distance = float(mujoco.mj_geomDistance(model, data, a, b, 1.0, None))
                if distance < 0:
                    mask_allows = bool(
                        (int(model.geom_contype[a]) & int(model.geom_conaffinity[b]))
                        or (int(model.geom_contype[b]) & int(model.geom_conaffinity[a]))
                    )
                    overlaps.append(
                        {
                            "digits": [digit1, digit2],
                            "geoms": [model.geom(a).name, model.geom(b).name],
                            "signed_proxy_distance_m": distance,
                            "mask_compatible": mask_allows,
                            "explicit_pair": tuple(sorted((a, b))) in explicit,
                        }
                    )
    masks = Counter(
        (int(model.geom_contype[g]), int(model.geom_conaffinity[g]))
        for g in scene.anatomy_geoms
    )
    return {
        "anatomical_proxy_count": len(scene.anatomy_geoms),
        "mask_counts": [
            {"contype": a, "conaffinity": b, "count": count}
            for (a, b), count in sorted(masks.items())
        ],
        "explicit_pairs": [
            [model.geom(a).name, model.geom(b).name] for a, b in sorted(explicit)
        ],
        "cross_digit_pairs_distance_queried": tested,
        "overlaps": sorted(overlaps, key=lambda p: p["signed_proxy_distance_m"]),
        "unchecked_overlap_count": sum(
            not p["mask_compatible"] and not p["explicit_pair"] for p in overlaps
        ),
        "claim": (
            "Collision-filter coverage and rigid-proxy overlap, not tissue feasibility"
        ),
    }


def run_coverage(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    records = []
    for request in source["poses"]:
        saved = read_hashed(definition.parent / request["result"], request["sha256"])
        e = Experiment.from_dict(saved["input"])
        scene = build_scene(
            e.geometry,
            e.player,
            e.setup,
            e.physical_contact,
            tuple(c.finger for c in e.contacts),
        )
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Collision coverage requires the recorded model")
        scene.data.qpos[:] = saved["qpos_rad"]
        audit = audit_collision_coverage(scene)
        phalanges = [
            p
            for p in audit["overlaps"]
            if all(g.startswith(("distph", "midph", "proxph")) for g in p["geoms"])
        ]
        audit["phalangeal_overlaps"] = phalanges
        highlight = tuple(phalanges[0]["geoms"]) if phalanges else ()
        cameras = render_views(
            scene,
            output / "renders" / request["id"],
            saved["target"]["surface_world_m"],
            saved["target"]["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=highlight,
        )
        records.append(
            {
                "id": request["id"],
                "source": request,
                "qpos_rad": saved["qpos_rad"],
                "joint_names": saved["joint_names"],
                "resolved_profiles": e.resolved_profiles(),
                **current_execution_metadata(scene.model),
                "audit": audit,
                "cameras": cameras,
                "highlighted_proxy_names": highlight,
            }
        )
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "status": "coverage_audited",
        "poses": records,
        "physical_feasibility": None,
        "interpretation": (
            "Unchecked proxy overlaps need envelope and human-pose validation; "
            "enabling every pair is not automatically a valid repair"
        ),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
