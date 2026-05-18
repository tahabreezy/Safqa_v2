from prometheus_client import Counter, Histogram, Gauge

tenders_scraped = Counter(
    "safqa_tenders_scraped_total",
    "Total tenders scraped per domain",
    ["domain_code"],
)
tenders_upserted = Counter(
    "safqa_tenders_upserted_total",
    "Total rows changed on upsert",
    ["domain_code"],
)
scrape_duration = Histogram(
    "safqa_scrape_duration_seconds",
    "Per-scrape duration in seconds",
    ["domain_code"],
)
scrape_errors = Counter(
    "safqa_scrape_errors_total",
    "Scraping failures per domain",
    ["domain_code", "error"],
)
alerts_sent = Counter(
    "safqa_alerts_sent_total",
    "Total alert emails dispatched",
)
dlq_depth = Gauge(
    "safqa_dlq_depth",
    "Dead letter queue message count",
    ["queue_name"],
)
cache_hits = Counter(
    "safqa_cache_hits_total",
    "Redis cache hits per endpoint",
    ["endpoint"],
)
cache_misses = Counter(
    "safqa_cache_misses_total",
    "Redis cache misses per endpoint",
    ["endpoint"],
)
pgbouncer_active = Gauge(
    "pgbouncer_pool_clients_active",
    "Active PgBouncer connections per database",
    ["database"],
)
