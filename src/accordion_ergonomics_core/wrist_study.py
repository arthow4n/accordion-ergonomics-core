"""Frozen wrist reassessments and matched physical evidence from saved searches."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from ._engine import mujoco
from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .movement_evidence import state_digest, validate_strategy
from .passage_media import independent_samples, render_strategy, search_diagram
from .provenance import compiled_model_digest, current_execution_metadata
from .quality_plots import trace_svg
from .render import render_views
from .scene import build_scene
from .strategy_audit import audit_states
from .wrist import (
    WristReference,
    orientation_trace,
    reference_geometry,
    wrist_descriptors,
)


def finish_record(definition, output, source, result, scene):
    result.update(
        input=source,
        definition_sha256=hashlib.sha256(definition.read_bytes()).hexdigest(),
        artifact_sha256={
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob("*")
            if p.suffix in (".svg", ".png", ".gif")
        },
        **current_execution_metadata(scene.model),
    )
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    metadata = output / "execution.json"
    if metadata.exists():
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
    return result


def run_wrist_study(definition: Path, output: Path):
    source = json.loads(definition.read_text())
    output.mkdir(parents=True, exist_ok=True)
    cases = []
    scene = None
    cameras = source.get("cameras")
    geometry = None
    for request in source["cases"]:
        saved = read_hashed(
            definition.parent / request["search_result"], request["search_sha256"]
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Wrist study changed recorded model")
        geometry = reference_geometry(scene)
        strategies = saved["strategies"]
        if "strategy_id" in request:
            strategies = [s for s in strategies if s["id"] == request["strategy_id"]]
        statesets: list[tuple[Any, list[dict[str, Any]]]] = [
            (s, s["samples"]) for s in strategies
        ]
        if request.get("failed_nodes"):
            statesets: list[tuple[Any, list[dict[str, Any]]]] = [
                (
                    None,
                    [
                        dict(
                            qpos_rad=n.get("qpos_rad", n["contact_solve"]["qpos_rad"]),
                            active_contacts=n["contacts"],
                            source_node_id=n["id"],
                            roles={c["finger"]: "attempted" for c in n["contacts"]},
                        )
                        for n in saved["nodes"]
                    ],
                )
            ]
        for strategy, states in statesets:
            if strategy:
                validate_strategy(saved, strategy)
            ident = request["id"] + (
                "-" + strategy["id"] if strategy else "-separate-nodes"
            )
            posture = wrist_descriptors(
                scene.model,
                states,
                saved["joint_names"],
                connected=strategy is not None,
            )
            sensitivity = [
                wrist_descriptors(
                    scene.model,
                    states,
                    saved["joint_names"],
                    WristReference(**r),
                    connected=strategy is not None,
                )["summary"]
                for r in source.get("alternative_references", [])
            ]
            orientations = []
            for state in states:
                scene.data.qpos[:] = state["qpos_rad"]
                mujoco.mj_forward(scene.model, scene.data)
                orientations.append(
                    dict(
                        body_axes_board_xyzw=orientation_trace(scene, e.geometry),
                        palm_board_m=(
                            e.geometry.rotation.T
                            @ (scene.data.body("capitate_r").xpos - e.geometry.origin_m)
                        ).tolist(),
                    )
                )
            directory = output / ident
            directory.mkdir()
            trace_svg(
                directory / "wrist.svg",
                ident + " | actual untimed samples",
                [
                    dict(
                        label="Signed native wrist (rad)",
                        series={
                            n: [t["signed_wrist_rad"][j] for t in posture["traces"]]
                            for j, n in enumerate(posture["coordinate_order"])
                        },
                    ),
                    dict(
                        label="Signed departure from imported reference (rad)",
                        series={
                            n: [
                                t["reference_departure_rad"][j]
                                for t in posture["traces"]
                            ]
                            for j, n in enumerate(posture["coordinate_order"])
                        },
                    ),
                    dict(
                        label="Forearm pro/supination (rad)",
                        series={
                            "pro_sup_r": [
                                t["forearm_rotation_rad"] for t in posture["traces"]
                            ]
                        },
                    ),
                    dict(
                        label=(
                            "Palm body quaternion in board (xyzw); not calibrated "
                            "palmar plane"
                        ),
                        series={
                            str(j): [
                                t["body_axes_board_xyzw"]["capitate_r"][j]
                                for t in orientations
                            ]
                            for j in range(4)
                        },
                    ),
                    dict(
                        label="Wrist limit margins (rad)",
                        series={
                            n: [
                                t["joint_limit_margin_rad"][j]
                                for t in posture["traces"]
                            ]
                            for j, n in enumerate(posture["coordinate_order"])
                        },
                    ),
                ],
            )
            record: dict[str, Any] = dict(
                id=ident,
                source=request,
                strategy_id=strategy["id"] if strategy else None,
                status="sampled_connected_path"
                if strategy
                else "separate_failed_nodes_not_movement",
                sample_count=len(states),
                state_sequence_sha256=state_digest(states),
                compiled_model_sha256=compiled_model_digest(scene.model),
                wrist=posture,
                orientation_traces=orientations,
                alternative_reference_summaries=sensitivity,
                first_note_approach="not_planned",
                media=[],
            )
            if source.get("audit_all") and strategy:
                record["whole_hand"] = audit_states(
                    scene, e.geometry, states, saved["joint_names"]
                )
                record["independent_audit"] = independent_samples(
                    scene, states, e.solver.penetration_tolerance_m
                )
            if request.get("render"):
                indices = {
                    0,
                    len(states) - 1,
                    len(states) // 2,
                    *[
                        s["extreme_reference_sample_index"]
                        for s in posture["summary"].values()
                    ],
                }
                audit = record.get("independent_audit") or independent_samples(
                    scene, states, e.solver.penetration_tolerance_m
                )
                indices.add(audit["worst_cross_digit"]["sample_index"])
                record["independent_audit"] = audit
                for index in sorted(indices):
                    state = states[index]
                    scene.data.qpos[:] = state["qpos_rad"]
                    contacts = state.get("active_contacts") or (
                        strategy["events"][-1]["contacts"]
                        if strategy
                        else states[0]["active_contacts"]
                    )
                    c = contacts[0]
                    cameras = render_views(
                        scene,
                        directory / f"state-{index}",
                        e.geometry.surface_world_m(
                            button_at(c["row"], c["column"])
                        ).tolist(),
                        c["button_id"],
                        collision_overlay=True,
                        highlighted_proxy_names=tuple(
                            audit["worst_cross_digit"]["geoms"]
                        ),
                        contact_roles=state.get("roles", {}),
                        state_label=(
                            f"{ident} | exact sample {index} | "
                            "model-reference wrist | initial approach unplanned"
                        ),
                        camera_overrides=cameras,
                    )
                    record["media"].append(
                        dict(
                            sample_index=index,
                            qpos_rad=state["qpos_rad"],
                            active_contacts=state.get("active_contacts", []),
                            roles=state.get("roles", {}),
                            cameras=cameras,
                            directory=f"{ident}/state-{index}",
                        )
                    )
                if (
                    strategy
                    and audit["status"] == "sampled_proxy_constraints_satisfied"
                ):
                    record["animation"] = render_strategy(
                        scene,
                        saved,
                        strategy,
                        audit,
                        directory / "path",
                        source.get("frames", 9),
                        {"hand": cameras["hand"]},
                        "Initial approach unplanned; untimed sampled path",
                    )
                search_diagram(saved, directory / "search.svg")
            cases.append(record)
    if scene is None:
        raise ValueError("Empty wrist benchmark")
    return finish_record(
        definition,
        output,
        source,
        dict(id="wrist-study-049", reference_geometry=geometry, cases=cases),
        scene,
    )


def run_posture_gallery(definition: Path, output: Path):
    """Compose exact matched rendered pixels; never construct new hand poses."""
    from PIL import Image

    source = json.loads(definition.read_text())
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for ref in source["evidence"]:
        path = definition.parent / ref["path"]
        saved = read_hashed(path, ref["sha256"])
        records.append((path, saved))
    comparisons = []
    scene = None
    for pair in source["pairs"]:
        panels = []
        images = []
        for case_id in pair["cases"]:
            path, record, case = next(
                (path, record, c)
                for path, record in records
                for c in record["cases"]
                if c["id"] == case_id and c["media"]
            )
            index = case["wrist"]["summary"]["flexion_r"][
                "extreme_reference_sample_index"
            ]
            state = next(s for s in case["media"] if s["sample_index"] == index)
            image_path = path.parent / state["directory"] / "hand.png"
            relative = str(image_path.relative_to(path.parent))
            if (
                hashlib.sha256(image_path.read_bytes()).hexdigest()
                != record["artifact_sha256"][relative]
            ):
                raise ValueError("Gallery source image hash differs")
            images.append(Image.open(image_path).copy())
            panels.append(
                dict(
                    case_id=case_id,
                    sample_index=index,
                    qpos_rad=state["qpos_rad"],
                    active_contacts=state["active_contacts"],
                    cameras=state["cameras"],
                    image_reference=dict(
                        path=os.path.relpath(image_path, definition.parent),
                        sha256=record["artifact_sha256"][relative],
                    ),
                )
            )
            saved = read_hashed(
                definition.parent / case["source"]["search_result"],
                case["source"]["search_sha256"],
            )
            e = Experiment.from_dict(saved["scene_input"])
            scene = build_scene(
                e.geometry, e.player, e.setup, e.physical_contact, DIGITS
            )
        if panels[0]["cameras"] != panels[1]["cameras"]:
            raise ValueError("Gallery needs matched cameras")
        canvas = Image.new("RGB", (1920, 720))
        for i, image in enumerate(images):
            canvas.paste(image, (i * 960, 0))
        canvas.save(output / (pair["id"] + ".png"))
        comparisons.append(dict(id=pair["id"], panels=panels))
    if scene is None:
        raise ValueError("Empty gallery")
    return finish_record(
        definition,
        output,
        source,
        dict(id="posture-gallery-052", comparisons=comparisons),
        scene,
    )
