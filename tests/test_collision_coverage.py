import json
from pathlib import Path

from accordion_ergonomics_core.collision_coverage import audit_collision_coverage
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.scene import build_scene


def test_accepted_two_contact_pose_has_unchecked_cross_digit_proxy_overlaps() -> None:
    saved = json.loads(
        Path("experiments/009-two-contacts/r2c4/result.json").read_text()
    )
    e = Experiment.from_dict(saved["input"])
    scene = build_scene(
        e.geometry, e.player, e.setup, e.physical_contact, ("index", "middle")
    )
    scene.data.qpos[:] = saved["qpos_rad"]
    audit = audit_collision_coverage(scene)
    assert audit["mask_counts"] == [{"contype": 1, "conaffinity": 0, "count": 36}]
    assert len(audit["explicit_pairs"]) == 4
    assert audit["unchecked_overlap_count"] > 0
    assert all(p["digits"][0] != p["digits"][1] for p in audit["overlaps"])
