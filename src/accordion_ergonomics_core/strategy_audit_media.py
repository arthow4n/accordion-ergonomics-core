"""Matched benchmark media from saved states and independent computational audits."""

import hashlib
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .passage_media import render_strategy, search_diagram
from .provenance import compiled_model_digest, current_execution_metadata
from .render import render_views
from .research import ExerciseLibrary
from .scene import build_scene


def run_strategy_audit_media(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    record = read_hashed(
        definition.parent / source["audit_result"], source["audit_sha256"]
    )
    library = ExerciseLibrary(definition.resolve().parents[2])
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    cameras = None
    scene = None
    for case in record["cases"]:
        reference = case["source_reference"]
        saved = read_hashed(
            definition.parent / reference["search_result"], reference["search_sha256"]
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        if (
            compiled_model_digest(scene.model)
            != saved["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Media and original numerical models disagree")
        index = case["worst_proxy_sample_index"]
        state = case["traces"][index]
        scene.data.qpos[:] = state["qpos_rad"]
        contacts = state["active_contacts"]
        strategy = next(
            (s for s in saved["strategies"] if s["id"] == reference["strategy_id"]),
            None,
        )
        if not contacts:
            if strategy is None:
                raise ValueError("Missing attempted contact requirements")
            contacts = strategy["events"][-1]["contacts"]
        primary = contacts[0]
        names = case["joint_names"]
        wrist = [
            state["qpos_rad"][names.index(n)] for n in ("flexion_r", "deviation_r")
        ]
        case_dir = output / reference["id"]
        label = (
            f"{reference['id']} | exact state {index} | "
            f"wrist {wrist[0]:.3f}/{wrist[1]:.3f} rad | "
            f"proxy {state['worst_cross_digit_proxy_m'] * 1000:.2f} mm | "
            f"{state['source_node_status'] or 'sampled path'} | "
            "initial approach unplanned"
        )
        actual_cameras = render_views(
            scene,
            case_dir / "worst-state",
            e.geometry.surface_world_m(
                button_at(primary["row"], primary["column"])
            ).tolist(),
            primary["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=tuple(state["worst_cross_digit_pair"]),
            contact_roles=state["roles"],
            button_roles={
                c["button_id"]: state["roles"].get(c["finger"], "moving")
                for c in contacts
            },
            state_label=label,
            camera_overrides=cameras,
        )
        if cameras is None:
            cameras = actual_cameras
        search_diagram(saved, case_dir / "search.svg")
        report = {
            "id": reference["id"],
            "source": reference,
            "state_kind": case["state_kind"],
            "worst_state": state,
            "cameras": actual_cameras,
            "animation": None,
        }
        if reference["id"] in source["animate"]:
            if strategy is None:
                raise ValueError("Failed benchmark cannot be animated as movement")
            query = source["library_bindings"][reference["id"]]
            audit = library.diagnostics(
                query["target_id"],
                reference["strategy_id"],
                trial_id=query.get("trial_id"),
            )
            if audit["worst_cross_digit"]["distance_m"] != case["worst_proxy_m"]:
                raise ValueError("Independent old and fresh proxy audits disagree")
            report["animation"] = render_strategy(
                scene,
                saved,
                strategy,
                audit,
                case_dir / "path",
                source["frames"],
                {"hand": cameras["hand"]},
                "Initial approach unplanned",
            )
        reports.append(report)
    for label, ids in source["comparisons"].items():
        canvas = Image.new("RGB", (960 * len(ids), 760), "#142030")
        for i, case_id in enumerate(ids):
            with Image.open(output / case_id / "worst-state/hand.png") as im:
                canvas.paste(im, (960 * i, 40))
            ImageDraw.Draw(canvas).text(
                (960 * i + 12, 12),
                case_id + " | own worst sample; matched cameras",
                fill="white",
            )
        canvas.save(output / (label + ".png"))
    if scene is None:
        raise ValueError("Empty media benchmark")
    result = {
        "id": "strategy-audit-media-045",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "cases": reports,
        "camera_claim": (
            "Same actual camera parameters for every case; "
            "own worst states are not synchronized event stages"
        ),
        "artifact_sha256": {
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob("*")
            if p.suffix in (".svg", ".png", ".gif")
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
