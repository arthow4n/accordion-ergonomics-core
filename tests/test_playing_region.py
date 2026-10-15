"""Frame, landmark and lifecycle falsification on real recorded states."""

import json
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.digits import DIGITS
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.playing_region import (
    LANDMARKS,
    board_coordinates,
    compiled_board_frame,
    lifecycle_summary,
    playing_region_trace,
    proximity_class,
)
from accordion_ergonomics_core.scene import build_scene

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def recorded():
    saved = json.loads(
        (
            ROOT / "experiments/042-connected-fingerings/repetition/result.json"
        ).read_text()
    )
    e = Experiment.from_dict(saved["scene_input"])
    return (
        saved,
        e,
        build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS),
    )


def test_compiled_board_signs_and_all_landmarks(recorded):
    saved, e, scene = recorded
    frame = compiled_board_frame(scene, e.geometry)
    rows = [next(c for c in frame["caps"] if c["row"] == r) for r in range(1, 6)]
    assert np.all(np.diff([r["surface_board_m"][0] for r in rows]) < 0)
    local = np.array([[0.02, 0.03, 0.04], [-0.02, -0.03, -0.04]])
    np.testing.assert_allclose(
        board_coordinates(
            e.geometry, local @ e.geometry.rotation.T + e.geometry.origin_m
        ),
        local,
        atol=1e-14,
    )
    strategy = saved["strategies"][0]
    region = playing_region_trace(scene, e, strategy, lifecycle=False)
    assert len(region["traces"]) == len(strategy["samples"])
    assert region["initial_approach"].startswith("unplanned")
    for i in [0, len(strategy["samples"]) // 2, len(strategy["samples"]) - 1]:
        scene.data.qpos[:] = strategy["samples"][i]["qpos_rad"]
        mujoco.mj_forward(scene.model, scene.data)
        for key, body in LANDMARKS.items():
            np.testing.assert_allclose(
                region["traces"][i]["landmarks_board_m"][key],
                board_coordinates(e.geometry, scene.data.body(body).xpos),
                atol=1e-14,
            )
        assert set(region["traces"][i]["fingertips_board_m"]) == set(DIGITS)
    p = np.array([r["landmarks_board_m"]["wrist"] for r in region["traces"]])
    np.testing.assert_allclose(
        region["landmarks"]["wrist"]["maximum_board_m"], p.max(axis=0)
    )
    assert region["landmarks"]["wrist"]["path_m"] >= np.linalg.norm(p[-1] - p[0])


def test_lifecycle_does_not_confuse_repeat_with_a_release():
    c = dict(finger="index", button_id="r1c5", behavior="release_after_event")
    observations: list[dict[str, Any]] = [
        dict(
            sample_index=i,
            binding_distances_m={"index:r1c5": v},
            held_contact_satisfied=True,
            destination_contact_satisfied=True,
            source_contact_satisfied=True,
        )
        for i, v in enumerate([0.0, 0.0, 0.0])
    ]
    result = lifecycle_summary([c], [c], observations, 0.001)
    assert result["releases"][0]["status"] == "release_not_demonstrated"
    observations[1]["binding_distances_m"]["index:r1c5"] = 0.005
    result = lifecycle_summary([c], [c], observations, 0.001)
    assert result["releases"][0]["separation_sample_indices"] == [1]
    assert result["mechanical_actuation"] == "unknown"
    held = dict(c, behavior="hold")
    observations[1]["held_contact_satisfied"] = False
    result = lifecycle_summary([held], [held], observations, 0.001)
    assert result["held_violation_sample_indices"] == [1]
    assert not result["releases"]


def test_incidental_proximity_is_not_actuation():
    assert proximity_class(0.0003, 0.001) == "near_cap_actuation_unknown"
    assert proximity_class(-0.004, 0.001) == "proxy_intersection"
    assert proximity_class(0.004, 0.001) == "geometrically_separated"


def test_interpolation_preserves_exact_saved_endpoints(recorded):
    from accordion_ergonomics_core.planning import PlanningSettings, audit_path

    saved, e, scene = recorded
    start = saved["strategies"][0]["samples"][0]["qpos_rad"]
    end = list(start)
    # Choose representable coordinates that exhibit subtraction/addition rounding.
    start = list(start)
    start[0], end[0] = -0.8765432109876543, 0.1234567890123456
    assert start[0] + (end[0] - start[0]) != end[0]
    audit = audit_path(scene, [start, end], e, PlanningSettings(max_joint_step_rad=0.1))
    assert audit["samples"][0]["qpos_rad"] == start
    assert audit["samples"][-1]["qpos_rad"] == end


def test_geometric_gate_rejects_contact_path_without_release(recorded, monkeypatch):
    from accordion_ergonomics_core import passage_search as search
    from accordion_ergonomics_core.planning import PlanningSettings

    saved, e, scene = recorded
    strategy = saved["strategies"][0]
    c = strategy["events"][0]["contacts"]
    q = strategy["samples"][0]["qpos_rad"]
    fake = dict(
        status="sampled_path_found",
        samples=[dict(qpos_rad=q), dict(qpos_rad=q)],
        attempts=[],
    )
    monkeypatch.setattr(
        search, "_plan_contact_change", lambda *args, **kwargs: dict(fake)
    )
    assert (
        search.plan_contact_change(scene, e, c, c, q, q, [], PlanningSettings())[
            "status"
        ]
        == "sampled_path_found"
    )
    strict = search.plan_contact_change(
        scene, e, c, c, q, q, [], PlanningSettings(), release_policy="geometric"
    )
    assert strict["status"] == "rejected_musical_lifecycle"
    assert not strict["musical_lifecycle"]["satisfied"]


def test_new_policies_are_optional_and_keep_five_fingers():
    from accordion_ergonomics_core.passage_search import PassageSearchSettings

    base = PassageSearchSettings()
    assert base.initial_selection == base.release_policy == "historical"
    assert base.selection_mode == "palm" and base.whole_hand_guidance_cost == 0
    assert base.fingers == DIGITS
    for field, value in [
        ("whole_hand_guidance_cost", -1),
        ("release_policy", "sounding"),
        ("initial_selection", "ergonomic"),
    ]:
        with pytest.raises(ValueError):
            options: dict[str, Any] = {field: value}
            PassageSearchSettings(**options)
