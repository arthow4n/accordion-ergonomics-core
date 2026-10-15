"""Board-relative FK and musical lifecycle observations of recorded movement.

Distances concern unchanged rigid proxies. No skin, actuation or human boundary.
"""

from typing import Any

import numpy as np

from ._engine import mujoco
from .digits import DIGITS, DISTAL_BINDINGS
from .instrument import buttons
from .movement_evidence import state_digest
from .passage_search import contact_check

# Body origins at imported joints; metacarpal origins are distinct from knuckles.
LANDMARKS = {
    "wrist": "lunate_r",
    "capitate": "capitate_r",
    **{
        f"metacarpal_{f}": b
        for f, b in zip(
            DIGITS,
            ("firstmc_r", "secondmc_r", "thirdmc_r", "fourthmc_r", "fifthmc_r"),
            strict=True,
        )
    },
    **{
        f"knuckle_{f}": b
        for f, b in zip(
            DIGITS,
            ("proximal_thumb_r", "2proxph_r", "3proxph_r", "4proxph_r", "5proxph_r"),
            strict=True,
        )
    },
}


def board_coordinates(geometry, world):
    """Row vectors in world -> row vectors in canonical board (+outer,+pitch,+out)."""
    return (np.asarray(world) - geometry.origin_m) @ geometry.rotation


def compiled_board_frame(scene, geometry):
    mujoco.mj_forward(scene.model, scene.data)
    rotation = scene.data.body("keyboard").xmat.reshape(3, 3)
    origin = scene.data.body("keyboard").xpos
    if not np.allclose(rotation, geometry.rotation, atol=1e-12) or not np.allclose(
        origin, geometry.origin_m, atol=1e-12
    ):
        raise ValueError("Compiled keyboard disagrees with canonical frame")
    caps: list[dict[str, Any]] = []
    for b in buttons():
        actual = scene.data.geom(b.id).xpos.copy()
        # Surface target differs from cap center in n only.
        local = board_coordinates(geometry, geometry.surface_world_m(b))
        actual_local = board_coordinates(geometry, actual)
        if not np.allclose(actual_local[:2], local[:2], atol=1e-12):
            raise ValueError("Compiled physical cap differs from target row/column")
        caps.append(
            dict(
                id=b.id,
                row=b.row,
                column=b.column,
                midi=b.midi,
                surface_board_m=local.tolist(),
                center_board_m=actual_local.tolist(),
            )
        )
    row_u = [
        next(c for c in caps if c["row"] == r)["surface_board_m"][0]
        for r in range(1, 6)
    ]
    if not np.all(np.diff(row_u) < 0):
        raise ValueError("Increasing physical row must move inward (-u)")
    return dict(
        origin_world_m=origin.tolist(),
        rotation_world_from_board=rotation.tolist(),
        directions=["+u outer / decreasing row", "+v increasing pitch", "+n outward"],
        caps=caps,
        landmark_bodies=LANDMARKS,
        orientation_claim="Imported body axes; no calibrated palmar plane",
    )


def distal_cap_distance(scene, finger, button_id):
    """Outer union of BOTH overlapping distal proxies, never marker-only contact."""
    return min(
        float(
            mujoco.mj_geomDistance(
                scene.model,
                scene.data,
                scene.model.geom(g).id,
                scene.model.geom(button_id).id,
                1.0,
                None,
            )
        )
        for g in DISTAL_BINDINGS[finger][1:3]
    )


def proximity_class(distance, contact_band):
    if distance < -contact_band:
        return "proxy_intersection"
    if distance <= contact_band:
        return "near_cap_actuation_unknown"
    return "geometrically_separated"


