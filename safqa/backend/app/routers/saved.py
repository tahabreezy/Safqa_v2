import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from dependencies import get_current_user
from models import ErrorResponse, SavedListResponse, TenderResponse
from services.saved_service import get_saved, save_tender, unsave_tender

router = APIRouter(prefix="/saved", tags=["saved"])


@router.get("", response_model=SavedListResponse)
async def list_saved(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: dict = Depends(get_current_user),
):
    rows, total = await get_saved(user["id"], page=page, limit=limit)
    return SavedListResponse(
        data=[TenderResponse(**r) for r in rows],
        page=page,
        limit=limit,
        total=total,
    )


@router.post(
    "/{tender_id}",
    responses={404: {"model": ErrorResponse}},
)
async def save_tender_route(
    tender_id: uuid.UUID,
    user: dict = Depends(get_current_user),
):
    ok = await save_tender(user["id"], tender_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tender not found")
    return {"status": "saved"}


@router.delete(
    "/{tender_id}",
    responses={404: {"model": ErrorResponse}},
)
async def unsave_tender_route(
    tender_id: uuid.UUID,
    user: dict = Depends(get_current_user),
):
    ok = await unsave_tender(user["id"], tender_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved tender not found")
    return {"status": "removed"}
