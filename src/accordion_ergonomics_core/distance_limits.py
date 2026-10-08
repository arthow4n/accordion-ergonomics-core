"""Explicit signed-distance displacement limits for the Mink QP.

Mink 1.3.0 bounds displacement using a velocity and drops some world pairs.
This implementation uses its public Limit contract with MuJoCo point Jacobians;
it does not patch the installed dependency or modify anatomical envelopes.
"""

from itertools import product

import mink
import numpy as np
from numpy.typing import NDArray

from ._engine import Data, Model, mujoco
from .profiles import ContactProfile


def collision_pairs(
    model: Model, anatomy: list[int], board: list[int]
) -> tuple[tuple[int, int], ...]:
    """Board/anatomy automatic pairs plus explicit pairs, in stable order.

    World weld groups are exempt from the parent filter, as in MuJoCo.
    Imported and profile-requested explicit pairs bypass mask filtering.
    """
    pairs = {
        (min(int(a), int(b)), max(int(a), int(b)))
        for a, b in zip(model.pair_geom1, model.pair_geom2, strict=True)
    }
    for a, b in product(anatomy, board):
        body_a, body_b = int(model.geom_bodyid[a]), int(model.geom_bodyid[b])
        weld_a, weld_b = int(model.body_weldid[body_a]), int(model.body_weldid[body_b])
        if weld_a == weld_b:
            continue
        if (
            weld_a
            and weld_b
            and (
                weld_a == int(model.body_weldid[model.body_parentid[weld_b]])
                or weld_b == int(model.body_weldid[model.body_parentid[weld_a]])
            )
        ):
            continue
        if not (
            (int(model.geom_contype[a]) & int(model.geom_conaffinity[b]))
            or (int(model.geom_contype[b]) & int(model.geom_conaffinity[a]))
        ):
            continue
        if (
            (min(body_a, body_b) << 16) + max(body_a, body_b)
        ) in model.exclude_signature:
            continue
        pairs.add((min(a, b), max(a, b)))
    return tuple(sorted(pairs))


def signed_distance_gradient(
    model: Model, data: Data, a: int, b: int, cutoff_m: float
) -> tuple[float, NDArray[np.float64] | None]:
    """Local derivative in m per tangent coordinate; nonsmoothness is unproven."""
    points = np.empty(6)
    distance = float(mujoco.mj_geomDistance(model, data, a, b, cutoff_m, points))
    if distance >= cutoff_m:
        return distance, None
    vector = points[3:] - points[:3]
    length = float(np.linalg.norm(vector))
    if length > 1e-12:
        normal = vector / length * (1 if distance >= 0 else -1)
    else:
        # At touching, the two closest points coincide. Use the engine normal
        # rather than silently adding a zero inequality row.
        # Mink refreshes kinematics without running collision detection.
        mujoco.mj_collision(model, data)
        normal = None
        for contact in data.contact:
            pair = (int(contact.geom1), int(contact.geom2))
            if pair == (a, b) or pair == (b, a):
                normal = np.asarray(contact.frame[:3]).copy()
                if pair == (b, a):
                    normal *= -1
                break
        if normal is None:
            raise ValueError("Degenerate distance normal with no engine contact")
    jac_a = np.zeros((3, model.nv))
    jac_b = np.zeros((3, model.nv))
    mujoco.mj_jac(model, data, jac_a, None, points[:3], int(model.geom_bodyid[a]))
    mujoco.mj_jac(model, data, jac_b, None, points[3:], int(model.geom_bodyid[b]))
    return distance, normal @ (jac_b - jac_a)


class DisplacementDistanceLimit(mink.Limit):
    """-grad(d) Δq <= gain * max(d - minimum, 0), independently of dt.

    This local inequality prevents closing an active positive gap too quickly;
    an already penetrated state is not guaranteed to recover. Samples and edges
    still need independent validation. The activation band is not a path proof.
    """

    def __init__(
        self, model: Model, pairs: tuple[tuple[int, int], ...], policy: ContactProfile
    ) -> None:
        self.model, self.pairs, self.policy = model, pairs, policy

    def compute_qp_inequalities(
        self, configuration: mink.Configuration, dt: float
    ) -> mink.Constraint:
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("Integration timestep must be positive seconds")
        rows, bounds = [], []
        cutoff = self.policy.collision_detection_distance_m
        # Bounding spheres conservatively reject far primitive pairs. Unbounded
        # shapes are retained. No contact masks are applied to explicit pairs.
        for a, b in self.pairs:
            if self.model.geom_rbound[a] > 0 and self.model.geom_rbound[b] > 0:
                if (
                    np.linalg.norm(
                        configuration.data.geom_xpos[b]
                        - configuration.data.geom_xpos[a]
                    )
                    > self.model.geom_rbound[a] + self.model.geom_rbound[b] + cutoff
                ):
                    continue
            distance, gradient = signed_distance_gradient(
                self.model, configuration.data, a, b, cutoff
            )
            if gradient is None:
                continue
            rows.append(-gradient)
            bounds.append(
                self.policy.collision_gain
                * max(distance - self.policy.collision_minimum_distance_m, 0)
            )
        if not rows:
            return mink.Constraint()
        return mink.Constraint(G=np.asarray(rows), h=np.asarray(bounds))
