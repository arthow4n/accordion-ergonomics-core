"""Engine sign, native parity, numerical capacity and inherited-routing tests."""

import json
from pathlib import Path

import myo_sim
import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.digits import DIGITS
from accordion_ergonomics_core.muscle_validation import native_parity
from accordion_ergonomics_core.muscles import (
    StaticScenario,
    conditional_static_screen,
    length_derivative_check,
    muscle_snapshot,
)
from accordion_ergonomics_core.passage_search import reference_experiment
from accordion_ergonomics_core.scene import build_scene

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def anatomy():
    e = reference_experiment()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    q = [
        e.initial_joints_rad.get(s.model.joint(i).name, s.model.qpos0[i])
        for i in range(s.model.njnt)
    ]
    return e, s, q


def test_native_parameters_lengths_and_transmissions_are_preserved(anatomy):
    _, scene, q = anatomy
    arm = myo_sim.load_spec("myoarm_r").compile()
    data = mujoco.MjData(arm)
    snapshot = muscle_snapshot(scene, q)
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    parity = native_parity(scene.model, arm, data, snapshot, names)
    assert max(parity["parameter_max_errors"].values()) == 0
    assert parity["musculotendon_length_max_error_m"] < 1e-12
    assert parity["moment_matrix_max_error_m_per_rad"] < 1e-12
    assert parity["gravity_bias_max_error_nm"] < 1e-12
    assert parity["passive_muscle_force_max_error_n"] < 1e-8
    assert scene.model.nu == 63 and scene.model.ntendon == 67


def test_negative_muscle_forces_and_inverse_balance_use_engine_signs(anatomy):
    _, scene, q = anatomy
    snapshot = muscle_snapshot(scene, q)
    assert max(snapshot["engine_checks"].values()) < 1e-8
    assert np.max(snapshot["active_force_per_activation_n"]) <= 0
    assert np.max(snapshot["passive_muscle_force_n"]) <= 0
    assert np.min(snapshot["passive_muscle_force_n"]) < -100
    eq = np.array(snapshot["equality_jacobian"])
    assert eq.shape == (11, 38) and np.linalg.matrix_rank(eq) == 11


@pytest.mark.parametrize("objective", ["activation_squared", "activation_sum"])
def test_constructed_balanced_fixture_is_solved_without_widening_bounds(
    anatomy, objective
):
    e, scene, q = anatomy
    snapshot = muscle_snapshot(scene, q)
    matrix = np.array(snapshot["transmission_length_derivative_m_per_rad"])
    active = np.array(snapshot["active_force_per_activation_n"])
    passive = np.array(snapshot["passive_muscle_force_n"])
    # Artificial force-balance RHS proves numerical solver correctness, not capacity.
    expected = matrix.T @ (passive + 0.2 * active)
    snapshot["gravity_bias_nm"] = (expected + snapshot["joint_passive_nm"]).tolist()
    result = conditional_static_screen(
        scene, e.geometry, snapshot, [], StaticScenario(objective=objective)
    )
    assert result["conditional_feasible"]
    assert result["force_balance_residual_full_nm"] < 1e-6
    assert min(result["activation"]) >= -1e-8
    assert max(result["activation"]) <= 1 + 1e-8
    assert result["human_feasibility"] is None


def test_inherited_pq_derivative_discrepancy_is_not_hidden(anatomy):
    _, scene, _ = anatomy
    case = json.loads(
        (ROOT / "experiments/045-strategy-audit/audit/result.json").read_text()
    )["cases"][0]
    q = case["traces"][19]["qpos_rad"]
    check = length_derivative_check(scene, q)
    assert check["worst_actuator"] == "PQ"
    assert check["worst_joint"] == "pro_sup_r"
    assert check["maximum_error_m_per_rad"] > 0.002
    second = length_derivative_check(scene, q, 1e-7)
    assert second["maximum_error_m_per_rad"] == pytest.approx(
        check["maximum_error_m_per_rad"], rel=1e-5
    )
    pq = scene.model.actuator("PQ").id
    errors = np.array(check["per_actuator_maximum_error_m_per_rad"])
    assert np.delete(errors, pq).max() < 1e-7
    np.testing.assert_allclose(scene.data.qpos, q, atol=0)


def test_conditional_hypothetical_reaction_is_separate_and_sign_correct(anatomy):
    e, scene, q = anatomy
    snapshot = muscle_snapshot(scene, q)
    baseline = conditional_static_screen(
        scene, e.geometry, snapshot, [], StaticScenario()
    )
    assert not baseline["conditional_feasible"]
    assert "not a feasible recruitment" in baseline["solution_kind"]
    forced = conditional_static_screen(
        scene, e.geometry, snapshot, [{"finger": "index"}], StaticScenario(1.0)
    )
    jacobian = np.zeros((3, scene.model.nv))
    mujoco.mj_jacSite(
        scene.model, scene.data, jacobian, None, scene.model.site("index_pad").id
    )
    np.testing.assert_allclose(
        forced["external_reaction_generalized_nm"],
        jacobian.T @ e.geometry.rotation[:, 2],
        atol=1e-12,
    )
    assert forced["applied_contact_count"] == 1
    assert "synthetic" in forced["scenario"]["force_provenance"]
    assert forced["dynamic_execution"] == "not_evaluated"
    with pytest.raises(ValueError):
        StaticScenario(-1.0)
    with pytest.raises(ValueError):
        StaticScenario(objective="human_effort")
