import subprocess
import zipfile
from pathlib import Path

from accordion_ergonomics_core import frozen


def test_running_code_is_isolated_from_workspace_edits(
    tmp_path: Path, monkeypatch
) -> None:
    package = tmp_path / "editable"
    package.mkdir()
    original = package / "model.py"
    original.write_text("VALUE = 1\n")
    monkeypatch.setattr(frozen, "__file__", str(package / "frozen.py"))
    observed = []

    def simulate_child(args, check):
        copy = Path(args[3]) / "accordion_ergonomics_core" / "model.py"
        original.write_text("VALUE = 2\n")
        observed.append(copy.read_text())
        return subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(subprocess, "run", simulate_child)
    output = tmp_path / "result"
    frozen.frozen_run("atlas", tmp_path / "input.json", output)
    assert observed == ["VALUE = 1\n"]
    with zipfile.ZipFile(output / "source-snapshot.zip") as archive:
        assert archive.read("accordion_ergonomics_core/model.py") == b"VALUE = 1\n"
    frozen.frozen_run(
        "atlas",
        tmp_path / "input.json",
        tmp_path / "replay",
        output / "source-snapshot.zip",
    )
    assert observed == ["VALUE = 1\n", "VALUE = 1\n"]
