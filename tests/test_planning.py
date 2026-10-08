import json
from dataclasses import replace
from pathlib import Path

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.planning import (
    PlanningSettings,
    audit_path,
    plan_transition,
)
from accordion_ergonomics_core.scene import build_scene


def test_search_finds_sampled_path_when_direct_interpolation_collides() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    start = json.loads(
        Path("experiments/004-profile-recalculation/result.json").read_text()
    )
    end = json.loads(
        Path("experiments/002-arm-ablation/r1c9-arm-enabled/result.json").read_text()
    )
    scene = build_scene(e.geometry)
    settings = PlanningSettings(withdrawal_depths_m=(0.02,))
    direct = audit_path(scene, [start["qpos_rad"], end["qpos_rad"]], e, settings)
    assert not direct["sampled_constraints_satisfied"]
    assert direct["maximum_penetration_m"] > 0.01
    result = plan_transition(
        scene, e, start["qpos_rad"], end["qpos_rad"], "r1c9", settings
    )
    assert result["status"] == "sampled_path_found"
    assert result["continuous_validity"] is None
    assert result["physical_feasibility"] is None
    assert result["maximum_penetration_m"] <= e.solver.penetration_tolerance_m
    finer = audit_path(
        scene,
        result["waypoints_qpos_rad"],
        e,
        replace(settings, max_joint_step_rad=0.001),
    )
    assert finer["sampled_constraints_satisfied"]
