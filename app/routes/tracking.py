"""
Single tracking endpoint: GET /go/{campaign_name}/{tracking_id} — record click, then redirect.
Creates a new lead if none exists (lead_id + campaign + first_click_at from URL).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Event, Lead

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/go/{campaign_name}/{tracking_id}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Tracking link",
    description=(
        "Record click with campaign name, then redirect to REDIRECT_BASE_URL. "
        "If no lead exists with this tracking_id, a new lead is created (tracking_id, campaign_name, first_click_at). "
        "Example: /go/dubai/001. "
        "Swagger 'Execute' may show 'Failed to fetch' (browser blocks cross-origin redirect); test in address bar or with curl."
    ),
    responses={302: {"description": "Redirect to REDIRECT_BASE_URL"}},
)
async def track_click(
    campaign_name: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    event = Event(tracking_id=tracking_id, event_type="click")
    db.add(event)
    now = datetime.now(timezone.utc)
    result = await db.execute(select(Lead).where(Lead.tracking_id == tracking_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        lead = Lead(
            tracking_id=tracking_id,
            campaign_name=campaign_name or None,
            email="",
            first_click_at=now,
        )
        db.add(lead)
        logger.info("Lead created from /go tracking_id=%s campaign_name=%s", tracking_id, campaign_name)
    else:
        if lead.first_click_at is None:
            lead.first_click_at = now
        if campaign_name and (lead.campaign_name is None or lead.campaign_name != campaign_name):
            lead.campaign_name = campaign_name
    await db.commit()
    logger.info("Click recorded tracking_id=%s campaign_name=%s", tracking_id, campaign_name)
    settings = get_settings()
    return RedirectResponse(url=settings.redirect_base_url.rstrip("/"), status_code=302)
