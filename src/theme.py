"""theme/theme.yaml -> LaTeX color/font definitions + website theme.css."""

from __future__ import annotations

from pathlib import Path

import yaml

from .loader import ROOT

THEME_FILE = ROOT / "theme" / "theme.yaml"


def load_theme() -> dict:
    with THEME_FILE.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def latex_color_defs(theme: dict | None = None) -> str:
    theme = theme or load_theme()
    lines = []
    for name, hexval in theme["colors"].items():
        r, g, b = _hex_to_rgb(hexval)
        lines.append(f"\\definecolor{{{name}}}{{RGB}}{{{r},{g},{b}}}")
    return "\n".join(lines)


def font_families(theme: dict | None = None) -> dict[str, str]:
    theme = theme or load_theme()
    return {role: spec["family"] for role, spec in theme["fonts"].items()}


def write_web_css(theme: dict | None = None) -> Path:
    theme = theme or load_theme()
    colors = theme["colors"]
    fonts = theme["fonts"]
    web = theme.get("web", {})

    imports = []
    for spec in fonts.values():
        for w in spec["weights"]:
            imports.append(f"@import '@fontsource/{spec['web_package']}/{w}.css';")

    # `--name` for plain CSS; `--name-rgb` so Tailwind opacity modifiers work.
    color_vars = "\n".join(
        f"  --{name}: #{hexval};\n  --{name}-rgb: {' '.join(str(c) for c in _hex_to_rgb(hexval))};"
        for name, hexval in colors.items()
    )
    display = fonts["display"].get("web_family", fonts["display"]["family"])
    text = fonts["text"].get("web_family", fonts["text"]["family"])
    display_fallback = fonts["display"].get("fallback", "Georgia, serif")
    text_fallback = fonts["text"].get("fallback", "system-ui, sans-serif")

    css = f"""/* GENERATED from theme/theme.yaml by `cv build-site` — do not edit. */
{chr(10).join(imports)}

:root {{
{color_vars}

  --display: '{display}', {display_fallback};
  --text: '{text}', {text_fallback};

  --max-width: {web.get('max_width', '920px')};
  --radius: {web.get('radius', '2px')};
}}
"""
    out = ROOT / "website" / "src" / "styles" / "theme.css"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(css, encoding="utf-8")
    return out
