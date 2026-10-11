import json
from pathlib import Path

from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.hand_audit import (
    HAND_POLICY_ID,
    audit_hand_pose,
    hand_pairs,
    run_hand_audit,
)
from accordion_ergonomics_core.scene import build_scene


def test_native_hand_policy_distinguishes_composition_and_hypotheses() -> None:
    saved = json.loads(
        Path("experiments/037-upper-anchor-regression/central/result.json").read_text()
    )
    e = Experiment.from_dict(saved["input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, ("index",))
    scene.data.qpos[:] = saved["qpos_rad"]
    pairs = hand_pairs(scene)
    assert len(pairs) == 276
    assert sum(p["configured"] for p in pairs) == 16
    audit = audit_hand_pose(scene, pairs)
    assert audit["policy_id"] == HAND_POLICY_ID
    assert audit["anatomical_validation"] == "unresolved"
    assert audit["human_feasibility"] is None
    assert audit["unresolved_overlap_count"] > 0
    composite = [
        p
        for p in audit["pairs"]
        if p["classification"] == "same_segment_composite_envelope"
    ]
    assert len(composite) == 5
    assert all(p["signed_proxy_distance_m"] < 0 for p in composite)
    assert all(not p["mask_compatible"] for p in pairs)
    assert sum(p["explicit_engine_pair"] for p in pairs) == 16


def test_empty_path_is_not_audit_success(tmp_path: Path) -> None:
    import hashlib

    import pytest

    saved_path = Path(
        "experiments/037-upper-anchor-regression/central/result.json"
    ).resolve()
    saved = json.loads(saved_path.read_text())
    saved["samples"] = []
    path = tmp_path / "path.json"
    path.write_text(json.dumps(saved))
    definition = tmp_path / "experiment.json"
    definition.write_text(
        json.dumps(
            {
                "id": "empty",
                "records": [
                    {
                        "id": "empty",
                        "result": str(path),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "kind": "path",
                        "model_result": str(saved_path),
                        "model_sha256": hashlib.sha256(
                            saved_path.read_bytes()
                        ).hexdigest(),
                    }
                ],
            }
        )
    )
    with pytest.raises(ValueError, match="Empty paths"):
        run_hand_audit(definition, tmp_path / "output")
