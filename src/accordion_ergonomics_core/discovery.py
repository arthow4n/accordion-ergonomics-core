"""Bounded autonomous evaluation and observed-result exploration allocation."""

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from html import escape
from pathlib import Path
from typing import Any

import numpy as np

from .digits import DIGITS
from .experiment import Experiment
from .generation import GenerationSettings, generate_challenges
from .movement_evidence import validate_strategy
from .passage_experiment import trim_iterations
from .passage_media import independent_samples
from .passage_search import PassageSearchSettings, search_passage
from .passages import NoteEvent, Passage
from .planning import PlanningSettings
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene


@dataclass(frozen=True)
class DiscoverySettings:
    initial_evaluations: int = 7
    adaptive_evaluations: int = 2
    retained_count: int = 5
    contact_iterations: int = 120
    assignments_per_parent: int = 2
    waypoint_iterations: int = 100
    waypoint_solve_limit: int = 24
    rrt_iterations: int = 60
    seed: int = 4302

    def __post_init__(self):
        if any(type(v) is not int or v < 0 for v in asdict(self).values()):
            raise ValueError("Discovery budgets must be nonnegative integers")
        if (
            min(
                self.initial_evaluations,
                self.retained_count,
                self.contact_iterations,
                self.assignments_per_parent,
                self.waypoint_iterations,
                self.waypoint_solve_limit,
            )
            < 1
        ):
            raise ValueError("Evaluation and numerical limits must be positive")


def observed_summary(search: dict[str, Any], reports: list[dict[str, Any]]):
    connected = [n for n in search["nodes"] if "qpos_rad" in n]
    summary: dict[str, Any] = {
        "status": search["status"],
        "completed_strategies": len(search["strategies"]),
        "deepest_connected_event_count": max(
            (n["event_index"] + 1 for n in connected), default=0
        ),
        "sampled_proxy_accepted_strategies": sum(
            r["status"] == "sampled_proxy_constraints_satisfied" for r in reports
        ),
        "attempted_contact_candidates": len(search["nodes"]),
        "failed_contact_solves": sum(
            n["contact_solve"]["status"] != "success" for n in search["nodes"]
        ),
        "failed_movement_edges": sum(
            e["status"] != "sampled_path_found" for e in search["edges"]
        ),
        "budget": search["budget"],
        "strategies": [],
    }
    for strategy, audit in zip(search["strategies"], reports, strict=True):
        q = np.array([s["qpos_rad"] for s in strategy["samples"]])
        fingers = sorted(
            {c["finger"] for e in strategy["events"] for c in e["contacts"]}
        )
        summary["strategies"].append(
            {
                "id": strategy["id"],
                "played_digits": fingers,
                "palm_path_length_m": strategy["cost_palm_path_m"],
                "sample_count": len(q),
                "joint_excursions_rad": dict(
                    zip(search["joint_names"], np.ptp(q, axis=0).tolist(), strict=True)
                ),
                "minimum_imported_joint_margin_rad": min(
                    s["joint_margin_min_rad"] for s in strategy["samples"]
                ),
                "worst_cross_digit_proxy_m": audit["worst_cross_digit"]["distance_m"],
                "independent_status": audit["status"],
            }
        )
    return summary


def adaptive_choices(evaluations: list[dict[str, Any]], budget: int):
    """Exploration rationale refers only to observed finite-search outcomes."""
    successful = [
        e for e in evaluations if e["observed"]["sampled_proxy_accepted_strategies"]
    ]
    partial = [
        e
        for e in evaluations
        if not e["observed"]["completed_strategies"]
        and e["observed"]["deepest_connected_event_count"]
    ]
    successful.sort(
        key=lambda e: (-len(e["observed"]["strategies"][0]["played_digits"]), e["id"])
    )
    partial.sort(
        key=lambda e: (-e["observed"]["deepest_connected_event_count"], e["id"])
    )
    choices = []
    # First seek alternate connected strategies; next recover a connected prefix.
    pools = (
        (
            successful,
            (
                "Explore alternate finger/button assignments "
                "after an audited connected discovery"
            ),
        ),
        (
            partial,
            (
                "Increase finite exploration after an observed "
                "connected prefix failed to complete"
            ),
        ),
    )
    used = set()
    for pool, reason in pools:
        if len(choices) >= budget:
            break
        if pool:
            e = pool[0]
            choices.append(
                {
                    "candidate_id": e["candidate_id"],
                    "parent_evaluation": e["id"],
                    "reason": reason,
                    "observed": e["observed"],
                }
            )
            used.add(e["candidate_id"])
    for e in successful + partial:
        if len(choices) >= budget:
            break
        if e["candidate_id"] not in used:
            choices.append(
                {
                    "candidate_id": e["candidate_id"],
                    "parent_evaluation": e["id"],
                    "reason": (
                        "Additional exploration of an observed "
                        "discovery or connected prefix"
                    ),
                    "observed": e["observed"],
                }
            )
            used.add(e["candidate_id"])
    return choices


