"""Seeded compositional musical hypotheses on the actual finite keyboard.

Grammar actions propose notes, not motions, ergonomic rules or difficulties.
"""

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .digits import DIGITS
from .instrument import buttons
from .passages import NoteEvent, Passage, fingering_hypotheses
from .targets import digest

FAMILIES = ("stepwise", "repetition", "reversal", "arpeggio", "jump", "chord", "held")


@dataclass(frozen=True)
class GenerationSettings:
    seed: int = 4301
    count: int = 21
    pitch_min: int = 60
    pitch_max: int = 72
    anchor_max: int = 64
    event_min: int = 3
    event_max: int = 4
    proposal_limit: int = 400

    def __post_init__(self):
        if any(type(v) is not int for v in asdict(self).values()):
            raise ValueError("Generation parameters must be integers")
        if self.seed < 0 or self.count < 1 or self.proposal_limit < self.count:
            raise ValueError("Invalid seed or finite generation budget")
        if not 2 <= self.event_min <= self.event_max <= 8:
            raise ValueError("Generate bounded multi-event passages")
        if not self.pitch_min <= self.anchor_max <= self.pitch_max:
            raise ValueError("Invalid finite pitch window")
        available = {b.midi for b in buttons()}
        if len(available & set(range(self.pitch_min, self.pitch_max + 1))) < 3:
            raise ValueError("Pitch window lacks sufficient physical buttons")


def generate_challenges(settings: GenerationSettings | None = None):
    """Compose and deduplicate passages; preserve every proposed grammar action."""
    settings = settings or GenerationSettings()
    rng = np.random.default_rng(settings.seed)
    available = sorted(
        {
            b.midi
            for b in buttons()
            if settings.pitch_min <= b.midi <= settings.pitch_max
        }
    )
    anchors = [p for p in available if p <= settings.anchor_max]
    if not anchors:
        raise ValueError("No physical pitch in anchor window")
    candidates: list[dict[str, Any]] = []
    proposals = []
    seen = set()
    for proposal_index in range(settings.proposal_limit):
        if len(candidates) >= settings.count:
            break
        # Balanced grammar scheduling is a generation prior, not a solved result.
        family = FAMILIES[len(candidates) % len(FAMILIES)]
        anchor = int(rng.choice(anchors))
        count = int(rng.integers(settings.event_min, settings.event_max + 1))
        direction = int(rng.choice((-1, 1)))
        current = anchor
        upper = None
        events = []
        actions = []
        for index in range(count):
            if family in ("chord", "held"):
                if upper is None:
                    options = [p for p in available if 1 <= p - anchor <= 7]
                else:
                    options = [
                        p for p in available if p > anchor and abs(p - upper) <= 4
                    ]
                if not options:
                    break
                upper = int(rng.choice(options))
                # A held branch can start with the single anchor, then add a voice.
                pitches = (
                    (anchor,) if family == "held" and index == 0 else (anchor, upper)
                )
                held = (anchor,) if family == "held" and index < count - 1 else ()
                actions.append(
                    {
                        "action": "retain_anchor_and_choose_voice",
                        "available_voice_pitches": options,
                        "chosen_voice": upper,
                    }
                )
            else:
                if index:
                    if family == "reversal":
                        direction *= -1
                    deltas = {
                        "stepwise": (1, 2),
                        "repetition": (0, 0, 0, 1, 2),
                        "reversal": (1, 2, 3),
                        "arpeggio": (3, 4, 7),
                        "jump": (5, 7, 9, 12),
                    }[family]
                    if family == "repetition" and index == 1:
                        deltas = (0,)
                    allowed = [
                        (d, current + direction * d)
                        for d in deltas
                        if current + direction * d in available
                    ]
                    if not allowed:
                        direction *= -1
                        allowed = [
                            (d, current + direction * d)
                            for d in deltas
                            if current + direction * d in available
                        ]
                    if not allowed:
                        break
                    chosen = int(rng.integers(len(allowed)))
                    delta, current = allowed[chosen]
                    actions.append(
                        {
                            "action": "choose_interval",
                            "direction": direction,
                            "available_interval_destinations": allowed,
                            "chosen_interval": delta,
                            "chosen_pitch": current,
                        }
                    )
                pitches, held = (current,), ()
            events.append(NoteEvent(pitches, held))
        proposal = {
            "proposal_index": proposal_index,
            "family": family,
            "anchor_pitch": anchor,
            "actions": actions,
        }
        if len(events) != count:
            proposal["status"] = "rejected_finite_keyboard_dead_end"
            proposals.append(proposal)
            continue
        signature = digest([asdict(e) for e in events])
        if signature in seen:
            proposal["status"] = "duplicate_musical_sequence"
            proposals.append(proposal)
            continue
        seen.add(signature)
        target_id = "generated-" + signature[:16]
        passage = Passage(target_id, tuple(events), "generated_compositional_grammar")
        proposal.update(status="generated_hypothesis", target_id=target_id)
        proposals.append(proposal)
        candidates.append(
            {
                "id": target_id,
                "family": family,
                "passage": passage.to_dict(),
                "proposal_index": proposal_index,
                "musical_signature_sha256": signature,
                "unconditioned_assignment_counts": [
                    len(fingering_hypotheses(e, DIGITS)) for e in events
                ],
                "status": "generated_unevaluated_hypothesis",
            }
        )
    return {
        "settings": asdict(settings),
        "candidates": candidates,
        "proposals": proposals,
        "status": "generation_budget_satisfied"
        if len(candidates) == settings.count
        else "generation_budget_exhausted",
        "claim": (
            "Musical hypotheses only; physical combinations are unconditioned "
            "on future held bindings and are not solves"
        ),
    }
