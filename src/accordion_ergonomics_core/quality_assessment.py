"""Versioned assessment sidecars; historical catalog identities stay unchanged."""

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from .exploration import read_hashed
from .provenance import project_source_digest
from .selection import TECHNIQUE_SOURCE


def hierarchy(realization):
    status = realization["status"]
    path = status in ("sampled_path_found", "sampled_connected_path")
    validity = realization["validity"]
    fingers = {
        c["finger"] for event in realization["events"] for c in event["contacts"]
    }
    return {
        "realization_id": realization["id"],
        "musical_target": "represented",
        "contact_pose": "discovered"
        if status
        in ("contact_candidates_found", "sampled_path_found", "sampled_connected_path")
        else "not_found",
        "connected_sampled_movement": "discovered" if path else "not_established",
        "configured_geometric_checks": validity.get(
            "independent_audit", "not_assessed"
        ),
        "anatomical_proxy_validity": validity.get(
            "anatomical_validation", "not_assessed"
        ),
        "whole_hand_posture": "not_deeply_assessed_in_045",
        "static_muscle_capacity": "not_assessed",
        "dynamic_muscle_execution": "not_evaluated",
        "human_feasibility": None,
        "ordinary_playing_recommendation": "not_established",
        "research_use": "retain_kinematic_evidence"
        if status
        in ("contact_candidates_found", "sampled_path_found", "sampled_connected_path")
        else "retain_hypothesis_or_negative_evidence",
        "technique_234_prior": {
            "contact_sequence_compatible": fingers <= {"index", "middle", "ring"},
            "source": TECHNIQUE_SOURCE,
            "scope": (
                "Optional exploration preference; "
                "1/5 use is not invalid or universally unusual"
            ),
        },
    }


