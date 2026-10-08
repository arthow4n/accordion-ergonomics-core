"""Calibration boundaries without claiming physiological personalization."""

from dataclasses import dataclass, field
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class PlayerProfile:
    model: str = "myoarm_r"
    model_mode: str = "imported_musculoskeletal"
    geometric_hand_scale: float = 1.0
    geometry_evidence: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "hypothesis",
            "source": "Wrist-origin geometric perturbation",
            "note": "Uniform hand scaling is not physiological personalization.",
            "uncertainty": None,
        }
    )
    joint_ranges_rad: dict[str, tuple[float, float]] = field(default_factory=dict)
    provenance: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "imported_model",
            "source": "myo-sim 0.2.3",
            "note": "Unscaled imported geometry; no player-specific validation.",
        }
    )

    joint_range_evidence: dict[str, dict[str, Any]] = field(default_factory=dict)
    uncertainty: str = (
        "Imported dimensions and ranges lack player-specific uncertainty estimates"
    )

    def __post_init__(self) -> None:
        if self.model_mode not in (
            "imported_musculoskeletal",
            "kinematic_geometry_hypothesis",
        ):
            raise ValueError("Unsupported anatomical model mode")
        if not isfinite(self.geometric_hand_scale) or self.geometric_hand_scale <= 0:
            raise ValueError("Geometric hand scale must be finite and positive")
        if (
            self.model_mode == "imported_musculoskeletal"
            and self.geometric_hand_scale != 1
        ):
            raise ValueError(
                "Scaling requires explicit kinematic geometry hypothesis mode"
            )
        unknown = set(self.joint_range_evidence) - set(self.joint_ranges_rad)
        if unknown:
            raise ValueError("Range evidence has no corresponding override")
        evidence = dict(self.joint_range_evidence)
        for name in self.joint_ranges_rad:
            evidence.setdefault(
                name,
                {
                    "kind": "assumption",
                    "source": "Profile override",
                    "note": "Unvalidated range replacement",
                    "uncertainty_rad": None,
                },
            )
        object.__setattr__(self, "joint_range_evidence", evidence)
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
    additional_collision_pairs: tuple[tuple[str, str], ...] = ()
    additional_collision_evidence: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "hypothesis",
            "source": "Explicit imported-proxy constraint",
            "note": "Pair nonpenetration is not calibrated tissue clearance.",
        }
    )
    inactive_digits_policy: str = "freeze"
    inactive_digits_evidence: dict[str, Any] = field(
        default_factory=lambda: {
            "kind": "assumption",
            "source": "Laboratory movement restriction",
            "note": "Unrequested digits freeze by default; a laboratory restriction.",
        }
    )
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
        pairs = []
        for pair in self.additional_collision_pairs:
            if (
                len(pair) != 2
                or not all(isinstance(n, str) and n for n in pair)
                or pair[0] == pair[1]
            ):
                raise ValueError("Collision pairs require two distinct named proxies")
            pairs.append((min(pair), max(pair)))
        if len(set(pairs)) != len(pairs):
            raise ValueError("Additional collision pairs must be unique")
        object.__setattr__(self, "additional_collision_pairs", tuple(sorted(pairs)))
        if self.inactive_digits_policy not in ("freeze", "allow_articulation"):
            raise ValueError("Unsupported inactive digit policy")
        values = (
            self.collision_detection_distance_m,
            self.collision_minimum_distance_m,
            self.collision_gain,
        )
        if (
            not all(isfinite(v) for v in values)
            or self.collision_detection_distance_m <= 0
            or self.collision_minimum_distance_m < 0
            or self.collision_detection_distance_m <= self.collision_minimum_distance_m
            or not 0 < self.collision_gain <= 1
        ):
            raise ValueError("Invalid collision policy")