def selection(
    evaluations: list[dict[str, Any]], candidates: list[dict[str, Any]], count: int
):
    by_candidate: dict[str, list[dict[str, Any]]] = {}
    for e in evaluations:
        by_candidate.setdefault(e["candidate_id"], []).append(e)
    selected = []
    families = set()
    problem_exists = any(
        not e["observed"]["sampled_proxy_accepted_strategies"] for e in evaluations
    )
    success_slots = count - int(problem_exists)
    # Prefer one audited discovery per generated family, then a meaningful failure.
    for candidate in candidates:
        trials = by_candidate.get(candidate["id"], [])
        passing = [
            e for e in trials if e["observed"]["sampled_proxy_accepted_strategies"]
        ]
        if (
            passing
            and candidate["family"] not in families
            and len(selected) < success_slots
        ):
            best = max(
                passing,
                key=lambda e: (
                    e["observed"]["sampled_proxy_accepted_strategies"],
                    e["id"],
                ),
            )
            selected.append(
                {
                    "candidate_id": candidate["id"],
                    "family": candidate["family"],
                    "evaluation_id": best["id"],
                    "reason": (
                        "Distinct generated musical family with an independently "
                        "sampled model path; anatomy unresolved"
                    ),
                }
            )
            families.add(candidate["family"])
    failed = [
        e for e in evaluations if not e["observed"]["sampled_proxy_accepted_strategies"]
    ]
    failed.sort(
        key=lambda e: (-e["observed"]["deepest_connected_event_count"], e["id"])
    )
    for e in failed:
        if len(selected) >= count:
            break
        if e["candidate_id"] not in {s["candidate_id"] for s in selected}:
            selected.append(
                {
                    "candidate_id": e["candidate_id"],
                    "family": e["family"],
                    "evaluation_id": e["id"],
                    "reason": (
                        "Preserve an evaluated unsuccessful or proxy-rejected "
                        "hypothesis; no impossibility claim"
                    ),
                }
            )
    return selected


def discovery_diagram(record: dict[str, Any], output: Path):
    evaluations = record["evaluations"]
    height = 185 + len(evaluations) * 48
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1150" height="{height}">',
        '<rect width="100%" height="100%" fill="#142030"/>',
        '<g fill="#eef3f8" font-family="monospace">',
        '<text x="20" y="30" font-size="17">Actual generated hypotheses → '
        "bounded numerical trials → retained evidence</text>",
        '<text x="20" y="58" font-size="13">'
        f"{len(record['generation']['candidates'])} unique musical hypotheses; "
        f"{len(evaluations)} evaluated trials; "
        f"{len(record['selected'])} retained targets</text>",
        '<text x="20" y="80" font-size="12">Green sampled proxy path | '
        "amber finite failure | * observed-result follow-up; anatomy unresolved</text>",
    ]
    possibilities = sum(
        sum(c["unconditioned_assignment_counts"])
        for c in record["generation"]["candidates"]
    )
    budget = record["total_budget_used"]
    parts.append(
        '<text x="20" y="101" font-size="11">'
        f"{possibilities} unconditioned event assignment possibilities; "
        f"beam generated {budget['generated_assignments']}; "
        f"contact calls {budget['contact_solves']}</text>"
    )
    selected_ids = {s["evaluation_id"] for s in record["selected"]}
    for i, e in enumerate(evaluations):
        y = 133 + i * 48
        obs = e["observed"]
        color = "#267866" if obs["sampled_proxy_accepted_strategies"] else "#985d35"
        label = (
            f"{e['id']} {'*' if e['stage'] == 'adaptive' else ' '} "
            f"{e['family']} | {e['candidate_id']}"
        )
        details = (
            f"contact calls {obs['budget']['contact_solves']}; "
            f"edges {obs['budget']['attempted_movement_edges']}; "
            f"sampled paths {obs['sampled_proxy_accepted_strategies']}; "
            f"prefix {obs['deepest_connected_event_count']}"
        )
        parts += [
            f'<rect x="20" y="{y}" width="1110" height="40" fill="{color}"/>',
            f'<text x="28" y="{y + 15}" font-size="12">{escape(label)} '
            f"{'RETAINED' if e['id'] in selected_ids else ''}</text>",
            f'<text x="28" y="{y + 31}" font-size="11">{escape(details)}</text>',
        ]
    parts += [
        f'<text x="20" y="{height - 18}" font-size="11">Unselected or '
        "unevaluated hypotheses were not proved impossible. Selection is "
        "diversity/evidence coverage, not a difficulty score.</text>",
        "</g></svg>",
    ]
    output.write_text("\n".join(parts) + "\n")


