# Safqa — Agent Execution Instructions

> Hand this file to the AI agent coder **alongside** `safqa_spec.md`.  
> The agent must read the spec first, then follow these instructions precisely.  
> Every section below maps directly to a section in the spec.

---

## 0. Agent Mindset & Rules

Before writing a single line of code, internalize these rules. They override any default coding habits.

1. **Spec is the source of truth.** If these instructions conflict with the spec, the spec wins. Flag the conflict, do not silently pick one.
2. **No creative additions.** Do not add features, tables, fields, or endpoints not in the spec. Out-of-scope items are listed explicitly — do not implement them.
3. **Ask before assuming.** If a spec section is ambiguous (e.g., exact Meilisearch index settings not listed), stop and ask. Do not invent a solution.
4. **One sprint at a time.** Complete and verify each sprint before starting the next. Never jump ahead.
5. **Every piece of code must be testable.** If you write a function with no test path, it is incomplete.
6. **Infrastructure is code.** Docker Compose, Nginx config, GitHub Actions YAML — treat them with the same rigor as application code.

---

## 1. Pre-Implementation Checklist

Complete all of the following before writing any application code.

### 1.1 Read the Full Spec
- [ ] Read `safqa_spec.md` sections 1–16 in full
- [ ] Confirm you understand the 8-container architecture (Section 4)
- [ ] Confirm you understand all 10 data flows (Section 5)
- [ ] Confirm you understand the tender state machine (Section 8)
- [ ] Confirm you understand the 4-layer FastAPI architecture (Section 4.3)

### 1.2 Environment Setup
- [ ] Confirm the target server is **Hetzner CX32** (4 vCPU, 8GB RAM, Ubuntu 22.04 LTS)
- [ ] Confirm Docker Engine 24+ and Docker Compose v2 are installed
- [ ] Confirm GitHub repository exists with `main` and `dev` branches
- [ ] Confirm GitHub Secrets are set: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `GHCR_TOKEN`
- [ ] Confirm domain `safqa.ma` and `api.safqa.ma` DNS A records point to the VPS IP

### 1.3 Tooling Versions — Pin These Exactly

| Tool | Version | Why Pinned |
|------|---------|------------|
| Python | 3.12.x | Spec explicitly states 3.12 |
| Node.js | 20.x LTS | Next.js 14 requirement |
| Next.js | 14.x | Spec explicitly states v14 |
| FastAPI | latest stable | No version conflict risk |
| PostgreSQL | 15 (postgres:15-alpine) | Spec pinned |
| Meilisearch | v1.7 (getmeili/meilisearch:v1.7) | Spec pinned |
| Redis | 7 (redis:7-alpine) | Spec pinned |
| RabbitMQ | 3 (rabbitmq:3-mgmt-alpine) | Spec pinned |
| Scrapy | latest stable | No pin — use latest |
| Alembic | latest stable | No pin |

**Do not upgrade pinned versions without explicit instruction.**

---

## 2. Repository Structure

Create this exact directory layout before writing any code. Do not deviate.

