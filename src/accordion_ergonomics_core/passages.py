"""Musical intent and finite five-finger hypotheses, independent of IK and media."""

from dataclasses import asdict, dataclass
from itertools import permutations, product
from typing import Any

import numpy as np

from .digits import DIGITS
from .instrument import buttons_for_pitch


@dataclass(frozen=True)
class NoteEvent:
    pitches: tuple[int, ...]
    hold_to_next: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "pitches", tuple(self.pitches))
        object.__setattr__(self, "hold_to_next", tuple(self.hold_to_next))
        if not 1 <= len(self.pitches) <= 5 or len(set(self.pitches)) != len(
            self.pitches
        ):
            raise ValueError("An event requires one to five distinct pitches")
        if any(type(p) is not int or not buttons_for_pitch(p) for p in self.pitches):
            raise ValueError("Pitch is absent from the finite C-system keyboard")
        if len(set(self.hold_to_next)) != len(self.hold_to_next) or not set(
            self.hold_to_next
        ) <= set(self.pitches):
            raise ValueError("Held pitches must be a distinct subset of this event")


@dataclass(frozen=True)
class Passage:
    id: str
    events: tuple[NoteEvent, ...]
    provenance: str = "consumer_supplied"

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(self.events))
        if (
            not self.id
            or not self.events
            or any(not isinstance(e, NoteEvent) for e in self.events)
        ):
            raise ValueError("A passage requires an ID and musical events")
        if self.events[-1].hold_to_next:
            raise ValueError("Final event cannot hold into an absent event")
        for a, b in zip(self.events[:-1], self.events[1:], strict=True):
            if not set(a.hold_to_next) <= set(b.pitches):
                raise ValueError("Held note disappears from the next event")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fingering_hypotheses(
    event: NoteEvent,
    fingers: tuple[str, ...] = DIGITS,
    held: tuple[dict[str, Any], ...] = (),
    seed: int = 0,
) -> list[dict[str, Any]]:
    """Enumerate physical alternatives; a hypothesis is never a solved pose.

    Shuffle deterministically before a caller truncates its numerical budget.
    Every finger is eligible by default; no pedagogical or anatomical ranking.
    Held bindings identify exact physical button AND finger, not pitch alone.
    """
    if not fingers or len(set(fingers)) != len(fingers) or set(fingers) - set(DIGITS):
        raise ValueError("Fingers must be a distinct named subset")
    if type(seed) is not int or seed < 0:
        raise ValueError("Seed must be a nonnegative integer")
    if any(h["midi"] not in event.pitches for h in held):
        raise ValueError("Held contact pitch is missing")
    if len({h["finger"] for h in held}) != len(held) or len(
        {h["midi"] for h in held}
    ) != len(held):
        raise ValueError("Held contacts have duplicate pitch or finger")
    result = []
    for physical in product(*(buttons_for_pitch(p) for p in event.pitches)):
        for assignment in permutations(fingers, len(physical)):
            contacts = [
                {
                    "button_id": b.id,
                    "row": b.row,
                    "column": b.column,
                    "midi": b.midi,
                    "finger": d,
                    "behavior": "hold"
                    if b.midi in event.hold_to_next
                    else "release_after_event",
                }
                for b, d in zip(physical, assignment, strict=True)
            ]
            if all(
                any(
                    c["midi"] == h["midi"]
                    and c["button_id"] == h["button_id"]
                    and c["finger"] == h["finger"]
                    for c in contacts
                )
                for h in held
            ):
                result.append({"contacts": contacts, "status": "generated_hypothesis"})
    rng = np.random.default_rng(seed)
    return [result[int(i)] for i in rng.permutation(len(result))]
