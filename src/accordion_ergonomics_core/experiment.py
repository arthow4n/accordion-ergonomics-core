"""Validated research inputs, deliberately separate from music-library objects."""

from dataclasses import asdict, dataclass, field, fields
from math import isfinite
from typing import Any

from .instrument import BoardGeometry, Evidence, EvidenceKind, button_at
from .profiles import ContactProfile, PlayerProfile, SetupProfile


@dataclass(frozen=True)
class ContactRequest:
    row: int
    column: int
    finger: str

    def __post_init__(self) -> None:
        if type(self.row) is not int or type(self.column) is not int:
            raise ValueError("Physical button indices must be integers")
        button_at(self.row, self.column)
        if self.finger != "index":
            raise ValueError("Prototype supports index fingertip contact only")


@dataclass(frozen=True)
class SolverSettings:
    backend: str
    max_iterations: int
    integration_dt_s: float
    position_cost: float
    normal_cost: float
    posture_cost: float
    damping: float
    position_tolerance_m: float
    normal_tolerance_rad: float
    joint_tolerance_rad: float
    equality_tolerance_rad: float
    penetration_tolerance_m: float
    collision_avoidance: bool

    def __post_init__(self) -> None:
        if self.backend != "mink-clarabel":
            raise ValueError("Unsupported solver backend")
        if type(self.max_iterations) is not int or self.max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer")
        if type(self.collision_avoidance) is not bool:
            raise ValueError("collision_avoidance must be boolean")
        for parameter in fields(self):
            if parameter.name in ("backend", "max_iterations", "collision_avoidance"):
                continue
            value = getattr(self, parameter.name)
            if type(value) not in (int, float) or not isfinite(value) or value <= 0:
                raise ValueError(f"{parameter.name} must be finite and positive")


@dataclass(frozen=True)
class Experiment:
    id: str
    geometry: BoardGeometry
    contacts: tuple[ContactRequest, ...]
    initial_joints_rad: dict[str, float]
    solver: SolverSettings
    source: dict[str, Any]
    frozen_joints: tuple[str, ...] = ()

    player: PlayerProfile = field(default_factory=PlayerProfile)
    setup: SetupProfile = field(default_factory=SetupProfile)
    physical_contact: ContactProfile = field(default_factory=ContactProfile)

    def resolved_profiles(self) -> dict[str, Any]:
        return {
            "instrument": asdict(self.geometry),
            "player": asdict(self.player),
            "setup": asdict(self.setup),
            "contact": asdict(self.physical_contact),
            "solver": asdict(self.solver),
        }

    @classmethod
    def from_dict(cls, source: dict[str, Any]) -> Experiment:
        if source["schema_version"] not in (1, 2):
            raise ValueError("Unsupported experiment schema")
        if source["randomness"] != {"used": False, "seed": None}:
            raise ValueError("This deterministic solver does not use a random seed")
        if source["anatomy"]["model"] != "myoarm_r":
            raise ValueError("Unsupported anatomy model")
        if source["render"] != {"width": 960, "height": 720, "backend": "egl"}:
            raise ValueError(
                "Prototype requires the recorded canonical render settings"
            )
        geometry = dict(source["geometry"])
        if source["schema_version"] == 2:
            placement = source["setup"]["board"]
            geometry["origin_m"] = placement["origin_m"]
            geometry["rotation_wxyz"] = tuple(placement["rotation_wxyz"])
        if "stagger_columns" in geometry:
            geometry["stagger_columns"] = tuple(geometry["stagger_columns"])
        provenance = geometry.pop("provenance")
        evidence = Evidence(
            EvidenceKind(provenance["kind"]), provenance["source"], provenance["note"]
        )
        geometry["origin_m"] = tuple(geometry["origin_m"])
        if len(geometry["origin_m"]) != 3:
            raise ValueError("World origin must have three coordinates")
        contacts = tuple(ContactRequest(**c) for c in source["contacts"])
        if len(contacts) != 1:
            raise ValueError("Prototype supports exactly one contact")
        initial = source["initial_joints_rad"]
        if not all(type(v) in (int, float) and isfinite(v) for v in initial.values()):
            raise ValueError("Initial joint angles must be finite radians")
        frozen = tuple(source.get("frozen_joints", []))
        if not all(isinstance(n, str) for n in frozen) or len(set(frozen)) != len(
            frozen
        ):
            raise ValueError("Frozen joint names must be unique strings")
        return cls(
            source["id"],
            BoardGeometry(**geometry, evidence=evidence),
            contacts,
            initial,
            SolverSettings(**source["solver"]),
            source,
            frozen,
            PlayerProfile(**source.get("player", {})),
            SetupProfile(**source.get("setup", {}).get("torso", {})),
            ContactProfile(**source.get("physical_contact", {})),
        )
