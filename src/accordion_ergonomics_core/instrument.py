"""Finite C-Griff topology and an explicitly provisional metric embedding.

Board frame B is right handed: +u toward outer edge (decreasing row),
+v down the keyboard (increasing pitch), +n out of the playing surface.
World W: +x player's right, +y forward, +z up. B axes in W are x, -z, y.
"""

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

import numpy as np
from numpy.typing import NDArray

Vector = tuple[float, float, float]


class EvidenceKind(StrEnum):
    MANUFACTURER = "manufacturer"
    MEASURED = "measured"
    DERIVED = "derived"
    IMPORTED_MODEL = "imported_model"
    IMPLEMENTATION = "implementation_evidence"
    ASSUMPTION = "assumption"
    HYPOTHESIS = "hypothesis"
    HEURISTIC = "heuristic"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Evidence:
    kind: EvidenceKind
    source: str
    note: str


@dataclass(frozen=True)
class Button:
    row: int
    column: int
    midi: int

    @property
    def id(self) -> str:
        return f"r{self.row}c{self.column}"


# Source mapping anchor retained for compatibility; NOT metric coordinates.
ROW_BOUNDS = ((4, 15), (3, 15), (3, 14), (3, 15), (3, 14))
PITCH_OFFSETS = (0, 1, 2, 0, 1)
# Roland manual p50: relative DOWNWARD positions of C4/C#4/D4/C4/C#4.
# Rows 1/3/5 align modulo a column, but NOT at equal logical columns.
STAGGER_COLUMNS = (0.0, 0.5, 1.0, 0.5, 1.0)
TOPOLOGY_EVIDENCE = Evidence(
    EvidenceKind.DERIVED,
    "https://cdn.roland.com/assets/media/pdf/FR-1x_OM.pdf#page=50",
    "Diagram cross-checked against both existing repositories; logical C4=r1c5.",
)


def buttons() -> tuple[Button, ...]:
    return tuple(
        Button(row, column, 60 + 3 * (column - 5) + PITCH_OFFSETS[row - 1])
        for row, (low, high) in enumerate(ROW_BOUNDS, start=1)
        for column in range(low, high + 1)
    )


def button_at(row: int, column: int) -> Button:
    for button in buttons():
        if (button.row, button.column) == (row, column):
            return button
    raise ValueError(f"No physical button at row={row}, column={column}")


def buttons_for_pitch(midi: int) -> tuple[Button, ...]:
    return tuple(b for b in buttons() if b.midi == midi)


BOARD_TO_WORLD: NDArray[np.float64] = np.array(
    [[1.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, -1.0, 0.0]]
)


@dataclass(frozen=True)
class BoardGeometry:
    """Synthetic metric fixture. Values MUST come from an experiment input.

    origin_m is r1c5's base in world coordinates. Travel is unknown, not zero.
    A flat regular board is a test fixture, not a measured FR-1XB model.
    """

    column_spacing_m: float
    row_spacing_m: float
    button_radius_m: float
    button_height_m: float
    origin_m: Vector
    evidence: Evidence
    geometry_model: str = "rectangular_v0"
    button_travel_m: float | None = None
    stagger_columns: tuple[float, ...] = STAGGER_COLUMNS
    panel_margin_m: float = 0.012
    panel_thickness_m: float = 0.008
    rotation_wxyz: tuple[float, float, float, float] = (2**-0.5, -(2**-0.5), 0, 0)

    @property
    def rotation(self) -> NDArray[np.float64]:
        w, x, y, z = self.rotation_wxyz
        return np.array(
            [
                [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
            ]
        )

    def __post_init__(self) -> None:
        if self.geometry_model not in ("rectangular_v0", "generic_cba_v2"):
            raise ValueError("Unsupported instrument geometry version")
        values = (
            self.column_spacing_m,
            self.row_spacing_m,
            self.button_radius_m,
            self.button_height_m,
            self.panel_margin_m,
            self.panel_thickness_m,
        )
        if not all(isfinite(x) and x > 0 for x in values):
            raise ValueError("Metric fixture dimensions must be finite and positive")
        if len(self.stagger_columns) != 5 or not all(
            isfinite(x) for x in self.stagger_columns
        ):
            raise ValueError("Five finite row staggers are required")
        if (
            len(self.rotation_wxyz) != 4
            or not all(isfinite(x) for x in self.rotation_wxyz)
            or abs(sum(x * x for x in self.rotation_wxyz) - 1) > 1e-10
        ):
            raise ValueError("Board quaternion must be finite and unit length")
        if len(self.origin_m) != 3 or not all(isfinite(x) for x in self.origin_m):
            raise ValueError("Board origin must be finite")
        if self.button_travel_m is not None and (
            not isfinite(self.button_travel_m) or self.button_travel_m < 0
        ):
            raise ValueError("Button travel must be unknown or finite and nonnegative")
        if self.evidence.kind == EvidenceKind.UNKNOWN:
            raise ValueError("Unknown dimensions cannot instantiate a metric board")

    def center_board_m(self, button: Button) -> Vector:
        return (
            -(button.row - 1) * self.row_spacing_m,
            (button.column - 5 + self.stagger_columns[button.row - 1])
            * self.column_spacing_m,
            self.button_height_m,
        )

    def surface_world_m(self, button: Button) -> NDArray[np.float64]:
        return np.asarray(self.origin_m) + self.rotation @ np.asarray(
            self.center_board_m(button)
        )
