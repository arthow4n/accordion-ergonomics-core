import json
from pathlib import Path

import numpy as np

from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.held import held_audit
from accordion_ergonomics_core.scene import build_scene


def test_collision_clear_path_can_still_lose_held_contact() -> None:
    start = json.loads(
        Path("experiments/009-two-contacts/r2c4/result.json").read_text()
    )
    end = json.loads(Path("experiments/009-two-contacts/r2c5/result.json").read_text())
    e = Experiment.from_dict(start["input"])
    scene = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "middle")
    )
    direct = held_audit(
        scene,
        [start["qpos_rad"], end["qpos_rad"]],
        e,
        np.asarray(start["target"]["surface_world_m"]),
        "r1c5",
        0.01,
    )
    assert direct["sampled_constraints_satisfied"]
    assert not direct["held_geometry_satisfied"]
    assert direct["held_position_error_max_m"] > 0.02


def test_searched_path_preserves_contact_under_finer_audit() -> None:
    result = json.loads(
        Path("experiments/013-held-index-transition/result.json").read_text()
    )
    start = json.loads(
        Path("experiments/009-two-contacts/r2c4/result.json").read_text()
    )
    e = Experiment.from_dict(start["input"])
    scene = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "middle")
    )
    audit = held_audit(
        scene,
        result["waypoints_qpos_rad"],
        e,
        np.asarray(start["target"]["surface_world_m"]),
        "r1c5",
        0.0005,
    )
    assert audit["sampled_constraints_satisfied"]
    assert audit["held_geometry_satisfied"]
    assert audit["held_position_error_max_m"] <= e.solver.position_tolerance_m
