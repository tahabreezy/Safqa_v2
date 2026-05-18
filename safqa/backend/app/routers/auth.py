from fastapi import APIRouter, Depends, HTTPException, Request, status
from middleware.rate_limit import limiter
from models import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    ErrorResponse,
)
from dependencies import get_current_user
from services.auth_service import (
    create_access_token,
    create_refresh_token,
    register_user,
    login_user,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    responses={409: {"model": ErrorResponse}},
)
@limiter.limit("10/minute")
async def register(request: Request, body: RegisterRequest):
    try:
        user = await register_user(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    access = create_access_token(user["id"])
    refresh = create_refresh_token(user["id"])
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    try:
        user = await login_user(body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    access = create_access_token(user["id"])
    refresh = create_refresh_token(user["id"])
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={401: {"model": ErrorResponse}},
)
@limiter.limit("10/minute")
async def refresh(request: Request, body: RefreshRequest):
    try:
        access, new_refresh = await rotate_refresh_token(body.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=access, refresh_token=new_refresh)


@router.get("/me")
@limiter.limit("10/minute")
async def me(request: Request, user: dict = Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"], "created_at": user["created_at"]}
