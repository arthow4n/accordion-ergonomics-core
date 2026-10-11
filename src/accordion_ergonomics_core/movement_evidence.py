"""Pure recorded-movement identity and sampling guards; never generate states."""

import hashlib
import json
from typing import Any

import numpy as np


def state_digest(samples: list[dict[str, Any]]) -> str:
    return hashlib.sha256(
        json.dumps(
            [s["qpos_rad"] for s in samples], separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def validate_strategy(saved: dict[str, Any], strategy: dict[str, Any]) -> None:
    """Reject missing edges, hidden discontinuities and substituted state arrays."""
    if strategy["status"] != "sampled_connected_path" or not strategy.get("samples"):
        raise ValueError(
            "Animation requires a successful recorded movement, not solver history"
        )
    if (
        len(strategy["events"]) < 2
        or len(strategy["edge_ids"]) != len(strategy["events"]) - 1
    ):
        raise ValueError("Missing movement evidence between musical events")
    nodes = {n["id"]: n for n in saved["nodes"]}
    edges = {e["id"]: e for e in saved["edges"]}
    joined = []
    for edge_id, source_id, dest_id in zip(
        strategy["edge_ids"],
        strategy["node_ids"][:-1],
        strategy["node_ids"][1:],
        strict=True,
    ):
        edge = edges[edge_id]
        part = edge["path"].get("samples", [])
        if edge["status"] != "sampled_path_found" or not part:
            raise ValueError(
                "Failed or empty interval cannot become an accepted animation"
            )
        if edge["source"] != source_id or edge["destination"] != dest_id:
            raise ValueError("Edge does not belong to the selected node chain")
        if (
            part[0]["qpos_rad"] != nodes[source_id]["qpos_rad"]
            or part[-1]["qpos_rad"] != nodes[dest_id]["qpos_rad"]
        ):
            raise ValueError(
                "Movement interval endpoints differ from actual node states"
            )
        if joined and joined[-1]["qpos_rad"] != part[0]["qpos_rad"]:
            raise ValueError("Unrecorded jump between movement intervals")
        joined.extend(part if not joined else part[1:])
    if state_digest(joined) != state_digest(strategy["samples"]):
        raise ValueError("Animation states differ from the recorded movement edges")
    if not all(s["sample_valid"] for s in strategy["samples"]):
        raise ValueError(
            "Rejected sampled states cannot be silently animated as accepted"
        )
    for event, node_id in zip(strategy["events"], strategy["node_ids"], strict=True):
        if (
            event["qpos_rad"] != nodes[node_id]["qpos_rad"]
            or event["contacts"] != nodes[node_id]["contacts"]
        ):
            raise ValueError(
                "Musical event differs from its recorded physical realization"
            )


def trajectory_frame_indices(strategy: dict[str, Any], frame_count: int) -> list[int]:
    if type(frame_count) is not int or frame_count < 2:
        raise ValueError("A sampled animation needs at least two frames")
    samples = strategy.get("samples", [])
    if not samples or strategy.get("status") != "sampled_connected_path":
        raise ValueError("Missing successful sampled movement evidence")
    boundaries = {i for i, s in enumerate(samples) if s.get("event_index") is not None}
    represented = {samples[i]["event_index"] for i in boundaries}
    if represented != set(range(len(strategy["events"]))):
        raise ValueError("Trajectory omits an actual musical event boundary")
    required = boundaries | {0, len(samples) - 1}
    if len(required) > frame_count:
        raise ValueError("Frame budget cannot show every recorded event boundary")
    indices = required | set(
        np.linspace(0, len(samples) - 1, frame_count).round().astype(int).tolist()
    )
    while len(indices) > frame_count:
        removable = sorted(indices - required)
        # Remove the least isolated optional sample; no new state is generated.
        victim = min(
            removable, key=lambda i: min(abs(i - j) for j in indices if j != i)
        )
        indices.remove(victim)
    return sorted(indices)
