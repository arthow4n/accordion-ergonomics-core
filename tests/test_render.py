import json
from pathlib import Path

import numpy as np

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.render import render_views
from accordion_ergonomics_core.scene import build_scene


def test_render_refreshes_pose_and_restores_model(tmp_path: Path) -> None:
    e = load_input(Path("experiments/004-profile-recalculation/experiment.json"))
    scene = build_scene(e.geometry)
    original = compiled_model_digest(scene.model)
    states = [
        json.loads(Path(p).read_text())
        for p in (
            "experiments/004-profile-recalculation/result.json",
            "experiments/002-arm-ablation/r1c9-arm-enabled/result.json",
        )
    ]
    for i, state in enumerate(states):
        scene.data.qpos[:] = state["qpos_rad"]
        render_views(
            scene,
            tmp_path / str(i),
            state["target"]["surface_world_m"],
            state["target"]["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=("proxph3_coll_r", "proxph4_coll_r"),
        )
        assert compiled_model_digest(scene.model) == original
        np.testing.assert_allclose(
            scene.data.site("index_pad").xpos,
            state["diagnostics"]["pad_world_m"],
            atol=1e-12,
        )
    assert (tmp_path / "0" / "keyboard.png").read_bytes() != (
        tmp_path / "1" / "keyboard.png"
    ).read_bytes()
