"""Load and validate the ``data/`` directory into a :class:`CVData` object."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import bibtexparser
import yaml
from bibtexparser.bibdatabase import BibDatabase
from bibtexparser.bwriter import BibTexWriter

from .models import (
    Award,
    Course,
    CVData,
    Education,
    Employment,
    News,
    Profile,
    Project,
    Publication,
    ResearchInterest,
    ScholarMetrics,
    SkillGroup,
    Supervision,
    Talk,
    Teaching,
)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def _load_yaml(name: str, i18n: dict[str, str]) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return _localize(yaml.safe_load(fh), i18n)


def _localize(node: Any, i18n: dict[str, str]) -> Any:
    """Resolve every ``{en: ..., it: ...}`` to its English text (what the CV and
    models see), recording the Italian in ``i18n`` for the website."""
    if isinstance(node, dict):
        if set(node) == {"en", "it"}:
            i18n[node["en"]] = node["it"]
            return node["en"]
        return {k: _localize(v, i18n) for k, v in node.items()}
    if isinstance(node, list):
        return [_localize(v, i18n) for v in node]
    return node


def _classify(entry_type: str, keywords: list[str], arxiv: str | None) -> str:
    if "workshop" in keywords:
        return "workshop"
    if entry_type == "article":
        return "journal"
    if entry_type in {"misc", "unpublished"} or arxiv:
        return "preprint"
    return "conference"


def _split_authors(raw: str) -> list[str]:
    return [re.sub(r"\s+", " ", a).strip() for a in raw.split(" and ") if a.strip()]


def _parse_publications() -> list[Publication]:
    bib_path = DATA_DIR / "publications.bib"
    if not bib_path.exists():
        return []

    with bib_path.open(encoding="utf-8") as fh:
        db = bibtexparser.load(fh)

    writer = BibTexWriter()
    writer.indent = "  "

    def _entry_bibtex(entry: dict) -> str:
        # Build-control fields are noise in a copied citation.
        single = BibDatabase()
        single.entries = [{k: v for k, v in entry.items() if k not in {"selected", "keywords"}}]
        return writer.write(single).strip()

    pubs: list[Publication] = []
    for e in db.entries:
        keywords = [k.strip() for k in e.get("keywords", "").split(",") if k.strip()]
        if "ignore" in keywords:
            continue
        arxiv = e.get("eprint") if e.get("archiveprefix", "").lower() == "arxiv" else None
        venue = e.get("journal") or e.get("booktitle") or e.get("howpublished")
        pubs.append(
            Publication(
                key=e["ID"],
                kind=_classify(e.get("ENTRYTYPE", ""), keywords, arxiv),
                title=re.sub(r"[{}]", "", e.get("title", "")).strip(),
                authors=_split_authors(e.get("author", "")),
                year=int(e.get("year", 0)),
                venue=venue,
                volume=e.get("volume"),
                pages=e.get("pages"),
                doi=e.get("doi"),
                arxiv=arxiv,
                keywords=keywords,
                bibtex=_entry_bibtex(e),
                selected=e.get("selected", "").strip().lower() in {"true", "yes", "1"},
            )
        )
    pubs.sort(key=lambda p: p.year, reverse=True)
    return pubs


def _group_courses(teaching: list[Teaching]) -> list[Course]:
    """One entry per (course, org), latest edition first."""
    groups: dict[tuple[str, str], list[Teaching]] = {}
    for t in teaching:
        groups.setdefault((t.course, t.org), []).append(t)
    courses = []
    for eds in groups.values():
        eds.sort(key=lambda t: t.year, reverse=True)
        roles = list(dict.fromkeys(t.role for t in eds))
        courses.append(Course(
            course=eds[0].course, org=eds[0].org, role=" / ".join(roles), degree=eds[0].degree,
            start=eds[-1].year, end=eds[0].year, editions=len(eds),
            hours=sum(t.hours or 0 for t in eds),
        ))
    return sorted(courses, key=lambda c: (c.end, c.start), reverse=True)


def _merge_scholar(pubs: list[Publication]) -> ScholarMetrics | None:
    cache = DATA_DIR / "scholar_cache.json"
    if not cache.exists():
        return None
    data = json.loads(cache.read_text(encoding="utf-8"))

    by_title = {
        re.sub(r"\W+", "", t).lower(): c
        for t, c in data.get("citations_by_title", {}).items()
    }
    for p in pubs:
        p.citations = by_title.get(re.sub(r"\W+", "", p.title).lower())

    m = data.get("metrics", {})
    return ScholarMetrics(**m) if m else None


def load() -> CVData:
    """Load, validate, and return all career data."""
    i18n: dict[str, str] = {}

    def items(name: str, model: type) -> list:
        return [model.model_validate(x) for x in (_load_yaml(name, i18n) or [])]

    profile = Profile.model_validate(_load_yaml("profile.yaml", i18n) or {})
    research = items("research_interests.yaml", ResearchInterest)
    skills = items("skills.yaml", SkillGroup)
    employment = items("employment.yaml", Employment)
    education = items("education.yaml", Education)
    teaching = items("teaching.yaml", Teaching)
    talks = items("talks.yaml", Talk)
    supervision = items("supervision.yaml", Supervision)
    awards = items("awards.yaml", Award)
    projects = items("projects.yaml", Project)
    news = sorted(items("news.yaml", News), key=lambda n: n.date, reverse=True)
    publications = _parse_publications()
    metrics = _merge_scholar(publications)
    # Glossary for recurring terms; inline {en, it} pairs take precedence.
    i18n = {**(_load_yaml("it.yaml", i18n) or {}), **i18n}

    return CVData(
        profile=profile,
        research_interests=research,
        skills=skills,
        employment=employment,
        education=education,
        teaching=teaching,
        courses=_group_courses(teaching),
        talks=talks,
        supervision=supervision,
        awards=awards,
        projects=projects,
        publications=publications,
        metrics=metrics,
        news=news,
        i18n=i18n,
    )
