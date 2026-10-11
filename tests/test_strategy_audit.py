"""Falsify palm-only equivalence and validate recorded-state audit semantics."""

import json
from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core.digits import DIGITS
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.strategy_audit import (
    audit_states,
    coordinate_descriptors,
)

ROOT = Path(__file__).resolve().parents[1]


def test_recorded_fk_and_proximal_coordinates_are_not_invented():
    saved = json.loads(
        (ROOT / "experiments/042-connected-fingerings/stepwise/result.json").read_text()
    )
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    states = saved["strategies"][0]["samples"][:3]
    audit = audit_states(scene, e.geometry, states, saved["joint_names"])
    for actual, expected in zip(audit["traces"], states, strict=True):
        assert actual["qpos_rad"] == expected["qpos_rad"]
        np.testing.assert_allclose(
            actual["palm_world_m"], expected["palm_world_m"], atol=1e-12
        )
        for digit in DIGITS:
            np.testing.assert_allclose(
                actual["finger_sites_world_m"][digit],
                expected["finger_sites_world_m"][digit],
                atol=1e-12,
            )
        r = np.asarray(actual["palm_body_axes_in_board"])
        np.testing.assert_allclose(r.T @ r, np.eye(3), atol=1e-12)
        assert actual["active_contacts"] == expected["active_contacts"]
    with pytest.raises(ValueError, match="actual states"):
        audit_states(scene, e.geometry, [], saved["joint_names"])
    with pytest.raises(ValueError, match="joint order"):
        audit_states(scene, e.geometry, states, list(reversed(saved["joint_names"])))


def test_untimed_total_variation_counts_reversals_and_ignores_duplicate_samples():
    q = np.array([[0.0], [0.1], [0.1], [-0.2], [0.0]])
    d = coordinate_descriptors(q, ["test_hinge"])["test_hinge"]
    assert d["total_variation_rad"] == pytest.approx(0.6)
    assert d["excursion_rad"] == pytest.approx(0.3)
    assert d["reversals"] == 2


def test_fixed_benchmark_falsifies_palm_only_order_and_preserves_failed_nodes():
    record = json.loads(
        (ROOT / "experiments/045-strategy-audit/audit/result.json").read_text()
    )
    cases = {c["source_reference"]["id"]: c for c in record["cases"]}
    short, long = cases["stepwise-index"], cases["stepwise-ring"]
    assert short["palm_path_m"] < long["palm_path_m"]
    assert (
        short["joint_descriptors"]["deviation_r"]["excursion_rad"]
        > long["joint_descriptors"]["deviation_r"]["excursion_rad"]
    )
    assert (
        short["joint_descriptors"]["flexion_r"]["excursion_rad"]
        < long["joint_descriptors"]["flexion_r"]["excursion_rad"]
    )
    assert cases["reversal-overlap"]["worst_proxy_m"] < -0.016
    failed = cases["held-incomplete"]
    assert failed["palm_path_m"] is None
    assert failed["maximum_joint_step_rad"] is None
    assert failed["state_kind"] == "separate_attempted_nodes; not movement"
    assert all(
        c["first_note_approach"]["status"] == "not_planned" for c in cases.values()
    )
