from pathlib import Path

from accordion_ergonomics_core.transition import run_transition


def test_valid_endpoints_can_have_an_invalid_intermediate_path(tmp_path: Path) -> None:
    result = run_transition(
        Path("experiments/003-transition-counterexample/experiment.json"),
        tmp_path,
        render=False,
    )
    assert result["endpoint_statuses"] == ["success", "success"]
    assert result["samples"][0]["violations"] == []
    assert result["samples"][-1]["violations"] == []
    assert result["candidate_valid"] is False
    assert result["global_transition_feasible"] is None
    assert result["maximum_detected_penetration_m"] > 0.01
    assert all(s["joint_max_violation_rad"] < 1e-6 for s in result["samples"])
    assert all(s["equality_max_residual_rad"] < 1e-6 for s in result["samples"])
    worst = result["samples"][result["worst_sample_index"]]
    assert any(
        c["geom2"] == "keyboard_panel" and c["distance_m"] < -0.01
        for c in worst["contacts"]
    )
