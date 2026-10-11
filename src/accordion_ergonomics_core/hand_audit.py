"""Versioned independent native hand proxy reporting; no tissue inference."""

import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

from ._engine import mujoco
from .experiment import Experiment
from .exploration import read_hashed
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import Scene, build_scene

HAND_POLICY_ID = "native-hand-proxy-report-v1"
DIGIT_ROOTS = dict(
    zip(
        ("thumb", "index", "middle", "ring", "little"),
        ("firstmc_r", "secondmc_r", "thirdmc_r", "fourthmc_r", "fifthmc_r"),
        strict=True,
    )
)


def hand_pairs(scene: Scene) -> list[dict[str, Any]]:
    """Classify topology, not tissue; configured pairs retain hypothesis status."""
    m = scene.model
    digits = {}
    metacarpals = set()
    for digit, name in DIGIT_ROOTS.items():
        root = m.body(name).id
        metacarpals.add(root)
        bodies = {root}
        for body in range(root + 1, m.nbody):
            if int(m.body_parentid[body]) in bodies:
                bodies.add(body)
        digits.update(
            {g: digit for g in scene.anatomy_geoms if int(m.geom_bodyid[g]) in bodies}
        )
    explicit = {
        tuple(sorted((int(a), int(b))))
        for a, b in zip(m.pair_geom1, m.pair_geom2, strict=True)
    }
    configured = {
        tuple(sorted(p)) for p in scene.contact_profile.additional_collision_pairs
    }
    pairs = []
    for a, b in combinations(sorted(digits), 2):
        names = [m.geom(a).name, m.geom(b).name]
        same_digit = digits[a] == digits[b]
        same_body = m.geom_bodyid[a] == m.geom_bodyid[b]
        palm = (
            int(m.geom_bodyid[a]) in metacarpals or int(m.geom_bodyid[b]) in metacarpals
        )
        selected = tuple(sorted(names)) in configured
        if selected:
            classification = "configured_separation_hypothesis"
        elif same_digit and same_body:
            classification = "same_segment_composite_envelope"
        elif same_digit:
            classification = "articulating_same_digit_unresolved"
        elif palm:
            classification = "cross_digit_palm_composition_unresolved"
        else:
            classification = "cross_digit_phalangeal_unresolved"
        pairs.append(
            {
                "geom_ids": [a, b],
                "geoms": names,
                "digits": [digits[a], digits[b]],
                "classification": classification,
                "configured": selected,
                "mask_compatible": bool(
                    (int(m.geom_contype[a]) & int(m.geom_conaffinity[b]))
                    or (int(m.geom_contype[b]) & int(m.geom_conaffinity[a]))
                ),
                "explicit_engine_pair": tuple(sorted((a, b))) in explicit,
            }
        )
    return pairs


