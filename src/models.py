"""Pydantic models: the contract between the ``data/`` files and every renderer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Contact(BaseModel):
    label: str
    value: str
    url: str | None = None
    icon: str | None = None
    cv: bool = True        # show on the PDF CV
    website: bool = True   # show on the website


class Profile(BaseModel):
    name: str
    suffix: str | None = None
    title: str
    tagline: str | None = None
    summary: str
    bio: str | None = None
    affiliation: str | None = None
    scholar_id: str | None = None
    contacts: list[Contact] = Field(default_factory=list)
    gdpr_authorization: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.name}, {self.suffix}" if self.suffix else self.name

    @property
    def bio_or_summary(self) -> str:
        return self.bio or self.summary


class Detail(BaseModel):
    label: str
    text: str


class Employment(BaseModel):
    role: str
    org: str
    location: str | None = None
    start: int
    end: int | Literal["present"]
    details: list[Detail] = Field(default_factory=list)

    @property
    def period(self) -> str:
        end = "present" if self.end == "present" else str(self.end)
        return f"{self.start}–{end}" if str(self.start) != end else str(self.start)


class Education(BaseModel):
    degree: str
    org: str
    location: str | None = None
    start: int
    end: int
    grade: str | None = None
    thesis: str | None = None

    @property
    def period(self) -> str:
        return f"{self.start}–{self.end}" if self.start != self.end else str(self.start)


class Teaching(BaseModel):
    role: str
    org: str
    year: int
    course: str
    degree: str | None = None  # course level, e.g. "MSc" / "BSc"
    hours: int | None = None
    note: str | None = None


class Award(BaseModel):
    title: str
    org: str | None = None
    year: int | None = None
    note: str | None = None


class Project(BaseModel):
    name: str
    full_name: str | None = None  # expanded title behind an acronym
    issuer: str                   # funding body / programme
    location: str | None = None
    role: str
    start: int
    end: int | Literal["present"]
    scope: str | None = None      # e.g. "European", "National"
    url: str | None = None
    description: str | None = None

    @property
    def period(self) -> str:
        end = "present" if self.end == "present" else str(self.end)
        return f"{self.start}–{end}" if str(self.start) != end else str(self.start)


class ResearchInterest(BaseModel):
    title: str
    description: str | None = None


class SkillGroup(BaseModel):
    category: str
    skills: list[str] = Field(default_factory=list)


class Talk(BaseModel):
    title: str
    event: str
    year: int
    location: str | None = None
    kind: str | None = None  # e.g. "Invited talk", "Seminar"
    url: str | None = None


class Supervision(BaseModel):
    student: str
    degree: str  # e.g. "MSc thesis"
    title: str
    year: int | None = None
    role: str | None = None  # e.g. "Co-advisor"


PubKind = Literal["journal", "conference", "workshop", "preprint"]


class Publication(BaseModel):
    key: str
    kind: PubKind
    title: str
    authors: list[str]
    year: int
    venue: str | None = None
    volume: str | None = None
    pages: str | None = None
    doi: str | None = None
    arxiv: str | None = None
    keywords: list[str] = Field(default_factory=list)
    bibtex: str | None = None      # raw BibTeX entry
    citations: int | None = None   # from scholar_cache.json
    selected: bool = False         # featured on the website (bib field `selected = {true}`)

    @property
    def url(self) -> str | None:
        if self.doi:
            return f"https://doi.org/{self.doi}"
        if self.arxiv:
            return f"https://arxiv.org/abs/{self.arxiv}"
        return None


class ScholarMetrics(BaseModel):
    h_index: int | None = None
    i10_index: int | None = None
    total_citations: int | None = None
    scholar_id: str | None = None
    fetched_at: str | None = None


class CVData(BaseModel):
    profile: Profile
    research_interests: list[ResearchInterest] = Field(default_factory=list)
    skills: list[SkillGroup] = Field(default_factory=list)
    employment: list[Employment] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    teaching: list[Teaching] = Field(default_factory=list)
    talks: list[Talk] = Field(default_factory=list)
    supervision: list[Supervision] = Field(default_factory=list)
    awards: list[Award] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    publications: list[Publication] = Field(default_factory=list)
    metrics: ScholarMetrics | None = None
