import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from accordion_ergonomics_core._engine import mujoco
from accordion_ergonomics_core.cba_diagnostics import audit_geometry
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.instrument import BOARD_TO_WORLD, button_at, buttons
from accordion_ergonomics_core.physical_cba import (
    MODEL,
    REFERENCE,
    BellowsConfiguration,
    RigidTransform,
    attach_instrument,
    transform,
)
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene


def reference():
    return Experiment.from_dict(
        json.loads(
            Path("experiments/034-cba-mounted-orientation/experiment.json").read_text()
        )
    )


def test_all_keyboard_targets_normals_and_component_frames():
    e = reference()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    h = s.data.body(MODEL)
    rh = h.xmat.reshape(3, 3)
    np.testing.assert_allclose(
        s.data.body("keyboard").xpos,
        h.xpos + rh @ REFERENCE.fingerboard.translation_m,
        atol=1e-12,
    )
    np.testing.assert_allclose(
        e.geometry.rotation, rh @ REFERENCE.fingerboard.rotation, atol=1e-12
    )
    assert np.dot(e.geometry.rotation[:, 2], rh[:, 2]) == pytest.approx(
        np.cos(np.deg2rad(20))
    )
    p = e.setup.seated
    assert p is not None
    expected_board = (
        Rotation.from_euler(
            "ZYX", [p.yaw_rad, p.long_axis_tilt_rad, p.fore_aft_tilt_rad]
        ).as_matrix()
        @ BOARD_TO_WORLD
    )
    np.testing.assert_allclose(e.geometry.rotation, expected_board, atol=1e-12)
    # Independent reference normal: 30 deg toward the player's right, rather
    # than the rejected composition's 85 deg almost lateral normal.
    np.testing.assert_allclose(
        e.geometry.rotation[:, 2], [0.5, np.sqrt(3) / 2, 0], atol=1e-12
    )
    for b in buttons():
        np.testing.assert_allclose(
            s.data.site("target_" + b.id).xpos,
            e.geometry.surface_world_m(b),
            atol=1e-12,
        )
        np.testing.assert_allclose(
            s.data.geom(b.id).xmat.reshape(3, 3)[:, 2],
            e.geometry.rotation[:, 2],
            atol=1e-12,
        )
        # Cap top lies 4 mm above B; panel surface is B.n=0.
        local = e.geometry.rotation.T @ (s.data.geom(b.id).xpos - e.geometry.origin_m)
        assert local[2] + s.model.geom(b.id).size[1] == pytest.approx(0.004)
    bf = s.data.body("bass_fingerboard")
    for name, p in REFERENCE.bass_buttons():
        np.testing.assert_allclose(
            s.data.site("target_" + name).xpos,
            bf.xpos + bf.xmat.reshape(3, 3) @ p,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            s.data.geom(name).xmat.reshape(3, 3)[:, 2], -rh[:, 0], atol=1e-12
        )
    assert len(REFERENCE.bass_buttons()) == 96
    assert len({name for name, _ in REFERENCE.bass_buttons()}) == 96
    assert (s.model.nq, s.model.neq) == (38, 11)
    assert s.model.body("bass_assembly").parentid == s.model.body(MODEL).id
    assert s.model.body("keyboard").parentid == s.model.body("treble_assembly").id


def test_hypothetical_bass_transform_compiled_invariance():
    e = reference()

    def compile(bellows):
        spec = mujoco.MjSpec()
        attach_instrument(spec, e.geometry, bellows)
        # Independent target sites so this pure test does not need anatomy.
        for b in buttons():
            spec.body("keyboard").add_site(
                name=b.id, pos=list(e.geometry.center_board_m(b))
            )
        m = spec.compile()
        d = mujoco.MjData(m)
        mujoco.mj_forward(m, d)
        return m, d

    _, a = compile(BellowsConfiguration())
    hypothetical = transform(
        (-0.30, 0.025, 0.010),
        Rotation.from_euler("xyz", [0.04, 0.1, -0.06]).as_matrix(),
    )
    _, b = compile(BellowsConfiguration(bass_relative=hypothetical))
    for name in ("treble_assembly", "keyboard"):
        np.testing.assert_array_equal(a.body(name).xpos, b.body(name).xpos)
        np.testing.assert_array_equal(a.body(name).xmat, b.body(name).xmat)
    for button in buttons():
        np.testing.assert_array_equal(a.site(button.id).xpos, b.site(button.id).xpos)
    root = b.body(MODEL)
    r = root.xmat.reshape(3, 3)
    for name in ("cba_bass_grille", "cba_bass_panel", "bass_r1c1", "bass_r6c16"):
        old_local = REFERENCE.frames()["bass"].rotation.T @ (
            r.T @ (a.geom(name).xpos - root.xpos) - [-0.25, 0, 0]
        )
        np.testing.assert_allclose(
            b.geom(name).xpos, root.xpos + r @ hypothetical.apply(old_local), atol=1e-12
        )
    for name in ("bass_strap_upper", "bass_strap_lower"):
        old_local = r.T @ (a.site(name).xpos - root.xpos) - [-0.25, 0, 0]
        np.testing.assert_allclose(
            b.site(name).xpos, root.xpos + r @ hypothetical.apply(old_local), atol=1e-12
        )
    with pytest.raises(ValueError):
        BellowsConfiguration(opening_m=0.01)
    with pytest.raises(ValueError):
        RigidTransform(rotation_wxyz=(2, 0, 0, 0))


