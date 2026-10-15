"""Frozen whole-hand/lifecycle benchmark and matched physical evidence workflow."""

import json
from typing import Any

from PIL import Image, ImageDraw

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .movement_evidence import validate_strategy
from .passage_media import independent_samples, search_diagram
from .playing_media import board_panel, render_playing_evidence
from .playing_region import playing_region_trace, preparation_linkage
from .provenance import compiled_model_digest
from .scene import build_scene
from .strategy_audit import audit_states, plots
from .wrist_study import finish_record


def run_playing_study(definition, output):
    source = json.loads(definition.read_text())
    output.mkdir(parents=True, exist_ok=True)
    cases: list[dict[str, Any]] = []
    scene = None
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
            raise ValueError("Playing analysis must use exact recorded compiled world")
        strategy = next(
            s
            for s in saved["strategies"]
            if s["id"] == request.get("strategy_id", "strategy-0")
        )
        validate_strategy(saved, strategy)
        directory = output / request["id"]
        directory.mkdir()
        region = playing_region_trace(
            scene, e, strategy, lifecycle=source.get("lifecycle", True)
        )
        region["label"] = request["id"]
        whole = audit_states(
            scene, e.geometry, strategy["samples"], saved["joint_names"]
        )
        audit = independent_samples(
            scene, strategy["samples"], e.solver.penetration_tolerance_m
        )
        search_diagram(saved, directory / "search.svg")
        plots(whole, directory / "joints.svg", request["id"])
        board_panel([region], bounds=source.get("board_bounds_m")).save(
            directory / "board-path.png"
        )
        record = dict(
            id=request["id"],
            source=request,
            strategy_id=strategy["id"],
            region=region,
            whole_hand=whole,
            independent_audit=audit,
            media=None,
            settings=saved["settings"],
            budget=saved["budget"],
            compiled_model_sha256=compiled_model_digest(scene.model),
            preparation_links=preparation_linkage(strategy["events"]),
        )
        if request.get("render"):
            record["media"] = render_playing_evidence(
                scene,
                saved,
                strategy,
                region,
                audit,
                whole,
                directory,
                source.get("cameras"),
                source.get("frames", 48),
                bounds=source.get("board_bounds_m"),
            )
        cases.append(record)
    comparisons = []
    for pair in source.get("comparisons", []):
        matched = [
            next(c for c in cases if c["id"] == ident) for ident in pair["cases"]
        ]
        if len({c["compiled_model_sha256"] for c in matched}) != 1:
            raise ValueError("Comparison models differ")
        board_panel(
            [c["region"] for c in matched], bounds=source.get("board_bounds_m")
        ).save(output / (pair["id"] + ".png"))
        event_panels = []
        if all(c["media"] for c in matched):
            event_rows = []
            for case in matched:
                event_rows.append(
                    [
                        row
                        for row in case["region"]["traces"]
                        if row["event_index"] is not None
                    ]
                )
            if len({len(rows) for rows in event_rows}) != 1:
                raise ValueError("Matched comparison musical event counts differ")
            image = Image.new(
                "RGB", (480 * len(matched), 390 * len(event_rows[0])), "white"
            )
            draw = ImageDraw.Draw(image)
            for column, (case, rows) in enumerate(
                zip(matched, event_rows, strict=True)
            ):
                for row_index, row in enumerate(rows):
                    frame = next(
                        f
                        for f in case["media"]["dense"]["frames"]
                        if f["sample_index"] == row["sample_index"]
                    )
                    path = output / case["id"] / "dense" / frame["frame"]
                    with Image.open(path) as panel:
                        image.paste(
                            panel.resize((480, 360)), (column * 480, row_index * 390)
                        )
                    draw.text(
                        (column * 480 + 5, row_index * 390 + 365),
                        f"{case['id']} / event {row['event_index']} "
                        f"/ sample {row['sample_index']}",
                        fill="black",
                    )
                    event_panels.append(
                        dict(
                            case_id=case["id"],
                            event_index=row["event_index"],
                            sample_index=row["sample_index"],
                            frame=str(path.relative_to(output)),
                            frame_sha256=frame["frame_sha256"],
                        )
                    )
            image.save(output / (pair["id"] + "-events.png"))
        comparisons.append(
            dict(
                event_panels=event_panels,
                **pair,
                image=pair["id"] + ".png",
                claim="Common physical mm axes; actual paths, not equal time",
            )
        )
    if scene is None:
        raise ValueError("Empty playing benchmark")
    return finish_record(
        definition,
        output,
        source,
        dict(
            id=source["id"],
            assessment_version="playing-region-lifecycle-v3",
            cases=cases,
            comparisons=comparisons,
        ),
        scene,
    )
