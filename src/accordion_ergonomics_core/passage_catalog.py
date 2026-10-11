"""Catalog adapters for recorded connected searches, including finite failures."""

from pathlib import Path
from typing import Any

from .movement_evidence import state_digest, validate_strategy


def build_passage_target(root: Path, spec: dict[str, Any], world: dict[str, Any]):
    from .targets import (
        check_world,
        digest,
        events_with_notes,
        evidence_ref,
        path_descriptors,
        read,
    )

    saved = read(root, spec["passage_search"])
    check_world(saved, world)
    search_ref = evidence_ref(root, spec["passage_search"], "connected_passage_search")
    media = read(root, spec["passage_media"])
    if media["input"]["search_sha256"] != search_ref["sha256"]:
        raise ValueError("Media references a different numerical search")
    refs = [
        search_ref,
        evidence_ref(root, spec["passage_media"], "passage_media_audit"),
    ]
    for relative in media["artifact_sha256"]:
        ref = evidence_ref(
            root,
            str(Path(spec["passage_media"]).parent / relative),
            "animation"
            if relative.endswith(".gif")
            else "search_diagram"
            if relative.endswith(".svg")
            else "diagnostic_render",
        )
        if ref["sha256"] != media["artifact_sha256"][relative]:
            raise ValueError("Media artifact differs from recorded rendering")
        refs.append(ref)
    realizations = []
    for strategy in saved["strategies"]:
        validate_strategy(saved, strategy)
        report = next(
            (
                r
                for r in media["strategy_reports"]
                if r["strategy_id"] == strategy["id"]
            ),
            None,
        )
        audit = report["independent_audit"] if report else None
        if audit and audit["state_sequence_sha256"] != state_digest(
            strategy["samples"]
        ):
            raise ValueError("Independent audit differs from strategy states")
        events = events_with_notes(strategy["events"])
        descriptors = path_descriptors(
            {"palm_path_length_m": strategy["cost_palm_path_m"]},
            strategy["samples"],
            saved["joint_names"],
        )
        status = (
            "sampled_path_found"
            if audit and audit["status"] == "sampled_proxy_constraints_satisfied"
            else "collision_policy_rejected"
            if audit
            else "sampled_path_found"
        )
        realizations.append(
            {
                "id": "realization-"
                + digest({"world": world["id"], "events": events})[:20],
                "events": events,
                "status": status,
                "branches": [],
                "movement_attempts": [
                    {
                        "id": strategy["id"],
                        "status": strategy["status"],
                        "descriptors": descriptors,
                        "evidence": search_ref,
                        "selector": {"strategy_id": strategy["id"], "field": "samples"},
                        "independent_sample_report": {
                            k: v for k, v in audit.items() if k != "samples"
                        }
                        if audit
                        else None,
                        "animation": report["animation"] if report else None,
                    }
                ],
                "searches": [
                    {
                        "evidence": search_ref,
                        "settings": saved["settings"],
                        "budget": saved["budget"],
                        "method": "Connected bounded beam search",
                    }
                ],
                "evidence": refs,
                "descriptors": descriptors,
                "validity": {
                    "quality": "numerically_realized",
                    "human_feasibility": None,
                    "anatomical_validation": "unresolved",
                    "independent_audit": audit["status"] if audit else "not_evaluated",
                    "coverage_limitations": [
                        (
                            "Rigid proxies and unconfigured cross-digit "
                            "overlaps remain unresolved"
                        ),
                        (
                            "Samples do not certify unsampled intervals "
                            "or human feasibility"
                        ),
                    ],
                },
            }
        )
    target = {
        "id": spec["id"],
        "family": spec["family"],
        "explanation": spec["explanation"],
        "provenance": saved["passage"]["provenance"],
        "musical_intent": {
            "event_pitches_midi": [e["pitches"] for e in saved["passage"]["events"]],
            "events": saved["passage"]["events"],
            "timing": None,
        },
        "reference_world": world["id"],
        "realizations": realizations,
        "search_status": saved["status"],
        "budget": saved["budget"],
        "evidence": refs,
        "human_feasibility": None,
    }

    if spec.get("generation_record"):
        generation_ref = evidence_ref(
            root, spec["generation_record"], "autonomous_discovery"
        )
        discovery = read(root, spec["generation_record"])
        candidate = next(
            c for c in discovery["generation"]["candidates"] if c["id"] == spec["id"]
        )
        if candidate["passage"] != saved["passage"]:
            raise ValueError("Generated musical intent differs from selected search")
        selected = next(
            s for s in discovery["selected"] if s["candidate_id"] == spec["id"]
        )
        target["generation"] = {
            "evidence": generation_ref,
            "candidate": candidate,
            "settings": discovery["generation"]["settings"],
            "selection": selected,
            "proposal": next(
                p
                for p in discovery["generation"]["proposals"]
                if p["proposal_index"] == candidate["proposal_index"]
            ),
        }
        target["evidence"].append(generation_ref)
        target["search_trials"] = []
        for trial in discovery["evaluations"]:
            if trial["candidate_id"] != spec["id"]:
                continue
            path = str(Path(spec["generation_record"]).parent / trial["search_result"])
            trial_ref = evidence_ref(root, path, "generated_search_trial")
            if trial_ref["sha256"] != trial["search_sha256"]:
                raise ValueError("Generated search trial identity differs")
            target["evidence"].append(trial_ref)
            target["search_trials"].append({**trial, "evidence": trial_ref})
        if spec.get("generation_summary"):
            summary = read(root, spec["generation_summary"])
            summary_ref = evidence_ref(
                root, spec["generation_summary"], "discovery_summary"
            )
            if summary["input"]["discovery_sha256"] != generation_ref["sha256"]:
                raise ValueError("Summary differs from generated search")
            target["evidence"].append(summary_ref)
            for name, expected in summary["artifact_sha256"].items():
                path = str(Path(spec["generation_summary"]).parent / name)
                ref = evidence_ref(root, path, "selection_diagram")
                if ref["sha256"] != expected:
                    raise ValueError("Selection diagram differs from source")
                target["evidence"].append(ref)
    return target
