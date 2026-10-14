"""Versioned wrist/coordination assessments without rewriting the target catalog."""

import hashlib
import json
from pathlib import Path

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .scene import build_scene
from .wrist_study import finish_record


def run_posture_library(definition: Path, output: Path):
    source = json.loads(definition.read_text())
    root = definition.resolve().parents[2]
    catalog = read_hashed(
        definition.parent / source["catalog_result"], source["catalog_sha256"]
    )
    evidence = []
    records = {}
    for ref in source["evidence"]:
        record = read_hashed(definition.parent / ref["path"], ref["sha256"])
        records[ref["role"]] = record
        evidence.append(
            dict(
                role=ref["role"],
                path=str((definition.parent / ref["path"]).resolve().relative_to(root)),
                sha256=ref["sha256"],
            )
        )
    cases = {}
    for role in source.get("wrist_roles", ("historical_wrist", "selection_audit")):
        for case in records[role]["cases"]:
            target_id = source["case_targets"][case["source"]["id"]]
            cases[case["id"]] = dict(
                case_id=case["id"],
                target_id=target_id,
                evidence_role=role,
                strategy_id=case["strategy_id"],
                status=case["status"],
                compiled_model_sha256=case["compiled_model_sha256"],
                state_sequence_sha256=case["state_sequence_sha256"],
            )
    targets = []
    for target in catalog["targets"]:
        ident = target["id"]
        matched = [c for c in cases.values() if c["target_id"] == ident]
        targets.append(
            dict(
                target_id=ident,
                status="model_posture_assessed" if matched else "unassessed",
                cases=matched,
                unknown=[
                    "observed neutral wrist",
                    "calibrated hand envelopes",
                    "button force and travel",
                    "physiological timing",
                    "strain, comfort and human feasibility",
                ],
                muscle_ranking="withheld",
                human_feasibility=None,
            )
        )
    saved = read_hashed(
        definition.parent
        / records["selection_audit"]["cases"][0]["source"]["search_result"],
        records["selection_audit"]["cases"][0]["source"]["search_sha256"],
    )
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    output.mkdir(parents=True, exist_ok=True)
    return finish_record(
        definition,
        output,
        source,
        dict(
            id="posture-library-052",
            assessment_version="posture-coordination-v2",
            catalog_sha256=hashlib.sha256(
                (definition.parent / source["catalog_result"]).read_bytes()
            ).hexdigest(),
            targets=targets,
            evidence=evidence,
            library_claim=(
                "50 original targets preserved; versioned assessments "
                "and physical media, no ergonomic certification"
            ),
        ),
        scene,
    )
