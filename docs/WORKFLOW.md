# RemoteJobHub — Project Workflow

This document describes how the RemoteJobHub remote job aggregator works end-to-end: from data ingestion through serving, searching, and notification. It covers architecture, setup, common tasks, and operational considerations (monitoring, testing, security, data management).

---

## Quick Start

**Prerequisites:** Docker + Docker Compose on a machine that can reach the internet (scrapers fetch live data).

```bash
# 1. Prepare environment (never commit the real .env)
cp .env.example .env
vim .env                       # set SECRET_KEY, DB creds; optional OPENAI_API_KEY

# 2. Build & launch the whole stack
./deploy.sh

# 3. Confirm the API is up
curl http://localhost:8000/health
```

The stack boots PostgreSQL, Elasticsearch, Redis, the FastAPI backend, the Next.js frontend, and a Celery worker + beat scheduler. Alembic runs migrations automatically and the first scrape is scheduled shortly after startup.

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ FRONTEND  (Next.js 14)                                                │
│  /  /search  /companies  /saved-jobs  /alerts  /login  /register     │
│  utils/api.ts — Axios + JWT interceptor + 401 redirect               │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ REST / JSON (JWT Bearer)
┌───────────────────────────────▼──────────────────────────────────────┐
│ BACKEND  (FastAPI · /api/v1)                                          │
│  /auth  /jobs  /search  /companies  /saved-jobs  /alerts  /hidden-*  │
└───────┬──────────────┬──────────────┬───────────────┬────────────────┘
        │              │              │               │
        ▼              ▼              ▼               ▼
   ┌─────────┐   ┌────────────┐  ┌────────┐    ┌──────────────┐
   │PostgreSQL│   │Elasticsearch│  │ Redis  │    │ Celery Beat  │
   │ source   │   │ full-text   │  │ broker │    │  + Worker    │
   │ of truth │   │ + suggest   │  │ /cache │    │ scrape/mail  │
   └─────────┘   └────────────┘  └────────┘    └──────┬───────┘
                                                      │ fetch raw
                                        ┌─────────────▼──────────────┐
                                        │ SCRAPERS (8 sources)        │
                                        │ Remotive · RemoteOK         │
                                        │ Arbeitnow · Jobicy          │
                                        │ WeWorkRemotely              │
                                        │ Greenhouse (14 cos)         │
                                        │ Lever · Workable            │
                                        └───────────────────────────┘
```

**Data flows:** scrapers → Celery worker → PostgreSQL (dedupe/upsert) → Elasticsearch (search) → FastAPI → Next.js UI. Alerts trigger emails when new jobs match user preferences.

---

## Development vs Production Setup

| Aspect | Development | Production |
|--------|-------------|------------|
| Command | `docker compose up db redis elasticsearch backend frontend` | `./deploy.sh` |
| Seed data | `python scripts/seed_data.py` (9 demo jobs) | none (live scraped data) |
| SECRET_KEY | `.env` (set locally) | `.env` maintained by `deploy.sh`, kept out of git |
| OpenAI enrichment | optional / mocked | real `OPENAI_API_KEY` (gitignored) |
| Scrape interval | short (e.g. 1h) for fast iteration | tuned to source rate limits |
| Debug / DB echo | `DEBUG=true` | `DEBUG=false` |

> ⚠️ The real `.env` (with secrets like `OPENAI_API_KEY` and `SECRET_KEY`) is **gitignored**. Only `.env.example` is committed. Never copy a real `.env` into the repo or into a commit.

---

## End-to-End Workflow

### 1. Data Ingestion (Scraping)

- **Celery Beat** schedules `scrape_all_jobs` every `SCRAPING_INTERVAL_HOURS` (default 1h).
- `ScraperManager` runs **8 scrapers concurrently** via `asyncio.gather`; each scraper is isolated so a single failure does not abort the run.
- Sources: Remotive, RemoteOK, Arbeitnow, Jobicy, WeWorkRemotely (boards) + Greenhouse, Lever, Workable (ATS APIs).
- Result: **~1,170 real, legitimate remote jobs** per scrape cycle.
- **Rate limiting:** each board/ATS is polled at most once per cycle, with exponential backoff and 3 retries per request (`fetch_url` uses `tenacity`). `SCRAPING_INTERVAL_HOURS` is the throttling mechanism.
- **Error handling:** individual scraper failures are caught in `_run_scraper_safely`, logged, and skipped — a dead source never blocks the rest.

### 2. Deduplication + Persistence (`scraping_tasks.py`)

```
fetch raw
  → AIEnrichmentService.enrich_job()    # optional OpenAI salary/summary
  → upsert into PostgreSQL             # dedupe on source_url
      → insert new / update existing
  → index each job into Elasticsearch
  → trigger instant alerts for new jobs
