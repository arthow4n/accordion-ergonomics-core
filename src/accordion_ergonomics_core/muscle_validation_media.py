"""Model-grounded static screen/routing evidence; no activation artwork or dynamics."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .instrument import button_at
from .passage_media import independent_samples
from .provenance import compiled_model_digest, current_execution_metadata
from .quality_plots import trace_svg
from .render import render_views
from .scene import build_scene


def run_muscle_validation_media(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    record = read_hashed(
        definition.parent / source["muscle_result"], source["muscle_sha256"]
    )
    benchmark = read_hashed(
        definition.parent / record["input"]["audit_result"],
        record["input"]["audit_sha256"],
    )
    e = Experiment.from_dict(record["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != record["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Muscle media does not match computed physical model")
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    matched_cameras = None
    for pose_id in source["render_pose_ids"]:
        selected = next(p for p in record["poses"] if p["pose"]["id"] == pose_id)
        pose = selected["pose"]
        if "case_id" in pose:
            case = next(
                c
                for c in benchmark["cases"]
                if c["source_reference"]["id"] == pose["case_id"]
            )
            state = case["traces"][pose["sample_index"]]
            roles = state["roles"]
            contacts = state["active_contacts"]
        else:
            roles = {"index": "attempted"} if pose_id == "reference-seed" else {}
            contacts = []
        contact: dict[str, Any] = (
            contacts[0] if contacts else {"row": 1, "column": 5, "button_id": "r1c5"}
        )
        directory = output / pose_id
        scene.data.qpos[:] = pose["qpos_rad"]
        audit = independent_samples(
            scene, [{"qpos_rad": pose["qpos_rad"]}], e.solver.penetration_tolerance_m
        )
        concern = audit["worst_cross_digit"]
        screen = next(
            s
            for s in selected["static_screens"]
            if s["scenario"]["reaction_per_contact_n"] == 0
            and s["scenario"]["objective"] == "activation_squared"
        )
        pq = selected["snapshot"]["actuator_names"].index("PQ")
        pq_mm = selected["snapshot"]["musculotendon_length_m"][pq] * 1000
        residual = screen["force_balance_residual_projected_nm"]
        status = (
            "equilibrium found" if screen["conditional_feasible"] else "no equilibrium"
        )
        label = (
            f"{pose_id} | PQ length {pq_mm:.3f} mm | "
            f"static residual {residual:.5g} Nm; {status} | "
            "static diagnostic, no performance claim"
        )
        overrides = matched_cameras
        if pose_id == "native-default":
            palm = scene.data.body("capitate_r").xpos.copy()
            palm[2] -= 0.035
            overrides = {
                name: dict(
                    lookat=palm.tolist(), distance=0.6, azimuth=180.0, elevation=-30.0
                )
                for name in ("hand", "collision")
            }
        cameras = render_views(
            scene,
            directory,
            e.geometry.surface_world_m(
                button_at(contact["row"], contact["column"])
            ).tolist(),
            contact["button_id"],
            collision_overlay=True,
            highlighted_proxy_names=tuple(concern["geoms"]),
            contact_roles=roles,
            button_roles={
                contact["button_id"]: roles.get(contacts[0]["finger"], "moving")
                if contacts
                else "free"
            },
            state_label=label,
            camera_overrides=overrides,
        )
        if matched_cameras is None:
            matched_cameras = cameras
        reports.append(
            {
                "pose_id": pose_id,
                "qpos_rad": pose["qpos_rad"],
                "contact_requirements": contacts,
                "roles": roles,
                "camera_group": "default-model-diagnostic"
                if pose_id == "native-default"
                else "matched-reference",
                "cameras": cameras,
                "independent_geometry_audit": audit,
                "static_screen_reference": {
                    "pose_id": pose_id,
                    "force_n": 0.0,
                    "objective": "activation_squared",
                },
            }
        )
    for case in benchmark["cases"]:
        if case["state_kind"] != "connected_sampled_path":
            continue
        traces = case["traces"]
        actor_ids = {
            name: case["actuator_names"].index(name)
            for name in source["muscles_to_plot"]
        }
        trace_svg(
            output / (case["source_reference"]["id"] + "-lengths.svg"),
            case["source_reference"]["id"]
            + " | actual kinematic path; not muscle-driven execution",
            [
                {
                    "label": "Routed musculotendon lengths (m)",
                    "series": {
                        n: [s["musculotendon_lengths_m"][i] for s in traces]
                        for n, i in actor_ids.items()
                    },
                }
            ],
        )
    for route in record["routing_probes"]:
        probes = route["diagnostic_probes"]
        trace_svg(
            output / (route["case_id"] + "-routing.svg"),
            route["case_id"]
            + " | "
            + route["muscle"]
            + " coordinate probe, NOT accepted motion",
            [
                {
                    "label": "Native versus reduced tendon length (m)",
                    "series": {
                        "native": [p["native_length_m"] for p in probes],
                        "reduced": [p["reduced_length_m"] for p in probes],
                    },
                },
                {
                    "label": "Engine length derivative along full source segment (m)",
                    "series": {
                        "engine": [
                            p["engine_derivative_along_segment_m"] for p in probes
                        ]
                    },
                },
            ],
            x_axis="diagnostic coordinate probe index (65 fractions)",
        )
    screens = [
        next(
            s
            for s in p["static_screens"]
            if s["scenario"]["reaction_per_contact_n"] == 0
            and s["scenario"]["objective"] == "activation_squared"
        )
        for p in record["poses"]
    ]
    feasible_count = sum(s["conditional_feasible"] for s in screens)
    trace_svg(
        output / "static-residuals.svg",
        f"Conditional static screens: {feasible_count} "
        f"of {len(screens)} equilibria; no physiological rank",
        [
            {
                "label": "Projected residual norm (Nm)",
                "series": {
                    "bounded residual": [
                        s["force_balance_residual_projected_nm"] for s in screens
                    ],
                    "numerical tolerance": [1e-6] * len(screens),
                },
            },
            {
                "label": "Bounded coefficients; infeasible screens are NOT recruitment",
                "series": {
                    "maximum coefficient": [s["maximum_activation"] for s in screens]
                },
            },
        ],
        x_axis=f"{len(screens)} separate static poses; not a trajectory",
    )
    # Literal side-by-side views retain cameras and original pixels.
    for name, ids in {
        "reference-vs-extreme": ["reference-seed", "synthetic-extreme"],
        "pq-route-before-after": ["stepwise-index-state-19", "stepwise-index-state-20"],
    }.items():
        canvas = Image.new("RGB", (1920, 720))
        for i, pose_id in enumerate(ids):
            with Image.open(output / pose_id / "hand.png") as image:
                canvas.paste(image, (i * 960, 0))
        canvas.save(output / (name + ".png"))
    result = {
        "id": "muscle-media-046",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "pose_reports": reports,
        "pose_plot_order": [p["pose"]["id"] for p in record["poses"]],
        "activation_claim": (
            "Infeasible screens contain bounded residual diagnostics only; "
            "no neural control or activation animation"
        ),
        "artifact_sha256": {
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob("*")
            if p.suffix in (".svg", ".png")
        },
        **current_execution_metadata(scene.model),
    }
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    metadata = output / "execution.json"
    if metadata.exists():
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
    return result
