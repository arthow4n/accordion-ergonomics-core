"""Physical saved-state playback synchronized with computed board-coordinate plots."""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .digits import DIGITS
from .experiment import Experiment
from .movement_evidence import trajectory_frame_indices
from .passage_media import render_strategy
from .quality_plots import trace_svg
from .render import render_views

COLORS = ("#20a0dd", "#ee9e35", "#b268d5", "#5ab65d", "#e05b70")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def board_panel(records, *, sample_index=None, size=(1000, 900), bounds=None):
    """Shared metric axes from all supplied actual traces, top + normal-side views."""
    image = Image.new("RGB", size, "#f5f7fa")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 14 if size[0] < 600 else 19)
    small = ImageFont.truetype(FONT, 11 if size[0] < 600 else 15)
    width, height = size
    caps = records[0]["frame"]["caps"]
    traces = [r for record in records for r in record["traces"]]
    all_points = (
        np.array(
            [
                r["landmarks_board_m"][k]
                for r in traces
                for k in ("wrist", "capitate", "knuckle_index", "knuckle_little")
            ]
            + [p for r in traces for p in r["fingertips_board_m"].values()]
            + [c["surface_board_m"] for c in caps]
        )
        * 1000
    )
    if bounds is not None:
        all_points = np.asarray(bounds) * 1000
    for panel, axes in enumerate(((0, 1), (1, 2))):
        left, right, top, bottom = (
            48,
            width - 18,
            70 + panel * height / 2,
            (panel + 1) * height / 2 - 55,
        )
        low = all_points[:, axes].min(axis=0) - 12
        high = all_points[:, axes].max(axis=0) + 12
        scale = min(
            (right - left) / (high[0] - low[0]), (bottom - top) / (high[1] - low[1])
        )

        def xy(
            p,
            axes=axes,
            left=left,
            low=low,
            scale=scale,
            bottom=bottom,
            panel=panel,
            top=top,
        ):
            a = np.asarray(p)[list(axes)] * 1000
            # Higher n goes up in side view; higher v down in top view.
            return (
                left + (a[0] - low[0]) * scale,
                bottom - (a[1] - low[1]) * scale
                if panel
                else top + (a[1] - low[1]) * scale,
            )

        draw.text(
            (8, top - 56),
            "TOP: +u outer -> / +v pitch down"
            if not panel
            else "SIDE: +v pitch -> / +n away up",
            fill="#142030",
            font=font,
        )
        draw.text(
            (8, top - 32),
            "mm; actual saved FK / no playing boundary",
            fill="#415066",
            font=small,
        )
        for c in caps:
            x, y = xy(c["surface_board_m"])
            radius = max(2, 4 * scale)
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                outline="#a5b1bd",
                width=1,
            )
        # Explicit scale bar.
        ybar = bottom + 15
        draw.line((left, ybar, left + 20 * scale, ybar), fill="#142030", width=2)
        draw.text((left, ybar + 3), "20 mm", fill="#142030", font=small)
        for record_index, record in enumerate(records):
            rows = record["traces"]
            selected = len(rows) - 1 if sample_index is None else sample_index
            end = rows[selected]
            for kind, color in zip(
                ("wrist", "capitate", "knuckle_index", "knuckle_little"),
                COLORS,
                strict=False,
            ):
                color = color if len(records) == 1 else COLORS[record_index]
                points = [xy(r["landmarks_board_m"][kind]) for r in rows]
                draw.line(points, fill=color, width=2 if kind == "capitate" else 1)
                x, y = points[selected]
                draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)
                if sample_index is None:
                    for r in rows:
                        if r["event_index"] is not None:
                            x, y = xy(r["landmarks_board_m"][kind])
                            if kind == "capitate":
                                draw.text(
                                    (x + 3, y),
                                    str(r["event_index"]),
                                    font=small,
                                    fill=color,
                                )
            if len(records) == 1:
                for digit, color in zip(DIGITS, COLORS, strict=True):
                    points = [xy(r["fingertips_board_m"][digit]) for r in rows]
                    draw.line(points, fill=color, width=1)
            relevant = {c["button_id"] for r in rows for c in r["active_contacts"]}
            current = (
                {c["button_id"] for c in end["active_contacts"]}
                if sample_index is not None
                else set()
            )
            upcoming = (
                {c["button_id"] for c in end["upcoming_contacts"]}
                if sample_index is not None
                else set()
            )
            for c in caps:
                if c["id"] in relevant:
                    x, y = xy(c["surface_board_m"])
                    draw.rectangle(
                        (x - 4, y - 4, x + 4, y + 4),
                        outline=(
                            "#207630"
                            if c["id"] in current
                            else "#cc7000"
                            if c["id"] in upcoming
                            else "#111111"
                        ),
                        width=2,
                    )
                    if not panel:
                        draw.text(
                            (x + 4, y),
                            f"{c['id']}:{c['midi']}",
                            font=small,
                            fill="#142030",
                        )
            label = record.get("label", "recorded hand")
            draw.text(
                (8, bottom - 18 - 19 * record_index),
                label[:65],
                fill=COLORS[record_index],
                font=small,
            )
    legend = (
        "wrist blue | capitate orange | index knuckle purple | little knuckle green"
    )
    if len(records) > 1:
        legend = "Each strategy one color; wrist/palm/knuckles; numbers = events"
    draw.text((8, height - 22), legend, font=small, fill="#142030")
    return image


