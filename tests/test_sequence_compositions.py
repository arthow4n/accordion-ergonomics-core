import hashlib
import json
from pathlib import Path

ROOT = Path("experiments/040-exercise-library")


def test_published_sequence_segments_have_exact_continuity_and_recorded_identity():
    compositions = json.loads((ROOT / "sequence-compositions.json").read_text())
    for sequence in compositions["sequences"]:
        states = []
        endpoints = []
        for segment in sequence["segments"]:
            path = ROOT / segment["result"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == segment["sha256"]
            saved = json.loads(path.read_text())
            assert saved["status"] == "sampled_path_found"
            assert (
                saved["provenance"]["compiled_model_sha256"]
                == sequence["compiled_model_sha256"]
            )
            samples = saved["samples"][::-1] if segment["reverse"] else saved["samples"]
            contacts = (
                saved["endpoints"][::-1] if segment["reverse"] else saved["endpoints"]
            )
            if states:
                assert states[-1] == samples[0]["qpos_rad"]
            else:
                endpoints.append(contacts[0]["input"]["contacts"][0])
            endpoints.append(contacts[-1]["input"]["contacts"][0])
            states.extend(
                s["qpos_rad"] for s in (samples if not states else samples[1:])
            )
        assert len(states) == sequence["sample_count"]
        digest = hashlib.sha256(
            json.dumps(states, separators=(",", ":")).encode()
        ).hexdigest()
        assert digest == sequence["sample_states_sha256"]
        assert [(c["row"], c["column"], c["finger"]) for c in endpoints] == [
            (c["row"], c["column"], c["finger"]) for c in sequence["events"]
        ]
        assert sequence["human_feasibility"] is None


def test_reusable_composer_reproduces_records_and_rejects_jumps():
    import copy

    import pytest

    from accordion_ergonomics_core.sequences import compose_sequence

    definition = json.loads((ROOT / "sequences/experiment.json").read_text())
    saved = json.loads((ROOT / "sequences/result.json").read_text())
    for request, record in zip(
        definition["sequences"], saved["sequences"], strict=True
    ):
        composed = compose_sequence(request, ROOT / "sequences")
        assert composed["sample_states_sha256"] == record["sample_states_sha256"]
        assert composed["descriptors"] == record["descriptors"]
        assert composed["events"] == record["events"]
    request = copy.deepcopy(definition["sequences"][0])
    request["segments"][1]["reverse"] = False
    with pytest.raises(ValueError, match="discontinuous"):
        compose_sequence(request, ROOT / "sequences")
