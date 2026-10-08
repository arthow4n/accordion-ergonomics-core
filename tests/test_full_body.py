from dataclasses import replace
from pathlib import Path

import myo_sim
import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.architecture import compare_right_arm
from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.full_body import (
    FullBodyPosture,
    build_full_body,
    native_spec,
    prescribed_pose,
    right_joint_names,
)
from accordion_ergonomics_core.instrument import button_at
from accordion_ergonomics_core.profiles import PlayerProfile
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene, coupled_initial_pose
from accordion_ergonomics_core.solver import solve_contact

REFERENCE = Path("experiments/029-myosim-seated-lower-body/reference/experiment.json")


@pytest.mark.parametrize("assembly", ["myofullbody_native", "myofullbody_reduced"])
@pytest.mark.parametrize("yaw", [0.0, 0.4])
def test_right_arm_fields_fk_and_jacobians_match(assembly, yaw):
    e = load_input(REFERENCE)
    quat = Rotation.from_euler("z", np.pi + yaw).as_quat()
    setup = replace(e.setup, torso_rotation_wxyz=(quat[3], *quat[:3]))
    old = build_scene(e.geometry, e.player, setup)
    new = build_scene(e.geometry, PlayerProfile(model=assembly), setup)
    comparison = compare_right_arm(
        old,
        new,
        [
            {},
            e.initial_joints_rad,
            {
                "shoulder_elv_r": 1.2,
                "elv_angle_r": -0.7,
                "shoulder_rot_r": 0.8,
                "elbow_flexion_r": 2.0,
                "pro_sup_r": -0.9,
                "flexion_r": -0.5,
                "deviation_r": 0.25,
                "mcp2_flexion_r": 1.0,
                "pm2_flexion_r": 0.8,
                "md2_flexion_r": 0.7,
            },
        ],
    )
    assert max(comparison["joint_field_max_errors"].values()) == 0
    assert max(comparison["geom_field_max_errors"].values()) < 1e-14
    assert comparison["coupling_max_error"] == 0
    assert comparison["coupling_links_match"]
    assert max(comparison["max_errors"].values()) < 2e-12
    assert new.data.body("humerus_r").xpos[0] > 0
    assert new.data.body("humerus_l").xpos[0] < 0


def test_reduction_preserves_every_native_body_and_bone_at_prescribed_pose():
    e = load_input(REFERENCE)
    posture = FullBodyPosture(torso_flexion_rad=0.1, left_elbow_flexion_rad=0.6)
    native, values, _ = build_full_body("myofullbody_native", e.setup, posture)
    reduced, _, _ = build_full_body("myofullbody_reduced", e.setup, posture)
    a, b = native.compile(), reduced.compile()
    da, db = mujoco.MjData(a), mujoco.MjData(b)
    da.qpos[:] = prescribed_pose(a, values)
    mujoco.mj_forward(a, da)
    mujoco.mj_forward(b, db)
    assert (b.nq, b.nu, b.neq, b.npair) == (38, 63, 11, 4)
    for i in range(1, a.nbody):
        name = a.body(i).name
        np.testing.assert_allclose(da.body(name).xpos, db.body(name).xpos, atol=2e-12)
        np.testing.assert_allclose(da.body(name).xmat, db.body(name).xmat, atol=2e-12)
    for i in range(a.ngeom):
        if a.geom_type[i] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        name = a.geom(i).name
        j = b.geom(name).id
        np.testing.assert_allclose(da.geom_xpos[i], db.geom_xpos[j], atol=2e-12)
        np.testing.assert_allclose(da.geom_xmat[i], db.geom_xmat[j], atol=2e-12)
        np.testing.assert_array_equal(a.geom_size[i], b.geom_size[j])
    reference = myo_sim.load_spec("myoarm_r").compile()
    for name in [reference.actuator(i).name for i in range(reference.nu)]:
        for field in ("actuator_gainprm", "actuator_biasprm", "actuator_dynprm"):
            np.testing.assert_array_equal(
                getattr(reference, field)[reference.actuator(name).id],
                getattr(b, field)[b.actuator(name).id],
            )
    assert not any(
        b.geom_contype[i] for i in range(b.ngeom) if b.geom(i).name.endswith("_l")
    )