```
safqa/
├── .github/
│   └── workflows/
│       ├── ci-staging.yml          # triggers on push to dev
│       └── ci-prod.yml             # triggers on push to main
├── ADR/
│   ├── ADR-01-rabbitmq-broker.md
│   ├── ADR-02-meilisearch.md
│   ├── ADR-03-pgbouncer.md
│   ├── ADR-04-hetzner.md
│   ├── ADR-05-scrapy-playwright.md
│   ├── ADR-06-docker-compose.md
│   ├── ADR-07-tanstack-query.md
│   └── ADR-08-self-issued-jwt.md
├── backend/
│   ├── app/
│   │   ├── routers/                # FastAPI route handlers (layer 1)
│   │   │   ├── tenders.py
│   │   │   ├── auth.py
│   │   │   ├── saved.py
│   │   │   ├── alerts.py
│   │   │   └── health.py
│   │   ├── services/               # Business logic (layer 2)
│   │   │   ├── search_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── alert_service.py
│   │   │   └── tender_service.py
│   │   ├── repositories/           # DB access (layer 3)
│   │   │   ├── tender_repo.py
│   │   │   ├── user_repo.py
│   │   │   ├── alert_repo.py
│   │   │   └── saved_repo.py
│   │   ├── infrastructure/         # Clients + connections (layer 4)
│   │   │   ├── database.py         # asyncpg pool via PgBouncer
│   │   │   ├── redis_client.py
│   │   │   ├── meili_client.py
│   │   │   └── resend_client.py
│   │   ├── models/                 # Pydantic schemas (request/response)
│   │   ├── middleware/
│   │   │   └── rate_limit.py       # slowapi config
│   │   ├── metrics.py              # Custom Prometheus counters/histograms
│   │   └── main.py
│   ├── migrations/                 # Alembic migration files
│   │   ├── env.py
│   │   └── versions/
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── requirements.txt
├── scraper/
│   ├── safqa_scraper/
│   │   ├── spiders/
│   │   │   └── tenders_spider.py
│   │   ├── pipelines/
│   │   │   ├── postgres_pipeline.py
│   │   │   └── meili_pipeline.py
│   │   ├── middlewares/
│   │   ├── items.py
│   │   └── settings.py
│   ├── tasks/
│   │   ├── scrape_task.py          # Celery task: triggers spider
│   │   └── alert_task.py           # Celery task: alert matching
│   ├── celery_app.py               # Celery + Beat config
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js 14 App Router
│   │   │   ├── page.tsx            # Home / search
│   │   │   ├── tenders/[id]/
│   │   │   │   └── page.tsx
│   │   │   ├── saved/
│   │   │   │   └── page.tsx
│   │   │   ├── alerts/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   ├── lib/
│   │   │   ├── api.ts              # Typed API client
│   │   │   └── query-client.ts     # TanStack Query setup
│   │   └── types/
│   │       └── tender.ts
│   ├── Dockerfile
│   ├── next.config.js
│   └── package.json
├── infra/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── sites-available/
│   │       └── safqa.conf
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   │       └── safqa_alerts.yml    # All 6 alert rules from spec §13.2
│   ├── grafana/
│   │   └── provisioning/
│   ├── loki/
│   │   └── loki-config.yml
│   └── pgbouncer/
│       └── pgbouncer.ini
├── docker-compose.yml              # Local development
├── docker-compose.prod.yml         # Production
├── .env.example                    # All vars from spec §14, no values
├── .env.prod                       # On VPS only — never committed
└── .gitignore                      # Must include: .env.prod, .env.local, *.pyc
```

---

## 3. Sprint Plan

Each sprint is 1 week. Do not start a sprint until all previous sprint acceptance criteria are met.

---

### Sprint 1 — Infrastructure Foundation

**Goal:** Every container starts. Services can reach each other. CI pipeline green.

#### Tasks

**1. Write `docker-compose.yml` (local dev)**
- Include all 14 containers from spec §4.2
- Use named volumes for Postgres data, Redis AOF, Meilisearch data
- All internal services bound to Docker internal network only
- Expose only Nginx on 80/443 externally

**2. Write `docker-compose.prod.yml`**
- Mirror local compose with production image tags (ghcr.io references)
- Add restart policies: `unless-stopped` on all containers
- Grafana accessible only via SSH tunnel (no external port binding)

