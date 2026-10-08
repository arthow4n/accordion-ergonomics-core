from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.instrument import button_at, buttons
from accordion_ergonomics_core.profiles import PlayerProfile, SetupProfile
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene


def test_legacy_and_explicit_profiles_compile_identically() -> None:
    old = load_input(Path("experiments/001-single-contact/experiment.json"))
    new = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    assert compiled_model_digest(
        build_scene(old.geometry, old.player).model
    ) == compiled_model_digest(
        build_scene(new.geometry, new.player, new.setup, new.physical_contact).model
    )


def test_board_rotation_and_torso_translation_are_independent() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    geometry = replace(e.geometry, rotation_wxyz=(1, 0, 0, 0))
    scene = build_scene(geometry, setup=SetupProfile(torso_origin_m=(0.1, 0.2, 1.1)))
    original = build_scene(e.geometry)
    for button in buttons():
        np.testing.assert_allclose(
            scene.data.site(f"target_{button.id}").xpos,
            geometry.surface_world_m(button),
            atol=1e-12,
        )
    np.testing.assert_allclose(
        scene.data.body("humerus_r").xpos - original.data.body("humerus_r").xpos,
        [0.1, 0.2, 0.1],
        atol=1e-12,
    )
    assert not np.allclose(
        geometry.surface_world_m(button_at(1, 5)),
        e.geometry.surface_world_m(button_at(1, 5)),
    )


def test_player_range_overrides_change_compiled_model() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    scene = build_scene(
        e.geometry, PlayerProfile(joint_ranges_rad={"deviation_r": (-0.2, 0.2)})
    )
    np.testing.assert_allclose(scene.model.joint("deviation_r").range, [-0.2, 0.2])
    assert compiled_model_digest(scene.model) != compiled_model_digest(
        build_scene(e.geometry).model
    )
    with pytest.raises(ValueError, match="Unknown joint"):
        build_scene(
            e.geometry, PlayerProfile(joint_ranges_rad={"invented": (-0.2, 0.2)})
        )
    with pytest.raises(ValueError):
        replace(e.geometry, rotation_wxyz=(2, 0, 0, 0))
