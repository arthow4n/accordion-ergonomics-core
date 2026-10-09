"""Saved-state physical-instrument diagnostics; no new renderer dependency."""

import hashlib
import json
from math import atan2, degrees

import numpy as np
from PIL import Image, ImageDraw

from ._engine import mujoco
from .experiment import Experiment
from .instrument import button_at, buttons
from .physical_cba import MODEL, REFERENCE, reference_for
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene, diagnostics


def cross_section(geometry, path):
    """Metric u/n section from component coordinates, independent of camera."""
    im = Image.new("RGB", (960, 720), (244, 246, 248))
    draw = ImageDraw.Draw(im)

    def pixels(p):
        return (int(540 + p[0] * 2100), int(230 - p[2] * 2100))

    def polygon(points, color):
        draw.polygon([pixels(p) for p in points], fill=color, outline=(30, 40, 50))

    def rectangle(u0, u1, n0, n1, color, frame=None):
        points = [(u0, 0, n0), (u1, 0, n0), (u1, 0, n1), (u0, 0, n1)]
        polygon([frame.apply(p) for p in points] if frame else points, color)

    t = REFERENCE.case_wall_m
    for bounds in (
        (-0.15, 0, -t, 0),
        (-0.15, 0, -0.20, -0.20 + t),
        (-0.15, -0.15 + t, -0.20 + t, -t),
    ):
        rectangle(*bounds, (115, 140, 160))
    fb = REFERENCE.fingerboard
    rectangle(-0.078, 0.012, -0.012, 0, (55, 82, 106), fb)
    rectangle(-0.078, 0.012, -0.018, -0.012, (115, 140, 160), fb)
    inner = fb.apply((-0.078, 0, -0.012))
    outer = fb.apply((0.012, 0, -0.018))
    for a, b in (
        (np.array([0.0, 0.0, 0.0]), inner),
        (outer, np.array([0.0, 0.0, -0.20])),
    ):
        delta = b - a
        normal = np.array([-delta[2], 0.0, delta[0]]) / np.linalg.norm(delta)
        if normal[0] > 0:
            normal = -normal
        polygon([a, b, b + normal * 0.006, a + normal * 0.006], (115, 140, 160))
    rectangle(0.012, 0.016, -0.012, 0.002, (155, 170, 180), fb)
    rectangle(-0.082, -0.078, -0.012, 0.002, (155, 170, 180), fb)
    for row in range(1, 6):
        u = geometry.center_board_m(button_at(row, 5))[0]
        rectangle(
            u - geometry.button_radius_m,
            u + geometry.button_radius_m,
            0,
            geometry.button_height_m,
            (231, 190, 79),
            fb,
        )
    draw.text(
        (25, 20),
        "Generic CBA v2 | metric treble u/n section (down axis into page)",
        fill=(25, 40, 55),
    )
    for location, label in (
        ((25, 55), "Grille plane H.n = 0; rear wall n = -200 mm"),
        ((25, 75), "H.u: outward treble; H.n: anterior / grille normal"),
        ((25, 95), "B normal tilted 20 deg toward outer side; B.u crosses board"),
        ((25, 115), "Board: 12 mm thick; case backing: 6 mm; caps: 4 mm above B"),
        ((25, 135), "B origin H = (78, 100, -160) mm; every metric is assumed"),
        ((185, 255), "Hollow case"),
        ((195, 210), "Grille"),
        ((680, 420), "Button tops"),
        ((705, 480), "Fingerboard"),
        ((650, 615), "Rear-adjacent case cheek"),
    ):
        draw.text(location, label, fill=(25, 40, 55))
    o = fb.apply((0, 0, 0))
    for axis, color, label in (
        (np.array([0.04, 0, 0]), (220, 50, 50), "B.u"),
        (np.array([0, 0, 0.04]), (50, 90, 230), "B.n"),
    ):
        end = o + fb.rotation @ axis
        draw.line((pixels(o), pixels(end)), fill=color, width=3)
        draw.text(pixels(end), label, fill=color)
    a, b = pixels((-0.14, 0, -0.22)), pixels((-0.09, 0, -0.22))
    draw.line((a, b), fill=(30, 40, 50), width=3)
    draw.text((a[0], a[1] + 10), "50 mm", fill=(30, 40, 50))
    im.save(path)


