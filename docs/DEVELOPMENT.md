# Author Factsheet Review App

A web app for paper authors to review AI-generated factsheets extracted by the [QE ArXiv Watch](https://huggingface.co/spaces/fmegahed/arxiv_control_charts) pipeline. Authors receive a unique link, review 8 questions per paper (correct/incorrect + optional comments), and their responses are collected to measure extraction accuracy for the academic paper.

## Tech Stack

- **Backend**: Python 3.12, FastAPI, Jinja2 (server-side rendered)
- **Database**: PostgreSQL 16
- **Data source**: CSVs fetched from [GitHub](https://github.com/fmegahed/hf_arxiv_control_charts/tree/main/data) (cached in-memory, 1hr TTL)
- **Styling**: Miami University theme with MathJax v3 for LaTeX rendering
- **Deployment**: Railway (Dockerfile)

## How It Works

```
Admin Panel                          Author Review Flow
─────────────                        ──────────────────
1. Admin logs in                     1. Author clicks unique URL
2. Searches for author by name       2. Sees welcome page with paper count
3. Selects papers across tracks      3. Reviews each paper (8 questions):
4. Generates unique review URL          - AI Summary
5. Shares URL with the author          - Key Results
                                        - Key Equations (MathJax rendered)
                                        - Unstated Future Work
                                        + 4 track-specific fields
                                     4. Submits correct/incorrect + comments
                                     5. Can revisit and edit anytime
```

### Tracks & Track-Specific Fields

| Track | Field 1 | Field 2 | Field 3 | Field 4 |
|-------|---------|---------|---------|---------|
| **SPC** (Control Charts) | Chart Family | Chart Statistic | Phase | Application Domain |
| **DOE** (Experimental Design) | Design Type | Design Objective | Optimality Criterion | Number of Factors |
| **Reliability** | Reliability Topic | Modeling Approach | Data Type | Maintenance Policy |

## Local Development

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose

### Run with Docker Compose

```bash
cd apps/author_review
docker compose up --build
```

This starts:
- **PostgreSQL 16** on port 5432
- **FastAPI app** on port 8000

Open http://localhost:8000 (redirects to admin login) and log in with password `changeme`.

The app waits for PostgreSQL to be fully ready (via healthcheck) before starting, so there are no race conditions on fresh volumes.

### Stopping

```bash
docker compose down        # stop containers, keep data
docker compose down -v     # stop containers and delete database volume
```

### Resetting the Database

To wipe all data and start fresh:

```bash
docker compose down -v
docker compose up --build
```

If the volume doesn't get removed (can happen on Windows), force it:

```cmd
docker compose down
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm <volume_name>
docker compose up --build
```

Find the volume name with `docker volume ls` — it's typically `author_review_pgdata` or `authorreview_pgdata` depending on your Docker Compose version.

### Environment Variables

Copy `.env.example` for reference. When using Docker Compose, these are already set in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@db:5432/author_review` |
| `ADMIN_PASSWORD` | Password for `/admin` panel | `changeme` |
| `SECRET_KEY` | Signs session cookies (use a random string in prod) | `dev-secret-key-change-in-production` |
| `BASE_URL` | Public URL for generating review links (no trailing slash) | `http://localhost:8000` |

### Run Without Docker

```bash
cd apps/author_review
pip install -r requirements.txt

# Start a local PostgreSQL, then:
export DATABASE_URL="postgresql://user:pass@localhost:5432/author_review"
export ADMIN_PASSWORD="your-password"
export SECRET_KEY="some-random-secret"
export BASE_URL="http://localhost:8000"

uvicorn main:app --reload --port 8000
```

## Deploying to Railway

### 1. Create the Project

1. Go to [railway.app](https://railway.app) and create a new project
2. Add a **PostgreSQL** database (click "New" → "Database" → "PostgreSQL")
3. Add a new **Service** from your GitHub repo:
   - Set the **Root Directory** to `apps/author_review`
   - Railway will detect the `Dockerfile` automatically

### 2. Configure Environment Variables

In the service's **Variables** tab, add:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (click "Add Reference" → select your Postgres) |
| `ADMIN_PASSWORD` | A strong password |
| `SECRET_KEY` | A random string (e.g., run `python -c "import secrets; print(secrets.token_hex(32))"`) |
| `BASE_URL` | Your Railway public URL, e.g., `https://your-app.up.railway.app` (no trailing slash) |

### 3. Deploy

Railway deploys automatically on push. To trigger manually:
- Click **Deploy** in the Railway dashboard, or
- Push to the branch connected to your Railway service

### 4. Verify

- Visit `https://your-app.up.railway.app/health` — should return `{"status": "ok"}`
- Visit `https://your-app.up.railway.app/admin/login` — log in with your admin password
- Database tables are created automatically on first startup

## Usage

### Admin Workflow

1. **Login** at `/admin/login`
2. **Search** for an author name (e.g., "Fadel M. Megahed") — searches all 3 tracks
3. **Select papers** to include (all checked by default) and enter the author's email
4. **Generate token** — produces a unique review URL
5. **Share the URL** with the author (copy button provided)
6. **Monitor progress** at `/admin/tokens` — shows review completion per token
7. **Export results** at `/admin/export` — downloads all reviews as CSV
8. **Refresh CSV cache** if source data has been updated

### Author Workflow

1. Open the review URL received from the admin
2. Click **Start Reviewing**
3. For each paper, read the AI-extracted content and mark each field as **Correct** (green) or **Incorrect** (yellow)
4. Optionally add comments explaining what's wrong (comment box auto-opens when "Incorrect" is selected)
5. Submit to advance to the next paper
6. After all papers: thank-you page with option to revisit/edit

### Export Format

The CSV export includes columns:
```
arxiv_id, track, author_name, author_email, submitted_at,
summary_correct, summary_comment,
key_results_correct, key_results_comment,
key_equations_correct, key_equations_comment,
future_work_unstated_correct, future_work_unstated_comment,
track_field_1_name, track_field_1_correct, track_field_1_comment,
track_field_2_name, track_field_2_correct, track_field_2_comment,
track_field_3_name, track_field_3_correct, track_field_3_comment,
track_field_4_name, track_field_4_correct, track_field_4_comment
```

## Project Structure

```
apps/author_review/
├── main.py                 # FastAPI app entry point
├── config.py               # Environment variables, track field mappings
├── database.py             # SQLAlchemy engine/session
├── models.py               # ORM models (3 tables)
├── schemas.py              # Pydantic validation models
├── data_loader.py          # CSV fetching/caching from GitHub
├── routes/
│   ├── admin.py            # Admin panel (login, search, tokens, export)
│   └── review.py           # Author review flow (form, submit, navigation)
├── templates/
│   ├── base.html           # Base layout with Miami header + MathJax
│   ├── admin/              # login, dashboard, tokens
│   └── review/             # landing, paper form, list, thank_you, invalid_token
├── assets/
│   └── logo.jpg            # Miami University logo (source)
├── static/
│   ├── miami-theme.css     # Miami University theme
│   ├── logo.jpg            # Logo used as favicon and header image
│   └── review.js           # Client-side interactions
├── Dockerfile
├── docker-compose.yml      # Local dev (app + PostgreSQL)
├── railway.toml            # Railway deployment config
├── requirements.txt
└── .env.example
```
