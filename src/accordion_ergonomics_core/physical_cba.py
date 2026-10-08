"""Generic closed CBA v1: public structural evidence, explicitly assumed metrics.

H axes: outer treble (+u), down (+v), grille anterior (+n). H origin is
upper outer grille corner. Keyboard B keeps the historical canonical meanings.
No articulation, strap load, left-hand IK or calibrated tissue is implemented.
"""

from dataclasses import asdict, dataclass, replace
from math import isfinite, radians
from typing import Any

import numpy as np
from scipy.spatial.transform import Rotation

from .instrument import BOARD_TO_WORLD, buttons

MODEL = "generic_cba_v1"
LEGACY = "rectangular_v0"


@dataclass(frozen=True)
class RigidTransform:
    translation_m: tuple[float, float, float] = (0, 0, 0)
    rotation_wxyz: tuple[float, float, float, float] = (1, 0, 0, 0)

    def __post_init__(self):
        if len(self.translation_m) != 3 or not all(
            isfinite(x) for x in self.translation_m
        ):
            raise ValueError("Transform requires three finite metres")
        if (
            len(self.rotation_wxyz) != 4
            or not all(isfinite(x) for x in self.rotation_wxyz)
            or abs(sum(x * x for x in self.rotation_wxyz) - 1) > 1e-10
        ):
            raise ValueError("Transform requires a finite unit quaternion")

    @property
    def rotation(self):
        w, x, y, z = self.rotation_wxyz
        return Rotation.from_quat([x, y, z, w]).as_matrix()

    def apply(self, point):
        return np.asarray(self.translation_m) + self.rotation @ np.asarray(point)

    def compose(self, child):
        return transform(
            self.apply(child.translation_m), self.rotation @ child.rotation
        )


def transform(position, rotation):
    q = Rotation.from_matrix(rotation).as_quat()
    return RigidTransform(
        (float(position[0]), float(position[1]), float(position[2])),
        (float(q[3]), float(q[0]), float(q[1]), float(q[2])),
    )


@dataclass(frozen=True)
class BellowsConfiguration:
    """Reference closure plus a PURE hypothetical bass transform for frame tests.

    Nonzero opening is rejected. The hypothetical transform is not a simulated
    bellows configuration, joint, deformation model or supported playing setup.
    """

    opening_m: float = 0.0
    bass_relative: RigidTransform = RigidTransform((-0.25, 0, 0))

    def __post_init__(self):
        if self.opening_m != 0:
            raise ValueError("Only fixed closed bellows are implemented")


@dataclass(frozen=True, init=False)
class GenericCBA:
    version: str = MODEL
    height_m: float = 0.38
    depth_m: float = 0.20
    treble_width_m: float = 0.15
    closed_bellows_width_m: float = 0.10
    bass_width_m: float = 0.11
    case_wall_m: float = 0.006
    treble_board_origin_h_m: tuple[float, float, float] = (0.055, 0.100, -0.165)
    treble_board_angle_rad: float = radians(55)
    treble_board_thickness_m: float = 0.012
    bass_button_radius_m: float = 0.0045
    bass_button_height_m: float = 0.003
    bass_column_spacing_m: float = 0.018
    bass_row_spacing_m: float = 0.012
    bass_shear_m: float = 0.009

    @property
    def fingerboard(self):
        return transform(
            self.treble_board_origin_h_m,
            Rotation.from_euler("y", self.treble_board_angle_rad).as_matrix(),
        )

    @property
    def bass_board(self):
        # L +x forward, +y down, +z outward from bass end (-H.u).
        return transform(
            (-self.bass_width_m - 0.006, 0.045, -0.145),
            np.array([[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]]),
        )

    def bass_buttons(self):
        return tuple(
            (
                f"bass_r{row + 1}c{column + 1}",
                (
                    row * self.bass_row_spacing_m,
                    column * self.bass_column_spacing_m + row * self.bass_shear_m,
                    self.bass_button_height_m,
                ),
            )
            for row in range(6)
            for column in range(16)
        )

    def frames(self, bellows=None):
        bellows = bellows or BellowsConfiguration()
        return {
            "treble": RigidTransform(),
            "fingerboard": self.fingerboard,
            "bass": bellows.bass_relative,
            "bass_fingerboard": bellows.bass_relative.compose(self.bass_board),
        }

    def specification(self):
        return {
            **asdict(self),
            "bass_button_count": 96,
            "bass_layout": "6 x 16 slanted columns; IDs only, no pitch mapping",
            "bellows": asdict(BellowsConfiguration()),
            "metric_evidence": "assumption: docs/research/generic-cba.md",
        }


REFERENCE = GenericCBA()


