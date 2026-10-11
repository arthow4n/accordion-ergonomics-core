import pytest

from accordion_ergonomics_core.anatomy import DIGITS
from accordion_ergonomics_core.passages import NoteEvent, Passage, fingering_hypotheses


def test_all_digits_and_duplicate_buttons_are_candidates():
    event = NoteEvent((60,))
    a = fingering_hypotheses(event, seed=41)
    assert a == fingering_hypotheses(event, seed=41)
    assert {h["contacts"][0]["finger"] for h in a} == set(DIGITS)
    assert {h["contacts"][0]["button_id"] for h in a} == {"r1c5", "r4c5"}
    assert len(a) == 10
    assert all(h["status"] == "generated_hypothesis" for h in a)


def test_chords_hold_exact_binding_and_reject_invalid_passages():
    event = NoteEvent((60, 64))
    held = ({"midi": 60, "button_id": "r4c5", "finger": "little"},)
    choices = fingering_hypotheses(event, held=held)
    assert choices
    assert all(
        h["contacts"][0]["finger"] == "little"
        and h["contacts"][0]["button_id"] == "r4c5"
        for h in choices
    )
    assert all(len({c["finger"] for c in h["contacts"]}) == 2 for h in choices)
    passage = Passage("hold", (NoteEvent((60, 61), (60,)), NoteEvent((60, 64))))
    assert passage.to_dict()["events"][0]["hold_to_next"] == (60,)
    with pytest.raises(ValueError, match="disappears"):
        Passage("invalid", (NoteEvent((60,), (60,)), NoteEvent((61,))))
    with pytest.raises(ValueError, match="distinct"):
        NoteEvent((60, 60))
    with pytest.raises(ValueError, match="finite"):
        NoteEvent((0,))
