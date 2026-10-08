"""Research-owned physical states and descriptors, without MuJoCo objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlayingState:
    joint_names: tuple[str, ...]
    joint_angles_rad: tuple[float, ...]
    profile_sha256: str
    contacts: tuple[str, ...]


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


@dataclass(frozen=True)
class CandidateRealization:
    state: PlayingState
    descriptors: PhysicalDescriptors
    start_id: str
    relocation_m: float
