"""Connected sequence semantics; synthetic record fixtures never claim physics."""

import copy
from typing import Any

import pytest

from accordion_ergonomics_core.passage_media import (
    trajectory_frame_indices,
    validate_strategy,
)


@pytest.fixture
def synthetic_record():
    contacts = [
        {"finger": "index", "button_id": "r1c5", "behavior": "release_after_event"}
    ]
    nodes = [
        {"id": str(i), "qpos_rad": [float(i)], "contacts": contacts} for i in range(3)
    ]
    edges: list[dict[str, Any]] = [
        {
            "id": str(i),
            "source": str(i),
            "destination": str(i + 1),
            "status": "sampled_path_found",
            "path": {
                "samples": [
                    {"qpos_rad": [i + t], "sample_valid": True}
                    for t in (0.0, 0.25, 0.5, 0.75, 1.0)
                ]
            },
        }
        for i in range(2)
    ]
    samples: list[dict[str, Any]] = copy.deepcopy(
        edges[0]["path"]["samples"] + edges[1]["path"]["samples"][1:]
    )
    for i, s in enumerate(samples):
        s["event_index"] = {0: 0, 4: 1, 8: 2}.get(i)
    strategy = {
        "status": "sampled_connected_path",
        "node_ids": ["0", "1", "2"],
        "edge_ids": ["0", "1"],
        "events": [{"qpos_rad": n["qpos_rad"], "contacts": contacts} for n in nodes],
        "samples": samples,
    }
    return {
        "synthetic_fixture": "Logical provenance tests only, not MuJoCo states",
        "nodes": nodes,
        "edges": edges,
    }, strategy


def test_frames_are_exact_recorded_samples_and_show_every_event(synthetic_record):
    record, strategy = synthetic_record
    validate_strategy(record, strategy)
    indices = trajectory_frame_indices(strategy, 5)
    assert set((0, 4, 8)) <= set(indices)
    assert len(indices) == 5
    assert all(type(i) is int and 0 <= i < len(strategy["samples"]) for i in indices)
    with pytest.raises(ValueError, match="budget"):
        trajectory_frame_indices(strategy, 2)


@pytest.mark.parametrize(
    "fault", ["missing", "failed", "fabricated", "jump", "rejected"]
)
def test_missing_or_fabricated_motion_never_becomes_successful_animation(
    synthetic_record, fault
):
    record, strategy = synthetic_record
    if fault == "missing":
        strategy["edge_ids"] = ["0"]
    elif fault == "failed":
        record["edges"][1]["status"] = "no_path_found"
    elif fault == "fabricated":
        strategy["samples"][2]["qpos_rad"] = [123.0]
    elif fault == "jump":
        record["edges"][1]["path"]["samples"][0]["qpos_rad"] = [99.0]
    elif fault == "rejected":
        strategy["samples"][2]["sample_valid"] = False
    with pytest.raises(ValueError):
        validate_strategy(record, strategy)


def test_static_solve_trace_is_not_a_trajectory(synthetic_record):
    record, strategy = synthetic_record
    strategy["status"] = "static_contact_only"
    with pytest.raises(ValueError, match="movement"):
        validate_strategy(record, strategy)
    strategy["samples"] = []
    with pytest.raises(ValueError, match="evidence"):
        trajectory_frame_indices(strategy, 5)


def test_actual_repetition_search_is_deterministic_and_releases_cap():
    import numpy as np

    from accordion_ergonomics_core.passage_search import (
        PassageSearchSettings,
        reference_experiment,
        search_passage,
    )
    from accordion_ergonomics_core.passages import NoteEvent, Passage
    from accordion_ergonomics_core.planning import PlanningSettings

    reference = reference_experiment()
    settings = PassageSearchSettings(
        seed=42,
        beam_width=1,
        assignments_per_parent=1,
        fingers=("index",),
        prepare_next=False,
        assignment_order="marker_distance",
        contact_iterations=120,
        planning=PlanningSettings(
            withdrawal_depths_m=(0.01,),
            max_joint_step_rad=0.01,
            waypoint_iterations=120,
            rrt_iterations=0,
        ),
    )
    passage = Passage("numerical-repeat-test", (NoteEvent((60,)), NoteEvent((60,))))
    first = search_passage(passage, reference, settings)
    second = search_passage(passage, reference, settings)
    assert first["status"] == second["status"] == "complete_passage_found"
    a, b = first["strategies"][0], second["strategies"][0]
    validate_strategy(first, a)
    assert a["events"] == b["events"]
    assert [s["qpos_rad"] for s in a["samples"]] == [
        s["qpos_rad"] for s in b["samples"]
    ]
    contact = a["events"][0]["contacts"][0]
    assert a["events"][1]["contacts"] == a["events"][0]["contacts"]
    from accordion_ergonomics_core.instrument import button_at

    target = reference.geometry.surface_world_m(
        button_at(contact["row"], contact["column"])
    )
    normal = reference.geometry.rotation[:, 2]
    gaps = [
        float((np.array(s["finger_sites_world_m"]["index"]) - target) @ normal)
        for s in a["samples"]
    ]
    assert (
        max(gaps) > 0.009
    )  # Actual FK withdrawal, not a musical label or target alone.
    assert abs(gaps[0]) < 0.0003 and abs(gaps[-1]) < 0.0003
    assert first["edges"][0]["path"]["geometric_release_required"]
    assert all(
        set(s["finger_sites_world_m"]) == {"thumb", "index", "middle", "ring", "little"}
        for s in a["samples"]
    )
