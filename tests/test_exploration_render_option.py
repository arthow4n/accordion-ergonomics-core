import hashlib
import json
from pathlib import Path

import numpy as np

from accordion_ergonomics_core.exploration import run_exploration


def test_contact_discovery_can_publish_numerical_evidence_without_renders(
    tmp_path, monkeypatch
):
    baseline = Path(
        "experiments/037-upper-anchor-regression/central/result.json"
    ).resolve()
    definition = tmp_path / "experiment.json"
    definition.write_text(
        json.dumps(
            {
                "id": "render-free-contact-control",
                "render": False,
                "baseline_result": str(baseline),
                "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
                "candidate_search": {"offsets_rad": [], "max_iterations": 2},
                "targets": [
                    {
                        "id": "c4",
                        "contacts": [{"row": 1, "column": 5, "finger": "index"}],
                    }
                ],
            }
        )
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Rendering must not be invoked by render:false")

    monkeypatch.setattr("accordion_ergonomics_core.render.render_views", forbidden)
    output = tmp_path / "output"
    result = run_exploration(definition, output)
    assert len(result["targets"][0]["candidates"]) == 1
    saved = json.loads((output / "c4/candidate-0/result.json").read_text())
    assert saved["status"] == "success"
    np.testing.assert_allclose(
        saved["qpos_rad"],
        json.loads(baseline.read_text())["qpos_rad"],
        atol=1e-14,
        rtol=0,
    )
    assert not list(output.rglob("*.png"))
