"""Recorded warm-start panels and bounded branch/search sensitivity summaries.

These descriptors measure finite numerical coverage, never human difficulty or
lower bounds on required movement. Existing exploration remains the solver.
"""

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from .exploration import read_hashed


def state_id(names: list[str], qpos: list[float], world: str) -> str:
    """Content identity independent of candidate enumeration and wall time."""
    raw = json.dumps(
        {"joint_names": names, "qpos_rad": qpos, "world": world},
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode()
    return "state-" + hashlib.sha256(raw).hexdigest()[:20]


def warm_start_offset(
    baseline: dict[str, Any], warm: dict[str, Any]
) -> dict[str, float]:
    """Convert exact-world recorded state to the exploration offset interface."""
    if baseline["joint_names"] != warm["joint_names"]:
        raise ValueError("Warm-start coordinate order differs")
    for key in ("profiles_sha256",):
        if baseline[key] != warm[key]:
            raise ValueError("Warm-start reference profiles differ")
    if (
        baseline["provenance"]["compiled_model_sha256"]
        != warm["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Warm-start compiled world differs")
    if warm["status"] != "success":
        raise ValueError("Warm-start evidence must be an accepted contact state")
    return {
        name: float(b - a)
        for name, a, b in zip(
            baseline["joint_names"], baseline["qpos_rad"], warm["qpos_rad"], strict=True
        )
        if b != a
    }


def write_search_panels(definition: Path, output: Path) -> list[Path]:
    """Generate ordinary explore inputs with explicit hashed warm provenance.

    Each panel retains the unperturbed start. The specification's offsets and
    warm records together must match the explicitly declared attempts budget.
    """
    source = json.loads(definition.read_text())
    baseline_path = (definition.parent / source["baseline_result"]).resolve()
    baseline = read_hashed(baseline_path, source["baseline_sha256"])
    paths = []
    for panel in source["panels"]:
        offsets = list(panel["offsets_rad"])
        for reference in panel.get("warm_states", []):
            warm = read_hashed(
                definition.parent / reference["result"], reference["sha256"]
            )
            offsets.append(warm_start_offset(baseline, warm))
        if len(offsets) + 1 != source["attempts_per_target"]:
            raise ValueError("Panels must have matched recorded starts budgets")
        directory = output / panel["id"]
        directory.mkdir(parents=True, exist_ok=True)
        result = {
            "id": source["id"] + "-" + panel["id"],
            "baseline_result": str(baseline_path),
            "baseline_sha256": source["baseline_sha256"],
            "candidate_search": {**source["candidate_search"], "offsets_rad": offsets},
            "targets": source["targets"],
            "search_panel_provenance": {
                "definition": str(definition.resolve()),
                "definition_sha256": hashlib.sha256(
                    definition.read_bytes()
                ).hexdigest(),
                "warm_states": panel.get("warm_states", []),
                "interpretation": "Finite deterministic starts; no feasibility bound",
            },
        }
        path = directory / "experiment.json"
        path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        paths.append(path)
    return paths


def summarize_discovery(record: dict[str, Any]) -> dict[str, Any]:
    """Expose failures, branch diversity, and ordered budget-prefix sensitivity."""
    attempts = record["attempts"]
    candidates = record["candidates"]
    points = np.asarray(
        [c["descriptors"]["palm_position_world_m"] for c in candidates], dtype=float
    )
    diameter = (
        float(np.linalg.norm(points[:, None] - points[None, :], axis=-1).max())
        if len(points)
        else None
    )
    prefixes = []
    for budget in sorted({1, min(4, len(attempts)), len(attempts)}):
        subset = attempts[:budget]
        prefixes.append(
            {
                "starts": budget,
                "accepted_attempts": sum(a["status"] == "success" for a in subset),
                "distinct_candidates": sum("candidate_index" in a for a in subset),
            }
        )
    world = record["provenance"]["compiled_model_sha256"]
    return {
        "target_id": record["target_id"],
        "status_counts": dict(sorted(Counter(a["status"] for a in attempts).items())),
        "failure_reasons": dict(
            sorted(
                Counter(
                    a.get("termination_reason", a.get("reason", "unspecified"))
                    for a in attempts
                    if a["status"] != "success"
                ).items()
            )
        ),
        "distinct_candidates": len(candidates),
        "candidate_state_ids": [
            state_id(
                list(c["state"]["joint_names"]),
                list(c["state"]["joint_angles_rad"]),
                world,
            )
            for c in candidates
        ],
        "palm_candidate_diameter_m": diameter,
        "budget_prefixes": prefixes,
        "max_solver_iterations_per_start": record["settings"]["max_iterations"],
        "human_feasibility": None,
        "interpretation": (
            "Observed branches and search budgets, not intrinsic difficulty"
        ),
    }


def summarize_panels(paths: list[Path], output: Path) -> dict[str, Any]:
    panels = []
    for path in paths:
        raw = path.read_bytes()
        result = json.loads(raw)
        panels.append(
            {
                "id": result["id"],
                "result": str(path.relative_to(output.parent)),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "targets": [summarize_discovery(t) for t in result["targets"]],
            }
        )
    summary = {"schema_version": 1, "panels": panels, "human_feasibility": None}
    output.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    return summary


def run_search_reliability(
    definition: Path, output: Path, render: bool = True
) -> dict[str, Any]:
    """Run matched ordinary exploration panels in this already frozen process."""
    from .exploration import run_exploration

    paths = write_search_panels(definition, output)
    for path in paths:
        run_exploration(path, path.parent, render)
    result = summarize_panels(
        [path.parent / "result.json" for path in paths], output / "result.json"
    )
    result.update(
        id=json.loads(definition.read_text())["id"],
        input=json.loads(definition.read_text()),
        definition_sha256=hashlib.sha256(definition.read_bytes()).hexdigest(),
        artifact_sha256={
            str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(output.rglob("*"))
            if path.is_file() and path != output / "result.json"
        },
    )
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
