"""Hash-bound v3 research navigation and diagrams from executed benchmark records."""

import json
from html import escape

from PIL import Image, ImageDraw, ImageFont

from .digits import DIGITS
from .experiment import Experiment
from .exploration import read_hashed
from .scene import build_scene
from .wrist_study import finish_record


def run_playing_library(definition, output):
    source = json.loads(definition.read_text())
    root = definition.resolve().parents[2]
    output.mkdir(parents=True, exist_ok=True)
    catalog = read_hashed(
        definition.parent / source["catalog_result"], source["catalog_sha256"]
    )
    bindings = {}
    studies, reviews, tables = [], [], []
    scene = None
    for ref in source["evidence"]:
        path = definition.parent / ref["path"]
        saved = read_hashed(path, ref["sha256"])
        evidence = dict(
            path=str(path.resolve().relative_to(root)), sha256=ref["sha256"]
        )
        if ref["kind"] == "review":
            reviews.append(evidence)
            continue
        studies.append(evidence)
        for case in saved["cases"]:
            target_id = source["case_targets"][case["id"]]
            bindings[case["id"]] = dict(
                case_id=case["id"],
                target_id=target_id,
                evidence=evidence,
                definition=str(
                    (definition.parent / ref["definition"]).resolve().relative_to(root)
                ),
                state_sequence_sha256=case["region"]["state_sequence_sha256"],
                compiled_model_sha256=case["compiled_model_sha256"],
                status="sampled_path_anatomy_unresolved",
                media_available=case["media"] is not None,
            )
            if ref.get("policy_table"):
                region = case["region"]
                whole = case["whole_hand"]
                tables.append(
                    dict(
                        id=case["id"],
                        palm_mm=whole["palm_path_m"] * 1000,
                        normal_span_mm=(
                            region["landmarks"]["capitate"]["maximum_board_m"][2]
                            - region["landmarks"]["capitate"]["minimum_board_m"][2]
                        )
                        * 1000,
                        overlap_mm=-whole["worst_proxy_m"] * 1000,
                        wrist_variation_rad=sum(
                            v["total_variation_rad"]
                            for v in whole["wrist"]["summary"].values()
                        ),
                        consumed_contact_solves=case["budget"]["contact_solves"],
                        budget=case["budget"],
                        evidence=evidence,
                        selection_mode=case["settings"]["selection_mode"],
                        guidance_cost=case["settings"]["whole_hand_guidance_cost"],
                    )
                )
            if scene is None:
                search = read_hashed(
                    definition.parent / ref["definition"], saved["definition_sha256"]
                )
                request = search["cases"][0]
                numerical = read_hashed(
                    (definition.parent / ref["definition"]).parent
                    / request["search_result"],
                    request["search_sha256"],
                )
                e = Experiment.from_dict(numerical["scene_input"])
                scene = build_scene(
                    e.geometry, e.player, e.setup, e.physical_contact, DIGITS
                )
    targets = [
        dict(
            target_id=t["id"],
            cases=[c for c in bindings.values() if c["target_id"] == t["id"]],
            review_ids=[
                rid
                for rid, tid in source.get("review_targets", {}).items()
                if tid == t["id"]
            ],
            status="model_assessed"
            if any(c["target_id"] == t["id"] for c in bindings.values())
            else "reviewed_failure"
            if any(tid == t["id"] for tid in source.get("review_targets", {}).values())
            else "unassessed",
            anatomical_validation="unresolved",
            human_feasibility=None,
        )
        for t in catalog["targets"]
    ]
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1450" height="'
        + str(120 + len(tables) * 32)
        + '"><rect width="100%" height="100%" fill="#f5f7fa"/>'
        '<g font-family="monospace" fill="#142030">',
        '<text x="20" y="28" font-size="18">Executed policy comparisons / '
        "all retained alternatives</text>",
        '<text x="20" y="52" font-size="13">Separate metrics; no comfort score. '
        "Same caps; consumed work and selected branches differ.</text>",
        '<text x="20" y="82" font-size="13">Case                                  '
        "palm mm   normal span mm   overlap mm   wrist variation rad   "
        "contact solves</text>",
    ]
    image = Image.new("RGB", (1450, 130 + 32 * len(tables)), "#f5f7fa")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    draw.text(
        (20, 12),
        "Actual retained strategies: separate metrics, no comfort score",
        fill="#142030",
        font=font,
    )
    draw.text(
        (20, 44),
        "case                                    palm mm   normal span mm   "
        "overlap mm   wrist variation rad   solves",
        fill="#142030",
        font=font,
    )
    for i, row in enumerate(tables):
        text = (
            f"{row['id']:<38} {row['palm_mm']:>7.2f} "
            f"{row['normal_span_mm']:>14.2f} {row['overlap_mm']:>12.3f} "
            f"{row['wrist_variation_rad']:>21.4f} {row['consumed_contact_solves']:>14}"
        )
        draw.text((20, 82 + i * 32), text, fill="#142030", font=font)
        lines.append(
            f'<text x="20" y="{110 + i * 32}" font-size="13">{escape(text)}</text>'
        )
    image.save(output / "policy-tradeoffs.png")
    lines.append("</g></svg>")
    (output / "policy-tradeoffs.svg").write_text("\n".join(lines) + "\n")
    if scene is None:
        raise ValueError("Library needs a compiled benchmark")
    return finish_record(
        definition,
        output,
        source,
        dict(
            id=source["id"],
            assessment_version="playing-region-lifecycle-v3",
            catalog_sha256=source["catalog_sha256"],
            targets=targets,
            studies=studies,
            reviews=reviews,
            policy_comparisons=tables,
            benchmarks=[c for c in bindings.values() if c["target_id"] is None],
            benchmark_references=[
                ref
                | {
                    "path": str(
                        (definition.parent / ref["path"]).resolve().relative_to(root)
                    )
                }
                for ref in source.get("benchmark_references", [])
            ],
            limitations=[
                "Uncalibrated hand proxies",
                "Actuation/forces/travel unknown",
                "Untimed sampled geometry",
                "Muscle ranking withheld",
                "Human comfort/feasibility unknown",
            ],
        ),
        scene,
    )