def lifecycle_plots(record, output):
    traces = record["traces"]
    if "binding_distances_m" not in traces[0]:
        return
    # Each interval has its own bindings; avoid drawing across absent observations.
    panels = []
    for interval in record["intervals"]:
        rows = [traces[i] for i in interval["sample_indices"]]
        keys = sorted(set.intersection(*(set(r["binding_distances_m"]) for r in rows)))
        if keys:
            panels.append(
                dict(
                    label=(
                        f"Event {interval['event_interval']} -> next: "
                        "distal outer-envelope/cap distance (m)"
                    ),
                    series={
                        key: [r["binding_distances_m"][key] for r in rows]
                        for key in keys
                    },
                )
            )
    if panels:
        trace_svg(
            output / "contact-distances.svg",
            "Geometric release / recontact; button actuation unknown",
            panels,
            x_axis="interval-local recorded sample order (not time)",
        )


def event_diagram(saved, strategy, record, path):
    from html import escape

    events = strategy["events"]
    width = 1200
    height = 115 + len(events) * 105
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        '<rect width="100%" height="100%" fill="#f5f7fa"/>'
        '<g font-family="monospace" fill="#142030">',
        (
            '<text x="20" y="28" font-size="18">Actual musical '
            "events / modeled contact lifecycle "
            "(untimed)</text>"
        ),
        (
            '<text x="20" y="52" font-size="13">Initial '
            "approach unplanned. Near a cap does not establish "
            "a sounding note. Actuation unknown.</text>"
        ),
    ]
    nodes = {n["id"]: n for n in saved["nodes"]}
    for i, event in enumerate(events):
        y = 90 + i * 105
        labels = "; ".join(
            f"MIDI {c['midi']} {c['button_id']} {c['finger']} ({c['behavior']})"
            for c in event["contacts"]
        )
        prep = nodes[strategy["node_ids"][i]].get("preparing", [])
        lines.append(
            f'<text x="20" y="{y}" font-size="14">Event {i}: {escape(labels)}</text>'
        )
        lines.append(
            f'<text x="20" y="{y + 22}" font-size="12">Preparing: {escape(str(prep))}; '
            "hypothesis, next chosen binding may differ</text>"
        )
        if i < len(record["intervals"]):
            interval = record["intervals"][i]
            lifecycle = interval.get("lifecycle", {})
            releases = ", ".join(
                c["contact"]["finger"] + ": " + c["status"]
                for c in lifecycle.get("releases", [])
            )
            text = (
                "Held preserved: "
                f"{lifecycle.get('held_contact_preserved', 'not assessed')}; "
                f"releases: {releases}"
            )
            phases = list(
                dict.fromkeys(
                    record["traces"][j]["phase"] for j in interval["sample_indices"]
                )
            )
            lines += [
                f'<text x="35" y="{y + 45}" font-size="12">{escape(text)}</text>',
                f'<text x="35" y="{y + 66}" font-size="12">Samples '
                f"{interval['sample_indices'][0]}..{interval['sample_indices'][-1]}: "
                f"{escape(' / '.join(phases))}</text>",
            ]
    lines.append("</g></svg>")
    path.write_text("\n".join(lines) + "\n")


