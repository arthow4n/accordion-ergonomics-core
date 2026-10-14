"""Independent inverse-wrap root probe; never substitutes native tendon geometry."""

import numpy as np
from scipy.optimize import brentq

from ._engine import mujoco


def inverse_wrap_diagnostic(model, data, tendon_name):
    """Compare native inverse-wrap points with a scalar root and fallback geometry.

    Limited to an isolated site/geom/site component with an interior side site.
    Root solutions are diagnostics, not repaired muscle transmissions or paths.
    """
    tid = model.tendon(tendon_name).id
    start = int(model.tendon_adr[tid])
    count = int(model.tendon_num[tid])
    segments = []
    for j in range(start + 1, start + count - 1):
        kind = int(model.wrap_type[j])
        if kind not in (
            int(mujoco.mjtWrap.mjWRAP_SPHERE),
            int(mujoco.mjtWrap.mjWRAP_CYLINDER),
        ):
            continue
        if (
            model.wrap_type[j - 1] != mujoco.mjtWrap.mjWRAP_SITE
            or model.wrap_type[j + 1] != mujoco.mjtWrap.mjWRAP_SITE
        ):
            continue
        geom = int(model.wrap_objid[j])
        side = int(model.wrap_prm[j])
        radius = float(model.geom_size[geom, 0])
        rotation = data.geom_xmat[geom].reshape(3, 3)
        if side < 0:
            continue
        local_side = rotation.T @ (data.site_xpos[side] - data.geom_xpos[geom])
        if np.linalg.norm(local_side) >= radius:
            continue
        endpoints = np.array(
            [
                rotation.T
                @ (data.site_xpos[int(model.wrap_objid[k])] - data.geom_xpos[geom])
                for k in (j - 1, j + 1)
            ]
        )
        if kind == int(mujoco.mjtWrap.mjWRAP_CYLINDER):
            axes = np.eye(3)[:2]
        else:
            axis = endpoints[0] / np.linalg.norm(endpoints[0])
            normal = np.cross(endpoints[0], endpoints[1])
            normal /= np.linalg.norm(normal)
            axes = np.array([axis, np.cross(normal, axis)])
        end = endpoints @ axes.T
        length = np.linalg.norm(end, axis=1)
        a, b = radius / length
        g = float(
            np.arccos(np.clip((end[0] @ end[1]) / (length[0] * length[1]), -1, 1))
        )
        if max(a, b) >= 1:
            continue

        def residual(z, a=a, b=b, g=g):
            return float(np.arcsin(a * z) + np.arcsin(b * z) - 2 * np.arcsin(z) + g)

        if residual(0) * residual(1) > 0:
            continue
        root = brentq(residual, 0, 1, xtol=1e-15)
        cross = end[0, 0] * end[1, 1] - end[0, 1] * end[1, 0]
        chosen = end[0] if cross > 0 else end[1]
        angle = np.arcsin(root) - np.arcsin((a if cross > 0 else b) * root)
        chosen = chosen / np.linalg.norm(chosen)
        c, s = np.cos(angle), np.sin(angle)
        point = radius * np.array(
            [c * chosen[0] - s * chosen[1], s * chosen[0] + c * chosen[1]]
        )
        fallback = end.sum(axis=0)
        fallback = radius * fallback / np.linalg.norm(fallback)
        adr = int(data.ten_wrapadr[tid])
        num = int(data.ten_wrapnum[tid])
        objects = data.wrap_obj.reshape(-1)[adr : adr + num]
        points = data.wrap_xpos.reshape(-1, 3)[adr : adr + num]
        selected = points[objects == geom]
        if not len(selected):
            continue
        native = (selected[0] - data.geom_xpos[geom]) @ rotation @ axes.T
        segments.append(
            dict(
                geom=model.geom(geom).name,
                inside_sidesite_local_m=local_side.tolist(),
                endpoints_in_wrap_plane_m=end.tolist(),
                native_point_in_wrap_plane_m=native.tolist(),
                independent_root=root,
                independent_point_m=point.tolist(),
                fallback_average_point_m=fallback.tolist(),
                native_to_root_distance_m=float(np.linalg.norm(native - point)),
                native_to_fallback_distance_m=float(np.linalg.norm(native - fallback)),
                root_residual=residual(root),
                pinned_initial_z=0.9999999,
                residual_at_pinned_initial_z=residual(0.9999999),
                native_point_classification=(
                    "matches_fallback_average"
                    if np.linalg.norm(native - fallback) < 1e-8
                    else "matches_independent_root"
                    if np.linalg.norm(native - point) < 1e-8
                    else "unexplained_native_point"
                ),
                claim=(
                    "Independent inverse-wrap root versus native branch; "
                    "not a geometry correction"
                ),
            )
        )
    return segments
