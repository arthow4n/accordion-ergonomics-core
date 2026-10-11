"""Versioned exercise catalog derived from exact-world frozen evidence.

A target is musical intent; a realization is a finite named-contact strategy.
Branches belong to a realization. Integrity and model audit status are separate
from human feasibility, which this program cannot determine.
"""

import hashlib
import json
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from .instrument import buttons
from .verification import verify_record

SCHEMA_VERSION = 1
ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path("targets/manifest.json")
BUTTONS = {b.id: b for b in buttons()}
STATUSES = {
    "hypothesis",
    "contact_candidates_found",
    "sampled_path_found",
    "not_found_with_current_search",
    "collision_policy_rejected",
}


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, allow_nan=False, separators=(",", ":")
        ).encode()
    ).hexdigest()


def note_name(midi: int) -> str:
    return ("C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B")[
        midi % 12
    ] + str(midi // 12 - 1)


def read(root: Path, relative: str) -> dict[str, Any]:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Evidence must remain in the repository")
    return json.loads(path.read_text())


def reference_world(saved: dict[str, Any]) -> dict[str, Any]:
    profiles = saved["resolved_profiles"]
    return {
        "id": "compact-upper-native-v3",
        "geometry_model": profiles["instrument"]["geometry_model"],
        "anatomy_model": profiles["player"]["model"],
        "instrument_sha256": digest(profiles["instrument"]),
        "player_sha256": digest(profiles["player"]),
        "wearing_setup_sha256": digest(profiles["setup"]),
        "contact_policy_sha256": digest(profiles["contact"]),
        "solver_collision_implementation": profiles["solver"][
            "collision_limit_implementation"
        ],
        "anatomy_source_sha256": saved["provenance"]["anatomy_source_sha256"],
        "compiled_model_sha256": saved["provenance"]["compiled_model_sha256"],
        "audit_policy": "037-independent-cross-digit-report",
    }


def evidence_ref(root: Path, relative: str, role: str) -> dict[str, str]:
    path = root / relative
    parent = path.parent
    while parent != root and not (parent / "execution.json").is_file():
        parent = parent.parent
    if parent == root:
        raise ValueError(f"No frozen root for {relative}")
    return {
        "path": relative,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "role": role,
        "frozen_root": str(parent.relative_to(root)),
    }


def events_with_notes(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for event in events:
        contacts = []
        for c in event["contacts"]:
            if c["finger"] not in ("index", "middle"):
                raise ValueError("Only index and middle contacts are supported")
            button = BUTTONS[c["button_id"]]
            contacts.append({**c, "midi": button.midi, "note": note_name(button.midi)})
        result.append({**event, "contacts": contacts})
    return result


def contact_signature(contacts: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(c["button_id"], c["finger"]) for c in contacts}


def check_world(saved: dict[str, Any], world: dict[str, Any]) -> None:
    actual = reference_world(saved)
    for key in actual:
        if (
            key not in ("audit_policy", "id", "compiled_model_sha256")
            and actual[key] != world[key]
        ):
            raise ValueError(f"Reference world differs: {key}")
    if actual["compiled_model_sha256"] not in world["compiled_model_variants"].values():
        raise ValueError("Unregistered compiled model variant")


def pose_branch(
    saved: dict[str, Any], physical: dict[str, Any], ref: dict[str, str]
) -> dict[str, Any]:
    return {
        "id": "branch-"
        + digest(
            {
                "world": saved["provenance"]["compiled_model_sha256"],
                "joints": saved["joint_names"],
                "qpos": saved["qpos_rad"],
            }
        )[:20],
        "status": saved["status"],
        "evidence": ref,
        "position_error_m": saved["diagnostics"]["position_error_m"],
        "descriptors": physical,
    }


def path_descriptors(
    record: dict[str, Any], samples: list[dict[str, Any]], names: list[str]
) -> dict[str, Any]:
    angles = np.asarray([s["qpos_rad"] for s in samples])
    groups = {
        "wrist": ["deviation_r", "flexion_r"],
        "forearm": ["pro_sup_r"],
        "shoulder": ["elv_angle_r", "shoulder_elv_r", "shoulder_rot_r"],
        "index": [
            "mcp2_flexion_r",
            "mcp2_abduction_r",
            "pm2_flexion_r",
            "md2_flexion_r",
        ],
        "middle": [
            "mcp3_flexion_r",
            "mcp3_abduction_r",
            "pm3_flexion_r",
            "md3_flexion",
        ],
    }
    return {
        "palm_path_length_m": record.get("palm_path_length_m"),
        "palm_max_excursion_m": record.get("palm_max_excursion_m"),
        "minimum_joint_margin_rad": record.get("minimum_joint_margin_rad"),
        "maximum_registered_penetration_m": record.get("maximum_penetration_m"),
        "sample_count": len(samples),
        "joint_excursion_rad": {
            group: {n: float(np.ptp(angles[:, names.index(n)])) for n in joints}
            for group, joints in groups.items()
        }
        if len(samples)
        else {},
        "maximum_held_position_error_m": record.get("maximum_held_position_error_m"),
        "continuous_validity": None,
    }


def build_realization(
    root: Path, spec: dict[str, Any], world: dict[str, Any]
) -> dict[str, Any]:
    events = events_with_notes(spec["events"])
    realization = {
        "id": "realization-" + digest({"world": world["id"], "events": events})[:20],
        "events": events,
        "status": "hypothesis",
        "branches": [],
        "searches": [],
        "evidence": [],
        "descriptors": {},
        "validity": {
            "quality": "generated_hypothesis",
            "human_feasibility": None,
            "anatomical_validation": "unresolved",
            "independent_audit": "not_evaluated",
            "coverage_limitations": [
                "Rigid proxies lack measured tissue calibration",
                "No human observation, forces, depression, fatigue or tempo",
            ],
        },
    }
    for source in spec.get("sources", []):
        record = read(root, source["path"])
        kind = source["kind"]
        ref = evidence_ref(root, source["path"], kind)
        realization["evidence"].append(ref)
        if kind == "discovery":
            target = next(
                t for t in record["targets"] if t["target_id"] == source["target_id"]
            )
            check_world(target, world)
            failures = Counter(
                a["status"] for a in target["attempts"] if a["status"] != "success"
            )
            realization["searches"].append(
                {
                    "evidence": ref,
                    "selector": source["target_id"],
                    "settings": target["settings"],
                    "attempt_count": len(target["attempts"]),
                    "successful_attempts": sum(
                        a["status"] == "success" for a in target["attempts"]
                    ),
                    "failure_counts": dict(failures),
                    "failure_reasons": dict(
                        Counter(
                            str(
                                a.get("failure")
                                or a.get("reason")
                                or a.get("termination_reason")
                                or a["status"]
                            )
                            for a in target["attempts"]
                            if a["status"] != "success"
                        )
                    ),
                    "distinct_candidates": len(target["candidates"]),
                    "seed_semantics": (
                        "Explicit deterministic offsets; no stochastic seed"
                    ),
                    "elapsed_s": target["elapsed_s"],
                }
            )
            for i, candidate in enumerate(target["candidates"]):
                if contact_signature(
                    candidate["state"]["contacts"]
                ) != contact_signature(events[0]["contacts"]):
                    raise ValueError("Discovery contacts differ from realization")
                path = str(
                    Path(source["path"]).parent
                    / source["target_id"]
                    / f"candidate-{i}"
                    / "result.json"
                )
                saved = read(root, path)
                check_world(saved, world)
                branch_ref = evidence_ref(root, path, "candidate_pose")
                realization["evidence"].append(branch_ref)
                branch = pose_branch(saved, candidate["descriptors"], branch_ref)
                if branch["id"] not in {b["id"] for b in realization["branches"]}:
                    realization["branches"].append(branch)
            realization["status"] = (
                "contact_candidates_found"
                if realization["branches"]
                else "not_found_with_current_search"
            )
        elif kind in ("path", "held"):
            check_world(record, world)
            audit = record if kind == "path" else record["searched_audit"]
            samples = audit.get("samples", [])
            if kind == "path":
                endpoints = record["endpoints"]
            else:
                endpoints = [
                    read(
                        root,
                        str(
                            Path(source["path"]).parent
                            / record["input"][key + "_result"]
                        ),
                    )
                    for key in ("start", "end")
                ]
            for event, endpoint in zip((events[0], events[-1]), endpoints, strict=True):
                if contact_signature(event["contacts"]) != contact_signature(
                    endpoint["targets"]
                ):
                    raise ValueError("Path endpoint contacts differ from realization")
                check_world(endpoint, world)
            found = record["status"] in (
                "sampled_path_found",
                "sampled_held_path_found",
            )
            if found and not audit.get("sampled_constraints_satisfied"):
                raise ValueError("Successful path lacks sampled constraint acceptance")
            if kind == "held" and found and not audit.get("held_geometry_satisfied"):
                raise ValueError("Held path lacks held geometry acceptance")
            realization["status"] = (
                "sampled_path_found" if found else "not_found_with_current_search"
            )
            realization["searches"].append(
                {
                    "evidence": ref,
                    "status": record["status"],
                    "settings": record.get("settings", record["input"]),
                    "failure": record.get("failure"),
                    "method": record.get("method", "held-waypoint-continuation"),
                }
            )
            realization["descriptors"] = path_descriptors(
                audit, samples, endpoints[0]["joint_names"]
            )
        else:
            raise ValueError("Unknown evidence kind")
    if realization["status"] in ("contact_candidates_found", "sampled_path_found"):
        realization["validity"]["quality"] = "numerically_realized"
    if spec.get("endpoint_coverage"):
        realization["evidence"].append(
            evidence_ref(
                root, spec["endpoint_coverage"], "independent_endpoint_coverage"
            )
        )
        realization["validity"]["independent_audit"] = (
            "endpoints_only_anatomy_unresolved"
        )
    if realization["branches"]:
        palms = np.asarray(
            [b["descriptors"]["palm_position_world_m"] for b in realization["branches"]]
        )
        realization["descriptors"]["candidate_palm_diameter_m"] = float(
            np.max(np.linalg.norm(palms[:, None] - palms[None, :], axis=2))
        )
    return realization


def build_catalog(root: Path = ROOT) -> dict[str, Any]:
    definition = read(root, "targets/definitions.json")
    world = reference_world(read(root, definition["reference_result"]))
    world["compiled_model_variants"] = {
        name: read(root, path)["provenance"]["compiled_model_sha256"]
        for name, path in definition["model_references"].items()
    }
    targets = []
    for spec in definition["targets"]:
        realizations = [build_realization(root, r, world) for r in spec["realizations"]]
        musical = [
            [c["midi"] for c in e["contacts"]] for e in realizations[0]["events"]
        ]
        if any(
            [[c["midi"] for c in e["contacts"]] for e in r["events"]] != musical
            for r in realizations
        ):
            raise ValueError("Physical alternatives must preserve musical intent")
        targets.append(
            {
                "id": spec["id"],
                "family": spec["family"],
                "explanation": spec["explanation"],
                "musical_intent": {"event_pitches_midi": musical, "timing": None},
                "reference_world": world["id"],
                "realizations": realizations,
                "human_feasibility": None,
            }
        )
    catalog = {
        "schema_version": SCHEMA_VERSION,
        "release": definition["release"],
        "reference_world": world,
        "targets": targets,
        "descriptor_definitions": {
            "palm_path_length_m": (
                "Sum of Euclidean palm "
                "displacement between saved samples; no proven "
                "minimum"
            ),
            "candidate_palm_diameter_m": (
                "Largest endpoint palm separation among discovered branches"
            ),
            "joint_excursion_rad": (
                "Max minus min coordinate over saved path samples, grouped by anatomy"
            ),
            "minimum_joint_margin_rad": (
                "Minimum distance to imported coordinate bound; not comfort"
            ),
            "maximum_registered_penetration_m": (
                "Configured engine/pair penetration; incomplete anatomical coverage"
            ),
        },
        "interpretation": (
            "Finite-search model "
            "realizations, not human-validated exercises or "
            "intrinsic difficulty rankings"
        ),
    }
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, Any]) -> None:
    if catalog["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported catalog schema")
    ids = [t["id"] for t in catalog["targets"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate target identity")
    for target in catalog["targets"]:
        if target["human_feasibility"] is not None:
            raise ValueError("This library has no human validation")
        ids = [r["id"] for r in target["realizations"]]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate physical realization")
        for r in target["realizations"]:
            if r["status"] not in STATUSES:
                raise ValueError("Unknown search status")
            events_with_notes(r["events"])
            if (
                r["status"] not in ("hypothesis", "not_found_with_current_search")
                and not r["evidence"]
            ):
                raise ValueError("Realized entry lacks actual evidence")
            if r["validity"]["human_feasibility"] is not None:
                raise ValueError("No human feasibility evidence")


def markdown(catalog: dict[str, Any]) -> str:
    lines = [
        "# Right-hand exercise target catalog",
        "",
        (
            f"Release {catalog['release']}. "
            f"{len(catalog['targets'])} musical targets in the "
            f"fixed compact-upper native v3 world."
        ),
        "",
        (
            "**Provisional model challenges. Human feasibility "
            "is unknown for every entry.**"
        ),
        "",
        (
            "Index/middle contacts only. Torso, legs, left "
            "arm, treble/bass cases and closed bellows remain "
            "fixed. No tempo, force or button depression is "
            "inferred."
        ),
        "",
        (
            "Use `uv run aec targets list --family held`, `uv "
            "run aec targets show TARGET_ID`, and `uv run aec "
            "targets verify TARGET_ID`. Verification checks "
            "commitments, not scientific validity."
        ),
        "",
        "| Target | Family | Notes | Search status | Audit |",
        "|---|---|---|---|---|",
    ]
    for t in catalog["targets"]:
        notes = " → ".join(
            "+".join(note_name(n) for n in event)
            for event in t["musical_intent"]["event_pitches_midi"]
        )
        lines.append(
            f"| [{t['id']}](#{t['id']}) | {t['family']} | "
            f"{notes} | "
            f"{', '.join(sorted({r['status'] for r in t['realizations']}))} "
            f"| unresolved anatomy |"
        )
    for t in catalog["targets"]:
        lines += ["", f"## {t['id']}", "", t["explanation"], ""]
        for r in t["realizations"]:
            events = " → ".join(
                ", ".join(
                    (
                        f"{c['finger']} {c['button_id']} ({c['note']}; "
                        f"{c.get('behavior', 'contact')})"
                    )
                    for c in e["contacts"]
                )
                for e in r["events"]
            )
            lines += [
                f"- `{r['id']}`: {events}.",
                (
                    f"  Status: {r['status']}; quality: "
                    f"{r['validity']['quality']}; audit: "
                    f"{r['validity']['independent_audit']}; anatomy "
                    f"unresolved."
                ),
            ]
            for search in r["searches"]:
                if "attempt_count" in search:
                    lines.append(
                        f"  Search: "
                        f"{search['successful_attempts']}/{search['attempt_count']} "
                        f"accepted starts, {search['distinct_candidates']} "
                        f"distinct candidates; failures "
                        f"{search['failure_counts']}."
                    )
            if r["descriptors"]:
                lines.append(
                    "  Descriptors: `"
                    + json.dumps(r["descriptors"], sort_keys=True)
                    + "`."
                )
            for ref in r["evidence"]:
                if ref["role"] != "candidate_pose":
                    lines.append(
                        f"  Evidence: "
                        f"[{ref['role']}]({Path('..') / ref['path']}) "
                        f"(SHA256 `{ref['sha256']}`)."
                    )
    lines += [
        "",
        (
            "Solver history is not a playing trajectory. A "
            "found path establishes one sampled model "
            "realization; a finite failure is not "
            "impossibility. Rigid proxy overlap does not "
            "measure tissue penetration. No result establishes "
            "a human movement minimum or universal difficulty."
        ),
        "",
    ]
    return "\n".join(lines)


def verify_target(
    catalog: dict[str, Any], root: Path, target_id: str | None = None
) -> dict[str, Any]:
    validate_catalog(catalog)
    targets = [
        t for t in catalog["targets"] if target_id is None or t["id"] == target_id
    ]
    if not targets:
        raise ValueError("Unknown target ID")
    checked = set()
    roots = set()
    for target in targets:
        for r in target["realizations"]:
            for ref in r["evidence"]:
                path = root / ref["path"]
                if hashlib.sha256(path.read_bytes()).hexdigest() != ref["sha256"]:
                    raise ValueError(f"Evidence changed: {ref['path']}")
                checked.add(ref["path"])
                roots.add(ref["frozen_root"])
    results = [verify_record(root / p) for p in sorted(roots)]
    if any(r.status != "verified" for r in results):
        raise ValueError(
            str(
                [
                    (r.directory, r.status, r.issues, r.limitations)
                    for r in results
                    if r.status != "verified"
                ]
            )
        )
    # Rebuild enforces world identities, mappings, statuses and endpoint requirements.
    rebuilt = build_catalog(root)
    selected = {t["id"] for t in targets}
    if [t for t in rebuilt["targets"] if t["id"] in selected] != targets:
        raise ValueError(
            "Catalog differs from definitions/evidence; rebuild explicitly"
        )
    return {
        "status": "integrity_verified",
        "targets": len(targets),
        "evidence_files": len(checked),
        "frozen_roots": len(roots),
        "scientific_validity": None,
        "human_feasibility": None,
    }


def targets_command(args: Namespace) -> None:
    if args.target_command == "build":
        catalog = build_catalog()
        (ROOT / CATALOG).write_text(
            json.dumps(catalog, indent=2, allow_nan=False) + "\n"
        )
        (ROOT / "targets/CATALOG.md").write_text(markdown(catalog))
        print(f"Built {len(catalog['targets'])} targets")
        return
    catalog = read(ROOT, str(CATALOG))
    if args.target_command == "verify":
        print(json.dumps(verify_target(catalog, ROOT, args.target_id), indent=2))
    elif args.target_command == "show":
        target = next(
            (t for t in catalog["targets"] if t["id"] == args.target_id), None
        )
        if target is None:
            raise ValueError("Unknown target ID")
        print(json.dumps(target, indent=2))
    else:
        for target in catalog["targets"]:
            statuses = {r["status"] for r in target["realizations"]}
            if args.family and args.family != target["family"]:
                continue
            if args.status and args.status not in statuses:
                continue
            notes = " -> ".join(
                "+".join(note_name(n) for n in e)
                for e in target["musical_intent"]["event_pitches_midi"]
            )
            print(
                f"{target['id']}\t{target['family']}\t{notes}\t{','.join(sorted(statuses))}"
            )
