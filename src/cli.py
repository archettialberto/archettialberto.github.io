"""`cv` command-line entry point."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import typer

from .loader import ROOT, load
from .render_cv import BUILD_DIR, render

app = typer.Typer(add_completion=False, help="Build the CV and website from data/.")


@app.command()
def data() -> None:
    """Validate the data layer and print a summary."""
    d = load()
    typer.echo(f"Profile     : {d.profile.full_name} — {d.profile.title}")
    typer.echo(f"Employment  : {len(d.employment)}")
    typer.echo(f"Education   : {len(d.education)}")
    typer.echo(f"Teaching    : {len(d.teaching)}")
    typer.echo(f"Awards      : {len(d.awards)}")
    typer.echo(f"Projects    : {len(d.projects)}")
    typer.echo(f"Publications: {len(d.publications)}")
    if d.metrics:
        typer.echo(f"Metrics     : h-index {d.metrics.h_index}, citations {d.metrics.total_citations}")
    typer.secho("OK — data validates.", fg=typer.colors.GREEN)


@app.command("build-cv")
def build_cv(
    compile_pdf: bool = typer.Option(True, "--compile/--no-compile", help="Run xelatex if available."),
) -> None:
    """Render the CV to LaTeX and compile to PDF if xelatex is installed."""
    d = load()
    tex = render(d)
    typer.secho(f"Wrote {tex.relative_to(ROOT)}", fg=typer.colors.GREEN)

    xelatex = shutil.which("xelatex")
    if not compile_pdf or not xelatex:
        if compile_pdf and not xelatex:
            typer.secho("xelatex not found — emitted .tex only.", fg=typer.colors.YELLOW)
        return
    _compile(tex, surname=d.profile.name.split()[-1].lower())


@app.command("build-site")
def build_site() -> None:
    """Export site.json + theme.css for the Astro website."""
    from .theme import write_web_css

    d = load()
    out = ROOT / "website" / "src" / "data" / "site.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(d.model_dump_json(indent=2), encoding="utf-8")
    typer.secho(f"Wrote {out.relative_to(ROOT)}", fg=typer.colors.GREEN)

    css = write_web_css()
    typer.secho(f"Wrote {css.relative_to(ROOT)}", fg=typer.colors.GREEN)


@app.command()
def scholar() -> None:
    """Fetch Scholar metrics (ID from profile.yaml) into scholar_cache.json and
    append new publications to publications.bib; existing entries are never changed."""
    from .scholar import append_new_publications, fetch_scholar

    scholar_id = load().profile.scholar_id
    if not scholar_id:
        typer.secho("No scholar_id set in data/profile.yaml.", fg=typer.colors.RED)
        raise typer.Exit(1)

    data = fetch_scholar(scholar_id)
    pubs = data.pop("publications", [])
    out = ROOT / "data" / "scholar_cache.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    typer.secho(f"Wrote {out.relative_to(ROOT)}", fg=typer.colors.GREEN)

    bib = ROOT / "data" / "publications.bib"
    added = append_new_publications(pubs, bib)
    if added:
        typer.secho(f"Added {len(added)} new publication(s) to {bib.relative_to(ROOT)}:",
                    fg=typer.colors.GREEN)
        for k in added:
            typer.echo(f"  + {k}")
        typer.secho("Review the new entries by hand.", fg=typer.colors.YELLOW)
    else:
        typer.echo("No new publications.")


def _compile(tex: Path, surname: str) -> None:
    # Run twice so cross-references settle.
    cmd = ["xelatex", "-interaction=nonstopmode", "-shell-escape", tex.name]
    typer.echo(f"Compiling: {' '.join(cmd)}  (cwd={BUILD_DIR})")
    res = None
    for _ in range(2):
        res = subprocess.run(cmd, cwd=BUILD_DIR, capture_output=True, text=True, check=False)

    # xelatex exits nonzero on harmless warnings, so trust the PDF's presence.
    pdf = (BUILD_DIR / tex.stem).with_suffix(".pdf")
    if not pdf.exists():
        typer.secho("xelatex failed; tail of log:", fg=typer.colors.RED)
        typer.echo("\n".join((res.stdout if res else "").splitlines()[-25:]))
        raise typer.Exit(1)
    typer.secho(f"PDF: {pdf.relative_to(ROOT)}", fg=typer.colors.GREEN)

    published = ROOT / "website" / "public" / "cv" / f"{surname}-cv.pdf"
    published.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, published)
    typer.secho(f"Published: {published.relative_to(ROOT)}", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
