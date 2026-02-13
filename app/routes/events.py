"""
POST /events — optional manual event logging (open or click). Minimal: no metadata.
When event_type is 'open', also set Lead.opened_at for the matching lead (if any).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event, Lead
from app.schemas import EventCreate, EventResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=201,
    summary="Log event (open or click)",
    description="Store a single event. event_type must be 'open' or 'click'. On 'open', lead.opened_at is set if the lead exists.",
)
async def create_event(
    body: EventCreate,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    event = Event(tracking_id=body.tracking_id, event_type=body.event_type)
    db.add(event)
    if body.event_type == "open":
        now = datetime.now(timezone.utc)
        result = await db.execute(select(Lead).where(Lead.tracking_id == body.tracking_id))
        lead = result.scalar_one_or_none()
        if lead is not None and lead.opened_at is None:
            lead.opened_at = now
    await db.commit()
    await db.refresh(event)
    logger.info("Event created tracking_id=%s type=%s id=%s", body.tracking_id, body.event_type, event.id)
    return EventResponse.model_validate(event)