def render_playing_evidence(
    scene, saved, strategy, region, audit, whole, output, cameras, frames, bounds=None
):
    output.mkdir(parents=True, exist_ok=True)
    rows = region["traces"]
    key_indices = {0, len(rows) - 1, whole["worst_proxy_sample_index"]}
    key_indices |= {
        i for i, s in enumerate(strategy["samples"]) if s.get("event_index") is not None
    }
    palm = np.array([r["landmarks_board_m"]["capitate"] for r in rows])
    q = np.array([s["qpos_rad"] for s in strategy["samples"]])
    key_indices |= {int(np.argmax(palm[:, 2])), int(np.argmin(palm[:, 0]))}
    for joint in ("flexion_r", "deviation_r"):
        key_indices.add(int(np.argmax(np.abs(q[:, saved["joint_names"].index(joint)]))))
    for interval in region["intervals"]:
        for release in interval.get("lifecycle", {}).get("releases", []):
            separated = release["separation_sample_indices"]
            if separated:
                key_indices |= {separated[0], separated[-1]}
    indices = sorted(set(trajectory_frame_indices(strategy, frames)) | key_indices)
    animation = render_strategy(
        scene,
        saved,
        strategy,
        audit,
        output / "dense",
        len(indices),
        {"hand": cameras["hand"]} if cameras else None,
        "actual untimed path / initial approach unplanned",
        sample_indices=indices,
    )
    composite = []
    for frame in animation["frames"]:
        im = Image.open(output / "dense" / frame["frame"]).convert("RGB")
        canvas = Image.new("RGB", (im.width + 480, im.height))
        canvas.paste(im, (0, 0))
        canvas.paste(
            board_panel(
                [region],
                sample_index=frame["sample_index"],
                size=(480, im.height),
                bounds=bounds,
            ),
            (im.width, 0),
        )
        composite.append(canvas)
    composite[0].save(
        output / "detailed.gif",
        save_all=True,
        append_images=composite[1:],
        duration=130,
        loop=0,
    )
    keyframes = [composite[indices.index(i)] for i in sorted(key_indices)]
    keyframes[0].save(
        output / "keyframes.gif",
        save_all=True,
        append_images=keyframes[1:],
        duration=450,
        loop=0,
    )
    board_panel([region], bounds=bounds).save(output / "board-path.png")
    lifecycle_plots(region, output)
    event_diagram(saved, strategy, region, output / "events.svg")
    static = []
    e = Experiment.from_dict(saved["scene_input"])
    from .instrument import button_at

    for index in sorted(
        {
            0,
            whole["worst_proxy_sample_index"],
            int(np.argmax(palm[:, 2])),
            len(rows) - 1,
        }
    ):
        sample = strategy["samples"][index]
        scene.data.qpos[:] = sample["qpos_rad"]
        c = (sample["active_contacts"] or region["traces"][index]["upcoming_contacts"])[
            0
        ]
        actual = render_views(
            scene,
            output / f"state-{index}",
            e.geometry.surface_world_m(button_at(c["row"], c["column"])).tolist(),
            c["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=tuple(
                whole["traces"][index]["worst_cross_digit_pair"]
            ),
            contact_roles=sample["roles"],
            state_label=(
                f"actual sample {index}; unresolved proxies; initial approach unplanned"
            ),
            camera_overrides=cameras,
        )
        static.append(
            dict(
                sample_index=index,
                qpos_rad=sample["qpos_rad"],
                active_contacts=sample["active_contacts"],
                cameras=actual,
                directory=f"state-{index}",
            )
        )
    return dict(
        dense=animation,
        keyframe_sample_indices=sorted(key_indices),
        static_states=static,
        detailed="detailed.gif",
        keyframes="keyframes.gif",
        board="board-path.png",
        events="events.svg",
        board_bounds_m=bounds,
        sampling=(
            "Uniform saved-sample index plus actual events, "
            "release boundaries and diagnostic extrema; no "
            "invented states or physiological time"
        ),
        synchronized_panel=(
            "Computed FK on matched metric axes; a diagram, "
            "not additional physical geometry"
        ),
    )
