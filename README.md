# Remote Job Aggregator (RemoteJobHub)

A full-stack remote job aggregator that filters, deduplicates, and enriches job postings from multiple ATS and job-board sources. Built to surface only **truly remote** roles (no hybrid/on-site), with salary transparency, instant search, saved jobs, and customizable job alerts.

> 📖 **Documentation:** See [`docs/WORKFLOW.md`](docs/WORKFLOW.md) for the full system architecture, data-ingestion pipeline, and end-to-end flow.

---

## Features

- **Pure Remote Filter** — Only shows jobs that are 100% remote. No "hybrid" or "occasional office visits."
- **Geo-Fencing / Time-Zone Filter** — Filter by "Remote in USA," "Remote in Europe," "Remote Global," or specific time zones.
- **Deduplication Engine** — The same job posted across multiple boards is shown only once.
- **Salary Transparency** — AI-powered salary estimation when a posting doesn't disclose one.
- **Instant Search** — Typeahead/autocomplete search for skills like "React," "DevOps," "Customer Support."
- **Saved Jobs & Hide** — Users can save jobs, add notes, and hide jobs/companies they don't want to see.
- **Job Alerts** — Automated email alerts triggered by skill/company/category keywords.
- **AI Enrichment** — OpenAI-powered summarization and skill extraction.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python / FastAPI (async) |
| Database | PostgreSQL (SQLAlchemy 2 async) |
| Search | Elasticsearch |
| Queue / Scheduler | Celery + Redis (workers + beat) |
| Frontend | Next.js + React + Tailwind CSS |
| Scraping | Scrapy, Playwright, httpx, BeautifulSoup, feedparser |
| AI | OpenAI API |
| Auth | JWT (python-jose) + bcrypt/passlib |

---

## Project Structure

```
remote-job-aggregator/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # FastAPI routers (jobs, search, auth, alerts,
│   │   │                     #   companies, saved_jobs, hidden_companies)
│   │   ├── core/             # Config (pydantic-settings), async DB setup
│   │   ├── models/           # SQLAlchemy models (Job, Company, User, ...)
│   │   ├── scrapers/         # Data source adapters
│   │   │   ├── base.py
│   │   │   ├── greenhouse.py
│   │   │   ├── lever.py
│   │   │   ├── remotive.py
│   │   │   ├── weworkremotely.py
│   │   │   ├── workable.py
│   │   │   └── manager.py
│   │   ├── services/         # AI enrichment, Elasticsearch, auth, email
│   │   ├── tasks/            # Celery tasks (scraping, alerts)
│   │   └── scripts/          # seed_data.py, scrape_once.py
│   ├── alembic/              # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── pages/                # Next.js pages + dynamic routes
│   ├── components/           # JobCard, SearchBar, FilterSidebar
│   ├── utils/api.ts          # Axios API client
│   └── package.json
├── docker-compose.yml
├── deploy.sh                 # Docker deployment script
└── run.sh                    # Local dev: frontend + backend (+ infra)
```

---

## Quick Start (Local Development)

The easiest way to run everything is the `run.sh` script. It **automatically starts PostgreSQL, Redis, and Elasticsearch** (via Docker) if they aren't already running, then launches the backend and frontend.

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** with npm
- **Docker + Docker Compose** (for the Postgres/Redis/Elasticsearch infrastructure)

### 1. Install backend dependencies

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install frontend dependencies

```bash
cd frontend
npm install
```

### 3. Configure the environment

Copy the example into `.env` (root of project):

