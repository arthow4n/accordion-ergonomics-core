"""Independent sampled proxy reports and media from exact recorded search states."""

import hashlib
import json
from html import escape
from pathlib import Path
from typing import Any

from PIL import Image

from ._engine import mujoco
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .hand_audit import audit_hand_pose, hand_pairs
from .instrument import button_at
from .movement_evidence import state_digest, trajectory_frame_indices, validate_strategy
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .scene import Scene, build_scene


def independent_samples(
    scene: Scene, samples: list[dict[str, Any]], tolerance: float
) -> dict[str, Any]:
    if not samples:
        raise ValueError("Independent trajectory audit requires actual samples")
    pairs = hand_pairs(scene)
    reports: list[dict[str, Any]] = []
    component_minima: dict[str, dict[str, Any]] = {}
    worst_hand = {"distance_m": 0.0, "sample_index": 0, "geoms": []}
    violations = []
    for index, sample in enumerate(samples):
        scene.data.qpos[:] = sample["qpos_rad"]
        hand = audit_hand_pose(scene, pairs)
        cross = [
            p
            for p in hand["pairs"]
            if p["classification"] == "cross_digit_phalangeal_unresolved"
        ]
        worst = min(cross, key=lambda p: p["signed_proxy_distance_m"])
        configured = [p for p in hand["pairs"] if p["configured"]]
        configured_min = min(
            (p["signed_proxy_distance_m"] for p in configured), default=1.0
        )
        instrument = []
        for j in scene.board_geoms:
            distance, i = min(
                (
                    float(
                        mujoco.mj_geomDistance(scene.model, scene.data, i, j, 1.0, None)
                    ),
                    i,
                )
                for i in scene.anatomy_geoms
            )
            name = scene.model.geom(j).name
            instrument.append(distance)
            if (
                name not in component_minima
                or distance < component_minima[name]["distance_m"]
            ):
                component_minima[name] = {
                    "distance_m": distance,
                    "sample_index": index,
                    "anatomy_geom": scene.model.geom(i).name,
                }
        if worst["signed_proxy_distance_m"] < worst_hand["distance_m"]:
            worst_hand = {
                "distance_m": worst["signed_proxy_distance_m"],
                "sample_index": index,
                "geoms": worst["geoms"],
            }
        valid = min(instrument) >= -tolerance and configured_min >= -tolerance
        if not valid:
            violations.append(index)
        reports.append(
            {
                "sample_index": index,
                "minimum_instrument_distance_m": min(instrument),
                "minimum_configured_pair_distance_m": configured_min,
                "worst_cross_digit_phalangeal_distance_m": worst[
                    "signed_proxy_distance_m"
                ],
                "unresolved_overlap_count": hand["unresolved_overlap_count"],
                "configured_and_instrument_satisfied": valid,
            }
        )
    return {
        "status": "sampled_proxy_constraints_satisfied"
        if not violations
        else "sampled_proxy_constraints_rejected",
        "state_sequence_sha256": state_digest(samples),
        "sample_count": len(samples),
        "hand_pairs_per_sample": len(pairs),
        "instrument_pairs_per_sample": len(scene.anatomy_geoms)
        * len(scene.board_geoms),
        "penetration_tolerance_m": tolerance,
        "query_cutoff_m": 1.0,
        "violation_sample_indices": violations,
        "worst_cross_digit": worst_hand,
        "instrument_component_minima": component_minima,
        "samples": reports,
        "anatomical_validation": "unresolved",
        "human_feasibility": None,
        "claim": (
            "All saved samples, all hand pairs and instrument solids; "
            "unsampled intervals and tissue validity unresolved"
        ),
    }


