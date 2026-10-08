import json
from dataclasses import replace
from pathlib import Path

import numpy as np

from accordion_ergonomics_core.candidates import CandidateSettings, discover_candidates
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.experiment import ContactRequest
from accordion_ergonomics_core.scene import build_scene


def test_multiple_starts_disprove_necessary_near_limit_wrist_pose() -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    baseline = json.loads(
        Path("experiments/004-profile-recalculation/result.json").read_text()
    )
    e = replace(e, contacts=(ContactRequest(3, 5, "index"),))
    scene = build_scene(e.geometry)
    settings = CandidateSettings(({"elbow_flexion_r": -0.4, "pro_sup_r": -0.4},))
    result = discover_candidates(
        scene, e, baseline["qpos_rad"], baseline["profiles_sha256"], settings
    )
    assert len(result["candidates"]) == 2
    wrist_margins = []
    for c in result["candidates"]:
        scene.data.qpos[:] = c["state"]["joint_angles_rad"]
        indices = [scene.model.joint(n).id for n in ("deviation_r", "flexion_r")]
        q = scene.data.qpos[indices]
        margins = np.minimum(
            q - scene.model.jnt_range[indices, 0], scene.model.jnt_range[indices, 1] - q
        )
        wrist_margins.append(float(margins.min()))
    assert wrist_margins[1] > wrist_margins[0] + 0.05
    assert result["physical_feasibility"] is None
