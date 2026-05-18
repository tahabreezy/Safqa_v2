from __future__ import annotations

import os
from typing import Any

from safqa_scraper.items import TenderItem


class MeilisearchPipeline:
    def __init__(self):
        self.meili_url = os.getenv("MEILI_URL", "http://meilisearch:7700")
        self.meili_key = os.getenv("MEILI_MASTER_KEY", "")
        self.client: Any = None
        self.batch: list[dict] = []
        self.batch_size = 100

    def open_spider(self, spider) -> None:
        from meilisearch import Client
        self.client = Client(self.meili_url, self.meili_key)
        self._ensure_index(spider)

    def _ensure_index(self, spider) -> None:
        try:
            index = self.client.get_index("tenders")
        except Exception:
            spider.logger.info("Creating Meilisearch index 'tenders'")
            self.client.create_index("tenders", {"primaryKey": "id"})
            index = self.client.get_index("tenders")

        index.update_settings({
            "searchableAttributes": ["title", "authority", "domain_label", "city"],
            "filterableAttributes": ["domain_code", "city", "status", "procedure_type"],
            "sortableAttributes": ["deadline_at", "budget_mad", "published_at"],
            "typoTolerance": {"enabled": True},
            "pagination": {"maxTotalHits": 100000},
        })

    def process_item(self, item: TenderItem, spider) -> TenderItem:
        doc = {
            "id": str(item.get("reference_number", "")),
            "reference_number": item.get("reference_number"),
            "title": item.get("title"),
            "authority": item.get("authority"),
            "city": item.get("city"),
            "domain_code": item.get("domain_code"),
            "domain_label": item.get("domain_label"),
            "procedure_type": item.get("procedure_type"),
            "budget_mad": float(item["budget_mad"]) if item.get("budget_mad") else None,
            "published_at": str(item.get("published_at")) if item.get("published_at") else None,
            "deadline_at": str(item.get("deadline_at")) if item.get("deadline_at") else None,
            "status": "active",
        }
        self.batch.append(doc)

        if len(self.batch) >= self.batch_size:
            self._flush(spider)

        return item

    def _flush(self, spider) -> None:
        if not self.batch:
            return
        for attempt in range(3):
            try:
                self.client.index("tenders").add_documents(self.batch)
                spider.logger.info("Indexed %d documents to Meilisearch", len(self.batch))
                break
            except Exception as e:
                spider.logger.error("Meilisearch indexing error (attempt %d): %s", attempt + 1, e)
                if attempt < 2:
                    import time
                    time.sleep(2 ** attempt)
        self.batch = []

    def close_spider(self, spider) -> None:
        self._flush(spider)
