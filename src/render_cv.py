"""Render the CV LaTeX from :class:`CVData` via Jinja2.

Jinja's default delimiters clash with LaTeX, so templates use
``\\VAR{ }`` (expressions), ``\\BLOCK{ }`` (statements), ``#= =#`` (comments).
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import jinja2

from .loader import ROOT
from .models import CVData
from .theme import font_families, latex_color_defs, load_theme

CV_DIR = ROOT / "cv"
TEMPLATE_DIR = CV_DIR / "templates"
FONTS_DIR = CV_DIR / "fonts"
BUILD_DIR = CV_DIR / "build"

_TEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex_escape(value: object) -> str:
    result = "".join(_TEX_REPLACEMENTS.get(ch, ch) for ch in str(value))
    # Keep -- and --- from becoming en/em-dash ligatures.
    return result.replace("---", "{-}{-}{-}").replace("--", "{-}{-}")


_STRONG_RE = re.compile(r"<strong>(.*?)</strong>", re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def html_to_tex(value: object) -> str:
    """<strong> -> \\textbf, strip other tags, escape the rest."""
    parts = _STRONG_RE.split(str(value).strip())
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out.append(tex_escape(_TAG_RE.sub("", part)))
        else:
            out.append(r"\textbf{" + tex_escape(part) + "}")
    return "".join(out)


def _env() -> jinja2.Environment:
    env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string="#=",
        comment_end_string="=#",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
    )
    env.filters["tex"] = tex_escape
    env.filters["htmltex"] = html_to_tex
    return env


def render(data: CVData, template: str = "cv") -> Path:
    """Render ``<template>.tex.j2`` to ``cv/build/<template>.tex`` and return its path."""
    # Make the build dir self-contained so a plain `xelatex cv` works.
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    _sync_dir(FONTS_DIR, BUILD_DIR / "fonts")

    theme = load_theme()
    fams = font_families(theme)
    disp = theme["fonts"]["display"]["latex"]
    txt = theme["fonts"]["text"]["latex"]
    theme_ctx = {
        "color_defs": latex_color_defs(theme),
        "font_display": fams["display"],
        "font_text": fams["text"],
        "face_display_upright": disp["upright"],
        "face_display_bold": disp["bold"],
        "face_display_title": disp["title"],
        "face_display_title_bold": disp["title_bold"],
        "face_text_upright": txt["upright"],
        "face_text_bold": txt["bold"],
        "face_text_italic": txt["italic"],
        "face_text_medium": txt["medium"],
        "face_text_medium_bold": txt["medium_bold"],
        "display_letterspace": theme["fonts"]["display"]["letterspace"],
        "fonts_path": "fonts",
    }

    _render_to(_env(), "_preamble.tex.j2", BUILD_DIR / "_preamble.tex", **theme_ctx)

    out = BUILD_DIR / f"{template}.tex"
    _render_to(
        _env(),
        f"{template}.tex.j2",
        out,
        profile=data.profile,
        research_interests=data.research_interests,
        skills=data.skills,
        employment=data.employment,
        education=data.education,
        courses=data.courses,
        talks=data.talks,
        supervision=data.supervision,
        awards=data.awards,
        projects=data.projects,
        publications=data.publications,
        metrics=data.metrics,
        **theme_ctx,
    )
    return out


def _render_to(env: jinja2.Environment, template_name: str, dest: Path, **ctx: object) -> None:
    dest.write_text(env.get_template(template_name).render(**ctx), encoding="utf-8")


def _sync_dir(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.glob("*.ttf"):
        target = dst / f.name
        if not target.exists() or target.stat().st_mtime < f.stat().st_mtime:
            shutil.copy2(f, target)
