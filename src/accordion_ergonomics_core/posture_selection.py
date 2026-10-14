"""Policy explanations, paired controls and separate numerical initial approaches."""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .movement_evidence import state_digest
from .passage_media import independent_samples
from .passage_search import audit_contact_path
from .planning import PlanningSettings
from .quality_plots import trace_svg
from .render import render_views
from .scene import build_scene
from .selection import posture_strategy_order
from .wrist import WristReference
from .wrist_study import finish_record


def run_posture_selection(definition: Path, output: Path):
    source = json.loads(definition.read_text())
    record = read_hashed(
        definition.parent / source["audit_result"], source["audit_sha256"]
    )
    output.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    for case in record["cases"]:
        grouped[case["source"]["id"]].append(case)
    rankings = []
    for trial, cases in grouped.items():
        rankings.append(
            dict(
                trial_id=trial,
                policies={
                    p: posture_strategy_order(cases, p)
                    for p in ("palm", "movement", "posture", "whole_hand")
                },
                reference_sensitivity=[
                    dict(
                        reference=r,
                        ranking=posture_strategy_order(
                            cases, "posture", WristReference(**r)
                        ),
                    )
                    for r in source["alternative_references"]
                ],
            )
        )
    pairs = []
    for request in source["paired_trials"]:
        base = read_hashed(
            definition.parent
            / grouped[request["baseline"]][0]["source"]["search_result"],
            grouped[request["baseline"]][0]["source"]["search_sha256"],
        )
        replay_ref = source["baseline_replays"][request["baseline"]]
        replay = read_hashed(
            definition.parent / replay_ref["path"], replay_ref["sha256"]
        )
        if replay["strategies"] != base["strategies"]:
            raise ValueError(
                "Current baseline replay differs from historical strategies"
            )
        base = replay
        changed = read_hashed(
            definition.parent
            / grouped[request["changed"]][0]["source"]["search_result"],
            grouped[request["changed"]][0]["source"]["search_sha256"],
        )
        base_settings = dict(base["settings"])
        changed_settings = dict(changed["settings"])
        base_settings.pop("selection_mode")
        changed_settings.pop("selection_mode")
        if (
            base_settings != changed_settings
            or base["initial_qpos_rad"] != changed["initial_qpos_rad"]
            or base["provenance"]["compiled_model_sha256"]
            != changed["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Paired control changed more than selection mode")
        pairs.append(
            dict(
                **request,
                matched_model=base["provenance"]["compiled_model_sha256"],
                matched_initial_qpos_rad=base["initial_qpos_rad"],
                matched_settings=base_settings,
                baseline_budget=base["budget"],
                changed_budget=changed["budget"],
                baseline_strategy_id=grouped[request["baseline"]][0]["id"],
                changed_strategy_id=grouped[request["changed"]][0]["id"],
                claim=(
                    "Matched caps and seed; different branches consume "
                    "different actual calls. Finite discovered "
                    "alternatives, not optimality."
                ),
            )
        )
    pools = {}
    for pool in source["candidate_pools"]:
        candidates = [c for trial in pool["trials"] for c in grouped[trial]]
        pools[pool["id"]] = {
            p: posture_strategy_order(candidates, p)
            for p in ("palm", "movement", "posture", "whole_hand")
        }
    movement = []
    for _trial, cases in grouped.items():
        saved = read_hashed(
            definition.parent / cases[0]["source"]["search_result"],
            cases[0]["source"]["search_sha256"],
        )
        for case in cases:
            hand = case["whole_hand"]
            strategy = next(
                s for s in saved["strategies"] if s["id"] == case["strategy_id"]
            )
            edges = {edge["id"]: edge for edge in saved["edges"]}
            intervals = []
            for edge_id in strategy["edge_ids"]:
                samples = edges[edge_id]["path"]["samples"]

                palm = np.array([sample["palm_world_m"] for sample in samples])
                displacement = float(np.linalg.norm(palm[-1] - palm[0]))
                length = float(np.linalg.norm(np.diff(palm, axis=0), axis=1).sum())
                intervals.append(
                    dict(
                        edge_id=edge_id,
                        palm_path_m=length,
                        palm_endpoint_displacement_m=displacement,
                        geometric_detour_ratio=length / displacement
                        if displacement > 1e-9
                        else None,
                    )
                )
            movement.append(
                dict(
                    case_id=case["id"],
                    intervals=intervals,
                    palm_board_normal_minimum_m=min(
                        t["palm_board_m"][2] for t in hand["traces"]
                    ),
                    palm_board_normal_maximum_m=max(
                        t["palm_board_m"][2] for t in hand["traces"]
                    ),
                    interpretation=(
                        "Geometric relocation descriptors; no hovering, "
                        "speed, smoothness or fatigue threshold"
                    ),
                )
            )
    approach = []
    scene = None
    for trial in source["initial_approach_trials"]:
        case = grouped[trial][0]
        saved = read_hashed(
            definition.parent / case["source"]["search_result"],
            case["source"]["search_sha256"],
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
        strategy = next(
            s for s in saved["strategies"] if s["id"] == case["strategy_id"]
        )
        endpoint = strategy["samples"][0]["qpos_rad"]
        start = saved["initial_qpos_rad"]
        path = audit_contact_path(
            scene,
            e,
            [start, endpoint],
            [],
            PlanningSettings(max_joint_step_rad=0.003, rrt_iterations=0),
        )
        independent = independent_samples(
            scene, path["samples"], e.solver.penetration_tolerance_m
        )
        accepted = (
            path["sampled_constraints_satisfied"]
            and independent["status"] == "sampled_proxy_constraints_satisfied"
        )
        media = []
        if source.get("render_approaches"):
            index = min(
                range(len(path["samples"])),
                key=lambda i: independent["samples"][i][
                    "minimum_instrument_distance_m"
                ],
            )
            for i in sorted({0, index, len(path["samples"]) - 1}):
                scene.data.qpos[:] = path["samples"][i]["qpos_rad"]
                c = strategy["events"][0]["contacts"][0]
                directory = output / f"{trial}-approach-state-{i}"
                cameras = render_views(
                    scene,
                    directory,
                    e.geometry.surface_world_m(
                        button_at(c["row"], c["column"])
                    ).tolist(),
                    c["button_id"],
                    collision_overlay=True,
                    highlighted_proxy_names=tuple(
                        independent["worst_cross_digit"]["geoms"]
                    ),
                    state_label=(
                        f"Reference-approach diagnostic | sample {i} | "
                        f"accepted sampled checks: {accepted}"
                    ),
                    camera_overrides=source["cameras"],
                )
                media.append(
                    dict(
                        directory=directory.name,
                        sample_index=i,
                        qpos_rad=path["samples"][i]["qpos_rad"],
                        active_contacts=[],
                        cameras=cameras,
                    )
                )
        approach.append(
            dict(
                trial_id=trial,
                strategy_id=case["strategy_id"],
                reference=(
                    "Resolved numerical 037 C4 contact seed; not natural "
                    "resting posture"
                ),
                status="sampled_reference_approach"
                if accepted
                else "rejected_direct_reference_approach",
                path=path,
                independent_audit=independent,
                state_sequence_sha256=state_digest(path["samples"]),
                media=media,
                interpretation=(
                    "Separate direct joint-space candidate; failed "
                    "approach does not invalidate the subsequent "
                    "connected passage. No approach animation for "
                    "rejected candidates."
                ),
            )
        )
    if scene is None:
        saved = read_hashed(
            definition.parent / record["cases"][0]["source"]["search_result"],
            record["cases"][0]["source"]["search_sha256"],
        )
        e = Experiment.from_dict(saved["scene_input"])
        scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    selected = [grouped[p["changed"]][0] for p in source["paired_trials"]]
    trace_svg(
        output / "paired-tradeoffs.svg",
        "Posture-aware selected paths; actual sampled records",
        [
            dict(
                label="Maximum reference departure (rad)",
                series={
                    n: [
                        c["wrist"]["summary"][n]["maximum_reference_departure_rad"]
                        for c in selected
                    ]
                    for n in ("flexion_r", "deviation_r")
                },
            ),
            dict(
                label="Palm path (m)",
                series={"palm": [c["whole_hand"]["palm_path_m"] for c in selected]},
            ),
            dict(
                label="Independent worst cross-digit proxy (m)",
                series={
                    "proxy": [
                        c["independent_audit"]["worst_cross_digit"]["distance_m"]
                        for c in selected
                    ]
                },
            ),
        ],
        x_axis="ordered independent matched trial; not movement",
    )
    return finish_record(
        definition,
        output,
        source,
        dict(
            id="posture-selection-052",
            rankings=rankings,
            candidate_pools=pools,
            movement_geometry=movement,
            paired_trials=pairs,
            initial_approaches=approach,
            full_path_scope=(
                "All retained complete strategies audited; "
                "beam-pruned and budget-unexplored branches remain "
                "unevaluated beyond their recorded search scope"
            ),
            muscle_policy="withheld",
        ),
        scene,
    )
