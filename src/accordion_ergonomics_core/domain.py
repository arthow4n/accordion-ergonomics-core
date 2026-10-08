"""Research-owned physical states and descriptors, without MuJoCo objects."""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ContactRequirement:
    button_id: str
    finger: str

    def __post_init__(self) -> None:
        if not self.button_id or self.finger not in (
            "thumb",
            "index",
            "middle",
            "ring",
            "little",
        ):
            raise ValueError("Contacts need a physical button ID and explicit finger")


@dataclass(frozen=True)
class PlayingState:
    joint_names: tuple[str, ...]
    joint_angles_rad: tuple[float, ...]
    profile_sha256: str
    contacts: tuple[ContactRequirement, ...]
    state_schema_version: int = 2

    def __post_init__(self) -> None:
        if any(not isinstance(c, ContactRequirement) for c in self.contacts):
            raise ValueError("State contacts require explicit finger bindings")
        if len(self.joint_names) != len(self.joint_angles_rad) or len(
            set(self.joint_names)
        ) != len(self.joint_names):
            raise ValueError("State needs one finite angle per unique named joint")
        if not all(isfinite(v) for v in self.joint_angles_rad):
            raise ValueError("State angles must be finite radians")


@dataclass(frozen=True)
class PhysicalDescriptors:
    palm_position_world_m: tuple[float, ...]
    palm_rotation_world: tuple[float, ...]
    elbow_position_world_m: tuple[float, ...]
    minimum_joint_margin_rad: float
    minimum_active_joint_margin_rad: float
    wrist_rad: tuple[float, float]
    forearm_rotation_rad: float
    shoulder_rad: tuple[float, ...]
    finger_rad: tuple[float, ...]
    other_digits_rad: dict[str, tuple[float, ...]]


@dataclass(frozen=True)
class CandidateRealization:
    state: PlayingState
    descriptors: PhysicalDescriptors
    start_id: str
    relocation_m: float


@dataclass(frozen=True)
class PhysicalAction:
    target_button_id: str
    finger: str
    profile_sha256: str
    source_contacts_allowed_to_release: tuple[ContactRequirement, ...]
    required_preserved_contacts: tuple[ContactRequirement, ...] = ()


@dataclass(frozen=True)
class Trajectory:
    joint_names: tuple[str, ...]
    waypoints_rad: tuple[tuple[float, ...], ...]
    profile_sha256: str
    max_audit_step_rad: float
    continuous_validity: bool | None = None
    timing_s: tuple[float, ...] | None = None
