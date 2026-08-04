"""Google Scholar sync via ``scholarly`` (unofficial scraper — may be rate-limited)."""

from __future__ import annotations

import re
from datetime import datetime, timezone


def _norm(title: str) -> str:
    return re.sub(r"\W+", "", title or "").lower()


def _bibkey(authors: str, year: str, title: str) -> str:
    first = re.split(r"\s+and\s+|,", authors or "x")[0].strip().split()[-1:] or ["pub"]
    word = re.sub(r"\W+", "", (title or "x").split()[0]).lower() or "pub"
    return f"{first[0].lower()}{year or ''}{word}"


def _entry_type(venue: str) -> tuple[str, str]:
    v = (venue or "").lower()
    if any(w in v for w in ("journal", "transactions", "letters")):
        return "article", "journal"
    if "arxiv" in v:
        return "misc", "note"
    return "inproceedings", "booktitle"


def fetch_scholar(scholar_id: str) -> dict:
    """Return {metrics, citations_by_title, publications: [bib dicts]}."""
    from scholarly import scholarly

    author = scholarly.search_author_id(scholar_id)
    author = scholarly.fill(author, sections=["basics", "indices", "publications"])

    citations_by_title: dict[str, int] = {}
    pubs: list[dict] = []
    for pub in author.get("publications", []):
        filled = scholarly.fill(pub)  # summary bib lacks author+venue
        bib = filled.get("bib", {})
        title = bib.get("title")
        if not title:
            continue
        cites = filled.get("num_citations")
        if cites is not None:
            citations_by_title[title] = int(cites)
        year = str(bib.get("pub_year", "")).strip()
        authors = bib.get("author", "")
        venue = bib.get("venue") or bib.get("journal") or bib.get("conference") or ""
        etype, field = _entry_type(venue)
        arxiv = re.search(r"arxiv[:\s/]*(\d{4}\.\d{4,5})", venue, re.I)
        pubs.append({
            "key": _bibkey(authors, year, title),
            "type": etype,
            "field": field,
            "title": title,
            "authors": authors,
            "year": year,
            "venue": venue,
            "arxiv": arxiv.group(1) if arxiv else None,
        })

    return {
        "metrics": {
            "h_index": author.get("hindex"),
            "i10_index": author.get("i10index"),
            "total_citations": author.get("citedby"),
            "scholar_id": scholar_id,
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "citations_by_title": citations_by_title,
        "publications": pubs,
    }


def append_new_publications(pubs: list[dict], bib_path) -> list[str]:
    """Append Scholar pubs whose title isn't already in the .bib. Returns added keys."""
    existing = bib_path.read_text(encoding="utf-8") if bib_path.exists() else ""
    existing_titles = {_norm(t) for t in re.findall(r"title\s*=\s*[{\"](.+?)[}\"]", existing)}

    added: list[str] = []
    blocks: list[str] = []
    for p in pubs:
        if _norm(p["title"]) in existing_titles:
            continue
        existing_titles.add(_norm(p["title"]))
        if p.get("arxiv"):
            venue_lines = (f"  eprint    = {{{p['arxiv']}}},\n"
                           f"  archiveprefix = {{arXiv}},\n")
        else:
            venue_lines = f"  {p['field']:9} = {{{p['venue']}}},\n"
        blocks.append(
            f"\n@{p['type']}{{{p['key']},\n"
            f"  author    = {{{p['authors']}}},\n"
            f"  title     = {{{p['title']}}},\n"
            f"{venue_lines}"
            f"  year      = {{{p['year']}}},\n"
            f"}}\n"
        )
        added.append(p["key"])

    if blocks:
        header = "" if existing.endswith("\n") or not existing else "\n"
        bib_path.write_text(existing + header + "".join(blocks), encoding="utf-8")
    return added