def render_cba(scene, geometry, output, cameras=None):
    output.mkdir(parents=True, exist_ok=True)
    m, d = scene.model, scene.data
    mujoco.mj_forward(m, d)
    h = d.body(MODEL)
    r = h.xmat.reshape(3, 3)
    center = h.xpos + r @ np.array([-0.15, 0.19, -0.08])

    def angle(direction):
        return degrees(atan2(-direction[1], -direction[0]))

    if cameras is None:
        cameras = {}
        for name, direction, distance, elevation in (
            ("treble", geometry.rotation[:, 2], 0.83, 0),
            ("front", r[:, 2], 0.90, 0),
            ("side", r[:, 0], 0.90, 0),
            ("oblique", r[:, 0] + r[:, 2], 0.95, -25),
            ("bass", -r[:, 0], 0.85, 0),
            ("top_section", r[:, 0] + r[:, 2], 1.05, -90),
        ):
            cameras["instrument_" + name] = dict(
                lookat=center.tolist(),
                distance=distance,
                azimuth=angle(direction),
                elevation=elevation,
                orthographic=1,
            )
        body_center = (d.body("Full Body").xpos + d.body("head").xpos) / 2 + np.array(
            [0, 0.10, -0.13]
        )
        for name, azimuth in (
            ("front", -90),
            ("right", 180),
            ("left", 0),
            ("oblique", -125),
        ):
            cameras["body_" + name] = dict(
                lookat=body_center.tolist(),
                distance=2.05,
                azimuth=azimuth,
                elevation=-8 if name == "oblique" else 0,
            )
        cameras["body_hand"] = dict(
            lookat=geometry.surface_world_m(button_at(1, 5)).tolist(),
            distance=0.48,
            azimuth=angle(geometry.rotation[:, 2]),
            elevation=-20,
        )
    groups = m.geom_group.copy()
    site_groups = m.site_group.copy()
    before = compiled_model_digest(m)
    descendant = set()
    for i in range(m.nbody):
        parent = i
        while parent:
            if parent == m.body(MODEL).id:
                descendant.add(i)
                break
            parent = int(m.body_parentid[parent])
    option = mujoco.MjvOption()
    option.sitegroup[:] = 0
    option.sitegroup[0] = 1
    option.geomgroup[3] = 0
    option.flags[mujoco.mjtVisFlag.mjVIS_TENDON] = False
    try:
        with mujoco.Renderer(m, height=720, width=960) as renderer:
            for name, settings in cameras.items():
                m.geom_group[:] = groups
                m.site_group[:] = site_groups
                if name.startswith("instrument_"):
                    for i in range(m.ngeom):
                        if int(m.geom_bodyid[i]) not in descendant:
                            m.geom_group[i] = 5
                if name.startswith("instrument_"):
                    for i in range(m.nsite):
                        if int(m.site_bodyid[i]) not in descendant:
                            m.site_group[i] = 5
                camera = mujoco.MjvCamera()
                for key, value in settings.items():
                    setattr(camera, key, value)
                renderer.update_scene(d, camera=camera, scene_option=option)
                renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SKYBOX] = False
                picture = Image.fromarray(renderer.render())
                draw = ImageDraw.Draw(picture)
                draw.rectangle((0, 0, 960, 50), fill=(20, 30, 40))
                draw.text(
                    (12, 10),
                    name
                    + " | "
                    + geometry.geometry_model
                    + " | assumed metrics; fixed closed",
                    fill="white",
                )
                draw.text(
                    (12, 30),
                    "Blue-grey: cases / dark: boards / red: bellows / gold: straps",
                    fill="white",
                )
                picture.save(output / (name + ".png"))
    finally:
        m.geom_group[:] = groups
        m.site_group[:] = site_groups
    if compiled_model_digest(m) != before:
        raise ValueError("Diagnostic rendering changed compiled world")
    cross_section(geometry, output / "treble_cross_section.png")
    return cameras


def audit_geometry(scene, geometry):
    m, d = scene.model, scene.data
    mujoco.mj_forward(m, d)
    pairs = []
    # Housing/board/bellows pairs include joins and reveal unintended overlaps.
    ids = [
        i
        for i in scene.board_geoms
        if m.geom(i).name.startswith("cba_") or m.geom(i).name == "keyboard_panel"
    ]
    for index, a in enumerate(ids):
        for b in ids[index + 1 :]:
            distance = float(mujoco.mj_geomDistance(m, d, a, b, 1, None))
            if distance < -1e-8:
                pairs.append(
                    dict(a=m.geom(a).name, b=m.geom(b).name, distance_m=distance)
                )
    target_error = max(
        float(
            np.linalg.norm(d.site("target_" + b.id).xpos - geometry.surface_world_m(b))
        )
        for b in buttons()
    )
    button_clearances = {}
    caps = [m.geom(b.id).id for b in buttons()] + [
        m.geom(name).id for name, _ in REFERENCE.bass_buttons()
    ]
    for a in caps:
        panel = "keyboard_panel" if m.geom(a).name.startswith("r") else "cba_bass_panel"
        button_clearances[m.geom(a).name] = min(
            float(mujoco.mj_geomDistance(m, d, a, b, 1, None))
            for b in ids
            if m.geom(b).name != panel
        )
    return {
        "cap_to_nonparent_component_clearances_m": button_clearances,
        "mounted_reference_diagnostics": diagnostics(
            scene, geometry.surface_world_m(button_at(1, 5))
        ),
        "component_overlaps": pairs,
        "max_target_frame_error_m": target_error,
        "specification": reference_for(geometry).specification(),
        "frames_world": {
            name: dict(
                position=d.body(name).xpos.tolist(), rotation=d.body(name).xmat.tolist()
            )
            for name in (
                MODEL,
                "treble_assembly",
                "keyboard",
                "bass_assembly",
                "bass_fingerboard",
                "closed_bellows_connection",
            )
        },
    }


