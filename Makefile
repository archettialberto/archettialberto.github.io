# Single entry point for every task; personal info lives in data/profile.yaml.

.PHONY: help install scholar build dev

help:
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

install:  ## install Python + website dependencies (activate the 'cv' conda env first)
	poetry install
	npm --prefix website install

scholar:  ## refresh Google Scholar metrics + pull new publications into the .bib
	cv scholar

build:  ## build the CV PDF and export site.json + theme.css for the website
	cv build-cv
	cv build-site

dev: build  ## build, then preview the website offline at http://localhost:4321/
	npm --prefix website run dev