def search_diagram(saved: dict[str, Any], path: Path) -> None:
    """SVG nodes/edges are actual numerical search records; layout is schematic."""
    nodes = saved["nodes"]
    stages = sorted({n["event_index"] for n in nodes})
    locations = {}
    for stage in stages:
        for row, node in enumerate(n for n in nodes if n["event_index"] == stage):
            locations[node["id"]] = (35 + stage * 360, 110 + row * 80)
    width = max(1000, 360 * len(stages) + 40)
    height = max(320, max((y for _, y in locations.values()), default=100) + 130)
    colors = {
        "failed_contact_solve": "#a93e45",
        "failed_transition": "#b16c35",
        "preparation_transition_failed": "#b16c35",
        "pruned_beam_cost": "#727b87",
        "retained_beam": "#267866",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#142030"/>',
        '<g font-family="monospace" fill="#eef3f8">',
        f'<text x="20" y="25" font-size="16">{escape(saved["id"])} — '
        "actual bounded search; schematic layout</text>",
        '<text x="20" y="48" font-size="11">Green retained | gray beam-pruned | '
        "red solve failure | amber movement failure; no optimum claim</text>",
    ]
    for edge in saved["edges"]:
        x, y = locations[edge["source"]]
        a, b = locations[edge["destination"]]
        color = "#83bda8" if edge["status"] == "sampled_path_found" else "#db8a62"
        parts.append(
            f'<path d="M{x + 310},{y + 22} L{a},{b + 22}" stroke="{color}" '
            'fill="none" opacity="0.55"/>'
        )
    for node in nodes:
        x, y = locations[node["id"]]
        label = ", ".join(f"{c['finger']} {c['button_id']}" for c in node["contacts"])
        color = colors.get(node["status"], "#466578")
        parts += [
            f'<rect x="{x}" y="{y}" width="310" height="62" rx="4" fill="{color}"/>',
            f'<text x="{x + 6}" y="{y + 14}" font-size="10">'
            f"{escape(node['id'])}</text>",
            f'<text x="{x + 6}" y="{y + 30}" font-size="10">{escape(label)}</text>',
            f'<text x="{x + 6}" y="{y + 47}" font-size="10">'
            f"{escape(node['status'])} "
            + (f"cost {node['cost']:.5f} m" if "cost" in node else "unscored")
            + "</text>",
        ]
    for stage in stages:
        batches = [b for b in saved["hypothesis_batches"] if b["event_index"] == stage]
        generated = sum(b["generated"] for b in batches)
        attempted = sum(
            h["status"] != "unexplored_budget" for b in batches for h in b["hypotheses"]
        )
        parts.append(
            f'<text x="{35 + stage * 360}" y="78" font-size="11">'
            f"Event {stage}: {generated} generated / {attempted} attempted / "
            f"{generated - attempted} unexplored</text>"
        )
    parts += [
        f'<text x="20" y="{height - 25}" font-size="11">'
        "Contact seed solves are not approach trajectories. "
        "Unexplored hypotheses have no numerical rejection.</text>",
        "</g></svg>",
    ]
    path.write_text("\n".join(parts) + "\n")


