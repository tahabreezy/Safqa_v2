# Safqa (صفقة) — Software Specification

> **Version:** v1.0 | **Date:** March 2026 | **Status:** Draft — Sprint Planning  
> **Author:** Taha Breezy | **Type:** Software Requirements & Design Specification

---

## 1. Executive Summary

Safqa is a production-grade web platform that aggregates, indexes, and surfaces public tender announcements from **marchespublics.gov.ma** (Morocco's official government procurement portal, operated by TGR).

**Core Problem:** The portal has 1,200+ active tenders across 80+ sectors but offers no modern search, no alerts, and no mobile-friendly UI.

**Solution Stack:**
- Automated scraper on a **4-hour cadence**
- **PostgreSQL** for structured storage
- **Meilisearch** for sub-50ms full-text search
- **FastAPI** REST API
- **Next.js 14** frontend
- **Celery** async task queue for scraping + email alerts

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Search p95 latency | < 200ms | Prometheus histogram |
| Full scrape cycle time | < 30 min | `scrape_logs.duration_ms` |
| Scrape coverage | > 98% tenders | Count vs portal |
| Alert delivery time | < 15 min post-scrape | `notification.sent_at − scrape_logs.run_at` |
| API uptime | > 99.5% / month | Prometheus + Grafana |
| Lighthouse score | ≥ 90 all categories | Lighthouse CI |

---

## 2. Scope

### In Scope (MVP — Sprint 1–7)
- Automated scraping of all tender domains from marchespublics.gov.ma
- Full-text search with typo tolerance, faceted filtering, and sorting
- User authentication (register, login, JWT refresh token rotation)
- Tender save/bookmark functionality per user
- Email alert system with filter-based matching and deduplication
- Prometheus + Grafana observability stack
- Nginx reverse proxy with SSL, rate limiting, and security headers
- GitHub Actions CI/CD pipeline → Hetzner VPS

### Out of Scope (MVP)
- AI-powered tender summarization
- PDF document parsing from tender attachments
- Multi-language support (Arabic UI)
- Mobile native application

### Assumptions & Constraints

| ID | Type | Description |
|----|------|-------------|
| A-01 | Assumption | marchespublics.gov.ma remains publicly accessible without auth for scraping |
| A-02 | Assumption | HTML structure of the mobile endpoint does not change significantly |
| A-03 | Assumption | Tender data is public domain |
| C-01 | Constraint | All infrastructure must be self-hosted (no SaaS database, no PaaS) |
| C-02 | Constraint | Scraping must respect rate limits: max 1 req/2s per domain |
| C-03 | Constraint | JWT secret rotation must not require service restart |
| C-04 | Constraint | Total monthly infrastructure cost must remain under €20 at launch |

---

## 3. Use Cases

### UC-01: Search Tenders
- **Actor:** Company / Job Seeker
- **Auth Required:** No (public endpoint)
- **Flow:** User enters query → applies optional filters (domain, city, procedure type) → results in < 200ms with highlights → clicks for detail view
- **Exit:** User has identified relevant tenders

### UC-02: Create Alert
- **Actor:** Authenticated User
- **Auth Required:** Yes (JWT)
- **Flow:** User configures filters + email → alert stored in DB → next scrape cycle triggers email for matching new tenders
- **Exit:** User receives email within 15 minutes of a matching tender being published

### UC-03: Scrape & Index (Automated)
- **Actor:** Celery Beat
- **Precondition:** RabbitMQ operational, Postgres + Meilisearch available
- **Flow:** Beat enqueues scrape task every 4h → Celery worker spawns Scrapy spider → tenders upserted to Postgres → new tenders indexed in Meilisearch → alert matching triggered
- **Exit:** DB contains up-to-date records with `scrape_logs` entry

---

## 4. System Architecture

### Container Overview (C4 Level 2)

All containers run on a **single Hetzner CX32 VPS** via Docker Compose in production.

| Container | Technology | Responsibility | Protocol |
|-----------|------------|----------------|----------|
| Nginx | nginx:alpine | Reverse proxy, SSL, rate limiting | HTTP/S |
| Next.js App | Next.js 14 / Node 20 | SSR frontend | HTTP (internal) |
| FastAPI | Python 3.12 / uvicorn | REST API, auth, business logic | HTTP + JWT |
| Redis | redis:7-alpine (AOF) | Response cache, token blocklist | RESP |
| PgBouncer | edoburu/pgbouncer | Connection pooling to Postgres | Postgres wire |
| PostgreSQL 15 | postgres:15-alpine | Primary data store | SQL |
| Meilisearch | getmeili/meilisearch:v1.7 | Full-text search engine | REST |
| RabbitMQ | rabbitmq:3-mgmt-alpine | Message broker, task queue | AMQP |
| Celery Workers | Python 3.12 | Async task execution (scrape/alerts) | AMQP consume |
| Celery Beat | Python 3.12 | Cron scheduler | AMQP publish |
| Scrapy Spider | Python 3.12 / Playwright | Web scraping pipeline | HTTP |
| Prometheus | prom/prometheus | Metrics collection | HTTP scrape |
| Grafana | grafana/grafana | Metrics visualization | HTTP (internal) |
| Loki | grafana/loki | Log aggregation | HTTP push |

### FastAPI Internal Architecture

Layered architecture with **one-directional dependencies**:

```
Routers → Services → Repositories → Infrastructure
```

---

## 5. Data Flows

| Flow ID | From | To | Data | Trigger |
|---------|------|----|------|---------|
| DF-01 | Celery Beat | RabbitMQ | scrape task message | Cron: every 4h |
| DF-02 | Celery Worker | TGR Portal | HTTP GET (mobile URL) | Task consumed |
| DF-03 | TGR Portal | Scrapy Spider | HTML tender pages | HTTP response |
| DF-04 | Scrapy Pipelines | PostgreSQL | UPSERT tender rows | Item yielded |
| DF-05 | Scrapy Pipelines | Meilisearch | `add_documents()` | After PG write |
| DF-06 | Browser | Nginx → FastAPI | GET /search + filters | User action |
| DF-07 | FastAPI | Meilisearch | `search()` with filter expr | Cache miss |
| DF-08 | FastAPI | Redis | SET cache_key TTL=1800 | After search |
| DF-09 | Celery Alert Worker | Postgres | SELECT active alerts | Post-scrape |
| DF-10 | Celery Alert Worker | Resend API | POST /email | Alert matched |

---

## 6. Database Schema

### `tenders` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | uuid | PK, DEFAULT gen_random_uuid() | Internal primary key |
| `reference_number` | text | UNIQUE NOT NULL | Official TGR reference — deduplication key |
| `title` | text | NOT NULL | Tender title in French |
| `authority` | text | NOT NULL | Issuing government body |
| `city` | text | NULLABLE | Geographic location |
| `domain_code` | text | NOT NULL | Activity domain code (e.g., "1.15") |
| `domain_label` | text | NULLABLE | Human-readable domain label |
| `procedure_type` | text | NULLABLE | AO Ouvert / Restreint / Bon de Commande |
| `budget_raw` | text | NULLABLE | Budget string as scraped |
| `budget_mad` | numeric(15,2) | NULLABLE | Parsed budget in MAD |
| `published_at` | date | NOT NULL | Publication date |
| `deadline_at` | date | NOT NULL | Submission deadline |
| `source_url` | text | NULLABLE | Original URL on TGR portal |
| `status` | text | DEFAULT 'active' | `active` \| `expired` \| `cancelled` |
| `scraped_at` | timestamptz | DEFAULT now() | Last scrape timestamp |
| `created_at` | timestamptz | DEFAULT now() | First ingestion timestamp |

### Index Strategy

| Index Name | Columns | Type | Purpose |
|------------|---------|------|---------|
| `idx_tenders_ref` | `reference_number` | UNIQUE BTREE | Deduplication on upsert |
| `idx_tenders_domain_dl` | `domain_code, deadline_at, status` | PARTIAL BTREE | Primary filter query — WHERE status='active' |
| `idx_tenders_deadline` | `deadline_at` | PARTIAL BTREE | Nightly expiry job — WHERE status='active' |
| `idx_tenders_fts` | `to_tsvector('french', title \|\| authority)` | GIN | Fallback text search (Meilisearch is primary) |

### Other Tables (7 total)
- **`users`** — registered user accounts
- **`saved_tenders`** — user bookmarks (user ↔ tender M:M)
- **`saved_searches`** — alert subscriptions with JSONB filter set
- **`alert_notifications`** — deduplication log (alert ↔ tender)
- **`scrape_logs`** — per-domain scrape run records

---

## 7. Key Sequences

### Scraping Pipeline
```
Celery Beat (every 4h)
  → RabbitMQ [AMQP, delivery guaranteed]
    → Celery Worker
      → Scrapy Spider (+ Playwright for JS pages)
        → Postgres UPSERT (reference_number as key)
        → Meilisearch add_documents()
        → Alert matching task enqueued
```

### Search & Cache Flow
```
Browser → Nginx (rate limit)
  → FastAPI
    → Redis GET cache_key
      [HIT]  → return cached JSON (< 20ms)
      [MISS] → Meilisearch search()
             → Postgres (field enrichment)
             → Redis SET TTL=1800
             → return JSON
```

### Auth Flow
- Passwords: **bcrypt, cost=12**
- Access token: **JWT, 15-minute expiry**
- Refresh token: **7-day expiry, rotated on use**
- Used refresh tokens blocklisted in **Redis** for remaining TTL (replay prevention)

### Alert Notification Flow
```
Post-scrape trigger
  → Celery Alert Worker
    → SELECT active saved_searches from Postgres
    → For each alert: evaluate new tender IDs against filter set
    → Check alert_notifications for deduplication
    → For matches: POST to Resend API
    → On failure: retry x3 → Dead Letter Queue (RabbitMQ)
```

---

## 8. Tender State Machine

```
          scraper yields new item
[—] ─────────────────────────────→ SCRAPED
                                      │
                              budget parsed,
                              deadline valid
                                      ↓
                                   ACTIVE ←─────┐
                                      │          │ (edge case: days_left recalc > 14)
                          deadline_at │          │
                          - today()   │     URGENT (computed at query time,
                          <= 14 days  │            NOT stored in DB)
                                      │
                 ┌────────────────────┤
                 ↓                    ↓
              EXPIRED            CANCELLED
          (nightly job          (scraper detects
           at 02:00)             cancellation)
```

**Note:** `URGENT` is never written to the DB. It is derived at read time when `deadline_at - today() <= 14 days`.  
**Invariant:** `EXPIRED → ACTIVE` is **not allowed** — deadlines cannot extend.

---

## 9. Deployment

### Infrastructure
- **Host:** Hetzner CX32 VPS
- **Orchestration:** Docker Compose (not Kubernetes — single node, lower overhead)
- **Domain:** safqa.ma / api.safqa.ma
- **SSL:** Certbot + Let's Encrypt (auto-renewal via Nginx)

### Network Security

| Service | External Port | Internal Port | Accessible From |
|---------|--------------|---------------|-----------------|
| Nginx | 80, 443 | 80, 443 | Internet |
| FastAPI | none | 8000 | Nginx only |
| Next.js | none | 3000 | Nginx only |
| Postgres | none | 5432 | PgBouncer only |
| PgBouncer | none | 6432 | FastAPI, Scrapy |
| Redis | none | 6379 | FastAPI, Celery |
| RabbitMQ | none | 5672, 15672 | Celery workers only |
| Meilisearch | none | 7700 | FastAPI, Scrapy |
| Prometheus | none | 9090 | Grafana only |
| Grafana | none (SSH tunnel) | 3001 | Admin via SSH tunnel |

### CI/CD Pipeline (GitHub Actions)

| Stage | Tool | Action | On Failure |
|-------|------|--------|------------|
| Test | pytest + ruff | lint → unit tests → integration tests | Abort pipeline |
| Build | Docker buildx | Multi-stage build, layer cache via GHA | Abort pipeline |
| Push | ghcr.io | Tag image with git SHA | Abort pipeline |
| Deploy (staging) | SSH + Docker | Pull + restart (dev branch) | Alert only, prod unaffected |
| Deploy (prod) | SSH + Docker | Pull + restart + prune old images | Rollback via previous SHA tag |

---

## 10. API Specification

### Base URLs
- **Production:** `https://api.safqa.ma/v1`
- **Staging:** `https://api-staging.safqa.ma/v1`

**Conventions:** All responses JSON. Timestamps ISO 8601 UTC. List endpoints use cursor pagination (`page`, `limit`).

**Auth:** `Authorization: Bearer <access_token>` on protected endpoints. Access tokens expire in 15 minutes. Rotate via `POST /auth/refresh`.

### Public Endpoints (no auth)

| Method | Path | Description | Key Params |
|--------|------|-------------|------------|
| GET | `/tenders/search` | Full-text search via Meilisearch | `q, domain, city, type, status, sort, page, limit` |
| GET | `/tenders/{id}` | Tender detail by UUID | — |
| GET | `/tenders/ref/{ref}` | Tender lookup by TGR reference | — |
| GET | `/stats` | Global counts (active, urgent, new this week) | — |
| GET | `/domains` | All domain codes + labels + tender count | — |
| GET | `/health` | Liveness: DB + Redis + Meilisearch ping | — |
| GET | `/metrics` | Prometheus scrape endpoint | — |

### Protected Endpoints (JWT required)

| Method | Path | Description | Body / Response |
|--------|------|-------------|-----------------|
| POST | `/auth/register` | Create user account | `email, password` → `{access_token, refresh_token}` |
| POST | `/auth/login` | Authenticate user | `email, password` → `{access_token, refresh_token}` |
| POST | `/auth/refresh` | Rotate refresh token | `refresh_token` → `{access_token, refresh_token}` |
| POST | `/auth/logout` | Invalidate refresh token | `refresh_token` → `204` |
| GET | `/saved` | List user's saved tenders | → `{data: Tender[], pagination}` |
| POST | `/saved/{tender_id}` | Save a tender | → `201` |
| DELETE | `/saved/{tender_id}` | Remove a saved tender | → `204` |
| GET | `/alerts` | List user's active alerts | → `{data: Alert[]}` |
| POST | `/alerts` | Create alert with filter set | `filters (jsonb), email, label` → `Alert` |
| PATCH | `/alerts/{id}` | Toggle alert active/inactive | `is_active` → `Alert` |
| DELETE | `/alerts/{id}` | Delete an alert | → `204` |

### Standard Error Codes

| HTTP | `code` Field | Condition |
|------|-------------|-----------|
| 400 | `VALIDATION_ERROR` | Pydantic schema validation failure |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT |
| 401 | `TOKEN_EXPIRED` | Valid JWT but past expiry |
| 403 | `FORBIDDEN` | JWT valid but wrong user owns resource |
| 404 | `NOT_FOUND` | Tender or alert ID does not exist |
| 422 | `UNPROCESSABLE` | Invalid filter parameter value |
| 429 | `RATE_LIMITED` | Nginx/slowapi limit exceeded — `Retry-After` header present |
| 503 | `SERVICE_UNAVAIL` | DB/Redis/Meilisearch health check failing |

---

## 11. Functional Requirements

### Data Ingestion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Scrape all active tenders from marchespublics.gov.ma/mobile/ on a 4-hour schedule | Must |
| FR-02 | Support all domain activity codes (~80 codes) | Must |
| FR-03 | Upsert tenders using `reference_number` as deduplication key, updating only changed fields | Must |
| FR-04 | Log each scrape cycle in `scrape_logs` with `domain, count_scraped, count_upserted, duration_ms, errors` | Must |
| FR-05 | Retry failed scrape requests up to 3 times with exponential backoff | Must |
| FR-06 | Parse budget text into numeric `budget_mad`; store raw string in `budget_raw` | Should |

### Search & Filtering

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-07 | Full-text search across `title` and `authority` with typo tolerance | Must |
| FR-08 | Faceted filtering by `domain_code`, `city`, `status`, `procedure_type` | Must |
| FR-09 | Sorting by `deadline_at` (asc/desc), `budget_mad`, and `published_at` | Must |
| FR-10 | Search results include highlighted match fragments | Should |
| FR-11 | Cache search results in Redis with 30-minute TTL | Must |

### Authentication

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-12 | Passwords hashed with bcrypt at cost factor 12 | Must |
| FR-13 | Access tokens expire after 15 minutes | Must |
| FR-14 | Refresh tokens expire after 7 days and are invalidated on use (rotation) | Must |
| FR-15 | Used refresh tokens blocklisted in Redis for remaining TTL | Must |

### Alerts

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-16 | Users can create alert subscriptions on any combination of supported filters | Must |
| FR-17 | Alert matching runs within 15 minutes of each scrape cycle completing | Must |
| FR-18 | No duplicate notifications for the same tender to the same alert | Must |
| FR-19 | Failed email tasks retried up to 3 times before routing to DLQ | Must |
| FR-20 | Users can deactivate, reactivate, and delete alerts | Must |

---

## 12. Non-Functional Requirements

### Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | `GET /tenders/search` p95 latency | < 200ms (miss) / < 20ms (hit) |
| NFR-02 | `GET /tenders/{id}` p95 | < 100ms |
| NFR-03 | Sustain 200 concurrent requests/sec | p95 < 500ms (Locust test) |
| NFR-04 | Full scrape cycle (all domains) | < 30 min end-to-end |
| NFR-05 | Alert matching for 1,000 active alerts | < 5 min |
| NFR-06 | Frontend Lighthouse Performance | ≥ 90 (mobile + desktop) |

### Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-07 | API uptime (monthly) | > 99.5% |
| NFR-08 | Scraper job success rate | > 98% of scheduled runs |
| NFR-09 | Data freshness lag | < 4h 15min from publication |
| NFR-10 | Alert delivery reliability | > 99% of matched alerts delivered |
| NFR-11 | Zero data loss on restart | Redis AOF + Postgres WAL |

### Security

| ID | Requirement | Implementation |
|----|-------------|----------------|
| NFR-12 | All external traffic over HTTPS | Nginx + Certbot Let's Encrypt |
| NFR-13 | HTTP Strict Transport Security | HSTS max-age=31536000 preload |
| NFR-14 | Rate limiting on public API | 30 req/min/IP (Nginx); 10 req/min on auth (slowapi) |
| NFR-15 | No secrets in version control | GitHub Secrets for CI; `.env.prod` on VPS root:600 |
| NFR-16 | Internal services not internet-accessible | Docker network isolation |
| NFR-17 | Content Security Policy | Nginx CSP header on all responses |
| NFR-18 | SQL injection prevention | asyncpg parameterized queries exclusively |

### Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-19 | Python test coverage | > 70% line coverage on services + repos |
| NFR-20 | Architecture Decision Records | All significant decisions in `ADR/` directory |
| NFR-21 | Structured logging | JSON logs via structlog; readable by Loki |
| NFR-22 | Database migrations | Alembic only — no manual `ALTER TABLE` in production |
| NFR-23 | Deployment reproducibility | Full stack from `docker-compose.prod.yml` + `.env.prod` |

---

## 13. Observability

### Custom Prometheus Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `safqa_tenders_scraped_total` | Counter | `domain_code` | Total tenders scraped per domain |
| `safqa_tenders_upserted_total` | Counter | `domain_code` | Total rows changed on upsert |
| `safqa_scrape_duration_seconds` | Histogram | `domain_code` | Per-scrape duration |
| `safqa_scrape_errors_total` | Counter | `domain_code, error` | Scraping failures |
| `safqa_alerts_sent_total` | Counter | — | Total alert emails dispatched |
| `safqa_dlq_depth` | Gauge | `queue_name` | Dead letter queue message count |
| `safqa_cache_hits_total` | Counter | `endpoint` | Redis cache hits per endpoint |
| `safqa_cache_misses_total` | Counter | `endpoint` | Redis cache misses per endpoint |
| `pgbouncer_pool_clients_active` | Gauge | `database` | Active PgBouncer connections |

### Alert Rules

| Rule | Condition | Severity |
|------|-----------|----------|
| `HighAPILatency` | p95 > 2s for 5 min | Warning |
| `ScrapeSilent` | 0 scrapes in last 6h | Critical |
| `DLQNotEmpty` | dlq_depth > 0 for 15 min | Warning |
| `DBPoolExhausted` | pool_clients_active > 18 (of 20) | Warning |
| `HighErrorRate` | error rate > 1% for 10 min | Warning |
| `ServiceDown` | /health non-200 for 2 min | Critical |

---

## 14. Environment Variables

| Variable | Service | Description | Example |
|----------|---------|-------------|---------|
| `DATABASE_URL` | API, Scrapy | PgBouncer connection string | `postgresql://safqa:***@pgbouncer:6432/safqa` |
| `REDIS_URL` | API, Celery | Redis connection string | `redis://redis:6379/0` |
| `RABBITMQ_URL` | Celery | RabbitMQ AMQP URL | `amqp://user:***@rabbitmq:5672/safqa` |
| `MEILI_URL` | API, Scrapy | Meilisearch base URL | `http://meilisearch:7700` |
| `MEILI_MASTER_KEY` | API, Scrapy | Meilisearch auth key | `***` |
| `JWT_SECRET_KEY` | API | 256-bit secret for JWT signing | `***` |
| `JWT_ALGORITHM` | API | JWT algorithm | `HS256` |
| `RESEND_API_KEY` | Celery | Resend transactional email key | `re_***` |
| `PROXY_URL` | Scrapy | Optional HTTP proxy for scraping | `socks5://...` |
| `SENTRY_DSN` | API, Celery | Sentry error tracking DSN | `https://***@sentry.io/...` |

---

## 15. Architecture Decision Records (Summary)

| ADR | Decision | Rationale | Rejected |
|-----|----------|-----------|----------|
| ADR-01 | RabbitMQ over Redis as Celery broker | AMQP delivery guarantees; Redis BRPOP loses jobs on crash | Redis |
| ADR-02 | Meilisearch over Postgres GIN | Purpose-built for search; typo tolerance; sub-50ms; zero config | Postgres full-text |
| ADR-03 | PgBouncer in transaction mode | Prevents Postgres max_connections exhaustion | Direct asyncpg |
| ADR-04 | Hetzner VPS over Railway/Render | Root access; €4.5/mo vs $15+; no PaaS abstraction | Railway / Render |
| ADR-05 | Scrapy + scrapy-playwright over httpx | Framework handles throttle, retry, stats, pipelines | Raw httpx + Playwright |
| ADR-06 | Docker Compose over Kubernetes | Correct orchestration at single-node scale; K8s adds ~4h/wk overhead | Kubernetes |
| ADR-07 | TanStack Query over SWR | Optimistic mutations, infinite scroll, cache invalidation superset | SWR |
| ADR-08 | Self-issued JWT over Supabase Auth | No vendor dependency in auth critical path; key rotation owned | Supabase Auth |

---

## 16. Glossary

| Term | Definition |
|------|------------|
| TGR | Trésorerie Générale du Royaume — Morocco's General Treasury, operator of marchespublics.gov.ma |
| AO | Appel d'Offres — competitive tender/bidding process |
| Upsert | `INSERT ... ON CONFLICT DO UPDATE` — insert or update on conflict |
| DLQ | Dead Letter Queue — RabbitMQ queue for messages that failed after max retries |
| AMQP | Advanced Message Queuing Protocol — used by RabbitMQ |
| PgBouncer | Lightweight connection pooler for PostgreSQL |
| JWT | JSON Web Token — signed token for stateless authentication |
| AOF | Append-Only File — Redis persistence mode logging every write |
| LRU | Least Recently Used — Redis eviction policy for maxmemory management |
| AUTOTHROTTLE | Scrapy middleware that auto-adjusts crawl speed based on server response time |
