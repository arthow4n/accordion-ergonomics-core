from dataclasses import replace
from pathlib import Path

import pytest

from accordion_ergonomics_core.candidates import CandidateSettings
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.domain import PlayingState
from accordion_ergonomics_core.planning import PlanningSettings
from accordion_ergonomics_core.reachability import merge_parameters, reachable_actions
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.sensitivity import compare_atlases


def test_queries_reject_states_from_another_parameter_world(tmp_path: Path) -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    scene = build_scene(e.geometry)
    state = PlayingState(
        tuple(scene.model.joint(i).name for i in range(scene.model.njnt)),
        tuple(scene.model.qpos0),
        "wrong-profile",
        (),
    )
    with pytest.raises(ValueError, match="profile differs"):
        reachable_actions(
            state, scene, e, (), CandidateSettings(()), PlanningSettings(), tmp_path
        )
    with pytest.raises(ValueError, match="finite"):
        replace(state, joint_angles_rad=(float("nan"),) * len(state.joint_names))


def test_parameter_patch_rejects_typos_but_allows_named_range_overrides() -> None:
    with pytest.raises(ValueError, match="Unknown parameter"):
        merge_parameters(
            {"geometry": {"column_spacing_m": 0.019}},
            {"geometry": {"colum_spacing_m": 0.017}},
        )
    assert merge_parameters(
        {"player": {"joint_ranges_rad": {}}},
        {"player": {"joint_ranges_rad": {"flexion_r": [-0.4, 0.4]}}},
    )["player"]["joint_ranges_rad"]["flexion_r"] == [-0.4, 0.4]


def test_sensitivity_distinguishes_search_change_from_quantitative_change() -> None:
    a = {
        "actions": [
            {
                "button_id": "r1c5",
                "status": "sampled_transition_found",
                "best_discovered_relocation_m": 0.02,
            },
            {
                "button_id": "r1c6",
                "status": "no_pose_found",
                "best_discovered_relocation_m": None,
            },
        ]
    }
    b = {
        "actions": [
            {
                "button_id": "r1c5",
                "status": "sampled_transition_found",
                "best_discovered_relocation_m": 0.035,
            },
            {
                "button_id": "r1c6",
                "status": "sampled_transition_found",
                "best_discovered_relocation_m": 0.01,
            },
        ]
    }
    c = compare_atlases(a, b)
    assert c["status_changes"] == 1
    assert c["maximum_common_relocation_change_m"] == pytest.approx(0.015)
    assert c["changes"][1]["relocation_difference_m"] is None


def test_query_rejects_wrong_declared_contact_before_search(tmp_path: Path) -> None:
    import hashlib
    import json

    from accordion_ergonomics_core.domain import ContactRequirement

    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    scene = build_scene(e.geometry)
    baseline = json.loads(
        Path("experiments/004-profile-recalculation/result.json").read_text()
    )
    profile = hashlib.sha256(
        json.dumps(e.resolved_profiles(), sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    state = PlayingState(
        tuple(baseline["joint_names"]),
        tuple(baseline["qpos_rad"]),
        profile,
        (ContactRequirement("r1c9", "index"),),
    )
    with pytest.raises(ValueError, match="declared contact"):
        reachable_actions(
            state, scene, e, (), CandidateSettings(()), PlanningSettings(), tmp_path
        )
