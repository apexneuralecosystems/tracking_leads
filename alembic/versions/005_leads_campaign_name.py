"""add campaign_name to leads

Revision ID: 005
Revises: 004
Create Date: 2026-02-12

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("campaign_name", sa.String(256), nullable=True))
    op.create_index("ix_leads_campaign_name", "leads", ["campaign_name"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_campaign_name", table_name="leads")
    op.drop_column("leads", "campaign_name")
