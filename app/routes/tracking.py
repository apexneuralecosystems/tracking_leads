"""
Minimal email engagement: open pixel (GET /o/{tracking_id}.png) and click redirect (GET /t/{tracking_id}).

Open tracking works via a tracking pixel: the email HTML includes an <img> whose src is
https://apexneural.com/o/{tracking_id}.png. When the email client loads images, it requests
this URL; we record event_type="open" and return a 1x1 transparent PNG so nothing is visible.
We only store the first open per tracking_id to avoid duplicate opens from re-renders.

Click tracking is more reliable than open tracking because: (1) the user must take an action,
(2) most email clients block images by default (so opens are undercounted), (3) image blocking
means open tracking may be blocked entirely by some clients (e.g. Apple Mail, some Gmail
configs), while link clicks still fire when the user clicks.

Open tracking may be blocked by some email clients because: they block remote images for
privacy/security, or they proxy image requests and only load on user interaction, or they
strip tracking pixels. So treat open data as best-effort and use clicks as the primary signal.
"""

from __future__ import annotations

import base64
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import Event, Lead

logger = logging.getLogger(__name__)

router = APIRouter()

# 1x1 transparent PNG (smallest valid PNG). Returned for GET /o/{tracking_id}.png so the
# email client gets a valid image and we don't trigger broken-image behavior.
TRACKING_PIXEL_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)
TRACKING_PIXEL_BYTES = base64.b64decode(TRACKING_PIXEL_PNG_B64)


@router.get(
    "/o/{tracking_id}.png",
    response_class=Response,
    status_code=200,
    summary="Tracking pixel (open)",
    description="Record first open per tracking_id, return 1x1 transparent PNG. No redirect.",
)
async def track_open(
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    # Avoid duplicate open events: only store the first open per tracking_id.
    result = await db.execute(
        select(Event.id).where(
            Event.tracking_id == tracking_id,
            Event.event_type == "open",
        ).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        return Response(content=TRACKING_PIXEL_BYTES, media_type="image/png")

    event = Event(tracking_id=tracking_id, event_type="open")
    db.add(event)
    now = datetime.now(timezone.utc)
    result = await db.execute(select(Lead).where(Lead.tracking_id == tracking_id))
    lead = result.scalar_one_or_none()
    if lead is not None and lead.opened_at is None:
        lead.opened_at = now
    await db.commit()
    logger.info("Open recorded tracking_id=%s event_id=%s", tracking_id, event.id)
    return Response(content=TRACKING_PIXEL_BYTES, media_type="image/png")


async def _record_click_and_redirect(
    tracking_id: str,
    campaign_name: str | None,
    db: AsyncSession,
) -> RedirectResponse:
    event = Event(tracking_id=tracking_id, event_type="click")
    db.add(event)
    now = datetime.now(timezone.utc)
    result = await db.execute(select(Lead).where(Lead.tracking_id == tracking_id))
    lead = result.scalar_one_or_none()
    if lead is not None:
        if lead.first_click_at is None:
            lead.first_click_at = now
        if campaign_name and (lead.campaign_name is None or lead.campaign_name != campaign_name):
            lead.campaign_name = campaign_name
    await db.commit()
    logger.info("Click recorded tracking_id=%s campaign_name=%s event_id=%s", tracking_id, campaign_name, event.id)
    settings = get_settings()
    return RedirectResponse(url=settings.redirect_base_url.rstrip("/"), status_code=302)


@router.get(
    "/t/{tracking_id}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Tracking link (click)",
    description="Record click, then redirect to base URL. Event is stored before redirect.",
)
async def track_click(
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    return await _record_click_and_redirect(tracking_id, None, db)


@router.get(
    "/c/{campaign_name}/{tracking_id}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Tracking link with campaign (c)",
    description="Record click with campaign name (e.g. meetapexneural.com/c/DubaiCamp/t124), then redirect.",
)
async def track_click_c(
    campaign_name: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    return await _record_click_and_redirect(tracking_id, campaign_name, db)


@router.get(
    "/r/{campaign_name}/{tracking_id}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Tracking link with campaign (r)",
    description="Record click with campaign name (e.g. meetapexneural.com/r/DubaiCamp/t124), then redirect.",
)
async def track_click_r(
    campaign_name: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    return await _record_click_and_redirect(tracking_id, campaign_name, db)


@router.get(
    "/go/{campaign_name}/{tracking_id}",
    response_class=RedirectResponse,
    status_code=302,
    summary="Tracking link with campaign (go)",
    description="Record click with campaign name (e.g. meetapexneural.com/go/DubaiCamp/t124), then redirect.",
)
async def track_click_go(
    campaign_name: str,
    tracking_id: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    return await _record_click_and_redirect(tracking_id, campaign_name, db)
