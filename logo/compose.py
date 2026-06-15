"""Build the double-A monogram: a solid front A (with crossbar) and a
translucent back A (no crossbar) shifted straight up so its tip peeks above
the front A with a fixed white gap. Writes the logo, recoloured to the active
theme's accent, where the CV and website read it.

  python logo/compose.py                 # regenerate for the active theme
  python logo/compose.py --gap 0.45      # upward gap (fraction of height)
  python logo/compose.py --opacity 1.0   # back A full colour (default 0.3)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import cairosvg
except Exception:  # missing cairosvg or a broken native cairo library
    cairosvg = None

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "logo" / "original.svg"
GAP = 0.0       # upward shift of the back A, as a fraction of glyph height
OPACITY = 1.0   # back A opacity (1.0 = full colour)


def _glyphs() -> list[str]:
    """Two <path .../> strings from the original: [0]=back (no bar), [1]=front."""
    return re.findall(r"<path.*?/>", ORIGINAL.read_text(), re.DOTALL)


def build(color: str, gap: float = GAP, opacity: float = OPACITY) -> str:
    back, front = _glyphs()
    shift = -gap * 720  # original glyph box is 720 tall; SVG y grows downward
    back = back.replace('fill="#B8860B"', f'fill="{color}" fill-opacity="{opacity}"')
    front = front.replace('fill="#B8860B"', f'fill="{color}"')
    pad = 8
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{-15-pad} {shift-pad} {690+2*pad} {720-shift+2*pad}">'
        f'<g transform="translate(-15 0)">'
        f'<g transform="translate(0 {shift:.1f})">{back}</g>'
        f"{front}</g></svg>"
    )


def generate_for_theme(gap: float = GAP, opacity: float = OPACITY) -> list[Path]:
    sys.path.insert(0, str(ROOT))
    from src.theme import load_theme

    color = "#" + load_theme()["colors"]["gold"]
    svg = build(color, gap, opacity)
    targets = [
        ROOT / "cv" / "assets" / "logo-gold.svg",
        ROOT / "website" / "public" / "logo-gold.svg",
    ]
    for t in targets:
        t.write_text(svg)
    if cairosvg is not None:
        cairosvg.svg2pdf(url=str(targets[0]), write_to=str(ROOT / "cv" / "assets" / "logo-gold.pdf"))
    else:
        print("warning: cairo unavailable — logo-gold.pdf not regenerated (SVGs updated)")
    return targets


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=float, default=GAP)
    ap.add_argument("--opacity", type=float, default=OPACITY)
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()
    for t in generate_for_theme(args.gap, args.opacity):
        print(f"wrote {t.relative_to(ROOT)}")
    if args.png:
        cairosvg.svg2png(url=str(ROOT / "cv/assets/logo-gold.svg"),
                         write_to="/tmp/logo/preview.png", output_width=400,
                         background_color="white")
        print("wrote /tmp/logo/preview.png")


if __name__ == "__main__":
    main()