def run_geometry(definition, output):
    raw = definition.read_bytes()
    e = Experiment.from_dict(json.loads(raw))
    if e.geometry.geometry_model not in (MODEL, "generic_cba_v3"):
        raise ValueError("Physical geometry diagnostic needs generic_cba_v2")
    output.mkdir(parents=True, exist_ok=True)
    (output / "experiment.json").write_bytes(raw)
    s = build_scene(
        e.geometry,
        e.player,
        e.setup,
        e.physical_contact,
        tuple(c.finger for c in e.contacts),
    )
    profiles = e.resolved_profiles()
    result = {
        "input": json.loads(raw),
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "resolved_profiles": profiles,
        "profiles_sha256": hashlib.sha256(
            json.dumps(profiles, sort_keys=True, allow_nan=False).encode()
        ).hexdigest(),
        "qpos_rad": s.data.qpos.tolist(),
        "geometry_audit": audit_geometry(s, e.geometry),
        **current_execution_metadata(s.model),
    }
    if (
        e.setup.seated is not None
        and e.setup.seated.lower_body is not None
        and e.player.model != "myoarm_r"
    ):
        result["fit_diagnostics"] = fit_diagnostics(s, e)
    result["cameras"] = render_cba(s, e.geometry, output / "renders")
    result["artifact_sha256"] = {
        str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (output / "renders").glob("*.png")
    }
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def replay_geometry(result_path, output):
    record = json.loads(result_path.read_text())
    e = Experiment.from_dict(record["input"])
    s = build_scene(
        e.geometry,
        e.player,
        e.setup,
        e.physical_contact,
        tuple(c.finger for c in e.contacts),
    )
    if compiled_model_digest(s.model) != record["provenance"]["compiled_model_sha256"]:
        raise ValueError("Different compiled world; rerun instead of replaying")
    if e.resolved_profiles() != record["resolved_profiles"]:
        # JSON tuples versus lists: canonical encoding is the strict identity.
        actual = hashlib.sha256(
            json.dumps(e.resolved_profiles(), sort_keys=True, allow_nan=False).encode()
        ).hexdigest()
        if actual != record["profiles_sha256"]:
            raise ValueError("Different profiles")
    s.data.qpos[:] = record["qpos_rad"]
    render_cba(s, e.geometry, output, record["cameras"])


