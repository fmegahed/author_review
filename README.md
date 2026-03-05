# Author Factsheet Review

An evaluation tool for the [QE ArXiv Watch](https://huggingface.co/spaces/fmegahed/arxiv_control_charts) research pipeline, deployed at [author-review-production.up.railway.app](https://author-review-production.up.railway.app). This web app enables paper authors to review AI-generated factsheets extracted from their arXiv publications and report whether each extracted field is correct or incorrect.

## Motivation

[QE ArXiv Watch](https://huggingface.co/spaces/fmegahed/arxiv_control_charts) uses large language models to automatically extract structured factsheets from arXiv papers in three quality engineering research tracks: Statistical Process Control (SPC), Design of Experiments (DOE), and Reliability Engineering. To measure the accuracy of these extractions, we need ground-truth assessments from the paper authors themselves. This app collects those assessments.

Results will be reported in aggregate in an upcoming paper submitted to *Quality Engineering*.

## How It Works

An administrator searches for an author's papers across all three research tracks, generates a unique review link, and shares it with the author. The author opens the link and reviews 8 AI-extracted fields per paper:

| Common Fields (all tracks) | Track-Specific Fields |
|---|---|
| AI Summary | Varies by track (e.g., Chart Family, Design Type, Reliability Topic) |
| Key Results | Varies by track (e.g., Chart Statistic, Design Objective, Modeling Approach) |
| Key Equations (LaTeX rendered) | Varies by track (e.g., Phase, Optimality Criterion, Data Type) |
| Unstated Future Work | Varies by track (e.g., Application Domain, Number of Factors, Maintenance Policy) |

For each field, the author marks it as **Correct** or **Incorrect** and can optionally provide a comment. Reviews can be edited after submission.

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Jinja2
- **Database**: PostgreSQL
- **Data source**: CSVs from the [QE ArXiv Watch repository](https://github.com/fmegahed/hf_arxiv_control_charts/tree/main/data)
- **Styling**: Miami University theme with MathJax v3
- **Deployment**: [Railway](https://railway.app)

## Quick Start

```bash
cd apps/author_review
docker compose up --build
```

Open http://localhost:8000 and log in with password `changeme`.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for full local development instructions and [docs/RAILWAY-DEPLOYMENT.md](docs/RAILWAY-DEPLOYMENT.md) for production deployment.

## Project Structure

```
apps/author_review/
├── main.py              # FastAPI app entry point
├── config.py            # Track field mappings, environment config
├── database.py          # SQLAlchemy setup
├── models.py            # ORM models (review_tokens, paper_assignments, reviews)
├── data_loader.py       # CSV fetching/caching from GitHub
├── routes/
│   ├── admin.py         # Admin panel (search, token generation, export)
│   └── review.py        # Author review flow
├── templates/           # Jinja2 HTML templates
├── static/              # CSS, JS, logo
├── docs/                # Development and deployment guides
├── Dockerfile
├── docker-compose.yml
└── railway.toml
```

## Related

- **QE ArXiv Watch app**: https://huggingface.co/spaces/fmegahed/arxiv_control_charts
- **Source data**: https://github.com/fmegahed/hf_arxiv_control_charts

## License

This project is part of ongoing research at [Miami University](https://www.miamioh.edu). Please contact the authors before reuse.
