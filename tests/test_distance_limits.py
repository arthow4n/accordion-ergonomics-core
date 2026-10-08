import mink
import numpy as np
import pytest

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.distance_limits import (
    DisplacementDistanceLimit,
    collision_pairs,
    signed_distance_gradient,
)
from accordion_ergonomics_core.profiles import ContactProfile


def sphere_model(world_anchor: bool = False):
    anchor = '<geom name="fixed" type="sphere" size=".01"/>'
    if not world_anchor:
        anchor = (
            '<body><joint name="anchor" type="slide" axis="1 0 0"/>'
            + anchor
            + "</body>"
        )
    return mujoco.MjModel.from_xml_string(
        "<mujoco><worldbody>"
        + anchor
        + """
        <body pos=".03 0 0"><joint name="motion" type="slide" axis="1 0 0"/>
        <geom name="moving" type="sphere" size=".01"/><site name="tip"/>
        </body></worldbody></mujoco>"""
    )


@pytest.mark.parametrize("dt", [0.01, 0.02, 0.1, 1.0])
@pytest.mark.parametrize("world_anchor", [False, True])
def test_displacement_bound_preserves_gap_across_timesteps(dt, world_anchor) -> None:
    m = sphere_model(world_anchor)
    config = mink.Configuration(m)
    policy = ContactProfile(collision_detection_distance_m=0.05)
    limit = DisplacementDistanceLimit(m, collision_pairs(m, [1], [0]), policy)
    assert len(limit.pairs) == 1
    task = mink.FrameTask("tip", "site", position_cost=1, orientation_cost=0)
    task.set_target(mink.SE3.from_translation(np.zeros(3)))
    constraints = [] if world_anchor else [mink.DofFreezingTask(m, [0])]
    velocity = mink.solve_ik(
        config, [task], dt, solver="clarabel", limits=[limit], constraints=constraints
    )
    config.integrate_inplace(velocity, dt)
    distance = mujoco.mj_geomDistance(m, config.data, 0, 1, 1.0, None)
    assert distance == pytest.approx(0.0015, abs=1e-7)


@pytest.mark.parametrize("offset", [0, -0.02, -0.01])
def test_distance_gradient_matches_signed_finite_difference(offset) -> None:
    m = sphere_model()
    c = mink.Configuration(m, q=np.array([0.0, offset]))
    _, gradient = signed_distance_gradient(m, c.data, 0, 1, 1.0)
    assert gradient is not None
    numerical = []
    for i in range(m.nv):
        epsilon = np.zeros(m.nv)
        epsilon[i] = 1e-7
        plus = mink.Configuration(m, q=c.q + epsilon)
        minus = mink.Configuration(m, q=c.q - epsilon)
        numerical.append(
            (
                mujoco.mj_geomDistance(m, plus.data, 0, 1, 1.0, None)
                - mujoco.mj_geomDistance(m, minus.data, 0, 1, 1.0, None)
            )
            / 2e-7
        )
    np.testing.assert_allclose(gradient, numerical, atol=1e-7)


def test_detection_band_must_exceed_required_clearance() -> None:
    with pytest.raises(ValueError, match="Invalid collision policy"):
        ContactProfile(
            collision_detection_distance_m=0.01, collision_minimum_distance_m=0.01
        )
