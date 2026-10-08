"""Search withdrawal/reposition/approach paths; sampled validity is resolution-bound."""

from dataclasses import asdict, dataclass, replace
from time import perf_counter
from typing import Any

import numpy as np

from ._engine import mujoco
from .candidates import descriptors
from .experiment import Experiment
from .scene import Scene
from .solver import solve_contact


@dataclass(frozen=True)
class PlanningSettings:
    withdrawal_depths_m: tuple[float, ...] = (0.02, 0.04, 0.08, 0.12, 0.18)
    max_joint_step_rad: float = 0.005
    waypoint_iterations: int = 160
    withdrawal_step_m: float = 0.005
    rrt_iterations: int = 1500
    rrt_step_rad: float = 0.15
    rrt_bound_expansion_rad: float = 0.4
    seed: int = 614

    def __post_init__(self) -> None:
        positive = (
            self.max_joint_step_rad,
            self.withdrawal_step_m,
            self.rrt_step_rad,
            self.rrt_bound_expansion_rad,
        )
        if any(v <= 0 or not np.isfinite(v) for v in positive):
            raise ValueError("Path search dimensions must be finite and positive")
        if any(d <= 0 or not np.isfinite(d) for d in self.withdrawal_depths_m):
            raise ValueError("Withdrawal depths must be finite and positive")
        if type(self.waypoint_iterations) is not int or self.waypoint_iterations < 1:
            raise ValueError("Waypoint iteration budget must be positive integer")
        if type(self.rrt_iterations) is not int or self.rrt_iterations < 0:
            raise ValueError("RRT budget must be nonnegative integer")
        if type(self.seed) is not int or self.seed < 0:
            raise ValueError("Seed must be nonnegative integer")


def audit_path(
    scene: Scene,
    waypoints: list[list[float]],
    experiment: Experiment,
    settings: PlanningSettings,
) -> dict[str, Any]:
    model, data = scene.model, scene.data
    records = []
    for segment, (start, end) in enumerate(
        zip(waypoints[:-1], waypoints[1:], strict=True)
    ):
        a, b = np.array(start), np.array(end)
        steps = max(
            1, int(np.ceil(np.max(np.abs(b - a)) / settings.max_joint_step_rad))
        )
        for t in np.linspace(0, 1, steps + 1):
            data.qpos[:] = a + t * (b - a)
            mujoco.mj_forward(model, data)
            penetration = max([0.0] + [-float(c.dist) for c in data.contact])
            margins = np.minimum(
                data.qpos - model.jnt_range[:, 0], model.jnt_range[:, 1] - data.qpos
            )
            residual = float(
                np.max(
                    np.abs(
                        data.efc_pos[
                            data.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY
                        ]
                    ),
                    initial=0,
                )
            )
            valid = (
                penetration <= experiment.solver.penetration_tolerance_m
                and margins.min() >= -experiment.solver.joint_tolerance_rad
                and residual <= experiment.solver.equality_tolerance_rad
            )
            records.append(
                {
                    "segment": segment,
                    "segment_progress": float(t),
                    "qpos_rad": data.qpos.tolist(),
                    "sample_valid": bool(valid),
                    "penetration_m": penetration,
                    "joint_margin_min_rad": float(margins.min()),
                    "equality_residual_rad": residual,
                    "palm_world_m": data.body("capitate_r").xpos.tolist(),
                    "fingertip_world_m": data.site("index_pad").xpos.tolist(),
                }
            )
    valid = all(r["sample_valid"] for r in records)
    palm = np.array([r["palm_world_m"] for r in records])
    return {
        "status": "sampled_path_found" if valid else "candidate_rejected",
        "sampled_constraints_satisfied": valid,
        "continuous_validity": None,
        "maximum_penetration_m": max(r["penetration_m"] for r in records),
        "palm_path_length_m": float(
            np.linalg.norm(np.diff(palm, axis=0), axis=1).sum()
        ),
        "palm_max_excursion_m": float(np.linalg.norm(palm - palm[0], axis=1).max()),
        "minimum_joint_margin_rad": min(r["joint_margin_min_rad"] for r in records),
        "max_joint_step_rad": settings.max_joint_step_rad,
        "samples": records,
        "unvalidated": [
            "unsampled intervals",
            "dynamic actuation",
            "complete self-collision",
            "button operation",
        ],
    }