def lifecycle_summary(source, destination, observations, band):
    """Per-edge release/hold/recontact; an observed separation, not measured travel."""
    held = [c for c in source if c["behavior"] == "hold"]
    released = [c for c in source if c["behavior"] != "hold"]
    releases = []
    for c in released:
        key = c["finger"] + ":" + c["button_id"]
        values = [s["binding_distances_m"][key] for s in observations]
        separated = [
            s["sample_index"]
            for s, v in zip(observations, values, strict=True)
            if v > band
        ]
        releases.append(
            dict(
                contact=c,
                maximum_signed_distance_m=max(values),
                separation_sample_indices=separated,
                status="released_geometrically"
                if separated
                else "release_not_demonstrated",
                recontact_required=any(
                    d["button_id"] == c["button_id"] for d in destination
                ),
            )
        )
    held_checks = [s["held_contact_satisfied"] for s in observations]
    return dict(
        releases=releases,
        held_contacts=held,
        held_contact_preserved=all(held_checks),
        held_violation_sample_indices=[
            s["sample_index"] for s in observations if not s["held_contact_satisfied"]
        ],
        next_target_contact_established=observations[-1][
            "destination_contact_satisfied"
        ],
        source_contact_established=observations[0]["source_contact_satisfied"],
        geometric_release_band_m=band,
        release_band_provenance=(
            "Existing endpoint position tolerance; diagnostic "
            "separation outside contact acceptance band, not "
            "measured button travel"
        ),
        mechanical_actuation="unknown",
    )


