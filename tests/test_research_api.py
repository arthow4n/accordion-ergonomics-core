"""Consumer imports, saved evidence retrieval, and motion integrity."""

import subprocess
import sys
from pathlib import Path

import pytest

from accordion_ergonomics_core.research import ExerciseLibrary


def test_consumer_uses_library_outside_repository(tmp_path: Path):
    library = ExerciseLibrary()
    completed = subprocess.run(
        [sys.executable, str(library.root / "examples/consume_passage_library.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Recorded trajectory samples: 522" in completed.stdout
    assert "thumb" in completed.stdout and "little" in completed.stdout
    assert "trajectory.gif" in completed.stdout
    assert "source-snapshot.zip" in completed.stdout


def test_all_finger_queries_and_exact_trajectory_references():
    library = ExerciseLibrary()
    assert library.query(finger="thumb") and library.query(finger="ring")
    target = library.target("passage-stepwise")
    assert len(target["realizations"]) == 2
    a, b = [library.trajectory(target["id"], f"strategy-{i}") for i in range(2)]
    assert [c["midi"] for c in a["events"][-1]["contacts"]] == [64]
    assert a["events"][-1]["contacts"] != b["events"][-1]["contacts"]
    assert len(library.media(target["id"])) == 2
    for realization in target["realizations"]:
        assert realization["validity"]["anatomical_validation"] == "unresolved"
    assert library.target("passage-held-ring")["realizations"] == []
    assert library.media("passage-held-ring") == []
    with pytest.raises(KeyError):
        library.target("not-a-target")


def test_evidence_path_guards(tmp_path: Path):
    library = ExerciseLibrary()
    with pytest.raises(ValueError, match="escapes"):
        library.evidence_path({"path": str(tmp_path / "outside"), "sha256": "missing"})
    with pytest.raises(ValueError, match="differs"):
        library.evidence_path({"path": "targets/manifest.json", "sha256": "wrong"})


def test_frames_diagnostics_and_recorded_trial_choices():
    library = ExerciseLibrary()
    assert len(library.query(generated=True)) == 5
    assert len(library.query(generated=False)) == 45
    with pytest.raises(ValueError, match="digit"):
        library.query(finger="sixth")
    frames = library.frame_sequence("passage-stepwise")
    trajectory = library.trajectory("passage-stepwise")
    assert len(frames) == 9
    for frame in frames:
        assert frame["path"].is_file()
        assert (
            frame["qpos_rad"]
            == trajectory["samples"][frame["sample_index"]]["qpos_rad"]
        )
    audit = library.diagnostics("passage-stepwise")
    assert len(audit["samples"]) == len(trajectory["samples"])
    assert audit["anatomical_validation"] == "unresolved"
    arpeggio = library.query(family="arpeggio", generated=True)[0]
    initial = library.trajectory(arpeggio["id"], trial_id="evaluation-03")
    selected = library.trajectory(arpeggio["id"])
    assert initial["cost_palm_path_m"] > selected["cost_palm_path_m"]
    assert (
        library.diagnostics(arpeggio["id"], trial_id="evaluation-03")["status"]
        == "sampled_proxy_constraints_satisfied"
    )
    assert "thumb" in {c["finger"] for e in initial["events"] for c in e["contacts"]}
    with pytest.raises(KeyError, match="trial"):
        library.search_record(arpeggio["id"], trial_id="unexplored")
    with pytest.raises(KeyError, match="complete strategy"):
        library.trajectory("passage-held-ring")


def test_replay_refuses_to_overwrite_published_or_nonempty_directories(tmp_path):
    library = ExerciseLibrary()
    (tmp_path / "preserved").write_text("important")
    with pytest.raises(ValueError, match="empty"):
        library.reproduce("passage-stepwise", tmp_path)
    assert (tmp_path / "preserved").read_text() == "important"


def test_external_consumer_submits_passage_and_receives_independent_samples(tmp_path):
    code = """
from accordion_ergonomics_core.research import Passage, NoteEvent, discover_passage
from accordion_ergonomics_core.passage_search import PassageSearchSettings
from accordion_ergonomics_core.planning import PlanningSettings
p = Passage("consumer-repeat", (NoteEvent((60,)), NoteEvent((60,))))
s = PassageSearchSettings(beam_width=1, assignments_per_parent=1, fingers=("index",),
 prepare_next=False, assignment_order="marker_distance", contact_iterations=120,
 planning=PlanningSettings(withdrawal_depths_m=(.01,), max_joint_step_rad=.01,
 waypoint_iterations=120, rrt_iterations=0, waypoint_solve_limit=12))
r = discover_passage(p, settings=s)
assert r["status"] == "complete_passage_found"
audit = r["independent_strategy_audits"][0]
assert audit["status"] == "sampled_proxy_constraints_satisfied"
assert len(audit["samples"]) == len(r["strategies"][0]["samples"])
assert r["independent_strategy_audits"][0]["anatomical_validation"] == "unresolved"
print("consumer computed and audited actual repetition")
"""
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "computed and audited" in completed.stdout


def test_single_event_output_is_an_audited_static_pose_without_animation(tmp_path):
    import json

    from accordion_ergonomics_core.passage_search import PassageSearchSettings
    from accordion_ergonomics_core.research import NoteEvent, Passage, discover_passage

    saved = discover_passage(
        Passage("consumer-static", (NoteEvent((60,)),)),
        settings=PassageSearchSettings(
            beam_width=1,
            assignments_per_parent=1,
            fingers=("index",),
            prepare_next=False,
            assignment_order="marker_distance",
            contact_iterations=120,
        ),
        output=tmp_path,
    )
    assert saved["strategies"][0]["status"] == "static_contact_only"
    assert saved["strategies"][0]["samples"] == []
    media = json.loads(saved["evidence_paths"]["media"].read_text())
    report = media["strategy_reports"][0]
    assert report["animation"] is None
    assert (
        report["independent_audit"]["state_sequence_sha256"]
        == saved["independent_strategy_audits"][0]["state_sequence_sha256"]
    )
    assert report["independent_audit"]["state_kind"] == "static_contact_only"
    assert not list(tmp_path.rglob("*.gif"))
    assert list(tmp_path.rglob("*.png"))
    assert report["independent_audit"]["samples"][0]["sample_index"] == 0


def test_replay_checks_archive_and_input_integrity_before_execution(monkeypatch):
    from accordion_ergonomics_core.verification import RecordVerification

    def invalid(directory):
        return RecordVerification(str(directory), "invalid", (), ("tampered",), ())

    monkeypatch.setattr("accordion_ergonomics_core.verification.verify_record", invalid)
    with pytest.raises(ValueError, match="integrity"):
        ExerciseLibrary().reproduce_argv("passage-stepwise")
