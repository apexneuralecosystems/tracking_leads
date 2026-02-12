"""
Pydantic v2 schemas for request/response validation.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ----- POST /events (minimal: open | click only) -----
class EventCreate(BaseModel):
    tracking_id: str = Field(..., min_length=1, max_length=128)
    event_type: str = Field(..., pattern="^(open|click)$")


class EventResponse(BaseModel):
    id: UUID
    tracking_id: str
    event_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ----- POST /leads -----
class LeadCreate(BaseModel):
    tracking_id: str = Field(..., min_length=1, max_length=128)
    email: str = Field(..., min_length=1, max_length=320)
    first_name: str = Field("", max_length=256)
    company: str = Field("", max_length=256)


class LeadResponse(BaseModel):
    id: UUID
    tracking_id: str
    email: str
    first_name: str | None
    company: str | None
    created_at: datetime
    opened_at: datetime | None = None
    first_click_at: datetime | None = None

    model_config = {"from_attributes": True}
