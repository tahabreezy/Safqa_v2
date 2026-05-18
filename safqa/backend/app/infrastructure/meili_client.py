from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from meilisearch import Client


@dataclass
class SearchResult:
    hits: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    page: int = 1
    limit: int = 20


class MeiliClient:
    def __init__(self):
        self.url = os.getenv("MEILI_URL", "http://meilisearch:7700")
        self.key = os.getenv("MEILI_MASTER_KEY", "")
        self._client: Client | None = None

    def _get_client(self) -> Client:
        if self._client is None:
            self._client = Client(self.url, self.key)
        return self._client

    def search(
        self,
        q: str,
        filters: str | None = None,
        sort: list[str] | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> SearchResult:
        client = self._get_client()
        params: dict[str, Any] = {
            "limit": limit,
            "offset": (page - 1) * limit,
        }
        if filters:
            params["filter"] = filters
        if sort:
            params["sort"] = sort

        result = client.index("tenders").search(q, params)

        return SearchResult(
            hits=result.get("hits", []),
            total=result.get("estimatedTotalHits", 0),
            page=page,
            limit=limit,
        )

    def add_documents(self, docs: list[dict]) -> None:
        client = self._get_client()
        client.index("tenders").add_documents(docs)

    def health(self) -> dict:
        client = self._get_client()
        return client.health()


meili_client = MeiliClient()
