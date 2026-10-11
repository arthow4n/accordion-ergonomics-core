"""Algorithm summaries derived from recorded discovery decisions, never sketches."""

import hashlib
import json
from html import escape
from pathlib import Path

from .digits import DIGITS
from .discovery import discovery_diagram
from .experiment import Experiment
from .exploration import read_hashed
from .provenance import compiled_model_digest, current_execution_metadata
from .scene import build_scene
from .targets import note_name


def svg_text(x, y, label, size=12):
    return f'<text x="{x}" y="{y}" font-size="{size}">{escape(str(label))}</text>'


def selection_diagram(record, output: Path):
    evaluations = {e["id"]: e for e in record["evaluations"]}
    candidates = {c["id"]: c for c in record["generation"]["candidates"]}
    rows = record["selected"]
    height = 160 + len(rows) * 92
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="{height}">',
        '<rect width="100%" height="100%" fill="#142030"/>',
        '<g fill="#eef3f8" font-family="monospace">',
        svg_text(
            20, 30, "Retained challenges: actual musical and measured differences", 17
        ),
        svg_text(
            20,
            55,
            "Diversity and negative evidence; anatomy unresolved. No difficulty score.",
        ),
    ]
    for i, selected in enumerate(rows):
        y = 80 + i * 92
        candidate = candidates[selected["candidate_id"]]
        trial = evaluations[selected["evaluation_id"]]
        notes = []
        for event in candidate["passage"]["events"]:
            label = "+".join(note_name(p) for p in event["pitches"])
            if event["hold_to_next"]:
                label += (
                    " [hold "
                    + "+".join(note_name(p) for p in event["hold_to_next"])
                    + "]"
                )
            notes.append(label)
        sequence = " → ".join(notes)
        obs = trial["observed"]
        strategy = next(
            (
                s
                for s in obs["strategies"]
                if s["independent_status"] == "sampled_proxy_constraints_satisfied"
            ),
            None,
        )
        if strategy:
            details = (
                f"{strategy['sample_count']} samples; "
                f"palm {strategy['palm_path_length_m'] * 1000:.1f} mm; "
                f"digits {','.join(strategy['played_digits'])}; "
                f"unresolved proxy "
                f"{strategy['worst_cross_digit_proxy_m'] * 1000:.1f} mm"
            )
        else:
            details = (
                "No proxy-accepted complete path; "
                f"connected prefix {obs['deepest_connected_event_count']} events; "
                f"failed contacts {obs['failed_contact_solves']}; "
                f"failed edges {obs['failed_movement_edges']}"
            )
        parts += [
            f'<rect x="20" y="{y}" width="1240" height="80" fill="#29465a"/>',
            svg_text(
                28,
                y + 17,
                f"{selected['family']} | {sequence} | {selected['evaluation_id']}",
            ),
            svg_text(28, y + 36, details, 11),
            svg_text(28, y + 56, selected["reason"], 10),
            svg_text(28, y + 72, candidate["id"], 10),
        ]
    parts += [
        svg_text(
            20,
            height - 20,
            (
                "Saved model descriptors do not establish tissue validity, "
                "effort, tempo or necessary movement."
            ),
            11,
        ),
        "</g></svg>",
    ]
    output.write_text("\n".join(parts) + "\n")


def run_discovery_summary(definition: Path, output: Path):
    raw = definition.read_bytes()
    source = json.loads(raw)
    root = (definition.parent / source["discovery_result"]).parent
    record = read_hashed(
        definition.parent / source["discovery_result"], source["discovery_sha256"]
    )
    searches = [
        read_hashed(root / e["search_result"], e["search_sha256"])
        for e in record["evaluations"]
    ]
    e = Experiment.from_dict(searches[0]["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != record["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Summary reference model differs from discovery")
    output.mkdir(parents=True, exist_ok=True)
    discovery_diagram(record, output / "discovery.svg")
    selection_diagram(record, output / "selection.svg")
    result = {
        "id": "discovery-summary",
        "input": source,
        "definition_sha256": hashlib.sha256(raw).hexdigest(),
        "discovery_source_provenance": record["provenance"],
        "artifact_sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.glob("*.svg"))
        },
        "claim": (
            "Schematic algorithm summaries from actual "
            "trials, budgets and selection records"
        ),
        **current_execution_metadata(scene.model),
    }
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    return result
