"""Native MyoSim anatomy with explicit prescribed or baked passive coordinates."""

from dataclasses import asdict, dataclass
from math import isfinite, pi

import myo_sim
import numpy as np
from scipy.spatial.transform import Rotation

ASSEMBLIES = ("myoarm_r", "myofullbody_native", "myofullbody_reduced")
DEFAULT_ASSEMBLY = "myofullbody_reduced"
COLLISION_POLICY = "legacy_right_arm_proxies_and_four_self_pairs_v1"


@dataclass(frozen=True)
class FullBodyPosture:
    """Generic assumptions, independent of instrument placement or left tasks."""

    hip_flexion_rad: float = pi / 2
    hip_abduction_rad: float = pi / 36
    knee_flexion_rad: float = pi / 2
    left_elbow_flexion_rad: float = 0.35
    left_shoulder_elevation_rad: float = 0.1
    torso_flexion_rad: float = 0.0
    evidence: str = "docs/research/full-body-architecture.md"

    def __post_init__(self):
        if not all(
            isfinite(v) for v in asdict(self).values() if isinstance(v, (int, float))
        ):
            raise ValueError("Full-body posture must be finite")

    def joints(self):
        result = {
            "flex_extension": self.torso_flexion_rad,
            "elbow_flexion_l": self.left_elbow_flexion_rad,
            "shoulder_elv_l": self.left_shoulder_elevation_rad,
        }
        for side in ("r", "l"):
            result.update(
                {
                    f"hip_flexion_{side}": self.hip_flexion_rad,
                    f"hip_adduction_{side}": -self.hip_abduction_rad,
                    f"knee_angle_{side}": self.knee_flexion_rad,
                }
            )
        return result


def native_spec():
    """Use supported root option without leaking upstream's registry mutation.

    0.2.3 build_spec updates the registration's mutable build_kwargs in place.
    Restore it even on failure so historical builders remain deterministic.
    """
    from myo_sim.build.compose import MODEL_REGISTRY

    options = MODEL_REGISTRY["myofullbody"].build_kwargs
    saved = options.copy()
    try:
        return myo_sim.load_spec(
            "myofullbody", build_kwargs={"add_root_freejoint": False}
        )
    finally:
        options.clear()
        options.update(saved)


def right_joint_names():
    return tuple(j.name for j in myo_sim.load_spec("myoarm_r").joints)


def prescribed_pose(model, values):
    """Resolve scalar polynomial equalities relative to compiled qpos0."""
    from ._engine import mujoco

    q = model.qpos0.copy()
    for name, value in values.items():
        q[model.joint(name).qposadr[0]] = value
    for _ in range(model.neq + 1):
        for i in range(model.neq):
            if model.eq_type[i] != mujoco.mjtEq.mjEQ_JOINT:
                raise ValueError("Unexpected non-joint upstream equality")
            a, b = int(model.eq_obj1id[i]), int(model.eq_obj2id[i])
            ai = model.jnt_qposadr[a]
            delta = (
                q[model.jnt_qposadr[b]] - model.qpos0[model.jnt_qposadr[b]]
                if b >= 0
                else 0
            )
            q[ai] = model.qpos0[ai] + np.polynomial.polynomial.polyval(
                delta, model.eq_data[i, :5]
            )
    for i in range(model.njnt):
        if model.jnt_limited[i]:
            value = q[model.jnt_qposadr[i]]
            if (
                not model.jnt_range[i, 0] - 1e-8
                <= value
                <= model.jnt_range[i, 1] + 1e-8
            ):
                raise ValueError(
                    f"Prescribed posture exceeds range: {model.joint(i).name}"
                )
    return q


