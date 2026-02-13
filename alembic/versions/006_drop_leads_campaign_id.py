"""drop campaign_id from leads (use campaign_name only)

Revision ID: 006
Revises: 005
Create Date: 2026-02-12

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_leads_campaign_id", table_name="leads")
    op.drop_column("leads", "campaign_id")


def downgrade() -> None:
    op.add_column("leads", sa.Column("campaign_id", sa.String(128), nullable=True))
    op.create_index("ix_leads_campaign_id", "leads", ["campaign_id"], unique=False)
