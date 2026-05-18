from __future__ import annotations

from typing import Any


def apply_filters(
    tenders: list[dict[str, Any]], filters: dict[str, Any]
) -> list[dict[str, Any]]:
    if not filters:
        return tenders
    return [t for t in tenders if matches_tender(t, filters)]


def matches_tender(tender: dict[str, Any], filters: dict[str, Any]) -> bool:
    for key, value in filters.items():
        tender_val = tender.get(key)
        if tender_val is None or str(tender_val) != str(value):
            return False
    return True


def build_html_list(tenders: list[dict[str, Any]]) -> str:
    items = "".join(
        '<li>'
        f'<strong>{t.get("title", "")}</strong> — '
        f'{t.get("authority", "")} — '
        f'\u00c9ch\u00e9ance: {t.get("deadline_at", "")} — '
        f'<a href="{t.get("source_url", "#")}">Voir l\'offre</a>'
        '</li>'
        for t in tenders
    )
    return f"<ul>{items}</ul>"
