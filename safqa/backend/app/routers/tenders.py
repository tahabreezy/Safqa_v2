import uuid

from fastapi import APIRouter, HTTPException, Query, status

from models import (
    DomainResponse,
    ErrorResponse,
    SearchResponse,
    StatsResponse,
    TenderResponse,
)
from services.search_service import search_tenders
from services.tender_service import get_tender, get_tender_by_ref, get_stats, get_domains

router = APIRouter(prefix="/tenders", tags=["tenders"])


@router.get("", response_model=SearchResponse)
async def list_tenders(
    q: str = "",
    domain: str | None = Query(None),
    city: str | None = Query(None),
    type: str | None = Query(None, alias="type"),
    status: str | None = Query("active"),
    sort: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    result = await search_tenders(
        q=q, domain=domain, city=city, type=type,
        status=status, sort=sort, page=page, limit=limit,
    )
    total_pages = max(1, (result.total + limit - 1) // limit)
    return SearchResponse(
        data=[TenderResponse(**h) for h in result.hits],
        total=result.total,
        page=result.page,
        limit=result.limit,
        total_pages=total_pages,
    )


@router.get(
    "/stats",
    response_model=StatsResponse,
)
async def tenders_stats():
    stats = await get_stats()
    return StatsResponse(**stats)


@router.get(
    "/domains",
    response_model=list[DomainResponse],
)
async def tenders_domains():
    domains = await get_domains()
    return [DomainResponse(**d) for d in domains]


@router.get(
    "/ref/{reference}",
    response_model=TenderResponse,
    responses={404: {"model": ErrorResponse}},
)
async def tenders_by_ref(reference: str):
    tender = await get_tender_by_ref(reference)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return TenderResponse(**tender)


@router.get(
    "/{tender_id}",
    response_model=TenderResponse,
    responses={404: {"model": ErrorResponse}},
)
async def tenders_detail(tender_id: uuid.UUID):
    tender = await get_tender(tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return TenderResponse(**tender)
