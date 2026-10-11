"""Research policy must expose real tradeoffs and never silently ban a digit."""

from dataclasses import replace

import numpy as np
import pytest

from accordion_ergonomics_core.passage_search import PassageSearchSettings
from accordion_ergonomics_core.passages import NoteEvent, fingering_hypotheses
from accordion_ergonomics_core.selection import (
    CRITERIA,
    pareto_order,
    technique_priority,
)


def test_pareto_layers_preserve_tradeoffs_and_declared_tie_break():
    def node(name, vector):
        return dict(
            id=name,
            cost=vector[0],
            selection_descriptors=dict(zip(CRITERIA, vector, strict=True)),
        )

    short = node("short", [0.01, 2, 1, 0.01])
    wrist = node("wrist", [0.02, 1, 1, 0.01])
    dominated = node("dominated", [0.03, 3, 2, 0.02])
    actual = pareto_order([short, dominated, wrist])
    assert [n["id"] for n in actual] == ["wrist", "short", "dominated"]
    assert [n["pareto_layer"] for n in actual] == [0, 0, 1]
    assert short["selection_descriptors"]["palm_path_m"] < wrist["cost"]


def test_optional_technique_prior_preserves_all_five_hypotheses():
    hypotheses = fingering_hypotheses(NoteEvent((60,)), seed=17)
    original = {
        (h["contacts"][0]["finger"], h["contacts"][0]["button_id"]) for h in hypotheses
    }
    hypotheses.sort(key=technique_priority)
    assert {h["contacts"][0]["finger"] for h in hypotheses} == {
        "thumb",
        "index",
        "middle",
        "ring",
        "little",
    }
    assert hypotheses[0]["contacts"][0]["finger"] in ("index", "middle", "ring")
    assert original == {
        (h["contacts"][0]["finger"], h["contacts"][0]["button_id"]) for h in hypotheses
    }
    assert technique_priority(hypotheses[-1]) == 1


def test_muscle_prior_cannot_be_enabled_without_validation():
    with pytest.raises(ValueError, match="validation"):
        replace(PassageSearchSettings(), selection_mode="muscle")
    for bad in (0, -1, np.nan):
        with pytest.raises(ValueError, match="multiplier"):
            replace(PassageSearchSettings(), unassigned_posture_multiplier=bad)


def test_complete_sample_ranking_rejects_missing_evidence():
    from accordion_ergonomics_core.selection import audited_strategy_order

    partial = {
        "id": "partial",
        "status": "static_contact_only",
        "whole_hand": dict(sample_count=1, palm_path_m=0, state_sequence_sha256="same"),
        "independent_audit": dict(sample_count=1, state_sequence_sha256="same"),
    }
    with pytest.raises(ValueError, match="complete movement"):
        audited_strategy_order([partial])


def test_expanded_input_preserves_replaced_playing_seed_and_contact():
    from accordion_ergonomics_core.experiment import ContactRequest
    from accordion_ergonomics_core.passage_search import reference_experiment

    e = reference_experiment()
    changed = replace(
        e,
        initial_joints_rad={"flexion_r": 0.123},
        contacts=(ContactRequest(1, 5, "ring"),),
    )
    expanded = changed.expanded_source()
    assert expanded["initial_joints_rad"] == {"flexion_r": 0.123}
    assert expanded["contacts"][0]["finger"] == "ring"
    assert e.source["initial_joints_rad"] != expanded["initial_joints_rad"]


def test_recorded_baseline_and_sampled_counterexamples():
    import json
    from pathlib import Path

    from accordion_ergonomics_core.selection import audited_strategy_order

    root = Path(__file__).resolve().parents[1]
    historical = json.loads(
        (
            root / "experiments/043-autonomous-discovery/discovery/evaluation-07.json"
        ).read_text()
    )
    baseline = json.loads(
        (
            root / "experiments/047-whole-hand-comparison/arpeggio-A-4309/result.json"
        ).read_text()
    )
    assert baseline["strategies"] == historical["strategies"]
    comparison = json.loads(
        (
            root / "experiments/047-whole-hand-comparison/comparison/result.json"
        ).read_text()
    )
    by_name = {t["source"]["id"]: t for t in comparison["trials"]}
    strategies = by_name["arpeggio-B-4309"]["strategies"]
    assert audited_strategy_order(strategies)[0]["id"] == "strategy-1"
    assert audited_strategy_order(strategies, "wrist_first")[0]["id"] == "strategy-0"
    assert (
        strategies[0]["independent_audit"]["worst_cross_digit"]["distance_m"] < -0.013
    )
    free = by_name["stepwise-free"]["strategies"][0]["whole_hand"]
    frozen = by_name["stepwise-frozen"]["strategies"][0]["whole_hand"]
    assert sum(d["free_joint_total_variation_rad"] for d in free["digits"].values()) > 0
    assert (
        sum(d["free_joint_total_variation_rad"] for d in frozen["digits"].values())
        < 1e-10
    )
    stronger = by_name["stepwise-local10"]["strategies"][0]["whole_hand"]

    def wrist(a):
        return sum(
            a["joint_descriptors"][k]["total_variation_rad"]
            for k in ("flexion_r", "deviation_r")
        )

    assert stronger["palm_path_m"] < free["palm_path_m"]
    assert wrist(stronger) > wrist(free) * 5
