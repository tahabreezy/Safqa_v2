# ADR-08: Self-Issued JWT Authentication

## Context
Authentication is in the critical path and must avoid vendor lock-in.

## Decision
Issue and validate JWT tokens in Safqa services.

## Rationale
Self-issued JWT keeps auth behavior and key rotation under direct control.

## Rejected Alternatives
- Supabase Auth

## Consequences
- Team owns token lifecycle, rotation, and security hardening.
- No dependency on third-party auth availability.