```

- **Primary key / dedupe:** `source_url` is unique. Re-crawling the same posting updates it instead of duplicating.

### 3. Data Serving (FastAPI Routes)

| Route | Purpose |
|-------|---------|
| `/auth` | register, login (JWT), profile, change password |
| `/jobs` | paginated job feed with filters (category, remote, experience, salary, skills) |
| `/search` | Elasticsearch full-text search + autocomplete suggestions |
| `/companies` | company list, detail, aggregated stats (SQL counts/avg) |
| `/saved-jobs` | per-user saved jobs (N+1-optimized JOIN) |
| `/alerts` | per-user job-alert CRUD (limit 5 for free users) |
| `/hidden-*` | hide jobs/companies per user |

### 4. Frontend (Next.js)

```
User loads /
  → fetchJobs() via utils/api.ts
      → Axios attaches Bearer JWT from localStorage
      → 401 → interceptor clears token, redirects to /login

User actions:
  Save job  → saveJob() / unsaveJob()
  Hide job  → hideJob()
  Apply     → opens apply_url (official app page) in a new tab
  Filter    → fetchJobs(filters)
  Search    → searchJobs() / getSuggestions()
  Alerts    → getAlerts() / createAlert() / updateAlert() / deleteAlert()
```

### 5. Notifications

- `send_instant_alert` (Celery) matches new jobs against active alerts → email (SMTP).

---

## Database & Indexing Strategy

- **PostgreSQL indexes** (migration `004`): single-column indexes on commonly filtered fields plus composite indexes for hot query patterns:
  - `(is_active, posted_at)` — main feed ordering
  - `(category, remote_type)` — filter combinations
  - `(experience_level, remote_type)` — filter combinations
  - `(title, company_name)` — quick lookup
  - GIN index on `search_vector` (tsvector) for keyword search.
- **Elasticsearch** is the search engine (not the source of truth). Its index serves `MultiMatch` full-text queries and `completion` typeahead suggestions. Fields not meant to be searched (e.g. `apply_url`, `source_url`) are indexed but marked `"index": false` to save space.

---

## Common Tasks

### How to add a new scraper

1. Create `backend/app/scrapers/<name>.py` extending `BaseScraper`.
2. Implement `async fetch_jobs()` and `parse_job(raw)` returning a dict that matches the `Job` schema (most importantly `source_url` for dedupe and `apply_url` for the Apply button).
3. Register the scraper in `ScraperManager.__init__` (`manager.py`) in the `self.scrapers` list.
4. Add any configuration (e.g. company tokens) to `config.py`.
5. Run `python app/scripts/scrape_once.py` to verify it fetches real jobs, then confirm they appear in `/jobs`.

### How to run a one-off scrape

```bash
cd backend
python app/scripts/scrape_once.py        # fetch + upsert + index once
```

### How to apply a schema change

```bash
cd backend
alembic revision -m "description"        # hand-write upgrade/downgrade
alembic upgrade head                     # apply
alembic upgrade head --sql               # preview SQL without applying
```

### How to reset the local database

```bash
docker compose down -v                   # wipe volumes
./deploy.sh                              # recreate + migrate + boostrap
```

---

## Testing Strategy

- **Backend unit tests** cover scraper parsing (`parse_job` on fixture payloads), the API routes, and the auth flow. Run from `backend/`:
  ```bash
  python -m pytest
  ```
- **Frontend typing/lint guard:** a clean compile is enforced before merge:
  ```bash
  cd frontend && npx tsc --noEmit && npx next build
  ```
- **Live scrapers** are validated manually via `scripts/scrape_once.py` (the sources return live data, so they are a final integration check).
- **Migration validation:** `alembic upgrade head --sql` is used to confirm a migration produces valid SQL and the chain stays a single head.

---

## Monitoring, Logging & Alerting

- **Logs** are emitted by FastAPI (Uvicorn) and Celery at `INFO`/`ERROR`; scraper failures are logged with the source name so a broken source is visible in the worker logs.
- **Health endpoint:** `/health` on the backend reports readiness — wire it to an orchestrator or uptime monitor.
- **Suggested production monitoring (not yet wired in):**
  - Collect `/health` and scrape-success metrics with Prometheus + Grafana.
  - Alert when `ScraperManager` total jobs drops below a threshold (e.g. a source returning 0 jobs repeatedly → likely rate-limited or schema-changed).
  - Watch Celery queue depth and Redis memory; alert on task failures.
  - Track error logs into a centralized sink (e.g. Loki/Sentry).

---

## Performance & Scaling Considerations

- **Frontend:** static routes are prerendered; client-side data fetching keeps the read path on the API.
- **Backend API:** paginated queries, filtered indexes, and the Elasticsearch search offload keep the Postgres read path fast.
- **Elasticsearch** shards are set to 1 with 0 replicas for a single-node dev/prod; scale replicas when the read load grows.
- **Scaling levers:**
  - Add Celery worker replicas for faster concurrent scraping (`docker compose up --scale worker=N`).
  - Add DB replicas or connection pooling (e.g. PgBouncer) as request volume grows.
  - Increase Elasticsearch replicas/shards if search latency degrades.
- **Throttle sources:** poll frequency is governed by `SCRAPING_INTERVAL_HOURS`; keep intervals respectful of each board/ATS rate limit to avoid IP blocks.

---

## Security Considerations

- **Secrets:** real `.env` is gitignored; only `.env.example` committed. `SECRET_KEY` must be ≥32 chars and is auto-generated if unset.
- **CORS** restricted to `ALLOWED_ORIGINS`.
- **Auth:** JWT via `python-jose`, passwords hashed with bcrypt, tokens in `localStorage` (401 interceptor clears and redirects).
- **Rate limiting** via slowapi on auth endpoints to slow brute-force.
- **Scraper URLs are never trusted** as navigational targets in the app — the frontend opens apply links in a new tab with `noopener,noreferrer`.
- **Debug/disclosure:** DB `echo` only when `DEBUG=true`; timezone-aware timestamps everywhere.
- **Outbound calls:** AI enrichment and scraping only contact the configured source/OpenAI domains.

---

## Data Retention & Backup

- **Data retention:** jobs have `expires_at` and `is_active` flags; stale or expired postings are filtered from feeds. (Active pruning/archival job is a manual `expires_at` policy — extend `scraping_tasks.py` to deactivate listings older than a threshold when your data lifecycle requires it.)
- **Backups:**
  - **PostgreSQL** (source of truth) — snapshot regularly:
    ```bash
    docker compose exec postgres pg_dump -U $POSTGRES_USER remote_jobs > backup_$(date +%F).sql
    ```
  - **Elasticsearch** can be re-populated from Postgres by re-running the scraper + indexer, so treat ES as recoverable/derived.
  - Store backups off-box (object storage) and test restore regularly.

---

## Typical Happy Path

1. Scraper pulls real jobs → stored in Postgres + indexed in Elasticsearch.
2. User registers / logs in → receives JWT.
3. User searches and filters real remote jobs → saves favorites → sets up a job alert → applies via the official link.
4. Celery matches new jobs → emails the user.
5. All data is persisted and queryable via the REST API consumed by the Next.js UI.

---

## Repository Layout

```
backend/
  alembic/            # database migrations (001→005)
  tests/              # unittest-based scraper/metrics/migration tests
  app/
    api/routes/       # FastAPI route handlers
    core/             # config, database, security, metrics registry
    models/           # SQLAlchemy models (Job, Company, User, ...)
    scrapers/         # 8 data-source scrapers + manager
    scripts/          # seed_data, scrape_once
    services/         # auth, AI enrichment, Elasticsearch
    tasks/            # Celery scraping + alert + retention tasks
frontend/
  components/         # UI components (Header, JobCard, ...)
  pages/              # Next.js pages (incl. /jobs/[id] apply page)
  utils/api.ts        # centralized API client
docker-compose.yml    # full stack orchestration
deploy.sh             # one-command deployment
```