**3. Configure Nginx (`infra/nginx/safqa.conf`)**
- Upstream blocks: `fastapi` → localhost:8000, `nextjs` → localhost:3000
- Rate limiting: 30 req/min/IP on all routes; 10 req/min on `/v1/auth/*`
- Security headers: `HSTS max-age=31536000; preload`, `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`
- SSL: Certbot managed (Let's Encrypt); HTTP → HTTPS redirect

**4. Configure PgBouncer (`infra/pgbouncer/pgbouncer.ini`)**
- Mode: **transaction** (spec ADR-03)
- max_client_conn: 100
- default_pool_size: 20
- Pool connects to Postgres on port 5432; FastAPI and Scrapy connect to PgBouncer on 6432

**5. Write GitHub Actions pipelines**
- `ci-staging.yml`: triggers on `push` to `dev`
  - jobs: `test` → `build` → `push` → `deploy-staging`
- `ci-prod.yml`: triggers on `push` to `main`
  - jobs: `test` → `build` → `push` → `deploy-prod`
- Tag images with git SHA: `ghcr.io/{org}/safqa-api:{SHA}`
- Deploy step: SSH into VPS, `docker pull`, `docker compose up -d`, `docker image prune -f`

**6. Write ADR documents**
- One `.md` per ADR from spec §15
- Format: Context → Decision → Rationale → Rejected alternatives → Consequences

#### Sprint 1 Acceptance Criteria
- [ ] `docker compose up` brings all containers to healthy state
- [ ] `curl http://localhost/health` returns 200
- [ ] Push to `dev` triggers staging pipeline to completion
- [ ] Push to `main` triggers prod pipeline to completion
- [ ] Nginx rejects requests beyond rate limit with 429
- [ ] All 8 ADR files exist in `ADR/`

---

### Sprint 2 — Database & Migrations

**Goal:** All 7 tables exist in Postgres. Alembic manages all schema changes. Indexes applied.

#### Tasks

**1. Initialize Alembic**
```bash
cd backend
alembic init migrations
```
- Configure `env.py` to use asyncpg DSN from `DATABASE_URL` env var
- **Rule:** Never use `alembic revision --autogenerate` without reviewing the generated SQL before committing

**2. Write migrations in order**

Each table is a separate migration file:

| Migration | Table | Notes |
|-----------|-------|-------|
| `001_create_tenders` | `tenders` | All columns from spec §6.2; include all 4 indexes |
| `002_create_users` | `users` | `id uuid PK`, `email unique`, `password_hash text`, `created_at`, `updated_at` |
| `003_create_saved_tenders` | `saved_tenders` | FK to users + tenders; composite PK `(user_id, tender_id)`; `saved_at timestamptz` |
| `004_create_saved_searches` | `saved_searches` | `id uuid PK`, `user_id FK`, `label text`, `filters jsonb NOT NULL`, `email text`, `is_active bool DEFAULT true`, `created_at` |
| `005_create_alert_notifications` | `alert_notifications` | `id uuid PK`, `saved_search_id FK`, `tender_id FK`, `sent_at timestamptz`; UNIQUE `(saved_search_id, tender_id)` |
| `006_create_scrape_logs` | `scrape_logs` | `id uuid PK`, `domain_code text`, `count_scraped int`, `count_upserted int`, `duration_ms int`, `errors jsonb`, `run_at timestamptz DEFAULT now()` |

**3. Implement the `tenders` table index strategy exactly as spec §6.2:**
```sql
-- idx_tenders_ref (from migration 001)
CREATE UNIQUE INDEX idx_tenders_ref ON tenders (reference_number);

-- idx_tenders_domain_dl — partial index
CREATE INDEX idx_tenders_domain_dl ON tenders (domain_code, deadline_at)
WHERE status = 'active';

-- idx_tenders_deadline — partial index
CREATE INDEX idx_tenders_deadline ON tenders (deadline_at)
WHERE status = 'active';

-- idx_tenders_fts — GIN index for French full-text
CREATE INDEX idx_tenders_fts ON tenders
USING GIN (to_tsvector('french', coalesce(title,'') || ' ' || coalesce(authority,'')));
```

**4. Write a nightly Celery Beat task: `expire_tenders`**
- Schedule: daily at 02:00 UTC
- Query: `UPDATE tenders SET status='expired' WHERE deadline_at < CURRENT_DATE AND status='active'`
- Log count of rows updated

#### Sprint 2 Acceptance Criteria
- [ ] `alembic upgrade head` runs clean with zero errors
- [ ] `alembic downgrade base` runs clean (all migrations reversible)
- [ ] All 6 tables exist with correct columns, types, and constraints
- [ ] All 4 indexes on `tenders` exist and are verified with `\d tenders` in psql
- [ ] No `ALTER TABLE` statements exist anywhere outside migration files
- [ ] `expire_tenders` task exists and is scheduled

---

### Sprint 3 — Scraping Pipeline

**Goal:** Scrapy spider runs on schedule, scrapes all domains, upserts to Postgres, indexes in Meilisearch, logs every run.

#### Tasks

**1. Configure Celery + Beat (`scraper/celery_app.py`)**
```python
# Beat schedule — scrape every 4 hours
CELERYBEAT_SCHEDULE = {
    'scrape-all-domains': {
        'task': 'tasks.scrape_task.scrape_all_domains',
        'schedule': crontab(minute=0, hour='*/4'),
    },
    'expire-tenders': {
        'task': 'tasks.scrape_task.expire_tenders',
        'schedule': crontab(minute=0, hour=2),
    },
}
```
- Broker: `RABBITMQ_URL` from env
- Result backend: Redis (`REDIS_URL`)
- Use **RabbitMQ** as broker (ADR-01). Do not use Redis as broker.

**2. Write Scrapy Spider (`spiders/tenders_spider.py`)**
- Target: `https://www.marchespublics.gov.ma/mobile/`
- Iterate all ~80 domain codes (discover from the portal's domain list endpoint)
- Rate limiting: **max 1 request per 2 seconds per domain** (spec C-02). Implement via Scrapy's `DOWNLOAD_DELAY = 2` and `AUTOTHROTTLE_ENABLED = True`
- Retry: up to 3 retries with exponential backoff (FR-05) via `RETRY_TIMES = 3`
- Use `scrapy-playwright` only for pages that require JS rendering

**3. Define `TenderItem` (`scraper/safqa_scraper/items.py`)**

Map every field from the `tenders` table:
```python
class TenderItem(scrapy.Item):
    reference_number = scrapy.Field()
    title = scrapy.Field()
    authority = scrapy.Field()
    city = scrapy.Field()
    domain_code = scrapy.Field()
    domain_label = scrapy.Field()
    procedure_type = scrapy.Field()
    budget_raw = scrapy.Field()
    budget_mad = scrapy.Field()   # parsed float — see budget parsing below
    published_at = scrapy.Field() # date string → python date
    deadline_at = scrapy.Field()  # date string → python date
    source_url = scrapy.Field()
```

**4. Budget Parsing (FR-06)**

Write a `parse_budget(raw: str) -> float | None` utility:
- Strip currency symbols: `MAD`, `DH`, `Dhs`, whitespace, commas
- Handle formats: `1.500.000,00`, `1,500,000.00`, `1500000`
- Return `None` if unparseable — store raw in `budget_raw`, `None` in `budget_mad`
- Write unit tests for all formats

**5. Write `PostgresPipeline` (`pipelines/postgres_pipeline.py`)**
- Connect to PgBouncer on `DATABASE_URL`
- UPSERT on `reference_number`:
```sql
INSERT INTO tenders (...) VALUES (...)
ON CONFLICT (reference_number)
DO UPDATE SET
  title = EXCLUDED.title,
  authority = EXCLUDED.authority,
  budget_raw = EXCLUDED.budget_raw,
  budget_mad = EXCLUDED.budget_mad,
  deadline_at = EXCLUDED.deadline_at,
  status = EXCLUDED.status,
  scraped_at = now()
WHERE tenders.title IS DISTINCT FROM EXCLUDED.title
   OR tenders.deadline_at IS DISTINCT FROM EXCLUDED.deadline_at;
-- Only update if something actually changed
```
- Return `(count_scraped, count_upserted)` to the task for logging

**6. Write `MeilisearchPipeline` (`pipelines/meili_pipeline.py`)**
- Index name: `tenders`
- Call `add_documents()` in batches of 100 after Postgres write
- Document fields to index: `id, reference_number, title, authority, city, domain_code, domain_label, procedure_type, budget_mad, published_at, deadline_at, status`
- Configure Meilisearch index settings (run once at startup):
```python
index.update_settings({
    'searchableAttributes': ['title', 'authority', 'domain_label', 'city'],
    'filterableAttributes': ['domain_code', 'city', 'status', 'procedure_type'],
    'sortableAttributes': ['deadline_at', 'budget_mad', 'published_at'],
    'typoTolerance': {'enabled': True},
    'pagination': {'maxTotalHits': 1000}
})
```

**7. Write `scrape_logs` writer**

After each domain scrape completes, insert a row:
```sql
INSERT INTO scrape_logs (domain_code, count_scraped, count_upserted, duration_ms, errors)
VALUES ($1, $2, $3, $4, $5::jsonb)
```
- `errors`: JSON array of `{url, error_message}` objects; empty array if clean run
- Emit Prometheus metrics: `safqa_tenders_scraped_total`, `safqa_scrape_duration_seconds` (see spec §13.1)

#### Sprint 3 Acceptance Criteria
- [ ] `celery worker` starts without errors; `celery beat` schedules correctly
- [ ] Manual task invocation `celery call tasks.scrape_task.scrape_all_domains` completes
- [ ] After run: tenders exist in Postgres; records exist in `scrape_logs`
- [ ] After run: tenders searchable in Meilisearch admin UI
- [ ] Rate limit confirmed: no request faster than 1 req/2s per domain
- [ ] `parse_budget` unit tests pass for all currency formats
- [ ] UPSERT confirmed: running scraper twice does not duplicate rows

---

### Sprint 4 — FastAPI Backend

**Goal:** All endpoints from spec §10.2 implemented, tested, and performant.

#### Tasks

**1. Set up FastAPI application (`backend/app/main.py`)**
- Mount all routers under `/v1` prefix
- Register `prometheus-fastapi-instrumentator` — auto-expose `/metrics`
- Register `slowapi` rate limiter: 10 req/min on `/v1/auth/*`
- Register global exception handlers that return the standard error format from spec §10.2
- Startup event: verify DB + Redis + Meilisearch connections; log status

**2. Implement the 4-layer architecture strictly**

**Rule for the agent:** No repository method may be called from a router directly. No infrastructure client may be called from a service directly.

```
router (tenders.py)
  calls → search_service.search_tenders(q, filters, page, limit)
    calls → meili_client.search(...)           # cache miss path
    calls → redis_client.get/set(...)           # cache layer
    calls → tender_repo.get_by_ids([...])       # enrichment
```

**3. Implement Infrastructure Layer**

`infrastructure/database.py`:
- Use `asyncpg` connection pool
- Pool connects to **PgBouncer** (port 6432), NOT directly to Postgres
- Pool size: min=2, max=10 (PgBouncer handles the rest)
- **All queries must use parameterized statements** — zero string interpolation (NFR-18)

`infrastructure/redis_client.py`:
- Use `redis.asyncio`
- Implement `get(key)`, `set(key, value, ttl)`, `delete(key)`, `blocklist_token(token, ttl)`
- TTL for search cache: **1800 seconds** (FR-11)

`infrastructure/meili_client.py`:
- Use `meilisearch-python` async client
- Implement `search(q, filters, sort, page, limit) -> SearchResult`
- Implement `add_documents(docs: list[dict])` for pipeline use

**4. Implement Auth (spec §11.3 — all 4 requirements)**

`services/auth_service.py`:
- `hash_password(plain: str) -> str`: bcrypt, **cost=12** (FR-12)
- `verify_password(plain: str, hashed: str) -> bool`
- `create_access_token(user_id: uuid) -> str`: JWT, **15-minute expiry** (FR-13), signed with `JWT_SECRET_KEY`, algorithm `HS256`
- `create_refresh_token(user_id: uuid) -> str`: JWT, **7-day expiry** (FR-14)
- `rotate_refresh_token(old_token: str) -> tuple[str, str]`:
  1. Verify old token signature and expiry
  2. Check Redis blocklist — if present, raise `UNAUTHORIZED`
  3. Blocklist old token in Redis with TTL = remaining lifetime (FR-15)
  4. Issue new access + refresh token pair
  5. Return both

**5. Implement Search with Cache (spec §5, DF-06 to DF-08)**

`services/search_service.py`:
```python
async def search_tenders(q, domain, city, type, status, sort, page, limit):
    cache_key = f"search:{hash(q, domain, city, type, status, sort, page, limit)}"
    
    cached = await redis.get(cache_key)
    if cached:
        # Increment safqa_cache_hits_total counter
        return cached
    
    # Increment safqa_cache_misses_total counter
    results = await meili.search(q, filters, sort, page, limit)
    
    if results.hits:
        ids = [h['id'] for h in results.hits]
        enriched = await tender_repo.get_by_ids(ids)  # PG for fresh field data
        results.hits = enriched
    
    await redis.set(cache_key, results, ttl=1800)
    return results
```

**6. Implement the URGENT computation**

`URGENT` is **never stored in DB**. It is computed at response serialization:
```python
# In the Tender response model
@computed_field
def is_urgent(self) -> bool:
    return (self.deadline_at - date.today()).days <= 14
```

**7. Implement all endpoints from spec §10.2**

For each endpoint, write:
- Route handler in `routers/`
- Service method in `services/`
- Repository query in `repositories/` (parameterized asyncpg)
- Pydantic request/response model in `models/`
- At least 1 happy-path test + 1 error-path test in `tests/`

**8. Register all custom Prometheus metrics (spec §13.1)**

`backend/app/metrics.py`:
```python
from prometheus_client import Counter, Histogram, Gauge

tenders_scraped = Counter('safqa_tenders_scraped_total', '...', ['domain_code'])
tenders_upserted = Counter('safqa_tenders_upserted_total', '...', ['domain_code'])
scrape_duration = Histogram('safqa_scrape_duration_seconds', '...', ['domain_code'])
scrape_errors = Counter('safqa_scrape_errors_total', '...', ['domain_code', 'error'])
alerts_sent = Counter('safqa_alerts_sent_total', '...')
dlq_depth = Gauge('safqa_dlq_depth', '...', ['queue_name'])
cache_hits = Counter('safqa_cache_hits_total', '...', ['endpoint'])
cache_misses = Counter('safqa_cache_misses_total', '...', ['endpoint'])
pgbouncer_active = Gauge('pgbouncer_pool_clients_active', '...', ['database'])
```

#### Sprint 4 Acceptance Criteria
- [ ] All 18 endpoints return correct HTTP status codes (test with pytest)
- [ ] Auth flow: register → login → access protected endpoint → refresh → logout works end-to-end
- [ ] Used refresh token is rejected after rotation (blocklist verified)
- [ ] `GET /tenders/search?q=...` returns results in < 200ms on cache miss (measured)
- [ ] Second identical search returns in < 20ms (cache hit verified via `safqa_cache_hits_total`)
- [ ] `URGENT` field is computed correctly at query time, not stored
- [ ] `/metrics` returns all 9 custom metrics
- [ ] `> 70%` line coverage on all services and repositories (run `pytest --cov`)
- [ ] Standard error format returned for all 8 error codes in spec §10.2

---

### Sprint 5 — Alert System

**Goal:** Alert matching runs post-scrape, deduplicates correctly, emails deliver within 15 minutes.

#### Tasks

**1. Write Alert Matching Task (`tasks/alert_task.py`)**

This task is triggered **after each scrape cycle completes** (chain in Scrapy pipeline):
```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def match_and_send_alerts(self, new_tender_ids: list[str]):
    # 1. Fetch all active saved_searches from Postgres
    alerts = await alert_repo.get_active_alerts()
    
    # 2. For each alert, evaluate filter set against new_tender_ids
    for alert in alerts:
        matching_ids = apply_filters(new_tender_ids, alert.filters)
        if not matching_ids:
            continue
        
        # 3. Deduplicate against alert_notifications
        unseen_ids = await alert_repo.filter_unseen(alert.id, matching_ids)
        if not unseen_ids:
            continue
        
        # 4. Fetch tender details for email rendering
        tenders = await tender_repo.get_by_ids(unseen_ids)
        
        # 5. Send email via Resend
        await send_alert_email(alert.email, alert.label, tenders)
        
        # 6. Write deduplication records
        await alert_repo.record_notifications(alert.id, unseen_ids)
        
        # 7. Increment safqa_alerts_sent_total
```

**2. `apply_filters` logic**

Filters are stored as JSONB in `saved_searches.filters`. Example:
```json
{"domain_code": "1.15", "city": "Casablanca", "procedure_type": "AO Ouvert"}
```
- All filter keys are optional; only present keys are evaluated
- Match is: tender's field equals filter value (exact match per field)
- A tender matches an alert only if ALL specified filter fields match

**3. Email via Resend**

Use `RESEND_API_KEY` env var. POST to Resend API:
- From: `noreply@safqa.ma`
- Subject: `[Safqa Alert] {alert.label} — {count} new tenders`
- Body: HTML list of matching tenders with title, authority, deadline, and `source_url`
- **Do not send more than 10 tenders per email.** If more match, summarize and link to search.

**4. Dead Letter Queue**

On failure after 3 retries:
```python
# In celery_app.py
task_reject_on_worker_lost = True
task_acks_late = True

CELERY_QUEUES = (
    Queue('default', routing_key='default'),
    Queue('dlq', routing_key='dlq'),
)
```
- Failed alert tasks route to `dlq` queue
- `safqa_dlq_depth` Gauge is polled from RabbitMQ management API every 60s

#### Sprint 5 Acceptance Criteria
- [ ] End-to-end test: scrape run → alert matching runs within 15 minutes (measured in `scrape_logs` + `alert_notifications.sent_at`)
- [ ] Deduplication verified: running match task twice for same tenders sends only 1 email
- [ ] `alert_notifications` table records are written for every sent alert
- [ ] Failed task after 3 retries lands in `dlq` queue (verified in RabbitMQ management UI)
- [ ] `safqa_alerts_sent_total` increments correctly
- [ ] Filter matching unit tests cover: all filters match, partial match, no match, empty filter set

---

### Sprint 6 — Next.js Frontend

**Goal:** All pages functional. Lighthouse ≥ 90 all categories. TanStack Query implemented.

#### Tasks

**1. Set up TanStack Query (ADR-07)**
```typescript
// lib/query-client.ts
import { QueryClient } from '@tanstack/react-query'
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  }
})
```

**2. Typed API Client (`lib/api.ts`)**
- Base URL from `NEXT_PUBLIC_API_URL` env var
- All endpoints from spec §10.2 implemented as typed async functions
- Auth token management: store access token in memory (not localStorage); store refresh token in httpOnly cookie
- Auto-refresh: on 401 `TOKEN_EXPIRED`, call `/auth/refresh`, retry original request once

**3. Implement Pages**

| Page | Route | Key Features |
|------|-------|-------------|
| Home / Search | `/` | Search input, filter panel (domain, city, procedure type), results grid with highlights, pagination |
| Tender Detail | `/tenders/[id]` | All tender fields, save/unsave button (auth required), deadline urgency indicator |
| Saved Tenders | `/saved` | Auth-gated, list of bookmarked tenders, unsave action |
| Alerts | `/alerts` | Auth-gated, create/edit/delete alerts, filter builder UI |
| Login / Register | `/auth/login`, `/auth/register` | Form + JWT flow |

**4. Search Page Requirements**
- Debounce input: 300ms before firing query
- Display Meilisearch highlights (`_formatted` fields) in results
- URL state sync: filters + query + page reflected in URL params (`?q=...&domain=...&page=2`)
- Infinite scroll OR pagination — pick one; document the choice in an ADR

**5. Lighthouse Compliance (NFR-06)**
- Use Next.js `Image` component for all images (no raw `<img>`)
- Use `next/font` for font loading
- All pages must be server-side rendered or statically generated where possible
- Run `lighthouse-ci` in GitHub Actions; fail pipeline if any category < 90

#### Sprint 6 Acceptance Criteria
- [ ] `npm run build` completes with zero errors
- [ ] All 5 page routes render without console errors
- [ ] Search returns results with highlights visible in UI
- [ ] Auth flow complete: register, login, protected pages gated, logout clears session
- [ ] Lighthouse CI passes ≥ 90 in all categories (Performance, Accessibility, Best Practices, SEO)
- [ ] URL state syncs correctly (copy-paste URL preserves search state)

---

### Sprint 7 — Observability & Hardening

**Goal:** All alert rules active. Dashboards deployed. Security headers verified. Load test passes.

#### Tasks

**1. Configure Prometheus (`infra/prometheus/prometheus.yml`)**
```yaml
scrape_configs:
  - job_name: 'fastapi'
    scrape_interval: 15s
    static_configs:
      - targets: ['fastapi:8000']
    metrics_path: '/v1/metrics'
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

**2. Implement all 6 Alert Rules (spec §13.2)**

In `infra/prometheus/rules/safqa_alerts.yml`:
```yaml
groups:
  - name: safqa
    rules:
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning

      - alert: ScrapeSilent
        expr: increase(safqa_tenders_scraped_total[6h]) == 0
        for: 0m
        labels:
          severity: critical

      - alert: DLQNotEmpty
        expr: safqa_dlq_depth > 0
        for: 15m
        labels:
          severity: warning

      - alert: DBPoolExhausted
        expr: pgbouncer_pool_clients_active > 18
        for: 0m
        labels:
          severity: warning

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[10m]) / rate(http_requests_total[10m]) > 0.01
        for: 10m
        labels:
          severity: warning

      - alert: ServiceDown
        expr: up{job="fastapi"} == 0
        for: 2m
        labels:
          severity: critical
```

**3. Configure Loki + structlog**

Every log statement in FastAPI and Celery must use `structlog` and emit JSON:
```python
import structlog
log = structlog.get_logger()
log.info("scrape_completed", domain=domain_code, count=count_scraped, duration_ms=duration)
```

**4. Security Hardening Checklist**

Run each check and confirm passing:

| Check | Command / Method | Expected Result |
|-------|-----------------|-----------------|
| HSTS header present | `curl -I https://safqa.ma` | `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` |
| CSP header present | `curl -I https://safqa.ma` | `Content-Security-Policy: default-src 'self' ...` |
| Internal services unreachable | `curl http://{VPS_IP}:7700` (from outside) | Connection refused |
| SQL injection test | `GET /tenders/search?q=' OR 1=1--` | 200 with normal results (not a DB error) |
| Rate limit enforced | Send 31 req/min to `/v1/tenders/search` | 31st returns 429 with `Retry-After` |
| Auth rate limit | Send 11 req/min to `/v1/auth/login` | 11th returns 429 |
| Secrets not in git | `git log --all --full-history -- .env.prod` | No results |

**5. Load Test (NFR-03)**

Using Locust:
```python
# locustfile.py
class SafqaUser(HttpUser):
    @task
    def search(self):
        self.client.get("/v1/tenders/search?q=construction&domain=1.15")
```
- Target: 200 concurrent users
- Pass condition: p95 < 500ms, error rate < 1%

#### Sprint 7 Acceptance Criteria
- [ ] All 6 Prometheus alert rules firing correctly on simulated conditions
- [ ] Grafana dashboard loads and displays all 9 custom metrics
- [ ] Loki receives and indexes structured JSON logs from FastAPI + Celery
- [ ] All 7 security checks in hardening checklist pass
- [ ] Locust load test passes: 200 concurrent users, p95 < 500ms, error rate < 1%
- [ ] `GET /health` returns all 3 dependency statuses (DB, Redis, Meilisearch)
- [ ] Full stack reproducible: `git clone` + `cp .env.example .env.prod` + fill values + `docker compose -f docker-compose.prod.yml up -d` → all services healthy

---

## 4. Cross-Cutting Rules (Every Sprint)

### Secrets Management
- Every secret lives in `.env.prod` on the VPS at `/opt/safqa/.env.prod` with permissions `root:root 600`
- In CI, secrets come exclusively from GitHub Secrets
- `.env.prod` is in `.gitignore` — verify with `git check-ignore .env.prod`
- `.env.example` must list every variable from spec §14 with empty or placeholder values

### Database Rules
- Zero raw SQL strings in application code — use asyncpg parameterized queries
- Zero `ALTER TABLE` statements outside Alembic migrations
- Every schema change = new Alembic migration file, reviewed before commit
- Migrations must be reversible (`downgrade` implemented)

### Testing Rules
- Every service method has at least 1 unit test
- Every repository method has at least 1 integration test (against real test DB)
- Every endpoint has at least 1 happy-path and 1 error-path test
- Run `pytest --cov=app --cov-report=term-missing` — coverage must stay above 70%

### Logging Rules
- Use `structlog` everywhere — no raw `print()` or `logging.info()` strings
- Every log event must include: `timestamp`, `level`, `service`, and relevant context fields
- Never log: passwords, JWT tokens, API keys, raw SQL with user data

### Deployment Rules
- Never SSH into VPS and run `docker compose up` manually — always push through CI
- Rollback = push the previous git SHA to `main` (pipeline re-tags and redeploys)
- After every production deployment, verify `/health` returns 200

---

## 5. Definition of Done

A feature is **Done** only when all of the following are true:

- [ ] Code matches the spec — no additions, no omissions
- [ ] Tests written and passing (`pytest`)
- [ ] Coverage ≥ 70% maintained
- [ ] Linter passes (`ruff check .`)
- [ ] Docker build succeeds (`docker build .`)
- [ ] Feature is deployed to staging via CI (not manually)
- [ ] Acceptance criteria for the sprint are checked off
- [ ] No secrets committed to git
- [ ] Structured logs emitted for the feature
- [ ] If a new endpoint: documented with request/response example

---

## 6. Failure Modes & What to Do

| Situation | Correct Action |
|-----------|---------------|
| marchespublics.gov.ma changes HTML structure | Stop spider, log error to `scrape_logs`, alert via `ScrapeSilent` rule, fix xpath/selectors, redeploy |
| Meilisearch index corrupts | Delete and recreate index, re-run `add_documents()` from Postgres as source of truth |
| Redis loses data (restart without AOF) | Search cache cold-starts fine; token blocklist loss = expired refresh tokens may replay once. Mitigate: ensure AOF is enabled in `redis.conf` |
| JWT secret rotation needed | Update `JWT_SECRET_KEY` in `.env.prod`, `docker compose restart fastapi`. All existing tokens invalidated — users must re-login. This is the intended behavior (spec C-03 says rotation must not require full service restart, but only the API container restarts) |
| PgBouncer pool exhausted (`DBPoolExhausted` fires) | Check for long-running queries (`pg_stat_activity`), kill if needed; reduce asyncpg pool max size; do not increase PgBouncer max past 20 without increasing Postgres `max_connections` |
| DLQ fills up | Inspect failed task payloads in RabbitMQ management UI (SSH tunnel to port 15672); fix root cause (e.g. Resend API down); re-queue after fix |
| CI pipeline fails on deploy | Do not manually deploy. Fix the failing test or build, push a fix commit, let CI retry |

---

## 7. Out-of-Scope Reminder

The agent must not implement any of the following, even if they seem like obvious improvements:

- AI summarization of tenders
- PDF parsing of tender attachments
- Arabic UI translation
- Mobile native app (iOS/Android)
- Multi-tenant support
- Webhook delivery for alerts (email only per spec)
- GraphQL API
- Kubernetes / Helm charts
- Any SaaS database (Supabase, PlanetScale, etc.)
- Any PaaS deployment (Railway, Render, Fly.io, etc.)

If the user requests any of the above during implementation, acknowledge the request, note it as post-MVP, and continue with the spec as written.
