"""Hash source inputs without publishing environment values or local secrets."""

import hashlib
from pathlib import Path
from typing import Any

import myo_sim


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
