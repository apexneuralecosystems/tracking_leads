"""
Leads API: GET all, GET by id, GET by email/tracking_id, POST (lead_id OR email only one), DELETE.
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, time, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _date_start_utc(d: date) -> datetime:
    return datetime.combine(d, time.min, tzinfo=timezone.utc)


def _date_end_utc(d: date) -> datetime:
    return datetime.combine(d, time(23, 59, 59, 999999), tzinfo=timezone.utc)


@router.get(
    "/leads",
    response_model=list[LeadResponse],
    summary="Get all leads",
    description="List all leads. Optional filters: email, tracking_id, from_date, to_date (filter by created_at).",
)
async def list_leads(
    db: AsyncSession = Depends(get_db),
    email: str | None = Query(None, description="Filter by email"),
    tracking_id: str | None = Query(None, description="Filter by tracking_id (lead_id)"),
    from_date: date | None = Query(None, description="Filter leads created on or after this date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="Filter leads created on or before this date (YYYY-MM-DD)"),
) -> list[LeadResponse]:
    if from_date is not None and to_date is not None and from_date > to_date:
        raise HTTPException(status_code=400, detail="from_date must be on or before to_date")

    q = select(Lead).order_by(Lead.created_at.desc())
    if email is not None and email.strip():
        q = q.where(Lead.email == email.strip())
    if tracking_id is not None and tracking_id.strip():
        q = q.where(Lead.tracking_id == tracking_id.strip())
    if from_date is not None:
        q = q.where(Lead.created_at >= _date_start_utc(from_date))
    if to_date is not None:
        q = q.where(Lead.created_at <= _date_end_utc(to_date))
    result = await db.execute(q)
    leads = result.scalars().all()
    return [LeadResponse.model_validate(lead) for lead in leads]


@router.get(
    "/leads/{lead_id}",
    response_model=LeadResponse,
    summary="Get lead by ID",
    description="Get a single lead by UUID.",
)
async def get_lead_by_id(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=201,
    summary="Create lead",
    description="Create a lead. Pass exactly one of: lead_id (tracking_id) OR email. campaign_name optional. Returns 409 if lead_id/tracking_id or email already exists.",
)
async def create_lead(
    body: LeadCreate,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    if body.lead_id is not None and body.lead_id.strip():
        tracking_id = body.lead_id.strip()
        email = body.email or ""
    else:
        email = (body.email or "").strip()
        tracking_id = uuid.uuid4().hex[:32]

    result = await db.execute(select(Lead).where(Lead.tracking_id == tracking_id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Lead with this tracking_id already exists")
    if email:
        result = await db.execute(select(Lead).where(Lead.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Lead with this email already exists")

    lead = Lead(
        tracking_id=tracking_id,
        campaign_name=body.campaign_name or None,
        email=email,
        first_name=None,
        company=None,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    logger.info(
        "Lead created tracking_id=%s campaign_name=%s id=%s",
        tracking_id,
        body.campaign_name,
        lead.id,
    )
    return LeadResponse.model_validate(lead)


@router.delete(
    "/leads/{lead_id}",
    status_code=204,
    summary="Delete lead",
    description="Delete a lead by UUID. Returns 404 if not found.",
)
async def delete_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    logger.info("Lead deleted id=%s", lead_id)
