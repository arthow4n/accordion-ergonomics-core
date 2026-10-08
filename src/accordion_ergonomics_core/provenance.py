"""Hash source inputs without publishing environment values or local secrets."""

import hashlib
import os
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Any

import myo_sim


def current_execution_metadata(model: Any) -> dict[str, Any]:
    """Describe this execution, rather than inheriting an input record's runtime."""
    return {
        "provenance": {
            "compiled_model_sha256": compiled_model_digest(model),
            "anatomy_source_sha256": anatomy_digest(),
            "project_source_sha256": project_source_digest(),
            "lock_sha256": hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest(),
            "render_backend": os.environ.get("MUJOCO_GL", "egl"),
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {
                p: version(p)
                for p in (
                    "mujoco",
                    "myo-sim",
                    "mink",
                    "numpy",
                    "scipy",
                    "clarabel",
                    "pillow",
                )
            },
        },
    }


def anatomy_digest() -> str:
    root = Path(myo_sim.__file__).parent
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def project_source_digest() -> str:
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def compiled_model_digest(model: Any) -> str:
    """Hash the complete compiled model before diagnostic display mutations.

    MJB captures transformed geometry, limits, equality constraints and assets.
    It is engine-version-specific; a mismatch requires an explicit recomputation.
    """
    import numpy as np

    from ._engine import mujoco

    buffer = np.zeros(mujoco.mj_sizeModel(model), dtype=np.uint8)
    mujoco.mj_saveModel(model, None, buffer)
    return hashlib.sha256(buffer.tobytes()).hexdigest()
