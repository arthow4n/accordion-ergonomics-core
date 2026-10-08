"""Controlled kinematic geometry perturbations without physiological claims."""

import numpy as np

from ._engine import Spec, mujoco
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