def validate_keyboard(geometry):
    centers = np.array([geometry.center_board_m(b) for b in buttons()])
    # Fixed representative profile, not a configurator. Prevent unsupported
    # metric patches from silently expanding its board beyond the case.
    low, high = centers.min(axis=0), centers.max(axis=0)
    if not (
        low[0] >= -0.067 and high[0] <= 0 and low[1] >= -0.029 and high[1] <= 0.210
    ):
        raise ValueError("Right-hand fixture exceeds generic CBA usable region")
    if geometry.panel_thickness_m != REFERENCE.treble_board_thickness_m:
        raise ValueError("Generic CBA v1 requires a 12 mm treble board")
    if geometry.button_radius_m > 0.008 or geometry.button_height_m > 0.008:
        raise ValueError("Unsupported generic cap size")
    lateral = centers[:, :2]
    distances = np.linalg.norm(lateral[:, None] - lateral[None, :], axis=2)
    np.fill_diagonal(distances, np.inf)
    if distances.min() <= 2 * geometry.button_radius_m:
        raise ValueError("Generic CBA caps overlap")
    if np.any(low[:2] - geometry.button_radius_m < [-0.078, -0.041]) or np.any(
        high[:2] + geometry.button_radius_m > [0.012, 0.221]
    ):
        raise ValueError("Caps exceed fixed fingerboard bounds")


def derive_physical_setup(geometry, setup):
    """Mount actual rear case walls and bottom edges against generic support planes.

    Reuse anatomical anchor extraction, not the legacy shell placement. Bottom
    and rear extrema come from component corners; shoulder fixes outer board rim.
    """
    import myo_sim

    from ._engine import mujoco
    from .lower_body import lower_body_anchors

    validate_keyboard(geometry)
    p = setup.seated
    if p is None:
        # Explicit world B is allowed for instrument-only diagnostics.
        return geometry, {}
    if p.lower_body is None:
        raise ValueError("Physical seated reference requires MyoSim leg anchors")
    spec = myo_sim.load_spec("myoarm_r")
    spec.body("Full Body").pos = list(setup.torso_origin_m)
    spec.body("Full Body").quat = list(setup.torso_rotation_wxyz)
    m = spec.compile()
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    root = np.asarray(setup.torso_origin_m)
    q = setup.torso_rotation_wxyz
    canonical = Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix() @ np.diag(
        [-1.0, -1.0, 1.0]
    )
    rh = (
        Rotation.from_euler(
            "ZYX", [p.yaw_rad, p.long_axis_tilt_rad, p.fore_aft_tilt_rad]
        ).as_matrix()
        @ BOARD_TO_WORLD
    )
    corners = np.array(
        [(u, v, n) for u in (-0.36, 0) for v in (0, 0.38) for n in (-0.20, 0)]
    )
    board_corners = np.array(
        [
            REFERENCE.fingerboard.apply((u, v, n))
            for u in (-0.078, 0.012)
            for v in (-0.041, 0.221)
            for n in (-0.012, 0.008)
        ]
    )
    fb = REFERENCE.fingerboard
    cheek = np.array(
        [
            fb.apply((u, v, n))
            for u in (-0.078, 0.012)
            for v in (-0.100, 0.280)
            for n in (-0.018, -0.012)
        ]
    )
    points = np.vstack((corners, board_corners, cheek)) @ rh.T
    shoulder = canonical.T @ (d.body("humerus_r").xpos - root)
    origin = np.zeros(3)
    origin[0] = (
        shoulder[0] + p.treble_edge_to_shoulder_m - board_corners.dot(rh.T)[:, 0].max()
    )
    landmarks, thigh = lower_body_anchors(setup)
    support_height = (
        max(
            (canonical.T @ (landmarks[k] - root))[2]
            for k in ("femur_r", "femur_l", "tibia_r", "tibia_l")
        )
        + p.lower_body.thigh_envelope_radius_m
    )
    origin[2] = support_height + p.support_clearance_m - points[:, 2].min()
    # Each imported thorax proxy has its own forward support; compare actual
    # component rear-most points in the common anterior direction.
    n = rh[:, 2]
    supports = []
    for name in ("thorax_coll1", "thorax_coll2", "thorax_coll3"):
        g = m.geom(name)
        position = canonical.T @ (d.geom_xpos[g.id] - root)
        frame = canonical.T @ d.geom_xmat[g.id].reshape(3, 3)
        extent = (
            np.linalg.norm(g.size * (frame.T @ n))
            if name == "thorax_coll1"
            else g.size[0] + g.size[1] * abs(frame[:, 2] @ n)
        )
        supports.append(position @ n + extent)
    rear = np.min(points @ n)
    origin[1] = (
        max(supports) + p.torso_gap_m - rear - origin[0] * n[0] - origin[2] * n[2]
    ) / n[1]
    h_world = transform(root + canonical @ origin, canonical @ rh)
    b_world = h_world.compose(REFERENCE.fingerboard)
    derived = replace(
        geometry, origin_m=b_world.translation_m, rotation_wxyz=b_world.rotation_wxyz
    )
    anchors: dict[str, Any] = {
        "treble_frame_world": asdict(h_world),
        "shell_center_world_m": h_world.apply((-0.18, 0.19, -0.10)).tolist(),
        "shoulder_world_m": d.body("humerus_r").xpos.tolist(),
        "right_thigh_reference_world_m": thigh.tolist(),
        "treble_support_corner_world_m": h_world.apply((0, 0.38, -0.10)).tolist(),
        "lower_body_landmarks_world_m": {k: v.tolist() for k, v in landmarks.items()},
        "support_height_above_root_m": float(support_height),
        "anchor_policy": (
            "Actual rear/bottom extrema; shoulder-relative board rim; "
            "approximate thigh envelopes, no load equilibrium"
        ),
    }
    return derived, anchors


