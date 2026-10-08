"""Recompute the same physical queries across explicit parameter replacements."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .exploration import read_hashed
from .reachability import merge_parameters, run_atlas


def compare_atlases(reference: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    if (
        reference.get("status") == "no_anchor_solution"
        or other.get("status") == "no_anchor_solution"
    ):
        return {
            "status": "comparison_unavailable",
            "changes": [],
            "status_changes": None,
            "maximum_common_relocation_change_m": None,
            "interpretation": "No source contact found; comparison unavailable",
        }
    baseline = {a["button_id"]: a for a in reference["actions"]}
    changes: list[dict[str, Any]] = []
    for action in other["actions"]:
        old = baseline[action["button_id"]]
        a, b = (
            old["best_discovered_relocation_m"],
            action["best_discovered_relocation_m"],
        )
        changes.append(
            {
                "button_id": action["button_id"],
                "reference_status": old["status"],
                "status": action["status"],
                "status_changed": old["status"] != action["status"],
                "relocation_difference_m": None if a is None or b is None else b - a,
            }
        )
    return {
        "changes": changes,
        "status_changes": sum(c["status_changed"] for c in changes),
        "maximum_common_relocation_change_m": max(
            [
                abs(c["relocation_difference_m"])
                for c in changes
                if c["relocation_difference_m"] is not None
            ]
            + [0.0]
        ),
        "interpretation": "Finite-search sensitivity; human boundaries unknown",
    }


def run_sensitivity(definition: Path, output: Path) -> dict[str, Any]:
    raw_definition = definition.read_bytes()
    source = json.loads(raw_definition)
    prototype = read_hashed(
        definition.parent / source["atlas_definition"],
        source["atlas_definition_sha256"],
    )
    baseline = (definition.parent / source["atlas_definition"]).parent / prototype[
        "baseline_result"
    ]
    output.mkdir(parents=True, exist_ok=True)
    records = []
    reference = None
    for case in source["cases"]:
        case_dir = output / case["id"]
        case_dir.mkdir(exist_ok=True)
        config = dict(prototype)
        config["baseline_result"] = os.path.relpath(
            baseline.resolve(), case_dir.resolve()
        )
        config["id"] = source["id"] + "-" + case["id"]
        config["targets"] = source["targets"]
        config["parameter_patch"] = (
            merge_parameters(prototype.get("parameter_patch", {}), case["patch"])
            if prototype.get("parameter_patch")
            else case["patch"]
        )
        path = case_dir / "experiment.json"
        path.write_text(json.dumps(config, indent=2) + "\n")
        result = run_atlas(path, case_dir)
        if reference is None:
            reference = result
        records.append(
            {
                "case": case,
                "summary": result.get("summary"),
                "status": result["status"],
                "profile_sha256": result["anchor"]["profiles_sha256"],
                "anchor_qpos_rad": result["anchor"]["qpos_rad"],
                "elapsed_s": result["elapsed_s"],
                "comparison": compare_atlases(reference, result),
                "result": str(Path(case["id"]) / "result.json"),
                "result_sha256": hashlib.sha256(
                    (case_dir / "result.json").read_bytes()
                ).hexdigest(),
            }
        )
    report = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw_definition).hexdigest(),
        "cases": records,
        "anchor_policy": "Recalibrate source contact from same prior per profile",
        "claim": "Synthetic local-search sensitivity, not calibrated human ergonomics",
    }
    (output / "result.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    return report
