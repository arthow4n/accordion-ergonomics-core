import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from accordion_ergonomics_core.cli import load_input
from accordion_ergonomics_core.lower_body import (
    SeatedLegs,
    default_lower_body,
    posed_lower_body,
)
from accordion_ergonomics_core.provenance import compiled_model_digest
from accordion_ergonomics_core.scene import build_scene, diagnostics
from accordion_ergonomics_core.seated_setup import SeatedSetup, derive_setup


def reference():
    old = load_input(Path("experiments/023-reference-seated-setup/experiment.json"))
    return replace(old, setup=replace(old.setup, seated=SeatedSetup()))


def test_baked_bones_match_upstream_seated_fk_and_arm_is_unchanged():
    e = reference()
    _, upstream, data, landmarks = posed_lower_body(e.setup)
    s = build_scene(e.geometry, e.player, setup=e.setup)
    assert (s.model.nq, s.model.nv, s.model.nu, s.model.neq) == (38, 38, 63, 11)
    for name, point in landmarks.items():
        np.testing.assert_allclose(
            s.data.body(f"seated_{name}").xpos, point, atol=1e-12
        )
    checked = 0
    for i in range(upstream.ngeom):
        g = upstream.geom(i)
        parent = int(upstream.geom_bodyid[i])
        ancestors = set()
        while parent > 0:
            ancestors.add(upstream.body(parent).name)
            parent = int(upstream.body_parentid[parent])
        if g.type == 7 and g.group == 0 and "pelvis" in ancestors:
            n = s.model.geom(f"seated_{g.name}").id
            np.testing.assert_allclose(
                s.data.geom_xpos[n], data.geom_xpos[i], atol=1e-12
            )
            np.testing.assert_allclose(
                s.data.geom_xmat[n], data.geom_xmat[i], atol=1e-12
            )
            checked += 1
    assert checked >= 14
    legacy = load_input(Path("experiments/023-reference-seated-setup/experiment.json"))
    before = build_scene(legacy.geometry, legacy.player, setup=legacy.setup).model
    for attribute in ("jnt_range", "eq_data", "actuator_gainprm", "actuator_biasprm"):
        np.testing.assert_array_equal(
            getattr(s.model, attribute), getattr(before, attribute)
        )
    distances = diagnostics(s, np.array(e.geometry.origin_m))[
        "approximate_support_envelope_distances_m"
    ]
    assert min(distances.values()) >= e.setup.seated.support_clearance_m - 1e-6
    assert landmarks["tibia_r"][1] > landmarks["femur_r"][1] + 0.35
    assert abs(landmarks["tibia_r"][2] - landmarks["femur_r"][2]) < 0.01
    assert landmarks["calcn_r"][2] < landmarks["tibia_r"][2] - 0.4
    assert s.model.geom("approximate_thigh_support_r").contype == 0
    assert all(
        not s.model.body(i).name.startswith("seated_sacrum")
        for i in range(s.model.nbody)
    )


def test_support_anchor_is_independent_of_instrument_and_tracks_leg_pose():
    e = reference()
    _, a = derive_setup(e.geometry, e.setup)
    moved = replace(
        e.setup, seated=replace(e.setup.seated, yaw_rad=0.0, torso_gap_m=0.03)
    )
    _, b = derive_setup(e.geometry, moved)
    np.testing.assert_allclose(
        a["right_thigh_reference_world_m"], b["right_thigh_reference_world_m"]
    )
    changed = replace(
        e.setup,
        seated=replace(
            e.setup.seated, lower_body={**default_lower_body(), "hip_flexion_rad": 1.4}
        ),
    )
    g, c = derive_setup(e.geometry, changed)
    assert abs(g.origin_m[2] - e.geometry.origin_m[2]) > 0.001
    assert c["right_thigh_reference_world_m"] != a["right_thigh_reference_world_m"]
    with pytest.raises(ValueError):
        SeatedLegs(knee_flexion_rad=float("nan"))
    with pytest.raises(FrozenInstanceError):
        e.setup.seated.lower_body.hip_flexion_rad = 0.1


@pytest.mark.parametrize(
    "directory",
    [
        "experiments/023-reference-seated-setup",
        "experiments/029-myosim-seated-lower-body/reference",
    ],
)
def test_recorded_seated_profiles_and_compiled_models_are_preserved(directory):
    p = json.loads((Path(directory) / "result.json").read_text())
    e = load_input(Path(directory) / "experiment.json")
    assert e.setup.seated is not None
    if "023" in directory:
        assert e.setup.seated.lower_body is None
    else:
        assert isinstance(e.setup.seated.lower_body, SeatedLegs)
    digest = hashlib.sha256(
        json.dumps(e.resolved_profiles(), sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    s = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
    if "023" in directory:
        assert digest == p["profiles_sha256"]
        assert (
            compiled_model_digest(s.model) == p["provenance"]["compiled_model_sha256"]
        )
    else:
        # Nontrivial baked rotations can differ by roundoff across CPU/libm/BLAS.
        # Production state/model hash guards remain exact; do not relax them here.
        def equivalent(actual, recorded):
            if isinstance(actual, dict):
                assert actual.keys() == recorded.keys()
                for key in actual:
                    equivalent(actual[key], recorded[key])
            elif isinstance(actual, (list, tuple)):
                assert len(actual) == len(recorded)
                for a, b in zip(actual, recorded, strict=True):
                    equivalent(a, b)
            elif isinstance(actual, float):
                assert actual == pytest.approx(recorded, rel=0, abs=1e-12)
            else:
                assert actual == recorded

        equivalent(e.resolved_profiles(), p["resolved_profiles"])
        again = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
        assert compiled_model_digest(s.model) == compiled_model_digest(again.model)


def test_baked_leg_frames_follow_rotated_torso():
    e = reference()
    r = Rotation.from_euler("xyz", [0.1, -0.15, 0.2])
    q = Rotation.from_matrix(r.as_matrix() @ np.diag([-1.0, -1.0, 1.0])).as_quat()
    setup = replace(
        e.setup, torso_origin_m=(0.1, 0.2, 0.75), torso_rotation_wxyz=(q[3], *q[:3])
    )
    _, _, _, points = posed_lower_body(e.setup)
    s = build_scene(e.geometry, e.player, setup=setup)
    for name, p in points.items():
        np.testing.assert_allclose(
            s.data.body(f"seated_{name}").xpos,
            [0.1, 0.2, 0.75] + r.apply(p - [0, 0, 0.65]),
            atol=1e-12,
        )
