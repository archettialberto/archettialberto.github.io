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


def _color_vars(colors: dict, indent: str = "  ") -> str:
    # `--name` for plain CSS; `--name-rgb` so Tailwind opacity modifiers work.
    return "\n".join(
        f"{indent}--{name}: #{hexval};\n{indent}--{name}-rgb: {' '.join(str(c) for c in _hex_to_rgb(hexval))};"
        for name, hexval in colors.items()
    )


def write_web_css(theme: dict | None = None) -> Path:
    theme = theme or load_theme()
    colors = theme["colors"]
    fonts = theme["fonts"]
    web = theme["web"]

    imports = []
    for spec in fonts.values():
        for w in spec["weights"]:
            imports.append(f"@import '@fontsource/{spec['web_package']}/{w}.css';")

    display = fonts["display"].get("web_family", fonts["display"]["family"])
    text = fonts["text"].get("web_family", fonts["text"]["family"])

    css = f"""/* GENERATED from theme/theme.yaml by `cv build-site` — do not edit. */
{chr(10).join(imports)}

:root {{
  color-scheme: light;
{_color_vars(colors)}

  --display: '{display}', {fonts["display"]["fallback"]};
  --text: '{text}', {fonts["text"]["fallback"]};

  --max-width: {web["max_width"]};
  --radius: {web["radius"]};
}}

/* Dark: explicit choice (data-theme, set by the header toggle) or, without JS, the OS setting. */
:root[data-theme='dark'] {{
  color-scheme: dark;
{_color_vars(web["dark"])}
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme='light']) {{
    color-scheme: dark;
{_color_vars(web["dark"], indent="    ")}
  }}
}}
"""
    out = ROOT / "website" / "src" / "styles" / "theme.css"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(css, encoding="utf-8")
    return out