```env
# Backend
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/remotejobs
REDIS_URL=redis://localhost:6379/0
ELASTICSEARCH_URL=http://localhost:9200
DEBUG=true
SECRET_KEY=change-me-to-a-random-string-at-least-32-chars

# Security
ALLOWED_ORIGINS=http://localhost:3000

# OpenAI (optional, enables AI salary/summary enrichment)
OPENAI_API_KEY=your-openai-api-key

# Scraping
GREENHOUSE_COMPANY_TOKENS=stripe,gitlab,airbnb,discord,figma,vercel,coinbase,reddit,instacart,datadog,duolingo,airtable,chime,upwork
LEVER_COMPANY_TOKENS=linkedin,spotify
# Set to a comma-separated list of Workable account slugs to enable (e.g. miro,strava)
WORKABLE_COMPANY_TOKENS=

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Initialize the database (first time only)

Creates all tables and seeds sample data (companies, jobs, a demo user).

```bash
cd backend
source .venv/bin/activate
python app/scripts/seed_data.py
```

> Seed login — `demo@remotejobhub.com` / `Demo1234`

### 5. Run everything

```bash
./run.sh
```

This starts, in order:
1. **PostgreSQL, Redis, Elasticsearch** — via `docker-compose` (if not already running)
2. **Backend** — FastAPI + uvicorn on port `8000`
3. **Frontend** — Next.js dev server on port `3000`

Press **Ctrl+C** to stop all services.

### Access the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/docs |
| Flower (Celery monitor) | http://localhost:5555 |

---

## Running With Docker (Full Stack)

For a containerized deployment of **everything** (including the backend/frontend containers):

```bash
chmod +x deploy.sh
./deploy.sh
```

`deploy.sh`:
1. Detects `docker compose` (v2 plugin) or `docker-compose` (standalone).
2. Creates a `.env` if missing with a generated `SECRET_KEY`.
3. Builds and starts all containers.
4. Runs Alembic migrations and initializes the Elasticsearch index.

---

## Data Sources

Current scrapers (`backend/app/scrapers/`) — all pull **real, legitimate** remote jobs:

| Source | Type | Status | What It Provides |
|--------|------|--------|------------------|
| **Greenhouse** | ATS API | ✅ Active | Remote jobs from 14 verified boards (GitLab, Coinbase, Reddit, Instacart, Stripe, etc.) |
| **Arbeitnow** | Job board API | ✅ Active | Large remote-friendly listings |
| **RemoteOK** | Remote job board API | ✅ Active | Remote jobs with salary data |
| **Jobicy** | Remote job board API | ✅ Active | Remote jobs with structured salary data |
| **We Work Remotely** | RSS feed | ✅ Active | Remote programming job listings |
| **Remotive** | Remote job board API | ✅ Active | Curated remote jobs |
| **Lever** | ATS API | ⚠️ Configured (LinkedIn/Spotify) | Picks up jobs only when a board lists remote roles |
| **Workable** | ATS API | ⚠️ Disabled by default | Enable by setting `WORKABLE_COMPANY_TOKENS` |

> **Note on seed data**: `seed_data.py` inserts 9 synthetic jobs for development/demo only. Live scrapes (via Celery or `scrape_once.py`) overwrite/merge real listings and are the intended production data source.

### Adding a new source

1. Create `backend/app/scrapers/<name>.py`.
2. Subclass `BaseScraper`, implementing `fetch_jobs()` and `parse_job()`.
3. Register it in `scrapers/manager.py`.

---

## API Endpoints

All routes are prefixed with `/api/v1`.

### Jobs
- `GET /api/v1/jobs/` — List jobs with filters (category, remote_type, experience_level, salary_min, skills, q, pagination)
- `GET /api/v1/jobs/{job_id}` — Job details
- `POST /api/v1/jobs/{job_id}/hide` — Hide a job for the current user

### Search
- `GET /api/v1/search/?q=query` — Full-text search via Elasticsearch
- `GET /api/v1/search/suggest?q=prefix` — Autocomplete suggestions

### Authentication
- `POST /api/v1/auth/register` — Register a user
- `POST /api/v1/auth/login` — Login, returns a JWT
- (Protected endpoints) — saved jobs, alerts, hidden items

### Companies
- `GET /api/v1/companies/` — List companies
- `GET /api/v1/companies/{slug}/` — Company detail

### Saved Jobs & Alerts
- Saved jobs CRUD, job-alert CRUD, hidden-companies management.

> Full interactive docs: http://localhost:8000/api/docs

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Async Postgres connection string | `postgresql+asyncpg://user:password@localhost:5432/remotejobs` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ELASTICSEARCH_URL` | Elasticsearch endpoint | `http://localhost:9200` |
| `DEBUG` | Enable debug/docs | `true` |
| `SECRET_KEY` | JWT signing secret (min 32 chars, auto-generated if empty) | — |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `http://localhost:3000` |
| `OPENAI_API_KEY` | OpenAI key for AI enrichment (optional) | — |
| `GREENHOUSE_COMPANY_TOKENS` | Comma-separated Greenhouse board tokens to scrape | 14 verified remote-first companies |
| `LEVER_COMPANY_TOKENS` | Comma-separated Lever company slugs to scrape | `linkedin,spotify` |
| `WORKABLE_COMPANY_TOKENS` | Comma-separated Workable account slugs to scrape | empty (disabled) |
| `NEXT_PUBLIC_API_URL` | Frontend → backend base URL | `http://localhost:8000/api/v1` |

---

## Running Individual Services

### Backend only

```bash
cd backend
source .venv/bin/activate
python3 -m uvicorn app.main:app --reload
```

### Frontend only

```bash
cd frontend
npm run dev
```

### Celery (scraping + alerts)

```bash
cd backend
source .venv/bin/activate
celery -A app.tasks.scraping_tasks.celery_app worker --loglevel=info
celery -A app.tasks.scraping_tasks.celery_app beat --loglevel=info
```

---

## Troubleshooting

**Backend returns 500 / "relation jobs does not exist"**
The database tables haven't been created. Run:
```bash
cd backend && source .venv/bin/activate && python app/scripts/seed_data.py
```

**Backend "Connect call failed (127.0.0.1, 5432)"**
PostgreSQL isn't running. Start infrastructure with `./run.sh` (it auto-starts it) or run `docker-compose up -d postgres redis elasticsearch`.

**Password hashing error with bcrypt**
If you installed a `bcrypt` version newer than 4.0.x, passlib breaks. Pin it:
```bash
pip install "bcrypt==4.0.1"
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push and open a Pull Request.

---

## License

MIT License — see the `LICENSE` file for details.
