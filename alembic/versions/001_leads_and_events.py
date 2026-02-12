"""leads and events tables

Revision ID: 001
Revises:
Create Date: 2026-02-05

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tracking_id", sa.String(128), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("first_name", sa.String(256), nullable=True),
        sa.Column("company", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_leads_tracking_id", "leads", ["tracking_id"], unique=True)
    op.create_index("ix_leads_email", "leads", ["email"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tracking_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_events_tracking_id", "events", ["tracking_id"], unique=False)
    op.create_index("ix_events_event_type", "events", ["event_type"], unique=False)
    op.create_index("ix_events_tracking_created", "events", ["tracking_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_events_tracking_created", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_index("ix_events_tracking_id", table_name="events")
    op.drop_table("events")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_index("ix_leads_tracking_id", table_name="leads")
    op.drop_table("leads")
