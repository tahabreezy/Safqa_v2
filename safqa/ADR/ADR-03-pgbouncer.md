# ADR-03: PgBouncer in Transaction Mode

## Context
FastAPI, scraper, and workers share one PostgreSQL instance and need controlled connection usage.

## Decision
Use PgBouncer in transaction pooling mode.

## Rationale
Transaction pooling protects PostgreSQL from connection exhaustion while maintaining good throughput.

## Rejected Alternatives
- Direct asyncpg connections to PostgreSQL

## Consequences
- Application connections target PgBouncer on port 6432.
- Some session-level features are unavailable in transaction mode.
