# ADR-06: Docker Compose Orchestration

## Context
Safqa MVP runs on a single VPS and needs repeatable deployment with low operational overhead.

## Decision
Use Docker Compose for orchestration.

## Rationale
Compose is sufficient for single-node deployment and keeps operational complexity low.

## Rejected Alternatives
- Kubernetes

## Consequences
- Simpler deployment and troubleshooting.
- Manual scaling constraints compared with cluster orchestrators.