def run_quality_assessment(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    root = definition.resolve().parents[2]
    catalog = read_hashed(root / source["catalog_result"], source["catalog_sha256"])
    audit = read_hashed(root / source["audit_result"], source["audit_sha256"])
    muscles = read_hashed(root / source["muscle_result"], source["muscle_sha256"])
    seed = read_hashed(root / source["seed_result"], source["seed_sha256"])
    comparison = read_hashed(
        root / source["comparison_result"], source["comparison_sha256"]
    )
    media = read_hashed(
        root / source["audit_media_result"], source["audit_media_sha256"]
    )
    targets = []
    for target in catalog["targets"]:
        cases = [
            c
            for c in audit["cases"]
            if source["case_targets"][c["source_reference"]["id"]] == target["id"]
        ]
        benchmarks: list[dict[str, Any]] = []
        for c in cases:
            cid = c["source_reference"]["id"]
            static = [p for p in muscles["poses"] if p["pose"].get("case_id") == cid]
            screens = [s for p in static for s in p["static_screens"]]
            routing = next(
                (a for a in muscles["motion_derivative_audits"] if a["case_id"] == cid),
                None,
            )
            # Exact versioned records, not an inferred human verdict.
            benchmarks.append(
                dict(
                    case_id=cid,
                    source=c["source_reference"],
                    whole_hand_descriptors={
                        k: v
                        for k, v in c.items()
                        if k not in ("traces", "source_reference")
                    },
                    sampled_cross_digit_min_m=c["worst_proxy_m"],
                    strict_rigid_proxy_policy="rejected"
                    if c["worst_proxy_m"] < 0
                    else "no_overlap_found",
                    strict_policy_scope=(
                        "Reject any negative unconfigured rigid "
                        "cross-digit distance; not calibrated anatomy"
                    ),
                    first_note_approach={
                        **c["first_note_approach"],
                        "historical_seed_dictionary": (
                            "stale original input; not executed seed"
                        ),
                        "resolved_seed_evidence_role": "seed",
                    },
                    static_screen_count=len(screens),
                    conditional_equilibria=sum(
                        s["conditional_feasible"] for s in screens
                    ),
                    static_muscle_capacity="attempted_conditional_balance_failed"
                    if screens
                    else "not_assessed",
                    routing_derivative_failure_samples=routing["failure_sample_indices"]
                    if routing
                    else None,
                    research_use="retain_negative_evidence"
                    if c["palm_path_m"] is None
                    else "retain_kinematic_comparison",
                    ordinary_playing_recommendation="not_established",
                    human_feasibility=None,
                )
            )
        reassessed_realizations = [hierarchy(r) for r in target["realizations"]]
        primary_hashes = {
            r["sha256"]
            for r in target.get("evidence", [])
            if r["role"] == "connected_passage_search"
        }
        for benchmark in benchmarks:
            if benchmark["source"]["search_sha256"] not in primary_hashes:
                continue
            strategy_id = benchmark["source"]["strategy_id"]
            if strategy_id is None:
                continue
            index = int(strategy_id.removeprefix("strategy-"))
            if index >= len(reassessed_realizations):
                raise ValueError("Assessment strategy does not match catalog")
            row = reassessed_realizations[index]
            row["whole_hand_posture"] = "analyzed_exact_recorded_samples"
            row["static_muscle_capacity"] = benchmark["static_muscle_capacity"]
            row["benchmark_case_id"] = benchmark["case_id"]
            row["strict_rigid_proxy_policy"] = benchmark["strict_rigid_proxy_policy"]
        targets.append(
            dict(
                target_id=target["id"],
                realizations=reassessed_realizations,
                benchmarks=benchmarks,
                discovery_status=target.get("search_status", "historical"),
                complete_movement_available=any(
                    r["status"] == "sampled_path_found" for r in target["realizations"]
                ),
                negative_evidence_retained=not bool(target["realizations"]),
                human_feasibility=None,
            )
        )
    evidence = []
    for key in ("catalog", "audit", "muscle", "comparison", "audit_media", "seed"):
        evidence.append(
            dict(role=key, path=source[key + "_result"], sha256=source[key + "_sha256"])
        )
    examples = []
    for case in media["cases"]:
        # File hashes are anchored to the numerical media record's own manifest.
        cid = case["id"]
        prefix = cid + "/"
        files = [
            dict(path=str(Path(source["audit_media_result"]).parent / k), sha256=v)
            for k, v in media["artifact_sha256"].items()
            if k.startswith(prefix) and (k.endswith("hand.png") or k.endswith(".gif"))
        ]
        examples.append(
            dict(target_id=source["case_targets"][cid], case_id=cid, files=files)
        )
    comparison_media = []
    for ref in source["comparison_media"]:
        saved_media = read_hashed(root / ref["path"], ref["sha256"])
        prefix = Path(ref["path"]).parent
        files = [
            dict(path=str(prefix / k), sha256=v)
            for k, v in saved_media["artifact_sha256"].items()
            if k.endswith("hand.png") or k.endswith(".gif")
        ]
        examples.append(
            dict(
                target_id=source["trial_targets"][ref["trial_id"]],
                trial_id=ref["trial_id"],
                files=files,
            )
        )
        comparison_media.append(ref)
    comparison_directory = Path(source["comparison_definition"]).parent
    output.mkdir(parents=True, exist_ok=True)
    selection_reassessment, frame_sources = quality_visuals(
        root, output, comparison, comparison_media, source["visual_comparisons"]
    )
    result = dict(
        id="library-quality-048-v1",
        assessment_version="biomechanics-v1",
        input=source,
        definition_sha256=hashlib.sha256(raw).hexdigest(),
        targets=targets,
        evidence=evidence,
        comparison_trials=[
            dict(
                id=t["source"]["id"],
                target_id=source["trial_targets"][t["source"]["id"]],
                status=t["status"],
                settings=t["settings"],
                budget=t["budget"],
                source=t["source"],
                search_evidence={
                    "path": str(comparison_directory / t["source"]["search_result"]),
                    "sha256": t["source"]["search_sha256"],
                },
            )
            for t in comparison["trials"]
        ],
        visual_examples=examples,
        comparison_media=comparison_media,
        full_path_selection_reassessment=selection_reassessment,
        comparison_frame_sources=frame_sources,
        initial_input_correction=seed["historical_correction"],
        muscle_source_off_manifold_poses=[
            p["pose"]["id"]
            for p in muscles["poses"]
            if max(abs(x) for x in p["snapshot"]["equality_position_residual_rad"])
            > 1e-8
        ],
        artifact_sha256={
            str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.iterdir()
            if p.suffix in (".svg", ".png")
        },
        limitations=[
            "Rigid proxies uncalibrated",
            "Static scenarios lack measured support and button reactions",
            "No dynamic muscle-driven execution",
            "No validated human comfort or feasibility",
        ],
        provenance={
            "kind": "versioned_posthoc_assessment",
            "historical_catalog_sha256": source["catalog_sha256"],
            "project_source_sha256": project_source_digest(),
            "lock_sha256": hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest(),
        },
    )
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    metadata = output / "execution.json"
    if metadata.exists():
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
    return result


def quality_visuals(root, output, comparison, comparison_media, groups):
    """Literal matched frames and criterion plots from committed algorithm records."""
    from PIL import Image, ImageDraw

    from .quality_plots import trace_svg
    from .selection import audited_strategy_order

    reports = []
    for trial in comparison["trials"]:
        if trial["settings"]["selection_mode"] != "whole_hand_pareto":
            continue
        last = trial["selection_records"][-1]
        nodes = last["ordered_candidates"]
        trace_svg(
            output / (trial["source"]["id"] + "-beam-criteria.svg"),
            trial["source"]["id"] + " | actual final-event beam candidates",
            [
                dict(
                    label="Untimed variation (rad)",
                    series={
                        k: [n["descriptors"][k] for n in nodes]
                        for k in ("wrist_variation_rad", "digit_variation_rad")
                    },
                ),
                dict(
                    label="Lengths (m); proxy scope is endpoints only",
                    series={
                        k: [n["descriptors"][k] for n in nodes]
                        for k in ("palm_path_m", "endpoint_proxy_penetration_m")
                    },
                ),
                dict(
                    label="Algorithm state (dimensionless)",
                    series={
                        "Pareto layer": [n["pareto_layer"] for n in nodes],
                        "retained": [int(n["retained"]) for n in nodes],
                    },
                ),
            ],
            x_axis="actual ordered candidate index; node IDs in record",
        )
        reports.append(
            dict(
                trial_id=trial["source"]["id"],
                node_plot_order=[n["node_id"] for n in nodes],
                full_path_proxy_first=audited_strategy_order(trial["strategies"]),
                full_path_wrist_first=audited_strategy_order(
                    trial["strategies"], "wrist_first"
                ),
            )
        )
    frame_sources = []
    for group in groups:
        if len(group["strategies"]) != 4:
            raise ValueError("A matched gallery requires exactly four real frames")
        model_hash = None
        final_pitches = None
        canvas = Image.new("RGB", (1920, 1480), "#142030")
        draw = ImageDraw.Draw(canvas)
        entries = []
        camera = None
        for i, item in enumerate(group["strategies"]):
            ref = next(r for r in comparison_media if r["trial_id"] == item["trial_id"])
            media = read_hashed(root / ref["path"], ref["sha256"])
            identity = media["provenance"]["compiled_model_sha256"]
            if model_hash is not None and model_hash != identity:
                raise ValueError("Gallery model identities differ")
            model_hash = identity
            strategy = next(
                s
                for s in media["strategy_reports"]
                if s["strategy_id"] == item["strategy_id"]
            )
            animation = strategy["animation"]
            if not animation:
                raise ValueError("No complete movement for comparison")
            if camera is not None and camera != animation["cameras"]:
                raise ValueError("Comparison cameras differ")
            camera = animation["cameras"]
            frame = animation["frames"][-1]
            pitches = sorted(c["midi"] for c in frame["active_contacts"])
            if final_pitches is not None and final_pitches != pitches:
                raise ValueError("Gallery final musical events differ")
            final_pitches = pitches
            trial = next(
                t for t in comparison["trials"] if t["source"]["id"] == item["trial_id"]
            )
            actual = next(
                s for s in trial["strategies"] if s["id"] == item["strategy_id"]
            )
            if (
                animation["state_sequence_sha256"]
                != actual["whole_hand"]["state_sequence_sha256"]
            ):
                raise ValueError("Gallery animation differs from audited path")
            path = Path(ref["path"]).parent / item["strategy_id"] / frame["frame"]
            image_path = root / path
            if (
                hashlib.sha256(image_path.read_bytes()).hexdigest()
                != frame["frame_sha256"]
            ):
                raise ValueError("Comparison frame differs from saved actual state")
            with Image.open(image_path) as image:
                canvas.paste(image, ((i % 2) * 960, (i // 2) * 740 + 20))
            label = (
                f"{item['trial_id']} {item['strategy_id']} | "
                f"actual final event, sample {frame['sample_index']}"
            )
            draw.text(((i % 2) * 960, (i // 2) * 740), label, fill="white")
            entries.append(
                dict(
                    **item,
                    path=str(path),
                    sha256=frame["frame_sha256"],
                    actual_frame_metadata=frame,
                )
            )
        canvas.save(output / (group["id"] + ".png"))
        frame_sources.append(
            dict(
                id=group["id"],
                target_id=group["target_id"],
                frames=entries,
                camera=camera,
                claim="Literal final-event pixels; no invented pose or movement",
            )
        )
    return reports, frame_sources
