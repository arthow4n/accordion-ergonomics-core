"""Compose released-contact sequences from exact sampled kinematic segments."""

import hashlib
import json
from pathlib import Path
from typing import Any

from .experiment import Experiment
from .exploration import read_hashed
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene
from .targets import contact_signature, path_descriptors


def compose_sequence(request: dict[str, Any], directory: Path) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    events = []
    identities = []
    names = []
    length = 0.0
    for segment in request["segments"]:
        saved = read_hashed(directory / segment["result"], segment["sha256"])
        if (
            saved["status"] != "sampled_path_found"
            or not saved["sampled_constraints_satisfied"]
        ):
            raise ValueError("Sequence requires successful sampled segments")
        endpoints = (
            saved["endpoints"][::-1] if segment.get("reverse") else saved["endpoints"]
        )
        part = saved["samples"][::-1] if segment.get("reverse") else saved["samples"]
        if not part:
            raise ValueError("Empty segment")
        if (
            part[0]["qpos_rad"] != endpoints[0]["qpos_rad"]
            or part[-1]["qpos_rad"] != endpoints[1]["qpos_rad"]
        ):
            raise ValueError("Segment samples do not match endpoints")
        identity = saved["provenance"]["compiled_model_sha256"]
        if identities and identity != identities[0]:
            raise ValueError("Sequence compiled worlds differ")
        identities.append(identity)
        if names and names != endpoints[0]["joint_names"]:
            raise ValueError("Sequence coordinate orders differ")
        names = endpoints[0]["joint_names"]
        if samples:
            if samples[-1]["qpos_rad"] != part[0]["qpos_rad"]:
                raise ValueError("Sequence joint endpoints are discontinuous")
            if contact_signature(events[-1]["contacts"]) != contact_signature(
                endpoints[0]["targets"]
            ):
                raise ValueError("Sequence contact endpoints are discontinuous")
        else:
            events.append(
                {
                    "contacts": [
                        {**c, "behavior": "release_after_event"}
                        for c in endpoints[0]["targets"]
                    ]
                }
            )
        events.append(
            {
                "contacts": [
                    {**c, "behavior": "release_after_event"}
                    for c in endpoints[1]["targets"]
                ]
            }
        )
        samples.extend(part if not samples else part[1:])
        length += saved["palm_path_length_m"]
    if not samples:
        raise ValueError("Sequence needs segments")
    state_hash = hashlib.sha256(
        json.dumps([s["qpos_rad"] for s in samples], separators=(",", ":")).encode()
    ).hexdigest()
    aggregate = {
        "palm_path_length_m": length,
        "minimum_joint_margin_rad": min(s["joint_margin_min_rad"] for s in samples),
        "maximum_penetration_m": max(s["penetration_m"] for s in samples),
    }
    return {
        "id": request["id"],
        "segments": request["segments"],
        "status": "sampled_path_composed",
        "events": events,
        "exact_joint_endpoint_continuity": True,
        "compiled_model_sha256": identities[0],
        "sample_states_sha256": state_hash,
        "descriptors": path_descriptors(aggregate, samples, names),
        "sample_count": len(samples),
        "human_feasibility": None,
        "continuous_validity": None,
        "interpretation": (
            "Ordered released-contact paths, including reverse traversal of "
            "recorded kinematic samples. Exact qpos/contact joins; no timing, "
            "force, dynamics or new collision certificate."
        ),
    }


def run_sequences(definition: Path, output: Path) -> dict[str, Any]:
    raw = definition.read_bytes()
    source = json.loads(raw)
    records = []
    scenes = {}
    for request in source["sequences"]:
        composed = compose_sequence(request, definition.parent)
        first = read_hashed(
            definition.parent / request["segments"][0]["result"],
            request["segments"][0]["sha256"],
        )
        expected = composed["compiled_model_sha256"]
        if expected not in scenes:
            e = Experiment.from_dict(first["endpoints"][0]["input"])
            scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact)
            if compiled_model_digest(scene.model) != expected:
                raise ValueError(
                    "Sequence recorded model differs from current composition"
                )
            scenes[expected] = scene
        records.append(
            {
                **composed,
                **current_execution_metadata(scenes[expected].model),
                "resolved_profiles": first["resolved_profiles"],
            }
        )
    result = {
        "id": source["id"],
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "sequences": records,
        "human_feasibility": None,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "result.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n"
    )
    return result
