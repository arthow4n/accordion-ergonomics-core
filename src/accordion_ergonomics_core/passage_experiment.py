"""Frozen numerical passage experiments with explicit finite budgets."""

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

from .experiment import Experiment
from .exploration import read_hashed
from .passage_search import PassageSearchSettings, search_passage
from .passages import NoteEvent, Passage
from .planning import PlanningSettings


def trim_iterations(value: Any) -> None:
    """Retain numerical outcome and exact rerunnable inputs without redundant traces.

    Solver diagnostics are not playing trajectories. All actual path states,
    failed endpoint states, budgets and termination reasons remain present.
    """
    if isinstance(value, dict):
        if "solver_history" in value:
            history = value.pop("solver_history")
            value["iteration_trace_summary"] = {
                "diagnostic_iterations": len(history),
                "accepted_integrations": sum(
                    "integration_step" in step for step in history
                ),
                "semantics": "Numerical solver trace; never a movement trajectory",
            }
        for child in value.values():
            trim_iterations(child)
    elif isinstance(value, list):
        for child in value:
            trim_iterations(child)


def run_passage(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    baseline = read_hashed(
        definition.parent / source["baseline_result"], source["baseline_sha256"]
    )
    e = Experiment.from_dict(baseline["input"])
    e = replace(
        e,
        initial_joints_rad=dict(
            zip(baseline["joint_names"], baseline["qpos_rad"], strict=True)
        ),
    )
    musical = source["passage"]
    passage = Passage(
        musical["id"],
        tuple(NoteEvent(**event) for event in musical["events"]),
        musical.get("provenance", "curated_research_demonstration"),
    )
    options = dict(source.get("search", {}))
    if "fingers" in options:
        options["fingers"] = tuple(options["fingers"])
    if "planning" in options:
        planning = dict(options["planning"])
        if "withdrawal_depths_m" in planning:
            planning["withdrawal_depths_m"] = tuple(planning["withdrawal_depths_m"])
        options["planning"] = PlanningSettings(**planning)
    result = search_passage(passage, e, PassageSearchSettings(**options))
    result["scene_input"] = result.pop("input")
    result["input"] = source
    result["definition_sha256"] = hashlib.sha256(raw).hexdigest()
    trim_iterations(result)
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    return result
