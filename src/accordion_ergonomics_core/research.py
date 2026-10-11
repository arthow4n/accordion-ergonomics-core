"""Small internal consumer API; evidence stays in this Git checkout.

Numerical engines load only when requested. No publication or remote services.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

from .movement_evidence import validate_strategy
from .passages import NoteEvent as NoteEvent
from .passages import Passage as Passage
from .passages import fingering_hypotheses as fingering_hypotheses
from .targets import ROOT


class ExerciseLibrary:
    def __init__(self, root: Path = ROOT):
        self.root = root.resolve()
        self.catalog = json.loads((self.root / "targets/manifest.json").read_text())

    def query(self, *, family: str | None = None, finger: str | None = None):
        return [
            t
            for t in self.catalog["targets"]
            if (family is None or t["family"] == family)
            and (
                finger is None
                or any(
                    c["finger"] == finger
                    for r in t["realizations"]
                    for e in r["events"]
                    for c in e["contacts"]
                )
            )
        ]

    def target(self, target_id: str) -> dict[str, Any]:
        try:
            return next(t for t in self.catalog["targets"] if t["id"] == target_id)
        except StopIteration:
            raise KeyError(target_id) from None

    def evidence_path(self, reference: dict[str, Any]) -> Path:
        path = (self.root / reference["path"]).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("Evidence escapes the library checkout")
        if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
            raise ValueError("Evidence differs from its catalog commitment")
        return path

    def search_record(self, target_id: str) -> dict[str, Any]:
        target = self.target(target_id)
        reference = next(
            r
            for r in target.get("evidence", [])
            if r["role"] == "connected_passage_search"
        )
        return json.loads(self.evidence_path(reference).read_text())

    def trajectory(self, target_id: str, strategy_id: str = "strategy-0"):
        saved = self.search_record(target_id)
        strategy = next(s for s in saved["strategies"] if s["id"] == strategy_id)
        validate_strategy(saved, strategy)
        return {"joint_names": saved["joint_names"], **strategy}

    def media(self, target_id: str, *, role: str = "animation") -> list[Path]:
        target = self.target(target_id)
        refs = target.get("evidence", []) or [
            r for s in target["realizations"] for r in s["evidence"]
        ]
        return list(
            dict.fromkeys(self.evidence_path(r) for r in refs if r["role"] == role)
        )

    def reproduce_argv(self, target_id: str, *, media: bool = True) -> list[str]:
        role = "passage_media_audit" if media else "connected_passage_search"
        reference = next(
            r for r in self.target(target_id)["evidence"] if r["role"] == role
        )
        self.evidence_path(reference)
        return list(reference["reproduce_argv"])


def discover_passage(passage: Passage, *, settings=None, reference=None):
    """Run bounded numerical search; returned paths need independent media audits."""
    from .passage_search import search_passage

    return search_passage(passage, reference, settings)


def generate_challenges(settings=None):
    """Generate deterministic musical hypotheses; these are not physical results."""
    from .generation import generate_challenges as generate

    return generate(settings)


def discover_challenges(
    output: Path, *, generation=None, settings=None, reference=None
):
    """Evaluate generated passages and retain evidence; use frozen CLI for long runs."""
    from .discovery import discover_challenges as discover
    from .passage_search import reference_experiment

    return discover(reference or reference_experiment(), output, generation, settings)
