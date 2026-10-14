"""Actual whole-path policy tradeoffs and historically compatible consumers."""

import json
from pathlib import Path

import pytest

from accordion_ergonomics_core.selection import posture_strategy_order

ROOT = Path(__file__).resolve().parents[1]


def test_posture_and_whole_hand_policies_retain_real_counterexamples():
    record = json.loads(
        (ROOT / "experiments/052-posture-selection/audit/result.json").read_text()
    )
    cases = [
        c
        for c in record["cases"]
        if c["source"]["id"]
        in ("arpeggio-A-4309", "arpeggio-B-4309", "arpeggio-C-4309")
    ]
    posture = posture_strategy_order(cases, "posture")
    whole = posture_strategy_order(cases, "whole_hand")
    assert posture[0]["id"].startswith("arpeggio-C-4309")
    assert whole[0]["id"] == "arpeggio-B-4309-strategy-1"
    assert posture[0]["descriptors"]["maximum_flexion_reference_departure_rad"] < 0.22
    assert posture[0]["descriptors"]["sampled_proxy_penetration_m"] > 0.016
    assert whole[0]["descriptors"]["sampled_proxy_penetration_m"] < 0.004
    assert len(posture) == len(whole) == len(cases)
    assert set(c["id"] for c in cases) == set(c["id"] for c in posture)
    with pytest.raises(ValueError, match="policy"):
        posture_strategy_order(cases, "muscle")


def test_new_search_retains_all_fingers_and_records_budget_pruning():
    r = json.loads(
        (
            ROOT / "experiments/052-posture-selection/arpeggio-C-4309/result.json"
        ).read_text()
    )
    assert set(r["settings"]["fingers"]) == {
        "thumb",
        "index",
        "middle",
        "ring",
        "little",
    }
    assert any(
        h["status"] == "unexplored_budget"
        for b in r["hypothesis_batches"]
        for h in b["hypotheses"]
    )
    assert any(n["status"] == "pruned_beam_policy" for n in r["nodes"])
    assert any(
        "maximum_flexion_reference_departure_rad" in c["descriptors"]
        for selection in r["selection_records"]
        for c in selection["ordered_candidates"]
    )


def test_v2_library_integrity_and_historical_api():
    from accordion_ergonomics_core.research import ExerciseLibrary

    library = ExerciseLibrary(ROOT)
    assert len(library.posture_record()["targets"]) == 50
    assert (
        library.assessment("passage-stepwise")["assessment_version"]
        == "biomechanics-v1"
    )
    assessment = library.posture_assessment("passage-stepwise")
    assert assessment["assessment_version"] == "posture-coordination-v2"
    assert assessment["human_feasibility"] is None
    ident = "stepwise-C-4309-strategy-0"
    case = library.posture_case(ident)
    trajectory = library.posture_trajectory(ident)
    assert len(trajectory["samples"]) == case["sample_count"]
    media = library.posture_media(ident)
    for frame in media["animation"]["frames"]:
        assert (
            frame["qpos_rad"]
            == trajectory["samples"][frame["sample_index"]]["qpos_rad"]
        )
    assert any(p.suffix == ".gif" for p in media["paths"])
    assert library.posture_comparisons("passage-stepwise")
    with pytest.raises(KeyError, match="complete movement"):
        library.posture_trajectory("held-incomplete-separate-nodes")


def test_paired_controls_and_rejected_approaches_have_saved_evidence():
    record = json.loads(
        (ROOT / "experiments/052-posture-selection/selection/result.json").read_text()
    )
    assert len(record["paired_trials"]) == 3
    assert all(
        a["status"] == "rejected_direct_reference_approach"
        for a in record["initial_approaches"]
    )
    assert all(
        a["path"]["samples"] and a["media"] for a in record["initial_approaches"]
    )
    assert "pruned" in record["full_path_scope"]


def test_budget_control_retains_identical_paths_and_explicit_coverage_states():
    from accordion_ergonomics_core.movement_evidence import state_digest

    base = json.loads(
        (
            ROOT / "experiments/052-posture-selection/arpeggio-C-4309/result.json"
        ).read_text()
    )
    expanded = json.loads(
        (
            ROOT / "experiments/052-posture-selection/arpeggio-C-4309-five/result.json"
        ).read_text()
    )
    for a, b in zip(base["strategies"], expanded["strategies"], strict=True):
        assert state_digest(a["samples"]) == state_digest(b["samples"])
    coverage = json.loads(
        (ROOT / "experiments/052-posture-selection/coverage/result.json").read_text()
    )
    for pose in coverage["poses"]:
        source = pose["source"]
        saved = json.loads(
            (ROOT / "experiments/052-posture-selection" / source["result"]).read_text()
        )
        strategy = next(
            s for s in saved["strategies"] if s["id"] == source["strategy_id"]
        )
        assert (
            pose["qpos_rad"] == strategy["samples"][source["sample_index"]]["qpos_rad"]
        )
        assert pose["audit"]["cross_digit_pairs_distance_queried"] > 0
