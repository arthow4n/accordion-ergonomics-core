"""Imported overlaps remain unresolved even without free-finger movement."""

from accordion_ergonomics_core.coordination import coordination_audit
from accordion_ergonomics_core.digits import DIGITS
from accordion_ergonomics_core.passage_search import reference_experiment
from accordion_ergonomics_core.scene import build_scene


def test_imported_envelope_control_is_not_a_calibration():
    e = reference_experiment()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    states = [
        dict(qpos_rad=s.model.qpos0.tolist(), roles={d: "free" for d in DIGITS})
    ] * 2
    audit = coordination_audit(s, states)
    assert audit["collision_validity"].endswith("anatomy unresolved")
    assert any(p["minimum_m"] < 0 for p in audit["pair_minima"])
    assert all(d["free_joint_variation_rad"] == 0 for d in audit["digits"].values())
    assert audit["traces"][0]["maximum_increase_over_imported_overlap_m"] == 0
    assert all(
        p["geometry_at_worst"][0]["underlying_meshes"] for p in audit["pair_minima"]
    )
    attempted = coordination_audit(s, states, connected=False)
    assert all(
        d["free_joint_variation_rad"] is None for d in attempted["digits"].values()
    )
