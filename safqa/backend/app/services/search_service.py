from __future__ import annotations

import json
import uuid
from typing import Any

from infrastructure.meili_client import meili_client, SearchResult
from infrastructure.redis_client import redis_client
from metrics import cache_hits, cache_misses
from repositories.tender_repo import tender_repo


async def search_tenders(
    q: str = "",
    domain: str | None = None,
    city: str | None = None,
    type: str | None = None,
    status: str | None = "active",
    sort: str | None = None,
    page: int = 1,
    limit: int = 20,
) -> SearchResult:
    cache_key = _search_cache_key(q, domain, city, type, status, sort, page, limit)

    cached = await redis_client.get(cache_key)
    if cached:
        cache_hits.labels(endpoint="tenders.search").inc()
        data = json.loads(cached)
        return SearchResult(**data)

    cache_misses.labels(endpoint="tenders.search").inc()

    filter_exprs = _build_filters(domain, city, type, status)
    sort_expr = _build_sort(sort)

    result = meili_client.search(
        q=q,
        filters=" AND ".join(filter_exprs) if filter_exprs else None,
        sort=sort_expr,
        page=page,
        limit=limit,
    )

    if result.hits:
        ids = [h["id"] for h in result.hits]
        enriched = await tender_repo.get_by_ids(ids)
        id_map = {str(r["id"]): r for r in enriched}
        merged = []
        for h in result.hits:
            row = id_map.get(h["id"])
            merged.append(row if row else h)
        result.hits = merged

    await redis_client.set(cache_key, json.dumps(_result_to_dict(result), default=str))

    return result


def _build_filters(
    domain: str | None,
    city: str | None,
    type: str | None,
    status: str | None,
) -> list[str]:
    exprs: list[str] = []
    if domain:
        exprs.append(f'domain_code = "{domain}"')
    if city:
        exprs.append(f'city = "{city}"')
    if type:
        exprs.append(f'procedure_type = "{type}"')
    if status:
        exprs.append(f'status = "{status}"')
    return exprs


def _build_sort(sort: str | None) -> list[str] | None:
    if not sort:
        return None
    mapping = {
        "deadline_asc": "deadline_at:asc",
        "deadline_desc": "deadline_at:desc",
        "budget_asc": "budget_mad:asc",
        "budget_desc": "budget_mad:desc",
        "published_asc": "published_at:asc",
        "published_desc": "published_at:desc",
    }
    val = mapping.get(sort)
    return [val] if val else None


def _search_cache_key(
    q: str, domain: str | None, city: str | None,
    type: str | None, status: str | None,
    sort: str | None, page: int, limit: int,
) -> str:
    from utils import hash_cache_key
    return f"search:{hash_cache_key(q, domain, city, type, status, sort, page, limit)}"


def _result_to_dict(r: SearchResult) -> dict:
    return {
        "hits": r.hits,
        "total": r.total,
        "page": r.page,
        "limit": r.limit,
    }
