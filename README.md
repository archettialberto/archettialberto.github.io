### Hi, I'm Alberto 👋

Postdoctoral Researcher in AI at **AIRLab, Politecnico di Milano**.

I work on **tabular foundation models**, **federated learning**, and **survival analysis** — building models that learn from private, distributed healthcare data.

🌐 [archettialberto.github.io](https://archettialberto.github.io) ·
🎓 [Google Scholar](https://scholar.google.com/citations?user=--kj4bcAAAAJ&hl=en) ·
💼 [LinkedIn](https://www.linkedin.com/in/albertoarchetti/) ·
📫 [alberto.archetti@polimi.it](mailto:alberto.archetti@polimi.it)

---

## Guide

This repo builds my CV (LaTeX → PDF) and website (Astro) from a single source of truth: the `data/` directory.

### Where to edit

| What | File |
|---|---|
| Name, title, bio, links, Scholar ID | `data/profile.yaml` |
| Publications | `data/publications.bib` — `selected = {true}` features an entry on the website; keyword `ignore` hides it |
| Employment, education, teaching, talks, projects, … | the other `data/*.yaml` files |
| Colors & fonts (CV **and** website) | `theme/theme.yaml` |

### Setup (once)

Needs conda, Node, and TeX Live (`xelatex`):

```bash
conda env create -f environment.yaml && conda activate cv
make install
```

### Everyday use

```bash
make scholar   # refresh citation metrics + pull new publications into the .bib (review by hand)
make build     # CV PDF → website/public/cv/, site.json + theme.css → website/
make dev       # build, then preview the website offline at http://localhost:4321/
```

### Publish

```bash
git add -A && git commit -m "Update CV" && git push
```

Pushing to `main` deploys to GitHub Pages. **CI only runs `npm run build`** — it does not regenerate data or PDFs, so commit the generated files (`website/src/data/site.json`, `website/src/styles/theme.css`, `website/public/cv/archetti-cv.pdf`) along with your changes; `make build` keeps them current.
