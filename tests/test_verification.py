import json
import shutil
from pathlib import Path

import pytest

from accordion_ergonomics_core.verification import verify_record, verify_records


@pytest.mark.parametrize(
    "record",
    [
        "018-collision-step-backtracking",
        "019-selective-self-collision/reference",
        "019-selective-self-collision/index-middle-pairs",
        "019-selective-self-collision/coverage",
        "020-selective-transition-comparison",
        "021-dual-contact-seed-transfer",
        "022-held-contact-with-self-pairs",
    ],
)
def test_published_records_match_archived_sources_and_references(record: str) -> None:
    result = verify_record(Path("experiments") / record)
    assert result.status == "verified", result
    assert result.issues == ()
    assert result.limitations == (
        "Integrity only; no numerical replay or physical validation",
    )


@pytest.mark.parametrize("changed", ["archive", "input", "profiles", "lock"])
def test_record_tampering_is_detected(tmp_path: Path, changed: str) -> None:
    original = Path("experiments/018-collision-step-backtracking")
    for name in (
        "execution.json",
        "source-snapshot.zip",
        "experiment.json",
        "result.json",
    ):
        shutil.copyfile(original / name, tmp_path / name)
    if changed == "archive":
        path = tmp_path / "source-snapshot.zip"
        path.write_bytes(path.read_bytes() + b"unexpected appended bytes")
    elif changed == "input":
        path = tmp_path / "experiment.json"
        path.write_bytes(path.read_bytes() + b"\n")
    else:
        path = tmp_path / "result.json"
        result = json.loads(path.read_text())
        if changed == "profiles":
            result["profiles_sha256"] = "0" * 64
        else:
            result["provenance"]["lock_sha256"] = "0" * 64
        path.write_text(json.dumps(result))
    report = verify_record(tmp_path)
    assert report.status == "invalid"
    assert any("hash mismatch" in issue for issue in report.issues)


def test_missing_metadata_is_partial_and_explicit_inputs_are_unambiguous(
    tmp_path: Path,
) -> None:
    assert verify_record(tmp_path).status == "partial"
    with pytest.raises(ValueError, match="one record directory"):
        verify_records([tmp_path, tmp_path], tmp_path / "experiment.json")


def test_missing_per_result_lock_is_not_fully_verified(tmp_path: Path) -> None:
    original = Path("experiments/018-collision-step-backtracking")
    for name in (
        "execution.json",
        "source-snapshot.zip",
        "experiment.json",
        "result.json",
    ):
        shutil.copyfile(original / name, tmp_path / name)
    path = tmp_path / "result.json"
    result = json.loads(path.read_text())
    del result["provenance"]["lock_sha256"]
    path.write_text(json.dumps(result))
    report = verify_record(tmp_path)
    assert report.status == "partial"
    assert "result lacks recorded-lock hash" in report.limitations