def test_geometry_intersections_dimensions_and_identity():
    e = reference()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    report = audit_geometry(s, e.geometry)
    # Unnamed imported surfaces must not overwrite each other in the audit.
    assert len(
        report["mounted_reference_diagnostics"]["instrument_component_distances_m"]
    ) == len(s.anatomy_geoms)
    # Only intentional backing/case junctions penetrate. Other components touch
    # at bellows end frames, wall edges and board/cap bases, or are separated.
    allowed = {
        frozenset(("cba_treble_rear", "cba_treble_rear_return")),
        frozenset(("cba_treble_grille", "cba_treble_shoulder")),
        frozenset(("cba_treble_shoulder", "cba_inner_rim")),
        frozenset(("cba_treble_rear_return", "keyboard_panel")),
        frozenset(("cba_treble_rear_return", "cba_treble_mount")),
        frozenset(("cba_bass_inner", "cba_bass_panel")),
    }
    for end in ("top", "bottom", "wing_top", "wing_bottom"):
        for wall in ("shoulder", "rear_return", "mount"):
            allowed.add(frozenset(("cba_treble_" + end, "cba_treble_" + wall)))
    for p in report["component_overlaps"]:
        assert frozenset((p["a"], p["b"])) in allowed
        assert p["distance_m"] > -0.008
    assert min(report["cap_to_nonparent_component_clearances_m"].values()) > 0.005
    support = report["mounted_reference_diagnostics"][
        "approximate_support_envelope_distances_m"
    ]
    assert set(support) == {
        "approximate_thigh_support_r",
        "approximate_thigh_support_l",
    }
    assert min(support.values()) > 0.0099
    for wall in ("shoulder", "rear_return"):
        np.testing.assert_allclose(
            s.data.geom("cba_treble_" + wall).xmat.reshape(3, 3)[:, 1],
            s.data.body("treble_assembly").xmat.reshape(3, 3)[:, 1],
            atol=1e-12,
        )
    h = s.data.body(MODEL)
    local = h.xmat.reshape(3, 3).T @ (s.data.body("keyboard").xpos - h.xpos)
    np.testing.assert_allclose(local, [0.078, 0.100, -0.160], atol=1e-12)
    assert -0.19 < local[2] < -0.14  # rear-adjacent, never grille-corner mounted
    for i in s.board_geoms:
        assert np.all(s.model.geom_size[i, :2] > 0)
        assert (s.model.geom_contype[i], s.model.geom_conaffinity[i]) == (2, 1)
    assert not any(
        s.model.geom(i).name == "instrument_envelope" for i in range(s.model.ngeom)
    )
    assert s.model.geom("cba_bellows_front").size[0] * 2 == pytest.approx(0.10)
    for _name, p in REFERENCE.bass_buttons():
        assert (
            -0.016 + REFERENCE.bass_button_radius_m
            <= p[0]
            <= 0.076 - REFERENCE.bass_button_radius_m
        )
        assert (
            -0.017 + REFERENCE.bass_button_radius_m
            <= p[1]
            <= 0.332 - REFERENCE.bass_button_radius_m
        )
    repeated = Experiment.from_dict(e.expanded_source())
    np.testing.assert_array_equal(repeated.geometry.origin_m, e.geometry.origin_m)
    again = build_scene(
        repeated.geometry, repeated.player, repeated.setup, repeated.physical_contact
    )
    assert compiled_model_digest(s.model) == compiled_model_digest(again.model)
    assert repeated.resolved_profiles() == e.resolved_profiles()
    old = replace(e, geometry=replace(e.geometry, geometry_model="rectangular_v0"))
    assert compiled_model_digest(
        build_scene(old.geometry, old.player, old.setup, old.physical_contact).model
    ) != compiled_model_digest(s.model)
    assert (
        e.geometry.surface_world_m(button_at(1, 5))[2]
        > e.geometry.surface_world_m(button_at(1, 15))[2]
    )


def test_mount_rigid_root_invariance_and_replay_rejection(tmp_path):
    from accordion_ergonomics_core.cba_diagnostics import replay_geometry

    e = reference()
    delta = Rotation.from_euler("xyz", [0.03, -0.06, 0.09])
    root = delta.as_matrix() @ np.diag([-1.0, -1.0, 1.0])
    q = Rotation.from_matrix(root).as_quat()
    moved = replace(
        e,
        setup=replace(
            e.setup,
            torso_origin_m=(0.10, 0.20, 0.75),
            torso_rotation_wxyz=(q[3], *q[:3]),
        ),
    )
    np.testing.assert_allclose(
        moved.geometry.origin_m,
        np.array([0.10, 0.20, 0.75])
        + delta.apply(np.asarray(e.geometry.origin_m) - [0, 0, 0.65]),
        atol=1e-12,
    )
    rejected = Path(
        "experiments/032-generic-cba-geometry/rejected-front-attachment/geometry/result.json"
    )
    with pytest.raises(
        ValueError,
        match="Different compiled world|Unsupported instrument geometry version",
    ):
        replay_geometry(rejected, tmp_path)
    with pytest.raises(
        ValueError,
        match="Different compiled world|Unsupported instrument geometry version",
    ):
        replay_geometry(
            Path("experiments/032-generic-cba-geometry/reference/result.json"), tmp_path
        )
