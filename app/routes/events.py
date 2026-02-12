"""
POST /events — optional manual event logging (open or click). Minimal: no metadata.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Event
from app.schemas import EventCreate, EventResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/events",
    response_model=EventResponse,
    status_code=201,
    summary="Log event (open or click)",
    description="Store a single event. event_type must be 'open' or 'click'.",
)
async def create_event(
    body: EventCreate,
    db: AsyncSession = Depends(get_db),
) -> EventResponse:
    event = Event(tracking_id=body.tracking_id, event_type=body.event_type)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    logger.info("Event created tracking_id=%s type=%s id=%s", body.tracking_id, body.event_type, event.id)
    return EventResponse.model_validate(event)
