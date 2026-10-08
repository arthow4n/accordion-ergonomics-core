"""Body-anchored setup hypotheses; manufacturer scale is not shell calibration."""

from dataclasses import asdict, dataclass, field, replace
from math import isfinite, pi
from typing import Any

import numpy as np
from scipy.spatial.transform import Rotation

from .instrument import BOARD_TO_WORLD, BoardGeometry, buttons
from .lower_body import SeatedLegs, lower_body_anchors


def parameter_evidence() -> dict[str, Any]:
    """Ranges are broad modeling hypotheses, never measured population bounds."""
    roland = "https://www.roland.com/uk/products/fr-1xb/"
    teaching = "https://www.gorkahermosa.com/web/img/publicaciones/3568a.pdf#page=4"
    ranges = {
        "torso_gap_m": (0.0, 0.04),
        "treble_edge_to_shoulder_m": (-0.03, 0.03),
        "support_height_above_root_m": (0.07, 0.13),
        "support_clearance_m": (0.0, 0.04),
        "c4_top_inset_m": (0.045, 0.095),
        "outer_edge_inset_m": (0.01, 0.025),
        "yaw_rad": (-pi / 4, 0.0),
        "long_axis_tilt_rad": (-pi / 18, pi / 18),
        "fore_aft_tilt_rad": (-pi / 18, pi / 18),
    }
    evidence = {
        name: {
            "kind": "assumption",
            "qualitative_source": teaching,
            "range": bounds,
            "range_source": "Generic setup hypothesis, 023",
            "uncertainty": "Not a measured interval or population coverage estimate",
            "rationale": "docs/research/seated-setup.md#parameter-family",
        }
        for name, bounds in ranges.items()
    }
    for dimension in ("width", "depth", "height"):
        evidence[f"instrument_{dimension}_m"] = {
            "kind": "manufacturer",
            "source": roland,
            "uncertainty": "Catalogue size; tolerance and reference surfaces unknown",
            "rationale": "Overall size sets scale; box shape is a separate hypothesis",
        }
    return evidence


@dataclass(frozen=True)
class SeatedSetup:
    lower_body: SeatedLegs | None = field(default_factory=SeatedLegs)
    name: str = "reference_seated_cba_setup"
    instrument_width_m: float = 0.365
    instrument_depth_m: float = 0.195
    instrument_height_m: float = 0.380
    torso_gap_m: float = 0.01
    treble_edge_to_shoulder_m: float = 0.0
    support_height_above_root_m: float = 0.10
    support_clearance_m: float = 0.01
    c4_top_inset_m: float = 0.06
    outer_edge_inset_m: float = 0.015
    yaw_rad: float = -pi / 6
    long_axis_tilt_rad: float = 0.0
    fore_aft_tilt_rad: float = 0.0
    evidence: str = "docs/research/seated-setup.md"
    parameter_evidence: dict[str, Any] = field(default_factory=parameter_evidence)

    def __post_init__(self) -> None:
        if isinstance(self.lower_body, dict):
            object.__setattr__(self, "lower_body", SeatedLegs(**self.lower_body))
        for name, value in asdict(self).items():
            if isinstance(value, (int, float)) and not isfinite(value):
                raise ValueError(f"Nonfinite seated setup parameter: {name}")
        for name in ("instrument_width_m", "instrument_depth_m", "instrument_height_m"):
            if getattr(self, name) <= 0:
                raise ValueError("Instrument envelope dimensions must be positive")
        if self.torso_gap_m < 0 or self.support_clearance_m < 0:
            raise ValueError("Support clearances must be nonnegative")
        if not 0 < self.c4_top_inset_m < self.instrument_height_m:
            raise ValueError("C4 must lie within instrument height")
        if not 0 <= self.outer_edge_inset_m < self.instrument_width_m:
            raise ValueError("Board inset must lie within instrument width")
        if (
            max(
                abs(self.yaw_rad),
                abs(self.long_axis_tilt_rad),
                abs(self.fore_aft_tilt_rad),
            )
            > pi / 3
        ):
            raise ValueError("Setup angles outside supported upright abstraction")


