"""Explicit research preferences and Pareto descriptors, not physiology scores."""

import numpy as np

from ._engine import mujoco
from .anatomy import digit_dofs
from .hand_audit import hand_pairs

TECHNIQUE_SOURCE = "https://playingchromaticaccordion.blogspot.com/2017/"
CRITERIA = (
    "palm_path_m",
    "wrist_variation_rad",
    "digit_variation_rad",
    "endpoint_proxy_penetration_m",
)


def technique_priority(hypothesis):
    """Optional 2/3/4 exploration preference; neither 1 nor 5 is prohibited."""
    return sum(c["finger"] in ("thumb", "little") for c in hypothesis["contacts"])


def branch_descriptors(scene, parent, qpos, edge, palm_cost):
    """Actual sampled excursions; endpoint-only proxy metric is labeled as such."""
    q = np.asarray([s["qpos_rad"] for s in edge["path"]["samples"]] if edge else [qpos])
    delta = np.abs(np.diff(q, axis=0)).sum(axis=0)
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    dofs = digit_dofs(scene.model)
    scene.data.qpos[:] = qpos
    mujoco.mj_forward(scene.model, scene.data)
    distances = [
        float(mujoco.mj_geomDistance(scene.model, scene.data, *p["geom_ids"], 1, None))
        for p in hand_pairs(scene)
        if p["classification"] == "cross_digit_phalangeal_unresolved"
    ]
    previous = parent.get("selection_descriptors", {})
    return {
        "palm_path_m": palm_cost,
        "wrist_variation_rad": previous.get("wrist_variation_rad", 0)
        + float(delta[[names.index("flexion_r"), names.index("deviation_r")]].sum()),
        "digit_variation_rad": previous.get("digit_variation_rad", 0)
        + float(delta[[i for indices in dofs.values() for i in indices]].sum()),
        "endpoint_proxy_penetration_m": max(
            previous.get("endpoint_proxy_penetration_m", 0), -min(distances), 0
        ),
        "minimum_sampled_joint_margin_rad": min(
            previous.get("minimum_sampled_joint_margin_rad", float("inf")),
            float(
                np.minimum(
                    q - scene.model.jnt_range[:, 0], scene.model.jnt_range[:, 1] - q
                ).min()
            ),
        ),
        "proxy_scope": "event endpoints only; full path audited separately",
        "initial_approach": "not_planned; initial solve displacement excluded",
    }


def pareto_order(nodes):
    """Nondominated layers, then declared wrist/proxy/digit/palm tie preference."""
    pending = list(nodes)
    ordered = []
    layer = 0
    while pending:
        frontier = []
        for node in pending:
            a = np.array([node["selection_descriptors"][k] for k in CRITERIA])
            dominated_by = []
            for other in pending:
                b = np.array([other["selection_descriptors"][k] for k in CRITERIA])
                if np.all(b <= a) and np.any(b < a):
                    dominated_by.append(other["id"])
            node["dominated_by_this_layer"] = dominated_by
            if not dominated_by:
                frontier.append(node)
        for node in frontier:
            node["pareto_layer"] = layer
        frontier.sort(
            key=lambda n: (
                n["selection_descriptors"]["wrist_variation_rad"],
                n["selection_descriptors"]["endpoint_proxy_penetration_m"],
                n["selection_descriptors"]["digit_variation_rad"],
                n["cost"],
                n["id"],
            )
        )
        ordered.extend(frontier)
        ids = {n["id"] for n in frontier}
        pending = [n for n in pending if n["id"] not in ids]
        layer += 1
    return ordered


def audited_strategy_order(strategies, policy="proxy_first"):
    """Rank complete independently audited paths, preserving every alternative.

    Proxy-first is an explicit research risk preference on uncalibrated envelopes,
    not an ordinary-playing certificate. Unlike online endpoint ranking, it sees
    the worst recorded intermediate state.
    """
    if policy not in ("proxy_first", "wrist_first"):
        raise ValueError("Unknown whole-path preference")
    nodes = []
    rejected = []
    for strategy in strategies:
        hand = strategy["whole_hand"]
        independent = strategy["independent_audit"]
        if (
            hand["sample_count"] < 2
            or strategy.get("status") != "sampled_connected_path"
            or hand["palm_path_m"] is None
            or hand["state_sequence_sha256"] != independent["state_sequence_sha256"]
            or hand["sample_count"] != independent["sample_count"]
        ):
            raise ValueError("Selection requires matching complete movement audits")
        if independent["status"] != "sampled_proxy_constraints_satisfied":
            rejected.append(
                {
                    "id": strategy["id"],
                    "status": "rejected_configured_proxy_checks",
                    "policy": policy,
                    "pareto_layer": None,
                }
            )
            continue
        digit_names = {n for d in hand["digits"].values() for n in d["joint_names"]}
        descriptors = {
            "palm_path_m": hand["palm_path_m"],
            "wrist_variation_rad": sum(
                hand["joint_descriptors"][n]["total_variation_rad"]
                for n in ("flexion_r", "deviation_r")
            ),
            "digit_variation_rad": sum(
                hand["joint_descriptors"][n]["total_variation_rad"] for n in digit_names
            ),
            "endpoint_proxy_penetration_m": max(
                0.0, -independent["worst_cross_digit"]["distance_m"]
            ),
        }
        nodes.append(
            dict(
                id=strategy["id"],
                cost=hand["palm_path_m"],
                selection_descriptors=descriptors,
                state_sequence_sha256=hand["state_sequence_sha256"],
            )
        )
    ordered = pareto_order(nodes)
    if policy == "proxy_first":
        ordered.sort(
            key=lambda n: (
                n["pareto_layer"],
                n["selection_descriptors"]["endpoint_proxy_penetration_m"],
                n["selection_descriptors"]["wrist_variation_rad"],
                n["selection_descriptors"]["digit_variation_rad"],
                n["cost"],
                n["id"],
            )
        )
    for node in ordered:
        # Rename the shared Pareto axis to its true whole-path scope.
        node["descriptors"] = node.pop("selection_descriptors")
        node["descriptors"]["sampled_proxy_penetration_m"] = node["descriptors"].pop(
            "endpoint_proxy_penetration_m"
        )
        node["policy"] = policy
        node["claim"] = (
            "Bounded alternatives; uncalibrated proxy risk, no human optimum"
        )
    return ordered + rejected
