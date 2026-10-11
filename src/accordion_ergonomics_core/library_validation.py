"""Reproduce selected media through the consumer API and compare actual evidence."""

import hashlib
import json
import os
from pathlib import Path

from .digits import DIGITS
from .experiment import Experiment
from .provenance import current_execution_metadata
from .research import ExerciseLibrary
from .scene import build_scene
from .verification import verify_record


def run_library_validation(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    root = (definition.parent / source["catalog_result"]).resolve().parent.parent
    library = ExerciseLibrary(root)
    library.evidence_path(
        {"path": "targets/manifest.json", "sha256": source["catalog_sha256"]}
    )
    checked = []
    for target_id in source["inspect_targets"]:
        media, _ = library.media_record(target_id)
        strategies = []
        for report in media["strategy_reports"]:
            if report["animation"] is None:
                continue
            strategy_id = report["strategy_id"]
            frames = library.frame_sequence(target_id, strategy_id)
            audit = library.diagnostics(target_id, strategy_id)
            strategies.append(
                {
                    "strategy_id": strategy_id,
                    "frame_sample_indices": [f["sample_index"] for f in frames],
                    "frame_hashes": [f["frame_sha256"] for f in frames],
                    "state_sequence_sha256": audit["state_sequence_sha256"],
                    "sample_count": len(audit["samples"]),
                    "anatomical_validation": audit["anatomical_validation"],
                }
            )
        checked.append({"target_id": target_id, "strategies": strategies})
    target_id = source["replay_target"]
    replay = (definition.parent / source["replay_output"]).resolve()
    library.reproduce(target_id, replay)
    verification = verify_record(replay)
    if verification.status != "verified":
        raise ValueError("Archived replay integrity failed: " + str(verification))
    original, reference = library.media_record(target_id)
    regenerated = json.loads((replay / "result.json").read_text())
    artifacts = []
    for path, expected in original["artifact_sha256"].items():
        actual = hashlib.sha256((replay / path).read_bytes()).hexdigest()
        artifacts.append(
            {
                "path": path,
                "original_sha256": expected,
                "replay_sha256": actual,
                "byte_identical": expected == actual,
            }
        )
    # Record discrepancies rather than asserting that runtime rasterization is portable.
    comparisons = {
        key: original[key] == regenerated[key]
        for key in (
            "provenance",
            "strategy_reports",
            "strategy_comparison",
            "failed_contact_state",
            "search_source_provenance",
        )
    }
    saved = library.search_record(target_id)
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    result = {
        "id": "library-validation-044",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "checked_targets": checked,
        "replayed_media_reference": reference,
        "replay_execution": json.loads((replay / "execution.json").read_text()),
        "replay_integrity_status": verification.status,
        "record_comparisons": comparisons,
        "replayed_artifacts": artifacts,
        "claim": (
            "Consumer retrieval and actual archived-render replay; "
            "no new anatomical validation"
        ),
        **current_execution_metadata(scene.model),
    }
    output.mkdir(parents=True, exist_ok=True)
    execution_path = output / "execution.json"
    if execution_path.exists():
        execution = json.loads(execution_path.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        execution_path.write_text(json.dumps(execution, indent=2) + "\n")
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
