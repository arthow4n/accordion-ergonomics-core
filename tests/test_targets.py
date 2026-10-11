"""Evidence and interpretation guards for the provisional exercise library."""

import copy
import json
from pathlib import Path

import pytest

from accordion_ergonomics_core.targets import (
    ROOT,
    build_catalog,
    digest,
    events_with_notes,
    validate_catalog,
    verify_target,
)


def test_catalog_deterministic_and_committed():
    catalog = build_catalog()
    assert catalog == build_catalog()
    assert catalog == json.loads((ROOT / "targets/manifest.json").read_text())
    assert all(t["human_feasibility"] is None for t in catalog["targets"])


def test_realization_identity_and_equivalent_buttons():
    target = next(t for t in build_catalog()["targets"] if t["id"] == "equivalent-c4")
    a, b = target["realizations"]
    assert a["id"] != b["id"]
    assert (
        a["events"][0]["contacts"][0]["midi"]
        == b["events"][0]["contacts"][0]["midi"]
        == 60
    )
    branch_ids = [b["id"] for b in a["branches"]]
    assert len(set(branch_ids)) == len(branch_ids)
    assert digest({"qpos": [1, 2], "world": "v3"}) == digest(
        {"world": "v3", "qpos": [1, 2]}
    )


def test_schema_does_not_promote_missing_evidence():
    catalog = copy.deepcopy(build_catalog())
    r = catalog["targets"][0]["realizations"][0]
    r["evidence"] = []
    with pytest.raises(ValueError, match="lacks actual evidence"):
        validate_catalog(catalog)
    r["status"] = "hypothesis"
    validate_catalog(catalog)
    r["validity"]["human_feasibility"] = True
    with pytest.raises(ValueError, match="No human"):
        validate_catalog(catalog)


def test_contact_mapping_and_scope():
    with pytest.raises(ValueError, match="Only index"):
        events_with_notes([{"contacts": [{"button_id": "r1c5", "finger": "thumb"}]}])
    with pytest.raises(KeyError):
        events_with_notes([{"contacts": [{"button_id": "r1c999", "finger": "index"}]}])


def test_integrity_detects_modified_evidence(tmp_path: Path):
    catalog = copy.deepcopy(build_catalog())
    ref = catalog["targets"][0]["realizations"][0]["evidence"][0]
    ref["path"] = "modified.json"
    (tmp_path / "modified.json").write_text("{}")
    with pytest.raises(ValueError, match="Evidence changed"):
        verify_target(catalog, tmp_path, catalog["targets"][0]["id"])