def discover_challenges(
    reference: Experiment,
    output: Path,
    generation: GenerationSettings | None = None,
    settings: DiscoverySettings | None = None,
):
    generation = generation or GenerationSettings()
    settings = settings or DiscoverySettings()
    generated = generate_challenges(generation)
    output.mkdir(parents=True, exist_ok=True)
    candidates = generated["candidates"]
    by_id = {c["id"]: c for c in candidates}
    evaluations: list[dict[str, Any]] = []
    scene = None

    def evaluate(candidate, stage, rationale):
        nonlocal scene
        index = len(evaluations)
        adaptive = stage == "adaptive"
        options = PassageSearchSettings(
            seed=settings.seed + index,
            beam_width=2 if adaptive else 1,
            assignments_per_parent=settings.assignments_per_parent
            * (2 if adaptive else 1),
            contact_iterations=settings.contact_iterations * (2 if adaptive else 1),
            prepare_next=False,
            assignment_order="seeded" if adaptive else "marker_distance",
            planning=PlanningSettings(
                withdrawal_depths_m=(0.01, 0.02) if adaptive else (0.01,),
                max_joint_step_rad=0.003,
                waypoint_iterations=settings.waypoint_iterations
                * (2 if adaptive else 1),
                waypoint_solve_limit=settings.waypoint_solve_limit
                * (2 if adaptive else 1),
                rrt_iterations=settings.rrt_iterations * (2 if adaptive else 1),
                seed=settings.seed + index,
            ),
        )
        p = candidate["passage"]
        passage = Passage(
            p["id"], tuple(NoteEvent(**e) for e in p["events"]), p["provenance"]
        )
        search = search_passage(passage, reference, options)
        search["scene_input"] = search.pop("input")
        e = Experiment.from_dict(search["scene_input"])
        if scene is None:
            scene = build_scene(
                e.geometry, e.player, e.setup, e.physical_contact, DIGITS
            )
        if (
            compiled_model_digest(scene.model)
            != search["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError("Discovery independent audit uses a different model")
        audits = []
        for strategy in search["strategies"]:
            validate_strategy(search, strategy)
            audits.append(
                independent_samples(
                    scene, strategy["samples"], e.solver.penetration_tolerance_m
                )
            )
        search["independent_strategy_audits"] = audits
        observed = observed_summary(search, audits)
        trim_iterations(search)
        file = f"evaluation-{index:02}.json"
        data = (
            json.dumps(search, separators=(",", ":"), allow_nan=False) + "\n"
        ).encode()
        (output / file).write_bytes(data)
        entry = {
            "id": f"evaluation-{index:02}",
            "candidate_id": candidate["id"],
            "family": candidate["family"],
            "stage": stage,
            "rationale": rationale,
            "settings": asdict(options),
            "search_result": file,
            "search_sha256": hashlib.sha256(data).hexdigest(),
            "observed": observed,
        }
        evaluations.append(entry)
        print(
            json.dumps(
                {
                    "evaluation": entry["id"],
                    "family": entry["family"],
                    "status": observed["status"],
                    "sampled_proxy_paths": observed[
                        "sampled_proxy_accepted_strategies"
                    ],
                }
            ),
            flush=True,
        )

    for candidate in candidates[: settings.initial_evaluations]:
        evaluate(
            candidate,
            "initial",
            "Balanced generated-family prefix, no prior numerical outcome assumed",
        )
    decisions = adaptive_choices(evaluations, settings.adaptive_evaluations)
    for decision in decisions:
        evaluate(by_id[decision["candidate_id"]], "adaptive", decision)
    if scene is None:
        raise ValueError("Discovery produced no evaluated model")
    retained = selection(evaluations, candidates, settings.retained_count)
    result = {
        "id": "autonomous-challenge-discovery",
        "generation": generated,
        "settings": asdict(settings),
        "evaluations": evaluations,
        "allocation_decisions": decisions,
        "selected": retained,
        "unevaluated_candidate_ids": [
            c["id"]
            for c in candidates
            if c["id"] not in {e["candidate_id"] for e in evaluations}
        ],
        "total_budget_used": {
            key: sum(e["observed"]["budget"].get(key, 0) for e in evaluations)
            for key in evaluations[0]["observed"]["budget"]
        },
        "claim": (
            "Autonomous finite musical/model exploration; no global reachability, "
            "anatomical validity, optimum, tempo or difficulty claim"
        ),
        **current_execution_metadata(scene.model),
    }
    discovery_diagram(result, output / "discovery.svg")
    result["artifact_sha256"] = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(output.iterdir())
        if p.suffix in (".svg", ".json")
        and p.name.startswith(("evaluation-", "discovery"))
    }
    return result


def run_discovery(definition: Path, output: Path):
    from .exploration import read_hashed

    raw = definition.read_bytes()
    source = json.loads(raw)
    baseline = read_hashed(
        definition.parent / source["baseline_result"], source["baseline_sha256"]
    )
    reference = replace(
        Experiment.from_dict(baseline["input"]),
        initial_joints_rad=dict(
            zip(baseline["joint_names"], baseline["qpos_rad"], strict=True)
        ),
    )
    result = discover_challenges(
        reference,
        output,
        GenerationSettings(**source.get("generation", {})),
        DiscoverySettings(**source.get("discovery", {})),
    )
    result["input"] = source
    result["definition_sha256"] = hashlib.sha256(raw).hexdigest()
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    return result
