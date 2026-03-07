# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A FastAPI web app that lets paper authors review AI-generated factsheets extracted by the [QE ArXiv Watch](https://huggingface.co/spaces/fmegahed/arxiv_control_charts) pipeline. Admins search for authors, generate unique review links, and authors rate each extracted field on a 1-5 Likert scale (Completely Incorrect to Completely Correct). Results are exported as CSV for accuracy measurement in an academic paper submitted to *Quality Engineering*.

## Running Locally

```bash
# Docker Compose (recommended) — starts PostgreSQL 16 + FastAPI app
docker compose up --build
# App at http://localhost:8000, admin password: changeme

# Without Docker
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:pass@localhost:5432/author_review"
uvicorn main:app --reload --port 8000
```

## Deployment

Deployed to Railway via Dockerfile. Redeploy with `railway up` from this directory. See `docs/RAILWAY-DEPLOYMENT.md` for full setup.

Required env vars: `DATABASE_URL`, `ADMIN_PASSWORD`, `SECRET_KEY`, `BASE_URL` (no trailing slash).

## Architecture

**Server-side rendered** FastAPI app with Jinja2 templates. No frontend build step.

### Data Flow

1. **CSV source**: Metadata and factsheet CSVs fetched from GitHub (`data_loader.py`), cached in-memory with 1hr TTL. Admin can refresh cache at `/admin/refresh-cache`.
2. **Admin creates review token**: Searches author name across all 3 tracks, selects papers, generates a UUID-based review URL (`routes/admin.py`).
3. **Author reviews**: Opens URL, reviews 8 fields per paper (4 common + 4 track-specific), rates each 1-5 + optional comments (`routes/review.py`). Admin search has client-side autocomplete from preloaded author names.
4. **Export**: Admin downloads all reviews as CSV at `/admin/export`.

### Key Modules

- `config.py` — Track definitions, field mappings (common fields + per-track fields), env vars
- `models.py` — 3 SQLAlchemy models: `ReviewToken` → `PaperAssignment` → `Review` (1:many:1). Review fields use `_rating` Integer columns (1-5), not Boolean.
- `data_loader.py` — Fetches/caches CSVs from GitHub, merges metadata+factsheet, formats pipe-delimited fields into sentences
- `schemas.py` — Pydantic models for form validation
- `routes/admin.py` — Cookie-based auth (signed with `itsdangerous`), search, token CRUD, CSV export
- `routes/review.py` — Token validation, paper review form, submit/update flow, progress tracking

### Track System

Three research tracks with 4 track-specific fields each, configured in `TRACKS` and `TRACK_FIELD_MAPPINGS` in `config.py`:

| Track | Key | Track Fields |
|-------|-----|-------------|
| Control Charts | `spc` | chart_family, chart_statistic, phase, application_domain |
| Experimental Design | `exp_design` | design_type, design_objective, optimality_criterion, number_of_factors |
| Reliability | `reliability` | reliability_topic, modeling_approach, data_type, maintenance_policy |

Adding a track requires updating both `TRACKS` and `TRACK_FIELD_MAPPINGS` in `config.py`. The review form dynamically adapts — no template changes needed.

### Database

PostgreSQL with SQLAlchemy (synchronous). Tables auto-created on startup with retry logic (`main.py` lifespan). DB session via `get_db()` generator in `database.py`.

### Templates

Markdown rendered client-side via marked.js + DOMPurify, LaTeX via MathJax v3 — both applied to all `.field-value` elements. Miami University branded theme (`static/miami-theme.css`). Base template at `templates/base.html`.
