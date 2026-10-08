"""Validated research inputs, deliberately separate from music-library objects."""

from dataclasses import asdict, dataclass, field, fields
from importlib.metadata import version
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
        if self.finger not in ("index", "middle"):
            raise ValueError("Supported contact fingers: index and middle")


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
    collision_limit_implementation: str = "displacement"
    collision_backtrack_steps: int = 12
    collision_edge_step_rad: float = 0.01

    def __post_init__(self) -> None:
        if self.backend != "mink-clarabel":
            raise ValueError("Unsupported solver backend")
        if type(self.max_iterations) is not int or self.max_iterations < 1:
            raise ValueError("max_iterations must be a positive integer")
        if type(self.collision_avoidance) is not bool:
            raise ValueError("collision_avoidance must be boolean")
        if self.collision_limit_implementation not in ("displacement", "mink_native"):
            raise ValueError("Unsupported collision limit implementation")
        if (
            type(self.collision_backtrack_steps) is not int
            or self.collision_backtrack_steps < 1
        ):
            raise ValueError(
                "Collision backtracking requires a positive integer budget"
            )
        for parameter in fields(self):
            if parameter.name in (
                "backend",
                "max_iterations",
                "collision_avoidance",
                "collision_limit_implementation",
                "collision_backtrack_steps",
            ):
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

    def __post_init__(self) -> None:
        if self.setup.seated is not None:
            from .seated_setup import derive_setup

            object.__setattr__(
                self, "geometry", derive_setup(self.geometry, self.setup)[0]
            )

    def resolved_profiles(self) -> dict[str, Any]:
        instrument = asdict(self.geometry)
        if self.geometry.geometry_model == "rectangular_v0":
            instrument.pop("geometry_model")
        else:
            from .physical_cba import REFERENCE

            instrument["physical_model"] = REFERENCE.specification()
        setup = asdict(self.setup)
        if self.setup.seated is not None and self.setup.seated.lower_body is None:
            setup["seated"].pop("lower_body")
        if self.setup.seated is None:
            setup.pop("seated")
        else:
            from .seated_setup import derive_setup

            setup["derived_anchors"] = derive_setup(self.geometry, self.setup)[1]
        setup["board"] = {
            "origin_m": self.geometry.origin_m,
            "rotation_wxyz": self.geometry.rotation_wxyz,
            "provenance": self.source.get("setup", {})
            .get("board", {})
            .get("provenance", asdict(self.geometry.evidence)),
        }
        if self.setup.seated is not None:
            setup["board"]["provenance"] = {
                "kind": "derived",
                "source": self.setup.seated.evidence,
                "note": "Recalculated from torso, instrument scale and support anchors",
            }
        solver = asdict(self.solver)
        contact = asdict(self.physical_contact)
        if not self.physical_contact.additional_collision_pairs:
            contact.pop("additional_collision_pairs")
            contact.pop("additional_collision_evidence")
        # Published profile hashes used implicit Mink-native semantics. Keep
        # that legacy representation; new explicit settings carry the field.
        if self.solver.collision_limit_implementation == "mink_native":
            solver.pop("collision_limit_implementation")
            solver.pop("collision_backtrack_steps")
            solver.pop("collision_edge_step_rad")
        player = asdict(self.player)
        if self.player.model == "myoarm_r":
            player.pop("full_body_posture")
        return {
            "instrument": instrument,
            "player": player,
            "setup": setup,
            "contact": contact,
            "solver": solver,
        }

    def expanded_source(self) -> dict[str, Any]:
        """Materialize profile defaults before applying calibration patches."""
        import json

        result: dict[str, Any] = json.loads(json.dumps(self.source))
        result["schema_version"] = 2
        result["anatomy"]["model"] = self.player.model
        geometry = asdict(self.geometry)
        if self.geometry.geometry_model == "rectangular_v0":
            geometry.pop("geometry_model")
        evidence = geometry.pop("evidence")
        origin, rotation = geometry.pop("origin_m"), geometry.pop("rotation_wxyz")
        result["geometry"] = {**geometry, "provenance": evidence}
        result["player"] = asdict(self.player)
        if self.player.model == "myoarm_r":
            result["player"].pop("full_body_posture")
        result["physical_contact"] = asdict(self.physical_contact)
        result["solver"] = asdict(self.solver)
        torso = asdict(self.setup)
        if self.setup.seated is not None and self.setup.seated.lower_body is None:
            torso["seated"].pop("lower_body")
        if self.setup.seated is None:
            torso.pop("seated")
        result["setup"] = {
            "torso": torso,
            "board": {
                "origin_m": origin,
                "rotation_wxyz": rotation,
                "provenance": self.source.get("setup", {})
                .get("board", {})
                .get("provenance", evidence),
            },
        }
        return result

    @classmethod
    def from_dict(cls, source: dict[str, Any]) -> Experiment:
        if source["schema_version"] not in (1, 2):
            raise ValueError("Unsupported experiment schema")
        if source["randomness"] != {"used": False, "seed": None}:
            raise ValueError("This deterministic solver does not use a random seed")
        if source["anatomy"]["version"] != version("myo-sim"):
            raise ValueError(
                "Recorded anatomy package version differs from installed model"
            )
        from .full_body import ASSEMBLIES

        if source["anatomy"]["model"] not in ASSEMBLIES:
            raise ValueError("Unsupported anatomy model")
        if source["render"] != {"width": 960, "height": 720, "backend": "egl"}:
            raise ValueError(
                "Prototype requires the recorded canonical render settings"
            )
        if (
            source.get("player", {}).get("model", source["anatomy"]["model"])
            != source["anatomy"]["model"]
        ):
            raise ValueError("Anatomy assembly disagrees with player profile")
        geometry = dict(source["geometry"])
        if source["schema_version"] == 2:
            placement = source["setup"].get("board", {})
            geometry["origin_m"] = placement.get("origin_m", (0, 0, 0))
            geometry["rotation_wxyz"] = tuple(
                placement.get("rotation_wxyz", (2**-0.5, -(2**-0.5), 0, 0))
            )
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
        if not 1 <= len(contacts) <= 2 or len({c.finger for c in contacts}) != len(
            contacts
        ):
            raise ValueError("One or two contacts with distinct fingers are supported")
        if len({(c.row, c.column) for c in contacts}) != len(contacts):
            raise ValueError("Two fingers on one button are outside this experiment")
        initial = source["initial_joints_rad"]
        if not all(type(v) in (int, float) and isfinite(v) for v in initial.values()):
            raise ValueError("Initial joint angles must be finite radians")
        frozen = tuple(source.get("frozen_joints", []))
        if not all(isinstance(n, str) for n in frozen) or len(set(frozen)) != len(
            frozen
        ):
            raise ValueError("Frozen joint names must be unique strings")
        solver = dict(source["solver"])
        solver.setdefault("collision_limit_implementation", "mink_native")
        return cls(
            source["id"],
            BoardGeometry(**geometry, evidence=evidence),
            contacts,
            initial,
            SolverSettings(**solver),
            source,
            frozen,
            PlayerProfile(
                **{"model": source["anatomy"]["model"], **source.get("player", {})}
            ),
            SetupProfile(**source.get("setup", {}).get("torso", {})),
            ContactProfile(**source.get("physical_contact", {})),
        )
