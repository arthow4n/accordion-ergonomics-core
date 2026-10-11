"""Controlled kinematic geometry perturbations without physiological claims."""

import numpy as np

from ._engine import Model, Spec, mujoco
from .digits import DIGITS as DIGITS
from .digits import DISTAL_BINDINGS as DISTAL_BINDINGS
from .profiles import PlayerProfile


def transform_anatomy(spec: Spec, player: PlayerProfile) -> None:
    """Uniformly transform hand geometry about the imported wrist origin.

    Actuators/tendons are removed in hypothesis mode: retaining their parameters
    after a geometric transform would silently imply physiological validity.
    """
    if player.model_mode == "imported_musculoskeletal":
        return
    probe = spec.compile()
    root = probe.body("lunate_r").id
    selected = {root}
    for i in range(root + 1, probe.nbody):
        if int(probe.body_parentid[i]) in selected:
            selected.add(i)
    scale = player.geometric_hand_scale
    mesh_names = set()
    for i in selected:
        body = spec.body(probe.body(i).name)
        if body.frame is not None or list(body.frames):
            raise ValueError("Hand transform requires explicit body frames")
        if i == root and any(np.linalg.norm(j.pos) > 1e-12 for j in body.joints):
            raise ValueError("Imported wrist origin is not the joint anchor")
        for geom in body.geoms:
            if geom.meshname:
                mesh_names.add(geom.meshname)
    for geom in spec.geoms:
        if (
            geom.meshname in mesh_names
            and int(probe.geom(geom.name).bodyid[0]) not in selected
        ):
            raise ValueError("Hand transform cannot alter a shared outside mesh")
    for i in selected:
        body = spec.body(probe.body(i).name)
        if i != root:
            body.pos = np.array(body.pos) * scale
        body.ipos = np.array(body.ipos) * scale
        body.mass *= scale**3
        body.inertia = np.array(body.inertia) * scale**5
        body.fullinertia = np.array(body.fullinertia) * scale**5
        for joint in body.joints:
            joint.pos = np.array(joint.pos) * scale
        for site in body.sites:
            site.pos = np.array(site.pos) * scale
            site.size = np.array(site.size) * scale
            site.fromto = np.array(site.fromto) * scale
        for geom in body.geoms:
            geom.pos = np.array(geom.pos) * scale
            geom.fromto = np.array(geom.fromto) * scale
            if geom.type != mujoco.mjtGeom.mjGEOM_MESH:
                geom.size = np.array(geom.size) * scale
    for name in mesh_names:
        mesh = spec.mesh(name)
        mesh.scale = np.array(mesh.scale) * scale
        mesh.refpos = np.array(mesh.refpos) * scale
    for actuator in list(spec.actuators):
        spec.delete(actuator)
    for tendon in list(spec.tendons):
        spec.delete(tendon)


def digit_dofs(model: Model) -> dict[str, tuple[int, ...]]:
    """Bind anatomical digits by imported body subtrees, not coordinate indices."""
    roots = {
        "thumb": "firstmc_r",
        "index": "secondmc_r",
        "middle": "thirdmc_r",
        "ring": "fourthmc_r",
        "little": "fifthmc_r",
    }
    result = {}
    for digit, name in roots.items():
        root = model.body(name).id
        bodies = {root}
        for i in range(root + 1, model.nbody):
            if int(model.body_parentid[i]) in bodies:
                bodies.add(i)
        result[digit] = tuple(
            int(model.jnt_dofadr[j])
            for j in range(model.njnt)
            if int(model.jnt_bodyid[j]) in bodies
        )
        if len(result[digit]) != 4:
            raise ValueError("Pinned digit anatomy has unexpected coordinates")
    return result


def distal_support(model: Model, digit: str) -> tuple[np.ndarray, np.ndarray]:
    """Support of the compiled capsule/ellipsoid union along its distal axis.

    Thumb's imported capsule is oriented proximally (+z); reverse that axis.
    This is a rigid proxy hypothesis, not a calibrated fleshy contact patch.
    """
    _, capsule_name, ellipse_name, direction = DISTAL_BINDINGS[digit]
    capsule, ellipse = model.geom(capsule_name), model.geom(ellipse_name)
    matrix = np.zeros(9)
    mujoco.mju_quat2Mat(matrix, capsule.quat)
    normal = direction * matrix.reshape(3, 3)[:, 2]
    point = capsule.pos + (capsule.size[1] + capsule.size[0]) * normal
    mujoco.mju_quat2Mat(matrix, ellipse.quat)
    rotation = matrix.reshape(3, 3)
    shape = rotation @ np.diag(ellipse.size**2) @ rotation.T
    alternative = ellipse.pos + shape @ normal / np.sqrt(normal @ shape @ normal)
    if normal @ alternative > normal @ point:
        point = alternative
    quat = capsule.quat.copy()
    if direction == -1:
        reversed_quat = np.zeros(4)
        mujoco.mju_mulQuat(reversed_quat, quat, np.array([0.0, 1.0, 0.0, 0.0]))
        quat = reversed_quat
    return point, quat
