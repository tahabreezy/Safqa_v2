# ADR-02: Meilisearch for Full-Text Search

## Context
Safqa must provide typo-tolerant, low-latency tender search across large datasets.

## Decision
Use Meilisearch as the primary search engine.

## Rationale
Meilisearch offers fast full-text search, typo tolerance, and simple filtering/sorting configuration.

## Rejected Alternatives
- PostgreSQL full-text only

## Consequences
- Requires search indexing pipeline and Meilisearch operations.
- Better query latency and UX for search endpoints.
