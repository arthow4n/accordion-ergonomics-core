"""Generation/selection semantics: synthetic outcome fixtures never imply anatomy."""

from typing import Any

import pytest

from accordion_ergonomics_core.discovery import adaptive_choices, selection
from accordion_ergonomics_core.generation import (
    FAMILIES,
    GenerationSettings,
    generate_challenges,
)
from accordion_ergonomics_core.instrument import buttons_for_pitch
from accordion_ergonomics_core.passages import NoteEvent, Passage


def test_compositional_generation_is_deterministic_diverse_and_finite():
    a = generate_challenges()
    assert a == generate_challenges()
    assert a != generate_challenges(GenerationSettings(seed=4302))
    assert len(a["candidates"]) == 21
    assert len({c["id"] for c in a["candidates"]}) == 21
    assert {c["family"] for c in a["candidates"]} == set(FAMILIES)
    assert (
        len(
            {
                tuple(tuple(e["pitches"]) for e in c["passage"]["events"])
                for c in a["candidates"]
            }
        )
        >= 18
    )
    for c in a["candidates"]:
        p = c["passage"]
        Passage(p["id"], tuple(NoteEvent(**e) for e in p["events"]), p["provenance"])
        assert c["status"] == "generated_unevaluated_hypothesis"
        assert all(buttons_for_pitch(n) for e in p["events"] for n in e["pitches"])
        assert all(v >= 5 for v in c["unconditioned_assignment_counts"])
    assert all(p["actions"] for p in a["proposals"])
    for kwargs in (
        {"count": 0},
        {"event_min": 1},
        {"pitch_min": 0, "pitch_max": 2, "anchor_max": 1},
    ):
        with pytest.raises(ValueError):
            GenerationSettings(**kwargs)


def test_allocation_uses_observed_paths_and_prefixes_and_selection_keeps_failure():
    # Synthetic logical selection fixtures, deliberately containing no physical qpos.
    trials: list[dict[str, Any]] = [
        {
            "id": "a",
            "candidate_id": "one",
            "family": "stepwise",
            "observed": {
                "sampled_proxy_accepted_strategies": 1,
                "completed_strategies": 1,
                "deepest_connected_event_count": 3,
                "strategies": [{"played_digits": ["index", "little"]}],
            },
        },
        {
            "id": "b",
            "candidate_id": "two",
            "family": "held",
            "observed": {
                "sampled_proxy_accepted_strategies": 0,
                "completed_strategies": 0,
                "deepest_connected_event_count": 2,
                "strategies": [],
            },
        },
        {
            "id": "c",
            "candidate_id": "three",
            "family": "chord",
            "observed": {
                "sampled_proxy_accepted_strategies": 0,
                "completed_strategies": 0,
                "deepest_connected_event_count": 0,
                "strategies": [],
            },
        },
    ]
    choices = adaptive_choices(trials, 2)
    assert [c["parent_evaluation"] for c in choices] == ["a", "b"]
    assert adaptive_choices(trials, 0) == []
    retained = selection(
        trials, [{"id": e["candidate_id"], "family": e["family"]} for e in trials], 2
    )
    assert [s["evaluation_id"] for s in retained] == ["a", "b"]
    assert "no impossibility" in retained[-1]["reason"]


def test_generated_catalog_links_real_trials_and_media_to_exact_searches():
    import json

    from accordion_ergonomics_core.research import ExerciseLibrary

    library = ExerciseLibrary()
    targets = [
        t
        for t in library.query()
        if t.get("provenance") == "generated_compositional_grammar"
    ]
    assert len(targets) == 5
    arpeggio = next(t for t in targets if t["family"] == "arpeggio")
    assert arpeggio["generation"]["candidate"]["id"] == arpeggio["id"]
    assert len(arpeggio["search_trials"]) == 2
    assert len(library.media(arpeggio["id"])) == 2
    for trial in arpeggio["search_trials"]:
        saved = json.loads(library.evidence_path(trial["evidence"]).read_text())
        assert saved["passage"]["id"] == arpeggio["id"]
        assert trial["observed"]["budget"] == saved["budget"]
    trajectory = library.trajectory(arpeggio["id"])
    assert {c["finger"] for e in trajectory["events"] for c in e["contacts"]} == {
        "index",
        "little",
    }
    held = next(t for t in targets if t["family"] == "held")
    assert held["realizations"] == [] and library.media(held["id"]) == []
    assert len(held["search_trials"]) == 2
