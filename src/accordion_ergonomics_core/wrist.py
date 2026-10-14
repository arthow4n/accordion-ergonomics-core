"""Signed, untimed wrist descriptors relative to an identified model reference."""

import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path

import myo_sim
import numpy as np
from scipy.spatial.transform import Rotation

from ._engine import mujoco
from .anatomy import digit_dofs

WRIST_JOINTS = ("flexion_r", "deviation_r")


@dataclass(frozen=True)
class WristReference:
    id: str = "myosim-imported-zero-v1"
    flexion_rad: float = 0.0
    deviation_rad: float = 0.0
    provenance: str = (
        "Pinned MyoSim qpos0; geometric reference, no observed neutral calibration"
    )

    def __post_init__(self):
        if (
            not self.id
            or not self.provenance
            or not np.isfinite([self.flexion_rad, self.deviation_rad]).all()
        ):
            raise ValueError(
                "Wrist reference needs identity, provenance and finite angles"
            )


def wrist_coordinates(model):
    expected = (("flexion_r", [1, 0, 0]), ("deviation_r", [0, 0, 1]))
    coordinates = {}
    for name, axis in expected:
        joint = model.joint(name)
        if (
            model.body(joint.bodyid[0]).name != "lunate_r"
            or not np.allclose(joint.axis, axis, atol=1e-12)
            or joint.type[0] != mujoco.mjtJoint.mjJNT_HINGE
        ):
            raise ValueError("Unsupported imported wrist frame")
        coordinates[name] = dict(
            qpos_index=int(joint.qposadr[0]),
            axis_in_body=joint.axis.tolist(),
            body="lunate_r",
            range_rad=joint.range.tolist(),
            default_rad=float(model.qpos0[joint.qposadr[0]]),
            positive_direction="flexion toward native FCR side"
            if name == "flexion_r"
            else "radial deviation toward second metacarpal",
        )
    return coordinates


def reference_geometry(scene):
    """Compiled FK probes establish geometric signs, not clinical neutrality."""
    m, d = scene.model, scene.data
    previous = d.qpos.copy()
    coordinates = wrist_coordinates(m)
    probes = []
    try:
        for name, delta in (
            ("reference", 0),
            ("flexion_r", 0.05),
            ("deviation_r", 0.05),
            ("pro_sup_r", 0.05),
        ):
            d.qpos[:] = m.qpos0
            if name != "reference":
                d.qpos[m.joint(name).qposadr[0]] += delta
            mujoco.mj_forward(m, d)
            radius = d.body("radius_r")
            r = radius.xmat.reshape(3, 3)
            palm = d.body("capitate_r")
            longitudinal = d.body("thirdmc_r").xpos - palm.xpos
            longitudinal /= np.linalg.norm(longitudinal)
            radial = d.body("secondmc_r").xpos - d.body("fifthmc_r").xpos
            radial /= np.linalg.norm(radial)
            probes.append(
                dict(
                    coordinate=name,
                    delta_rad=delta,
                    qpos_rad=d.qpos.tolist(),
                    hand_longitudinal_in_radius=(r.T @ longitudinal).tolist(),
                    radial_landmark_direction_in_radius=(r.T @ radial).tolist(),
                    palm_axes_in_radius=(r.T @ palm.xmat.reshape(3, 3)).tolist(),
                )
            )
    finally:
        d.qpos[:] = previous
        mujoco.mj_forward(m, d)
    chain = Path(myo_sim.__file__).parent / "models/arm/assets/myoarm_r_chain.xml"
    return dict(
        coordinates=coordinates,
        probes=probes,
        source=dict(
            path="myo_sim/models/arm/assets/myoarm_r_chain.xml",
            sha256=hashlib.sha256(chain.read_bytes()).hexdigest(),
        ),
        zero_interpretation=(
            "Native radius/lunate/capitate body axes coincide at "
            "zero. Landmark hand axis is oblique; no observed neutral "
            "wrist."
        ),
        sign_evidence=(
            "Positive x hinge turns distal -y toward -z (native FCR "
            "palmar routing side). Positive z hinge turns -y toward "
            "+x (second versus fifth metacarpal radial side)."
        ),
        forearm_interpretation=(
            "pro_sup_r rotates radius and whole downstream wrist; "
            "neither board orientation nor palm body axes are wrist "
            "angles"
        ),
    )


