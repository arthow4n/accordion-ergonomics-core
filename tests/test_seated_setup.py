import hashlib
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.instrument import buttons
from accordion_ergonomics_core.profiles import SetupProfile
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene, diagnostics
from accordion_ergonomics_core.seated_setup import SeatedSetup, derive_setup


def reference():
    old = load_input(
        Path("experiments/018-collision-step-backtracking/experiment.json")
    )
    return replace(
        old, setup=SetupProfile(torso_origin_m=(0, 0, 0.65), seated=SeatedSetup())
    )


def test_derived_frame_matches_compiled_targets_and_envelope():
    e = reference()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    for b in buttons():
        np.testing.assert_allclose(
            s.data.site(f"target_{b.id}").xpos,
            e.geometry.surface_world_m(b),
            atol=1e-12,
        )
    assert np.linalg.det(e.geometry.rotation) == pytest.approx(1)
    assert e.geometry.rotation[2, 1] == pytest.approx(-1)
    np.testing.assert_allclose(
        s.model.geom("instrument_envelope").size, [0.1825, 0.19, 0.0975]
    )
    d = diagnostics(s, e.geometry.surface_world_m(buttons()[1]))
    for name in ("thorax_coll1", "thorax_coll2", "thorax_coll3"):
        assert d["instrument_envelope_distances_m"][name] >= 0.009999
    assert (s.model.nq, s.model.neq) == (38, 11)


def test_torso_rigid_transform_moves_setup_and_support_references_together():
    e = reference()
    r = Rotation.from_euler("y", 0.1)
    q = Rotation.from_matrix(r.as_matrix() @ np.diag([-1.0, -1.0, 1.0])).as_quat()
    translated = replace(
        e,
        setup=replace(
            e.setup, torso_origin_m=(0.1, 0.2, 0.75), torso_rotation_wxyz=(q[3], *q[:3])
        ),
    )
    expected = np.array([0.1, 0.2, 0.75]) + r.apply(
        np.array(e.geometry.origin_m) - [0, 0, 0.65]
    )
    np.testing.assert_allclose(translated.geometry.origin_m, expected, atol=1e-10)
    _, a = derive_setup(e.geometry, e.setup)
    _, b = derive_setup(translated.geometry, translated.setup)
    for key in (
        "shell_center_world_m",
        "right_thigh_reference_world_m",
        "treble_support_corner_world_m",
    ):
        np.testing.assert_allclose(
            b[key],
            np.array([0.1, 0.2, 0.75]) + r.apply(np.array(a[key]) - [0, 0, 0.65]),
            atol=1e-10,
        )


def test_setup_recalculates_and_cannot_accept_cached_board_pose():
    e = reference()
    x = e.expanded_source()
    x["setup"]["board"]["origin_m"] = [100, 100, 100]
    replay = Experiment.from_dict(x)
    np.testing.assert_allclose(replay.geometry.origin_m, e.geometry.origin_m)
    changed = replace(
        e, setup=replace(e.setup, seated=replace(e.setup.seated, torso_gap_m=0.03))
    )
    assert changed.resolved_profiles() != e.resolved_profiles()
    assert compiled_model_digest(
        build_scene(e.geometry, setup=e.setup).model
    ) != compiled_model_digest(build_scene(changed.geometry, setup=changed.setup).model)
    assert changed.geometry.origin_m[1] > e.geometry.origin_m[1]
    taller = replace(
        e,
        setup=replace(
            e.setup, seated=replace(e.setup.seated, instrument_height_m=0.40)
        ),
    )
    assert taller.geometry.origin_m[2] > e.geometry.origin_m[2]
    assert (
        asdict(SeatedSetup())["parameter_evidence"]["yaw_rad"]["kind"] == "assumption"
    )


def test_legacy_profile_commitment_is_unchanged():
    saved = json.loads(
        Path("experiments/018-collision-step-backtracking/result.json").read_text()
    )
    e = Experiment.from_dict(saved["input"])
    digest = hashlib.sha256(
        json.dumps(e.resolved_profiles(), sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    assert digest == saved["profiles_sha256"]
    with pytest.raises(ValueError):
        SeatedSetup(yaw_rad=float("nan"))
    with pytest.raises(ValueError):
        SeatedSetup(instrument_depth_m=-1)
