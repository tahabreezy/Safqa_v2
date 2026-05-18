# ADR-07: TanStack Query for Frontend Data Layer

## Context
Frontend requires robust caching, retries, and mutation synchronization.

## Decision
Use TanStack Query as the client data layer.

## Rationale
It provides flexible cache invalidation and request lifecycle controls for API-driven UI.

## Rejected Alternatives
- SWR

## Consequences
- Slight setup overhead.
- Better long-term ergonomics for search and saved/alert mutations.
