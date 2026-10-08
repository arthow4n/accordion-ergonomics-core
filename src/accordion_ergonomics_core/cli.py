"""Canonical headless experiment, render and verification commands."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Any

from .experiment import Experiment
from .instrument import button_at
from .provenance import anatomy_digest, compiled_model_digest, project_source_digest


def load_input(path: Path) -> Experiment:
    return Experiment.from_dict(json.loads(path.read_text()))


def run_experiment(path: Path, output: Path, render: bool) -> dict[str, Any]:
    # Set before importing MuJoCo/OpenGL. No DISPLAY or interactive viewer required.
    os.environ.setdefault("MUJOCO_GL", "egl")
    from .render import render_views
    from .scene import build_scene
    from .solver import solve_contact

    raw_input = path.read_bytes()
    experiment = Experiment.from_dict(json.loads(raw_input))
    source, geometry = experiment.source, experiment.geometry
    scene = build_scene(
        geometry,
        experiment.player,
        experiment.setup,
        experiment.physical_contact,
        tuple(c.finger for c in experiment.contacts),
    )
    contact = experiment.contacts[0]
    button = button_at(contact.row, contact.column)
    target = geometry.surface_world_m(button)
    result = solve_contact(
        scene,
        target,
        experiment.initial_joints_rad,
        experiment.solver,
        button.id,
        experiment.frozen_joints,
        finger=contact.finger,
        additional_contacts=tuple(
            (
                geometry.surface_world_m(button_at(c.row, c.column)),
                c.finger,
                button_at(c.row, c.column).id,
            )
            for c in experiment.contacts[1:]
        ),
    )
    profiles = experiment.resolved_profiles()
    profiles_hash = hashlib.sha256(
        json.dumps(profiles, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    result.update(
        {
            "resolved_profiles": profiles,
            "profiles_sha256": profiles_hash,
            "schema_version": 1,
            "experiment_id": source["id"],
            "input_sha256": hashlib.sha256(raw_input).hexdigest(),
            "input": source,
            "provenance": {
                "compiled_model_sha256": compiled_model_digest(scene.model),
                "anatomy_source_sha256": anatomy_digest(),
                "project_source_sha256": project_source_digest(),
                "lock_sha256": hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest(),
                "render_backend": os.environ["MUJOCO_GL"],
            },
            "runtime": {
                "python": platform.python_version(),
                "platform": platform.platform(),
                "packages": {
                    p: version(p)
                    for p in (
                        "mujoco",
                        "myo-sim",
                        "mink",
                        "numpy",
                        "scipy",
                        "clarabel",
                        "pillow",
                    )
                },
            },
            "model": {
                "nq": scene.model.nq,
                "nv": scene.model.nv,
                "neq": scene.model.neq,
                "nu": scene.model.nu,
                "index_pad_local_m": scene.pad_local_m,
                "index_pad_quat_wxyz": scene.model.site_quat[
                    scene.model.site("index_pad").id
                ].tolist(),
                "contact_sites": {
                    f"{c.finger}_pad": {
                        "pos_m": scene.model.site_pos[
                            scene.model.site(f"{c.finger}_pad").id
                        ].tolist(),
                        "quat_wxyz": scene.model.site_quat[
                            scene.model.site(f"{c.finger}_pad").id
                        ].tolist(),
                    }
                    for c in experiment.contacts
                },
                "index_pad_provenance": (
                    "Outer envelope of compiled distal capsule and ellipsoid; "
                    "normal along distal capsule axis"
                ),
            },
            "targets": [
                {
                    "button_id": button_at(c.row, c.column).id,
                    "finger": c.finger,
                    "midi": button_at(c.row, c.column).midi,
                    "surface_world_m": geometry.surface_world_m(
                        button_at(c.row, c.column)
                    ).tolist(),
                    "normal_world": geometry.rotation[:, 2].tolist(),
                }
                for c in experiment.contacts
            ],
            "target": {
                "button_id": button.id,
                "midi": button.midi,
                "surface_world_m": target.tolist(),
                "normal_world": geometry.rotation[:, 2].tolist(),
            },
        }
    )
    output.mkdir(parents=True, exist_ok=True)
    if render:
        result["cameras"] = render_views(
            scene, output / "renders", target.tolist(), button.id
        )
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    experiment = sub.add_parser("experiment")
    experiment.add_argument("input", type=Path)
    experiment.add_argument(
        "--output", type=Path, default=Path("artifacts/single-contact")
    )
    experiment.add_argument("--no-render", action="store_true")
    render = sub.add_parser("render")
    render.add_argument("result", type=Path)
    render.add_argument("--output", type=Path, default=Path("artifacts/renders"))
    ablation = sub.add_parser("ablation")
    ablation.add_argument("definition", type=Path)
    ablation.add_argument("--output", type=Path, default=Path("artifacts/ablation"))
    transition = sub.add_parser("transition")
    transition.add_argument("definition", type=Path)
    transition.add_argument("--output", type=Path, default=Path("artifacts/transition"))
    exploration = sub.add_parser("explore")
    exploration.add_argument("definition", type=Path)
    exploration.add_argument("--output", type=Path, default=Path("artifacts/explore"))
    exploration.add_argument("--no-render", action="store_true")
    planning = sub.add_parser("plan")
    planning.add_argument("definition", type=Path)
    planning.add_argument("--output", type=Path, default=Path("artifacts/plan"))
    planning.add_argument("--no-render", action="store_true")
    atlas = sub.add_parser("atlas")
    atlas.add_argument("definition", type=Path)
    atlas.add_argument("--output", type=Path, default=Path("artifacts/atlas"))
    sweep = sub.add_parser("sweep")
    sweep.add_argument("definition", type=Path)
    sweep.add_argument("--output", type=Path, default=Path("artifacts/sweep"))
    frozen = sub.add_parser("frozen")
    frozen.add_argument(
        "workflow",
        choices=(
            "atlas",
            "sweep",
            "explore",
            "plan",
            "experiment",
            "render",
            "exercise",
            "held",
            "collision-coverage",
            "limit-probe",
        ),
    )
    frozen.add_argument("definition", type=Path)
    frozen.add_argument("--output", type=Path, required=True)
    frozen.add_argument("--source-snapshot", type=Path)
    diagram = sub.add_parser("atlas-render")
    diagram.add_argument("result", type=Path)
    diagram.add_argument("--output", type=Path, default=Path("artifacts/atlas.png"))
    exercise = sub.add_parser("exercise")
    exercise.add_argument("definition", type=Path)
    exercise.add_argument("--output", type=Path, default=Path("artifacts/exercise"))
    held = sub.add_parser("held")
    held.add_argument("definition", type=Path)
    held.add_argument("--output", type=Path, default=Path("artifacts/held"))
    coverage = sub.add_parser("collision-coverage")
    coverage.add_argument("definition", type=Path)
    coverage.add_argument(
        "--output", type=Path, default=Path("artifacts/collision-coverage")
    )
    probe = sub.add_parser("limit-probe")
    probe.add_argument("definition", type=Path)
    probe.add_argument("--output", type=Path, default=Path("artifacts/limit-probe"))
    verification = sub.add_parser("verify")
    verification.add_argument("directories", type=Path, nargs="+")
    verification.add_argument("--input", type=Path)
    verification.add_argument("--output", type=Path)
    verification.add_argument("--require-complete", action="store_true")
    sub.add_parser("check")
    args = parser.parse_args()
    if args.command == "check":
        for command in (
            ["ruff", "format", "--check", "."],
            ["ruff", "check", "."],
            ["ty", "check"],
            [sys.executable, "-m", "pytest"],
        ):
            subprocess.run(command, check=True)
    elif args.command == "verify":
        from .verification import verify_records

        result = verify_records(args.directories, args.input)
        raw = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(raw)
        print(raw, end="")
        if any(
            r["status"] == "invalid"
            or (args.require_complete and r["status"] != "verified")
            for r in result["records"]
        ):
            raise SystemExit(1)
    elif args.command == "limit-probe":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .limit_probe import run_probe

        result = run_probe(args.definition, args.output)
        print(json.dumps({"id": result["id"], "cases": len(result["cases"])}))
    elif args.command == "collision-coverage":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .collision_coverage import run_coverage

        result = run_coverage(args.definition, args.output)
        print(json.dumps({"status": result["status"], "poses": len(result["poses"])}))
    elif args.command == "held":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .held import run_held

        result = run_held(args.definition, args.output)
        print(json.dumps({"status": result["status"], "failure": result["failure"]}))
    elif args.command == "exercise":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .exercise import run_exercise

        result = run_exercise(args.definition, args.output)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "relocation_m": result.get("selected_endpoint_relocation_m"),
                }
            )
        )
    elif args.command == "atlas-render":
        from .reachability import render_atlas

        args.output.parent.mkdir(parents=True, exist_ok=True)
        render_atlas(json.loads(args.result.read_text()), args.output)
        args.output.with_suffix(".json").write_text(
            json.dumps(
                {
                    "input_sha256": hashlib.sha256(
                        args.result.read_bytes()
                    ).hexdigest(),
                    "image_sha256": hashlib.sha256(
                        args.output.read_bytes()
                    ).hexdigest(),
                    "visualization_source_sha256": project_source_digest(),
                    "units": "metres internally; millimetres in diagram",
                },
                indent=2,
            )
            + "\n"
        )
    elif args.command == "frozen":
        from .frozen import frozen_run

        frozen_run(args.workflow, args.definition, args.output, args.source_snapshot)
    elif args.command == "sweep":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .sensitivity import run_sensitivity

        result = run_sensitivity(args.definition, args.output)
        print(
            json.dumps(
                {
                    "id": result["id"],
                    "cases": [
                        {
                            "id": c["case"]["id"],
                            "changes": c["comparison"]["status_changes"],
                        }
                        for c in result["cases"]
                    ],
                }
            )
        )
    elif args.command == "atlas":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .reachability import run_atlas

        result = run_atlas(args.definition, args.output)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "summary": result.get("summary"),
                    "elapsed_s": result["elapsed_s"],
                }
            )
        )
    elif args.command == "plan":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .exploration import run_planning

        result = run_planning(args.definition, args.output, not args.no_render)
        print(
            json.dumps({"status": result["status"], "elapsed_s": result["elapsed_s"]})
        )
    elif args.command == "explore":
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .exploration import run_exploration

        result = run_exploration(args.definition, args.output, not args.no_render)
        print(
            json.dumps(
                {
                    "targets": [
                        {"button": t["button_id"], "candidates": len(t["candidates"])}
                        for t in result["targets"]
                    ]
                }
            )
        )
    elif args.command == "transition":
        from .transition import run_transition

        result = run_transition(args.definition, args.output)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "max_penetration_m": result["maximum_detected_penetration_m"],
                }
            )
        )
    elif args.command == "ablation":
        from .ablation import run_ablation

        summary = run_ablation(args.definition, args.output)
        print(
            json.dumps(
                {
                    "id": summary["id"],
                    "cases": [
                        {"case": c["case_id"], "status": c["status"]}
                        for c in summary["cases"]
                    ],
                }
            )
        )
    elif args.command == "experiment":
        result = run_experiment(args.input, args.output, not args.no_render)
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "feasible": result["feasible"],
                    "position_error_m": result["diagnostics"]["position_error_m"],
                    "output": str(args.output),
                }
            )
        )
        if result["status"] != "success":
            raise SystemExit(1)
    else:
        os.environ.setdefault("MUJOCO_GL", "egl")
        from .render import render_views
        from .scene import build_scene

        result = json.loads(args.result.read_text())
        result = result.get("render_state", result)
        experiment = Experiment.from_dict(result["input"])
        if (
            result.get("provenance", {}).get("anatomy_source_sha256", anatomy_digest())
            != anatomy_digest()
        ):
            raise ValueError("Anatomical source differs from the saved result")
        scene = build_scene(
            experiment.geometry,
            experiment.player,
            experiment.setup,
            experiment.physical_contact,
            tuple(c.finger for c in experiment.contacts),
        )
        if (
            "compiled_model_sha256" in result.get("provenance", {})
            and compiled_model_digest(scene.model)
            != result["provenance"]["compiled_model_sha256"]
        ):
            raise ValueError(
                "Compiled model differs; recompute explicitly before replay"
            )
        site = scene.model.site("index_pad").id
        scene.model.site_pos[site] = result["model"]["index_pad_local_m"]
        if "index_pad_quat_wxyz" in result["model"]:
            scene.model.site_quat[site] = result["model"]["index_pad_quat_wxyz"]
        scene.data.qpos[:] = result["qpos_rad"]
        from ._engine import mujoco

        mujoco.mj_forward(scene.model, scene.data)
        render_views(
            scene,
            args.output,
            result["target"]["surface_world_m"],
            result["target"]["button_id"],
            collision_overlay=result.get("collision_overlay", False),
        )
