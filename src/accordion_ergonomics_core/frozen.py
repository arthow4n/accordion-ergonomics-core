"""Isolate long-running research code while another agent turn edits the workspace."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


def frozen_run(
    workflow: str, definition: Path, output: Path, source_snapshot: Path | None = None
) -> None:
    """Use the current locked environment with a frozen package-source snapshot."""
    if workflow not in (
        "atlas",
        "sweep",
        "explore",
        "plan",
        "experiment",
        "render",
        "exercise",
        "held",
        "collision-coverage",
        "limit-probe",
        "architecture",
    ):
        raise ValueError("Unsupported frozen workflow")
    output.mkdir(parents=True, exist_ok=True)
    snapshot = output / "source-snapshot.zip"
    with tempfile.TemporaryDirectory(prefix="aec-frozen-") as temporary:
        root = Path(temporary)
        package = root / "accordion_ergonomics_core"
        package.mkdir()
        if source_snapshot is None:
            for source in Path(__file__).parent.glob("*.py"):
                shutil.copyfile(source, package / source.name)
        else:
            with zipfile.ZipFile(source_snapshot) as archive:
                for name in archive.namelist():
                    path = Path(name)
                    if (
                        len(path.parts) != 2
                        or path.parts[0] != package.name
                        or path.suffix != ".py"
                    ):
                        raise ValueError("Unexpected file in research source snapshot")
                    (package / path.name).write_bytes(archive.read(name))
        with zipfile.ZipFile(
            snapshot, "w", compression=zipfile.ZIP_DEFLATED
        ) as archive:
            for source in sorted(package.glob("*.py")):
                info = zipfile.ZipInfo(
                    f"{package.name}/{source.name}", date_time=(1980, 1, 1, 0, 0, 0)
                )
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, source.read_bytes())
        source_digest = hashlib.sha256()
        for source in sorted(package.glob("*.py")):
            source_digest.update(source.name.encode())
            source_digest.update(b"\0")
            source_digest.update(source.read_bytes())
        execution = {
            "package_source_sha256": source_digest.hexdigest(),
            "source_snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            "lock_sha256": hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest(),
            "workflow": workflow,
            "source_snapshot": "source-snapshot.zip",
        }
        (output / "execution.json").write_text(json.dumps(execution, indent=2) + "\n")
        code = (
            "import sys; sys.path.insert(0, sys.argv.pop(1)); "
            "from accordion_ergonomics_core.cli import main; main()"
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(root),
                workflow,
                str(definition.resolve()),
                "--output",
                str(output.resolve()),
            ],
            check=False,
        )

        if completed.returncode:
            raise SystemExit(completed.returncode)
