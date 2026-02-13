"""
Minimal email engagement: leads + events (open or click only).
All timestamps stored in UTC via DateTime(timezone=True).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Lead(Base):
    """Lead with optional first-open and first-click timestamps for fast 'opened or not' queries."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    campaign_name: Mapped[str | None] = mapped_column(String(256), index=True, nullable=True)
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    company: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_click_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Event(Base):
    """Minimal events: event_type is 'open' (pixel) or 'click' (link). No IP, UA, or metadata."""

    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tracking_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # "open" | "click"
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


Index("ix_events_tracking_created", Event.tracking_id, Event.created_at)
