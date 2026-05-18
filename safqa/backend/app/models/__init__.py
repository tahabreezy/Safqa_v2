from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, computed_field, EmailStr


# ── Auth ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# ── Tenders ─────────────────────────────────────────────────────────────────

class TenderResponse(BaseModel):
    id: uuid.UUID
    reference_number: str
    title: str
    authority: str
    city: str | None = None
    domain_code: str
    domain_label: str | None = None
    procedure_type: str | None = None
    budget_raw: str | None = None
    budget_mad: float | None = None
    published_at: date
    deadline_at: date
    source_url: str | None = None
    status: str
    scraped_at: datetime | None = None
    created_at: datetime | None = None

    @computed_field
    def is_urgent(self) -> bool:
        return (self.deadline_at - date.today()).days <= 14

class TenderSearchParams(BaseModel):
    q: str = ""
    domain: str | None = None
    city: str | None = None
    type: str | None = None
    status: str | None = "active"
    sort: str | None = None
    page: int = 1
    limit: int = 20

class SearchResponse(BaseModel):
    data: list[TenderResponse]
    total: int
    page: int
    limit: int
    total_pages: int

class StatsResponse(BaseModel):
    active: int
    urgent: int
    new_this_week: int
    total: int

class DomainResponse(BaseModel):
    domain_code: str
    domain_label: str
    count: int

# ── Saved Tenders ───────────────────────────────────────────────────────────

class SavedListResponse(BaseModel):
    data: list[TenderResponse]
    page: int
    limit: int
    total: int

# ── Alerts ──────────────────────────────────────────────────────────────────

class AlertCreateRequest(BaseModel):
    filters: dict[str, Any]
    email: EmailStr
    label: str

class AlertPatchRequest(BaseModel):
    is_active: bool

class AlertResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    label: str
    filters: dict[str, Any]
    email: str
    is_active: bool
    created_at: datetime

# ── Common ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Any = None
