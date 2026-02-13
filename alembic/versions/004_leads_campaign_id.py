"""add campaign_id to leads

Revision ID: 004
Revises: 003
Create Date: 2026-02-12

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("campaign_id", sa.String(128), nullable=True))
    op.create_index("ix_leads_campaign_id", "leads", ["campaign_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_campaign_id", table_name="leads")
    op.drop_column("leads", "campaign_id")
