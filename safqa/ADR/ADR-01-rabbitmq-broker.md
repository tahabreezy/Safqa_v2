# ADR-01: RabbitMQ as Celery Broker

## Context
Safqa needs reliable task delivery for scrape and alert jobs.

## Decision
Use RabbitMQ as the Celery broker.

## Rationale
AMQP delivery guarantees are stronger than Redis list-based broker semantics for this workload.

## Rejected Alternatives
- Redis as broker

## Consequences
- Requires running and monitoring RabbitMQ.
- Improves reliability for queued workloads.
