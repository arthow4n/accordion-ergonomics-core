"""Fixed MyoSim bone anatomy; support capsules remain explicit hypotheses."""

from dataclasses import asdict, dataclass
from math import isfinite, pi

import numpy as np
from scipy.spatial.transform import Rotation


@dataclass(frozen=True)
class SeatedLegs:
    model: str = "myolegs"
    hip_flexion_rad: float = pi / 2
    hip_abduction_rad: float = pi / 36
    knee_flexion_rad: float = pi / 2
    thigh_envelope_radius_m: float = 0.075
    support_fraction: float = 0.45
    evidence: str = "docs/research/seated-lower-body.md"

    def __post_init__(self):
        if self.model != "myolegs":
            raise ValueError("Only the audited myolegs skeleton is supported")
        for value in asdict(self).values():
            if isinstance(value, (int, float)) and not isfinite(value):
                raise ValueError("Lower-body parameters must be finite")
        if not (
            0 <= self.hip_flexion_rad <= 2.0944 and 0 <= self.knee_flexion_rad <= 2.0944
        ):
            raise ValueError("Seated flexion exceeds imported joint ranges")
        if not 0 <= self.hip_abduction_rad <= 0.3:
            raise ValueError("Unsupported seated hip abduction")
        if not 0.04 <= self.thigh_envelope_radius_m <= 0.11:
            raise ValueError("Unsupported assumed thigh envelope")
        if not 0.1 <= self.support_fraction <= 0.9:
            raise ValueError("Support station must lie along the femur")


def default_lower_body():
    return asdict(SeatedLegs())


def posed_lower_body(setup):
    """Evaluate upstream FK and polynomial knee/patella couplings before baking."""
    import myo_sim

    from ._engine import mujoco

    p = setup.seated.lower_body
    assert isinstance(p, SeatedLegs)
    spec = myo_sim.load_spec(p.model)
    spec.body("Full Body").pos = list(setup.torso_origin_m)
    spec.body("Full Body").quat = list(setup.torso_rotation_wxyz)
    model = spec.compile()
    data = mujoco.MjData(model)
    for side in ("r", "l"):
        for name, value in (
            ("hip_flexion", p.hip_flexion_rad),
            ("hip_adduction", -p.hip_abduction_rad),
            ("knee_angle", p.knee_flexion_rad),
        ):
            data.qpos[model.joint(f"{name}_{side}").qposadr[0]] = value
    # Upstream dependencies may themselves depend on other coupled coordinates.
    for _ in range(model.neq + 1):
        for i in range(model.neq):
            if model.eq_type[i] == mujoco.mjtEq.mjEQ_JOINT:
                a, b = model.eq_obj1id[i], model.eq_obj2id[i]
                x = data.qpos[model.jnt_qposadr[b]] if b >= 0 else 0.0
                data.qpos[model.jnt_qposadr[a]] = np.polynomial.polynomial.polyval(
                    x, model.eq_data[i, :5]
                )
    mujoco.mj_forward(model, data)
    landmarks = {
        name: data.body(name).xpos.copy()
        for name in (
            "pelvis",
            "femur_r",
            "femur_l",
            "tibia_r",
            "tibia_l",
            "calcn_r",
            "calcn_l",
        )
    }
    return spec, model, data, landmarks


def lower_body_anchors(setup):
    _, _, _, points = posed_lower_body(setup)
    p = setup.seated.lower_body
    assert isinstance(p, SeatedLegs)
    q = setup.torso_rotation_wxyz
    frame = Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix() @ np.diag(
        [-1.0, -1.0, 1.0]
    )
    hip, knee = points["femur_r"], points["tibia_r"]
    center = hip + p.support_fraction * (knee - hip)
    direction = frame @ np.array([-0.5, 0, np.sqrt(3) / 2])
    axis = (knee - hip) / np.linalg.norm(knee - hip)
    direction -= axis * (axis @ direction)
    direction /= np.linalg.norm(direction)
    reference = center + p.thigh_envelope_radius_m * direction
    return points, reference


def attach_fixed_lower_body(spec, setup):
    """Attach original bone meshes at baked FK, adding no dynamic coordinates."""
    from ._engine import mujoco

    child, model, data, _ = posed_lower_body(setup)
    # Capture resolved local transforms; raw XML quaternions omit Euler frames.
    transforms = {}
    for b in child.bodies:
        if b.name == "world":
            continue
        i = model.body(b.name).id
        parent = model.body_parentid[i]
        r = data.xmat[parent].reshape(3, 3)
        pos = r.T @ (data.xpos[i] - data.xpos[parent])
        rotation = r.T @ data.xmat[i].reshape(3, 3)
        quat = Rotation.from_matrix(rotation).as_quat()
        transforms[b.name] = (pos, np.r_[quat[3], quat[:3]])
    for collection in (
        child.actuators,
        child.sensors,
        child.tendons,
        child.equalities,
        child.pairs,
        child.excludes,
        child.keys,
        child.joints,
        child.sites,
        child.lights,
        child.cameras,
    ):
        for item in list(collection):
            child.delete(item)
    child.delete(child.body("sacrum"))  # Arm already supplies identical torso/sacrum.
    for geom in list(child.geoms):
        if geom.type != mujoco.mjtGeom.mjGEOM_MESH or geom.group != 0:
            child.delete(geom)
        else:
            geom.contype = geom.conaffinity = 0
    for b in child.bodies:
        if b.name != "world":
            b.pos, b.quat = transforms[b.name]
    frame = spec.worldbody.add_frame()
    spec.attach(child, prefix="seated_", frame=frame)
    p = setup.seated.lower_body
    assert isinstance(p, SeatedLegs)
    landmarks = {
        name: data.body(name).xpos.copy()
        for name in ("femur_r", "femur_l", "tibia_r", "tibia_l")
    }
    for side in ("r", "l"):
        spec.worldbody.add_geom(
            name=f"approximate_thigh_support_{side}",
            type=mujoco.mjtGeom.mjGEOM_CAPSULE,
            fromto=[*landmarks[f"femur_{side}"], *landmarks[f"tibia_{side}"]],
            size=[p.thigh_envelope_radius_m, 0, 0],
            rgba=[0.35, 0.42, 0.5, 0.18],
            contype=0,
            conaffinity=0,
        )
