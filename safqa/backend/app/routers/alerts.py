import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_current_user
from models import AlertCreateRequest, AlertPatchRequest, AlertResponse, ErrorResponse
from services.alert_service import get_alerts, create_alert, toggle_alert, delete_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
async def list_alerts(user: dict = Depends(get_current_user)):
    alerts = await get_alerts(user["id"])
    return [AlertResponse(**a) for a in alerts]


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alert_route(
    body: AlertCreateRequest,
    user: dict = Depends(get_current_user),
):
    alert = await create_alert(user["id"], body.filters, body.email, body.label)
    return AlertResponse(**alert)


@router.patch(
    "/{alert_id}",
    response_model=AlertResponse,
    responses={404: {"model": ErrorResponse}},
)
async def patch_alert(
    alert_id: uuid.UUID,
    body: AlertPatchRequest,
    user: dict = Depends(get_current_user),
):
    alert = await toggle_alert(alert_id, body.is_active)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return AlertResponse(**alert)


@router.delete(
    "/{alert_id}",
    responses={404: {"model": ErrorResponse}},
)
async def delete_alert_route(
    alert_id: uuid.UUID,
    user: dict = Depends(get_current_user),
):
    ok = await delete_alert(alert_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return {"status": "deleted"}
