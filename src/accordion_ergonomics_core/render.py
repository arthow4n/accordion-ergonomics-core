"""Four deterministic diagnostic views from the saved numerical state."""

from math import atan2, degrees, isfinite
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from ._engine import mujoco
from .scene import Scene


def render_views(
    scene: Scene,
    output: Path,
    target: list[float],
    button_id: str,
    collision_overlay: bool = False,
    highlighted_proxy_names: tuple[str, ...] = (),
    views_to_render: tuple[str, ...] | None = None,
    contact_roles: dict[str, str] | None = None,
    closeup: bool = False,
    button_roles: dict[str, str] | None = None,
    state_label: str | None = None,
    camera_overrides: dict[str, dict[str, Any]] | None = None,
    highlighted_tendon_names: tuple[str, ...] = (),
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    views: dict[str, dict[str, Any]] = {
        "overview": {
            "lookat": [0.06, 0.1, 1.35],
            "distance": 1.3,
            "azimuth": -110.0,
            "elevation": -12.0,
        },
        "keyboard": {
            "lookat": [0.22, 0.22, 1.18],
            "distance": 0.65,
            "azimuth": -90.0,
            "elevation": 0.0,
        },
        "side": {
            "lookat": [0.2, 0.12, 1.2],
            "distance": 0.85,
            "azimuth": 180.0,
            "elevation": 0.0,
        },
        "hand": {
            "lookat": target,
            "distance": 0.28,
            "azimuth": -65.0,
            "elevation": -25.0,
        },
    }
    physical = any(
        scene.model.body(i).name == "generic_cba_v2" for i in range(scene.model.nbody)
    )
    seated = physical or any(
        scene.model.geom(i).name == "instrument_envelope"
        for i in range(scene.model.ngeom)
    )
    if not seated:
        mujoco.mj_forward(scene.model, scene.data)
        shift = scene.data.body("Full Body").xpos - [0.0, 0.0, 1.0]
        for name in ("overview", "keyboard", "side"):
            views[name]["lookat"] = (shift + views[name]["lookat"]).tolist()
    if seated:
        mujoco.mj_forward(scene.model, scene.data)
        center = (
            scene.data.body("generic_cba_v2").xpos.tolist()
            if physical
            else scene.data.geom("instrument_envelope").xpos.tolist()
        )
        views["overview"] = dict(
            lookat=center, distance=1.15, azimuth=-125.0, elevation=-12.0
        )
        views["keyboard"] = dict(
            lookat=center, distance=1.0, azimuth=-90.0, elevation=0.0
        )
        views["side"] = dict(lookat=center, distance=1.0, azimuth=180.0, elevation=0.0)
        views["hand"] = dict(
            lookat=target, distance=0.55, azimuth=-55.0, elevation=-15.0
        )
    if seated and any(
        scene.model.body(i).name in ("seated_pelvis", "pelvis")
        for i in range(scene.model.nbody)
    ):
        center = (
            scene.data.body("generic_cba_v2").xpos.tolist()
            if physical
            else scene.data.geom("instrument_envelope").xpos.tolist()
        )
        center[2] = (
            scene.data.body("Full Body").xpos[2] + scene.data.body("head").xpos[2]
        ) / 2 - 0.15
        for name in ("overview", "keyboard", "side"):
            views[name]["lookat"] = center
            views[name]["distance"] = 1.95
    if physical:
        normal = scene.data.body("keyboard").xmat.reshape(3, 3)[:, 2]
        facing = degrees(atan2(-normal[1], -normal[0]))
        views["hand"] = dict(
            lookat=((scene.data.body("capitate_r").xpos + target) / 2).tolist(),
            distance=0.42,
            azimuth=facing,
            elevation=-20.0,
        )
    if closeup:
        views["contact"] = {
            **views["hand"],
            "lookat": target,
            "distance": 0.18,
            "azimuth": views["hand"]["azimuth"] - 55,
            "elevation": -10.0,
        }
    if highlighted_tendon_names:
        mujoco.mj_forward(scene.model, scene.data)
        tid = scene.model.tendon(highlighted_tendon_names[0]).id
        adr, num = int(scene.data.ten_wrapadr[tid]), int(scene.data.ten_wrapnum[tid])
        points = scene.data.wrap_xpos.reshape(-1, 3)[adr : adr + num]
        views["tendon"] = dict(views["hand"])
        views["tendon"].update(lookat=points.mean(axis=0).tolist(), distance=0.35)
    if collision_overlay:
        views["collision"] = dict(views["hand"])
        if closeup:
            views["contact_collision"] = dict(views["contact"])
    for name, values in (camera_overrides or {}).items():
        if name not in views or set(values) != {
            "lookat",
            "distance",
            "azimuth",
            "elevation",
        }:
            raise ValueError(
                "Camera override must identify a complete diagnostic camera"
            )
        if (
            len(values["lookat"]) != 3
            or values["distance"] <= 0
            or not all(
                isfinite(v)
                for v in (
                    *values["lookat"],
                    values["distance"],
                    values["azimuth"],
                    values["elevation"],
                )
            )
        ):
            raise ValueError("Camera override requires finite dimensions")
        views[name] = dict(values)
    if views_to_render is not None:
        if not views_to_render or set(views_to_render) - set(views):
            raise ValueError("Unknown or empty diagnostic view selection")
        views = {name: views[name] for name in views_to_render}
    # qpos changes do not update Cartesian geometry until forward kinematics.
    mujoco.mj_forward(scene.model, scene.data)
    colors = {
        "required": [1.0, 0.5, 0.05, 1.0],
        "attempted": [1.0, 0.2, 0.15, 1.0],
        "held": [0.1, 0.9, 1.0, 1.0],
        "moving": [0.95, 0.85, 0.1, 1.0],
        "preparing": [0.7, 0.5, 1.0, 1.0],
        "free": [0.5, 0.7, 0.5, 1.0],
        "released": [0.6, 0.6, 0.6, 1.0],
        "frozen": [0.5, 0.5, 0.7, 1.0],
    }
    from .anatomy import DIGITS

    if contact_roles is not None and (
        set(contact_roles) - set(DIGITS) or set(contact_roles.values()) - set(colors)
    ):
        raise ValueError("Unknown recorded contact role")
    if button_roles is not None and set(button_roles.values()) - set(colors):
        raise ValueError("Unknown recorded button role")
    site_rgba = scene.model.site_rgba.copy()
    rgba = scene.model.geom_rgba.copy()
    groups = scene.model.geom_group.copy()
    materials = scene.model.geom_matid.copy()
    tendon_rgba = scene.model.tendon_rgba.copy()
    tendon_width = scene.model.tendon_width.copy()
    try:
        if contact_roles is not None:
            for digit in DIGITS:
                ids = [
                    i
                    for i in range(scene.model.nsite)
                    if scene.model.site(i).name == f"{digit}_pad"
                ]
                if ids:
                    scene.model.site_rgba[ids[0]] = (
                        [0.1, 1.0, 0.2, 1.0]
                        if contact_roles.get(digit) == "required"
                        else colors[contact_roles.get(digit, "free")]
                    )
        scene.model.geom(button_id).rgba[:] = [1.0, 0.5, 0.05, 1.0]
        for button, role in (button_roles or {}).items():
            scene.model.geom(button).rgba[:] = colors[role]
        option = mujoco.MjvOption()
        option.geomgroup[3] = 0  # muscle wrapping objects are not body surfaces
        option.sitegroup[:] = 0
        option.sitegroup[0] = 1
        option.tendongroup[:] = 1
        option.flags[mujoco.mjtVisFlag.mjVIS_TENDON] = bool(highlighted_tendon_names)
        if highlighted_tendon_names:
            scene.model.tendon_rgba[:, 3] = 0
            for tendon in highlighted_tendon_names:
                tid = scene.model.tendon(tendon).id
                scene.model.tendon_rgba[tid] = [1, 0.85, 0.1, 1]
                scene.model.tendon_width[tid] = 0.0015
        with mujoco.Renderer(scene.model, height=720, width=960) as renderer:
            for name, settings in views.items():
                if name in ("collision", "contact_collision"):
                    # Show the actual contact proxies without the visual bone meshes.
                    option.geomgroup[0] = 0
                    option.geomgroup[4] = 1
                    for geom_id in scene.anatomy_geoms:
                        scene.model.geom_matid[geom_id] = -1
                    for geom_id in scene.board_geoms:
                        scene.model.geom_group[geom_id] = 2
                    for contact in scene.data.contact:
                        if contact.dist < 0:
                            for geom_id in (int(contact.geom1), int(contact.geom2)):
                                scene.model.geom_rgba[geom_id] = [1.0, 0.1, 0.1, 0.9]
                    for proxy_name in highlighted_proxy_names:
                        scene.model.geom(proxy_name).rgba[:] = [0.95, 0.1, 0.9, 1.0]
                if name == "tendon":
                    option.geomgroup[0] = 0
                    option.geomgroup[4] = 0
                    # Tendon routes remain visible without occluding bone meshes.
                    option.geomgroup[3] = 0
                camera = mujoco.MjvCamera()
                camera.type = mujoco.mjtCamera.mjCAMERA_FREE
                camera.lookat[:] = settings["lookat"]
                camera.distance = settings["distance"]
                camera.azimuth = settings["azimuth"]
                camera.elevation = settings["elevation"]
                renderer.update_scene(scene.data, camera=camera, scene_option=option)
                picture = Image.fromarray(renderer.render())
                draw = ImageDraw.Draw(picture)
                draw.rectangle((0, 0, 960, 45), fill=(18, 25, 36))
                label = (
                    (
                        "generic CBA v3"
                        if any(
                            scene.model.site(i).name == "fit_upper_case"
                            for i in range(scene.model.nsite)
                        )
                        else "generic CBA v2"
                    )
                    if physical
                    else "seated setup / assumed shell"
                    if seated
                    else "synthetic board"
                )
                draw.text(
                    (12, 10),
                    (
                        f"{name} | {label} | {button_id} "
                        + (
                            button_roles[button_id]
                            if button_roles and button_id in button_roles
                            else "orange"
                        )
                    ),
                    fill=(255, 255, 255),
                )
                draw.text(
                    (12, 26),
                    (
                        "Magenta: unchecked proxy overlap; not engine contact"
                        if name in ("collision", "contact_collision")
                        and highlighted_proxy_names
                        else "Board axes: red outward / green down (higher pitch) / "
                        "blue surface normal"
                    ),
                    fill=(220, 225, 230),
                )
                if contact_roles is not None:
                    draw.rectangle((0, 674, 960, 720), fill=(18, 25, 36))
                    draw.text(
                        (12, 682),
                        " | ".join(
                            f"{d}: {contact_roles.get(d, 'free')}" for d in DIGITS
                        ),
                        fill=(255, 255, 255),
                    )
                    draw.text(
                        (12, 700),
                        (state_label or "Saved kinematic state")
                        + "; anatomy unresolved",
                        fill=(240, 200, 180),
                    )
                picture.save(output / f"{name}.png")
    finally:
        scene.model.tendon_rgba[:] = tendon_rgba
        scene.model.tendon_width[:] = tendon_width
        scene.model.site_rgba[:] = site_rgba
        scene.model.geom_rgba[:] = rgba
        scene.model.geom_group[:] = groups
        scene.model.geom_matid[:] = materials
    return views
