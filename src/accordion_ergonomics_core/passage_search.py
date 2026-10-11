"""Bounded whole-hand beam search over musical assignments and audited movements."""

from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any

import numpy as np

from ._engine import mujoco
from .digits import DIGITS
from .experiment import ContactRequest, Experiment
from .instrument import button_at
from .passages import Passage, fingering_hypotheses
from .planning import PlanningSettings, audit_path, plan_transition
from .provenance import current_execution_metadata
from .scene import Scene, build_scene, diagnostics
from .solver import accepted, solve_contact

ROOT = (
    Path.cwd()
    if (
        Path.cwd() / "experiments/037-upper-anchor-regression/central/result.json"
    ).is_file()
    else Path(__file__).resolve().parents[2]
)


@dataclass(frozen=True)
class PassageSearchSettings:
    seed: int = 4201
    beam_width: int = 2
    assignments_per_parent: int = 5
    contact_iterations: int = 160
    preparation_height_m: float = 0.015
    prepare_next: bool = True
    assignment_order: str = "seeded"
    fingers: tuple[str, ...] = DIGITS
    planning: PlanningSettings = field(
        default_factory=lambda: PlanningSettings(
            withdrawal_depths_m=(0.01, 0.02, 0.04),
            waypoint_iterations=160,
            max_joint_step_rad=0.002,
            rrt_iterations=300,
        )
    )

    def __post_init__(self) -> None:
        if any(
            type(v) is not int or v < 1
            for v in (
                self.beam_width,
                self.assignments_per_parent,
                self.contact_iterations,
            )
        ):
            raise ValueError("Search budgets must be positive integers")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("Seed must be a nonnegative integer")
        if not np.isfinite(self.preparation_height_m) or self.preparation_height_m <= 0:
            raise ValueError("Preparation height must be positive")
        if self.assignment_order not in ("seeded", "marker_distance"):
            raise ValueError("Unknown assignment priority")
        if type(self.prepare_next) is not bool:
            raise ValueError("Preparation policy must be boolean")
        if (
            not self.fingers
            or len(set(self.fingers)) != len(self.fingers)
            or set(self.fingers) - set(DIGITS)
        ):
            raise ValueError("Search fingers must be a distinct named subset")


def reference_experiment(root: Path | None = None) -> Experiment:
    """Load the internal fixed reference; consumers need not open experiment folders."""
    import json

    saved = json.loads(
        (
            (root or ROOT)
            / "experiments/037-upper-anchor-regression/central/result.json"
        ).read_text()
    )
    e = Experiment.from_dict(saved["input"])
    return replace(
        e,
        initial_joints_rad=dict(
            zip(saved["joint_names"], saved["qpos_rad"], strict=True)
        ),
    )


def point(e: Experiment, contact: dict[str, Any]) -> np.ndarray:
    return e.geometry.surface_world_m(button_at(contact["row"], contact["column"]))


def contact_check(
    scene: Scene, e: Experiment, contacts: list[dict[str, Any]]
) -> dict[str, Any]:
    checks = [
        {
            "finger": c["finger"],
            "button_id": c["button_id"],
            **diagnostics(scene, point(e, c), c["button_id"], c["finger"]),
        }
        for c in contacts
    ]
    return {"satisfied": all(accepted(c, e.solver) for c in checks), "contacts": checks}


def solve_targets(
    scene: Scene,
    e: Experiment,
    q: list[float],
    contacts: list[dict[str, Any]],
    targets: list[np.ndarray],
    required: list[bool],
    iterations: int,
) -> dict[str, Any]:
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    return solve_contact(
        scene,
        targets[0],
        dict(zip(names, q, strict=True)),
        replace(e.solver, max_iterations=iterations),
        contacts[0]["button_id"],
        e.frozen_joints,
        finger=contacts[0]["finger"],
        additional_contacts=tuple(
            (t, c["finger"], c["button_id"])
            for t, c in zip(targets[1:], contacts[1:], strict=True)
        ),
        required_contacts=tuple(required),
    )


