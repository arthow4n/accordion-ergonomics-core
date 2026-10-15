"""Versioned consumers and scientific-media integrity on published records."""

import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pytest

from accordion_ergonomics_core.experiment import Experiment
from accordion_ergonomics_core.movement_evidence import state_digest, validate_strategy
from accordion_ergonomics_core.research import ExerciseLibrary

ROOT = Path(__file__).resolve().parents[1]


def test_v3_preserves_catalog_and_retrieves_exact_untimed_geometry():
    library = ExerciseLibrary(ROOT)
    assert len(library.playing_record()["targets"]) == 50
    assert len(library.catalog["targets"]) == 50
    assert (
        library.playing_assessment("passage-stepwise")["assessment_version"]
        == "playing-region-lifecycle-v3"
    )
    assert (
        library.assessment("passage-stepwise")["assessment_version"]
        == "biomechanics-v1"
    )
    assert (
        library.posture_assessment("passage-stepwise")["assessment_version"]
        == "posture-coordination-v2"
    )
    for ident in ("stepwise-coordinated-strategy-0", "arpeggio-region-strategy-0"):
        case = library.playing_case(ident)
        path = library.playing_trajectory(ident)
        assert case["region"]["state_sequence_sha256"] == state_digest(path["samples"])
        assert (
            case["independent_audit"]["status"] == "sampled_proxy_constraints_satisfied"
        )
        assert case["independent_audit"]["anatomical_validation"] == "unresolved"
        media = library.playing_media(ident)
        assert len(media["manifest"]["dense"]["frames"]) >= 48
        assert "not physiological time" in media["playback_claim"]
        for frame in media["manifest"]["dense"]["frames"]:
            assert (
                frame["qpos_rad"] == path["samples"][frame["sample_index"]]["qpos_rad"]
            )
        assert all(p.exists() for p in media["paths"])
    with pytest.raises(KeyError):
        library.playing_trajectory("held-D4-failure")


def test_approach_joins_actual_seed_and_does_not_certify_resting_hand():
    library = ExerciseLibrary(ROOT)
    for ident in ("stepwise-coordinated-strategy-0", "arpeggio-region-strategy-0"):
        approach = library.playing_initial_approach(ident)["record"]["details"]
        validate_strategy(approach["approach_graph"], approach["approach_strategy"])
        assert approach["exact_original_first_pose_reached"]
        joined = library.playing_complete_trajectory(ident)
        musical = library.playing_trajectory(ident)
        assert (
            len(joined["samples"])
            == joined["approach_sample_count"] + len(musical["samples"]) - 1
        )
        assert (
            joined["samples"][joined["approach_sample_count"] - 1]["qpos_rad"]
            == musical["samples"][0]["qpos_rad"]
        )
        assert "no resting hand" in joined["claim"]
    held = next(
        r
        for review in library.playing_reviews()
        for r in review["records"]
        if r["id"] == "held-D4-failure"
    )
    assert held["states"][0]["held_check"]["satisfied"]
    assert not held["states"][1]["held_check"]["satisfied"]
    assert "media" not in held["details"]


def test_matched_comparisons_have_same_model_cameras_scale_and_real_events():
    r = json.loads(
        (ROOT / "experiments/055-coordinated-planning/evidence/result.json").read_text()
    )
    cases = {c["id"]: c for c in r["cases"]}
    for pair in r["comparisons"]:
        a, b = [cases[i] for i in pair["cases"]]
        assert a["compiled_model_sha256"] == b["compiled_model_sha256"]
        assert a["media"]["dense"]["cameras"] == b["media"]["dense"]["cameras"]
        assert a["media"]["board_bounds_m"] == b["media"]["board_bounds_m"]
        for panel in pair["event_panels"]:
            row = cases[panel["case_id"]]["region"]["traces"][panel["sample_index"]]
            assert row["event_index"] == panel["event_index"]
    for name, old in [
        ("stepwise", "047-whole-hand-comparison/stepwise-free"),
        ("arpeggio", "047-whole-hand-comparison/arpeggio-A-4309"),
    ]:
        historical = json.loads(
            (ROOT / "experiments" / old / "result.json").read_text()
        )
        fresh = json.loads(
            (
                ROOT
                / "experiments/055-coordinated-planning"
                / (name + "-historical")
                / "result.json"
            ).read_text()
        )
        for a, b in zip(historical["strategies"], fresh["strategies"], strict=True):
            np.testing.assert_allclose(
                [s["qpos_rad"] for s in a["samples"]],
                [s["qpos_rad"] for s in b["samples"]],
                # Endpoint bit preservation can amplify local IK rounding.
                # Bound against the existing solver's numerical acceptance scale.
                atol=Experiment.from_dict(
                    fresh["scene_input"]
                ).solver.equality_tolerance_rad,
                rtol=0,
            )
    hashes = [
        json.loads(p.read_text())["package_source_sha256"]
        for p in (ROOT / "experiments/055-coordinated-planning").glob(
            "*-*/execution.json"
        )
        if p.parent.name.split("-")[-1]
        in ("historical", "region", "coordinated", "combined")
    ]
    assert len(hashes) == 8 and len(set(hashes)) == 1


def test_visual_guide_and_milestone_links_exist():
    paths = [
        ROOT / "README.md",
        ROOT / "targets/README.md",
        ROOT / "targets/VISUALS.md",
        ROOT / "targets/API.md",
    ]
    paths += list((ROOT / "experiments").glob("05[3-7]-*/notes.md"))
    for path in paths:
        for href in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if href.startswith(("https:", "http:", "#")):
                continue
            target = href.split("#")[0]
            assert (path.parent / target).exists(), (path, href)
    assert "targets/VISUALS.md" in (ROOT / "README.md").read_text()
    assert (
        "Visualization-first scientific research requirements"
        in (ROOT / "AGENTS.md").read_text()
    )
    replay = json.loads(
        (ROOT / "experiments/057-playing-library/replay-check.json").read_text()
    )
    assert replay["media_count"] >= 70 and all(c["equal"] for c in replay["checks"])


def test_future_preparation_and_budget_provenance_are_explicit():
    lib = ExerciseLibrary(ROOT)
    for binding in lib.playing_cases():
        case = lib.playing_case(binding["case_id"])
        assert case["budget"]["contact_solves"] > 0
        assert case["settings"]["planning"]["max_joint_step_rad"] > 0
        strategy = lib.playing_trajectory(binding["case_id"])
        for link in case["preparation_links"]:
            i = link["event_index"]
            expected = (
                strategy["events"][i + 1]["contacts"]
                if i + 1 < len(strategy["events"])
                else []
            )
            assert link["selected_next_contacts"] == expected
            for c in link["matched_next_bindings"]:
                assert any(
                    c["finger"] == n["finger"] and c["button_id"] == n["button_id"]
                    for n in expected
                )
        # Every returned file hash is checked independently of renderer appearance.
        saved = lib.playing_record()
        assert saved["assessment_version"].endswith("v3")
        assert (
            hashlib.sha256((ROOT / "targets/manifest.json").read_bytes()).hexdigest()
            == saved["catalog_sha256"]
        )