def playing_region_trace(scene, e, strategy, *, lifecycle=True):
    """Compute every saved sample; relevant region uses actual current/upcoming caps."""
    frame = compiled_board_frame(scene, e.geometry)
    samples, events = strategy["samples"], strategy["events"]
    traces: list[dict[str, Any]] = []
    # All digit proxies for incidental cap observations, independently of masks.
    digit_geoms = {}
    for digit, root in zip(
        DIGITS,
        ("firstmc_r", "secondmc_r", "thirdmc_r", "fourthmc_r", "fifthmc_r"),
        strict=True,
    ):
        bodies = {scene.model.body(root).id}
        for body in range(scene.model.nbody):
            if int(scene.model.body_parentid[body]) in bodies:
                bodies.add(body)
        digit_geoms[digit] = [
            g for g in scene.anatomy_geoms if int(scene.model.geom_bodyid[g]) in bodies
        ]
    band = e.solver.position_tolerance_m
    for index, sample in enumerate(samples):
        interval = sample["event_interval"]
        source, destination = (
            events[interval]["contacts"],
            events[interval + 1]["contacts"],
        )
        held = [c for c in source if c["behavior"] == "hold"]
        scene.data.qpos[:] = sample["qpos_rad"]
        mujoco.mj_forward(scene.model, scene.data)
        landmarks = {
            name: board_coordinates(e.geometry, scene.data.body(body).xpos).tolist()
            for name, body in LANDMARKS.items()
        }
        tips = {
            digit: board_coordinates(
                e.geometry, scene.data.site(f"{digit}_pad").xpos
            ).tolist()
            for digit in DIGITS
        }
        relevant = {c["button_id"] for c in source + destination}
        caps = np.array(
            [c["surface_board_m"] for c in frame["caps"] if c["id"] in relevant]
        )
        palm = np.asarray(landmarks["capitate"])
        row = dict(
            sample_index=index,
            event_index=sample.get("event_index"),
            event_interval=interval,
            phase=sample.get("phase", {}).get("phase", "recorded_connection"),
            active_contacts=sample.get("active_contacts", []),
            upcoming_contacts=destination,
            roles=sample.get("roles", {}),
            landmarks_board_m=landmarks,
            fingertips_board_m=tips,
            body_axes_in_board={
                body: (
                    e.geometry.rotation.T @ scene.data.body(body).xmat.reshape(3, 3)
                ).tolist()
                for body in ("capitate_r", "lunate_r", "radius_r")
            },
            relevant_button_ids=sorted(relevant),
            palm_offset_from_relevant_cap_centroid_m=(
                palm - caps.mean(axis=0)
            ).tolist(),
            palm_nearest_relevant_cap_planar_distance_m=float(
                np.linalg.norm(caps[:, :2] - palm[:2], axis=1).min()
            ),
        )
        if lifecycle:
            bindings = {(c["finger"], c["button_id"]) for c in source + destination}
            distances = {
                f + ":" + b: distal_cap_distance(scene, f, b) for f, b in bindings
            }
            active = {
                (c["finger"], c["button_id"]) for c in sample.get("active_contacts", [])
            }
            near = []
            for digit in DIGITS:
                for cap in frame["caps"]:
                    if (digit, cap["id"]) in active:
                        continue
                    distance = min(
                        float(
                            mujoco.mj_geomDistance(
                                scene.model,
                                scene.data,
                                g,
                                scene.model.geom(cap["id"]).id,
                                1.0,
                                None,
                            )
                        )
                        for g in digit_geoms[digit]
                    )
                    if distance <= band:
                        near.append(
                            dict(
                                finger=digit,
                                button_id=cap["id"],
                                signed_proxy_distance_m=distance,
                                classification=proximity_class(distance, band),
                                task_relation="source_or_upcoming"
                                if cap["id"] in relevant
                                else "other_cap",
                                mechanical_actuation="unknown",
                            )
                        )
            row.update(
                binding_distances_m=distances,
                incidental_caps=near,
                held_contact_satisfied=contact_check(scene, e, held)["satisfied"],
                source_contact_satisfied=contact_check(scene, e, source)["satisfied"]
                if sample.get("event_index") == interval
                else None,
                destination_contact_satisfied=contact_check(scene, e, destination)[
                    "satisfied"
                ]
                if sample.get("event_index") == interval + 1
                else None,
            )
        traces.append(row)
    intervals = []
    # Include shared event boundary in both adjacent edge observations.
    for i in range(len(events) - 1):
        indices = [j for j, s in enumerate(samples) if s["event_interval"] == i]
        if i and samples[indices[0]].get("event_index") != i:
            indices.insert(0, indices[0] - 1)
        rows = [dict(traces[j]) for j in indices]
        palm = np.array([r["landmarks_board_m"]["capitate"] for r in rows])
        length = float(np.linalg.norm(np.diff(palm, axis=0), axis=1).sum())
        displacement = float(np.linalg.norm(palm[-1] - palm[0]))
        record = dict(
            event_interval=i,
            sample_indices=indices,
            palm_path_m=length,
            palm_displacement_m=displacement,
            detour_ratio=length / displacement if displacement > 1e-9 else None,
        )
        if lifecycle:
            # Recheck shared event boundaries with this interval's requirements.
            for row, event in ((rows[0], i), (rows[-1], i + 1)):
                scene.data.qpos[:] = samples[row["sample_index"]]["qpos_rad"]
                row[
                    "source_contact_satisfied"
                    if event == i
                    else "destination_contact_satisfied"
                ] = contact_check(scene, e, events[event]["contacts"])["satisfied"]
                row["binding_distances_m"] = {
                    c["finger"] + ":" + c["button_id"]: distal_cap_distance(
                        scene, c["finger"], c["button_id"]
                    )
                    for c in events[i]["contacts"] + events[i + 1]["contacts"]
                }
                row["held_contact_satisfied"] = contact_check(
                    scene,
                    e,
                    [c for c in events[i]["contacts"] if c["behavior"] == "hold"],
                )["satisfied"]
            record["lifecycle"] = lifecycle_summary(
                events[i]["contacts"], events[i + 1]["contacts"], rows, band
            )
        intervals.append(record)
    summary = {}
    for name in LANDMARKS:
        p = np.array([r["landmarks_board_m"][name] for r in traces])
        summary[name] = dict(
            minimum_board_m=p.min(axis=0).tolist(),
            maximum_board_m=p.max(axis=0).tolist(),
            axis_total_variation_m=np.abs(np.diff(p, axis=0)).sum(axis=0).tolist(),
            path_m=float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()),
        )
    return dict(
        version="playing-region-lifecycle-v3",
        frame=frame,
        state_sequence_sha256=state_digest(samples),
        sample_count=len(samples),
        traces=traces,
        landmarks=summary,
        intervals=intervals,
        initial_approach="unplanned_reference_to_first_contact",
        interpretation=(
            "Descriptive actual FK; no rigid playing region, "
            "measured release travel, timing, comfort or "
            "tissue validity"
        ),
    )


def preparation_linkage(events):
    """Bind optional preparation to the actual next finger AND physical button."""
    links = []
    for i, event in enumerate(events):
        controls = event.get("preparing_controls", [])
        selected = events[i + 1]["contacts"] if i + 1 < len(events) else []
        links.append(
            dict(
                event_index=i,
                controls=controls,
                selected_next_contacts=selected,
                matched_next_bindings=[
                    c
                    for c in controls
                    if any(
                        c["finger"] == n["finger"] and c["button_id"] == n["button_id"]
                        for n in selected
                    )
                ],
            )
        )
    return links
