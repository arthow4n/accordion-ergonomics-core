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

    def playing_record(self):
        """Versioned whole-hand/lifecycle evidence with unchanged catalog identities."""
        index = json.loads(
            (self.root / "targets/playing-assessments-v3.json").read_text()
        )
        record = json.loads(self.evidence_path(index["evidence"]).read_text())
        if index["assessment_version"] != record["assessment_version"]:
            raise ValueError("Playing assessment index differs from evidence")
        if record["assessment_version"] != "playing-region-lifecycle-v3":
            raise ValueError("Unsupported playing assessment version")
        self.evidence_path(
            dict(path="targets/manifest.json", sha256=record["catalog_sha256"])
        )
        return record

    def playing_assessment(self, target_id: str):
        self.target(target_id)
        record = self.playing_record()
        return dict(
            assessment_version=record["assessment_version"],
            **next(t for t in record["targets"] if t["target_id"] == target_id),
        )

    def playing_cases(self, target_id: str | None = None):
        record = self.playing_record()
        if target_id is not None:
            self.target(target_id)
        return (record.get("benchmarks", []) if target_id is None else []) + [
            c
            for t in record["targets"]
            if target_id is None or t["target_id"] == target_id
            for c in t["cases"]
        ]

    def playing_case(self, case_id: str):
        binding = next(
            (c for c in self.playing_cases() if c["case_id"] == case_id), None
        )
        if binding is None:
            raise KeyError(case_id)
        saved = json.loads(self.evidence_path(binding["evidence"]).read_text())
        case = next(c for c in saved["cases"] if c["id"] == case_id)
        if case["region"]["state_sequence_sha256"] != binding["state_sequence_sha256"]:
            raise ValueError("Playing state identity differs from assessment")
        return case

    def playing_search(self, case_id: str):
        """Retrieve actual hypotheses, solves, budgets and branch decisions."""
        case = self.playing_case(case_id)
        binding = next(c for c in self.playing_cases() if c["case_id"] == case_id)
        definition = self.root / binding["definition"]
        reference = case["source"]
        path = (definition.parent / reference["search_result"]).resolve()
        saved = json.loads(
            self.evidence_path(
                dict(
                    path=str(path.relative_to(self.root)),
                    sha256=reference["search_sha256"],
                )
            ).read_text()
        )
        return saved

    def playing_trajectory(self, case_id: str):
        case = self.playing_case(case_id)
        saved = self.playing_search(case_id)
        strategy = next(
            s for s in saved["strategies"] if s["id"] == case["strategy_id"]
        )
        validate_strategy(saved, strategy)
        if state_digest(strategy["samples"]) != case["region"]["state_sequence_sha256"]:
            raise ValueError("Playing trajectory differs from assessment")
        return strategy

    def playing_media(self, case_id: str):
        binding = next(
            (c for c in self.playing_cases() if c["case_id"] == case_id), None
        )
        if binding is None:
            raise KeyError(case_id)
        result_path = self.evidence_path(binding["evidence"])
        saved = json.loads(result_path.read_text())
        case = self.playing_case(case_id)
        media = []
        for relative, digest in saved["artifact_sha256"].items():
            if relative.startswith(case_id + "/"):
                path = result_path.parent / relative
                media.append(
                    self.evidence_path(
                        dict(path=str(path.relative_to(self.root)), sha256=digest)
                    )
                )
        return dict(
            manifest=case["media"],
            paths=media,
            playback_claim=(
                "Actual recorded samples; display intervals are not physiological time"
            ),
        )

    def playing_initial_approach(self, case_id: str):
        """Retrieve a separately audited connection from the resolved numerical seed."""
        case = self.playing_case(case_id)
        for ref in self.playing_record()["reviews"]:
            path = self.evidence_path(ref)
            saved = json.loads(path.read_text())
            for record in saved["records"]:
                source = record["source"]
                if (
                    source.get("kind") == "initial_approach"
                    and source["search_sha256"] == case["source"]["search_sha256"]
                    and source.get("strategy_id", "strategy-0") == case["strategy_id"]
                ):
                    media = [
                        self.evidence_path(
                            dict(
                                path=str(
                                    (path.parent / relative).relative_to(self.root)
                                ),
                                sha256=digest,
                            )
                        )
                        for relative, digest in saved["artifact_sha256"].items()
                        if relative.startswith(record["id"] + "/")
                    ]
                    return dict(record=record, paths=media, evidence=ref)
        raise KeyError("No audited initial approach for " + case_id)

    def playing_complete_trajectory(self, case_id: str):
        """Join recorded seed approach and passage; no resting-hand claim."""
        musical = self.playing_trajectory(case_id)
        connection = self.playing_initial_approach(case_id)
        details = connection["record"]["details"]
        if (
            details["status"] != "sampled_path_found"
            or details.get("independent_approach_audit", {}).get("status")
            != "sampled_proxy_constraints_satisfied"
            or not details.get("exact_original_first_pose_reached")
        ):
            raise ValueError("Initial approach is incomplete or independently rejected")
        approach = details["approach_strategy"]
        validate_strategy(details["approach_graph"], approach)
        if approach["samples"][-1]["qpos_rad"] != musical["samples"][0]["qpos_rad"]:
            raise ValueError("Initial approach does not join exact first musical state")
        samples = approach["samples"][:-1] + musical["samples"]
        return dict(
            status="sampled_geometry_from_resolved_numerical_seed",
            samples=samples,
            state_sequence_sha256=state_digest(samples),
            approach_sample_count=len(approach["samples"]),
            musical_strategy=musical,
            approach_evidence=connection["evidence"],
            claim=(
                "Actual exact-state join; no resting hand, timing, "
                "actuation or anatomical certification"
            ),
        )

    def playing_reviews(self):
        """Failed held contacts / separate approach attempts never become passages."""
        return [
            json.loads(self.evidence_path(ref).read_text())
            for ref in self.playing_record()["reviews"]
        ]

    def playing_comparisons(self):
        return [
            comparison
            for ref in self.playing_record()["studies"]
            for comparison in json.loads(self.evidence_path(ref).read_text())[
                "comparisons"
            ]
        ]

    def posture_record(self):
        """Hash-bound v2 sidecar; historical catalog and v1 API remain available."""
        index = json.loads(
            (self.root / "targets/posture-assessments-v2.json").read_text()
        )
        record = json.loads(self.evidence_path(index["evidence"]).read_text())
        self.evidence_path(
            dict(path="targets/manifest.json", sha256=record["catalog_sha256"])
        )
        if index["version"] != record["assessment_version"]:
            raise ValueError("Posture assessment version differs from its index")
        return record

    def posture_assessment(self, target_id: str):
        self.target(target_id)
        record = self.posture_record()
        target = next(t for t in record["targets"] if t["target_id"] == target_id)
        return dict(assessment_version=record["assessment_version"], **target)

    def posture_evidence(self, role: str):
        record = self.posture_record()
        ref = next((r for r in record["evidence"] if r["role"] == role), None)
        if ref is None:
            raise KeyError(role)
        return self.evidence_path(ref)

    def posture_case(self, case_id: str):
        record = self.posture_record()
        binding = next(
            (
                c
                for t in record["targets"]
                for c in t["cases"]
                if c["case_id"] == case_id
            ),
            None,
        )
        if binding is None:
            raise KeyError(case_id)
        source = json.loads(self.posture_evidence(binding["evidence_role"]).read_text())
        case = next(c for c in source["cases"] if c["id"] == case_id)
        if case["state_sequence_sha256"] != binding["state_sequence_sha256"]:
            raise ValueError("Posture assessment state identity differs")
        return case

    def posture_trajectory(self, case_id: str):
        case = self.posture_case(case_id)
        if case["strategy_id"] is None:
            raise KeyError("No complete movement: " + case_id)
        reference = case["source"]
        # Search references resolve relative to the originating definition.
        # All definitions are direct children of experiments/<milestone>.
        record = self.posture_record()
        binding = next(
            c for t in record["targets"] for c in t["cases"] if c["case_id"] == case_id
        )
        path = (
            self.posture_evidence(binding["evidence_role"]).parent.parent
            / reference["search_result"]
        )
        ref = dict(
            path=str(path.resolve().relative_to(self.root)),
            sha256=reference["search_sha256"],
        )
        saved = json.loads(self.evidence_path(ref).read_text())
        strategy = next(
            s for s in saved["strategies"] if s["id"] == case["strategy_id"]
        )
        validate_strategy(saved, strategy)
        if state_digest(strategy["samples"]) != case["state_sequence_sha256"]:
            raise ValueError("Posture trajectory differs from assessed states")
        return dict(
            joint_names=saved["joint_names"],
            first_note_approach="not_planned",
            **strategy,
        )

    def posture_media(self, case_id: str):
        case = self.posture_case(case_id)
        record = self.posture_record()
        binding = next(
            c for t in record["targets"] for c in t["cases"] if c["case_id"] == case_id
        )
        path = self.posture_evidence(binding["evidence_role"])
        source = json.loads(path.read_text())
        prefix = str(path.parent.relative_to(self.root))
        media = []
        for relative, sha in source["artifact_sha256"].items():
            if relative.startswith(case_id + "/"):
                media.append(
                    self.evidence_path(dict(path=prefix + "/" + relative, sha256=sha))
                )
        return dict(
            paths=media,
            static_states=case["media"],
            animation=case.get("animation"),
            missing=[]
            if case["media"]
            else ["new physical rendering unavailable for this case"],
            first_note_approach="not_planned",
        )

    def posture_comparisons(self, target_id: str):
        cases = self.posture_assessment(target_id)["cases"]
        references = {
            role: json.loads(self.posture_evidence(role).read_text())
            for role in {c["evidence_role"] for c in cases}
        }
        wanted = {c["case_id"] for c in cases}
        trials = {
            c["source"]["id"]
            for record in references.values()
            for c in record["cases"]
            if c["id"] in wanted
        }
        selected = json.loads(self.posture_evidence("selection").read_text())
        return [r for r in selected["rankings"] if r["trial_id"] in trials]

    def quality_record(self, version: str = "biomechanics-v1"):
        """Load a hash-bound sidecar without changing historical target identities."""
        index = json.loads((self.root / "targets/assessments-v1.json").read_text())
        if index["version"] != version:
            raise KeyError("Unknown assessment version")
        record = json.loads(self.evidence_path(index["evidence"]).read_text())
        self.evidence_path(
            {
                "path": "targets/manifest.json",
                "sha256": record["input"]["catalog_sha256"],
            }
        )
        return record

    def assessment(self, target_id: str, version: str = "biomechanics-v1"):
        self.target(target_id)
        record = self.quality_record(version)
        target = next(t for t in record["targets"] if t["target_id"] == target_id)
        return {"assessment_version": record["assessment_version"], **target}

    def quality_evidence(self, role: str):
        if role == "assessment":
            index = json.loads((self.root / "targets/assessments-v1.json").read_text())
            return self.evidence_path(index["evidence"])
        record = self.quality_record()
        ref = next((r for r in record["evidence"] if r["role"] == role), None)
        if ref is None:
            raise KeyError(role)
        return self.evidence_path(ref)

    def comparison_trials(self, target_id: str):
        self.target(target_id)
        return [
            t
            for t in self.quality_record()["comparison_trials"]
            if t["target_id"] == target_id
        ]

    def comparison_trajectory(self, trial_id: str, strategy_id: str = "strategy-0"):
        trial = next(
            (
                t
                for t in self.quality_record()["comparison_trials"]
                if t["id"] == trial_id
            ),
            None,
        )
        if trial is None:
            raise KeyError(trial_id)
        saved = json.loads(self.evidence_path(trial["search_evidence"]).read_text())
        strategy = next(
            (s for s in saved["strategies"] if s["id"] == strategy_id), None
        )
        if strategy is None:
            raise KeyError("No complete movement: " + strategy_id)
        validate_strategy(saved, strategy)
        return {
            "joint_names": saved["joint_names"],
            "first_note_approach": "not_planned",
            **strategy,
        }

    def ranked_comparisons(self, target_id: str, *, policy: str = "proxy_first"):
        """Whole-path ranking; preserve wrist/proxy tradeoffs and source trial IDs."""
        from .selection import audited_strategy_order

        trials = {t["id"] for t in self.comparison_trials(target_id)}
        comparison = json.loads(self.quality_evidence("comparison").read_text())
        return [
            {
                "trial_id": t["source"]["id"],
                "ranking": audited_strategy_order(t["strategies"], policy),
            }
            for t in comparison["trials"]
            if t["source"]["id"] in trials
        ]

    def muscle_screens(self, target_id: str):
        """Exact conditional estimates; empty means unassessed, not a capacity pass."""
        cases = {b["case_id"] for b in self.assessment(target_id)["benchmarks"]}
        record = json.loads(self.quality_evidence("muscle").read_text())
        return [
            {
                "case_id": p["pose"]["case_id"],
                "pose": p["pose"],
                "length_derivative_check": p["length_derivative_check"],
                "native_parity": p["native_parity"],
                "static_screens": p["static_screens"],
            }
            for p in record["poses"]
            if p["pose"].get("case_id") in cases
        ]

    def quality_media(self, target_id: str):
        self.target(target_id)
        record = self.quality_record()
        files = [
            self.evidence_path(ref)
            for example in record["visual_examples"]
            if example["target_id"] == target_id
            for ref in example["files"]
        ]
        directory = self.quality_evidence("assessment").parent.relative_to(self.root)
        for gallery in record["comparison_frame_sources"]:
            if gallery["target_id"] == target_id:
                name = gallery["id"] + ".png"
                files.append(
                    self.evidence_path(
                        {
                            "path": str(directory / name),
                            "sha256": record["artifact_sha256"][name],
                        }
                    )
                )
        return files

    def comparison_frame_sequence(self, trial_id: str, strategy_id: str = "strategy-0"):
        record = self.quality_record()
        reference = next(
            (r for r in record["comparison_media"] if r["trial_id"] == trial_id), None
        )
        if reference is None:
            raise KeyError("No saved comparison media: " + trial_id)
        media = json.loads(self.evidence_path(reference).read_text())
        strategy = self.comparison_trajectory(trial_id, strategy_id)
        report = next(
            (r for r in media["strategy_reports"] if r["strategy_id"] == strategy_id),
            None,
        )
        if report is None:
            raise KeyError("No saved frames for strategy: " + strategy_id)
        animation = report["animation"]
        if not animation or animation["state_sequence_sha256"] != state_digest(
            strategy["samples"]
        ):
            raise ValueError("Missing or different movement evidence")
        frames = []
        for frame in animation["frames"]:
            sample = strategy["samples"][frame["sample_index"]]
            if any(
                frame[k] != sample[k] for k in ("qpos_rad", "active_contacts", "roles")
            ):
                raise ValueError("Frame differs from its actual sample")
            path = Path(reference["path"]).parent / strategy_id / frame["frame"]
            frames.append(
                {
                    **frame,
                    "path": self.evidence_path(
                        {"path": str(path), "sha256": frame["frame_sha256"]}
                    ),
                }
            )
        return frames

    def reproduce_quality_argv(self, role: str, output: Path):
        """Archived-code replay arguments for a quality experiment or media trial."""
        record = self.quality_record()
        refs = (
            record["evidence"]
            + record["comparison_media"]
            + [
                {
                    "role": "assessment",
                    "path": str(
                        self.quality_evidence("assessment").relative_to(self.root)
                    ),
                    "sha256": hashlib.sha256(
                        self.quality_evidence("assessment").read_bytes()
                    ).hexdigest(),
                }
            ]
        )
        reference = next(
            (r for r in refs if r.get("role") == role or r.get("trial_id") == role),
            None,
        )
        if reference is None:
            raise KeyError(role)
        result = self.evidence_path(reference)
        from .verification import verify_record

        verified = verify_record(result.parent)
        if verified.status != "verified":
            raise ValueError("Incomplete replay provenance")
        execution = json.loads((result.parent / "execution.json").read_text())
        definition = (result.parent / execution["definition_reference"]).resolve()
        return [
            "uv",
            "run",
            "aec",
            "frozen",
            execution["workflow"],
            str(definition),
            "--source-snapshot",
            str(result.parent / "source-snapshot.zip"),
            "--output",
            str(output.resolve()),
        ]

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
    final_selection_policy: str | None = None,
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
    if final_selection_policy is not None and final_selection_policy not in (
        "palm",
        "movement",
        "posture",
        "whole_hand",
    ):
        raise ValueError("Unknown full-path selection policy")
    saved = search_passage(passage, reference or reference_experiment(root), settings)
    saved["scene_input"] = saved.pop("input")
    e = Experiment.from_dict(saved["scene_input"])
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != saved["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Independent audit model differs from numerical search")
    from .strategy_audit import audit_states

    audits = []
    whole_hand_audits = []
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
        whole_hand_audits.append(
            audit_states(
                scene,
                e.geometry,
                states,
                saved["joint_names"],
                connected=strategy["status"] == "sampled_connected_path",
            )
        )
    from .selection import posture_strategy_order

    complete = [
        dict(
            id=strategy["id"],
            status=strategy["status"],
            whole_hand=hand,
            independent_audit=audit,
            wrist=hand["wrist"],
        )
        for strategy, hand, audit in zip(
            saved["strategies"], whole_hand_audits, audits, strict=True
        )
        if strategy["status"] == "sampled_connected_path"
    ]
    saved["posture_policy_rankings"] = {
        policy: posture_strategy_order(complete, policy)
        for policy in ("palm", "movement", "posture", "whole_hand")
    }
    if final_selection_policy is not None:
        if final_selection_policy not in saved["posture_policy_rankings"]:
            raise ValueError("Unknown full-path selection policy")
        saved["final_selection"] = dict(
            policy=final_selection_policy,
            preferred_strategy_id=next(
                (
                    r["id"]
                    for r in saved["posture_policy_rankings"][final_selection_policy]
                    if r.get("status") != "rejected_configured_sample_checks"
                ),
                None,
            ),
            retained_alternatives=saved["posture_policy_rankings"][
                final_selection_policy
            ],
            scope=(
                "Second stage audits every complete beam survivor; "
                "pruned branches not re-solved"
            ),
        )
    saved["whole_hand_strategy_audits"] = whole_hand_audits
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


def measure_playing_strategy(
    saved: dict[str, Any], strategy_id: str, *, lifecycle: bool = True
):
    """Compute landmarks/lifecycle for a consumer's actual search result."""
    from .experiment import Experiment
    from .playing_region import playing_region_trace
    from .provenance import compiled_model_digest
    from .scene import build_scene

    strategy = next(s for s in saved["strategies"] if s["id"] == strategy_id)
    validate_strategy(saved, strategy)
    e = Experiment.from_dict(saved.get("scene_input", saved["input"]))
    scene = build_scene(e.geometry, e.player, e.setup, e.physical_contact, DIGITS)
    if (
        compiled_model_digest(scene.model)
        != saved["provenance"]["compiled_model_sha256"]
    ):
        raise ValueError("Consumer model differs from recorded trajectory")
    return playing_region_trace(scene, e, strategy, lifecycle=lifecycle)
