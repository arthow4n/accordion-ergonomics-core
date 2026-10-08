"""MyoArm composition, exact source couplings, and model-derived contact marker."""

from dataclasses import dataclass
from typing import Any

import myo_sim
import numpy as np
from numpy.typing import NDArray

from ._engine import Data, Model, Spec, mujoco
from .instrument import BoardGeometry, buttons
from .profiles import ContactProfile, PlayerProfile, SetupProfile


@dataclass
class Scene:
    model: Model
    data: Data
    anatomy_geoms: list[int]
    board_geoms: list[int]
    pad_local_m: list[float]
    contact_profile: ContactProfile


def build_scene(
    geometry: BoardGeometry,
    player: PlayerProfile | None = None,
    setup: SetupProfile | None = None,
    contact: ContactProfile | None = None,
) -> Scene:
    player = player or PlayerProfile()
    setup = setup or SetupProfile()
    contact = contact or ContactProfile()
    spec: Spec = myo_sim.load_spec("myoarm_r")
    root = spec.body("Full Body")
    if root is None:
        raise ValueError("Pinned anatomical model has no expected torso scaffold")
    root.quat = list(setup.torso_rotation_wxyz)
    root.pos = list(setup.torso_origin_m)
    for name, bounds in player.joint_ranges_rad.items():
        joint = spec.joint(name)
        if joint is None:
            raise ValueError(f"Unknown joint override: {name}")
        joint.range = list(bounds)
    # Distal surface support of imported geometry; no invented finger length.
    geom = spec.geom("distph2_coll_r")
    finger = spec.body("distph2_r")
    if geom is None or finger is None:
        raise ValueError("Pinned anatomical index collision geometry is absent")
    # MjSpec Euler orientation is resolved only at compile time.
    probe = spec.compile()
    compiled_geom = probe.geom("distph2_coll_r")
    matrix = np.zeros(9)
    mujoco.mju_quat2Mat(matrix, compiled_geom.quat)
    axis = matrix.reshape(3, 3)[:, 2]
    # The capsule +z axis points distally in the source phalanx frame.
    # Use its distal hemispherical pole, not the volar cylinder support.
    normal = axis
    point = (
        compiled_geom.pos
        + compiled_geom.size[1] * np.sign(normal @ axis) * axis
        + compiled_geom.size[0] * normal
    )
    # The source also has an ellipsoid that extends beyond the capsule.
    # Contact must be on the outer envelope of BOTH distal collision proxies.
    ellipse = probe.geom("distph2_coll_2_r")
    ellipse_matrix = np.zeros(9)
    mujoco.mju_quat2Mat(ellipse_matrix, ellipse.quat)
    rotation = ellipse_matrix.reshape(3, 3)
    shape = rotation @ np.diag(ellipse.size**2) @ rotation.T
    ellipse_point = ellipse.pos + shape @ normal / np.sqrt(normal @ shape @ normal)
    if normal @ ellipse_point > normal @ point:
        point = ellipse_point
    finger.add_site(
        name="index_pad",
        pos=point.tolist(),
        quat=compiled_geom.quat.tolist(),
        size=[0.0015, 0, 0],
        rgba=[0.1, 1.0, 0.2, 1.0],
        group=0,
    )
    # Remove the upstream decorative room; it is unrelated to body geometry.
    for decor in list(spec.worldbody.geoms):
        spec.delete(decor)
    board = spec.worldbody.add_body(
        name="keyboard",
        pos=list(geometry.origin_m),
        quat=list(geometry.rotation_wxyz),
    )
    centers = np.array([geometry.center_board_m(b) for b in buttons()])
    low, high = centers.min(axis=0), centers.max(axis=0)
    center = (low + high) / 2
    board.add_geom(
        name="keyboard_panel",
        type=mujoco.mjtGeom.mjGEOM_BOX,
        pos=[center[0], center[1], -geometry.panel_thickness_m / 2],
        size=[
            (high[0] - low[0]) / 2 + geometry.panel_margin_m,
            (high[1] - low[1]) / 2 + geometry.panel_margin_m,
            geometry.panel_thickness_m / 2,
        ],
        rgba=[0.12, 0.17, 0.23, 1],
        contype=2,
        conaffinity=1,
    )
    for button, position in zip(buttons(), centers, strict=True):
        black = button.midi % 12 in (1, 3, 6, 8, 10)
        color = [0.16, 0.17, 0.19, 1] if black else [0.92, 0.92, 0.86, 1]
        board.add_geom(
            name=button.id,
            type=mujoco.mjtGeom.mjGEOM_CYLINDER,
            pos=[position[0], position[1], geometry.button_height_m / 2],
            size=[geometry.button_radius_m, geometry.button_height_m / 2, 0],
            rgba=color,
            contype=2,
            conaffinity=1,
        )
        board.add_site(
            name=f"target_{button.id}",
            pos=position.tolist(),
            size=[0.001, 0, 0],
            rgba=[1, 0.5, 0, 1],
            group=5,
        )
    # Frame markers: red +u (outer), green +v (high pitch/down), blue +n.
    for name, endpoint, color in (
        ("axis_u", [0.05, 0, 0.006], [1, 0.2, 0.2, 1]),
        ("axis_v", [0, 0.05, 0.006], [0.2, 1, 0.2, 1]),
        ("axis_n", [0, 0, 0.056], [0.2, 0.5, 1, 1]),
    ):
        board.add_site(
            name=name,
            type=mujoco.mjtGeom.mjGEOM_CAPSULE,
            fromto=[0, 0, 0.006, *endpoint],
            size=[0.001, 0, 0],
            rgba=color,
            group=0,
        )
    spec.visual.global_.offwidth = 960
    spec.visual.global_.offheight = 720
    spec.worldbody.add_light(pos=[0.7, 0.8, 2.5], dir=[-0.4, -0.4, -1])
    model = spec.compile()
    model.opt.jacobian = mujoco.mjtJacobian.mjJAC_DENSE
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    board_geoms = [model.geom("keyboard_panel").id] + [
        model.geom(b.id).id for b in buttons()
    ]
    anatomy_geoms = [
        i
        for i in range(model.ngeom)
        if i not in board_geoms and model.geom_contype[i] != 0
    ]
    return Scene(model, data, anatomy_geoms, board_geoms, point.tolist(), contact)