def audit_contact_path(
    scene: Scene,
    e: Experiment,
    waypoints: list[list[float]],
    held: list[dict[str, Any]],
    settings: PlanningSettings,
) -> dict[str, Any]:
    audit = audit_path(scene, waypoints, e, settings)
    violations = []
    maximum_error = 0.0
    for i, sample in enumerate(audit["samples"]):
        scene.data.qpos[:] = sample["qpos_rad"]
        check = contact_check(scene, e, held)
        if not check["satisfied"]:
            violations.append(i)
        maximum_error = max(
            maximum_error,
            max((c["position_error_m"] for c in check["contacts"]), default=0.0),
        )
    audit["held_violation_sample_indices"] = violations
    audit["held_marker_error_max_m"] = maximum_error
    audit["held_contacts"] = held
    audit["sampled_constraints_satisfied"] &= not violations
    audit["status"] = (
        "sampled_path_found"
        if audit["sampled_constraints_satisfied"]
        else "candidate_rejected"
    )
    return audit


def plan_contact_change(
    scene: Scene,
    e: Experiment,
    source: list[dict[str, Any]],
    destination: list[dict[str, Any]],
    start_q: list[float],
    end_q: list[float],
    held: list[dict[str, Any]],
    settings: PlanningSettings,
) -> dict[str, Any]:
    """Release/reposition/approach; incremental IK states are audited as a path.

    A waypoint continuation may reach a different valid endpoint than the first
    contact solve. The achieved configuration becomes the actual child node.
    """
    source_binding = {(c["finger"], c["button_id"]) for c in source}
    dest_binding = {(c["finger"], c["button_id"]) for c in destination}
    held_binding = {(c["finger"], c["button_id"]) for c in held}
    if not held_binding <= source_binding & dest_binding:
        raise ValueError("Held binding must persist through both events")
    repeated_release = bool(
        ({c["button_id"] for c in source} & {c["button_id"] for c in destination})
        - {c["button_id"] for c in held}
    )
    if len(source) == len(destination) == 1 and not held and not repeated_release:
        single = replace(
            e,
            contacts=(
                ContactRequest(
                    source[0]["row"], source[0]["column"], source[0]["finger"]
                ),
            ),
        )
        result = plan_transition(
            scene,
            single,
            start_q,
            end_q,
            destination[0]["button_id"],
            settings,
            end_finger=destination[0]["finger"],
        )
        if result["status"] == "sampled_path_found":
            result["achieved_qpos_rad"] = result["samples"][-1]["qpos_rad"]
        return result
    direct = audit_contact_path(scene, e, [start_q, end_q], held, settings)
    if repeated_release:
        direct["status"] = "rejected_missing_release"
        direct["musical_release_satisfied"] = False
    if not repeated_release and direct["sampled_constraints_satisfied"]:
        for sample in direct["samples"]:
            sample["phase"] = {
                "phase": "audited_joint_interpolation",
                "moving_fingers": sorted(
                    {
                        c["finger"]
                        for c in [
                            c
                            for c in source + destination
                            if (c["finger"], c["button_id"]) not in held_binding
                        ]
                    }
                ),
            }
        return {
            **direct,
            "method": "audited-direct-interpolation",
            "achieved_qpos_rad": end_q,
            "attempts": [],
        }
    normal = e.geometry.rotation[:, 2]
    source_moving = [
        c for c in source if (c["finger"], c["button_id"]) not in held_binding
    ]
    dest_moving = [
        c for c in destination if (c["finger"], c["button_id"]) not in held_binding
    ]
    attempts = []
    waypoint_calls = 0
    for depth in settings.withdrawal_depths_m:
        if (
            settings.waypoint_solve_limit is not None
            and waypoint_calls >= settings.waypoint_solve_limit
        ):
            break
        q = start_q
        waypoints = [q]
        phases = []
        solves = []
        failure = None
        # Each leg controls held plus moving digits, leaving the others free.
        for phase in ("withdraw", "reposition", "approach"):
            moving = source_moving if phase == "withdraw" else dest_moving
            contacts = held + moving
            if not contacts:
                continue
            scene.data.qpos[:] = q
            mujoco.mj_forward(scene.model, scene.data)
            begin = [
                scene.data.site(f"{c['finger']}_pad").xpos.copy() for c in contacts
            ]
            end = [
                point(e, c)
                if c in held or phase == "approach"
                else point(e, c) + normal * depth
                for c in contacts
            ]
            count = max(
                1,
                int(
                    np.ceil(
                        max(
                            np.linalg.norm(a - b)
                            for a, b in zip(begin, end, strict=True)
                        )
                        / settings.withdrawal_step_m
                    )
                ),
            )
            for fraction in np.linspace(0, 1, count + 1)[1:]:
                targets = [
                    a + fraction * (b - a) for a, b in zip(begin, end, strict=True)
                ]
                required = [c in held for c in contacts]
                if phase == "approach" and fraction == 1:
                    required = [True] * len(contacts)
                if (
                    settings.waypoint_solve_limit is not None
                    and waypoint_calls >= settings.waypoint_solve_limit
                ):
                    failure = "waypoint_budget_exhausted"
                    break
                waypoint_calls += 1
                solve = solve_targets(
                    scene,
                    e,
                    q,
                    contacts,
                    targets,
                    required,
                    settings.waypoint_iterations,
                )
                solves.append(
                    {
                        "phase": phase,
                        "fraction": float(fraction),
                        "cartesian_targets_world_m": [t.tolist() for t in targets],
                        "required_contacts": required,
                        "contacts": contacts,
                        "result": solve,
                    }
                )
                if solve["status"] != "success":
                    failure = "waypoint_solver_failed"
                    break
                q = solve["qpos_rad"]
                waypoints.append(q)
                phases.append(
                    {"phase": phase, "moving_fingers": [c["finger"] for c in moving]}
                )
            if failure:
                break
        audit = audit_contact_path(scene, e, waypoints, held, settings)
        scene.data.qpos[:] = q
        ending = contact_check(scene, e, destination)
        found = (
            failure is None
            and audit["sampled_constraints_satisfied"]
            and ending["satisfied"]
        )
        attempt = {
            "depth_m": depth,
            "failure": failure,
            "waypoint_solves": solves,
            "waypoint_solver_calls": len(solves),
            "waypoints_qpos_rad": waypoints,
            "phases": phases,
            "audit": {k: v for k, v in audit.items() if k != "samples"},
            "ending_contacts": ending,
        }
        attempts.append(attempt)
        if found:
            for sample in audit["samples"]:
                if phases:
                    sample["phase"] = phases[min(sample["segment"], len(phases) - 1)]
            return {
                **audit,
                "method": "incremental-named-contact-change",
                "attempts": attempts,
                "achieved_qpos_rad": q,
                "waypoints_qpos_rad": waypoints,
                "geometric_release_required": repeated_release,
                "continuous_validity": None,
                "physical_feasibility": None,
            }
    return {
        "status": "no_path_found",
        "direct_audit": direct,
        "attempts": attempts,
        "geometric_release_required": repeated_release,
        "claim": "Finite continuation search failed, not an impossibility proof",
    }


