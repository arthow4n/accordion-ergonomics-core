"""Small deterministic SVG traces from computational arrays (no physiology art)."""

from html import escape
from pathlib import Path

import numpy as np

COLORS = ("#5bd4dd", "#f5b55c", "#df7bcd", "#92cb70", "#8ca9ff", "#f08080")


def trace_svg(
    path: Path, title: str, panels: list[dict], *, x_axis: str = "actual sample index"
):
    width, height = 1100, 75 + 235 * len(panels)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<rect width="100%" height="100%" fill="#142030"/>',
        '<g font-family="monospace" fill="#eef3f8">',
        f'<text x="20" y="25" font-size="15">{escape(title)}</text>',
        f'<text x="20" y="48" font-size="11">X: {escape(x_axis)}; '
        "no velocity/effort/human-validity inference</text>",
    ]
    for row, panel in enumerate(panels):
        top = 100 + row * 235
        series = panel["series"]
        values = np.concatenate([np.asarray(v) for v in series.values()])
        if not np.isfinite(values).all():
            raise ValueError("Plot requires finite actual observations")
        low, high = float(values.min()), float(values.max())
        span = high - low or 1.0
        svg += [
            f'<text x="15" y="{top - 15}" font-size="12">'
            f"{escape(panel['label'])} [{low:.5g}, {high:.5g}]</text>",
            f'<path d="M70,{top} V{top + 145} H1070" fill="none" stroke="#7b8c9e"/>',
        ]
        for i, (label, data) in enumerate(series.items()):
            color = COLORS[i % len(COLORS)]
            data = np.asarray(data)
            x = np.linspace(70, 1070, len(data))
            y = top + 145 - 140 * (data - low) / span
            points = " ".join(f"{a:.2f},{b:.2f}" for a, b in zip(x, y, strict=True))
            svg += [
                f'<polyline points="{points}" fill="none" '
                f'stroke="{color}" stroke-width="1.5"/>',
                f'<text x="{70 + (i % 3) * 335}" '
                f'y="{top + 167 + (i // 3) * 16}" fill="{color}" '
                f'font-size="10">{escape(label)}</text>',
            ]
        svg.append(
            f'<text x="70" y="{top + 145}" font-size="9">0</text>'
            f'<text x="1030" y="{top + 145}" font-size="9">'
            f"{len(next(iter(series.values()))) - 1}</text>"
        )
    svg.append("</g></svg>")
    path.write_text("\n".join(svg) + "\n")
