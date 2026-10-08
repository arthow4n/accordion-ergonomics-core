import copy
import json
from pathlib import Path

import pytest

from accordion_ergonomics_core.experiment import Experiment


@pytest.mark.parametrize(
    ("section", "key", "value"),
    [
        ("solver", "integration_dt_s", 0),
        ("solver", "max_iterations", -1),
        ("solver", "position_tolerance_m", float("inf")),
        ("anatomy", "model", "unvalidated-model"),
    ],
)
def test_experiment_rejects_invalid_parameters(section, key, value) -> None:
    source = json.loads(
        Path("experiments/001-single-contact/experiment.json").read_text()
    )
    invalid = copy.deepcopy(source)
    invalid[section][key] = value
    with pytest.raises(ValueError):
        Experiment.from_dict(invalid)
