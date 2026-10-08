from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.profiles import PlayerProfile
from accordion_ergonomics_core.scene import build_scene, coupled_initial_pose


@pytest.mark.parametrize("scale", [0.95, 1.05])
def test_hand_transform_scales_geometry_about_fixed_wrist_and_removes_muscles(
    scale: float,
) -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    original = build_scene(e.geometry)
    variant = build_scene(
        e.geometry,
        PlayerProfile(
            model_mode="kinematic_geometry_hypothesis", geometric_hand_scale=scale
        ),
    )
    q = coupled_initial_pose(original.model, e.initial_joints_rad)
    for scene in (original, variant):
        scene.data.qpos[:] = q
        mujoco.mj_forward(scene.model, scene.data)
    assert variant.model.nu == 0
    assert variant.model.ntendon == 0
    assert variant.model.nq == original.model.nq == 38
    np.testing.assert_allclose(
        variant.model.jnt_range, original.model.jnt_range, atol=1e-12
    )
    for name in ("lunate_r", "humerus_r", "ulna_r", "radius_r"):
        np.testing.assert_allclose(
            variant.data.body(name).xpos, original.data.body(name).xpos, atol=1e-12
        )
    wrist = original.data.body("lunate_r").xpos
    for name in ("capitate_r", "distph2_r", "distph3_r", "distal_thumb_r"):
        np.testing.assert_allclose(
            variant.data.body(name).xpos - wrist,
            scale * (original.data.body(name).xpos - wrist),
            atol=1e-12,
        )
    np.testing.assert_allclose(
        variant.data.site("index_pad").xpos - wrist,
        scale * (original.data.site("index_pad").xpos - wrist),
        atol=1e-12,
    )
    np.testing.assert_allclose(
        variant.model.geom("distph2_coll_r").size,
        scale * original.model.geom("distph2_coll_r").size,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        variant.model.body("distph2_r").mass,
        scale**3 * original.model.body("distph2_r").mass,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        variant.model.body("distph2_r").inertia,
        scale**5 * original.model.body("distph2_r").inertia,
        atol=1e-12,
    )


def test_scaling_cannot_silently_keep_physiological_actuators() -> None:
    with pytest.raises(ValueError, match="hypothesis mode"):
        PlayerProfile(geometric_hand_scale=0.95)
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    assert e.player.geometric_hand_scale == 1
    assert e.expanded_source()["player"]["model_mode"] == "imported_musculoskeletal"
    assert (
        PlayerProfile(joint_ranges_rad={"flexion_r": (-0.4, 0.4)}).joint_range_evidence[
            "flexion_r"
        ]["kind"]
        == "assumption"
    )