def audit_hand_pose(
    scene: Scene, pairs: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Query every hand pair regardless of automatic engine contact filtering."""
    mujoco.mj_forward(scene.model, scene.data)
    records: list[dict[str, Any]] = []
    for pair in hand_pairs(scene) if pairs is None else pairs:
        a, b = pair["geom_ids"]
        records.append(
            {k: v for k, v in pair.items() if k != "geom_ids"}
            | {
                "signed_proxy_distance_m": float(
                    mujoco.mj_geomDistance(scene.model, scene.data, a, b, 1.0, None)
                ),
            }
        )
    unresolved = [
        p
        for p in records
        if p["classification"].endswith("unresolved")
        and p["signed_proxy_distance_m"] < 0
    ]
    return {
        "policy_id": HAND_POLICY_ID,
        "pairs": records,
        "unresolved_overlap_count": len(unresolved),
        "cross_digit_phalangeal_overlap_count": sum(
            p["classification"] == "cross_digit_phalangeal_unresolved"
            for p in unresolved
        ),
        "anatomical_validation": "unresolved",
        "human_feasibility": None,
    }


def run_hand_audit(definition: Path, output: Path) -> dict[str, Any]:
    """Audit hashed saved states and every recorded trajectory sample, no solving."""
    raw = definition.read_bytes()
    source = json.loads(raw)
    records: list[dict[str, Any]] = []
    output.mkdir(parents=True, exist_ok=True)
    scenes: dict[str, Scene] = {}
    for request in source["records"]:
        saved = read_hashed(definition.parent / request["result"], request["sha256"])
        model_saved = read_hashed(
            definition.parent / request.get("model_result", request["result"]),
            request.get("model_sha256", request["sha256"]),
        )
        e = Experiment.from_dict(model_saved["input"])
        world_key = json.dumps(
            {
                "profiles": e.resolved_profiles(),
                "fingers": [c.finger for c in e.contacts],
            },
            sort_keys=True,
        )
        if world_key not in scenes:
            scenes[world_key] = build_scene(
                e.geometry,
                e.player,
                e.setup,
                e.physical_contact,
                tuple(c.finger for c in e.contacts),
            )
        scene = scenes[world_key]
        digest = compiled_model_digest(scene.model)
        if any(
            s["provenance"]["compiled_model_sha256"] != digest
            for s in (saved, model_saved)
        ):
            raise ValueError("Hand audit requires identical recorded compiled worlds")
        kind = request.get("kind", "pose")
        if kind == "neutral":
            states = [scene.model.qpos0.tolist()]
        elif kind == "pose":
            states = [saved["qpos_rad"]]
        elif kind == "path":
            states = [sample["qpos_rad"] for sample in saved["samples"]]
        elif kind == "held":
            states = [
                sample["qpos_rad"] for sample in saved["searched_audit"]["samples"]
            ]
        else:
            raise ValueError("Unknown hand audit state kind")
        if not states:
            raise ValueError("Empty paths cannot be independently audited")
        pairs = hand_pairs(scene)
        minima = [1.0] * len(pairs)
        minima_indices = [0] * len(pairs)
        samples = []
        instrument_minima: dict[str, dict[str, Any]] = {}
        instrument_requested = request.get("audit_instrument", kind in ("path", "held"))
        worst_index, worst_distance = 0, 0.0
        for index, state in enumerate(states):
            scene.data.qpos[:] = state
            audit = audit_hand_pose(scene, pairs)
            for i, pair in enumerate(audit["pairs"]):
                distance = pair["signed_proxy_distance_m"]
                if distance < minima[i]:
                    minima[i], minima_indices[i] = distance, index
                if (
                    pair["classification"] == "cross_digit_phalangeal_unresolved"
                    and distance < worst_distance
                ):
                    worst_index, worst_distance = index, distance
            if instrument_requested:
                for solid in scene.board_geoms:
                    distance, anatomy = min(
                        (
                            float(
                                mujoco.mj_geomDistance(
                                    scene.model,
                                    scene.data,
                                    proxy,
                                    solid,
                                    1.0,
                                    None,
                                )
                            ),
                            proxy,
                        )
                        for proxy in scene.anatomy_geoms
                    )
                    name = scene.model.geom(solid).name or f"unnamed_geom_{solid}"
                    if (
                        name not in instrument_minima
                        or distance
                        < instrument_minima[name]["minimum_signed_proxy_distance_m"]
                    ):
                        instrument_minima[name] = {
                            "minimum_signed_proxy_distance_m": distance,
                            "minimum_sample_index": index,
                            "anatomy_geom": scene.model.geom(anatomy).name,
                        }
            samples.append(
                {
                    "index": index,
                    "unresolved_overlap_count": audit["unresolved_overlap_count"],
                    "cross_digit_phalangeal_overlap_count": audit[
                        "cross_digit_phalangeal_overlap_count"
                    ],
                }
            )
        pair_records: list[dict[str, Any]] = [
            {k: v for k, v in pair.items() if k != "geom_ids"}
            | {
                "minimum_signed_proxy_distance_m": minima[i],
                "minimum_sample_index": minima_indices[i],
            }
            for i, pair in enumerate(pairs)
        ]
        rejected = [
            p
            for p in pair_records
            if p["configured"]
            and p["minimum_signed_proxy_distance_m"] < -e.solver.penetration_tolerance_m
        ]
        cameras = {}
        if request.get("render", False):
            scene.data.qpos[:] = states[worst_index]
            target = model_saved["target"]
            suspect = [
                p
                for p in pair_records
                if p["classification"] == "cross_digit_phalangeal_unresolved"
            ]
            highlight = (
                min(suspect, key=lambda p: p["minimum_signed_proxy_distance_m"])[
                    "geoms"
                ]
                if suspect
                else []
            )
            cameras = render_views(
                scene,
                output / "renders" / request["id"],
                target["surface_world_m"],
                target["button_id"],
                collision_overlay=True,
                highlighted_proxy_names=tuple(highlight),
            )
        records.append(
            {
                "id": request["id"],
                "source": request,
                **current_execution_metadata(scene.model),
                "sample_count": len(states),
                "instrument_component_minima": instrument_minima,
                "instrument_proxy_pairs_distance_queried": (
                    len(states) * len(scene.board_geoms) * len(scene.anatomy_geoms)
                    if instrument_requested
                    else 0
                ),
                "instrument_policy_status": (
                    "rejected"
                    if any(
                        component["minimum_signed_proxy_distance_m"]
                        < -e.solver.penetration_tolerance_m
                        for component in instrument_minima.values()
                    )
                    else "sampled_pairs_satisfied"
                    if instrument_requested
                    else "not_audited"
                ),
                "samples": samples,
                "pair_minima": pair_records,
                "configured_pair_rejections": rejected,
                "configured_policy_status": "rejected"
                if rejected
                else "sampled_pairs_satisfied",
                "anatomical_validation": "unresolved",
                "worst_cross_digit_phalangeal_distance_m": worst_distance,
                "render_sample_index": worst_index,
                "render_qpos_rad": states[worst_index] if cameras else None,
                "cameras": cameras,
            }
        )
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "artifact_sha256": {
            str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted((output / "renders").rglob("*.png"))
        },
        "policy_id": HAND_POLICY_ID,
        "status": "hand_proxy_audited",
        "records": records,
        "human_feasibility": None,
        "interpretation": (
            "All hand pair distances independently queried at recorded samples. "
            "Same-segment proxies compose envelopes; configured separation pairs "
            "remain hypotheses. Other intersections remain unresolved rigid-proxy "
            "overlaps, not proven tissue intersections. Unsampled intervals and "
            "calibrated anatomy remain unvalidated."
        ),
    }
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