def derive_setup(
    geometry: BoardGeometry, setup: Any
) -> tuple[BoardGeometry, dict[str, Any]]:
    """Resolve from compiled imported torso, shell scale and seated support plane.

    The thorax ellipsoid support plane is deliberately conservative. It prevents
    shell/torso overlap without pretending the rear case matches the chest shape.
    MyoSim femurs anchor approximate envelopes in new setups; legacy thighs
    remain schematic. Neither support forces nor straps are simulated.
    """
    import myo_sim

    from ._engine import mujoco

    p = setup.seated
    if p is None:
        return geometry, {}
    spec = myo_sim.load_spec("myoarm_r")
    spec.body("Full Body").pos = list(setup.torso_origin_m)
    spec.body("Full Body").quat = list(setup.torso_rotation_wxyz)
    model = spec.compile()
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    root = np.asarray(setup.torso_origin_m)
    q = setup.torso_rotation_wxyz
    canonical = Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix() @ np.diag(
        [-1.0, -1.0, 1.0]
    )
    shoulder = canonical.T @ (data.body("humerus_r").xpos - root)
    orientation = (
        Rotation.from_euler(
            "ZYX", [p.yaw_rad, p.long_axis_tilt_rad, p.fore_aft_tilt_rad]
        ).as_matrix()
        @ BOARD_TO_WORLD
    )
    n = orientation[:, 2]
    size = np.array([p.instrument_width_m, p.instrument_height_m, p.instrument_depth_m])
    # x fixes the right outer edge relative to the imported right shoulder.
    center = np.zeros(3)
    center[0] = (
        shoulder[0]
        + p.treble_edge_to_shoulder_m
        - (
            orientation
            @ np.array(
                [
                    size[0] / 2 - p.outer_edge_inset_m,
                    -size[1] / 2 + p.c4_top_inset_m,
                    size[2] / 2,
                ]
            )
        )[0]
    )
    lower_landmarks = None
    anatomical_reference = None
    support_height = p.support_height_above_root_m
    if p.lower_body is not None:
        lower_landmarks, anatomical_reference = lower_body_anchors(setup)
        leg_parameters = p.lower_body
        support_height = (
            max(
                (canonical.T @ (lower_landmarks[name] - root))[2]
                for name in ("femur_r", "femur_l", "tibia_r", "tibia_l")
            )
            + leg_parameters.thigh_envelope_radius_m
        )
    center[2] = (
        support_height + p.support_clearance_m + np.abs(orientation[2]) @ (size / 2)
    )
    support_values = []
    thorax_center = np.zeros(3)
    for name in ("thorax_coll1", "thorax_coll2", "thorax_coll3"):
        thorax = model.geom(name)
        position = canonical.T @ (data.geom_xpos[thorax.id] - root)
        frame = canonical.T @ data.geom_xmat[thorax.id].reshape(3, 3)
        if name == "thorax_coll1":
            thorax_center = position
            extent = np.linalg.norm(thorax.size * (frame.T @ n))
        else:
            extent = thorax.size[0] + thorax.size[1] * abs(frame[:, 2] @ n)
        support_values.append(position @ n + extent)
    support = max(support_values)
    center[1] = (
        support + p.torso_gap_m + size[2] / 2 - center[0] * n[0] - center[2] * n[2]
    ) / n[1]
    local_origin = np.array(
        [
            size[0] / 2 - p.outer_edge_inset_m,
            -size[1] / 2 + p.c4_top_inset_m,
            size[2] / 2,
        ]
    )
    rotation = canonical @ orientation
    origin = root + canonical @ (center + orientation @ local_origin)
    quat = Rotation.from_matrix(rotation).as_quat()
    derived = replace(
        geometry,
        origin_m=tuple(origin),
        rotation_wxyz=(float(quat[3]), *map(float, quat[:3])),
    )
    centers = np.array([geometry.center_board_m(b) for b in buttons()])
    if (
        centers[:, 1].max() + p.c4_top_inset_m + geometry.panel_margin_m > size[1]
        or -centers[:, 1].min() + geometry.panel_margin_m > p.c4_top_inset_m
    ):
        raise ValueError("Keyboard fixture exceeds instrument height")
    board_width = -centers[:, 0].min() + geometry.panel_margin_m
    support_corner = center + orientation @ np.array(
        [size[0] / 2 - p.outer_edge_inset_m - board_width, size[1] / 2, 0.0]
    )
    thigh_reference = np.array(
        [shoulder[0] - 0.07, support_corner[1], p.support_height_above_root_m]
    )
    if anatomical_reference is not None:
        thigh_reference = canonical.T @ (anatomical_reference - root)
    anchors = {
        "shell_center_board_m": (-local_origin).tolist(),
        "shell_half_size_m": (size / 2).tolist(),
        "shell_center_world_m": (root + canonical @ center).tolist(),
        "shoulder_world_m": data.body("humerus_r").xpos.tolist(),
        "torso_reference_world_m": (root + canonical @ thorax_center).tolist(),
        "right_thigh_reference_world_m": (root + canonical @ thigh_reference).tolist(),
        "treble_support_corner_world_m": (root + canonical @ support_corner).tolist(),
        "support_reference_separation_m": float(
            np.linalg.norm(support_corner - thigh_reference)
        ),
        "rear_thorax_support_plane_gap_m": p.torso_gap_m,
        "shell_bottom_above_support_m": p.support_clearance_m,
        "anchor_policy": (
            "Thorax support plane; shoulder-relative treble edge; "
            "pelvis-relative thigh-height plane. "
            "No force equilibrium or rigid thigh pin."
        ),
    }

    if lower_landmarks is not None:
        anchors["lower_body_landmarks_world_m"] = {
            k: v.tolist() for k, v in lower_landmarks.items()
        }
        anchors["anchor_policy"] = (
            "Compiled MyoSim seated FK; approximate thigh-envelope station, "
            "independent of instrument; thorax plane and shoulder edge. "
            "No support forces."
        )
        anchors["support_height_above_root_m"] = float(support_height)
    return derived, anchors
