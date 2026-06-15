"""Load and validate the ``data/`` directory into a :class:`CVData` object.

This is the single ingestion point. YAML sections are loaded directly; the
``.bib`` is parsed and classified into journal/conference/workshop/preprint.
An optional ``scholar_cache.json`` (written by the opt-in Scholar fetch) is
merged in for citation counts and h-index — its absence is not an error.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from .models import (
    Award,
    CVData,
    Education,
    Employment,
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

# Repo root = parent of src/
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def _load_yaml(name: str) -> object:
    path = DATA_DIR / name
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _classify(entry_type: str, keywords: list[str], arxiv: str | None) -> str:
    if "workshop" in keywords:
        return "workshop"
    if entry_type == "article":
        return "journal"
    if entry_type in {"misc", "unpublished"} or arxiv:
        return "preprint"
    return "conference"


def _split_authors(raw: str) -> list[str]:
    # bibtexparser leaves "and"-separated names; normalise whitespace.
    return [re.sub(r"\s+", " ", a).strip() for a in raw.split(" and ") if a.strip()]


def _parse_publications() -> list[Publication]:
    bib_path = DATA_DIR / "publications.bib"
    if not bib_path.exists():
        return []

    import bibtexparser  # local import keeps loader importable without the dep
    from bibtexparser.bwriter import BibTexWriter
    from bibtexparser.bibdatabase import BibDatabase

    with bib_path.open(encoding="utf-8") as fh:
        db = bibtexparser.load(fh)

    writer = BibTexWriter()
    writer.indent = "  "

    def _entry_bibtex(entry: dict) -> str:
        single = BibDatabase()
        single.entries = [entry]
        return writer.write(single).strip()

    pubs: list[Publication] = []
    for e in db.entries:
        keywords = [k.strip() for k in e.get("keywords", "").split(",") if k.strip()]
        if "ignore" in keywords:
            continue  # kept in the .bib (e.g. after a Scholar fetch) but not rendered
        arxiv = e.get("eprint") if e.get("archiveprefix", "").lower() == "arxiv" else None
        venue = e.get("journal") or e.get("booktitle")
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
    # Most recent first; stable within a year by reverse insertion order.
    pubs.sort(key=lambda p: p.year, reverse=True)
    return pubs


def _merge_scholar(pubs: list[Publication]) -> ScholarMetrics | None:
    cache = DATA_DIR / "scholar_cache.json"
    if not cache.exists():
        return None
    data = json.loads(cache.read_text(encoding="utf-8"))

    # citations keyed by bib key OR by normalised title
    by_key = data.get("citations_by_key", {})
    by_title = {
        re.sub(r"\W+", "", t).lower(): c
        for t, c in data.get("citations_by_title", {}).items()
    }
    for p in pubs:
        if p.key in by_key:
            p.citations = by_key[p.key]
        else:
            p.citations = by_title.get(re.sub(r"\W+", "", p.title).lower())

    m = data.get("metrics", {})
    return ScholarMetrics(**m) if m else None


def load() -> CVData:
    """Load, validate, and return all career data."""
    profile = Profile.model_validate(_load_yaml("profile.yaml") or {})
    research = [ResearchInterest.model_validate(x) for x in (_load_yaml("research_interests.yaml") or [])]
    skills = [SkillGroup.model_validate(x) for x in (_load_yaml("skills.yaml") or [])]
    employment = [Employment.model_validate(x) for x in (_load_yaml("employment.yaml") or [])]
    education = [Education.model_validate(x) for x in (_load_yaml("education.yaml") or [])]
    teaching = [Teaching.model_validate(x) for x in (_load_yaml("teaching.yaml") or [])]
    talks = [Talk.model_validate(x) for x in (_load_yaml("talks.yaml") or [])]
    supervision = [Supervision.model_validate(x) for x in (_load_yaml("supervision.yaml") or [])]
    awards = [Award.model_validate(x) for x in (_load_yaml("awards.yaml") or [])]
    projects = [Project.model_validate(x) for x in (_load_yaml("projects.yaml") or [])]
    publications = _parse_publications()
    metrics = _merge_scholar(publications)

    return CVData(
        profile=profile,
        research_interests=research,
        skills=skills,
        employment=employment,
        education=education,
        teaching=teaching,
        talks=talks,
        supervision=supervision,
        awards=awards,
        projects=projects,
        publications=publications,
        metrics=metrics,
    )