def search_passage(
    passage: Passage,
    reference: Experiment | None = None,
    settings: PassageSearchSettings | None = None,
) -> dict[str, Any]:
    """Search actual connected branches; costs describe a bounded search only."""
    e = reference or reference_experiment()
    settings = settings or PassageSearchSettings()
    if (
        e.player.model != "myofullbody_reduced"
        or e.geometry.geometry_model != "generic_cba_v3"
    ):
        raise ValueError(
            "Passage discovery requires the fixed native compact CBA reference"
        )
    e = replace(
        e,
        physical_contact=replace(
            e.physical_contact,
            inactive_digits_policy="allow_articulation",
            inactive_digits_evidence={
                "kind": "hypothesis",
                "source": "042 whole-hand search",
                "note": (
                    "Unassigned digits articulate with posture regularization; "
                    "biological coordination unresolved"
                ),
            },
        ),
        solver=replace(e.solver, collision_limit_implementation="displacement"),
    )
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    from .scene import coupled_initial_pose

    initial = coupled_initial_pose(scene.model, e.initial_joints_rad).tolist()
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    batches: list[dict[str, Any]] = []
    beam: list[dict[str, Any]] = [
        {
            "id": "initial-seed",
            "qpos_rad": initial,
            "contacts": [],
            "cost": 0.0,
            "event_index": -1,
            "node_path": [],
            "edge_path": [],
        }
    ]
    solve_count = 0
    for event_index, event in enumerate(passage.events):
        next_beam = []
        for parent_index, parent in enumerate(beam):
            held = [c for c in parent["contacts"] if c["behavior"] == "hold"]
            hypotheses = fingering_hypotheses(
                event,
                settings.fingers,
                tuple(held),
                settings.seed + event_index * 1009 + parent_index,
            )
            if settings.assignment_order == "marker_distance":
                scene.data.qpos[:] = parent["qpos_rad"]
                mujoco.mj_forward(scene.model, scene.data)
                for h in hypotheses:
                    h["priority_marker_distance_sum_m"] = float(
                        sum(
                            np.linalg.norm(
                                scene.data.site(f"{c['finger']}_pad").xpos - point(e, c)
                            )
                            for c in h["contacts"]
                        )
                    )
                hypotheses.sort(key=lambda h: h["priority_marker_distance_sum_m"])
            batch = {
                "assignment_order": settings.assignment_order,
                "priority_claim": (
                    "Marker proximity is an exploration priority, "
                    "never a contact or feasibility certificate"
                ),
                "event_index": event_index,
                "parent": parent["id"],
                "hypotheses": hypotheses,
                "generated": len(hypotheses),
                "attempt_budget": settings.assignments_per_parent,
            }
            batches.append(batch)
            for hypothesis_index, hypothesis in enumerate(
                hypotheses[: settings.assignments_per_parent]
            ):
                contacts = hypothesis["contacts"]
                preparing = []
                preparation_generation = None
                if settings.prepare_next and event_index + 1 < len(passage.events):
                    future = fingering_hypotheses(
                        passage.events[event_index + 1],
                        settings.fingers,
                        tuple(c for c in contacts if c["behavior"] == "hold"),
                        settings.seed + event_index + hypothesis_index,
                    )
                    occupied = {c["finger"] for c in contacts}
                    for future_hypothesis in future:
                        preparing = [
                            c
                            for c in future_hypothesis["contacts"]
                            if c["finger"] not in occupied
                            and c["button_id"] not in {p["button_id"] for p in contacts}
                        ][:1]
                        if preparing:
                            break
                    preparation_generation = {
                        "seed": settings.seed + event_index + hypothesis_index,
                        "generated_assignments": len(future),
                        "selected_hypothesis_contacts": preparing,
                        "status": "optional_control_hypothesis_not_a_future_solve",
                    }
                targets = [point(e, c) for c in contacts] + [
                    point(e, c)
                    + e.geometry.rotation[:, 2] * settings.preparation_height_m
                    for c in preparing
                ]
                solve = solve_targets(
                    scene,
                    e,
                    parent["qpos_rad"],
                    contacts + preparing,
                    targets,
                    [True] * len(contacts) + [False] * len(preparing),
                    settings.contact_iterations,
                )
                solve_count += 1
                preparation_attempt = None
                if preparing and solve["status"] != "success":
                    preparation_attempt = solve
                    preparing = []
                    targets = [point(e, c) for c in contacts]
                    solve = solve_targets(
                        scene,
                        e,
                        parent["qpos_rad"],
                        contacts,
                        targets,
                        [True] * len(contacts),
                        settings.contact_iterations,
                    )
                    solve_count += 1
                node = {
                    "id": f"node-{event_index}-{parent_index}-{hypothesis_index}",
                    "event_index": event_index,
                    "parent": parent["id"],
                    "contacts": contacts,
                    "preparing": preparing,
                    "contact_solve": solve,
                    "optional_preparation_failure": preparation_attempt,
                    "preparation_generation": preparation_generation,
                    "status": "successful_contact_candidate"
                    if solve["status"] == "success"
                    else "failed_contact_solve",
                }
                nodes.append(node)
                hypothesis["status"] = node["status"]
                hypothesis["node_id"] = node["id"]
                if solve["status"] != "success":
                    continue
                q = solve["qpos_rad"]
                edge: dict[str, Any] | None = None
                if event_index:
                    path = plan_contact_change(
                        scene,
                        e,
                        parent["contacts"],
                        contacts,
                        parent["qpos_rad"],
                        q,
                        held,
                        settings.planning,
                    )
                    edge = {
                        "id": f"edge-{node['id']}",
                        "source": parent["id"],
                        "destination": node["id"],
                        "event_index": event_index,
                        "status": path["status"],
                        "path": path,
                    }
                    edges.append(edge)
                    if path["status"] != "sampled_path_found":
                        node["status"] = "failed_transition"
                        hypothesis["status"] = "failed_transition"
                        continue
                    q = path["achieved_qpos_rad"]
                preparation_checks = []
                for c in preparing:
                    scene.data.qpos[:] = q
                    check = diagnostics(
                        scene,
                        point(e, c)
                        + e.geometry.rotation[:, 2] * settings.preparation_height_m,
                        c["button_id"],
                        c["finger"],
                    )
                    preparation_checks.append(check)
                if (
                    edge
                    and preparing
                    and not all(
                        accepted(c, e.solver, False) for c in preparation_checks
                    )
                ):
                    refinement = solve_targets(
                        scene,
                        e,
                        q,
                        contacts + preparing,
                        targets,
                        [True] * len(contacts) + [False] * len(preparing),
                        settings.contact_iterations,
                    )
                    solve_count += 1
                    edge["preparation_solve"] = refinement
                    if refinement["status"] != "success":
                        edge["status"] = node["status"] = (
                            "preparation_transition_failed"
                        )
                        continue
                    bridge = audit_contact_path(
                        scene,
                        e,
                        [q, refinement["qpos_rad"]],
                        contacts,
                        settings.planning,
                    )
                    edge["preparation_bridge"] = bridge
                    if not bridge["sampled_constraints_satisfied"]:
                        edge["status"] = node["status"] = (
                            "preparation_transition_failed"
                        )
                        continue
                    for sample in bridge["samples"][1:]:
                        sample["active_contacts"] = contacts
                        sample["roles"] = {
                            c["finger"]: "required" for c in contacts
                        } | {c["finger"]: "preparing" for c in preparing}
                    edge["path"]["samples"].extend(bridge["samples"][1:])
                    edge["path"]["palm_path_length_m"] += bridge["palm_path_length_m"]
                    q = refinement["qpos_rad"]
                    edge["path"]["achieved_qpos_rad"] = q
                node["preparing_controls"] = [
                    {
                        **c,
                        "target_world_m": (
                            point(e, c)
                            + e.geometry.rotation[:, 2] * settings.preparation_height_m
                        ).tolist(),
                    }
                    for c in preparing
                ]
                scene.data.qpos[:] = q
                ending = contact_check(scene, e, contacts)
                if not ending["satisfied"]:
                    raise ValueError(
                        "Planned endpoint lost its actual musical contacts"
                    )
                node.update(
                    qpos_rad=q,
                    connected_contact_check=ending,
                    status="connected_candidate",
                    cost=parent["cost"]
                    + (edge["path"]["palm_path_length_m"] if edge else 0.0),
                    node_path=parent["node_path"] + [node["id"]],
                    edge_path=parent["edge_path"] + ([edge["id"]] if edge else []),
                )
                next_beam.append(node)
            for hypothesis in hypotheses[settings.assignments_per_parent :]:
                hypothesis["status"] = "unexplored_budget"
        next_beam.sort(key=lambda n: (n["cost"], n["id"]))
        beam = next_beam[: settings.beam_width]
        for node in next_beam[settings.beam_width :]:
            node["status"] = "pruned_beam_cost"
        for node in beam:
            node["status"] = "retained_beam"
        if not beam:
            break
    complete = [n for n in beam if n["event_index"] == len(passage.events) - 1]
    strategies = []
    by_node = {n["id"]: n for n in nodes}
    by_edge = {edge["id"]: edge for edge in edges}
    for index, leaf in enumerate(complete):
        samples: list[dict[str, Any]] = []
        events = [by_node[n] for n in leaf["node_path"]]
        for edge_id in leaf["edge_path"]:
            edge = by_edge[edge_id]
            part = edge["path"]["samples"]
            if (
                not part
                or part[0]["qpos_rad"] != by_node[edge["source"]]["qpos_rad"]
                or part[-1]["qpos_rad"] != by_node[edge["destination"]]["qpos_rad"]
            ):
                raise ValueError("Edge samples do not join actual graph nodes")
            if samples and samples[-1]["qpos_rad"] != part[0]["qpos_rad"]:
                raise ValueError("Hidden jump at a passage event boundary")
            event_start = len(samples) - 1 if samples else 0
            for sample in part if not samples else part[1:]:
                s = {
                    **sample,
                    "event_interval": edge["event_index"] - 1,
                    "event_index": None,
                    "edge_id": edge_id,
                    "active_contacts": sample.get(
                        "active_contacts", edge["path"].get("held_contacts", [])
                    ),
                    "roles": dict(
                        sample.get(
                            "roles",
                            {
                                c["finger"]: "held"
                                for c in edge["path"].get("held_contacts", [])
                            },
                        )
                    ),
                }
                for digit in sample.get("phase", {}).get("moving_fingers", []):
                    s["roles"][digit] = "moving"
                samples.append(s)
            samples[event_start]["event_index"] = by_node[edge["source"]]["event_index"]
            samples[-1]["event_index"] = by_node[edge["destination"]]["event_index"]
            samples[event_start]["active_contacts"] = by_node[edge["source"]][
                "contacts"
            ]
            samples[event_start]["roles"] = {
                c["finger"]: "held" if c["behavior"] == "hold" else "required"
                for c in by_node[edge["source"]]["contacts"]
            }
            samples[-1]["active_contacts"] = by_node[edge["destination"]]["contacts"]
            samples[-1]["roles"] = {
                c["finger"]: "held" if c["behavior"] == "hold" else "required"
                for c in by_node[edge["destination"]]["contacts"]
            }
            for endpoint_index, endpoint in (
                (event_start, by_node[edge["source"]]),
                (len(samples) - 1, by_node[edge["destination"]]),
            ):
                for c in endpoint["preparing"]:
                    samples[endpoint_index]["roles"][c["finger"]] = "preparing"
        strategies.append(
            {
                "id": f"strategy-{index}",
                "node_ids": leaf["node_path"],
                "edge_ids": leaf["edge_path"],
                "events": [
                    {
                        "contacts": n["contacts"],
                        "preparing_controls": n["preparing_controls"],
                        "qpos_rad": n["qpos_rad"],
                    }
                    for n in events
                ],
                "samples": samples,
                "cost_palm_path_m": leaf["cost"],
                "status": "sampled_connected_path"
                if samples
                else "static_contact_only",
                "anatomical_validation": "unresolved",
                "human_feasibility": None,
            }
        )
    return {
        "id": passage.id,
        "resolved_profiles": e.resolved_profiles(),
        "passage": passage.to_dict(),
        "settings": asdict(settings),
        "input": e.expanded_source(),
        "joint_names": names,
        "nodes": nodes,
        "edges": edges,
        "hypothesis_batches": batches,
        "strategies": strategies,
        "status": "complete_passage_found" if complete else "no_complete_passage_found",
        "budget": {
            "contact_solves": solve_count,
            "attempted_movement_edges": len(edges),
            "generated_assignments": sum(b["generated"] for b in batches),
            "movement_waypoint_solves": sum(
                a.get("waypoint_solver_calls", 0)
                for edge in edges
                for a in edge["path"].get("attempts", [])
            ),
            "movement_rrt_iterations": sum(
                a.get("rrt_search", {}).get("iterations", 0)
                for edge in edges
                for a in edge["path"].get("attempts", [])
            ),
            "movement_rrt_collision_evaluations": sum(
                a.get("rrt_search", {}).get("collision_evaluations", 0)
                for edge in edges
                for a in edge["path"].get("attempts", [])
            ),
        },
        "cost_claim": (
            "Bounded beam ranking by discovered palm path; "
            "not optimal or universal difficulty"
        ),
        "trajectory_claim": (
            "Audited interpolation samples of computed waypoints; "
            "no tempo or continuous validity"
        ),
        "initial_seed_claim": (
            "Event 0 contact solved from the seed; "
            "no initial approach trajectory is claimed"
        ),
        **current_execution_metadata(scene.model),
    }