def coupled_initial_pose(model: Model, values: dict[str, float]) -> NDArray[np.float64]:
    """Apply source polynomial constraints exactly, not as guessed joint limits."""
    q = model.qpos0.copy()
    for name, value in values.items():
        q[model.joint(name).qposadr[0]] = value
    for i in range(model.neq):
        if model.eq_type[i] != mujoco.mjtEq.mjEQ_JOINT:
            raise ValueError("This prototype only initializes scalar joint equalities")
        j1, j2 = int(model.eq_obj1id[i]), int(model.eq_obj2id[i])
        a1, a2 = model.jnt_qposadr[j1], model.jnt_qposadr[j2]
        delta = q[a2] - model.qpos0[a2]
        q[a1] = model.qpos0[a1] + np.polynomial.polynomial.polyval(
            delta, model.eq_data[i, :5]
        )
    if np.any(q < model.jnt_range[:, 0] - 1e-9) or np.any(
        q > model.jnt_range[:, 1] + 1e-9
    ):
        raise ValueError("Initial pose violates imported joint limits")
    return q


def diagnostics(
    scene: Scene, target: NDArray[np.float64], button_id: str = "r1c5"
) -> dict[str, Any]:
    model, data = scene.model, scene.data
    mujoco.mj_forward(model, data)
    equality_mask = data.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY
    equalities = data.efc_pos[equality_mask]
    normal = data.site("index_pad").xmat.reshape(3, 3)[:, 2]
    margins = np.minimum(
        data.qpos - model.jnt_range[:, 0], model.jnt_range[:, 1] - data.qpos
    )
    contacts = []
    for contact in data.contact:
        contacts.append(
            {
                "geom1": model.geom(int(contact.geom1)).name,
                "geom2": model.geom(int(contact.geom2)).name,
                "distance_m": float(contact.dist),
                "position_world_m": contact.pos.tolist(),
            }
        )
    target_geom = model.geom(button_id).id
    contact_distance = min(
        mujoco.mj_geomDistance(model, data, model.geom(name).id, target_geom, 1.0, None)
        for name in ("distph2_coll_r", "distph2_coll_2_r")
    )
    return {
        "target_contact_distance_m": float(contact_distance),
        "position_error_m": float(np.linalg.norm(data.site("index_pad").xpos - target)),
        "normal_error_rad": float(
            np.arccos(
                np.clip(normal @ -data.body("keyboard").xmat.reshape(3, 3)[:, 2], -1, 1)
            )
        ),
        "equality_max_residual_rad": float(np.max(np.abs(equalities), initial=0)),
        "joint_max_violation_rad": float(max(0, -margins.min())),
        "joint_margins_rad": {
            model.joint(i).name: float(margins[i]) for i in range(model.njnt)
        },
        "contacts": contacts,
        "max_penetration_m": max([0.0] + [-c["distance_m"] for c in contacts]),
        "pad_world_m": data.site("index_pad").xpos.tolist(),
        "pad_normal_world": normal.tolist(),
        "palm_world_m": data.body("capitate_r").xpos.tolist(),
    }
