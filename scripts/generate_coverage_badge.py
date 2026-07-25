import os
import sys

import coverage


def get_color(pct: float) -> str:
    """Return badge color hex code based on percentage."""
    if pct >= 95:
        return "#4c1"  # brightgreen
    elif pct >= 90:
        return "#97CA00"  # green
    elif pct >= 75:
        return "#a4a61d"  # yellowgreen
    elif pct >= 60:
        return "#dfb317"  # yellow
    elif pct >= 40:
        return "#fe7d37"  # orange
    else:
        return "#e05d44"  # red


def generate_badge(output_path: str = "coverage.svg") -> None:
    """Generate SVG coverage badge from .coverage data."""
    cov = coverage.Coverage()
    cov.load()
    with open(os.devnull, "w") as null:
        total = cov.report(file=null)

    pct_str = f"{int(round(total))}%"
    color = get_color(total)

    font_fam = "DejaVu Sans,Verdana,Geneva,sans-serif"
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="99" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="99" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="{color}" d="M63 0h36v20H63z"/>
        <path fill="url(#b)" d="M0 0h99v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="{font_fam}" font-size="11">
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
        <text x="31.5" y="14">coverage</text>
        <text x="80" y="15" fill="#010101" fill-opacity=".3">{pct_str}</text>
        <text x="80" y="14">{pct_str}</text>
    </g>
</svg>
"""
    with open(output_path, "w", encoding="utf-8") as fdesc:
        fdesc.write(svg)
    print(f"Saved coverage badge to {output_path} ({pct_str})")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "coverage.svg"
    generate_badge(output)
