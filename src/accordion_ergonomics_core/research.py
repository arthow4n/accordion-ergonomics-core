"""Small internal consumer API; evidence stays in this Git checkout.

Numerical engines load only when requested. No publication or remote services.
"""

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .digits import DIGITS
from .movement_evidence import state_digest, validate_strategy
from .passages import NoteEvent as NoteEvent
from .passages import Passage as Passage
from .passages import fingering_hypotheses as fingering_hypotheses
from .targets import ROOT


class ExerciseLibrary:
    def __init__(self, root: Path = ROOT):
        self.root = root.resolve()
        self.catalog = json.loads((self.root / "targets/manifest.json").read_text())

    def query(
        self,
        *,
        family: str | None = None,
        finger: str | None = None,
        generated: bool | None = None,
    ):
        if finger is not None and finger not in DIGITS:
            raise ValueError("Unknown named digit")
        if generated is not None and type(generated) is not bool:
            raise ValueError("Generated filter must be boolean")
        return [
            t
            for t in self.catalog["targets"]
            if (family is None or t["family"] == family)
            and (
                generated is None
                or t.get("provenance", "curated").startswith("generated") == generated
            )
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

    def search_record(
        self, target_id: str, *, trial_id: str | None = None
    ) -> dict[str, Any]:
        target = self.target(target_id)
        if trial_id is not None:
            trial = next(
                (t for t in target.get("search_trials", []) if t["id"] == trial_id),
                None,
            )
            if trial is None:
                raise KeyError("Unknown recorded trial: " + trial_id)
            reference = trial["evidence"]
        else:
            reference = next(
                (
                    r
                    for r in target.get("evidence", [])
                    if r["role"] == "connected_passage_search"
                ),
                None,
            )
            if reference is None:
                raise ValueError("Target has no recorded passage search")
        return json.loads(self.evidence_path(reference).read_text())

    def trajectory(
        self,
        target_id: str,
        strategy_id: str = "strategy-0",
        *,
        trial_id: str | None = None,
    ):
        saved = self.search_record(target_id, trial_id=trial_id)
        strategy = next(
            (s for s in saved["strategies"] if s["id"] == strategy_id), None
        )
        if strategy is None:
            raise KeyError("No recorded complete strategy: " + strategy_id)
        validate_strategy(saved, strategy)
        return {"joint_names": saved["joint_names"], **strategy}

    def media_record(self, target_id: str):
        target = self.target(target_id)
        ref = next(
            (
                r
                for r in target.get("evidence", [])
                if r["role"] == "passage_media_audit"
            ),
            None,
        )
        if ref is None:
            raise ValueError("Target has no recorded passage media")
        return json.loads(self.evidence_path(ref).read_text()), ref

    def diagnostics(
        self,
        target_id: str,
        strategy_id: str = "strategy-0",
        *,
        trial_id: str | None = None,
    ):
        saved = self.search_record(target_id, trial_id=trial_id)
        strategy = self.trajectory(target_id, strategy_id, trial_id=trial_id)
        if "independent_strategy_audits" in saved:
            index = next(
                i for i, s in enumerate(saved["strategies"]) if s["id"] == strategy_id
            )
            audit = saved["independent_strategy_audits"][index]
        else:
            media, _ = self.media_record(target_id)
            report = next(
                (
                    r
                    for r in media["strategy_reports"]
                    if r["strategy_id"] == strategy_id
                ),
                None,
            )
            if report is None:
                raise ValueError(
                    "This numerical strategy has no independent saved audit"
                )
            audit = report["independent_audit"]
        if audit["state_sequence_sha256"] != state_digest(strategy["samples"]):
            raise ValueError("Diagnostics differ from recorded movement states")
        return audit

    def frame_sequence(self, target_id: str, strategy_id: str = "strategy-0"):
        strategy = self.trajectory(target_id, strategy_id)
        media, ref = self.media_record(target_id)
        report = next(
            (r for r in media["strategy_reports"] if r["strategy_id"] == strategy_id),
            None,
        )
        if report is None or not report["animation"]:
            raise ValueError("No accepted recorded animation for this strategy")
        animation = report["animation"]
        if animation["state_sequence_sha256"] != state_digest(strategy["samples"]):
            raise ValueError("Frames reference different movement evidence")
        frames = []
        for frame in animation["frames"]:
            sample = strategy["samples"][frame["sample_index"]]
            if (
                frame["qpos_rad"] != sample["qpos_rad"]
                or frame["active_contacts"] != sample["active_contacts"]
                or frame["roles"] != sample["roles"]
            ):
                raise ValueError(
                    "Frame state/requirements differ from actual trajectory"
                )
            image = Path(ref["path"]).parent / strategy_id / frame["frame"]
            path = self.evidence_path(
                {"path": str(image), "sha256": frame["frame_sha256"]}
            )
            frames.append({**frame, "path": path})
        return frames

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
        from .verification import verify_record

        checked = verify_record(self.root / reference["frozen_root"])
        if checked.status != "verified":
            raise ValueError("Archived replay source/input integrity is incomplete")
        return list(reference["reproduce_argv"])

    def reproduce(self, target_id: str, output: Path, *, media: bool = True):
        """Execute the exact archived source; keep original published files intact."""
        output = output.resolve()
        if output.exists() and (not output.is_dir() or any(output.iterdir())):
            raise ValueError("Replay output must be empty to preserve record identity")
        argv = self.reproduce_argv(target_id, media=media)
        definition = (self.root / argv[argv.index("frozen") + 2]).resolve()
        argv[argv.index("--output") + 1] = str(output)
        subprocess.run(argv, cwd=self.root, check=True)
        metadata = output / "execution.json"
        execution = json.loads(metadata.read_text())
        execution["definition_reference"] = os.path.relpath(definition, output)
        metadata.write_text(json.dumps(execution, indent=2) + "\n")
        return output


def discover_passage(
    passage: Passage,
    *,
    settings=None,
    reference=None,
    root: Path | None = None,
    output: Path | None = None,
):
    """Search and independently audit a passage; optional output saves actual media.

    Long research runs should use the frozen CLI while source edits continue.
    """
    from .experiment import Experiment
    from .passage_experiment import trim_iterations
    from .passage_media import independent_samples, run_passage_media
    from .passage_search import reference_experiment, search_passage
    from .provenance import compiled_model_digest
    from .scene import build_scene

    if (
        output is not None
        and output.exists()
        and (not output.is_dir() or any(output.iterdir()))
    ):
        raise ValueError("Discovery output must be empty")
    saved = search_passage(passage, reference or reference_experiment(root), settings)
    saved["scene_input"] = saved.pop("input")
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != saved["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Independent audit model differs from numerical search")
    audits = []
    for strategy in saved["strategies"]:
        if strategy["status"] == "sampled_connected_path":
            validate_strategy(saved, strategy)
            states = strategy["samples"]
        else:
            event = strategy["events"][0]
            states = [
                {
                    "qpos_rad": event["qpos_rad"],
                    "active_contacts": event["contacts"],
                    "roles": {c["finger"]: "required" for c in event["contacts"]},
                    "event_interval": 0,
                }
            ]
        report = independent_samples(scene, states, e.solver.penetration_tolerance_m)
        report["state_kind"] = strategy["status"]
        audits.append(report)
    saved["independent_strategy_audits"] = audits
    saved["execution_mode"] = (
        "direct_internal_API; use frozen CLI for changing-source long runs"
    )
    trim_iterations(saved)
    if output is not None:
        output.mkdir(parents=True, exist_ok=True)
        path = output / "search.json"
        path.write_text(
            json.dumps(saved, separators=(",", ":"), allow_nan=False) + "\n"
        )
        definition = output / "media-input.json"
        definition.write_text(
            json.dumps(
                {
                    "search_result": "search.json",
                    "search_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "strategy_limit": len(saved["strategies"]),
                    "frames": max(9, len(passage.events)),
                },
                indent=2,
            )
            + "\n"
        )
        run_passage_media(definition, output / "media")
        saved["evidence_paths"] = {
            "search": path,
            "media": output / "media/result.json",
        }
    return saved


def generate_challenges(settings=None):
    """Generate deterministic musical hypotheses; these are not physical results."""
    from .generation import generate_challenges as generate

    return generate(settings)


def discover_challenges(
    output: Path,
    *,
    generation=None,
    settings=None,
    reference=None,
    root: Path | None = None,
):
    """Evaluate generated passages and retain evidence; use frozen CLI for long runs."""
    from .discovery import discover_challenges as discover
    from .passage_search import reference_experiment

    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Discovery output must be empty")
    result = discover(
        reference or reference_experiment(root), output, generation, settings
    )
    (output / "result.json").write_text(
        json.dumps(result, separators=(",", ":"), allow_nan=False) + "\n"
    )
    return result