def attach_instrument(spec, geometry, bellows=None):
    """Build fixed component hierarchy. Return B; existing solver adds RH caps."""
    from ._engine import mujoco

    bellows = bellows or BellowsConfiguration()
    validate_keyboard(geometry)
    fb = REFERENCE.fingerboard
    h_rotation = geometry.rotation @ fb.rotation.T
    h_position = np.asarray(geometry.origin_m) - h_rotation @ np.asarray(
        fb.translation_m
    )
    h = transform(h_position, h_rotation)
    root = spec.worldbody.add_body(
        name=MODEL, pos=list(h.translation_m), quat=list(h.rotation_wxyz)
    )
    treble = root.add_body(name="treble_assembly")
    board = treble.add_body(
        name="keyboard", pos=list(fb.translation_m), quat=list(fb.rotation_wxyz)
    )
    bass_transform = bellows.bass_relative
    bass = root.add_body(
        name="bass_assembly",
        pos=list(bass_transform.translation_m),
        quat=list(bass_transform.rotation_wxyz),
    )
    connection = root.add_body(
        name="closed_bellows_connection", pos=[-0.20, 0.19, -0.10]
    )

    def box(body, name, pos, size, color, solid=True):
        return body.add_geom(
            name=name,
            type=mujoco.mjtGeom.mjGEOM_BOX,
            pos=list(pos),
            size=list(size),
            rgba=color,
            contype=2 if solid else 0,
            conaffinity=1 if solid else 0,
            group=2,
        )

    def case(body, prefix, width):
        # Hollow six-wall enclosure: no artificial filled global case volume.
        w, h, dep, t = (
            width,
            REFERENCE.height_m,
            REFERENCE.depth_m,
            REFERENCE.case_wall_m,
        )
        color = [0.25, 0.32, 0.40, 1] if prefix == "treble" else [0.30, 0.37, 0.45, 1]
        for label, pos, size in (
            ("rear", (-w / 2, h / 2, -dep + t / 2), (w / 2, h / 2, t / 2)),
            ("grille", (-w / 2, h / 2, -t / 2), (w / 2, h / 2, t / 2)),
            ("outer", (-t / 2, h / 2, -dep / 2), (t / 2, h / 2, dep / 2 - t)),
            ("inner", (-w + t / 2, h / 2, -dep / 2), (t / 2, h / 2, dep / 2 - t)),
            ("top", (-w / 2, t / 2, -dep / 2), (w / 2 - t, t / 2, dep / 2 - t)),
            ("bottom", (-w / 2, h - t / 2, -dep / 2), (w / 2 - t, t / 2, dep / 2 - t)),
        ):
            if prefix == "treble" and label == "outer":
                continue  # replaced by the rear-adjacent shaped cheek below
            if prefix == "treble" and label in ("top", "bottom"):
                pos = ((-w + t) / 2, pos[1], pos[2])
                size = ((w - t) / 2, size[1], size[2])
            box(body, f"cba_{prefix}_{label}", pos, size, color)

    case(treble, "treble", 0.15)
    case(bass, "bass", 0.11)
    box(
        board,
        "keyboard_panel",
        (-0.033, 0.090, -0.006),
        (0.045, 0.131, 0.006),
        [0.12, 0.19, 0.26, 1],
    )
    # Rear-adjacent keyboard aperture in the outer treble cheek. The angled
    # backing, front shoulder and rear return enclose an actual case extension;
    # the keyboard is not a plate on a block at the grille corner.
    color = [0.25, 0.32, 0.40, 1]
    inner = fb.apply((-0.078, 0, -0.012))
    outer = fb.apply((0.012, 0, -0.012))
    inner[1] = outer[1] = 0.0  # cross-section, not B origin height
    for label, a, b in (
        ("shoulder", np.array([0.0, 0.0, 0.0]), inner),
        ("rear_return", outer, np.array([0.0, 0.0, -0.20])),
    ):
        delta = b - a
        length = np.linalg.norm(delta)
        normal = np.array([-delta[2], 0.0, delta[0]]) / length
        direction = delta / length
        # Choose an inward displacement relative to the enclosure interior.
        if normal[0] > 0:
            normal = -normal
        rotation = np.column_stack(
            (direction, [0.0, 1.0, 0.0], np.cross(direction, [0.0, 1.0, 0.0]))
        )
        q = transform((a + b) / 2 + normal * 0.003 + [0, 0.19, 0], rotation)
        wall = box(
            treble,
            "cba_treble_" + label,
            q.translation_m,
            (length / 2, 0.19, 0.003),
            color,
        )
        wall.quat = list(q.rotation_wxyz)
    box(
        board, "cba_treble_mount", (-0.033, 0.090, -0.015), (0.045, 0.190, 0.003), color
    )
    # Full-height cheek backing; close the top/bottom of the external wing
    # with convex triangle meshes made in MuJoCo itself, not a CAD dependency.
    # Main rectangular end walls already close u<=0.
    wing = [(0.0, inner[2]), (inner[0], inner[2]), (outer[0], outer[2]), (0.0, -0.20)]
    for label, v in (("wing_top", 0.0), ("wing_bottom", 0.374)):
        vertices = [[u, y, n] for y in (v, v + 0.006) for u, n in wing]
        spec.add_mesh(name=label, uservert=np.asarray(vertices).ravel().tolist())
        treble.add_geom(
            name="cba_treble_" + label,
            type=mujoco.mjtGeom.mjGEOM_MESH,
            meshname=label,
            rgba=color,
            contype=2,
            conaffinity=1,
            group=2,
        )
    # Edge guards stay below released caps. No rim across the usable lattice.
    for name, pos, size in (
        ("outer_rim", (0.014, 0.090, -0.005), (0.002, 0.131, 0.007)),
        ("inner_rim", (-0.080, 0.090, -0.005), (0.002, 0.131, 0.007)),
    ):
        box(board, "cba_" + name, pos, size, [0.42, 0.48, 0.53, 1])
    # Bellows envelope: four walls, hollow interior; no fake case bridging boards.
    for name, pos, size in (
        ("front", (0, 0, 0.094), (0.05, 0.19, 0.006)),
        ("rear", (0, 0, -0.094), (0.05, 0.19, 0.006)),
        ("top", (0, -0.184, 0), (0.05, 0.006, 0.088)),
        ("bottom", (0, 0.184, 0), (0.05, 0.006, 0.088)),
    ):
        box(connection, "cba_bellows_" + name, pos, size, [0.43, 0.24, 0.23, 1])
    # Fold ribs are visual only; envelope above is the collision hypothesis.
    for i in range(13):
        box(
            connection,
            f"bellows_visual_rib_{i}",
            (-0.048 + i * 0.008, 0, 0.1005),
            (0.001, 0.19, 0.0005),
            [0.65, 0.58, 0.48, 1],
            False,
        )
    bf = REFERENCE.bass_board
    lb = bass.add_body(
        name="bass_fingerboard", pos=list(bf.translation_m), quat=list(bf.rotation_wxyz)
    )
    box(
        lb,
        "cba_bass_panel",
        (0.030, 0.1575, -0.004),
        (0.046, 0.1745, 0.004),
        [0.12, 0.19, 0.26, 1],
    )
    for name, position in REFERENCE.bass_buttons():
        lb.add_geom(
            name=name,
            type=mujoco.mjtGeom.mjGEOM_CYLINDER,
            pos=[position[0], position[1], 0.0015],
            size=[0.0045, 0.0015, 0],
            rgba=[0.88, 0.89, 0.83, 1],
            contype=2,
            conaffinity=1,
            group=2,
        )
        lb.add_site(
            name="target_" + name, pos=list(position), size=[0.001, 0, 0], group=5
        )
    for body, name, position in (
        (treble, "shoulder_strap_upper", (-0.025, 0.010, -0.15)),
        (treble, "shoulder_strap_lower", (-0.025, 0.370, -0.15)),
        (bass, "bass_strap_upper", (-0.11, 0.015, -0.175)),
        (bass, "bass_strap_lower", (-0.11, 0.365, -0.175)),
    ):
        body.add_site(
            name=name,
            pos=list(position),
            size=[0.004, 0, 0],
            rgba=[1, 0.65, 0.1, 1],
            group=0,
        )
    box(
        bass,
        "bass_strap_visual",
        (-0.15, 0.19, -0.175),
        (0.002, 0.175, 0.012),
        [0.55, 0.40, 0.21, 1],
        False,
    )
    return board
