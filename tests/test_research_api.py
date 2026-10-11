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
