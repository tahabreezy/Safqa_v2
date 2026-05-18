from __future__ import annotations

import uuid
from typing import Any

import bcrypt
import jwt

from infrastructure.redis_client import redis_client
from models import TokenResponse
from repositories.user_repo import user_repo


JWT_SECRET = "secret"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = 15 * 60
REFRESH_TOKEN_EXPIRE = 7 * 24 * 60 * 60


def _load_jwt_config():
    import os
    global JWT_SECRET, JWT_ALGORITHM
    JWT_SECRET = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-prod")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


_load_jwt_config()


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": _now() + ACCESS_TOKEN_EXPIRE,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": _now() + REFRESH_TOKEN_EXPIRE,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


async def rotate_refresh_token(old_token: str) -> tuple[str, str]:
    payload = decode_token(old_token)
    user_id = uuid.UUID(payload["sub"])

    remaining = payload["exp"] - _now()
    if remaining > 0:
        await redis_client.blocklist_token(old_token, int(remaining))

    access = create_access_token(user_id)
    refresh = create_refresh_token(user_id)
    return access, refresh


def _now() -> int:
    from datetime import datetime, timezone
    return int(datetime.now(timezone.utc).timestamp())


async def register_user(email: str, password: str) -> dict:
    existing = await user_repo.get_by_email(email)
    if existing:
        raise ValueError("Email already registered")
    hashed = hash_password(password)
    user = await user_repo.create(email, hashed)
    return user


async def login_user(email: str, password: str) -> dict:
    user = await user_repo.get_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid email or password")
    return user


