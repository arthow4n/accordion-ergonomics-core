import json
from pathlib import Path

import numpy as np

from accordion_ergonomics_core.cli import run_experiment


def test_endpoint_input_replays_selected_configuration(tmp_path: Path) -> None:
    root = Path("experiments/015-exercise-endpoint-replay")
    saved = json.loads((root / "endpoint.json").read_text())
    replay = run_experiment(root / "endpoint-input.json", tmp_path, False)
    assert replay["status"] == "success"
    assert replay["target"]["button_id"] == saved["target"]["button_id"]
    assert replay["input"]["id"] == saved["experiment_id"]
    np.testing.assert_allclose(replay["qpos_rad"], saved["qpos_rad"], atol=1e-12)
    np.testing.assert_allclose(saved["initial_qpos_rad"], saved["qpos_rad"], atol=1e-12)
    assert replay["profiles_sha256"] == saved["profiles_sha256"]
    assert (
        replay["provenance"]["compiled_model_sha256"]
        == saved["provenance"]["compiled_model_sha256"]
    )
