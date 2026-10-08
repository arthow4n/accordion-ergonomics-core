"""Calibration boundaries without claiming physiological personalization."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class PlayerProfile:
    model: str = "myoarm_r"
    joint_ranges_rad: dict[str, tuple[float, float]] = field(default_factory=dict)
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "imported_model",
            "source": "myo-sim 0.2.3",
            "note": "Unscaled imported geometry; no player-specific validation.",
        }
    )

    def __post_init__(self) -> None:
        if self.model != "myoarm_r":
            raise ValueError("Unsupported anatomy")
        for bounds in self.joint_ranges_rad.values():
            if (
                len(bounds) != 2
                or not all(isfinite(v) for v in bounds)
                or bounds[0] >= bounds[1]
            ):
                raise ValueError(
                    "Joint overrides require increasing finite radian bounds"
                )


@dataclass(frozen=True)
class SetupProfile:
    torso_origin_m: tuple[float, float, float] = (0, 0, 1)
    torso_rotation_wxyz: tuple[float, float, float, float] = (0, 0, 0, 1)
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "assumption",
            "source": "Legacy laboratory setup",
            "note": "Fixed torso scaffold; no straps or instrument body.",
        }
    )

    def __post_init__(self) -> None:
        if len(self.torso_origin_m) != 3 or not all(
            isfinite(v) for v in self.torso_origin_m
        ):
            raise ValueError("Torso origin requires finite metres")
        if (
            len(self.torso_rotation_wxyz) != 4
            or not all(isfinite(v) for v in self.torso_rotation_wxyz)
            or abs(sum(v * v for v in self.torso_rotation_wxyz) - 1) > 1e-10
        ):
            raise ValueError("Torso rotation requires unit quaternion")


@dataclass(frozen=True)
class ContactProfile:
    collision_detection_distance_m: float = 0.03
    collision_minimum_distance_m: float = 0.0
    collision_gain: float = 0.85
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "assumption",
            "source": "Laboratory contact policy",
            "note": "Rigid imported distal envelope; no deformation, force or travel.",
        }
    )

    def __post_init__(self) -> None:
        values = (
            self.collision_detection_distance_m,
            self.collision_minimum_distance_m,
            self.collision_gain,
        )
        if (
            not all(isfinite(v) for v in values)
            or self.collision_detection_distance_m <= 0
            or self.collision_minimum_distance_m < 0
            or not 0 < self.collision_gain <= 1
        ):
            raise ValueError("Invalid collision policy")