def plan_transition(
    scene: Scene,
    experiment: Experiment,
    start_q: list[float],
    end_q: list[float],
    button_id: str,
    settings: PlanningSettings,
) -> dict[str, Any]:
    if len(experiment.contacts) != 1 or experiment.contacts[0].finger != "index":
        raise ValueError("Transition search currently supports one index contact")
    began = perf_counter()
    direct = audit_path(scene, [start_q, end_q], experiment, settings)
    attempts: list[dict[str, Any]] = []
    if direct["sampled_constraints_satisfied"]:
        return {
            **direct,
            "method": "direct-joint-interpolation",
            "settings": asdict(settings),
            "elapsed_s": perf_counter() - began,
            "attempts": attempts,
        }
    normal = scene.data.body("keyboard").xmat.reshape(3, 3)[:, 2].copy()
    names = [scene.model.joint(i).name for i in range(scene.model.njnt)]
    targets = []
    for q in (start_q, end_q):
        scene.data.qpos[:] = q
        mujoco.mj_forward(scene.model, scene.data)
        targets.append(scene.data.site("index_pad").xpos.copy())
    for depth in settings.withdrawal_depths_m:
        withdraw = []
        chains = []
        for q, target in zip((start_q, end_q), targets, strict=True):
            chain = [q]
            result = None
            for distance in np.linspace(
                0, depth, max(1, int(np.ceil(depth / settings.withdrawal_step_m))) + 1
            )[1:]:
                result = solve_contact(
                    scene,
                    target + normal * distance,
                    dict(zip(names, chain[-1], strict=True)),
                    replace(
                        experiment.solver, max_iterations=settings.waypoint_iterations
                    ),
                    button_id,
                    experiment.frozen_joints,
                    contact_required=False,
                )
                if result["status"] != "success":
                    break
                chain.append(result["qpos_rad"])
            assert result is not None
            withdraw.append(result)
            chains.append(chain)
        attempt: dict[str, Any] = {
            "withdrawal_depth_m": depth,
            "waypoint_solves": withdraw,
        }
        if all(r["status"] == "success" for r in withdraw):
            middle = [chains[0][-1], chains[1][-1]]
            middle_audit = audit_path(scene, middle, experiment, settings)
            if not middle_audit["sampled_constraints_satisfied"]:
                middle, search = rrt_connect(
                    scene, middle[0], middle[1], experiment, settings
                )
                attempt["rrt_search"] = search
            if middle:
                waypoints = chains[0][:-1] + middle + list(reversed(chains[1]))[1:]
                audit = audit_path(scene, waypoints, experiment, settings)
                attempt["audit"] = {k: v for k, v in audit.items() if k != "samples"}
                if audit["sampled_constraints_satisfied"]:
                    attempts.append(attempt)
                    scene.data.qpos[:] = end_q
                    return {
                        **audit,
                        "method": "incremental-withdraw-rrt-approach",
                        "withdrawal_depth_m": depth,
                        "waypoints_qpos_rad": waypoints,
                        "settings": asdict(settings),
                        "attempts": attempts,
                        "endpoint_descriptors": asdict(descriptors(scene)),
                        "direct_audit": {
                            k: v for k, v in direct.items() if k != "samples"
                        },
                        "elapsed_s": perf_counter() - began,
                        "physical_feasibility": None,
                    }
        attempts.append(attempt)
    return {
        "status": "no_path_found",
        "physical_feasibility": None,
        "continuous_validity": None,
        "direct_audit": direct,
        "attempts": attempts,
        "settings": asdict(settings),
        "elapsed_s": perf_counter() - began,
        "claim": "Finite waypoint search failed; not an impossibility proof",
    }


