"""Independent negative evidence, initial approach attempts and policy comparisons."""

import json
from typing import Any

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .passage_media import independent_samples, search_diagram
from .passage_search import (
    audit_contact_path,
    contact_check,
    plan_contact_change,
)
from .planning import PlanningSettings
from .provenance import compiled_model_digest
from .render import render_views
from .scene import build_scene
from .wrist_study import finish_record


def run_playing_review(definition, output):
    source = json.loads(definition.read_text())
    output.mkdir(parents=True, exist_ok=True)
    records = []
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
            raise ValueError("Review changed compiled world")
        directory = output / request["id"]
        directory.mkdir()
        search_diagram(saved, directory / "search.svg")
        states: list[dict[str, Any]] = []
        details: dict[str, Any]
        if request["kind"] == "held_failure":
            failed = next(
                n
                for n in saved["nodes"]
                if n["event_index"] > 0 and n["status"] == "failed_contact_solve"
            )
            parent = next(n for n in saved["nodes"] if n["id"] == failed["parent"])
            held = [c for c in parent["contacts"] if c["behavior"] == "hold"]
            start, end = parent["qpos_rad"], failed["contact_solve"]["qpos_rad"]
            probe = audit_contact_path(
                scene, e, [start, end], held, PlanningSettings(max_joint_step_rad=0.003)
            )
            details = dict(
                kind="rejected_diagnostic_interpolation_not_movement",
                parent_node=parent["id"],
                failed_node=failed["id"],
                held_contacts=held,
                failed_solve=failed["contact_solve"],
                diagnostic_probe=probe,
            )
            states = [
                dict(
                    label="last valid held contact",
                    qpos_rad=start,
                    contacts=parent["contacts"],
                ),
                dict(
                    label="attempted failed chord; not accepted movement",
                    qpos_rad=end,
                    contacts=failed["contacts"],
                ),
            ]
        elif request["kind"] == "initial_approach":
            strategy = next(
                s
                for s in saved["strategies"]
                if s["id"] == request.get("strategy_id", "strategy-0")
            )
            start = saved["initial_qpos_rad"]
            end = strategy["events"][0]["qpos_rad"]
            contacts = []
            for c in e.contacts:
                b = button_at(c.row, c.column)
                contacts.append(
                    dict(
                        row=b.row,
                        column=b.column,
                        button_id=b.id,
                        midi=b.midi,
                        finger=c.finger,
                        behavior="release_after_event",
                    )
                )
            target = strategy["events"][0]["contacts"]
            planning = dict(saved["settings"]["planning"])
            planning["withdrawal_depths_m"] = tuple(planning["withdrawal_depths_m"])
            path = plan_contact_change(
                scene,
                e,
                contacts,
                target,
                start,
                end,
                [],
                PlanningSettings(**planning),
                request.get("guidance_cost", 0.0),
                "geometric",
            )
            details = dict(
                kind="numerical_seed_approach_not_resting_hand",
                path=path,
                source_contacts=contacts,
                destination_contacts=target,
                status=path["status"],
                counted_separately_from_passage_budget=True,
            )
            states = [
                dict(
                    label="resolved numerical seed, not resting hand",
                    qpos_rad=start,
                    contacts=contacts,
                ),
                dict(
                    label="first contact endpoint; approach status " + path["status"],
                    qpos_rad=end,
                    contacts=target,
                ),
            ]
            if path.get("samples"):
                checked = independent_samples(
                    scene, path["samples"], e.solver.penetration_tolerance_m
                )
                details["independent_approach_audit"] = checked
                indices = checked["violation_sample_indices"]
                if indices:
                    states.append(
                        dict(
                            label="rejected approach sample",
                            qpos_rad=path["samples"][indices[0]]["qpos_rad"],
                            contacts=target,
                        )
                    )
                # A separate path is saved; no attachment to the historical passage.
                details["initial_approach_claim"] = (
                    "Separate attempted connection; original passage "
                    "initial approach remains unplanned"
                )
                if (
                    path["status"] == "sampled_path_found"
                    and checked["status"] == "sampled_proxy_constraints_satisfied"
                ):
                    from .playing_media import render_playing_evidence
                    from .playing_region import playing_region_trace
                    from .strategy_audit import audit_states

                    part = []
                    for i, sample in enumerate(path["samples"]):
                        active = (
                            contacts
                            if i == 0
                            else target
                            if i == len(path["samples"]) - 1
                            else []
                        )
                        part.append(
                            dict(
                                **{
                                    k: v
                                    for k, v in sample.items()
                                    if k
                                    not in (
                                        "event_index",
                                        "active_contacts",
                                        "roles",
                                        "event_interval",
                                        "edge_id",
                                    )
                                },
                                event_index=0
                                if i == 0
                                else 1
                                if i == len(path["samples"]) - 1
                                else None,
                                active_contacts=active,
                                roles={c["finger"]: "required" for c in active},
                                event_interval=0,
                                edge_id="actual-approach",
                            )
                        )
                    graph = dict(
                        id=request["id"],
                        scene_input=saved["scene_input"],
                        joint_names=saved["joint_names"],
                        nodes=[
                            dict(
                                id="seed",
                                qpos_rad=part[0]["qpos_rad"],
                                contacts=contacts,
                                preparing=[],
                                event_index=0,
                                status="recorded_seed",
                            ),
                            dict(
                                id="first",
                                qpos_rad=part[-1]["qpos_rad"],
                                contacts=target,
                                preparing=[],
                                event_index=1,
                                status="accepted_contact",
                            ),
                        ],
                        edges=[
                            dict(
                                id="actual-approach",
                                source="seed",
                                destination="first",
                                status="sampled_path_found",
                                path=dict(samples=part),
                            )
                        ],
                    )
                    approach = dict(
                        id="approach-strategy",
                        status="sampled_connected_path",
                        node_ids=["seed", "first"],
                        edge_ids=["actual-approach"],
                        samples=part,
                        events=[
                            dict(contacts=contacts, qpos_rad=part[0]["qpos_rad"]),
                            dict(contacts=target, qpos_rad=part[-1]["qpos_rad"]),
                        ],
                    )
                    region = playing_region_trace(scene, e, approach)
                    region["label"] = request["id"]
                    region["initial_approach"] = (
                        "separate_resolved_numerical_seed_approach"
                    )
                    region["approach_label"] = (
                        "Separate numerical C4 seed approach; no resting hand, "
                        "actuation or performance timing"
                    )
                    whole = audit_states(scene, e.geometry, part, saved["joint_names"])
                    details["approach_graph"] = graph
                    details["approach_strategy"] = approach
                    details["exact_original_first_pose_reached"] = (
                        part[-1]["qpos_rad"] == end
                    )
                    details["media"] = render_playing_evidence(
                        scene,
                        graph,
                        approach,
                        region,
                        checked,
                        whole,
                        directory / "approach-media",
                        source.get("cameras"),
                        36,
                        context_label=region["approach_label"],
                    )
                    details["region"] = region
        else:
            raise ValueError("Unknown review kind")
        rendered = []
        for i, state in enumerate(states):
            scene.data.qpos[:] = state["qpos_rad"]
            checks = contact_check(scene, e, state["contacts"])
            held_checks = contact_check(scene, e, details.get("held_contacts", []))
            independent = independent_samples(
                scene, [state], e.solver.penetration_tolerance_m
            )
            c = state["contacts"][0]
            camera = render_views(
                scene,
                directory / f"state-{i}",
                e.geometry.surface_world_m(button_at(c["row"], c["column"])).tolist(),
                c["button_id"],
                collision_overlay=True,
                highlighted_proxy_names=tuple(
                    independent["worst_cross_digit"]["geoms"]
                ),
                contact_roles={
                    c["finger"]: "held" if c["behavior"] == "hold" else "required"
                    for c in state["contacts"]
                },
                state_label=state["label"],
                camera_overrides=source.get("cameras"),
            )
            rendered.append(
                dict(
                    **state,
                    contact_check=checks,
                    held_check=held_checks,
                    independent_audit=independent,
                    cameras=camera,
                    directory=f"state-{i}",
                )
            )
        records.append(
            dict(id=request["id"], source=request, details=details, states=rendered)
        )
    # Policy tables preserve every retained candidate and executed budget.
    comparisons = []
    for group in source.get("comparison_groups", []):
        cases = []
        for ref in group["records"]:
            r = read_hashed(definition.parent / ref["path"], ref["sha256"])
            cases.append(
                dict(
                    source=ref,
                    status=r["status"],
                    settings=r["settings"],
                    budget=r["budget"],
                    strategies=[
                        dict(
                            id=s["id"],
                            cost_palm_path_m=s["cost_palm_path_m"],
                            sample_count=len(s["samples"]),
                            contacts=[ev["contacts"] for ev in s["events"]],
                        )
                        for s in r["strategies"]
                    ],
                )
            )
        comparisons.append(
            dict(
                id=group["id"],
                candidates=cases,
                claim="Matched caps; consumed budgets and branches may differ; "
                "no universal ranking",
            )
        )
    if scene is None:
        raise ValueError("Review needs actual states")
    return finish_record(
        definition,
        output,
        source,
        dict(id=source["id"], records=records, comparisons=comparisons),
        scene,
    )
