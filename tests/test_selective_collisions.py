import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core.candidates import (
    CandidateSettings,
    descriptors,
    materially_distinct,
)
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.distance_limits import collision_pairs
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.instrument import button_at
from accordion_ergonomics_core.profiles import ContactProfile
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene, diagnostics
from accordion_ergonomics_core.solver import accepted


def test_named_self_pair_detects_previously_unchecked_overlap_without_scaling() -> None:
    saved = json.loads(
        Path("experiments/009-two-contacts/r2c4/result.json").read_text()
    )
    e = Experiment.from_dict(saved["input"])
    policy = ContactProfile(
        additional_collision_pairs=(("midph2_coll_r", "midph3_coll_r"),)
    )
    scene = build_scene(e.geometry, contact=policy, fingers=("index", "middle"))
    original = build_scene(e.geometry, fingers=("index", "middle"))
    np.testing.assert_array_equal(scene.model.geom_size, original.model.geom_size)
    np.testing.assert_array_equal(scene.model.geom_pos, original.model.geom_pos)
    np.testing.assert_array_equal(scene.model.jnt_range, original.model.jnt_range)
    assert scene.model.npair == original.model.npair + 1
    assert compiled_model_digest(scene.model) != compiled_model_digest(original.model)
    pair = tuple(
        sorted(
            (scene.model.geom("midph2_coll_r").id, scene.model.geom("midph3_coll_r").id)
        )
    )
    assert pair in collision_pairs(scene.model, scene.anatomy_geoms, scene.board_geoms)
    scene.data.qpos[:] = saved["qpos_rad"]
    check = diagnostics(scene, e.geometry.surface_world_m(button_at(1, 5)))
    assert check["max_penetration_m"] > 0.009
    assert not accepted(check, e.solver)


def test_pair_order_is_canonical_and_invalid_pairs_are_rejected() -> None:
    a = ContactProfile(additional_collision_pairs=(("midph3_coll_r", "midph2_coll_r"),))
    b = ContactProfile(additional_collision_pairs=(("midph2_coll_r", "midph3_coll_r"),))
    assert a == b
    with pytest.raises(ValueError, match="unique"):
        ContactProfile(
            additional_collision_pairs=a.additional_collision_pairs
            + b.additional_collision_pairs
        )
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    with pytest.raises(ValueError, match="Unknown"):
        build_scene(
            e.geometry,
            contact=ContactProfile(
                additional_collision_pairs=(("unknown", "midph2_coll_r"),)
            ),
        )


def test_deduplication_preserves_materially_different_middle_finger() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    scene = build_scene(e.geometry)
    a = descriptors(scene)
    others = dict(a.other_digits_rad)
    others["middle"] = tuple(v + 0.2 for v in others["middle"])
    b = replace(a, other_digits_rad=others)
    assert materially_distinct(a, b, CandidateSettings(offsets_rad=()))