def render_strategy(
    scene: Scene,
    saved: dict[str, Any],
    strategy: dict[str, Any],
    audit: dict[str, Any],
    output: Path,
    frame_count: int,
    cameras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_strategy(saved, strategy)
    if audit["status"] != "sampled_proxy_constraints_satisfied" or audit[
        "state_sequence_sha256"
    ] != state_digest(strategy["samples"]):
        raise ValueError("Missing or rejected independent movement audit")
    output.mkdir(parents=True, exist_ok=True)
    e = Experiment.from_dict(saved["scene_input"])
    indices = trajectory_frame_indices(strategy, frame_count)
    frames = []
    manifest = []
    for frame_index, sample_index in enumerate(indices):
        sample = strategy["samples"][sample_index]
        scene.data.qpos[:] = sample["qpos_rad"]
        contacts = sample["active_contacts"]
        phase = sample.get("phase", {}).get("phase", "event")
        event_hint = sample["event_interval"] + (0 if phase == "withdraw" else 1)
        reference_contacts = (
            contacts
            or strategy["events"][min(event_hint, len(strategy["events"]) - 1)][
                "contacts"
            ]
        )
        primary = reference_contacts[0]
        target = e.geometry.surface_world_m(
            button_at(primary["row"], primary["column"])
        ).tolist()
        roles = sample["roles"]
        directory = output / f"frame-{frame_index:02}"
        labels = " + ".join(
            f"{c['midi']}:{c['finger']}:{c['button_id']}" for c in reference_contacts
        )
        observed = audit["samples"][sample_index]
        label = (
            f"sample {sample_index} | {phase} | {labels} | proxy concern "
            f"{observed['worst_cross_digit_phalangeal_distance_m'] * 1000:.2f} mm"
        )
        actual = render_views(
            scene,
            directory,
            target,
            primary["button_id"],
            views_to_render=("hand",),
            contact_roles=roles,
            button_roles={
                c["button_id"]: roles.get(c["finger"], "moving")
                for c in reference_contacts
            },
            state_label=label,
            camera_overrides=cameras,
        )
        if cameras is None:
            cameras = actual
        with Image.open(directory / "hand.png") as im:
            frames.append(im.copy())
        manifest.append(
            {
                "frame_index": frame_index,
                "sample_index": sample_index,
                "qpos_rad": sample["qpos_rad"],
                "active_contacts": contacts,
                "roles": roles,
                "frame": str((directory / "hand.png").relative_to(output)),
                "frame_sha256": hashlib.sha256(
                    (directory / "hand.png").read_bytes()
                ).hexdigest(),
            }
        )
    frames[0].save(
        output / "trajectory.gif",
        save_all=True,
        append_images=frames[1:],
        duration=180,
        loop=0,
    )
    return {
        "strategy_id": strategy["id"],
        "sample_indices": indices,
        "frames": manifest,
        "cameras": cameras,
        "state_sequence_sha256": state_digest(strategy["samples"]),
        "gif_sha256": hashlib.sha256(
            (output / "trajectory.gif").read_bytes()
        ).hexdigest(),
        "duration_ms_per_frame": 180,
        "playback_claim": (
            "Illustrative playback only; no tempo, effort "
            "or continuous validity evidence"
        ),
    }


def run_passage_media(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    saved = read_hashed(
        definition.parent / source["search_result"], source["search_sha256"]
    )
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != saved["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Visualization model differs from numerical search")
    output.mkdir(parents=True, exist_ok=True)
    search_diagram(saved, output / "search.svg")
    reports: list[dict[str, Any]] = []
    cameras = None
    for strategy in saved["strategies"][: source.get("strategy_limit", 2)]:
        is_movement = strategy["status"] == "sampled_connected_path"
        if is_movement:
            validate_strategy(saved, strategy)
            states = strategy["samples"]
        elif strategy["status"] == "static_contact_only":
            node = next(n for n in saved["nodes"] if n["id"] == strategy["node_ids"][0])
            if (
                len(strategy["events"]) != 1
                or strategy["events"][0]["qpos_rad"] != node["qpos_rad"]
                or strategy["events"][0]["contacts"] != node["contacts"]
            ):
                raise ValueError("Static render differs from recorded contact node")
            contacts = node["contacts"]
            states = [
                {
                    "qpos_rad": node["qpos_rad"],
                    "active_contacts": contacts,
                    "roles": {c["finger"]: "required" for c in contacts},
                    "event_interval": 0,
                }
            ]
        else:
            raise ValueError("Unsuccessful evidence cannot become accepted media")
        audit = independent_samples(scene, states, e.solver.penetration_tolerance_m)
        audit["state_kind"] = strategy["status"]
        record = {
            "strategy_id": strategy["id"],
            "independent_audit": audit,
            "animation": None,
        }
        if is_movement and audit["status"] == "sampled_proxy_constraints_satisfied":
            record["animation"] = render_strategy(
                scene,
                saved,
                strategy,
                audit,
                output / strategy["id"],
                source.get("frames", 9),
                cameras,
            )
            cameras = record["animation"]["cameras"]
        worst = audit["worst_cross_digit"]
        sample_index = (
            audit["violation_sample_indices"][0]
            if audit["violation_sample_indices"]
            else worst["sample_index"]
        )
        sample = states[sample_index]
        scene.data.qpos[:] = sample["qpos_rad"]
        hand = audit_hand_pose(scene)
        cross = [
            p
            for p in hand["pairs"]
            if p["classification"] == "cross_digit_phalangeal_unresolved"
        ]
        concern = min(cross, key=lambda p: p["signed_proxy_distance_m"])
        contacts = (
            sample["active_contacts"]
            or strategy["events"][
                min(sample["event_interval"] + 1, len(strategy["events"]) - 1)
            ]["contacts"]
        )
        contact = contacts[0]
        record["worst_state_sample_index"] = sample_index
        record["worst_state_active_contacts"] = sample["active_contacts"]
        record["worst_state_cameras"] = render_views(
            scene,
            output / strategy["id"] / "worst-state",
            e.geometry.surface_world_m(
                button_at(contact["row"], contact["column"])
            ).tolist(),
            contact["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=tuple(concern["geoms"]),
            contact_roles=sample["roles"],
            button_roles={
                c["button_id"]: sample["roles"].get(c["finger"], "moving")
                for c in contacts
            },
            state_label=(
                f"{'actual sample' if is_movement else 'static node'} {sample_index} | "
                f"{audit['status']} | "
                f"cross-digit {concern['signed_proxy_distance_m'] * 1000:.2f} mm"
            ),
        )
        reports.append(record)
    failed = next(
        (
            n
            for n in saved["nodes"]
            if n["contact_solve"]["status"] == "failed"
            or n.get("optional_preparation_failure")
            or n["status"] in ("failed_transition", "preparation_transition_failed")
        ),
        None,
    )
    failed_state = None
    if failed:
        failure_solve = (
            failed.get("optional_preparation_failure") or failed["contact_solve"]
        )
        scene.data.qpos[:] = failure_solve["qpos_rad"]
        requirements = failure_solve["contact_requirements"]
        parent = next((n for n in saved["nodes"] if n["id"] == failed["parent"]), None)
        temporal_contacts = failed["contacts"] + (parent["contacts"] if parent else [])
        held_bindings = {
            (c["finger"], c["button_id"])
            for c in temporal_contacts
            if c["behavior"] == "hold"
        }
        failure_roles = {
            c["finger"]: (
                "held" if (c["finger"], c["button_id"]) in held_bindings else "required"
            )
            if c["surface_contact_required"]
            else "preparing"
            for c in requirements
        }
        failed_state = {
            "node_id": failed["id"],
            "source_field": "optional_preparation_failure"
            if failed.get("optional_preparation_failure")
            else "contact_solve",
            "qpos_rad": failure_solve["qpos_rad"],
            "contact_requirements": requirements,
            "roles": failure_roles,
        }
        failure_audit = independent_samples(
            scene,
            [{"qpos_rad": failure_solve["qpos_rad"]}],
            e.solver.penetration_tolerance_m,
        )
        failed_state["independent_audit"] = failure_audit
        contact = failed["contacts"][0]
        render_views(
            scene,
            output / "failed-contact",
            e.geometry.surface_world_m(
                button_at(contact["row"], contact["column"])
            ).tolist(),
            contact["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=tuple(failure_audit["worst_cross_digit"]["geoms"]),
            contact_roles=failure_roles,
            button_roles={
                c["button_id"]: failure_roles[c["finger"]] for c in requirements
            },
            state_label=(
                f"problem branch {failed['id']}; cross-digit "
                f"{failure_audit['worst_cross_digit']['distance_m'] * 1000:.2f} mm; "
                "not a movement or impossibility claim"
            ),
        )
    comparison = None
    animated = [r for r in reports if r["animation"]]
    if len(animated) >= 2:
        first, second = animated[:2]
        if first["animation"]["cameras"] != second["animation"]["cameras"]:
            raise ValueError("Alternative comparison requires matched cameras")
        sources = []
        panels = []
        for record in (first, second):
            frame = record["animation"]["frames"][-1]
            path = output / record["strategy_id"] / frame["frame"]
            with Image.open(path) as im:
                panels.append(im.copy())
            sources.append(
                {
                    "strategy_id": record["strategy_id"],
                    "frame": str(path.relative_to(output)),
                    "sample_index": frame["sample_index"],
                    "frame_sha256": frame["frame_sha256"],
                }
            )
        canvas = Image.new("RGB", (sum(p.width for p in panels), panels[0].height))
        offset = 0
        for panel in panels:
            canvas.paste(panel, (offset, 0))
            offset += panel.width
        canvas.save(output / "alternative-final-event.png")
        comparison = {
            "image": "alternative-final-event.png",
            "event_index": len(saved["passage"]["events"]) - 1,
            "sources": sources,
            "cameras": first["animation"]["cameras"],
            "claim": (
                "Matched actual final event states, "
                "not equal elapsed time or optimality"
            ),
        }
    result = {
        "id": saved["id"] + "-media",
        "strategy_comparison": comparison,
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "search_source_provenance": saved["provenance"],
        "strategy_reports": reports,
        "failed_contact_node_id": failed["id"] if failed else None,
        "failed_contact_state": failed_state,
        "artifact_sha256": {
            str(f.relative_to(output)): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(output.rglob("*"))
            if f.is_file() and f.suffix in (".png", ".gif", ".svg")
        },
        **current_execution_metadata(scene.model),
    }
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    return result