def rrt_connect(
    scene: Scene,
    start: list[float],
    end: list[float],
    experiment: Experiment,
    settings: PlanningSettings,
) -> tuple[list[list[float]], dict[str, Any]]:
    """Seeded bidirectional RRT on independent coordinates, with exact coupling lift."""
    from .scene import coupled_initial_pose

    rng = np.random.default_rng(settings.seed)
    model, data = scene.model, scene.data
    if np.any(model.eq_data[:, 2:5] != 0):
        raise ValueError("RRT edge interpolation requires affine joint couplings")
    dependent = set(int(model.eq_obj1id[i]) for i in range(model.neq))
    frozen = set(
        list(range(18, 22))
        + list(range(26, model.nv))
        + [int(model.joint(n).id) for n in experiment.frozen_joints]
    )
    active = [i for i in range(model.njnt) if i not in dependent and i not in frozen]
    names = [model.joint(i).name for i in range(model.njnt)]
    a, b = np.array(start), np.array(end)
    low = np.maximum(
        model.jnt_range[active, 0],
        np.minimum(a[active], b[active]) - settings.rrt_bound_expansion_rad,
    )
    high = np.minimum(
        model.jnt_range[active, 1],
        np.maximum(a[active], b[active]) + settings.rrt_bound_expansion_rad,
    )
    nodes = [[a], [b]]
    parents = [[-1], [-1]]
    evaluations = 0

    def lift(v: np.ndarray) -> np.ndarray | None:
        q = a.copy()
        q[active] = v
        try:
            return coupled_initial_pose(
                model, dict(zip(names, q.tolist(), strict=True))
            )
        except ValueError:
            return None

    def edge(q0: np.ndarray, q1: np.ndarray) -> bool:
        nonlocal evaluations
        count = max(
            1, int(np.ceil(np.max(np.abs(q1 - q0)) / settings.max_joint_step_rad))
        )
        for t in np.linspace(0, 1, count + 1):
            data.qpos[:] = q0 + t * (q1 - q0)
            mujoco.mj_forward(model, data)
            evaluations += 1
            if any(
                c.dist < -experiment.solver.penetration_tolerance_m
                for c in data.contact
            ):
                return False
        return True

    def extend(tree: int, target: np.ndarray) -> tuple[int | None, bool]:
        nearest = int(
            np.argmin([np.linalg.norm(n[active] - target[active]) for n in nodes[tree]])
        )
        q = nodes[tree][nearest]
        delta = target[active] - q[active]
        length = np.linalg.norm(delta)
        v = q[active] + delta * min(1.0, settings.rrt_step_rad / max(length, 1e-12))
        proposed = lift(v)
        if proposed is None or not edge(q, proposed):
            return None, False
        nodes[tree].append(proposed)
        parents[tree].append(nearest)
        return len(nodes[tree]) - 1, bool(length <= settings.rrt_step_rad)

    def chain(tree: int, index: int) -> list[list[float]]:
        result = []
        while index >= 0:
            result.append(nodes[tree][index].tolist())
            index = parents[tree][index]
        return list(reversed(result))

    for iteration in range(settings.rrt_iterations):
        tree = iteration % 2
        other = 1 - tree
        random = lift(rng.uniform(low, high))
        if random is None:
            continue
        first, _ = extend(tree, random)
        if first is None:
            continue
        target = nodes[tree][first]
        for _ in range(100):
            second, reached = extend(other, target)
            if second is None:
                break
            if reached:
                c0, c1 = (
                    (chain(tree, first), chain(other, second))
                    if tree == 0
                    else (chain(other, second), chain(tree, first))
                )
                return c0 + list(reversed(c1))[1:], {
                    "status": "path_found",
                    "iterations": iteration + 1,
                    "collision_evaluations": evaluations,
                    "nodes": [len(n) for n in nodes],
                    "seed": settings.seed,
                }
    return [], {
        "status": "no_path_found",
        "iterations": settings.rrt_iterations,
        "collision_evaluations": evaluations,
        "nodes": [len(n) for n in nodes],
        "seed": settings.seed,
    }
