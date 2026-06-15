"""Theme: one source of truth (theme/theme.yaml) for CV + website.

- :func:`load_theme` reads the YAML.
- :func:`latex_color_defs` emits ``\\definecolor`` lines for the LaTeX preamble.
- :func:`write_web_css` generates ``website/src/styles/theme.css`` (CSS variables
  + ``@fontsource`` imports) so the site uses the identical palette and fonts.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from .loader import ROOT

THEME_DIR = ROOT / "theme"
THEMES_DIR = THEME_DIR / "themes"
ACTIVE_FILE = THEME_DIR / "active.yaml"
DEFAULT_THEME = "old-money"


def list_themes() -> list[str]:
    """Names of all available themes (theme/themes/*.yaml)."""
    return sorted(p.stem for p in THEMES_DIR.glob("*.yaml"))


def active_theme_name() -> str:
    """Resolve the active theme: CV_THEME env var > active.yaml > default."""
    env = os.environ.get("CV_THEME")
    if env:
        return env
    if ACTIVE_FILE.exists():
        with ACTIVE_FILE.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if data.get("active"):
            return str(data["active"])
    return DEFAULT_THEME


def set_active_theme(name: str) -> None:
    """Persist the active theme name into theme/active.yaml."""
    if name not in list_themes():
        raise ValueError(f"Unknown theme {name!r}. Available: {', '.join(list_themes())}")
    ACTIVE_FILE.write_text(
        "# Which theme is active. Switch with `python -m src.cli theme use <name>`.\n"
        f"active: {name}\n",
        encoding="utf-8",
    )


def theme_path(name: str | None = None) -> Path:
    name = name or active_theme_name()
    path = THEMES_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Theme {name!r} not found at {path}. Available: {', '.join(list_themes())}"
        )
    return path


def load_theme(name: str | None = None) -> dict:
    with theme_path(name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def latex_color_defs(theme: dict | None = None) -> str:
    """Return ``\\definecolor{...}{RGB}{r,g,b}`` lines for every theme color."""
    theme = theme or load_theme()
    lines = []
    for name, hexval in theme["colors"].items():
        r, g, b = _hex_to_rgb(hexval)
        # LaTeX color names can't contain digits-only oddities; keep as-is (alpha).
        lines.append(f"\\definecolor{{{name}}}{{RGB}}{{{r},{g},{b}}}")
    return "\n".join(lines)


def font_families(theme: dict | None = None) -> dict[str, str]:
    """Return mapping role -> LaTeX/CSS family name (e.g. {'display': 'CormorantGaramond'})."""
    theme = theme or load_theme()
    return {role: spec["family"] for role, spec in theme["fonts"].items()}


def write_web_css(theme: dict | None = None) -> Path:
    """Generate the website's theme.css from the theme. Returns its path."""
    theme = theme or load_theme()
    colors = theme["colors"]
    fonts = theme["fonts"]
    web = theme.get("web", {})

    imports = []
    for spec in fonts.values():
        pkg = spec["web_package"]
        for w in spec["weights"]:
            imports.append(f"@import '@fontsource/{pkg}/{w}.css';")

    # Each color is emitted twice: `--name` for plain CSS use, and `--name-rgb`
    # (space-separated channels) so Tailwind can apply opacity modifiers via
    # `rgb(var(--name-rgb) / <alpha-value>)`. Tailwind reads the *variables*,
    # not baked values, so a theme switch only needs this file regenerated —
    # no Tailwind/dev-server restart.
    color_vars = "\n".join(
        f"  --{name}: #{hexval};\n  --{name}-rgb: {' '.join(str(c) for c in _hex_to_rgb(hexval))};"
        for name, hexval in colors.items()
    )
    display = fonts["display"].get("web_family", fonts["display"]["family"])
    text = fonts["text"].get("web_family", fonts["text"]["family"])
    # Generic fallback per font role (serif/sans-serif), declared by the theme.
    display_fallback = fonts["display"].get("fallback", "Georgia, serif")
    text_fallback = fonts["text"].get("fallback", "system-ui, sans-serif")

    css = f"""/* GENERATED from theme/themes/{theme.get('name', '?')}.yaml by `cv build-theme` — do not edit. */
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

    # Also emit a JSON token file Tailwind can import for color/font utilities.
    import json

    tokens = {
        "name": theme.get("name", "?"),
        "colors": {name: f"#{hexval}" for name, hexval in colors.items()},
        "fonts": {
            "display": display,
            "displayFallback": display_fallback,
            "text": text,
            "textFallback": text_fallback,
        },
        "web": {"maxWidth": web.get("max_width", "920px"), "radius": web.get("radius", "2px")},
    }
    (out.parent.parent / "theme.tokens.json").write_text(
        json.dumps(tokens, indent=2), encoding="utf-8"
    )
    return out
