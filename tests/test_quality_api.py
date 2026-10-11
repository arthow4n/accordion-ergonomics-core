"""Versioned hierarchy, full-path selection, exact frames and consumer portability."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from accordion_ergonomics_core.research import ExerciseLibrary
from accordion_ergonomics_core.verification import verify_record

ROOT = Path(__file__).resolve().parents[1]


def test_historical_catalog_identity_and_assessment_coverage():
    library = ExerciseLibrary(ROOT)
    record = library.quality_record()
    assert (
        record["input"]["catalog_sha256"]
        == hashlib.sha256((ROOT / "targets/manifest.json").read_bytes()).hexdigest()
    )
    assert len(record["targets"]) == len(library.query()) == 50
    assert record["muscle_source_off_manifold_poses"] == [
        "reference-seed",
        "synthetic-extreme",
    ]
    assert all(t["human_feasibility"] is None for t in record["targets"])
    held = library.assessment("generated-247e3482c25d6082")
    assert not held["complete_movement_available"]
    assert held["negative_evidence_retained"]
    assert held["benchmarks"][0]["whole_hand_descriptors"]["palm_path_m"] is None
    step = library.assessment("passage-stepwise")
    assert all(
        r["whole_hand_posture"] == "analyzed_exact_recorded_samples"
        for r in step["realizations"]
    )
    with pytest.raises(KeyError):
        library.assessment("does-not-exist")
    with pytest.raises(KeyError):
        library.quality_record("unknown")


def test_ranking_preserves_little_finger_alternative_and_exact_frames():
    library = ExerciseLibrary(ROOT)
    trial = next(
        t
        for t in library.ranked_comparisons("generated-dcbc77238f1b5559")
        if t["trial_id"] == "arpeggio-B-4309"
    )
    assert [r["id"] for r in trial["ranking"]] == ["strategy-1", "strategy-0"]
    trajectory = library.comparison_trajectory("arpeggio-B-4309", "strategy-1")
    assert trajectory["events"][-1]["contacts"][0]["finger"] == "little"
    for frame in library.comparison_frame_sequence("arpeggio-B-4309", "strategy-1"):
        source = trajectory["samples"][frame["sample_index"]]
        assert frame["qpos_rad"] == source["qpos_rad"]
        assert frame["active_contacts"] == source["active_contacts"]
        assert frame["roles"] == source["roles"]
        assert frame["path"].is_file()
    assert trajectory["first_note_approach"] == "not_planned"
    assert library.quality_media("passage-stepwise")
    assert library.muscle_screens("generated-dcbc77238f1b5559")
    assert not any(
        s["conditional_feasible"]
        for p in library.muscle_screens("generated-dcbc77238f1b5559")
        for s in p["static_screens"]
    )
    with pytest.raises(KeyError):
        library.comparison_frame_sequence("arpeggio-A-4309", "strategy-1")
    with pytest.raises(KeyError):
        library.comparison_trajectory("held-fabrication")


def test_corrected_seed_and_versioned_quality_records_verify():
    for directory in ("seed", "assessment"):
        assert (
            verify_record(
                ROOT / "experiments/048-library-reassessment" / directory
            ).status
            == "verified"
        )
    seed = json.loads(
        (ROOT / "experiments/048-library-reassessment/seed/result.json").read_text()
    )
    poses = {p["id"]: p for p in seed["poses"]}
    assert poses["resolved-playing-seed"]["static_screens"][0][
        "ideal_equality_position_consistent"
    ]
    assert not poses["historical-uncoupled-input"]["static_screens"][0][
        "ideal_equality_position_consistent"
    ]
    assert not any(
        s["conditional_feasible"] for p in seed["poses"] for s in p["static_screens"]
    )


def test_consumer_example_works_outside_repository(tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / "examples/quality_consumer.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    saved = json.loads(result.stdout)
    assert saved["selected_strategy"] == "strategy-1"
    assert saved["sample_count"] > saved["saved_frame_count"] >= 4
    assert saved["human_feasibility"] is None
    assert saved["initial_approach"] == "not_planned"
    assert saved["media_replay_argv"][3] == "frozen"