def build_full_body(assembly, setup, posture):
    """Return editable anatomy, prescribed scalar values and frozen names.

    Reduction preserves the original body tree and all right-arm joint fields.
    It bakes compiled passive FK, rather than guessing raw Euler/frame transforms.
    Right-arm muscle/tendon parameters are retained; no muscle-control claim.
    """
    from ._engine import mujoco

    if assembly not in ASSEMBLIES[1:]:
        raise ValueError("Unknown full-body assembly")
    spec = native_spec()
    spec.body("Full Body").pos = list(setup.torso_origin_m)
    spec.body("Full Body").quat = list(setup.torso_rotation_wxyz)
    reference = myo_sim.load_spec("myoarm_r")
    active = {j.name for j in reference.joints}
    model = spec.compile()
    data = mujoco.MjData(model)
    values = posture.joints()
    if setup.seated is not None and setup.seated.lower_body is not None:
        legs = setup.seated.lower_body
        for side in ("r", "l"):
            values.update(
                {
                    f"hip_flexion_{side}": legs.hip_flexion_rad,
                    f"hip_adduction_{side}": -legs.hip_abduction_rad,
                    f"knee_angle_{side}": legs.knee_flexion_rad,
                }
            )
    data.qpos[:] = prescribed_pose(model, values)
    mujoco.mj_forward(model, data)
    frozen = tuple(j.name for j in spec.joints if j.name not in active)
    prescribed = {
        name: float(data.qpos[model.joint(name).qposadr[0]]) for name in frozen
    }
    # Explicit matched legacy diagnostic policy; extra native contacts remain
    # available in unmodified upstream inspection, not silently enabled in IK.
    keep_pairs = {frozenset((p.geomname1, p.geomname2)) for p in reference.pairs}
    for pair in list(spec.pairs):
        if frozenset((pair.geomname1, pair.geomname2)) not in keep_pairs:
            spec.delete(pair)
    keep_geoms = {g.name for g in reference.geoms if g.contype != 0}
    for geom in spec.geoms:
        if geom.name not in keep_geoms:
            geom.contype = geom.conaffinity = 0
    if assembly == "myofullbody_reduced":
        # Body transforms include attachment frames. Replace a framed body's
        # frame with an identity frame on its actual compiled parent when baking.
        right_root = model.body("myoarm_r_root").id
        right_bodies = {right_root}
        for i in range(right_root + 1, model.nbody):
            if int(model.body_parentid[i]) in right_bodies:
                right_bodies.add(i)
        for b in spec.bodies:
            if b.name == "world" or model.body(b.name).id in right_bodies:
                continue
            i = model.body(b.name).id
            parent = int(model.body_parentid[i])
            r = data.xmat[parent].reshape(3, 3)
            if b.frame is not None:
                b.set_frame(spec.body(model.body(parent).name).add_frame())
            b.pos = r.T @ (data.xpos[i] - data.xpos[parent])
            quat = Rotation.from_matrix(r.T @ data.xmat[i].reshape(3, 3)).as_quat()
            b.quat = np.r_[quat[3], quat[:3]]
        for sensor in list(spec.sensors):
            spec.delete(sensor)
        keep_actuators = {a.name for a in reference.actuators}
        keep_tendons = {t.name for t in reference.tendons}
        for actuator in list(spec.actuators):
            if actuator.name not in keep_actuators:
                spec.delete(actuator)
        for tendon in list(spec.tendons):
            if tendon.name not in keep_tendons:
                spec.delete(tendon)
        for equality in list(spec.equalities):
            if equality.name not in {e.name for e in reference.equalities}:
                spec.delete(equality)
        for joint in list(spec.joints):
            if joint.name not in active:
                spec.delete(joint)
        prescribed, frozen = {}, ()
    # Existing support hypothesis stays identical; no new tissue or support model.
    if setup.seated is not None and setup.seated.lower_body is not None:
        radius = setup.seated.lower_body.thigh_envelope_radius_m
        for side in ("r", "l"):
            spec.worldbody.add_geom(
                name=f"approximate_thigh_support_{side}",
                type=mujoco.mjtGeom.mjGEOM_CAPSULE,
                fromto=[
                    *data.body(f"femur_{side}").xpos,
                    *data.body(f"tibia_{side}").xpos,
                ],
                size=[radius, 0, 0],
                rgba=[0.35, 0.42, 0.5, 0.18],
                contype=0,
                conaffinity=0,
            )
    return spec, prescribed, frozen
