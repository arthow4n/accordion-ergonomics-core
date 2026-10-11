import json
from copy import deepcopy
from pathlib import Path

import pytest

from accordion_ergonomics_core.search_reliability import (
    state_id,
    summarize_discovery,
    warm_start_offset,
    write_search_panels,
)

ROOT = Path("experiments/037-upper-anchor-regression")


def test_warm_offsets_preserve_recorded_state_and_reject_other_world() -> None:
    baseline = json.loads((ROOT / "central/result.json").read_text())
    warm = json.loads((ROOT / "explore/single-c4/candidate-2/result.json").read_text())
    offset = warm_start_offset(baseline, warm)
    reconstructed = [
        a + offset.get(n, 0)
        for n, a in zip(baseline["joint_names"], baseline["qpos_rad"], strict=True)
    ]
    assert reconstructed == pytest.approx(warm["qpos_rad"], abs=1e-15)
    incompatible = deepcopy(warm)
    incompatible["provenance"]["compiled_model_sha256"] = "different"
    with pytest.raises(ValueError, match="compiled world"):
        warm_start_offset(baseline, incompatible)
    incompatible = deepcopy(warm)
    incompatible["status"] = "failure"
    with pytest.raises(ValueError, match="accepted contact"):
        warm_start_offset(baseline, incompatible)


def test_search_summary_distinguishes_failure_duplicate_and_unknown_feasibility() -> (
    None
):
    record = json.loads((ROOT / "explore/single-c4/discovery.json").read_text())
    summary = summarize_discovery(record)
    assert summary["status_counts"] == {
        "failed": 2,
        "invalid_initialization": 1,
        "success": 5,
    }
    assert summary["distinct_candidates"] == 3
    assert summary["budget_prefixes"][-1]["accepted_attempts"] == 5
    assert summary["human_feasibility"] is None
    assert summary["palm_candidate_diameter_m"] == pytest.approx(0.115846, abs=1e-6)
    record["candidates"].reverse()
    assert set(summary["candidate_state_ids"]) == set(
        summarize_discovery(record)["candidate_state_ids"]
    )
    empty = {**record, "candidates": []}
    assert summarize_discovery(empty)["palm_candidate_diameter_m"] is None


def test_panel_generation_is_deterministic_and_budget_is_explicit(
    tmp_path: Path,
) -> None:
    definition = Path("experiments/039-search-reliability/experiment.json")
    paths = write_search_panels(definition, tmp_path)
    before = [p.read_bytes() for p in paths]
    write_search_panels(definition, tmp_path)
    assert before == [p.read_bytes() for p in paths]
    for path in paths:
        panel = json.loads(path.read_text())
        assert len(panel["candidate_search"]["offsets_rad"]) + 1 == 8
        assert panel["candidate_search"]["max_iterations"] == 220
    bad = json.loads(definition.read_text())
    bad["baseline_result"] = str((definition.parent / bad["baseline_result"]).resolve())
    bad["attempts_per_target"] = 7
    altered = tmp_path / "bad.json"
    altered.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="matched recorded starts"):
        write_search_panels(altered, tmp_path / "bad")


def test_state_identity_depends_on_world_and_pose() -> None:
    first = state_id(["x"], [0.0], "world-a")
    assert first == state_id(["x"], [0.0], "world-a")
    assert first != state_id(["x"], [0.0], "world-b")
    assert first != state_id(["x"], [0.1], "world-a")


def test_recorded_warm_branch_replays_contact_in_current_reference() -> None:
    from accordion_ergonomics_core.candidates import (
        CandidateSettings,
        discover_candidates,
    )
    from accordion_ergonomics_core.experiment import Experiment
    from accordion_ergonomics_core.scene import build_scene

    warm = json.loads((ROOT / "explore/single-c4/candidate-2/result.json").read_text())
    experiment = Experiment.from_dict(warm["input"])
    scene = build_scene(
        experiment.geometry,
        experiment.player,
        experiment.setup,
        experiment.physical_contact,
    )
    result = discover_candidates(
        scene,
        experiment,
        warm["qpos_rad"],
        warm["profiles_sha256"],
        CandidateSettings((), max_iterations=5),
    )
    assert result["status"] == "candidates_found"
    assert result["attempts"][0]["status"] == "success"
    assert result["attempts"][0]["diagnostics"]["max_penetration_m"] <= 0.0001
    assert result["physical_feasibility"] is None
