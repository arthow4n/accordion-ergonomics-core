from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.anatomy import (
    DIGITS,
    DISTAL_BINDINGS,
    digit_dofs,
    distal_support,
)
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.experiment import ContactRequest
from accordion_ergonomics_core.instrument import button_at
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.solver import solve_contact


@pytest.fixture(scope="module")
def reference():
    e = load_input(
        Path("experiments/037-upper-anchor-regression/central/experiment.json")
    )
    return e, build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)


@pytest.mark.parametrize("digit", DIGITS)
def test_compiled_distal_marker_matches_outer_support(reference, digit):
    _, scene = reference
    m = scene.model
    point, quat = distal_support(m, digit)
    site = m.site(f"{digit}_pad")
    np.testing.assert_allclose(site.pos, point, atol=1e-15)
    np.testing.assert_allclose(site.quat, quat, atol=1e-15)
    assert int(site.bodyid[0]) == m.body(DISTAL_BINDINGS[digit][0]).id
    assert len(digit_dofs(m)[digit]) == 4
    matrix = np.zeros(9)
    mujoco.mju_quat2Mat(matrix, quat)
    normal = matrix.reshape(3, 3)[:, 2].copy()
    c, e = (m.geom(n) for n in DISTAL_BINDINGS[digit][1:3])
    mujoco.mju_quat2Mat(matrix, c.quat)
    axis = matrix.reshape(3, 3)[:, 2].copy()
    capsule_support = normal @ c.pos + c.size[1] * abs(normal @ axis) + c.size[0]
    mujoco.mju_quat2Mat(matrix, e.quat)
    radii = e.size * (matrix.reshape(3, 3).T @ normal)
    ellipse_support = normal @ e.pos + np.linalg.norm(radii)
    assert normal @ point == pytest.approx(
        max(capsule_support, ellipse_support), abs=1e-14
    )
    # Thumb reverses the imported capsule axis; all other digits retain +z.
    assert normal @ axis == pytest.approx(DISTAL_BINDINGS[digit][3])


def test_contact_requests_and_simultaneous_distinctness(reference):
    e, scene = reference
    contacts = tuple(ContactRequest(1, 4 + i, d) for i, d in enumerate(DIGITS))
    assert len(replace(e, contacts=contacts).contacts) == 5
    with pytest.raises(ValueError, match="distinct"):
        replace(e, contacts=(contacts[0], contacts[0]))
    with pytest.raises(ValueError, match="one button"):
        replace(
            e, contacts=(ContactRequest(1, 5, "thumb"), ContactRequest(1, 5, "little"))
        )
    with pytest.raises(ValueError, match="simultaneous"):
        solve_contact(
            scene,
            np.zeros(3),
            {},
            e.solver,
            finger="ring",
            additional_contacts=((np.ones(3), "ring", "r1c6"),),
        )


def test_unassigned_policy_is_explicit_and_posture_regularized(reference):
    from accordion_ergonomics_core.profiles import ContactProfile

    e, _ = reference
    for policy in ("freeze", "allow_articulation"):
        scene = build_scene(
            e.geometry,
            e.player,
            e.setup,
            replace(e.physical_contact, inactive_digits_policy=policy),
        )
        result = solve_contact(
            scene,
            e.geometry.surface_world_m(button_at(1, 5)),
            e.initial_joints_rad,
            replace(e.solver, max_iterations=1),
        )
        unassigned = {
            i
            for d, indices in digit_dofs(scene.model).items()
            if d != "index"
            for i in indices
        }
        frozen = set(result["frozen_dof_indices"])
        assert (
            (unassigned <= frozen) if policy == "freeze" else not (unassigned & frozen)
        )
        assert result["solver_settings"]["posture_cost"] > 0

    with pytest.raises(ValueError, match="policy"):
        ContactProfile(inactive_digits_policy="free")


def test_diagnostic_roles_and_cameras_reject_unsupported_labels(reference, tmp_path):
    from accordion_ergonomics_core.render import render_views

    _, scene = reference
    before = scene.model.site_rgba.copy()
    with pytest.raises(ValueError, match="role"):
        render_views(
            scene, tmp_path, [0, 0, 0], "r1c5", contact_roles={"ring": "optimal"}
        )
    with pytest.raises(ValueError, match="camera"):
        render_views(
            scene,
            tmp_path,
            [0, 0, 0],
            "r1c5",
            camera_overrides={"hand": {"distance": 1.0}},
        )
    np.testing.assert_array_equal(before, scene.model.site_rgba)


def test_cli_does_not_load_mujoco_before_backend_selection():
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import accordion_ergonomics_core.cli; "
            "assert 'mujoco' not in sys.modules",
        ],
        check=False,
    )
    assert result.returncode == 0


def test_named_ring_hold_uses_ring_geometry_not_index():
    import json

    from accordion_ergonomics_core.experiment import Experiment
    from accordion_ergonomics_core.held import held_audit
    from accordion_ergonomics_core.scene import coupled_initial_pose

    saved = json.loads(
        Path(
            "experiments/041-five-finger-contacts/free/index-ring/candidate-0/result.json"
        ).read_text()
    )
    e = Experiment.from_dict(saved["input"])
    scene = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "ring")
    )
    target = np.asarray(saved["targets"][1]["surface_world_m"])
    q = saved["qpos_rad"]
    audit = held_audit(scene, [q], e, target, "r2c6", 0.01, "ring")
    assert audit["held_geometry_satisfied"]
    initial = dict(zip(saved["joint_names"], q, strict=True))
    initial["mcp4_flexion_r"] += 0.04
    moved = coupled_initial_pose(scene.model, initial).tolist()
    audit = held_audit(scene, [q, moved], e, target, "r2c6", 0.01, "ring")
    assert not audit["held_geometry_satisfied"]
    assert audit["held_position_error_max_m"] > e.solver.position_tolerance_m


def test_mixed_contact_flags_and_world_controls_are_explicit(reference):
    e, scene = reference
    surface = e.geometry.surface_world_m(button_at(1, 6))
    preparation = surface + 0.01 * e.geometry.rotation[:, 2]
    additional = ((e.geometry.surface_world_m(button_at(1, 5)), "index", "r1c5"),)
    invalid_flags: tuple[Any, ...] = ((True,), (False, "held"))
    for flags in invalid_flags:
        with pytest.raises(ValueError, match="flags"):
            solve_contact(
                scene,
                preparation,
                e.initial_joints_rad,
                e.solver,
                "r1c6",
                finger="ring",
                additional_contacts=additional,
                required_contacts=flags,
            )
    result = solve_contact(
        scene,
        preparation,
        e.initial_joints_rad,
        replace(e.solver, max_iterations=1),
        "r1c6",
        finger="ring",
        additional_contacts=additional,
        required_contacts=(False, True),
    )
    assert result["contact_required"] is False
    requirements = result["contact_requirements"]
    assert [r["surface_contact_required"] for r in requirements] == [False, True]
    np.testing.assert_array_equal(requirements[0]["target_world_m"], preparation)
    assert result["trajectory"] is None  # Numerical iterations never claim movement.
