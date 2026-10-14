"""Compiled frame signs and separation of absolute posture from untimed motion."""

import numpy as np
import pytest

from accordion_ergonomics_core.digits import DIGITS
from accordion_ergonomics_core.passage_search import reference_experiment
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.wrist import (
    WristReference,
    reference_geometry,
    wrist_descriptors,
)


@pytest.fixture(scope="module")
def wrist_scene():
    e = reference_experiment()
    return build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)


def test_native_geometry_signs_and_zero_are_compiled(wrist_scene):
    s = wrist_scene
    before = s.data.qpos.copy()
    g = reference_geometry(s)
    base, flex, dev, forearm = g["probes"]
    assert np.allclose(base["palm_axes_in_radius"], np.eye(3), atol=1e-12)
    assert (
        flex["hand_longitudinal_in_radius"][2] < base["hand_longitudinal_in_radius"][2]
    )
    assert (
        dev["hand_longitudinal_in_radius"][0] > base["hand_longitudinal_in_radius"][0]
    )
    assert np.allclose(
        forearm["palm_axes_in_radius"], base["palm_axes_in_radius"], atol=1e-12
    )
    assert np.array_equal(before, s.data.qpos)
    assert g["coordinates"]["deviation_r"]["range_rad"][1] > abs(
        g["coordinates"]["deviation_r"]["range_rad"][0]
    )


def test_motionless_displaced_wrist_is_not_reference_neutral(wrist_scene):
    m = wrist_scene.model
    names = [m.joint(i).name for i in range(m.njnt)]
    q = m.qpos0.copy()
    q[m.joint("flexion_r").qposadr[0]] = 0.7
    states = [dict(qpos_rad=q.tolist(), event_index=i) for i in range(2)]
    a = wrist_descriptors(m, states, names)
    assert a["summary"]["flexion_r"]["total_variation_rad"] == 0
    assert a["summary"]["flexion_r"]["maximum_reference_departure_rad"] == 0.7
    assert len(a["musical_events"]) == 2
    shifted = wrist_descriptors(
        m, states, names, WristReference("hypothesis", 0.1, 0, "synthetic sensitivity")
    )
    assert shifted["summary"]["flexion_r"]["total_variation_rad"] == 0
    assert shifted["summary"]["flexion_r"][
        "maximum_reference_departure_rad"
    ] == pytest.approx(0.6)


def test_intermediate_extreme_is_preserved_and_failed_nodes_have_no_motion(wrist_scene):
    m = wrist_scene.model
    names = [m.joint(i).name for i in range(m.njnt)]
    states = []
    for i, v in enumerate((0, 0.6, 0)):
        q = m.qpos0.copy()
        q[m.joint("flexion_r").qposadr[0]] = v
        states.append(dict(qpos_rad=q.tolist(), event_index=i if i != 1 else None))
    full = wrist_descriptors(m, states, names)
    endpoints = wrist_descriptors(m, [states[0], states[-1]], names)
    assert full["summary"]["flexion_r"]["maximum_reference_departure_rad"] == 0.6
    assert endpoints["summary"]["flexion_r"]["maximum_reference_departure_rad"] == 0
    assert full["summary"]["flexion_r"]["extreme_reference_sample_index"] == 1
    failed = wrist_descriptors(m, states, names, connected=False)
    assert failed["summary"]["flexion_r"]["total_variation_rad"] is None
    with pytest.raises(ValueError, match="coordinate order"):
        wrist_descriptors(m, states, list(reversed(names)))
