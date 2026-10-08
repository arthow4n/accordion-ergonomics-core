import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.instrument import button_at
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.solver import solve_contact


def test_second_contact_is_required_and_both_distal_envelopes_are_respected() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    s = build_scene(e.geometry, fingers=("index", "middle"))
    b = json.loads(
        Path("experiments/004-profile-recalculation/result.json").read_text()
    )
    s.data.qpos[:] = b["qpos_rad"]
    mujoco.mj_forward(s.model, s.data)
    pad = s.data.site("middle_pad").xpos
    normal = s.data.site("middle_pad").xmat.reshape(3, 3)[:, 2]
    margins = []
    for name in ("distph3_coll_r", "distph3_coll_2_r"):
        geom = s.model.geom(name)
        r = s.data.geom_xmat[geom.id].reshape(3, 3)
        center = s.data.geom_xpos[geom.id]
        support = center @ normal + (
            geom.size[1] * abs(r[:, 2] @ normal) + geom.size[0]
            if name == "distph3_coll_r"
            else np.linalg.norm(geom.size * (r.T @ normal))
        )
        margins.append(pad @ normal - support)
    assert min(margins) > -1e-12
    assert min(margins) < 1e-12
    result = solve_contact(
        s,
        e.geometry.surface_world_m(button_at(1, 5)),
        dict(zip(b["joint_names"], b["qpos_rad"], strict=True)),
        replace(e.solver, max_iterations=2),
        additional_contacts=((np.array([8.0, 8.0, 8.0]), "middle", "r1c6"),),
    )
    assert result["status"] == "failed"
    assert result["feasible"] is None
    assert len(result["diagnostics"]["contact_diagnostics"]) == 2
    assert result["diagnostics"]["position_error_m"] > 1
    assert all(i not in result["frozen_dof_indices"] for i in range(22, 30))


def test_two_contacts_are_accepted_only_with_individual_geometric_checks() -> None:
    e = load_input(Path("experiments/009-two-contacts/r2c4/experiment.json"))
    s = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "middle")
    )
    a, b = e.contacts
    result = solve_contact(
        s,
        e.geometry.surface_world_m(button_at(a.row, a.column)),
        e.initial_joints_rad,
        e.solver,
        button_at(a.row, a.column).id,
        additional_contacts=(
            (
                e.geometry.surface_world_m(button_at(b.row, b.column)),
                b.finger,
                button_at(b.row, b.column).id,
            ),
        ),
    )
    assert result["status"] == "success"
    assert result["feasible"] is None
    for check in result["diagnostics"]["contact_diagnostics"]:
        assert abs(check["target_contact_distance_m"]) <= e.solver.position_tolerance_m
        assert check["position_error_m"] <= e.solver.position_tolerance_m
        assert check["max_penetration_m"] <= e.solver.penetration_tolerance_m


def test_unused_digits_can_articulate_without_empty_freezing_constraint() -> None:
    from accordion_ergonomics_core.profiles import ContactProfile

    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    b = json.loads(
        Path("experiments/004-profile-recalculation/result.json").read_text()
    )
    scene = build_scene(
        e.geometry, contact=ContactProfile(inactive_digits_policy="allow_articulation")
    )
    result = solve_contact(
        scene,
        e.geometry.surface_world_m(button_at(1, 5)),
        dict(zip(b["joint_names"], b["qpos_rad"], strict=True)),
        e.solver,
    )
    assert result["status"] == "success"
    assert result["frozen_dof_indices"] == []
