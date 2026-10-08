from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.instrument import (
    BOARD_TO_WORLD,
    button_at,
    buttons,
    buttons_for_pitch,
)

INPUT = Path("experiments/001-single-contact/experiment.json")


def test_finite_manufacturer_diagram_mapping() -> None:
    board = buttons()
    assert len(board) == 62
    assert len({b.id for b in board}) == 62
    assert [sum(b.row == row for b in board) for row in range(1, 6)] == [
        12,
        13,
        12,
        13,
        12,
    ]
    assert {b.midi for b in board} == set(range(54, 92))
    assert [(b.row, b.column) for b in buttons_for_pitch(60)] == [(1, 5), (4, 5)]
    assert [(b.row, b.column) for b in buttons_for_pitch(62)] == [(3, 5)]
    # Edge asymmetry matters: the lowest F# exists only on support row 4.
    assert [(b.row, b.column) for b in buttons_for_pitch(54)] == [(4, 3)]
    assert buttons_for_pitch(53) == ()
    with pytest.raises(ValueError):
        button_at(1, 3)


def test_board_frame_is_right_handed_and_pitch_goes_down() -> None:
    geometry = load_input(INPUT).geometry
    assert np.linalg.det(BOARD_TO_WORLD) == pytest.approx(1)
    np.testing.assert_allclose(BOARD_TO_WORLD.T @ BOARD_TO_WORLD, np.eye(3))
    origin = geometry.surface_world_m(button_at(1, 5))
    high = geometry.surface_world_m(button_at(1, 6))
    inner = geometry.surface_world_m(button_at(2, 5))
    assert high[2] < origin[2]
    assert inner[0] < origin[0]
    assert inner[2] < origin[2]
    np.testing.assert_allclose(BOARD_TO_WORLD[:, 2], [0, 1, 0])


def test_roland_diagram_stagger_at_equal_logical_columns() -> None:
    geometry = load_input(INPUT).geometry
    v = [geometry.center_board_m(button_at(r, 5))[1] for r in range(1, 6)]
    np.testing.assert_allclose(
        np.array(v) / geometry.column_spacing_m, [0, 0.5, 1, 0.5, 1]
    )
    # This is the manual's first topmost button in each row: A3/G3/G#3/F#3/G3.
    top = [button_at(row, low) for row, low in enumerate([4, 3, 3, 3, 3], 1)]
    assert [b.midi for b in top] == [57, 55, 56, 54, 55]
    np.testing.assert_allclose(
        [geometry.center_board_m(b)[1] / geometry.column_spacing_m for b in top],
        [-1, -1.5, -1, -1.5, -1],
    )


@pytest.mark.parametrize("value", [0, -0.01, float("nan"), float("inf")])
def test_unknown_or_invalid_metric_values_are_not_silently_usable(value: float) -> None:
    geometry = load_input(INPUT).geometry
    assert geometry.button_travel_m is None
    with pytest.raises(ValueError):
        replace(geometry, column_spacing_m=value)