def fit_diagnostics(scene, experiment):
    """Independent compiled distances and landmarks; no wearing optimization."""
    from .collision_coverage import audit_collision_coverage

    m, d = scene.model, scene.data
    mujoco.mj_forward(m, d)
    h = d.body(MODEL)
    rotation = h.xmat.reshape(3, 3)
    height = reference_for(experiment.geometry).height_m
    landmarks = {
        name: d.body(name).xpos.tolist()
        for name in (
            "humerus_r",
            "torso",
            "pelvis",
            "femur_r",
            "femur_l",
            "tibia_r",
            "tibia_l",
        )
    }
    for name, point in {
        "upper_treble": (0, 0, -0.10),
        "lower_treble": (0, height, -0.10),
        "lower_treble_rear": (0, height, -0.20),
    }.items():
        landmarks[name] = (h.xpos + rotation @ point).tolist()
    landmarks["fingerboard_c4"] = experiment.geometry.surface_world_m(
        button_at(1, 5)
    ).tolist()
    for name in ("shoulder_strap_upper", "shoulder_strap_lower"):
        landmarks[name] = d.site(name).xpos.tolist()
    root = np.asarray(experiment.setup.torso_origin_m)
    q = experiment.setup.torso_rotation_wxyz
    from scipy.spatial.transform import Rotation

    up = Rotation.from_quat([q[1], q[2], q[3], q[0]]).as_matrix()[:, 2]
    support = (
        max(
            np.dot(np.asarray(landmarks[n]) - root, up)
            for n in ("femur_r", "femur_l", "tibia_r", "tibia_l")
        )
        + experiment.setup.seated.lower_body.thigh_envelope_radius_m
    )
    corners = np.array(
        [
            h.xpos + rotation @ (u, v, n)
            for u in (-0.36, 0)
            for v in (0, height)
            for n in (-0.20, 0)
        ]
    )
    shoulder = np.asarray(landmarks["humerus_r"])
    torso_length = float(np.dot(shoulder - landmarks["pelvis"], up))
    support_distances = diagnostics(scene, landmarks["fingerboard_c4"])[
        "approximate_support_envelope_distances_m"
    ]
    # Include passive native proxies whose collision masks were disabled during
    # reduction. Bone queries use MuJoCo convex collision representation, not skin.
    instrument_bodies = {int(m.geom_bodyid[j]) for j in scene.board_geoms}
    distances = {"imported_bone_convex_hulls": {}, "all_imported_proxies": {}}
    for i in range(m.ngeom):
        if int(m.geom_bodyid[i]) in instrument_bodies or m.geom(i).name.startswith(
            "approximate_"
        ):
            continue
        category = (
            "all_imported_proxies"
            if m.geom_group[i] == 4
            else "imported_bone_convex_hulls"
            if m.geom_group[i] == 0 and m.geom_type[i] == mujoco.mjtGeom.mjGEOM_MESH
            else None
        )
        if category is None:
            continue
        value, j = min(
            (float(mujoco.mj_geomDistance(m, d, i, j, 2, None)), j)
            for j in scene.board_geoms
        )
        distances[category][m.geom(i).name or f"unnamed_geom_{i}"] = {
            "distance_m": value,
            "component": m.geom(j).name,
            "body": m.body(int(m.geom_bodyid[i])).name,
        }
    inner_reference = experiment.resolved_profiles()["setup"]["derived_anchors"][
        "right_thigh_reference_world_m"
    ]
    landmarks["right_inner_thigh_reference"] = inner_reference
    return {
        "independent_body_distances": distances,
        "lower_corner_minus_inner_thigh_reference_m": (
            np.asarray(landmarks["lower_treble"]) - inner_reference
        ).tolist(),
        "landmarks_world_m": landmarks,
        "case_bottom_above_thigh_station_plane_m": float(
            np.min((corners - root) @ up) - support
        ),
        "upper_case_minus_shoulder_m": (
            np.asarray(landmarks["upper_treble"]) - shoulder
        ).tolist(),
        "c4_minus_shoulder_m": (
            np.asarray(landmarks["fingerboard_c4"]) - shoulder
        ).tolist(),
        "lower_corner_minus_right_hip_m": (
            np.asarray(landmarks["lower_treble"]) - landmarks["femur_r"]
        ).tolist(),
        "shoulder_to_pelvis_vertical_m": torso_length,
        "case_height_over_shoulder_pelvis_vertical": height / torso_length,
        "approximate_thigh_signed_distances_m": support_distances,
        "classification": {
            name: "intersects"
            if value < 0
            else "near"
            if value <= 0.02
            else "above_or_clear"
            for name, value in support_distances.items()
        },
        "independent_proxy_coverage": audit_collision_coverage(scene),
        "limits": (
            "Bone meshes are visual imported skeleton; proxies and thigh "
            "capsules are uncalibrated envelopes. No skin, strap equilibrium "
            "or comfort inference."
        ),
    }


def compare_fit_renders(root, output):
    """Compose saved-state views without recentering/scaling individual candidates."""
    output.mkdir(parents=True, exist_ok=True)
    groups = {
        "size": ("compact-upper", "tall-upper"),
        "placement": ("compact-low", "compact-upper", "compact-high"),
        "coupled": ("historical-plane", "compact-upper", "tall-high"),
    }
    manifest = {}
    for group, names in groups.items():
        for view in ("front", "right", "left", "oblique", "hand"):
            sheet = Image.new("RGB", (640 * len(names), 510), "white")
            draw = ImageDraw.Draw(sheet)
            for column, name in enumerate(names):
                path = root / name / "renders" / f"body_{view}.png"
                picture = Image.open(path).convert("RGB").resize((640, 480))
                sheet.paste(picture, (640 * column, 30))
                draw.text((640 * column + 12, 10), name, fill="black")
                manifest[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            path = output / f"{group}_{view}.png"
            sheet.save(path)
            manifest[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
