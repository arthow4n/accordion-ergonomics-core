"""Read-only integrity checks across heterogeneous frozen research records."""

import hashlib
import json
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RecordVerification:
    directory: str
    status: str
    checks: tuple[str, ...]
    issues: tuple[str, ...]
    limitations: tuple[str, ...]


def verify_record(
    directory: Path, input_path: Path | None = None
) -> RecordVerification:
    """Verify recorded commitments, never current-source or physiological truth.

    Old records and renders can lack metadata; report partial verification.
    An archived package does not authenticate itself or prove numerical outcomes.
    """
    checks: list[str] = []
    issues: list[str] = []
    limitations = ["Integrity only; no numerical replay or physical validation"]

    def finish() -> RecordVerification:
        status = (
            "invalid" if issues else "partial" if len(limitations) > 1 else "verified"
        )
        return RecordVerification(
            str(directory), status, tuple(checks), tuple(issues), tuple(limitations)
        )

    def compare(actual: str, expected: str, label: str) -> None:
        if actual != expected:
            issues.append(label + " hash mismatch")
        else:
            checks.append(label)

    def file_hash(path: Path, expected: str, label: str) -> None:
        if not path.is_file():
            issues.append(label + " missing file: " + str(path))
        else:
            compare(hashlib.sha256(path.read_bytes()).hexdigest(), expected, label)

    def provenance(
        record: dict[str, Any], label: str, source_hash: str, lock_hash: str
    ) -> None:
        metadata = record.get("provenance", {})
        if "project_source_sha256" not in metadata:
            limitations.append(label + " lacks executed-source hash")
        else:
            compare(
                metadata["project_source_sha256"],
                source_hash,
                label + " executed source",
            )
        if "lock_sha256" in metadata:
            compare(metadata["lock_sha256"], lock_hash, label + " recorded lock")
        else:
            limitations.append(label + " lacks recorded-lock hash")
        if "profiles_sha256" in record and "resolved_profiles" in record:
            raw = json.dumps(
                record["resolved_profiles"], sort_keys=True, allow_nan=False
            ).encode()
            compare(
                hashlib.sha256(raw).hexdigest(),
                record["profiles_sha256"],
                label + " resolved profiles",
            )

    try:
        metadata_path = directory / "execution.json"
        if not metadata_path.is_file():
            limitations.append(
                "No frozen execution metadata; archive verification unavailable"
            )
            return finish()
        metadata = json.loads(metadata_path.read_text())
        archive_path = directory / metadata["source_snapshot"]
        file_hash(archive_path, metadata["source_snapshot_sha256"], "source archive")
        digest = hashlib.sha256()
        with zipfile.ZipFile(archive_path) as archive:
            if len(archive.namelist()) != len(set(archive.namelist())):
                issues.append("Duplicate archived source entries")
            for name in sorted(archive.namelist()):
                path = Path(name)
                if (
                    len(path.parts) != 2
                    or path.parts[0] != "accordion_ergonomics_core"
                    or path.suffix != ".py"
                ):
                    issues.append("Unexpected archived source entry: " + name)
                    continue
                digest.update(path.name.encode())
                digest.update(b"\0")
                digest.update(archive.read(name))
        source_hash = metadata["package_source_sha256"]
        compare(digest.hexdigest(), source_hash, "archived package source")
        lock_hash = metadata["lock_sha256"]
        result_path = directory / "result.json"
        if not result_path.is_file():
            limitations.append(
                "No numerical result.json; render-only output may be intentional"
            )
            return finish()
        result = json.loads(result_path.read_text())
        definition = input_path or directory / "experiment.json"
        input_hash = result.get("definition_sha256", result.get("input_sha256"))
        if input_hash and definition.is_file():
            file_hash(definition, input_hash, "recorded definition/input")
        else:
            limitations.append(
                "Raw input unavailable; provide --input to verify its exact bytes"
            )
        workflow = metadata["workflow"]
        records: list[tuple[str, dict[str, Any]]] = []
        atlases: list[tuple[Path, dict[str, Any]]] = []
        if workflow in ("experiment", "held", "exercise", "plan"):
            records.append(("result", result))
        elif workflow == "explore":
            records.extend(
                (t.get("target_id", t["button_id"]), t) for t in result["targets"]
            )
        elif workflow in ("limit-probe", "collision-coverage"):
            key = "poses" if workflow == "collision-coverage" else "cases"
            records.extend((f"{key}/{i}", r) for i, r in enumerate(result[key]))
        elif workflow == "cba-geometry":
            records.append(("geometry", result))
            if "artifact_sha256" not in result:
                limitations.append("Geometry record lacks artifact manifest")
            for relative, expected in result.get("artifact_sha256", {}).items():
                file_hash(directory / relative, expected, relative)
        elif workflow == "architecture":
            records.append(("architecture", result))
            if "artifact_sha256" not in result:
                limitations.append("Architecture record lacks artifact hash manifest")
            for relative, expected in result.get("artifact_sha256", {}).items():
                file_hash(directory / relative, expected, relative)
            for name, benchmark in result["benchmarks"].items():
                records.append((name + " benchmark", benchmark))
                for suffix in ("result.json", "playing/result.json"):
                    state_path = directory / name / suffix
                    state = json.loads(state_path.read_text())
                    records.append((name + "/" + suffix, state))
        elif workflow == "hand-audit":
            records.extend((r["id"], r) for r in result["records"])
            for request in result["input"]["records"]:
                file_hash(
                    definition.parent / request["result"],
                    request["sha256"],
                    request["id"] + " source",
                )
                if "model_result" in request:
                    file_hash(
                        definition.parent / request["model_result"],
                        request["model_sha256"],
                        request["id"] + " model source",
                    )
        elif workflow == "search-reliability":
            for relative, expected in result["artifact_sha256"].items():
                file_hash(directory / relative, expected, relative)
            for panel in result["panels"]:
                path = directory / panel["result"]
                file_hash(path, panel["sha256"], panel["id"] + " panel")
                saved_panel = json.loads(path.read_text())
                records.extend(
                    (panel["id"] + "/" + t["target_id"], t)
                    for t in saved_panel["targets"]
                )
            for panel in result["input"]["panels"]:
                for state in panel.get("warm_states", []):
                    file_hash(
                        definition.parent / state["result"],
                        state["sha256"],
                        panel["id"] + " warm source",
                    )
        elif workflow == "atlas":
            records.append(("anchor", result["anchor"]))
            atlases.append((directory, result))
        elif workflow == "sweep":
            for case in result["cases"]:
                path = directory / case["result"]
                file_hash(path, case["result_sha256"], case["case"]["id"] + " result")
                if path.is_file():
                    atlas = json.loads(path.read_text())
                    records.append(
                        (
                            case["case"]["id"] + " anchor",
                            atlas["anchor"],
                        )
                    )
                    atlases.append((path.parent, atlas))
        else:
            limitations.append("Workflow schema not supported: " + workflow)
        for label, record in records:
            provenance(record, label, source_hash, lock_hash)
        if "resulting_gesture_result" in result:
            file_hash(
                directory / result["resulting_gesture_result"],
                result["resulting_gesture_sha256"],
                "resulting gesture",
            )
        for parent, atlas in atlases:
            for action in atlas.get("actions", []):
                file_hash(
                    parent / action["evidence"],
                    action["evidence_sha256"],
                    atlas["id"] + "/" + action["button_id"],
                )
        if definition.is_file():
            source = result["input"]
            for key in ("baseline", "start", "end", "atlas", "reference"):
                if key == "reference" and "reference_input" in source:
                    file_hash(
                        definition.parent / source["reference_input"],
                        source["reference_sha256"],
                        "reference experiment",
                    )
                if key + "_result" in source and key + "_sha256" in source:
                    file_hash(
                        definition.parent / source[key + "_result"],
                        source[key + "_sha256"],
                        key + " referenced input",
                    )
            for pose in source.get("poses", []):
                file_hash(
                    definition.parent / pose["result"],
                    pose["sha256"],
                    pose["id"] + " referenced pose",
                )
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as error:
        issues.append(type(error).__name__ + ": " + str(error))
    return finish()


def verify_records(
    directories: list[Path], input_path: Path | None = None
) -> dict[str, Any]:
    if input_path is not None and len(directories) != 1:
        raise ValueError("--input is only unambiguous for one record directory")
    return {
        "records": [asdict(verify_record(p, input_path)) for p in directories],
        "claim": "File commitments and provenance links; not scientific validity",
    }
