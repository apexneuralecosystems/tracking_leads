"""
Pydantic v2 schemas for request/response validation.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


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
    campaign_name: str | None = Field(None, max_length=256)
    lead_id: str | None = Field(None, min_length=1, max_length=128, description="Tracking ID; pass this OR email, not both")
    email: str | None = Field(None, min_length=1, max_length=320, description="Email; pass this OR lead_id, not both")

    @model_validator(mode="after")
    def exactly_one_identifier(self) -> "LeadCreate":
        has_lead_id = self.lead_id is not None and self.lead_id.strip() != ""
        has_email = self.email is not None and self.email.strip() != ""
        if has_lead_id and has_email:
            raise ValueError("Pass only one of lead_id or email, not both")
        if not has_lead_id and not has_email:
            raise ValueError("Pass either lead_id or email (exactly one required)")
        return self


class LeadResponse(BaseModel):
    id: UUID
    tracking_id: str
    campaign_name: str | None = None
    email: str
    first_name: str | None
    company: str | None
    created_at: datetime
    opened_at: datetime | None = None
    first_click_at: datetime | None = None

    model_config = {"from_attributes": True}
