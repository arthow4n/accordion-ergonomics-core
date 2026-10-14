"""Bounded force geometry, equality gates and visual-only tendon overlays."""

import numpy as np
import pytest

from accordion_ergonomics_core.muscle_support import balance_certificate


def test_bounded_force_certificate_distinguishes_span_from_unilateral_capacity():
    # Full row rank does not imply bounded pulling forces can supply this load.
    a = np.array([[1.0, 0], [0, 1.0]])
    failed = balance_certificate(a, np.array([-0.01, 0.2]))
    assert failed["gap"] > 0
    assert failed["required_projected_work"] > failed["maximum_bounded_active_work"]
    good = balance_certificate(a, np.array([0.1, 0.2]))
    assert good["gap"] == pytest.approx(0, abs=1e-10)
    limited = balance_certificate(a, np.array([1.1, 0.2]))
    assert limited["gap"] == pytest.approx(0.1)


def test_tendon_overlay_restores_compiled_model(tmp_path):
    from accordion_ergonomics_core.digits import DIGITS
    from accordion_ergonomics_core.passage_search import reference_experiment
    from accordion_ergonomics_core.provenance import compiled_model_digest
    from accordion_ergonomics_core.render import render_views
    from accordion_ergonomics_core.scene import build_scene

    e = reference_experiment()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    s.data.qpos[:] = [
        e.initial_joints_rad[s.model.joint(i).name] for i in range(s.model.njnt)
    ]
    identity = compiled_model_digest(s.model)
    render_views(
        s,
        tmp_path,
        list(e.geometry.origin_m),
        "r1c5",
        views_to_render=("hand",),
        highlighted_tendon_names=("PQ_tendon",),
    )
    assert identity == compiled_model_digest(s.model)
    assert (tmp_path / "hand.png").is_file()


def test_pinned_inverse_wrap_fallback_is_not_a_transmission_sign_change():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    record = json.loads(
        (root / "experiments/051-muscle-support/diagnostics/result.json").read_text()
    )
    for route in record["routes"]:
        assert route["length_jump_m"] > 0.001
        assert route["fraction_gap"] < 2e-11
        diagnostics = [
            s["native"]["inverse_wrap_diagnostic"][0] for s in route["states"]
        ]
        assert {d["native_point_classification"] for d in diagnostics} == {
            "matches_fallback_average",
            "matches_independent_root",
        }
        assert all(abs(d["root_residual"]) < 2e-12 for d in diagnostics)
        for s in route["states"]:
            difference = abs(s["native"]["length_m"] - s["reduced"]["length_m"])
            assert difference < 1e-12 or difference == pytest.approx(
                route["length_jump_m"], abs=1e-10
            )
    assert all(
        p["native_parity"]["musculotendon_length_max_error_m"] < 1e-10
        for p in record["poses"]
    )
    subset = record["operating_quantity_subset"]
    assert set(subset["excluded_actuators"]) == {"PQ", "DELT3", "EDC2", "EDC4"}
    assert len(subset["passed_tested_probes"]) == 59
    assert all(
        p["diagnostics"]["equality_position_error_rad"] < 1e-8 for p in record["poses"]
    )
    assert all(
        p["diagnostics"]["load_ablations"][0]["certificate"]["gap"] > 1e-6
        for p in record["poses"]
    )
