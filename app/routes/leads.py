"""
POST /leads — create lead; prevent duplicate tracking_id.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lead
from app.schemas import LeadCreate, LeadResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/leads",
    response_model=list[LeadResponse],
    summary="List all leads with engagement",
    description="Returns all leads with id, tracking_id, email, and opened/clicked timestamps.",
)
async def list_leads(db: AsyncSession = Depends(get_db)) -> list[LeadResponse]:
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()))
    leads = result.scalars().all()
    return [LeadResponse.model_validate(lead) for lead in leads]


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=201,
    summary="Create lead",
    description="Create a lead. Returns 409 if tracking_id already exists.",
)
async def create_lead(
    body: LeadCreate,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    result = await db.execute(select(Lead).where(Lead.tracking_id == body.tracking_id))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Lead with this tracking_id already exists")

    lead = Lead(
        tracking_id=body.tracking_id,
        email=body.email,
        first_name=body.first_name or None,
        company=body.company or None,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    logger.info("Lead created tracking_id=%s email=%s id=%s", body.tracking_id, body.email, lead.id)
    return LeadResponse.model_validate(lead)
