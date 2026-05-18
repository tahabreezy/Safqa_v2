# ADR-05: Scrapy with Playwright Support

## Context
Tender pages may include dynamic content while scraping must stay robust and maintainable.

## Decision
Use Scrapy as the primary crawler and add Playwright only for JavaScript-required pages.

## Rationale
Scrapy provides retry/throttle/pipeline primitives; Playwright fills JS-rendering gaps.

## Rejected Alternatives
- Raw httpx + Playwright scripts

## Consequences
- Slightly more complex scraper stack.
- Better resilience and observability for crawl operations.
