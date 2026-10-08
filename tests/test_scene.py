from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.instrument import button_at, buttons
from accordion_ergonomics_core.scene import (
    build_scene,
    coupled_initial_pose,
    diagnostics,
)
from accordion_ergonomics_core.solver import accepted, solve_contact

INPUT = Path("experiments/001-single-contact/experiment.json")


@pytest.fixture(scope="module")
def scene():
    return build_scene(load_input(INPUT).geometry)


def test_compiled_anatomy_and_keyboard_frames(scene) -> None:
    experiment = load_input(INPUT)
    model, data = scene.model, scene.data
    assert (model.nq, model.nv, model.neq, model.nu) == (38, 38, 11, 63)
    for button in buttons():
        np.testing.assert_allclose(
            data.site(f"target_{button.id}").xpos,
            experiment.geometry.surface_world_m(button),
            atol=1e-12,
        )
    assert data.body("humerus_r").xpos[0] > 0  # actual right shoulder
    assert data.body("humerus_r").xpos[2] > data.body("capitate_r").xpos[2]
    data.qpos[:] = coupled_initial_pose(model, experiment.initial_joints_rad)
    check = diagnostics(scene, experiment.geometry.surface_world_m(button_at(1, 5)))
    assert check["equality_max_residual_rad"] < 1e-12
    assert check["joint_max_violation_rad"] == 0


def test_tip_is_on_outer_envelope_of_both_imported_shapes(scene) -> None:
    model, data = scene.model, scene.data
    mujoco.mj_forward(model, data)
    pad = data.site("index_pad").xpos
    normal = data.site("index_pad").xmat.reshape(3, 3)[:, 2]
    distances = []
    for name in ("distph2_coll_r", "distph2_coll_2_r"):
        geom = model.geom(name)
        center = data.geom_xpos[geom.id]
        rotation = data.geom_xmat[geom.id].reshape(3, 3)
        if name == "distph2_coll_r":
            axis = rotation[:, 2]
            support = center @ normal + geom.size[1] * abs(axis @ normal) + geom.size[0]
        else:
            support = center @ normal + np.linalg.norm(
                geom.size * (rotation.T @ normal)
            )
        distances.append(pad @ normal - support)
    assert min(distances) == pytest.approx(0, abs=1e-12)
    assert all(d >= -1e-12 for d in distances)
    # Prevent the earlier failure: the ellipsoid extends farther than the capsule.
    assert distances[0] > 0.001


def test_one_contact_ik_preserves_couplings_and_diagnostics(scene) -> None:
    experiment = load_input(INPUT)
    result = solve_contact(
        scene,
        experiment.geometry.surface_world_m(button_at(1, 5)),
        experiment.initial_joints_rad,
        experiment.solver,
    )
    assert result["status"] == "success"
    assert result["feasible"] is None
    assert result["trajectory"] is None
    assert accepted(result["diagnostics"], experiment.solver)
    tip_contacts = [
        c
        for c in result["diagnostics"]["contacts"]
        if c["geom1"] == "distph2_coll_2_r" and c["geom2"] == "r1c5"
    ]
    assert tip_contacts
    assert abs(tip_contacts[0]["distance_m"]) < experiment.solver.position_tolerance_m


def test_solved_endpoints_do_not_imply_a_trajectory(scene) -> None:
    experiment = load_input(INPUT)
    unreachable = np.array([8.0, 8.0, 8.0])
    from dataclasses import replace

    result = solve_contact(
        scene,
        unreachable,
        experiment.initial_joints_rad,
        replace(experiment.solver, max_iterations=4),
    )
    assert result["status"] == "failed"
    assert result["feasible"] is None  # local solver failure is not impossibility proof
    assert result["diagnostics"]["position_error_m"] > 1