def test_coupled_directional_jacobian_agrees_with_finite_difference():
    e = load_input(REFERENCE)
    s = build_scene(e.geometry, PlayerProfile(model="myofullbody_reduced"), e.setup)
    m, d = s.model, s.data
    values = dict(e.initial_joints_rad)
    base = coupled_initial_pose(m, values)
    d.qpos[:] = base
    mujoco.mj_forward(m, d)
    jp, jr = np.zeros((3, m.nv)), np.zeros((3, m.nv))
    mujoco.mj_jacSite(m, d, jp, jr, m.site("index_pad").id)
    epsilon = 1e-6
    for name in (
        "shoulder_elv_r",
        "elv_angle_r",
        "elbow_flexion_r",
        "pro_sup_r",
        "flexion_r",
        "mcp2_flexion_r",
        "md2_flexion_r",
    ):
        qplus = coupled_initial_pose(m, {**values, name: values.get(name, 0) + epsilon})
        qminus = coupled_initial_pose(
            m, {**values, name: values.get(name, 0) - epsilon}
        )
        d.qpos[:] = qplus
        mujoco.mj_forward(m, d)
        plus = d.site("index_pad").xpos.copy()
        d.qpos[:] = qminus
        mujoco.mj_forward(m, d)
        minus = d.site("index_pad").xpos.copy()
        derivative = (qplus - qminus) / (2 * epsilon)
        np.testing.assert_allclose(
            jp @ derivative, (plus - minus) / (2 * epsilon), atol=2e-9
        )


@pytest.mark.parametrize("assembly", ["myofullbody_native", "myofullbody_reduced"])
def test_representative_contact_and_passive_coordinates(assembly):
    e = load_input(REFERENCE)
    scene = build_scene(e.geometry, PlayerProfile(model=assembly), e.setup)
    result = solve_contact(
        scene,
        e.geometry.surface_world_m(button_at(1, 5)),
        e.initial_joints_rad,
        e.solver,
    )
    assert result["status"] == "success", result["failure"]
    for name in scene.passive_joints:
        assert (
            scene.data.qpos[scene.model.joint(name).qposadr[0]]
            == scene.prescribed_joints[name]
        )
    assert (
        result["diagnostics"]["equality_max_residual_rad"]
        <= e.solver.equality_tolerance_rad
    )
    assert (
        result["diagnostics"]["target_contact_distance_m"]
        <= e.solver.position_tolerance_m
    )
    assert len(result["frozen_dof_indices"]) == len(scene.passive_joints) + 16


def test_assembly_identity_and_upstream_registry_are_not_silently_changed():
    from myo_sim.build.compose import MODEL_REGISTRY

    before = MODEL_REGISTRY["myofullbody"].build_kwargs.copy()
    native_spec()
    assert MODEL_REGISTRY["myofullbody"].build_kwargs == before
    assert myo_sim.load_spec("myofullbody").compile().nv == 128
    e = load_input(REFERENCE)
    raw = e.expanded_source()
    raw["player"]["model"] = "myofullbody_reduced"
    with pytest.raises(ValueError, match="disagrees"):
        Experiment.from_dict(raw)
    old = build_scene(e.geometry, e.player, e.setup)
    new = build_scene(e.geometry, PlayerProfile(model="myofullbody_reduced"), e.setup)
    assert compiled_model_digest(old.model) != compiled_model_digest(new.model)
    assert (
        tuple(new.model.joint(i).name for i in range(new.model.njnt))
        == right_joint_names()
    )
    with pytest.raises(ValueError, match="range"):
        build_full_body(
            "myofullbody_reduced", e.setup, FullBodyPosture(left_elbow_flexion_rad=4)
        )


def test_native_left_arm_mirror_uses_equivalent_named_angles():
    s = native_spec()
    s.body("Full Body").pos = [0, 0, 0.65]
    s.body("Full Body").quat = [0, 0, 0, 1]
    m = s.compile()
    d = mujoco.MjData(m)
    q = prescribed_pose(
        m,
        {
            "shoulder_elv_r": 0.6,
            "elbow_flexion_r": 0.8,
            "pro_sup_r": 0.4,
            "flexion_r": 0.2,
            "mcp2_flexion_r": 0.8,
        },
    )
    for name in right_joint_names():
        left = name[:-2] + "_l" if name.endswith("_r") else name + "_l"
        q[m.joint(left).qposadr[0]] = q[m.joint(name).qposadr[0]]
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    for name in ("humerus", "ulna", "capitate", "distph2"):
        np.testing.assert_allclose(
            d.body(name + "_l").xpos, d.body(name + "_r").xpos * [-1, 1, 1], atol=1e-11
        )


def test_default_assembly_keeps_historical_input_selection_explicit():
    assert PlayerProfile().model == "myofullbody_reduced"
    e = load_input(REFERENCE)
    assert e.player.model == "myoarm_r"
    migrated = replace(e, player=PlayerProfile())
    raw = migrated.expanded_source()
    assert raw["anatomy"]["model"] == raw["player"]["model"] == "myofullbody_reduced"
    assert Experiment.from_dict(raw).player == migrated.player
