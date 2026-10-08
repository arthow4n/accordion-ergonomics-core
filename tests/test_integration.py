from dataclasses import replace
from pathlib import Path

import numpy as np

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.integration import collision_checked_step
from accordion_ergonomics_core.profiles import ContactProfile
from accordion_ergonomics_core.scene import Scene


def test_clear_endpoints_do_not_allow_a_colliding_ik_edge() -> None:
    model = mujoco.MjModel.from_xml_string("""<mujoco><worldbody>
        <geom name="obstacle" type="sphere" pos=".03 0 0" size=".01"/>
        <body><joint type="hinge" axis="0 0 1"/>
        <geom name="orbit" type="sphere" pos=".03 0 0" size=".01"/>
        </body></worldbody></mujoco>""")
    data = mujoco.MjData(model)
    scene = Scene(model, data, [1], [0], [], ContactProfile())
    start = np.array([-np.pi / 2])
    goal = np.array([np.pi / 2])
    for q in (start, goal):
        data.qpos[:] = q
        mujoco.mj_forward(model, data)
        assert not any(c.dist < 0 for c in data.contact)
    settings = replace(
        load_input(
            Path("experiments/004-profile-recalculation/experiment.json")
        ).solver,
        collision_limit_implementation="displacement",
    )
    found, record = collision_checked_step(scene, start, goal - start, settings)
    assert found is not None
    assert record["fraction"] < 1
    assert record["attempts"][0]["sampled_edge_valid"] is False
    assert record["continuous_validity"] is None
    assert found[0] < 0


def test_colliding_initial_seed_is_diagnostic_failure() -> None:
    import json

    from accordion_ergonomics_core.scene import build_scene

    saved = json.loads(
        Path("experiments/017-corrected-contact/result.json").read_text()
    )
    e = load_input(Path("experiments/017-corrected-contact/experiment.json"))
    scene = build_scene(e.geometry)
    q = np.asarray(saved["qpos_rad"])
    found, record = collision_checked_step(scene, q, np.zeros_like(q), e.solver)
    assert found is None
    assert record["reason"] == "initial_collision_violation"
