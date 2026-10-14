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

POSTURE_CRITERIA = CRITERIA + (
    "maximum_flexion_reference_departure_rad",
    "maximum_deviation_reference_departure_rad",
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
    posture = {
        "maximum_" + name + "_reference_departure_rad": max(
            previous.get("maximum_" + name + "_reference_departure_rad", 0),
            float(
                abs(
                    q[:, names.index(joint)] - scene.model.qpos0[names.index(joint)]
                ).max()
            ),
        )
        for name, joint in (("flexion", "flexion_r"), ("deviation", "deviation_r"))
    }
    return {
        **posture,
        "wrist_reference": "myosim-imported-zero-v1; not observed neutral",
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


def pareto_order(nodes, criteria=CRITERIA, preference=None):
    """Nondominated layers, then declared wrist/proxy/digit/palm tie preference."""
    pending = list(nodes)
    ordered = []
    layer = 0
    while pending:
        frontier = []
        for node in pending:
            a = np.array([node["selection_descriptors"][k] for k in criteria])
            dominated_by = []
            for other in pending:
                b = np.array([other["selection_descriptors"][k] for k in criteria])
                if np.all(b <= a) and np.any(b < a):
                    dominated_by.append(other["id"])
            node["dominated_by_this_layer"] = dominated_by
            if not dominated_by:
                frontier.append(node)
        for node in frontier:
            node["pareto_layer"] = layer
        if preference is None:
            frontier.sort(
                key=lambda n: (
                    n["selection_descriptors"]["wrist_variation_rad"],
                    n["selection_descriptors"]["endpoint_proxy_penetration_m"],
                    n["selection_descriptors"]["digit_variation_rad"],
                    n["cost"],
                    n["id"],
                )
            )
        if preference:
            frontier.sort(
                key=lambda n: (
                    *(n["selection_descriptors"][k] for k in preference),
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


def posture_strategy_order(records, policy="posture", reference=None):
    """Second-stage Pareto ranking of complete paths; all alternatives retained.

    Coordinates use a declared imported reference. Optional shifts are sensitivity
    hypotheses. No scalar ergonomic score or clinical rejection is computed.
    """
    if policy not in ("palm", "movement", "posture", "whole_hand"):
        raise ValueError("Unknown posture comparison policy")
    from .wrist import WristReference

    ref = reference or WristReference()
    criteria = ["palm_path_m", "wrist_variation_rad", "digit_variation_rad"]
    preference = ["wrist_variation_rad", "palm_path_m", "digit_variation_rad"]
    if policy in ("posture", "whole_hand"):
        posture_axes = [
            "maximum_flexion_reference_departure_rad",
            "maximum_deviation_reference_departure_rad",
        ]
        criteria += posture_axes
        preference = posture_axes + preference
    if policy == "whole_hand":
        criteria += ["sampled_proxy_penetration_m"]
        preference = ["sampled_proxy_penetration_m"] + preference
    nodes = []
    rejected = []
    for record in records:
        hand = record["whole_hand"]
        independent = record["independent_audit"]
        wrist = record["wrist"]
        if (
            record["status"] != "sampled_connected_path"
            or hand["sample_count"] < 2
            or hand["state_sequence_sha256"] != independent["state_sequence_sha256"]
            or hand["sample_count"] != independent["sample_count"]
            or len(wrist["traces"]) != hand["sample_count"]
        ):
            raise ValueError("Posture ranking requires matching complete path evidence")
        if independent["status"] != "sampled_proxy_constraints_satisfied":
            rejected.append(
                dict(
                    id=record["id"],
                    status="rejected_configured_sample_checks",
                    policy=policy,
                )
            )
            continue
        digit_names = {n for d in hand["digits"].values() for n in d["joint_names"]}
        descriptors = dict(
            palm_path_m=hand["palm_path_m"],
            wrist_variation_rad=sum(
                hand["joint_descriptors"][n]["total_variation_rad"]
                for n in ("flexion_r", "deviation_r")
            ),
            digit_variation_rad=sum(
                hand["joint_descriptors"][n]["total_variation_rad"] for n in digit_names
            ),
            sampled_proxy_penetration_m=max(
                0, -independent["worst_cross_digit"]["distance_m"]
            ),
        )
        for j, (n, value) in enumerate(
            (("flexion", ref.flexion_rad), ("deviation", ref.deviation_rad))
        ):
            descriptors["maximum_" + n + "_reference_departure_rad"] = max(
                abs(t["signed_wrist_rad"][j] - value) for t in wrist["traces"]
            )
        nodes.append(
            dict(
                id=record["id"],
                cost=hand["palm_path_m"],
                selection_descriptors=descriptors,
                state_sequence_sha256=hand["state_sequence_sha256"],
            )
        )
    if policy == "palm":
        ordered = sorted(nodes, key=lambda n: (n["cost"], n["id"]))
    else:
        ordered = pareto_order(nodes, criteria, preference)
    for node in ordered:
        node["descriptors"] = node.pop("selection_descriptors")
        node["policy"] = policy
        node["reference"] = dict(
            id=ref.id,
            flexion_rad=ref.flexion_rad,
            deviation_rad=ref.deviation_rad,
            provenance=ref.provenance,
        )
        node["claim"] = (
            "Finite retained alternatives; full saved samples; "
            "anatomy unresolved; no human optimum"
        )
    return ordered + rejected