def wrist_descriptors(model, states, names, reference=None, *, connected=True):
    reference = reference or WristReference()
    coords = wrist_coordinates(model)
    q = np.asarray([s["qpos_rad"] for s in states])
    if not len(q) or q.shape != (len(states), model.nq) or not np.isfinite(q).all():
        raise ValueError("Wrist diagnostics need finite actual configurations")
    if names != [model.joint(i).name for i in range(model.njnt)]:
        raise ValueError("Wrist diagnostics need verified compiled coordinate order")
    summary = {}
    traces = []
    reference_values = (reference.flexion_rad, reference.deviation_rad)
    for name, ref in zip(WRIST_JOINTS, reference_values, strict=True):
        c = coords[name]
        values = q[:, c["qpos_index"]]
        low, high = c["range_rad"]
        departure = abs(values - ref)
        summary[name] = dict(
            minimum_rad=float(values.min()),
            maximum_rad=float(values.max()),
            minimum_sample_index=int(values.argmin()),
            maximum_sample_index=int(values.argmax()),
            maximum_reference_departure_rad=float(departure.max()),
            extreme_reference_sample_index=int(departure.argmax()),
            minimum_joint_limit_margin_rad=float(
                np.minimum(values - low, high - values).min()
            ),
            total_variation_rad=float(abs(np.diff(values)).sum())
            if connected
            else None,
        )
    for i, state in enumerate(states):
        values = [float(q[i, coords[n]["qpos_index"]]) for n in WRIST_JOINTS]
        traces.append(
            dict(
                sample_index=i,
                event_index=state.get("event_index"),
                signed_wrist_rad=values,
                reference_departure_rad=(
                    np.asarray(values) - reference_values
                ).tolist(),
                range_fraction=[
                    (v - coords[n]["range_rad"][0]) / np.ptp(coords[n]["range_rad"])
                    for n, v in zip(WRIST_JOINTS, values, strict=True)
                ],
                joint_limit_margin_rad=[
                    min(v - coords[n]["range_rad"][0], coords[n]["range_rad"][1] - v)
                    for n, v in zip(WRIST_JOINTS, values, strict=True)
                ],
                forearm_rotation_rad=float(q[i, names.index("pro_sup_r")]),
                finger_coordinates_rad={
                    n: float(q[i, j])
                    for j, n in enumerate(names)
                    if n.startswith(("mcp", "pip", "dip", "cmc", "ip_"))
                },
            )
        )
    finger_indices = {i for ids in digit_dofs(model).values() for i in ids}
    for i, trace in enumerate(traces):
        trace["finger_coordinates_rad"] = {
            names[j]: float(q[i, j]) for j in sorted(finger_indices)
        }
    events = [t for t in traces if t["event_index"] is not None]
    return dict(
        version="wrist-posture-v1",
        reference=asdict(reference),
        coordinate_order=list(WRIST_JOINTS),
        coordinates=coords,
        summary=summary,
        traces=traces,
        musical_events=events,
        connected=connected,
        distribution_summary="omitted; untimed sampling density is not exposure",
        interpretation=(
            "Reference-relative model posture and motion are "
            "separate; no strain, clinical threshold or human "
            "feasibility"
        ),
    )


def orientation_trace(scene, geometry):
    r = geometry.rotation.T
    return {
        name: Rotation.from_matrix(r @ scene.data.body(name).xmat.reshape(3, 3))
        .as_quat()
        .tolist()
        for name in ("radius_r", "ulna_r", "capitate_r")
    }
