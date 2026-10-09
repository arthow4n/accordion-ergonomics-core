import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from accordion_ergonomics_core.cba_diagnostics import fit_diagnostics
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.instrument import buttons
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene
from accordion_ergonomics_core.seated_setup import derive_setup


def reference(name="compact-upper"):
    return Experiment.from_dict(
        json.loads(Path(f"experiments/036-instrument-size-fit/{name}.json").read_text())
    )


def test_height_changes_case_bottom_without_moving_any_target():
    compact, tall = reference(), reference("tall-upper")
    np.testing.assert_array_equal(compact.geometry.origin_m, tall.geometry.origin_m)
    for button in buttons():
        np.testing.assert_array_equal(
            compact.geometry.surface_world_m(button),
            tall.geometry.surface_world_m(button),
        )
    a = build_scene(compact.geometry, compact.player, compact.setup)
    b = build_scene(tall.geometry, tall.player, tall.setup)
    for body in ("pelvis", "femur_r", "tibia_r", "torso", "humerus_r"):
        np.testing.assert_array_equal(a.data.body(body).xpos, b.data.body(body).xpos)
    fa, fb = fit_diagnostics(a, compact), fit_diagnostics(b, tall)
    assert fb["case_bottom_above_thigh_station_plane_m"] == pytest.approx(
        fa["case_bottom_above_thigh_station_plane_m"] - 0.05
    )
    assert compiled_model_digest(a.model) != compiled_model_digest(b.model)
    # Extra height changes walls, bellows and lower strap; no board scaling.
    assert (
        b.model.geom("keyboard_panel").size.tolist()
        == a.model.geom("keyboard_panel").size.tolist()
    )
    assert b.model.geom("cba_bellows_front").size[1] == 0.215
    assert b.model.nq == a.model.nq == 38
    assert b.model.neq == a.model.neq == 11


def test_upper_anchor_independent_of_thigh_radius_and_rigid_root():
    e = reference()
    p = e.setup.seated
    setup = replace(
        e.setup,
        seated=replace(
            p, lower_body=replace(p.lower_body, thigh_envelope_radius_m=0.09)
        ),
    )
    derived, anchors = derive_setup(e.geometry, setup)
    np.testing.assert_array_equal(e.geometry.origin_m, derived.origin_m)
    assert (
        anchors["bottom_above_support_plane_m"]
        < derive_setup(e.geometry, e.setup)[1]["bottom_above_support_plane_m"]
    )
    delta = Rotation.from_euler("xyz", [0.04, -0.08, 0.12])
    q = Rotation.from_matrix(delta.as_matrix() @ np.diag([-1.0, -1.0, 1.0])).as_quat()
    moved = replace(
        e.setup, torso_origin_m=(0.1, 0.2, 0.7), torso_rotation_wxyz=(q[3], *q[:3])
    )
    actual = derive_setup(e.geometry, moved)[0]
    np.testing.assert_allclose(
        actual.origin_m,
        [0.1, 0.2, 0.7]
        + delta.apply(np.asarray(e.geometry.origin_m) - e.setup.torso_origin_m),
        atol=1e-12,
    )


def test_historical_world_and_profiles_remain_exact():
    saved = json.loads(
        Path(
            "experiments/034-cba-mounted-orientation/reference/result.json"
        ).read_text()
    )
    e = Experiment.from_dict(saved["input"])
    s = build_scene(
        e.geometry,
        e.player,
        e.setup,
        e.physical_contact,
        tuple(c.finger for c in e.contacts),
    )
    assert (
        compiled_model_digest(s.model) == saved["provenance"]["compiled_model_sha256"]
    )
    assert json.loads(json.dumps(e.resolved_profiles())) == saved["resolved_profiles"]
    with pytest.raises(ValueError, match="explicit shoulder"):
        replace(
            reference(),
            setup=replace(
                reference().setup,
                seated=replace(reference().setup.seated, upper_case_to_shoulder_m=None),
            ),
        )
