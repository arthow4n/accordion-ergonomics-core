"""Four deterministic diagnostic views from the saved numerical state."""

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
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    views = {
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
    if collision_overlay:
        views["collision"] = dict(views["hand"])
    # qpos changes do not update Cartesian geometry until forward kinematics.
    mujoco.mj_forward(scene.model, scene.data)
    rgba = scene.model.geom_rgba.copy()
    groups = scene.model.geom_group.copy()
    materials = scene.model.geom_matid.copy()
    try:
        scene.model.geom(button_id).rgba[:] = [1.0, 0.5, 0.05, 1.0]
        option = mujoco.MjvOption()
        option.geomgroup[3] = 0  # muscle wrapping objects are not body surfaces
        option.sitegroup[:] = 0
        option.sitegroup[0] = 1
        option.flags[mujoco.mjtVisFlag.mjVIS_TENDON] = False
        with mujoco.Renderer(scene.model, height=720, width=960) as renderer:
            for name, settings in views.items():
                if name == "collision":
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
                draw.text(
                    (12, 10),
                    f"{name} | synthetic board | {button_id} orange | index pad green",
                    fill=(255, 255, 255),
                )
                draw.text(
                    (12, 26),
                    (
                        "Magenta: unchecked proxy overlap; not engine contact"
                        if name == "collision" and highlighted_proxy_names
                        else "Board axes: red outward / green down (higher pitch) / "
                        "blue surface normal"
                    ),
                    fill=(220, 225, 230),
                )
                picture.save(output / f"{name}.png")
    finally:
        scene.model.geom_rgba[:] = rgba
        scene.model.geom_group[:] = groups
        scene.model.geom_matid[:] = materials
    return views
